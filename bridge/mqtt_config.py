import paho.mqtt.client as mqtt
import logging, json, requests
from time import sleep
import numpy as np

mqtt_broker_ip = "127.0.0.1"
mqtt_sensor_topic = "MQTT_Sensor_Data"
mqtt_actuator_topic = "MQTT_Actuator_Cmd"

url = "http://143.198.33.14:8080/"
idx_reading = "readings"
idx_th = "threshold"
idx_cleaning = "cleaning"

dic_bottles = {}
bottle_id = np.zeros(3, dtype=np.bool)

def query(url, method, payload=None):
    try:
        res = requests.Response()
        if method == "GET":
            res = requests.get(url)
        if method == "POST":
            res = requests.post(
                url,
                data=json.dumps(payload),
                headers={"content-type": "application/json"},
            )
        if method == "PUT":
            res = requests.put(
                url,
                data=json.dumps(payload),
                headers={"content-type": "application/json"},
            )
        if method == "DELETE":
            res = requests.delete(url)
        if res.content is not None:
            logging.debug(
                "HTTP - [" + method + "][" + str(res.status_code) + "][" + url + "]"
            )
            return json.loads(res.content.decode("utf8"))
    except:
        logging.error("HTTP - " + method + " - Connection error!")

def on_connect(client, userdata, flags, rc):
    logging.info("MQTT - connected to broker, code " + str(rc))


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    payloadJson = json.loads(msg.payload.decode("utf-8"))
    dict_id = int(payloadJson["bottle_id"])
    if bottle_id[dict_id] == False:
        bottle_id[dict_id] = True
        dic_bottles[dict_id] = {"threshold": -1, "cleaning": 0}
    del payloadJson["bottle_id"]
    query(url=url + idx_reading + "/" + str(dict_id), method="POST", payload=payloadJson)
    logging.info("MQTT - msg received [" + msg.topic + "]: " + payload)

def on_message_test(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    logging.info("MQTT - msg received [" + msg.topic + "]: " + payload)


def on_subscribe(client, userdata, mid, granted_qos):
    logging.info("MQTT - subscribed: " + str(mid) + " " + str(granted_qos))


def on_publish(client, userdata, mid):
    logging.info("MQTT - published:  " + str(mid))


def connect(ip, port=1883):
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    try:
        mqttc.connect(ip, port, 60)
    except:
        logging.error(
            "MQTT - [" + ip + ":" + str(port) + "] connection failed!, exiting..."
        )
        exit(1)
    return mqttc

def connect_test(ip, port=1883):
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message_test
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    try:
        mqttc.connect(ip, port, 60)
    except:
        logging.error(
            "MQTT - [" + ip + ":" + str(port) + "] connection failed!, exiting..."
        )
        exit(1)
    return mqttc