from mqtt_config_tester import *

mqttc_tester1 = connect(mqtt_broker_ip)
mqttc_tester2 = connect(mqtt_broker_ip)
mqttc_tester1.subscribe(mqtt_actuator_topic + "_1")
mqttc_tester2.subscribe(mqtt_actuator_topic + "_2")
mqttc_tester1.loop_start()
mqttc_tester2.loop_start()
mqttc_tester1.publish(mqtt_registration, json.dumps({"id":1}), 1)
mqttc_tester2.publish(mqtt_registration, json.dumps({"id":2}), 1)
sensor_data_array = np.zeros(5, dtype=float)
while (1):
    if initialized[1] == True:
        sensor_data_array[:] = np.round(np.random.normal(loc=30,scale=5,size=5),2)
        payload={"id":1,"vol":sensor_data_array[0],"rol":sensor_data_array[1],"pit":sensor_data_array[2],"yaw":sensor_data_array[3],"temp":sensor_data_array[4]}
        mqttc_tester1.publish(mqtt_sensor_topic, json.dumps(payload))
        sleep(5)
    if initialized[2] == True:
        sensor_data_array[:] = np.round(np.random.normal(loc=30,scale=5,size=5),2)
        payload={"id":2,"vol":sensor_data_array[0],"rol":sensor_data_array[1],"pit":sensor_data_array[2],"yaw":sensor_data_array[3],"temp":sensor_data_array[4]}
        mqttc_tester2.publish(mqtt_sensor_topic, json.dumps(payload))
        sleep(10)