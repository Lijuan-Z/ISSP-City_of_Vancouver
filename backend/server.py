import time, datetime, pytz
from search import search_files
import process_to_JSON
import scrape
from scrape import download_source_html, download_pdf, download_pdf_voc_bylaws, retrieve_document_type, read_previous_source, add_unpaired_file
from flask import Flask, request, make_response, render_template, abort
from flask_cors import CORS
import threading
import json
import pandas as pd
import io, os
import configparser

from output_handler import OutputHandler

thread_event = threading.Event()

# create excel_output if not exist
os.makedirs("excel_output", exist_ok=True)

# config file for information management
config = configparser.ConfigParser()
config.read('development.ini')
config.read('exclude_file.ini')

app = Flask(__name__)
# app._static_folder = "_next/static"
CORS(app)
update_status = False
o2_status = False
o2_output_info = ""

def read_source_with_exclusion(json_file):
    with open(json_file, "r", encoding="utf-8") as source_file:
        file_list = json.load(source_file)

        start_length = len(file_list)
        file_name = [i[1] for i in config.items("exclusion")]
        for file in file_name:
            for item in file_list:
                if list(item.keys())[0].lower() == file.lower():
                    file_list.remove(item)
                    break
        print(f"{start_length - len(file_list)} of files is excluded from the list")
        print(f"Excluded files: {[x + '.pdf' for x in file_name]}")
        return file_list

# preload the stored doc_type.json for retreiving last update date
latest_doc_type = read_source_with_exclusion(config.get('server', 'doc_file'))
last_update_date = max(list([list(obj.values())[0]["Last update"] for obj in latest_doc_type]))


# Generate excel output file name
# format objective-x-date-time.xlsx
def generate_excel_file_name(objective):
    result = f"output-obj-{objective}_"
    result = result + datetime.datetime.now(pytz.timezone('America/Vancouver')).strftime("%Y-%m-%d-%H-%M")
    return result + ".xlsx"

def create_api_excel_file_response(message, input_files, output_file):
    output_excel = pd.DataFrame({'Message': {"message": message, "files": input_files}})
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')
    output_excel.to_excel(excel_writer=writer, index=False, sheet_name='Report')
    writer.close()
    # Create response object
    response = make_response(out.getvalue())
    # Set headers
    response.headers["Content-Disposition"] = f"attachment; filename={output_file}"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    return response


# Generate Excel file based on the query
def generate_response(query, files, enable_ai, prompt, section):
    start_time = time.time()
    excel_file_path = generate_excel_file_name("1")

    output_dict = search_files(files, json_path=config.get('server', 'processed_json_file'), search_terms=query)
    if output_dict[1]:
        # There is search terms found in the file

        # if enable_ai is True:
        #     # For objective 2 - enable Gemini - API AI
        #     thread_o2 = threading.Thread(target=o2_handler, args=[output_dict[0], prompt, section], daemon=True)
        #     thread_o2.start()
        #
        #     end_time = time.time()
        #     elapsed_time = end_time - start_time
        #     # Print the elapsed time
        #     print("Elapsed time:", elapsed_time, "seconds")
        #
        #     output = f"/search AI is generating report. We will info you when file is created."
        #
        #     app.logger.info(f"/search: AI started generating report. Returning a status-code:200 response")
        #     response = app.response_class(
        #         response=json.dumps({"data": output}),
        #         status=200,
        #         mimetype='application/json'
        #     )
        #     return response
        # else:
            # For objective 1 output excel file
        try:
            OutputHandler.create_excel_file(output_dict[0],
                                        output_file=f'{config.get("server", "excel_folder")}/{excel_file_path}')

            with open(f'{config.get("server", "excel_folder")}/{excel_file_path}', "rb") as file:
                file_data = file.read()

            end_time = time.time()
            elapsed_time = end_time - start_time
            # Print the elapsed time
            print("Elapsed time:", elapsed_time, "seconds")

            # Create response object
            response = make_response(file_data)
            # Set headers
            response.headers["Content-Disposition"] = f"attachment; filename={excel_file_path}"
            response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return response

        except Exception as e:
            msg = f"There is an error when searching {query}. code: {e}"
            print(msg)
            return create_api_excel_file_response(msg, files, excel_file_path)

    else:
        # No search terms found in the file
        msg = f"There is no information for output with search term(s): {query}"
        o2_output_info = msg
        print(msg)
        return create_api_excel_file_response(msg, files, excel_file_path)








