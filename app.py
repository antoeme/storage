import json
from flask import Flask,jsonify
import requests
import datetime

GET_TEMP = "http://127.0.0.1:5002/temps"  #url che chiama get_temps nel collector
GET_STATUS_RELAYS = "http://127.0.0.1:5002/status_relays"

app = Flask(__name__)

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
        f.write(str(i)+ " "+ j +" "+ k + "\n") 
        f.close() 
    
    return "scritto su file valori temps e stati relays"
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True,port=5003)