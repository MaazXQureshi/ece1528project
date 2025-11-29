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

// The interval to collect sensor data and send it to Raspberry Pi.
#define SEND_INTERVAL 500
#define BOTTLE_ID 1
#define DENSITY_OF_LIQUID_IN_GRAMS_PER_ML 1.0

// Timer to detect when to collect sensor data.
unsigned long timer = 0;

// Actuation command parameters.
#define ACTUATION_TIMEOUT_PERIOD 60000 // 1 minute.
bool is_bottle_registered = false;
unsigned long actuation_timer = 0;
std::optional<double> threshold = std::nullopt;
std::optional<bool> cleaning_mode = std::nullopt;

// Initialize the MPU6050 light library.
MPU6050 mpu(Wire);
unsigned long seq_counter_for_spilling = 0;

// Initialize the load cell and HX711.
const int LOADCELL_DOUT_PIN = 12;
const int LOADCELL_SCK_PIN = 13;
#define CALIBRATION_FACTOR -424.7893333
HX711 scale;

// GPIO where the DS18B20 is connected to
// Setup a oneWire instance to communicate with any OneWire devices
// Pass our oneWire reference to Dallas Temperature sensor
const int oneWireBus = D2;
OneWire oneWire(oneWireBus); 
DallasTemperature sensors(&oneWire);

// Initialize the LCD.
#define LCD_WIDTH 16
LiquidCrystal_I2C lcd(0x27, LCD_WIDTH, 2);

// External LED is connected to board's digital pin D13.
#define LED D13

// Wi-Fi login credientials (should modify according to the your Wi-Fi).
char ssid_wifi[] = "BELL318";
char pass_wifi[] = "A2761E9A66C7";
WifiClient wifi_client(ssid_wifi, pass_wifi);

// MQTT publisher settings. Be sure to change the IP address!
const char* mqtt_broker_ip = "192.168.2.43";
const int mqtt_broker_port = 1883;
const char* client_id = "publisher_sensors";
const int num_subscribe_topics = 1;
String subscribe_topics[num_subscribe_topics] = {"Act_Data_" + String(BOTTLE_ID)};
MqttClient mqtt_client(mqtt_broker_ip, mqtt_broker_port, subscribe_topics, num_subscribe_topics);

// Helper function to send JSON data to MQTT.
void sendJSONMessageToMQTT(const DynamicJsonDocument& doc, const char* publish_topic, const int& qos) {
  String json_doc;
  serializeJson(doc, json_doc);
  char buf[500];
  json_doc.toCharArray(buf, 500);
  mqtt_client.publish_message(publish_topic, buf, qos);
}

// Helper function to print message on LCD.
void printMessageOnLCD(LiquidCrystal_I2C& lcd, const String& str) {
  if (str.length() < LCD_WIDTH) {
    uint8_t numberOfSpaces = LCD_WIDTH - str.length();
    lcd.print(str + std::string(numberOfSpaces, ' ').c_str());
  }
  else {
    lcd.print(str);
  }
}

// Callback function for the MQTT. Triggered whenever it receives an actuation 
// command.
void callback(String& topic, String& payload) {
  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, payload);

  if (err) {
    while(1) {Serial.println("Having trouble extracting actuation command!!! Help!!!");}
  }
  else {
    threshold = doc["th"];
    cleaning_mode = doc["clean"];
    Serial.println("Updated threshold to " + String(*threshold) + " and cleaning mode to " + String(*cleaning_mode));

    // Since we have received actuation command, this bottle is registered.
    is_bottle_registered = true;
    
    // Update the actuation timer since we have received a message from the 
    // Raspberry Pi.
    actuation_timer = millis();
  }
}

// Helper function to send the initial registration message.
void sendRegistrationMessage() {
  // Initial registration message to let the initial MQTT bridge know that
  // this bottle is ready to go.
  DynamicJsonDocument doc(1024);
  doc["id"] = BOTTLE_ID;

  // Sending the JSON to MQTT.
  sendJSONMessageToMQTT(doc, "Reg_Msg", 1);

  lcd.setCursor(0, 0);
  printMessageOnLCD(lcd, "Waiting for");
  lcd.setCursor(0, 1);
  printMessageOnLCD(lcd, "ActuationCommand");
}

