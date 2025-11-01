import paho.mqtt.client as mqtt
import logging, json
from time import sleep
import numpy as np

mqtt_broker_ip = "127.0.0.1"
mqtt_sensor_topic = "MQTT_Sensor_Data"
mqtt_actuator_topic = "MQTT_Actuator_Cmd"

threshold = -1 #threshold value in liters, -1 means no threshold set
mode = -1 #mode can be 0 (normal) or 1 (cleaning mode), -1 means no mode set

def on_connect(client, userdata, flags, rc):
    logging.info("MQTT - connected to broker, code " + str(rc))


def on_message(client, userdata, msg):
    global message
    message = msg
    topic = msg.topic
    payload = str(msg.payload.decode("utf-8"))
    logging.debug("MQTT - msg received [" + topic + "]: " + payload)


def on_subscribe(client, userdata, mid, granted_qos):
    logging.info("MQTT - subscribed: " + str(mid) + " " + str(granted_qos))


def on_publish(client, userdata, mid):
    logging.debug("MQTT - published:  " + str(mid))


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