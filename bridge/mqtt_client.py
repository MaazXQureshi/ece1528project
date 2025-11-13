from mqtt_config import *
#Change the mqtt_broker_ip and ensure MQTT broker is up

def publish_actuator_commands():
    while keepRunning.is_set():
        for i in bottle_id: 
            try:
                resThresh = query(url=url + idx_threshold + "/" + str(i), method="GET")
                resMode = query(url=url + idx_cleaning + "/" + str(i), method="GET")
                if dic_bottles[i]["threshold"] != resThresh["threshold"] or dic_bottles[i]["cleaning"] != resMode["cleaning"]:
                    dic_bottles[i]["threshold"] = resThresh["threshold"]
                    dic_bottles[i]["cleaning"] = resMode["cleaning"]
                    payload = {"TH":resThresh["threshold"],"CL":resMode["cleaning"]}
                    mqttc.publish(topic=dic_topics_act[i], payload=json.dumps(payload), qos=1)
            except:
                print("Error forwarding actuator data to bottle " + str(i))
        sleep(interval_Act_Data)
def message_processing():
    while keepRunning.is_set():
        if FIFO.empty() == False:
            msg = FIFO.get()
            payloadJson = json.loads(msg.payload)
            print("MQTT - msg processing - " + msg.topic + " - " + str(payloadJson))
            dict_id = int(payloadJson["id"])
            if msg.topic == mqtt_registration:
                bottle_register(dict_id)
            elif flag_id[dict_id]:
                del payloadJson["id"]
                try:
                    payloadJson={"volume":payloadJson["vol"],"roll":payloadJson["rol"],"pitch":payloadJson["pit"],"yaw":payloadJson["yaw"],"temperature":payloadJson["temp"]} #change this
                    query(url=url + idx_reading + "/" + str(dict_id), method="POST", payload=payloadJson)
                except:
                    print("Error posting sensor data for bottle " + str(dict_id))
            else:
                print("bottle " + str(dict_id) + " not registered")
mqttc = connect(mqtt_broker_ip)
mqttc.subscribe(topic=mqtt_sensor_topic, qos=0)
mqttc.subscribe(topic=mqtt_registration, qos=1)
try:
    mqttc.loop_start()
    keepRunning = threading.Event()
    keepRunning.set()
    message_Processor = threading.Thread(target=message_processing)
    actuator_Controller = threading.Thread(target=publish_actuator_commands)
    message_Processor.start()
    actuator_Controller.start()
    while(1):
        pass
except KeyboardInterrupt:
    keepRunning.clear()
    message_Processor.join()
    actuator_Controller.join()
    mqttc.disconnect()

