# ISSP-City_of_Vancouver
This application is for the PDS data optimization project of the City of Vancouver. Currently, it has fulfilled three objectives:
1) Identify Documents Referencing Specific Terms.
2) Utilize AI for Consequential Amendments.
3) Support Digitization of Policies/Regulations.

# Project Setup Instructions

## Clone the Repository
After cloning the repository, open a terminal and navigate to the Backend directory:

# Project Setup Instructions

## Clone the Repository
After cloning the repository. open one terminal, navigate to the Backend Directory:
cd backend

## Create a Virtual Environment
python -m venv myenv

## Activate the Virtual Environment
- On Windows:
myenv\Scripts\activate
- On macOS/Linux:
source myenv/bin/activate

## Install Dependencies
pip install -r requirements.txt

## Copy config.py
Copy credential.ini to the backend folder.

## Run the Backend
python server.py

## Check Backend
Open http://localhost:8000/ in the browser. It should display the main page of app.
