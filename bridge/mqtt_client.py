from mqtt_config import *
#Change the mqtt_broker_ip and ensure MQTT broker is up

def publish_actuator_commands():
    for i in np.flatnonzero(bottle_id): #Iterate over all detected bottles
        resThresh = query(url=url + idx_threshold + "/" + str(i), method="GET")
        resMode = query(url=url + idx_cleaning + "/" + str(i), method="GET")
        #only publish if there is a change in threshold/mode
        if resThresh is not None and resMode is not None:
            if dic_bottles[i]["threshold"] != resThresh["threshold"] or dic_bottles[i]["cleaning"] != resMode["cleaning"]:
                dic_bottles[i]["threshold"] = resThresh["threshold"]
                dic_bottles[i]["cleaning"] = resMode["cleaning"]
                payload = {"threshold":resThresh["threshold"],"cleaning":resMode["cleaning"]}
                mqttc.publish(dic_topics_act[i], json.dumps(payload))

if __name__ == "__main__":
    mqttc = connect(mqtt_broker_ip)
    mqttc.subscribe(mqtt_sensor_topic)
    mqttc.loop_start()
    while (1):
        if np.sum(bottle_id) > 0: #At least one bottle is detected
            publish_actuator_commands()
        sleep(15)




"""
Actuators Data:
For each bottle, the data is sent when there is a change in the data on the cloud on the 
topic MQTT_Actuator_Data_"bottle_id" where bottle_id is 1 or 2.
The data is in JSON format:
{
    "threshold": float,
    "cleaning": int (0 or 1)
} There is no need for identifier here since the topic identifies the bottle.

Sensors Data:
For each bottle, the data is sent on the topic MQTT_Sensor_Data.
The data is in JSON format:
{
    "bottle_id": int (1 or 2),
    "volume": float,
    "roll": float,
    "pitch": float,
    "yaw": float,
    "temperature": float
}
If the bottle is in cleaning mode, no sensor data should be sent.
The bottle is registered in the MQTT client once it has sent its first sensor data successfully.

"""