#!/bin/python3


import paho.mqtt.client as mqtt
import time
import configparser
import os.path
import json

from jsonpath_ng import jsonpath, parse
import rasterizer
import base64 

import traceback


import time
import locale
locale.setlocale(locale.LC_ALL,'fr_FR.UTF-8')

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
api_key = config.get("weather","api_key")

client2 = mqtt.Client()

# client2 is used to send events to wifi connection in the house 
client2.username_pw_set(username, password)
client2.connect(mqttbroker, 1883, 60)

client = mqtt.Client()
client.username_pw_set(username, password)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("connected")
    pass



def on_message(client, userdata, msg):
   try:
      print("message received")
   except:
      traceback.print_exc();

client.on_connect = on_connect
client.on_message = on_message
client.connect(mqttbroker, 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client2.loop_start()
client.loop_start()

latesttime = time.time() - 3*60*60

while True:
   try:
      time.sleep(3)
      client2.publish(EPAPER_AGENT + "/health", "1")

      # refresh every hour
      if latesttime < time.time() - 60*60:
          print("call weather api")
          # https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}
          import urllib
          import urllib.request

          try:
              response = urllib.request.urlopen(f"https://api.openweathermap.org/data/2.5/weather?lat=45.764430&lon=4.878273&appid={api_key}")
              print("response returned : {}".format(response.status))
              jsoncontent = json.loads(response.read())
              latesttime = time.time()
              exp = parse('$.weather[0].description')
              description = exp.find(jsoncontent)[0].value

              expdegre = parse('$.main.temp')
              v = int(expdegre.find(jsoncontent)[0].value) - 273

              date_display = time.strftime('%A %d/%m/%Y %H:%M:%S')
              result = rasterizer.construct_image("Meteo.svg", {"degres": str(v), "date": date_display })

              client2.publish(EPAPER_COMMAND_TOPIC,"d.clear()")
              for r in result:
                  (x,y,w,h,b) = r
                  f = f"p = p64(\"{base64.b64encode(b).decode('utf-8')}\", {w}, {h})\nd.picture(p, {x}, {y})"
                  client2.publish(EPAPER_COMMAND_TOPIC, f)
                  
              print("send the change to screen")
              client2.publish(EPAPER_COMMAND_TOPIC,"d.update()")
          except:
              traceback.print_exc()

   except Exception:
        traceback.print_exc()


