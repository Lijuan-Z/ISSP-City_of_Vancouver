import time
# from search_term import searching_endpoint
from search import search_files
from obj3_v2 import enter_obj3
import scrape
from scrape import download_source_html, download_pdf, download_pdf_voc_bylaws, retrieve_document_type
from flask import Flask, request, make_response, render_template, abort
from flask_cors import CORS
import threading
import json
import pandas as pd
import io
import configparser

from output_handler import OutputHandler

thread_event = threading.Event()

# config file for information management
config = configparser.ConfigParser()
config.read('development.ini')

app = Flask(__name__)
# app._static_folder = "_next/static"
CORS(app)

update_status = False


# Generate Excel file based on the query
def generate_response(query, files):
    start_time = time.time()
    excel_file_path = "output.xlsx"
    # output_str = searching_endpoint(query)
    # output_dict = search_files(files, json_path="processed_final.json", search_terms=query)
    try:
        output_dict = search_files(files, json_path=config.get('server', 'processed_json_file'), search_terms=query)
        OutputHandler.create_excel_file(output_dict, output_file=excel_file_path)
    except Exception as e:
        msg = f"There is an error when searching from AI. code: {e}"
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
            retrieve_document_type(source_html_cov, source_html_bylaw, output_file)

            update_status = False

        thread_event.clear()

def scrape_status():
        total_file_to_update = 590
        percentage_updated = float(scrape.file_counter / total_file_to_update * 100)

        status_message = "Idle"
        if update_status:
            status_message = "Updating"

        return {
            "status": status_message,
            "file_updated": scrape.file_counter,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
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
            scrap_file_and_data()
            end_time = time.time()
            elapsed_time = end_time - start_time

            output = {
                "status": "updated",
                "finished-time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
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
    output = "searching file 3 of xxxx.pdf"

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
            app.logger.info(f'/search/o3: is going to search {len(file_list)} files')
            
            # obj3_data = enter_obj3(file_list)   # temp gen output objective 3
            # response = make_response(obj3_data)
            # response.headers["Content-Disposition"] = f"attachment; filename=output_o3.xlsx"
            # response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            output = f"requesting AI to generate report for {len(file_list)} files"
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
    try:
        file_data = request.json
        app.logger.info(f'/search: received a request of {file_data["data"]["search-terms"]}')

        file_list = file_filter(file_data["data"]["files"], file_data["data"]["categories"])

        if len(file_list) != 0:
            print(file_list)
            app.logger.info(f'/search: is going to search {len(file_list)} files')
            return generate_response(file_data["data"]["search-terms"], file_list)
        else:
           app.logger.error(f"/search: receive an empty query and returning status code 404")
           abort(404)
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

@app.route("/data/o3")
def data_o3():
    app.logger.info(f"/data/o3: received a request")
    try:
        output_msg = "Asking AI to generate file - step (2/10) of zoning-by-law-district-schedule-fc-1.pdf"
        output_msg = "Asking AI to generate file - step (6/10) of zoning-by-law-district-schedule-r1-1.pdf"
        # output_msg = "finished excel creation output_03.xlsx in folder /LZR"

        o3_file_status = False

        output = {"data": output_msg,
                  "is_created": o3_file_status}

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
