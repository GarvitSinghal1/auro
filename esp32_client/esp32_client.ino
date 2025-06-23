/*
  AURo - ESP32-CAM Waste Classification Client (v2.0)

  This sketch runs on the ESP32-CAM. It connects to Wi-Fi,
  waits for a command from the main Arduino controller, takes a picture, 
  sends it to the public classification server, and parses the response.

  Team: AURoTech
  Engineer: Krishiv Gupta (Hardware Integration), Garvit Singhal (Software)
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- Configuration ---
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// The permanent, public URL of our deployed classification API
const char* API_URL = "https://auro-l4mh.onrender.com/classify/";

// Communication with the main Arduino Mega controller
// The Mega will send a 'c' character over Serial to trigger classification.
#define TRIGGER_CHAR 'c'

// Pins for Serial communication with Arduino Mega (Example: using Serial2)
// Connect ESP32's TX2 to Mega's RX1
// Connect ESP32's RX2 to Mega's TX1
// Make sure to have a common GND connection.
// #define MEGA_SERIAL Serial2 

// --- End of Configuration ---

void setup() {
  Serial.begin(115200); // For debugging on the computer
  // MEGA_SERIAL.begin(9600, SERIAL_8N1, 16, 17); // For communication with Mega
  
  Serial.println("\n\nAURo ESP32-CAM Client Initializing...");

  // --- KRISHIV: Camera Initialization ---
  // The code to initialize your specific camera model goes here.
  // For example: camera_init();
  // ---

  connect_to_wifi();
}

void loop() {
  // The ESP32 waits for a command from the main controller.
  // if (MEGA_SERIAL.available() > 0) {
  //   char command = MEGA_SERIAL.read();
  //   if (command == TRIGGER_CHAR) {
  //     classify_image();
  //   }
  // }

  // For testing without the Mega, you can trigger with the debug serial monitor.
  if (Serial.available() > 0) {
    char command = Serial.read();
    if (command == TRIGGER_CHAR) {
      classify_image();
    }
  }
}

void connect_to_wifi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void classify_image() {
  Serial.println("Classification triggered!");

  // --- KRISHIV: Camera Capture Logic ---
  // This is where the code to capture a single frame from the camera goes.
  // It should return a pointer to the image buffer and the length of the buffer.
  // For example:
  // camera_fb_t * fb = esp_camera_fb_get();
  // if (!fb) {
  //   Serial.println("Camera capture failed");
  //   MEGA_SERIAL.println("Error: Capture failed");
  //   return;
  // }
  // uint8_t* image_buffer = fb->buf;
  // size_t image_len = fb->len;
  // ---

  // For now, we'll use placeholder data.
  uint8_t* image_buffer = nullptr;
  size_t image_len = 0;
  
  HTTPClient http;
  http.begin(API_URL);

  int httpCode = http.POST(image_buffer, image_len);

  if (httpCode > 0) {
    String payload = http.getString();
    Serial.print("HTTP Response code: ");
    Serial.println(httpCode);
    Serial.print("Response payload: ");
    Serial.println(payload);

    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print("JSON parsing failed: ");
      Serial.println(error.c_str());
      // MEGA_SERIAL.println("Error: JSON parsing failed");
    } else {
      const char* classification = doc["classification"];
      Serial.print("Object classified as: ");
      Serial.println(classification);
      // MEGA_SERIAL.println(classification); // Send the result to the Mega
    }
  } else {
    Serial.print("Error on HTTP request: ");
    Serial.println(httpCode);
    // MEGA_SERIAL.println("Error: HTTP request failed");
  }

  http.end();
  
  // --- KRISHIV: Release Frame Buffer ---
  // Remember to release the frame buffer after you're done.
  // esp_camera_fb_return(fb);
  // ---
} 