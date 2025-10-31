#include <MPU6050_light.h>
#include "Wire.h"
#include "MqttClient.h"
#include "WifiClient.h"
#include <ArduinoJson.h>

// Initialize the MPU6050 light library.
MPU6050 mpu(Wire);
unsigned long timer = 0;

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

  // Attempt to connect to the Wi-Fi and MQTT.
  wifi_client.connect();
  mqtt_client.connect(client_id);

  // Setup for MPU6050 for the light library.
  Wire.begin();
  
  byte status = mpu.begin();
  Serial.print(F("MPU6050 status: "));
  Serial.println(status);
  while(status!=0){ } // stop everything if could not connect to MPU6050
  
  Serial.println(F("Calculating offsets, do not move MPU6050"));
  delay(1000);
  // mpu.upsideDownMounting = true; // uncomment this line if the MPU6050 is mounted upside-down
  mpu.calcOffsets(); // gyro and accelero
  Serial.println("Done!\n");

  delay(100);
}

void loop() {
  mpu.update();
  
  // Print data every 500 ms
  if((millis() - timer) > 500){
    float angle_x = mpu.getAngleX();
    float angle_y = mpu.getAngleY();
    float angle_z = mpu.getAngleZ();
    float temp = mpu.getTemp();
    Serial.println("Degrees: X : " + String(angle_x) + ", Y: " + String(angle_y) + ", Z: " + String(angle_z));
    Serial.println("Temp: " + String(temp));

    timer = millis(); 

    // Connect to the MQTT to send data.
    mqtt_client.check_connection(client_id);

    // First, we need to convert the readings to JSON that matches the API of the
    // backend.
    DynamicJsonDocument doc(1024);
    doc["temperature"] = temp;
    doc["roll"] = angle_x;
    doc["pitch"] = angle_y;
    doc["yaw"] = angle_z;

    // Sending the JSON to MQTT.
    String json_doc;
    serializeJson(doc, json_doc);
    char buf[500];
    json_doc.toCharArray(buf, 500);
    mqtt_client.publish_message(publish_topic, buf); 
  }
}
