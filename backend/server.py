import time
from search_term import searching_endpoint
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

# Generate Excel file based on the query
def generate_response(query):
    start_time = time.time()
    output_str = searching_endpoint(query)
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

###### Any pre-server start running code run here ######
# read pdf
# save to json

# return 404 Not found for non-exist route
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# return 500 When any there are server errors
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"server encounter error ${error.name} and returning status code 500")
    return render_template('500.html'), 500


@app.route("/search")
def search():
    try:
        query = request.args.get('q').split(",")  # Get the search query parameter

        app.logger.info(f"/search: received a request of ${query}")
        if query is not None:
            ###### Any query function run here #######
            return generate_response(query)
        else:
           app.logger.error(f"/search: receive an empty query and returning status code 404")
           abort(404)
    except:
        abort(500)

@app.route("/update")
def update():
    app.logger.info(f"/update: received a request")
    try:
        ### pdf downloading process ###
        with open('doc_type.json', "r") as file:
        # with open(config.get('server', 'doc_file'), "r") as file:
            data = json.load(file)

            output = [{k: {'type': v['type'], 'title': v['title'], 'url': v['url']} for k, v in obj.items()} for obj in data]
            list(output)
            output = {
                "last-updated": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                "data": output
            }
            response = app.response_class(
                response=json.dumps({"data": output}),
                status=200,
                mimetype='application/json'
            )
        return response
    except Exception as e:
        app.logger.error(f"/update: Error in loading file - {e}")
        abort(500)




if __name__ == "__main__":
    app.run(debug=config.get('server', 'debug'), port=config.get('server', 'port'))
