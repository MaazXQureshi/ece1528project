import paho.mqtt.client as mqtt
import json, requests
from time import sleep
import numpy as np

mqtt_broker_ip = "127.0.0.1"
mqtt_sensor_topic = "Sen_Data"
mqtt_actuator_topic = "Act_Data"
mqtt_registration = "Reg_Msg"

url = "http://143.198.33.14:8080/"
idx_reading = "readings"
idx_threshold = "threshold"
idx_cleaning = "cleaning"

dic_bottles = {}
dic_topics_act = {}
bottle_id = np.zeros(3, dtype=bool)

def query(url, method, payload=None):
    try:
        response = requests.Response()
        if method == "GET":
            response = requests.get(url)
        if method == "POST":
            response = requests.post(url, data=json.dumps(payload), headers={"content-type": "application/json"})
            print(method + " - " + str(response.status_code) + " - " + url)
        if response.content is not None:
            return json.loads(response.content.decode("utf-8"))
    except:
        print(method + " - Connection error - " + url)

def bottle_register(dict_id):
    bottle_id[dict_id] = True
    dic_bottles[dict_id] = {"threshold": -1.0, "cleaning": 0}
    dic_topics_act[dict_id] = mqtt_actuator_topic + "_" + str(dict_id)


def on_connect(client, userdata, flags, rc):
    print("Connected to MQT broker - rc:" + str(rc))


def on_message(client, userdata, msg):
    payloadJson = json.loads(msg.payload)
    dict_id = int(payloadJson["id"])
    if msg.topic == mqtt_registration:
        print("MQTT - msg received - " + msg.topic + " - " + str(payloadJson))
        bottle_register(dict_id)
    else:
        # Only post the data when it is not a registration message.
        del payloadJson["id"]
        print("MQTT - msg received - " + msg.topic + " - " + str(payloadJson))
        try:
            payloadJson={"volume":payloadJson["vol"],"roll":payloadJson["rol"],"pitch":payloadJson["pit"],"yaw":payloadJson["yaw"],"temperature":payloadJson["temp"]} #change this
            query(url=url + idx_reading + "/" + str(dict_id), method="POST", payload=payloadJson)
        except:
            print("Error posting sensor data for bottle " + str(dict_id))

def on_message_test(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    print("MQTT - msg received - " + msg.topic + " - " + payload)


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
