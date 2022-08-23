import json
from flask import Flask,jsonify, request
import requests
import datetime
import threading
import time

from requests.auth import HTTPBasicAuth

from dotenv import load_dotenv
from os import getenv

#docker run --name postgresdb -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres
#docker exec -tiu postgres postgresdb psql per entrare nella shell del db

NUM_SENSORI = 4
GET_TEMP = getenv("GET_TEMP") or  "http://127.0.0.1:5002/temps"  #url che chiama get_temps nel collector
GET_STATUS_RELAYS = getenv("GET_STATUS_RELAYS") or "http://127.0.0.1:5002/status_relays"
DB = "http://127.0.0.1:5003/db"
GET_T = "http://127.0.0.1:5000/temp/"
URL_STATS = "http://127.0.0.1:5005/transfer"

username = "daniele" or "antonio"
password = "Cisco123" or "Dtlab123"
stop_event = threading.Event()  #variabile evento per lo stop 

# load environment variables from '.env' file
load_dotenv()

app = Flask(__name__)


x = None

app.config['SQLALCHEMY_DATABASE_URI'] =  f'postgresql://{getenv("DB_USER")}:{getenv("DB_PASSWORD")}@{getenv("DB_HOST")}:{getenv("DB_PORT")}/{getenv("DB_NAME")}?sslmode=disable'

# db connection
from models import Stats, Storage, db

db.init_app(app)

with app.app_context():
    db.create_all() #crea tutte le tabelle



@app.route('/db')
def write_db():
    response_status = requests.get(GET_STATUS_RELAYS) 
    i = datetime.datetime.now()
    k = json.dumps(response_status.json())
    l = []
    for t in range(NUM_SENSORI):
        r_t = requests.get(GET_T + str(t+1), auth=HTTPBasicAuth(username,password) )    #fa la get al singolo sensore per la temp
        s = str (json.dumps(r_t.json()))    #arriva il json che trasformiamo in str
        t_s = s[4:-1]  #elimina caratteri non utili
        row = Storage(data = i, id_sens = t+1, temp = float(t_s) , status = str(k) )  #crea la riga da aggiungere al database della classe storage
        db.session.add(row)
        db.session.commit()
        print("aggiunta riga sensore ", t+1)
       
    return "aggiunte temperature in db"

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


@app.route('/query/<int:id_t>', methods=[ 'GET','POST'])
def query(id_t):
    l = []
    temps = (Storage.query.order_by(Storage.id.desc()).filter_by(id_sens=int(id_t)).with_entities(Storage.temp).all())  #restituisce tutte le occorrenze di id_t 
        
    #print(temps)
    for t in range(len(temps)):
        s = str(temps[t])
        chars = '(),'
        res = s.translate(str.maketrans('','',chars))
        l.append(float(res)) #
    #print((l))
 
    return json.dumps(l)

def startp(interval):

    while(not stop_event.is_set()):
        
        requests.get(DB)
        time.sleep(interval)
    print("thread stopped")

@app.route('/statistiche', methods=[ 'GET','POST'] )
def stats():

    d = request.json    #catturiamo la post ricevuta dal modulo compute
    for i in range(len(d)):
        dict = d[i]
        id_s = dict["id_sensore"]
        minimo = dict["min"]
        massimo = dict["max"]
        m = dict["media"]
        dev = dict["devs"]
        row = Stats(id_sens = int(id_s), media = float(m), devs = float(dev), min = float(minimo), max = float(massimo))
        db.session.add(row)
        db.session.commit()
        print("aggiunta riga sensore ", id_s," per tabella statistiche")
    
   
    return "catturate statistiche"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=5003)