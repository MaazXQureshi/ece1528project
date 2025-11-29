import paho.mqtt.client as mqtt
import json, requests, queue, threading
from time import sleep
import numpy as np

mqtt_broker_ip = "127.0.0.1" #change this to the broker IP

mqtt_sensor_topic = "Sen_Data"
mqtt_spill_topic = "Spill_Flag"
mqtt_act_topic = "Act_Data"
mqtt_reg_topic = "Reg_Msg"

interval_Act_Data = 10 #in seconds

url = "http://143.198.33.14:8080/"
idx_reading = "readings"
idx_threshold = "threshold"
idx_cleaning = "cleaning"
idx_spill = "spilling"

dic_bottles = {}
dic_topics_act = {}
bottle_id = []
bottle_reg_flag = [False]*10
spill_flag = [False]*10
active_flag = [False]*10
spill_seq = [-1]*10

FIFO = queue.Queue()
keepRunning = threading.Event()
keepRunning.set()

def query(url, method, payload=None):
    try:
        response = requests.Response()
        if method == "GET":
            response = requests.get(url)
            return json.loads(response.content)
        elif method == "POST":
            requests.post(url, data=json.dumps(payload), headers={"content-type": "application/json"})
        elif method == "PUT":
            requests.put(url, data=json.dumps(payload),headers={"content-type": "application/json"})
        else:
            print("Invalid method in query")
        return
    except:
        print(method + "-Connection error-" + url)

def bottle_register(dict_id):
    bottle_id.append(dict_id) 
    bottle_reg_flag[dict_id] = True
    dic_bottles[dict_id] = {"th": -1.0, "clean": False}
    dic_topics_act[dict_id] = mqtt_act_topic + "_" + str(dict_id)
    active_flag[dict_id] = True
    print("Bottle " + str(dict_id) + " registered.")
    return

def bottle_deregister(dict_id):
    bottle_reg_flag[dict_id] = False
    bottle_id.remove(dict_id)
    del dic_bottles[dict_id]
    del dic_topics_act[dict_id]
    active_flag[dict_id] = False
    print("Bottle " + str(dict_id) + " deregistered.")
    return

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
