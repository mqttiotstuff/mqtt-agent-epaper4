import umqttsimple

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

import display

ssid = '********'
password = '*************'

mqtt_server = 'mqtt.frett27.net'
#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'home/esp27/actuators/epaper4'


topic_main = b'home/esp27'
topic_health_check = b'home/esp27/sensors/health'
topic_errors = b'home/esp27/errors'


last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
try:
    station.connect(ssid, password)
    print("connecting")
except:
    print("error connecting to wifi")
    time.sleep(3)
    machine.reset()
    
while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

client = None

print('init the display')
# init paper  
import epaper4in2
from machine import Pin, SPI

#SPI2_HOST (FSPI) 	SCK 	GPIO12 	#SPI0_SCK 	can be used
#SPI2_HOST (FSPI) 	MOSI 	GPIO11 	#SPI0_MOSI 	can be used
#SPI2_HOST (FSPI) 	MISO 	GPIO13 	#SPI0_MISO 	can be used
#SPI2_HOST (FSPI) 	CS0 	GPIO10 	#SPI0_CS0 	can be used 

sck = Pin(12)
miso = Pin(13)
mosi = Pin(11)

dc = Pin(2)
cs = Pin(4)
rst = Pin(6)
busy = Pin(8)
spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=sck, miso=miso, mosi=mosi)

e = epaper4in2.EPD(spi, cs, dc, rst, busy)
e.init()

d = display.DisplayServer(e, 400, 300)
d.clear()
d.update()



def sub_cb(topic, msg):
  global client, topic_pub, d
  # print("executing " + str(msg))
  try:
      d.execute(msg)
  except Exception as e:
      print(str(e))
      client.publish(topic_errors, str(e))

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, port=1883, user="sys", password="ufdx80wu")
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(5)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()
  


client.publish(topic_main, b'epaper4')

main_sleep = 0.05
cpt = 2 / main_sleep
while True:
  try:
    new_message = client.check_msg()
    #if new_message != 'None':
    cpt = cpt - 1
    if cpt < 0:
        cpt = 2 / main_sleep
        gc.collect()
        client.publish(topic_health_check, "" + str(gc.mem_free()))
    
    time.sleep(main_sleep)
  except OSError as e:
    restart_and_reconnect()

