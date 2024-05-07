from flask import Flask, request, make_response, render_template, abort
from flask_cors import CORS
import pandas as pd
import io
import configparser

# config file for information management
config = configparser.ConfigParser()
config.read('development.ini')

app = Flask(__name__)
CORS(app)

# Generate Excel file based on the query
def generate_response(query):
    # This is a simple example file.
    df = pd.DataFrame({'Data': [1, 2, 3, 4, 5]})
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)  # Reset file pointer to the beginning
    
    # Create response object
    response = make_response(output.getvalue())
    
    # Set headers
    response.headers["Content-Disposition"] = f"attachment; filename={query}.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response

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

    query = request.args.get('q')  # Get the search query parameter
    app.logger.info(f"/search received a request of ${query}")
    if query is not None:
        return generate_response(query)
    else:
       app.logger.error(f"/search receive an empty query and returning status code 404")
       abort(404)




if __name__ == "__main__":
    app.run(debug=config.get('server', 'debug'), port=config.get('server', 'port'))
