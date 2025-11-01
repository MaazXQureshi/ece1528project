from mqtt_config import *


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.DEBUG,
    )
    mqttc_tester = connect(mqtt_broker_ip)
    mqttc_tester.subscribe(mqtt_actuator_topic)
    mqttc_tester.loop_start()
    sensor_data_array = np.zeros(5, dtype=float)
    while (1):
        sensor_data_array[:] = np.round(np.random.normal(loc=30,scale=5,size=5),2)
        payload={"id":"ESP1","temperature":sensor_data_array[0],"roll":sensor_data_array[1],"pitch":sensor_data_array[2],"yaw":sensor_data_array[3],"volume":sensor_data_array[4]}
        mqttc_tester.publish(mqtt_sensor_topic, json.dumps(payload))
        sleep(3)