import json
from flask import Flask,jsonify
import requests
import datetime

from dotenv import load_dotenv
from os import getenv

GET_TEMP = getenv("GET_TEMP") or  "http://127.0.0.1:5002/temps"  #url che chiama get_temps nel collector
GET_STATUS_RELAYS = getenv("GET_STATUS_RELAYS") or "http://127.0.0.1:5002/status_relays"

# load environment variables from '.env' file
load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =  f'postgresql://{getenv("DB_USER")}:{getenv("DB_PASSWORD")}@{getenv("DB_HOST")}:{getenv("DB_PORT")}/{getenv("DB_NAME")}?sslmode=disable'

# db connection
from models import Storage, db

db.init_app(app)

with app.app_context():
    db.create_all() #crea tutte le tabelle


@app.route('/')
def helloworld():
    return jsonify({"about": " Helloworld !"})



@app.route('/get_value')
def get_status():
    response_temps = requests.get(GET_TEMP)
    response_status = requests.get(GET_STATUS_RELAYS)
    with open("output.txt", "a") as f:
        i = datetime.datetime.now()
        j = json.dumps(response_temps.json())
        k = json.dumps(response_status.json())
        f.write(str(i)+ " "+ str(j) +" "+ str(k) + "\n") 
        f.close() 
    
    return "scritto su file valori temps e stati relays"

@app.route('/db')
def write_db():
    response_temps = requests.get(GET_TEMP)
    response_status = requests.get(GET_STATUS_RELAYS) 
    i = datetime.datetime.now()
    j = json.dumps(response_temps.json())
    k = json.dumps(response_status.json())
    row = Storage(data = str(i), temps = str(j), status = str(k) )  #crea la riga da aggiungere al database della classe storage
    db.session.add(row)
    db.session.commit()
    return "aggiunta riga db"


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=5003)