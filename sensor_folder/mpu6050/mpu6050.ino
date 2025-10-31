#include "MPU6050.h"
#include "MqttClient.h"
#include "WifiClient.h"
#include <ArduinoJson.h>

// Initialize the MPU6050.
MPU6050 mpu6050(MPU6050_RANGE_8_G, MPU6050_RANGE_500_DEG, MPU6050_BAND_5_HZ);

// Wi-Fi login credientials (should modify according to the your Wi-Fi).
char ssid_wifi[] = "BELL318";
char pass_wifi[] = "A2761E9A66C7";
WifiClient wifi_client(ssid_wifi, pass_wifi);

// MQTT publisher settings. Be sure to change the IP address!
const char* mqtt_broker_ip = "192.168.2.35";
const int mqtt_broker_port = 1883;
const char* client_id = "publisher_MPU6050";
const char* publish_topic = "MPU6050";
MqttClient mqtt_client(mqtt_broker_ip, mqtt_broker_port);

void setup(void) {
  Serial.begin(115200);

  // Error-checking to get the serial monitor up and running.
  while (!Serial) {
    delay(10);
  }

  // Print out the setup values of MPU6050.
  mpu6050.printSetup();

  // Attempt to connect to the Wi-Fi and MQTT.
  wifi_client.connect();
  mqtt_client.connect(client_id);

  delay(100);
}

void loop() {
  std::optional<sensors_event_t> a, g, temp;
  std::tie(a, g, temp) = mpu6050.getSensorData();

  if (a.has_value()) {
    Serial.println("Acceleration X: " + String(a->acceleration.x) + ", Y: " + String(a->acceleration.y) + ", Z: " + String(a->acceleration.z) + " m/s^2");
  }

  if (g.has_value()) {
    Serial.println("Rotation X: " + String(g->gyro.x) + ", Y: " + String(g->gyro.y) + ", Z: " + String(g->gyro.z) + " rad/s");
  }

  if (temp.has_value()) {
    Serial.println("Temperature: " + String(temp->temperature) + " degC");
  }

  if (a.has_value() && g.has_value() && temp.has_value()) {
    // Connect to the MQTT to send data.
    mqtt_client.check_connection(client_id);

    // First, we need to convert the readings to JSON that matches the API of the
    // backend.
    DynamicJsonDocument doc(1024);
    doc["temperature"] = temp->temperature;

    // Create an array to store the rotation of x-, y-, and z-axis.
    JsonArray angleValues = doc.createNestedArray("angle");
    angleValues.add(g->gyro.x);
    angleValues.add(g->gyro.y);
    angleValues.add(g->gyro.z);

    // Sending the JSON to MQTT.
    String json_doc;
    serializeJson(doc, json_doc);
    char buf[500];
    json_doc.toCharArray(buf, 500);
    mqtt_client.publish_message(publish_topic, buf);
  }

  delay(500);
}
