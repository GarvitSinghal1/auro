/*
  AURo - ESP32-CAM Waste Classification Client (v2.0)

  This sketch runs on the ESP32-CAM. It connects to Wi-Fi,
  waits for a command from the main Arduino controller, takes a picture, 
  sends it to the public classification server, and parses the response.

  Team: AURoTech
  Engineer: Krishiv Gupta (Hardware Integration), Garvit Singhal (Software)
*/

#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

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

void camera_init();

void setup() {
  Serial.begin(115200); // For debugging on the computer
  // MEGA_SERIAL.begin(9600, SERIAL_8N1, 16, 17); // For communication with Mega
  
  Serial.println("\n\nAURo ESP32-CAM Client Initializing...");

  // --- Initialize Camera ---
  camera_init();
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

  // --- Camera Capture Logic ---
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    // MEGA_SERIAL.println("Error: Capture failed");
    return;
  }
  // ---

  // For now, we'll use placeholder data.
  uint8_t* image_buffer = fb->buf;
  size_t image_len = fb->len;
  
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
      // Updated parsing for the new v1.7.3 API response structure
      if (doc["detections"].size() > 0) {
        // Get the first detected object
        JsonObject detection = doc["detections"][0];
        
        const char* category = detection["category"];
        
        JsonObject bbox = detection["bounding_box"];
        float y_min = bbox["y_min"];
        float x_min = bbox["x_min"];
        float y_max = bbox["y_max"];
        float x_max = bbox["x_max"];

        Serial.println("--- Classification Result ---");
        Serial.print("Category: ");
        Serial.println(category);
        Serial.println("Bounding Box:");
        Serial.print("  y_min: "); Serial.println(y_min);
        Serial.print("  x_min: "); Serial.println(x_min);
        Serial.print("  y_max: "); Serial.println(y_max);
        Serial.print("  x_max: "); Serial.println(x_max);
        Serial.println("---------------------------");

        // Example of sending data to Mega (adapt as needed)
        // String mega_message = String(category) + "," + String(x_min) + "," + String(y_max);
        // MEGA_SERIAL.println(mega_message);

      } else {
        Serial.println("No objects detected in the image.");
        // MEGA_SERIAL.println("Result: No objects detected");
      }
    }
  } else {
    Serial.print("Error on HTTP request: ");
    Serial.println(httpCode);
    // MEGA_SERIAL.println("Error: HTTP request failed");
  }

  http.end();
  
  // --- Release Frame Buffer ---
  esp_camera_fb_return(fb);
  // ---
}

void camera_init(){
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Frame size
  //FRAMESIZE_VGA (640x480) is a good balance.
  //For higher detail: FRAMESIZE_SVGA (800x600), FRAMESIZE_XGA (1024x768)
  //For faster speed: FRAMESIZE_QVGA (320x240)
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12; //0-63 lower number means higher quality
  config.fb_count = 1;

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  Serial.println("Camera initialized successfully.");
} 