# Handling web-scrapping of PDF and document-type json file
def scrap_file_and_data():
    global update_status
    global last_update_date
    global latest_doc_type

    while thread_event.is_set():
    ### html, pdf & doc-type json download process ###
        if config.getboolean('scrap', 'download'):
            update_status = True

            # # URL of the website to scrape
            website_url_cov = config.get('scrap', 'cov_url')
            website_url_bylaw = config.get('scrap', 'bylaw_url')
            # Directory to save the downloaded PDFs
            save_directory = config.get('scrap', 'pdf_folder')
            # Output file name for document_type json data
            output_file = config.get('server', 'doc_file')

            app.logger.info("/update: server is downloading html file")
            source_html_cov = download_source_html(website_url_cov)
            source_html_bylaw = download_source_html(website_url_bylaw)
            app.logger.info("/update: server finished downloading html. Now downloading pdf files")
            total_downloaded_cov = download_pdf(source_html_cov, website_url_cov, save_directory)
            total_downloaded_bylaw = download_pdf_voc_bylaws(source_html_bylaw, save_directory, total_downloaded_cov)
            app.logger.info(f"/update: server finished downloading {total_downloaded_cov + total_downloaded_bylaw} pdf files. Now creating doc-type-json file")
            previous_file = read_previous_source(config.get('server', 'doc_file'))
            retrieve_document_type(source_html_cov, source_html_bylaw, previous_file, output_file)
            # getting latest update date
            latest_file = read_previous_source(config.get('server', 'doc_file'))
            last_update_date = max(list([list(obj.values())[0]["Last update"] for obj in latest_file]))
            add_unpaired_file(config.get('scrap', 'pdf_folder'), config.get('server', 'doc_file'))
            updated_doc_type = read_previous_source(config.get('server', 'doc_file'))

            # run process to json function
            pdf_folder = config.get("scrap", "pdf_folder")
            processor = process_to_JSON.ProcessToJSON(pdf_folder)
            dict_info = processor.read_PDFs(image_included=True, URL_info=updated_doc_type)
            with open(config.get('server', 'processed_json_file'), 'w') as json_file:
                json.dump(dict_info, json_file, indent=4)

            latest_doc_type = read_source_with_exclusion(config.get('server', 'doc_file'))
            update_status = False

        thread_event.clear()

def scrape_status():

        total_file_to_update = 590
        if scrape.total_files > total_file_to_update:
            total_file_to_update = scrape.total_files

        percentage_updated = float(scrape.file_counter / total_file_to_update * 100)

        status_message = "Idle"
        if update_status:
            status_message = "Updating"

        return {
            "status": status_message,
            "file_updated": scrape.file_counter,
            "last_updated": last_update_date,
            "total_updated_files": total_file_to_update,
            "percentage_updated": f"{percentage_updated:.2f}",
            "ocr": process_to_JSON.process_update
        }

def read_data_type_file():
    # open stored doc-type file and return update info
    data = read_source_with_exclusion(config.get('server', 'doc_file'))

    output = []
    for obj in data:
        for k, v in obj.items():
            v["section"] = v['type']
            v["webpage-title"] = v['title']
            v["file-name"] = k
            del v["title_original"]
            del v['type']
            del v['title']
            output.append(v)
    return output

def file_filter(file_names, category):
    checked_list = []
    for f in file_names:
        ### file validation ####
        validated_file = (list(filter(lambda obj: list(obj.keys())[0] == f, latest_doc_type)))
        if len(validated_file) > 0:
            checked_list.append(f)
    if len(checked_list) == 0 and len(category) == 0:
        return []

    if len(category) == 0:
        return checked_list
    else:
        file_info = read_data_type_file()
        checkall = list([x.lower() for x in category])
        if "all" in checkall:
            file_list = list([f["file-name"] for f in file_info])
            return file_list
        else:
            file_info = list(filter(lambda f: f["section"] in category, file_info))
            file_list = list([f["file-name"] for f in file_info])
            return file_list + file_names

