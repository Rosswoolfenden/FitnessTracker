import sqlite3 as sql
import paho.mqtt.client as mqtt
from datetime import datetime
import json

def on_connect(client, userdata, flag, rc):
        client.subscribe("owntracks/user/nanofork")
        
def on_message(client, userdata, msg):
    con = sql.connect('location.db')
    cur = con.cursor()
    try:
        cur.execute("CREATE TABLE Location(longitude NUMBER(10,6), latitude NUMBER(10,6), time VARCHAR2(17));")
    except:
        pass
    data = json.loads(msg.payload.decode("utf8"))
    print(data["lon"],data["lat"])
    time = datetime.now()
    print(time)
    cur.execute("INSERT INTO Location values(?,?,?);", (data["lon"], data["lat"], time))
    con.commit()
    cur.close()
    con.close()
try:  
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("iot.eclipse.org")
    client.loop_forever()
except Exception as e:
    print(e)
