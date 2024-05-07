from flask import Flask, request, make_response
from flask_cors import CORS
import pandas as pd
import io

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


@app.route("/search")
def search():
    query = request.args.get('q')  # Get the search query parameter
    if query:
        return generate_response(query)
    else:
        return "Hello team!"
    

if __name__ == "__main__":
    app.run(debug=True, port=8000)
