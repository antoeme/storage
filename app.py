import json
from flask import Flask,jsonify
import requests
import datetime
import threading
import time

from requests.auth import HTTPBasicAuth

from dotenv import load_dotenv
from os import getenv

#docker run --name postgresdb -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres
#docker exec -tiu postgres postgresdb psql per entrare nella shell del db

GET_TEMP = getenv("GET_TEMP") or  "http://127.0.0.1:5002/temps"  #url che chiama get_temps nel collector
GET_STATUS_RELAYS = getenv("GET_STATUS_RELAYS") or "http://127.0.0.1:5002/status_relays"
DB = "http://127.0.0.1:5003/db"
GET_T = "http://127.0.0.1:5000/temp/"
username = "daniele" or "antonio"
password = "Cisco123" or "Dtlab123"
stop_event = threading.Event()  #variabile evento per lo stop 

# load environment variables from '.env' file
load_dotenv()

app = Flask(__name__)


x = None

app.config['SQLALCHEMY_DATABASE_URI'] =  f'postgresql://{getenv("DB_USER")}:{getenv("DB_PASSWORD")}@{getenv("DB_HOST")}:{getenv("DB_PORT")}/{getenv("DB_NAME")}?sslmode=disable'

# db connection
from models import Storage, db

db.init_app(app)

with app.app_context():
    db.create_all() #crea tutte le tabelle



@app.route('/')
def helloworld():
    return jsonify({"about": " Helloworld !"})



# @app.route('/get_value')
# def get_status():
#     response_temps = requests.get(GET_TEMP,auth=HTTPBasicAuth(username,password))
#     response_status = requests.get(GET_STATUS_RELAYS)
#     with open("output.txt", "a") as f:
#         i = datetime.datetime.now()
#         j = json.dumps(response_temps.json())
#         k = json.dumps(response_status.json())
#         f.write(str(i)+ " "+ str(j) +" "+ str(k) + "\n") 
#         f.close() 
    
#     return "scritto su file valori temps e stati relays"

@app.route('/db')
def write_db():
    response_status = requests.get(GET_STATUS_RELAYS) 
    i = datetime.datetime.now()
    k = json.dumps(response_status.json())
    l = []
    for t in range(4):
        r_t = requests.get(GET_T + str(t+1), auth=HTTPBasicAuth(username,password) )
        s = str (json.dumps(r_t.json()))    #arriva il json che trasformiamo in str
        temp = s[4:-1]
        l.append(float(temp))
    print(l)    
    row = Storage(data = i, t1 = l[0], t2= l[1], t3 = l[2], t4 = l[3], status = str(k) )  #crea la riga da aggiungere al database della classe storage
    db.session.add(row)
    db.session.commit()
    return "aggiunta riga db"

@app.route('/polling_db')
def polling():
    global x    #per dichiarare di usare la variabile globale
    if x is not None:   #controlla che non è già in esecuzione
        return "thread già in esecuzione"
    x = threading.Thread(target=startp, args =(10,), daemon=True) #crea l'oggetto thread per la funzione di polling
    x.start()
    time.sleep(5)
    return "inizio polling db"
        

@app.route('/stop')
def stop_polling():
    global x
    stop_event.set() #setta l'evento per stoppare il ciclo while
    x.join()    #esegue la join con il main thread 
    stop_event.clear()
    x = None
    
    return "stopped polling"

@app.route('/query')
def query():
    temps = str(Storage.query.order_by(Storage.id.desc()).limit(3).with_entities(Storage.temps).all())  #restituisce le ultime 3 occorrenze di temps
    print(type(temps))
    return json.dumps(temps)


def startp(interval):

    while(not stop_event.is_set()):
        
        requests.get(DB)
        time.sleep(interval)
    print("thread stopped")


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=5003)