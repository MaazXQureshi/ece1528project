#include "MqttClient.h"
#include <MQTT.h>
#include <ESP8266WiFi.h>

WiFiClient _wifi_client;
int _num_subscribe_topics;

MqttClient::MqttClient(const char* mqtt_broker_ip, const int mqtt_broker_port) {
  _mqtt_client.begin(mqtt_broker_ip, _wifi_client);
}

MqttClient::MqttClient(const char* mqtt_broker_ip, const int mqtt_broker_port, String* subscribe_topics, const int num_subscribe_topics) {
  _mqtt_client.begin(mqtt_broker_ip, _wifi_client);
  _subscribe_topics = subscribe_topics;
  _num_subscribe_topics = num_subscribe_topics;
}

void MqttClient::connect(const char* client_id, void (*callback)(String&, String&)) {
  Serial.print("Connecting to MQTT broker... ");
  while (!_mqtt_client.connect(client_id, "public", "public")) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("done!");
  for (int i = 0; i < _num_subscribe_topics; i++) {
    _mqtt_client.onMessage(callback);
    _mqtt_client.subscribe(_subscribe_topics[i]);
    Serial.println("Subscribed to topic: " + _subscribe_topics[i]);
  }
}

void MqttClient::publish_message(const char* topic, const char* msg, int qos) {
  _mqtt_client.publish(topic, msg, false, qos);
  Serial.println("Message published [ " + String(topic) +" ]: " + String(msg));
}

void MqttClient::check_connection(const char* client_id, void (*callback)(String&, String&)) {
  _mqtt_client.loop();
  delay(10);
  if (!_mqtt_client.connected()) {
    connect(client_id, callback);
  }
}
