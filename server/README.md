
## Description
Flask API with session and JWT authentication that allows users to manage personal notes.
Users can sign up, log in, stay logged in via sessions, and perform CRUD actions on their own notes.


## Setup
pipenv install  
pipenv shell  
flask db upgrade  
python seed.py  

## Run
flask run -p 5555

## Endpoints
POST /signup  
POST /login  
DELETE /logout  
GET /check_session  
GET /notes  
POST /notes  
PATCH /notes/<id>  
DELETE /notes/<id>  
