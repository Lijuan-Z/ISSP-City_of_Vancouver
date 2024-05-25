import time, datetime, pytz
# from search_term import searching_endpoint
from search import search_files
# from GeminiAPI import GeminiAPI
import GeminiAPI
import process_to_JSON
import obj3_v2
from obj3_v2 import enter_obj3
import scrape
from scrape import download_source_html, download_pdf, download_pdf_voc_bylaws, retrieve_document_type, read_previous_source
from flask import Flask, request, make_response, render_template, abort
from flask_cors import CORS
import threading
import json
import pandas as pd
import io
import configparser

from output_handler import OutputHandler

thread_event = threading.Event()
thread_event_o3 = threading.Event()

# config file for information management
config = configparser.ConfigParser()
config.read('development.ini')

# preload the stored doc_type.json for retreiving last update date
latest_doc_type = read_previous_source(config.get('server', 'doc_file'))
last_update_date = max(list([list(obj.values())[0]["Last update"] for obj in latest_doc_type]))

app = Flask(__name__)
# app._static_folder = "_next/static"
CORS(app)
gemini = GeminiAPI.GeminiAPI()
update_status = False
o3_status = False

def o3_handler(file_list):
    global  o3_status
    o3_status = True
    enter_obj3(file_list)
    o3_status = False


# Generate Excel file based on the query
def generate_response(query, files, enable_ai, prompt):
    start_time = time.time()
    excel_file_path = "output.xlsx"
    # output_str = searching_endpoint(query)
    try:
        output_dict = search_files(files, json_path=config.get('server', 'processed_json_file'), search_terms=query)
        if enable_ai is True:
            # For objective 2 - enable Gemini - API AI
            output_dict = gemini.get_amendment_and_rationale(output_dict, prompt)
        OutputHandler.create_excel_file(output_dict, output_file=excel_file_path)
    except Exception as e:
        msg = f"There is either no information for output or an error when searching {query}. code: {e}"
        print(msg)
        output_excel = pd.DataFrame({'Error': {"message": msg}})
        output_excel.to_excel(excel_file_path)
    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        # Print the elapsed time
        print("Elapsed time:", elapsed_time, "seconds")

    with open(excel_file_path, "rb") as file:
        file_data = file.read()

    # Create response object
    response = make_response(file_data)
    
    # Set headers
    response.headers["Content-Disposition"] = f"attachment; filename=output.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response

# Handling web-scrapping of PDF and document-type json file
def scrap_file_and_data():
    global update_status
    global last_update_date

    while thread_event.is_set():
    ### html, pdf & doc-type json download process ###
        if config.getboolean('scrap', 'download'):
            update_status = True

            # URL of the website to scrape
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
            "percentage_updated": f"{percentage_updated:.2f}"
        }



def read_data_type_file():
    # open stored doc-type file and return update info
    with open(config.get('server', 'doc_file'), "r") as file:
        data = json.load(file)

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
    ### file filtering is done here ####
    if len(category) == 0:
        return file_names
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
    return render_template('404.html'), 404

# return 500 When any there are server errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"server encounter error {error.name} and returning status code 500")
    return render_template('500.html'), 500

@app.route('/')
def home():
    app.logger.info("A request is received for loading home page")
    return render_template('index.html')

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
    output = {"ocr": process_to_JSON.process_update,
              "ai": GeminiAPI.gemini_update}

    app.logger.info(f"/search: finished scrapping and return response")
    response = app.response_class(
        response=json.dumps({"data": output}),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/search/o3", methods=["POST"])
def search_o3():
    try:
        file_data = request.json
        app.logger.info(f'/search/o3: received a request')

        # This is my function to filter the restricted list of files for objective 3
        file_list = file_filter(file_data["data"]["files"], file_data["data"]["categories"])
        # file_list = ["zoning-by-law-district-schedule-fc-1", "zoning-by-law-district-schedule-r1-1"]
        if len(file_list) != 0:
            print(file_list)

            # thread_o3 = threading.Thread(target=enter_obj3, args=[file_list], daemon=True)
            output = ""
            if not o3_status:
                app.logger.info(f'/search/o3: is going to extract data from {len(file_list)} files')
                output = f"requesting AI to generate report for {len(file_list)} files"
                thread_o3 = threading.Thread(target=o3_handler, args=[file_list], daemon=True)
                thread_o3.start()
            else:
                app.logger.info(f'/search/o3: is busy extracting data for {len(file_list)} files')
                output = f"AI is generating report for {len(file_list)} files. Request ignored"


            app.logger.info(f"/search/o3: is returning a response")
            response = app.response_class(
                response=json.dumps({"data": output}),
                status=200,
                mimetype='application/json'
            )

            return response
        else:
           app.logger.error(f"/search/o3: receive an empty query and returning status code 404")
           abort(404)
    except Exception as e:
        app.logger.error(f"/search: Error in loading file - {e}")
        abort(500)

@app.route("/search", methods=["POST"])
def search():
    # try:
        file_data = request.json
        app.logger.info(f'/search: received a request of {file_data["data"]["search-terms"]}')

        if file_data["data"]["ai"] is True:
            app.logger.info(f'/search: AI enabled. With prompt {file_data["data"]["prompt"]}')

        file_list = file_filter(file_data["data"]["files"], file_data["data"]["categories"])

        if len(file_list) != 0:
            print(file_list)
            app.logger.info(f'/search: is going to search {len(file_list)} files')
            return generate_response(file_data["data"]["search-terms"], file_list, file_data["data"]["ai"], file_data["data"]["prompt"])
        else:
           app.logger.error(f"/search: receive an empty query and returning status code 404")
           abort(404)
    # except Exception as e:
    #     app.logger.error(f"/search: Error in loading file - {e}")
    #     abort(500)

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

@app.route("/data/o3")
def data_o3():
    app.logger.info(f"/data/o3: received a request")
    try:
        # need to check whether output_o3.xlsx exist
        output = {"data": obj3_v2.o3_message,
                  "is_created": False}

        app.logger.info(f"/data: returning {len(output)} files response")
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
