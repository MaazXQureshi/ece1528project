from mqtt_config import *
#Change the mqtt_broker_ip and ensure MQTT broker is up

def publish_actuator_commands():
    for i in np.flatnonzero(bottle_id): #Iterate over all detected bottles
        try:
            resThresh = query(url=url + idx_threshold + "/" + str(i), method="GET")
            resMode = query(url=url + idx_cleaning + "/" + str(i), method="GET")
            #only publish if there is a change in threshold/mode
            if dic_bottles[i]["threshold"] != resThresh["threshold"] or dic_bottles[i]["cleaning"] != resMode["cleaning"]:
                dic_bottles[i]["threshold"] = resThresh["threshold"]
                dic_bottles[i]["cleaning"] = resMode["cleaning"]
                payload = {"TH":resThresh["threshold"],"CL":resMode["cleaning"]}
                mqttc.publish(dic_topics_act[i], json.dumps(payload),1)
        except:
            print("Error forwarding actuator data to bottle " + str(i))

mqttc = connect(mqtt_broker_ip)
mqttc.subscribe(mqtt_sensor_topic)
mqttc.subscribe(mqtt_registration)
mqttc.loop_start()

while (1):
    if np.any(bottle_id) == True: #At least one bottle is detected
        publish_actuator_commands()
    sleep(10)
