import paho.mqtt.client as mqtt
import json, requests, queue, threading
from time import sleep
import numpy as np

mqtt_broker_ip = "127.0.0.1"
mqtt_sensor_topic = "Sen_Data"
mqtt_actuator_topic = "Act_Data"
mqtt_registration = "Reg_Msg"
interval_Act_Data = 10 #in seconds

url = "http://143.198.33.14:8080/"
idx_reading = "readings"
idx_threshold = "threshold"
idx_cleaning = "cleaning"

dic_bottles = {}
dic_topics_act = {}
bottle_id = []
flag_id = [False]*10
FIFO = queue.Queue()

def query(url, method, payload=None):
    try:
        response = requests.Response()
        if method == "GET":
            response = requests.get(url)
        if method == "POST":
            response = requests.post(url, data=json.dumps(payload), headers={"content-type": "application/json"})
            print(method + " - " + str(response.status_code) + " - " + url)
        if response.content is not None:
            return json.loads(response.content)
    except:
        print(method + " - Connection error - " + url)

def bottle_register(dict_id):
    bottle_id.append(dict_id) 
    flag_id[dict_id] = True
    dic_bottles[dict_id] = {"threshold": -1.0, "cleaning": 0}
    dic_topics_act[dict_id] = mqtt_actuator_topic + "_" + str(dict_id)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQT broker - rc:" + str(rc))


def on_message(client, userdata, msg):
    FIFO.put(msg)

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
