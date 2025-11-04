from mqtt_config import *



mqttc_tester1 = connect_test(mqtt_broker_ip)
mqttc_tester2 = connect_test(mqtt_broker_ip)
mqttc_tester1.subscribe(mqtt_actuator_topic + "_1")
mqttc_tester2.subscribe(mqtt_actuator_topic + "_2")
mqttc_tester1.loop_start()
mqttc_tester2.loop_start()
sensor_data_array = np.zeros(5, dtype=float)
while (1):
    sensor_data_array[:] = np.round(np.random.normal(loc=30,scale=5,size=5),2)
    payload={"bottle_id":1,"volume":sensor_data_array[0],"roll":sensor_data_array[1],"pitch":sensor_data_array[2],"yaw":sensor_data_array[3],"temperature":sensor_data_array[4]}
    mqttc_tester1.publish(mqtt_sensor_topic, json.dumps(payload))
    sleep(10)
    sensor_data_array[:] = np.round(np.random.normal(loc=30,scale=5,size=5),2)
    payload={"bottle_id":2,"volume":sensor_data_array[0],"roll":sensor_data_array[1],"pitch":sensor_data_array[2],"yaw":sensor_data_array[3],"temperature":sensor_data_array[4]}
    mqttc_tester2.publish(mqtt_sensor_topic, json.dumps(payload))
    sleep(10)