#include <Arduino.h>
#include <MQTT.h>

class MqttClient {
  public:
    MqttClient(const char* mqtt_broker_ip, const int mqtt_broker_port);
    MqttClient(const char* mqtt_broker_ip, const int mqtt_broker_port, String* subscribe_topics, const int num_subscribe_topics);
    void connect(const char* client_id, void (*callback)(String&, String&));
    void publish_message(const char* topic, const char* msg, int qos);
    void check_connection(const char* client_id, void (*callback)(String&, String&));
  
  private:
    MQTTClient _mqtt_client;
    String* _subscribe_topics;
    int _num_subscribe_topics;
};