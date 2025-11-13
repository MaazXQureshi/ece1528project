import paho.mqtt.client as mqtt
import json
from time import sleep
import numpy as np

mqtt_broker_ip = "127.0.0.1"
mqtt_sensor_topic = "Sen_Data"
mqtt_actuator_topic = "Act_Data"
mqtt_registration = "Reg_Msg"

initialized = np.zeros(3, dtype=bool)

def on_connect(client, userdata, flags, rc):
    print("Connected to MQT broker - rc:" + str(rc))

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    if initialized[int(msg.topic[-1])] == False:
        initialized[int(msg.topic[-1])] = True 
    print("MQTT - msg received - " + msg.topic + " - " + str(payload))

def on_subscribe(client, userdata, mid, granted_qos):
    print("MQTT - subscribed")

def on_publish(client, userdata, mid):
    print("MQTT - published: " + str(mid))


def connect(ip, port=1883):
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    try:
        mqttc.connect(ip, port, 60)
    except:
        print("MQTT - connection failed")
        exit(1)
    return mqttc