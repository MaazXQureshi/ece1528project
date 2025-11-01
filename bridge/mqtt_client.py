from mqtt_config import *
#Change the mqtt_broker_ip and ensure MQTT broker is up

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.DEBUG,
    )
    #Connect to broker
    mqttc = connect(mqtt_broker_ip)
    #subscribe to sensor topic to receive messages from the sensors connected to ESP
    mqttc.subscribe(mqtt_sensor_topic)
    mqttc.loop_start()
    while (1):
        #Retrieve data from cloud and publish to mqtt broker
        mode_cloud = np.random.randint(0,2)
        threshold_cloud = np.round(np.random.uniform(0,0.3),1)
        if mode_cloud != mode or threshold_cloud != threshold:
            mode = mode_cloud
            threshold = threshold_cloud
            payload = {"id":"ESP1","th":threshold,"mode":mode} #mode can be 0 (normal) or 1 (cleaning mode), threshold [th] is a float value in liter between 0 and 1
            mqttc.publish(mqtt_actuator_topic, json.dumps(payload))
        else:
            logging.debug("No change in mode/threshold, not publishing")
        sleep(5)

