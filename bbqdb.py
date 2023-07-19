#!/usr/bin/python3

import sys
import hbmqtt
import mariadb


def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    temp = float(msg)
    probe = message.topic.split('/')[3]
    print ('probe',probe,'temp',temp)
    try:
        conn = mariadb.connect(
        user="yourdbuser",
        password="yourpasswword",
        host="localhost",
        database="yourdb"
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bbq (probe,temp) VALUES (?, ?)", (probe, temp))
        conn.commit() 
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")

bbqtopic = 'device/bbq/sensor/+/temperature/announce'

hbclient = hbmqtt.hbclient()
hbclient.subscribe(bbqtopic,on_message)
hbclient.connect()

hbclient.loop_forever()

