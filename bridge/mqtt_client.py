from mqtt_config import *
#Change the mqtt_broker_ip and ensure MQTT broker is up

def publish_actuator_commands():
    for i in np.flatnonzero(bottle_id): #Iterate over all detected bottles
        resThresh = query(url=url + idx_th + "/" + str(i), method="GET")
        resMode = query(url=url + idx_cleaning + "/" + str(i), method="GET")
        #only publish if there is a change in threshold/mode
        if resThresh is not None and resMode is not None:
            if dic_bottles[i]["threshold"] != resThresh["threshold"] or dic_bottles[i]["cleaning"] != resMode["cleaning"]:
                dic_bottles[i]["threshold"] = resThresh["threshold"]
                dic_bottles[i]["cleaning"] = resMode["cleaning"]
                payload = {"bottle_id":int(i),"threshold":resThresh["threshold"],"cleaning":resMode["cleaning"]}
                mqttc.publish(mqtt_actuator_topic, json.dumps(payload))

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.INFO,
    )

    mqttc = connect(mqtt_broker_ip)
    mqttc.subscribe(mqtt_sensor_topic)
    mqttc.loop_start()
    while (1):
        if np.sum(bottle_id) > 0: #At least one bottle is detected
            publish_actuator_commands()
        sleep(10)

