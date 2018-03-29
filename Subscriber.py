import json, os
import sqlite3 as sql
try:
    import paho.mqtt.client as mqtt
except:
    os.system('sudo pip3 install paho-mqtt')    #if module not present, installs it and runs again
    os.system('python3 Subscriber.py')
from datetime import date, datetime

"""connects to the data topic"""
def on_connect(client, userdata, flag, rc):
        client.subscribe("owntracks/user/ALL Project2")

"""what is done every time a new message gets posted to the topic"""
def on_message(client, userdata, msg):
    con = sql.connect('location.db') #opens the database, if not present, creates one
    cur = con.cursor()  #for executing sql queries
    try:
        cur.execute("CREATE TABLE Location(longitude NUMBER(10,6), latitude NUMBER(10,6), date VARCHAR2(20), time VARCHAR2(20));") #creates the table with the necessary parameters for storing values
    except:
        pass #if it's already created, then use that one
    data = json.loads(msg.payload.decode("utf8"))
    day = date.today()
    clock = datetime.now()
    time = datetime.time(clock)
    cur.execute("INSERT INTO Location values(?,?,?,?);", (data["lon"], data["lat"], str(day), str(time))) #puts the latitude, longitude from the posted message as well as the date and time when it was posted into the database
    con.commit()
    cur.close()
    con.close()
try:  
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("iot.eclipse.org") #connects throught the given broker
    client.loop_forever()  #loops, so that new data can continuously be accepted
except Exception as e:
    print(e)
