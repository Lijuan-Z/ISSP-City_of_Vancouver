# ISSP-City_of_Vancouver
This is the main structure of our app. Currently, there is a button on the frontend that, when clicked, triggers the backend to return an Excel file.

# Project Setup Instructions

## Clone the Repository
After cloning the repository, you need to open two terminals: one for the backend and one for the frontend. Follow the instructions below to run them separately.

### Backend (Flask)
in the first terminal, navigate to the Backend Directory:
cd backend

#### Create a Virtual Environment
python -m venv myenv

#### Activate the Virtual Environment
- On Windows:
myenv\Scripts\activate
- On macOS/Linux:
source myenv/bin/activate

#### Install Dependencies
pip install -r requirements.txt

#### Run the Backend
python server.py

#### Check Backend
Open http://localhost:8000/search in the browser. It should display "Hello team!"


### Frontend (React)
in the second terminal, navigate to the Frontend Directory:
cd frontend


#### Install Dependencies
npm install

#### Run the Frontend
npm start

#### Check Frontend
Open http://localhost:3000/searching in the browser. There should be a "Search" button.
