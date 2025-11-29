from mqtt_config import *
#Change the mqtt_broker_ip and ensure MQTT broker is up

def publish_actuator_commands():
    while keepRunning.is_set():
        for i in bottle_id: 
            resThresh = query(url=url + idx_threshold + "/" + str(i), method="GET")
            resClean = query(url=url + idx_cleaning + "/" + str(i), method="GET")
            if dic_bottles[i]["th"] != resThresh["th"] or dic_bottles[i]["clean"] != resClean["clean"]:
                dic_bottles[i]["th"] = resThresh["th"]
                dic_bottles[i]["clean"] = resClean["clean"]
                payload = {"th":resThresh["th"],"clean":resClean["clean"]}
                mqttc.publish(topic=dic_topics_act[i], payload=json.dumps(payload), qos=1)
        sleep(interval_Act_Data)

def message_processing():
    while keepRunning.is_set():
        if FIFO.empty() == False:
            msg = FIFO.get()
            payloadJson = json.loads(msg.payload)
            print("Msg process. - " + msg.topic + " - " + str(payloadJson))
            dict_id = int(payloadJson["id"])
            if msg.topic == mqtt_reg_topic:
                if bottle_reg_flag[dict_id] == False:
                    bottle_register(dict_id)
            elif bottle_reg_flag[dict_id] == False:
                print("bottle " + str(dict_id) + " not registered")
            elif msg.topic == mqtt_spill_topic:
                active_flag[dict_id] = True
                if payloadJson["seq"] > spill_seq[dict_id]:
                    if payloadJson["flag"] == True:
                        spill_flag[dict_id] = True
                        print("Spill detected for bottle " + str(dict_id) + "-seq" + str(payloadJson["seq"]))
                    else:
                        spill_flag[dict_id] = False
                        print("Spill cleared for bottle " + str(dict_id) + "-seq" + str(payloadJson["seq"]))
                    del payloadJson["id"]
                    del payloadJson["seq"]
                    query(url=url + idx_spill + "/" + str(dict_id), method="PUT", payload=payloadJson)
                else:
                    print("Out-of-sequence spill message for bottle " + str(dict_id))
            elif msg.topic == mqtt_sensor_topic:
                active_flag[dict_id] = True
                if spill_flag[dict_id] == False and dic_bottles[dict_id]["clean"] == False:
                    del payloadJson["id"]
                    query(url=url + idx_reading + "/" + str(dict_id), method="POST", payload=payloadJson)

            else:
                print("Unknown topic " + msg.topic)


if __name__ == "__main__":
    mqttc = connect(mqtt_broker_ip)
    mqttc.subscribe(topic=mqtt_sensor_topic, qos=0)
    mqttc.subscribe(topic=mqtt_reg_topic, qos=1)
    mqttc.subscribe(topic=mqtt_spill_topic, qos=1)
    try:
        mqttc.loop_start()
        message_Processor = threading.Thread(target=message_processing)
        actuator_Controller = threading.Thread(target=publish_actuator_commands)
        message_Processor.start()
        actuator_Controller.start()
        while 1:
            sleep(60)
            for i in bottle_id:
                if active_flag[i] == False:
                    bottle_deregister(i)
                else:
                    active_flag[i] = False
                    

    except KeyboardInterrupt:
        keepRunning.clear()
        message_Processor.join()
        actuator_Controller.join()
        mqttc.disconnect()