# return 404 Not found for non-exist route
@app.errorhandler(404)
def page_not_found(error):
    return app.response_class(
        response=json.dumps({"data": f"Error: The server encounter an error of {error}"}),
        status=404,
        mimetype='application/json'
    )

# return 500 When any there are server errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"server encounter error {error.name} and returning status code 500")
    return app.response_class(
        response=json.dumps({"data": f"Error: The server encounter an error of {error}"}),
        status=500,
        mimetype='application/json'
    )

@app.route('/')
def home():
    app.logger.info("A request is received for loading home page")
    return render_template('index.html')

# @app.route('/lazer')
# def lazer():
#     app.logger.info("A request is received for loading /lazer page")
#     return render_template('lazer.html')

@app.route("/update/<sub_path>")
def update_sub(sub_path):
    if sub_path == "info":
        app.logger.info(f"/update/{sub_path}: received a request")
        output = scrape_status()

        app.logger.info(f"/update: finished scrapping and return response")
        response = app.response_class(
            response=json.dumps({"data": output}),
            status=200,
            mimetype='application/json'
        )

        return response
    else:
        app.logger.error(f"/update/: Invalid path")
        return app.response_class(
            response=json.dumps({"error": f"path /{sub_path} not found"}),
            status=404,
            mimetype='application/json'
        )

@app.route("/update")
def update():
    app.logger.info(f"/update: received a request")
    try:
        process_to_JSON.process_update = ""
        if not update_status:
            start_time = time.time()
            thread_event.set()
            thread = threading.Thread(target=scrap_file_and_data())
            thread.start()
            end_time = time.time()
            elapsed_time = end_time - start_time

            output = {
                "status": "updated",
                "finished-time": datetime.datetime.now(pytz.timezone('America/Vancouver')).strftime("%Y-%m-%d %H:%M:%S"),
                "duration": f"{elapsed_time:.2f}s"
            }

            app.logger.info(f"/update: finished scrapping and return response")
            response = app.response_class(
                response=json.dumps({"data": output}),
                status=200,
                mimetype='application/json'
            )
            return response
    except Exception as e:
        app.logger.error(f"/update: Error in loading file - {e}")
        abort(500)

@app.route("/search/info")
def search_info():
    app.logger.info(f"/search/info: received a request")
    # if o2_status:
    #     output = {"ai": Obj2AI.gemini_update,
    #               "file_ready": not o2_status}
    # else:
    output = {"ai": o2_output_info,
              "file_ready": not o2_status}

    app.logger.info(f"/search: finished scrapping and return response")
    response = app.response_class(
        response=json.dumps({"data": output}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/search", methods=["POST"])
def search():
    try:
        file_data = request.json
        app.logger.info(f'/search: received a request of {file_data["data"]["search-terms"]}')

        # if file_data["data"]["ai"] is True:
        #     app.logger.info(f'/search: AI enabled. With prompt {file_data["data"]["prompt"]}')

        file_list = file_filter(file_data["data"]["files"], file_data["data"]["categories"])

        if len(file_list) != 0:
            print(len(file_list), "Length of the file list")
            app.logger.info(f'/search: is going to search {len(file_list)} files')
            return generate_response(
                file_data["data"]["search-terms"],
                file_list, file_data["data"]["ai"], file_data["data"]["prompt"],
                file_data["data"]["section"])
        else:
           app.logger.error(f"/search: receive an empty query and returning status code 404")
           output = "Error: There are no valid file can be search or all files and categories are empty. Please select " \
                    "files or categories from the search list"
           return app.response_class(
               response=json.dumps({"data": output}),
               status=404,
               mimetype='application/json'
           )
    except Exception as e:
        app.logger.error(f"/search: Error in loading file - {e}")
        abort(500)


@app.route("/data")
def data():
    app.logger.info(f"/data: received a request")
    try:
        output = read_data_type_file()

        app.logger.info(f"/data: return {len(output)} files response")
        response = app.response_class(
            response=json.dumps({"data": output}),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception as e:
        app.logger.error(f"/data: Error in loading file - {e}")
        abort(500)

if __name__ == "__main__":
    app.run(debug=config.get('server', 'debug'), port=config.get('server', 'port'))
