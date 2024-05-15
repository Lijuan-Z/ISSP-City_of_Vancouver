import time
from search_term import searching_endpoint
from scrape import download_source_html, download_pdf, retrieve_document_type
from flask import Flask, request, make_response, render_template, abort
from flask_cors import CORS
import json
import pandas as pd
import io
import configparser

from output_handler import OutputHandler

# config file for information management
config = configparser.ConfigParser()
config.read('development.ini')

app = Flask(__name__)
CORS(app)

update_status = False
file_counter = 0

# Generate Excel file based on the query
def generate_response(query, files):
    start_time = time.time()
    output_str = searching_endpoint(query)
    # output_str = searching_endpoint(query, files)
    OutputHandler.create_excel_file(output_str)
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Print the elapsed time
    print("Elapsed time:", elapsed_time, "seconds")
    
    

    excel_file_path = "output.xlsx"
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
    ### html, pdf & doc-type json download process ###
    if config.getboolean('scrap', 'download'):
        update_status = True

        # URL of the website to scrape
        website_url = config.get('scrap', 'cov_url')
        # Directory to save the downloaded PDFs
        save_directory = config.get('scrap', 'pdf_folder')
        # Output file name for document_type json data
        output_file = config.get('server', 'doc_file')

        app.logger.info("/update: server is downloading html file from")
        source_html = download_source_html(website_url)
        app.logger.info("/update: server finished downloading html. Now downloading pdf files")
        total_downloaded = download_pdf(source_html, website_url, save_directory)
        app.logger.info(f"/update: server finished downloading {total_downloaded} pdf files. Now creating doc-type-json file")
        retrieve_document_type(source_html, output_file)

        update_status = False

def scrape_status():
        # tmp:
        file_counter = 2
        total_file_to_update = 10
        percentage_updated = int(file_counter / total_file_to_update * 100)
        #

        status_message = "Idle"
        if update_status:
            status_message = "Updating"

        return {
            "status": status_message,
            "file_updated": file_counter,
            "last-updated": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "total-updated-files": total_file_to_update,
            "percentage_updated": percentage_updated
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
    return ""

# return 404 Not found for non-exist route
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# return 500 When any there are server errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"server encounter error ${error.name} and returning status code 500")
    return render_template('500.html'), 500


@app.route("/search", methods=["POST"])
def search():
    try:
        # query = request.args.get('q').split(",")  # Get the search query parameter
        file_data = request.json
        app.logger.info(f'/search: received a request of {file_data["data"]["search-terms"]}')

        file_list = file_filter(file_data["data"]["files"], file_data["data"]["categories"])

        if file_data["data"] is not None:
            return generate_response(file_data["data"]["search-terms"], file_list)
        else:
           app.logger.error(f"/search: receive an empty query and returning status code 404")
           abort(404)
    except Exception as e:
        app.logger.error(f"/search: Error in loading file - {e}")
        abort(500)

@app.route("/update")
def update():
    app.logger.info(f"/update: received a request")
    try:
        # if not update_status:
            # scrap_file_and_data()

        output = scrape_status()

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

@app.route("/data")
def data():
    app.logger.info(f"/data: received a request")
    # try:
    output = read_data_type_file()

    app.logger.info(f"/data: return {len(output)} files response")
    response = app.response_class(
        response=json.dumps({"data": output}),
        status=200,
        mimetype='application/json'
    )
    return response
    # except Exception as e:
    #     app.logger.error(f"/data: Error in loading file - {e}")
    #     abort(500)



if __name__ == "__main__":
    app.run(debug=config.get('server', 'debug'), port=config.get('server', 'port'))
