from mqtt_config_tester import *

mqttc_tester1 = connect(mqtt_broker_ip)
mqttc_tester2 = connect(mqtt_broker_ip)
mqttc_tester1.subscribe(mqtt_act_topic + "_1",1)
mqttc_tester2.subscribe(mqtt_act_topic + "_2",1)
mqttc_tester1.loop_start()
mqttc_tester2.loop_start()
mqttc_tester1.publish(mqtt_reg_topic, json.dumps({"id":1}), 1)
mqttc_tester2.publish(mqtt_reg_topic, json.dumps({"id":2}), 1)
counter = 0
spillFlag = False
spillFlag2 = False
while (1):
    
    for i in range(3):
        sensor_data = np.round(np.random.normal(loc=30,scale=5,size=2),2)
        payload={"id":1,"vol":sensor_data[0],"temp":sensor_data[1]}
        mqttc_tester1.publish(mqtt_sensor_topic, json.dumps(payload))
        sleep(2)
        sensor_data = np.round(np.random.normal(loc=30,scale=5,size=2),2)
        payload={"id":2,"vol":sensor_data[0],"temp":sensor_data[1]}
        mqttc_tester2.publish(mqtt_sensor_topic, json.dumps(payload))
        sleep(10)

    spillFlag = not spillFlag
    payload={"id":1,"flag":spillFlag,"seq":counter}
    mqttc_tester1.publish(mqtt_spill_topic, json.dumps(payload))

    spillFlag2 = not spillFlag2
    payload={"id":2,"flag":spillFlag2,"seq":counter}
    mqttc_tester2.publish(mqtt_spill_topic, json.dumps(payload))

    counter += 1