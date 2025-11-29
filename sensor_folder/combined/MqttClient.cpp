#include "MqttClient.h"
#include <MQTT.h>
#include <ESP8266WiFi.h>

WiFiClient _wifi_client;

MqttClient::MqttClient(const char* mqtt_broker_ip, const int mqtt_broker_port) {
  _mqtt_client.begin(mqtt_broker_ip, _wifi_client);
}

MqttClient::MqttClient(const char* mqtt_broker_ip, const int mqtt_broker_port, const std::vector<std::pair<String, int>>& subscribe_topics) {
  _mqtt_client.begin(mqtt_broker_ip, _wifi_client);
  _subscribe_topics = subscribe_topics;
}

void MqttClient::connect(const char* client_id, void (*callback)(String&, String&)) {
  Serial.print("Connecting to MQTT broker... ");
  while (!_mqtt_client.connect(client_id, "public", "public")) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("done!");
  // Specifies the topic name as well as QoS.
  for (const std::pair<String, int> entry: _subscribe_topics) {
    _mqtt_client.onMessage(callback);
    _mqtt_client.subscribe(entry.first, entry.second);
    Serial.println("Subscribed to topic: " + entry.first);
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
