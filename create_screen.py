#!/bin/python3

import configparser
import os
import paho.mqtt.client as mqtt
import time

import traceback

import json
from jsonpath_ng import jsonpath, parse
import rasterizer
import base64 

EPAPER_TOPIC = "home/esp27"
EPAPER_COMMAND_TOPIC = EPAPER_TOPIC + "/actuators/epaper4"

EPAPER_AGENT = "home/agents/epaperinfo"

config = configparser.RawConfigParser()

conffile = os.path.expanduser('~/.mqttagents.conf')
if not os.path.exists(conffile):
   raise Exception("config file " + conffile + " not found")

config.read(conffile)


username = config.get("agents","username")
password = config.get("agents","password")
mqttbroker = config.get("agents","mqttbroker")

client = mqtt.Client()
client.username_pw_set(username, password)

client2 = mqtt.Client()
client2.username_pw_set(username, password)

def on_connect(client, userdata, flags, rc):
    try:
        print("connected")
        with open("result.json", "r") as f:
            r = json.loads(f.readline())
            exp = parse('$.weather[0].description')

            result = rasterizer.construct_image("Meteo.svg", {"degres": "12" })

            client2.publish(EPAPER_COMMAND_TOPIC,"d.clear()")
            for r in result:
                (x,y,w,h,b) = r
                f = f"p = p64(\"{base64.b64encode(b).decode('utf-8')}\", {w}, {h})\nd.picture(p, {x}, {y})"
                client2.publish(EPAPER_COMMAND_TOPIC, f)
                
            print("send the change to screen")
            client2.publish(EPAPER_COMMAND_TOPIC,"d.update()")
    except:
        traceback.print_exc()

client.on_connect = on_connect
client.connect(mqttbroker, 1883, 60)
client2.connect(mqttbroker, 1883, 60)

client.loop_start()
client2.loop_start()
while True:
    time.sleep(1)

