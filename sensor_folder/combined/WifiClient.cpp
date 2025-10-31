#include "WifiClient.h"

WifiClient::WifiClient(char *ssid, char *pass) {
  _ssid = ssid;
  _pass = pass;
}

void WifiClient::connect() {
  WiFiClient wifiClient;
  Serial.println("Connecting to WPA SSID [" + String(_ssid) + "]...");
  WiFi.begin(_ssid, _pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address is: ");
  Serial.println(WiFi.localIP());
}