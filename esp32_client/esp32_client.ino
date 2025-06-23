/*
  AURo - ESP32-CAM Waste Classification Client

  This sketch runs on the ESP32-CAM. It connects to Wi-Fi,
  takes a picture, sends it to the classification server,
  and parses the JSON response.

  Team: AURoTech
  Engineer: Krishiv Gupta (Hardware Integration), Garvit Singhal (Software)
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- IMPORTANT: CONFIGURE YOUR SETTINGS HERE ---
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// The IP address of the computer running the Python API server
const char* SERVER_IP = "YOUR_COMPUTER_IP_ADDRESS"; 
const int SERVER_PORT = 8000;
// --- END OF CONFIGURATION ---

// TODO: Add your camera capture logic here.
// This function should return a pointer to the image buffer (uint8_t*)
// and the size of the buffer (size_t).
// For now, it's just a placeholder.
bool capture_camera_image(uint8_t*& image_buf, size_t& image_size) {
  Serial.println("Capturing image...");
  // In a real implementation, you would use the camera library
  // to get a JPEG image.
  // For example:
  // camera_fb_t * fb = esp_camera_fb_get();
  // if (!fb) {
  //   Serial.println("Camera capture failed");
  //   return false;
  // }
  // image_buf = fb->buf;
  // image_size = fb->len;
  Serial.println("Image captured successfully (placeholder).");
  return true;
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n\nAURo ESP32-CAM Client Initializing...");

  // Connect to Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // TODO: Initialize your camera here
  // For example:
  // camera_init();
}

void loop() {
  Serial.println("\nPress the 'c' key in the Serial Monitor to classify an image.");
  
  if (Serial.available() > 0) {
    char key = Serial.read();
    if (key == 'c') {
      classify_image();
    }
  }
  
  delay(1000);
}

void classify_image() {
  uint8_t* image_buffer = nullptr;
  size_t image_len = 0;

  if (!capture_camera_image(image_buffer, image_len)) {
    Serial.println("Could not get image. Aborting.");
    // In a real implementation, you would release the frame buffer here
    // esp_camera_fb_return(fb);
    return;
  }
  
  HTTPClient http;
  String server_url = "http://" + String(SERVER_IP) + ":" + String(SERVER_PORT) + "/classify/";
  
  Serial.print("Connecting to server: ");
  Serial.println(server_url);

  http.begin(server_url);

  // The content type for a file upload is multipart/form-data
  // We send the image as a file in a POST request.
  // The FastAPI server expects the file to be named "file".
  String boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW";
  String contentType = "multipart/form-data; boundary=" + boundary;
  
  String body_start = "--" + boundary + "\r\n";
  body_start += "Content-Disposition: form-data; name=\"file\"; filename=\"image.jpg\"\r\n";
  body_start += "Content-Type: image/jpeg\r\n\r\n";
  
  String body_end = "\r\n--" + boundary + "--\r\n";
  
  size_t total_len = body_start.length() + image_len + body_end.length();

  http.addHeader("Content-Type", contentType);

  // The HTTPClient library can't stream a request body built from multiple parts easily.
  // We will send the raw request data.
  WiFiClient* client = http.getStreamPtr();
  client->print(body_start);
  // client->write(image_buffer, image_len); // This is where you'd send the real image bytes
  client->print(body_end);
  
  int httpCode = http.POST(""); // Sending an empty string as we manually wrote the body

  if (httpCode > 0) {
    String payload = http.getString();
    Serial.print("HTTP Response code: ");
    Serial.println(httpCode);
    Serial.print("Response payload: ");
    Serial.println(payload);

    // Parse the JSON response
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print("deserializeJson() failed: ");
      Serial.println(error.c_str());
      return;
    }

    const char* classification = doc["classification"];
    Serial.print("Object classified as: ");
    Serial.println(classification);

    // TODO: Send the classification result to the Arduino Mega
    // For example, via Serial:
    // Serial2.println(classification);

  } else {
    Serial.print("Error on HTTP request: ");
    Serial.println(httpCode);
  }

  http.end();
  
  // In a real implementation, you would release the frame buffer here
  // esp_camera_fb_return(fb);
} 