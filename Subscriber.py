import json, os
import sqlite3 as sql
try:
    import paho.mqtt.client as mqtt
except:
    os.system('sudo pip3 install paho-mqtt')
    os.system('python3 Subscriber.py')
from datetime import date, datetime
def on_connect(client, userdata, flag, rc):
        client.subscribe("owntracks/user/ALL Project2")

def on_connect(client, userdata, flag, rc):
        client.subscribe("owntracks/user/nanofork")
        
def on_message(client, userdata, msg):
    con = sql.connect('location.db')
    cur = con.cursor()
    try:
        cur.execute("CREATE TABLE Location(longitude NUMBER(10,6), latitude NUMBER(10,6), date VARCHAR2(20), time VARCHAR2(20));")
    except:
        pass
    data = json.loads(msg.payload.decode("utf8"))
    print(data["lon"],data["lat"])
    day = date.today()
    dat = datetime.now()
    times = datetime.time(dat)
    print(day)
    print(times)
    cur.execute("INSERT INTO Location values(?,?,?,?);", (data["lon"], data["lat"], str(day), str(times)))
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