// Helper function to detect if there is spilling and send a message to the 
// Raspberry pi accordingly.
void detectSpillingAndSendData() {
  // MPU6050 sensor.
  float roll = mpu.getAngleX();
  float pitch = mpu.getAngleY();
  float yaw = mpu.getAngleZ();
  Serial.println("Degrees: Roll : " + String(roll) + ", Pitch: " + String(pitch) + ", Yaw: " + String(yaw));

  // To-do: logic for detecting spilling.
  bool is_spilling = (std::abs(roll) > 50);

  // First, we need to convert the readings to JSON that matches the API of the
  // Raspberry Pi.
  DynamicJsonDocument doc(1024);
  doc["id"] = BOTTLE_ID;
  doc["flag"] = is_spilling;
  doc["seq"] = seq_counter_for_spilling;

  // Sending the JSON to MQTT.
  sendJSONMessageToMQTT(doc, "Spill_Flag", 1);

  // Increment the spilling counter.
  seq_counter_for_spilling += 1;
}

// Helper function to retrieve sensor data and send it to the Raspberry Pi.
void gatherAndSendSensorData() {
  // Load cell and HX711 sensor.
  scale.power_up();
  float weight_in_grams = scale.get_units();
  float volume_in_milligrams = weight_in_grams / DENSITY_OF_LIQUID_IN_GRAMS_PER_ML;
  
  // DS18B20 sensor.
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);

  // Print the temperature to the LCD on the second row, first column.
  lcd.setCursor(0, 0);
  printMessageOnLCD(lcd, "Vol:" + String(volume_in_milligrams) + " mL");
  lcd.setCursor(0, 1);
  printMessageOnLCD(lcd, "Temp: " + String(temperatureC) + " degC");

  // Light up the volume is below threshold.
  if (volume_in_milligrams < *threshold) {
    digitalWrite(LED, HIGH);
  }
  else {
    digitalWrite(LED, LOW);
  }

  // Get the unique bottle ID to distinguish between different bottles.
  Serial.println("Bottle ID: " + String(BOTTLE_ID));

  // First, we need to convert the readings to JSON that matches the API of the
  // Raspberry Pi.
  DynamicJsonDocument doc(1024);
  doc["id"] = BOTTLE_ID;
  doc["vol"] = volume_in_milligrams;
  doc["temp"] = temperatureC;

  // Sending the JSON to MQTT.
  sendJSONMessageToMQTT(doc, "Sen_Data", 0);

  // Power down scale to save energy.
  scale.power_down(); 
}

void setup(void) {
  Serial.begin(115200);

  // Error-checking to get the serial monitor up and running.
  while (!Serial) {}

  // Attempt to connect to the Wi-Fi and MQTT.
  wifi_client.connect();
  mqtt_client.connect(client_id, callback);

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

  // Connect to the MQTT to send data.
  mqtt_client.check_connection(client_id, callback);

  if ((millis() - timer) > SEND_INTERVAL) {
    // Check if we have received actuation command from the Raspberry Pi in the
    // past minute. If not, the connection may have been lost.
    if ((millis() - actuation_timer) > ACTUATION_TIMEOUT_PERIOD) {
      is_bottle_registered = false;
    }

    if (is_bottle_registered == true) {
      // In cleaning mode, pause all the sensors and message publishing.
      if (*cleaning_mode == true) {
        lcd.setCursor(0, 0);
        printMessageOnLCD(lcd, "Cleaning Mode");
        lcd.setCursor(0, 1);
        printMessageOnLCD(lcd, "Readings paused");
      }
      else {
        gatherAndSendSensorData();
        detectSpillingAndSendData();
      }
    }
    else {
      sendRegistrationMessage();
    }

    // Update timer to accurately determine when to take the data sample again.
    timer = millis(); 
  }
}
