#include <MPU6050_light.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <LiquidCrystal_I2C.h>
#include "HX711.h"
#include "Wire.h"
#include "MqttClient.h"
#include "WifiClient.h"
#include <ArduinoJson.h>
#include <Arduino.h>

#define SEND_INTERVAL 500
#define DENSITY_OF_LIQUID_IN_GRAMS_PER_ML 1.0

// Interval used to send data to MQTT.
unsigned long timer = 0;

// Initialize the MPU6050 light library.
MPU6050 mpu(Wire);

// Initialize the load cell and HX711.
const int LOADCELL_DOUT_PIN = 12;
const int LOADCELL_SCK_PIN = 13;
#define CALIBRATION_FACTOR -416.4601307
HX711 scale;

// GPIO where the DS18B20 is connected to
// Setup a oneWire instance to communicate with any OneWire devices
// Pass our oneWire reference to Dallas Temperature sensor
const int oneWireBus = D2;
OneWire oneWire(oneWireBus); 
DallasTemperature sensors(&oneWire);

// Initialize the LCD.
LiquidCrystal_I2C lcd(0x27, 16, 2);

// External LED is connected to board's digital pin D13.
#define LED D13
#define SPILLING_DEGREE 20

// Wi-Fi login credientials (should modify according to the your Wi-Fi).
char ssid_wifi[] = "BELL318";
char pass_wifi[] = "A2761E9A66C7";
WifiClient wifi_client(ssid_wifi, pass_wifi);

// MQTT publisher settings. Be sure to change the IP address!
const char* mqtt_broker_ip = "192.168.2.43";
const int mqtt_broker_port = 1883;
const char* client_id = "publisher_sensors";
const char* publish_topic = "MQTT_Sensor_Data";
MqttClient mqtt_client(mqtt_broker_ip, mqtt_broker_port);

// Helper function to convert 64-bit ID address into a string.
String idToString(const DeviceAddress& deviceID) {
  String final_result = "";

  for (int i = 0; i < 8; ++i) {
    final_result += String(deviceID[i], HEX);
  }

  return final_result;
}

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

  // Intialize the load cell and HX711 sensor.
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(CALIBRATION_FACTOR); // Important: this value is obtained by calibrating the scale with known weights.
  scale.tare(); // Reset the scale to 0.

  // Start the DS18B20 sensor.
  sensors.begin();

  // Start the LCD.
  lcd.init();
  lcd.backlight();

  // Initialize the external LED.
  pinMode(LED, OUTPUT);

  delay(100);
}

void loop() {
  mpu.update();
  
  if ((millis() - timer) > SEND_INTERVAL) {
    // Load cell and HX711 sensor.
    scale.power_up();
    float weight_in_grams = scale.get_units();
    float volume_in_milligrams = weight_in_grams / DENSITY_OF_LIQUID_IN_GRAMS_PER_ML;

    // MPU6050 sensor.
    float roll = mpu.getAngleX();
    float pitch = mpu.getAngleY();
    float yaw = mpu.getAngleZ();
    Serial.println("Degrees: Roll : " + String(roll) + ", Pitch: " + String(pitch) + ", Yaw: " + String(yaw));
    
    // DS18B20 sensor.
    sensors.requestTemperatures();
    float temperatureC = sensors.getTempCByIndex(0);

    // Print the temperature to the LCD on the second row, first column.
    lcd.setCursor(0, 0);
    lcd.print(String(volume_in_milligrams) + " mL             ");
    lcd.setCursor(0, 1);
    lcd.print("Temp: " + String(temperatureC) + " degC     ");

    // Light up the LED if the pitch is above a certain degree.
    if (abs(roll) > SPILLING_DEGREE) {
      digitalWrite(LED, HIGH);
    }
    else {
      digitalWrite(LED, LOW);
    }

    // Connect to the MQTT to send data.
    mqtt_client.check_connection(client_id);

    // Get the unique bottle ID to distinguish between different bottles.
    // ID is obtained from DS18B20 which has a unique address per sensor.
    DeviceAddress bottle_id;
    sensors.getAddress(bottle_id, 0);
    String bottle_id_string = idToString(bottle_id);
    Serial.print("Bottle ID: " + bottle_id_string);

    // First, we need to convert the readings to JSON that matches the API of the
    // backend.
    DynamicJsonDocument doc(1024);
    doc["bottle_id"] = bottle_id_string;
    doc["volume"] = volume_in_milligrams;
    doc["temperature"] = temperatureC;
    doc["roll"] = roll;
    doc["pitch"] = pitch;
    doc["yaw"] = yaw;

    // Sending the JSON to MQTT.
    String json_doc;
    serializeJson(doc, json_doc);
    char buf[500];
    json_doc.toCharArray(buf, 500);
    mqtt_client.publish_message(publish_topic, buf);

    // Update timer to accurately determine when to take the data sample again.
    timer = millis(); 

    // Power down scale to save energy.
    scale.power_down();
  }
}
