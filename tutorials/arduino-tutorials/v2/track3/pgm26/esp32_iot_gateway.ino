/*
 * ESP32 IoT Gateway and ML Inference for 3D Printing Process Monitor
 * 
 * This code runs on ESP32 to handle IoT connectivity, machine learning inference,
 * and advanced data processing for the 3D printing monitoring system.
 * 
 * Features:
 * - WiFi connectivity and web server
 * - MQTT communication
 * - TensorFlow Lite inference for quality prediction
 * - Image processing for thermal data
 * - Real-time dashboard
 * - OTA updates
 * 
 * Author: Arduino Zero to Hero v2.0
 * Version: 1.0
 * Date: 2024
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <SPIFFS.h>
#include <Update.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include <TensorFlowLite_ESP32.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <tensorflow/lite/version.h>

// Pin Definitions
#define UART_RX_PIN 16
#define UART_TX_PIN 17
#define STATUS_LED_PIN 2
#define BUZZER_PIN 4
#define USER_BUTTON_PIN 0

// Network Configuration
const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "your-mqtt-broker.com";
const int mqtt_port = 1883;

// Web Server
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// MQTT Client
WiFiClient espClient;
PubSubClient mqtt(espClient);

// TensorFlow Lite Variables
constexpr int kTensorArenaSize = 60 * 1024;
uint8_t tensor_arena[kTensorArenaSize];
tflite::MicroErrorReporter micro_error_reporter;
tflite::AllOpsResolver resolver;
const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;

// Data Structures
struct SensorData {
  float hotend_temp;
  float bed_temp;
  float ambient_temp;
  float flow_rate;
  float thermal_array[768]; // 32x24 thermal image
  uint16_t current_layer;
  float completion_percentage;
  uint32_t timestamp;
};

struct MLPrediction {
  float success_probability;
  float failure_risk;
  String failure_type;
  float confidence;
  uint32_t prediction_time;
};

struct SystemMetrics {
  float cpu_usage;
  float memory_usage;
  float wifi_signal_strength;
  uint32_t uptime;
  uint32_t total_predictions;
  uint32_t successful_predictions;
};

// Global Variables
SensorData latest_sensor_data;
MLPrediction latest_prediction;
SystemMetrics system_metrics;
bool ml_model_loaded = false;
unsigned long last_prediction_time = 0;
unsigned long last_data_transmission = 0;
unsigned long last_metrics_update = 0;

// Buffers for data processing
const int THERMAL_BUFFER_SIZE = 100;
float thermal_history[THERMAL_BUFFER_SIZE][768];
int thermal_history_index = 0;

const int PREDICTION_BUFFER_SIZE = 50;
MLPrediction prediction_history[PREDICTION_BUFFER_SIZE];
int prediction_history_index = 0;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(USER_BUTTON_PIN, INPUT_PULLUP);
  
  Serial.println("ESP32 IoT Gateway for 3D Print Monitor");
  Serial.println("Initializing...");
  
  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS initialization failed");
    return;
  }
  
  // Initialize WiFi
  initializeWiFi();
  
  // Initialize MQTT
  initializeMQTT();
  
  // Initialize web server
  initializeWebServer();
  
  // Load ML model
  loadMLModel();
  
  // Initialize system metrics
  initializeMetrics();
  
  Serial.println("ESP32 initialization complete!");
  digitalWrite(STATUS_LED_PIN, HIGH);
}

void loop() {
  unsigned long current_time = millis();
  
  // Handle WiFi reconnection
  if (WiFi.status() != WL_CONNECTED) {
    reconnectWiFi();
  }
  
  // Handle MQTT
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();
  
  // Process incoming data from Arduino Mega
  processArduinoData();
  
  // Perform ML prediction
  if (current_time - last_prediction_time >= 5000 && ml_model_loaded) {
    performMLPrediction();
    last_prediction_time = current_time;
  }
  
  // Update system metrics
  if (current_time - last_metrics_update >= 10000) {
    updateSystemMetrics();
    last_metrics_update = current_time;
  }
  
  // Transmit data to cloud
  if (current_time - last_data_transmission >= 1000) {
    transmitDataToCloud();
    last_data_transmission = current_time;
  }
  
  // Handle user button
  handleUserButton();
  
  // Cleanup WebSocket connections
  ws.cleanupClients();
  
  delay(10);
}

void initializeWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 50) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("WiFi connected! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("WiFi connection failed!");
  }
}

void initializeMQTT() {
  mqtt.setServer(mqtt_server, mqtt_port);
  mqtt.setCallback(mqttCallback);
  
  if (mqtt.connect("ESP32_PrintMonitor")) {
    Serial.println("MQTT connected");
    mqtt.subscribe("printer/commands");
    mqtt.subscribe("printer/config");
  } else {
    Serial.println("MQTT connection failed");
  }
}

void initializeWebServer() {
  // Serve static files
  server.serveStatic("/", SPIFFS, "/").setDefaultFile("index.html");
  
  // WebSocket handler
  ws.onEvent(onWebSocketEvent);
  server.addHandler(&ws);
  
  // REST API endpoints
  server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request) {
    DynamicJsonDocument doc(2048);
    
    doc["sensor_data"]["hotend_temp"] = latest_sensor_data.hotend_temp;
    doc["sensor_data"]["bed_temp"] = latest_sensor_data.bed_temp;
    doc["sensor_data"]["flow_rate"] = latest_sensor_data.flow_rate;
    doc["sensor_data"]["current_layer"] = latest_sensor_data.current_layer;
    doc["sensor_data"]["completion"] = latest_sensor_data.completion_percentage;
    
    doc["prediction"]["success_probability"] = latest_prediction.success_probability;
    doc["prediction"]["failure_risk"] = latest_prediction.failure_risk;
    doc["prediction"]["failure_type"] = latest_prediction.failure_type;
    doc["prediction"]["confidence"] = latest_prediction.confidence;
    
    doc["system"]["cpu_usage"] = system_metrics.cpu_usage;
    doc["system"]["memory_usage"] = system_metrics.memory_usage;
    doc["system"]["wifi_signal"] = system_metrics.wifi_signal_strength;
    doc["system"]["uptime"] = system_metrics.uptime;
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  server.on("/api/thermal", HTTP_GET, [](AsyncWebServerRequest *request) {
    DynamicJsonDocument doc(8192);
    JsonArray thermal_array = doc.createNestedArray("thermal_data");
    
    for (int i = 0; i < 768; i++) {
      thermal_array.add(latest_sensor_data.thermal_array[i]);
    }
    
    doc["timestamp"] = latest_sensor_data.timestamp;
    doc["width"] = 32;
    doc["height"] = 24;
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  server.on("/api/prediction_history", HTTP_GET, [](AsyncWebServerRequest *request) {
    DynamicJsonDocument doc(4096);
    JsonArray predictions = doc.createNestedArray("predictions");
    
    for (int i = 0; i < PREDICTION_BUFFER_SIZE; i++) {
      int index = (prediction_history_index + i) % PREDICTION_BUFFER_SIZE;
      JsonObject pred = predictions.createNestedObject();
      pred["timestamp"] = prediction_history[index].prediction_time;
      pred["success_probability"] = prediction_history[index].success_probability;
      pred["failure_risk"] = prediction_history[index].failure_risk;
      pred["confidence"] = prediction_history[index].confidence;
    }
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  // Configuration endpoints
  server.on("/api/config", HTTP_POST, [](AsyncWebServerRequest *request) {
    // Handle configuration updates
    if (request->hasParam("ml_threshold", true)) {
      float threshold = request->getParam("ml_threshold", true)->value().toFloat();
      updateMLThreshold(threshold);
    }
    
    request->send(200, "application/json", "{\"status\":\"success\"}");
  });
  
  // OTA update endpoint
  server.on("/api/update", HTTP_POST, [](AsyncWebServerRequest *request) {
    // Handle OTA updates
    request->send(200, "application/json", "{\"status\":\"update_initiated\"}");
  }, handleFileUpload);
  
  server.begin();
  Serial.println("Web server started");
}

void loadMLModel() {
  // Load TensorFlow Lite model from SPIFFS
  File model_file = SPIFFS.open("/model.tflite", "r");
  if (!model_file) {
    Serial.println("Failed to open ML model file");
    return;
  }
  
  size_t model_size = model_file.size();
  uint8_t* model_data = (uint8_t*)malloc(model_size);
  model_file.readBytes((char*)model_data, model_size);
  model_file.close();
  
  // Load the model
  model = tflite::GetModel(model_data);
  if (model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema version mismatch");
    free(model_data);
    return;
  }
  
  // Create interpreter
  static tflite::MicroInterpreter static_interpreter(
    model, resolver, tensor_arena, kTensorArenaSize, &micro_error_reporter);
  interpreter = &static_interpreter;
  
  // Allocate tensors
  TfLiteStatus allocate_status = interpreter->AllocateTensors();
  if (allocate_status != kTfLiteOk) {
    Serial.println("Failed to allocate tensors");
    free(model_data);
    return;
  }
  
  // Get input and output tensors
  input = interpreter->input(0);
  output = interpreter->output(0);
  
  ml_model_loaded = true;
  Serial.println("ML model loaded successfully");
  Serial.printf("Model input shape: [%d, %d]\n", input->dims->data[0], input->dims->data[1]);
  Serial.printf("Model output shape: [%d, %d]\n", output->dims->data[0], output->dims->data[1]);
}

void processArduinoData() {
  if (Serial2.available()) {
    String data = Serial2.readStringUntil('\n');
    data.trim();
    
    if (data.startsWith("{") && data.endsWith("}")) {
      // Parse JSON data from Arduino
      DynamicJsonDocument doc(2048);
      DeserializationError error = deserializeJson(doc, data);
      
      if (error) {
        Serial.println("Failed to parse Arduino data");
        return;
      }
      
      // Update sensor data structure
      latest_sensor_data.hotend_temp = doc["hotend_temp"];
      latest_sensor_data.bed_temp = doc["bed_temp"];
      latest_sensor_data.ambient_temp = doc["ambient_temp"];
      latest_sensor_data.flow_rate = doc["flow_rate"];
      latest_sensor_data.current_layer = doc["current_layer"];
      latest_sensor_data.completion_percentage = doc["completion"];
      latest_sensor_data.timestamp = millis();
      
      // Parse thermal array if present
      if (doc.containsKey("thermal_array")) {
        JsonArray thermal_array = doc["thermal_array"];
        for (int i = 0; i < 768 && i < thermal_array.size(); i++) {
          latest_sensor_data.thermal_array[i] = thermal_array[i];
        }
        
        // Store in thermal history buffer
        for (int i = 0; i < 768; i++) {
          thermal_history[thermal_history_index][i] = latest_sensor_data.thermal_array[i];
        }
        thermal_history_index = (thermal_history_index + 1) % THERMAL_BUFFER_SIZE;
      }
      
      // Send data to connected WebSocket clients
      sendDataToWebSocketClients();
    }
  }
}

void performMLPrediction() {
  if (!ml_model_loaded || input == nullptr || output == nullptr) {
    return;
  }
  
  // Prepare input features for ML model
  float features[10];
  features[0] = latest_sensor_data.hotend_temp / 300.0;  // Normalize
  features[1] = latest_sensor_data.bed_temp / 100.0;
  features[2] = latest_sensor_data.flow_rate / 10.0;
  features[3] = calculateThermalUniformity();
  features[4] = calculateFlowStability();
  features[5] = latest_sensor_data.ambient_temp / 50.0;
  features[6] = latest_sensor_data.current_layer / 1000.0;
  features[7] = latest_sensor_data.completion_percentage / 100.0;
  features[8] = calculateThermalGradient();
  features[9] = calculatePrintSpeed();
  
  // Copy features to input tensor
  for (int i = 0; i < 10; i++) {
    input->data.f[i] = features[i];
  }
  
  // Run inference
  TfLiteStatus invoke_status = interpreter->Invoke();
  if (invoke_status != kTfLiteOk) {
    Serial.println("ML inference failed");
    return;
  }
  
  // Extract results
  latest_prediction.success_probability = output->data.f[0];
  latest_prediction.failure_risk = 1.0 - latest_prediction.success_probability;
  latest_prediction.confidence = output->data.f[1];
  latest_prediction.prediction_time = millis();
  
  // Determine failure type based on feature analysis
  latest_prediction.failure_type = predictFailureType(features);
  
  // Store in prediction history
  prediction_history[prediction_history_index] = latest_prediction;
  prediction_history_index = (prediction_history_index + 1) % PREDICTION_BUFFER_SIZE;
  
  // Update system metrics
  system_metrics.total_predictions++;
  if (latest_prediction.confidence > 0.8) {
    system_metrics.successful_predictions++;
  }
  
  // Send alert if high failure risk
  if (latest_prediction.failure_risk > 0.7) {
    sendFailureAlert();
  }
  
  Serial.printf("ML Prediction: Success=%.2f, Risk=%.2f, Confidence=%.2f\n",
    latest_prediction.success_probability,
    latest_prediction.failure_risk,
    latest_prediction.confidence);
}

String predictFailureType(float* features) {
  // Simple rule-based failure type prediction
  // In a real implementation, this would be part of the ML model
  
  if (features[0] > 0.9) { // High hotend temperature
    return "Overheating";
  } else if (features[2] < 0.1) { // Low flow rate
    return "Underextrusion";
  } else if (features[3] < 0.5) { // Poor thermal uniformity
    return "Poor_Adhesion";
  } else if (features[4] < 0.3) { // Flow instability
    return "Flow_Issues";
  } else {
    return "Unknown";
  }
}

void sendDataToWebSocketClients() {
  DynamicJsonDocument doc(2048);
  
  doc["type"] = "sensor_data";
  doc["data"]["hotend_temp"] = latest_sensor_data.hotend_temp;
  doc["data"]["bed_temp"] = latest_sensor_data.bed_temp;
  doc["data"]["flow_rate"] = latest_sensor_data.flow_rate;
  doc["data"]["current_layer"] = latest_sensor_data.current_layer;
  doc["data"]["completion"] = latest_sensor_data.completion_percentage;
  doc["data"]["timestamp"] = latest_sensor_data.timestamp;
  
  String message;
  serializeJson(doc, message);
  ws.textAll(message);
}

void sendFailureAlert() {
  // Send MQTT alert
  DynamicJsonDocument alert_doc(512);
  alert_doc["timestamp"] = millis();
  alert_doc["type"] = "quality_alert";
  alert_doc["failure_risk"] = latest_prediction.failure_risk;
  alert_doc["failure_type"] = latest_prediction.failure_type;
  alert_doc["confidence"] = latest_prediction.confidence;
  
  String alert_message;
  serializeJson(alert_doc, alert_message);
  mqtt.publish("printer/alerts", alert_message.c_str());
  
  // Send WebSocket alert
  DynamicJsonDocument ws_doc(512);
  ws_doc["type"] = "alert";
  ws_doc["severity"] = "high";
  ws_doc["message"] = "High failure risk detected: " + latest_prediction.failure_type;
  ws_doc["data"] = alert_doc;
  
  String ws_message;
  serializeJson(ws_doc, ws_message);
  ws.textAll(ws_message);
  
  // Sound buzzer
  soundAlert();
}

void transmitDataToCloud() {
  if (!mqtt.connected()) return;
  
  // Prepare telemetry data
  DynamicJsonDocument doc(1024);
  doc["device_id"] = "printer_monitor_001";
  doc["timestamp"] = millis();
  doc["sensor_data"]["hotend_temp"] = latest_sensor_data.hotend_temp;
  doc["sensor_data"]["bed_temp"] = latest_sensor_data.bed_temp;
  doc["sensor_data"]["flow_rate"] = latest_sensor_data.flow_rate;
  doc["sensor_data"]["current_layer"] = latest_sensor_data.current_layer;
  doc["sensor_data"]["completion"] = latest_sensor_data.completion_percentage;
  doc["prediction"]["success_probability"] = latest_prediction.success_probability;
  doc["prediction"]["failure_risk"] = latest_prediction.failure_risk;
  doc["prediction"]["confidence"] = latest_prediction.confidence;
  doc["system"]["memory_usage"] = system_metrics.memory_usage;
  doc["system"]["cpu_usage"] = system_metrics.cpu_usage;
  
  String telemetry;
  serializeJson(doc, telemetry);
  mqtt.publish("printer/telemetry", telemetry.c_str());
}

void updateSystemMetrics() {
  system_metrics.uptime = millis();
  system_metrics.memory_usage = (float)(ESP.getFreeHeap()) / ESP.getHeapSize() * 100.0;
  system_metrics.wifi_signal_strength = WiFi.RSSI();
  
  // Simple CPU usage estimation
  static unsigned long last_cpu_time = 0;
  static unsigned long cpu_busy_time = 0;
  unsigned long current_time = millis();
  
  if (current_time - last_cpu_time >= 1000) {
    system_metrics.cpu_usage = (float)cpu_busy_time / (current_time - last_cpu_time) * 100.0;
    cpu_busy_time = 0;
    last_cpu_time = current_time;
  }
}

// Helper functions for feature calculation
float calculateThermalUniformity() {
  if (thermal_history_index == 0) return 0.5; // Default value
  
  int latest_index = (thermal_history_index - 1 + THERMAL_BUFFER_SIZE) % THERMAL_BUFFER_SIZE;
  
  float sum = 0;
  float sum_sq = 0;
  for (int i = 0; i < 768; i++) {
    float temp = thermal_history[latest_index][i];
    sum += temp;
    sum_sq += temp * temp;
  }
  
  float mean = sum / 768.0;
  float variance = (sum_sq / 768.0) - (mean * mean);
  float std_dev = sqrt(variance);
  
  // Normalize: lower std_dev = higher uniformity
  return constrain(1.0 - (std_dev / 50.0), 0.0, 1.0);
}

float calculateFlowStability() {
  // Calculate flow rate stability over recent history
  static float flow_history[10];
  static int flow_index = 0;
  
  flow_history[flow_index] = latest_sensor_data.flow_rate;
  flow_index = (flow_index + 1) % 10;
  
  float sum = 0, sum_sq = 0;
  for (int i = 0; i < 10; i++) {
    sum += flow_history[i];
    sum_sq += flow_history[i] * flow_history[i];
  }
  
  float mean = sum / 10.0;
  float variance = (sum_sq / 10.0) - (mean * mean);
  float cv = sqrt(variance) / mean; // Coefficient of variation
  
  return constrain(1.0 - cv, 0.0, 1.0);
}

float calculateThermalGradient() {
  if (thermal_history_index == 0) return 0.0;
  
  int latest_index = (thermal_history_index - 1 + THERMAL_BUFFER_SIZE) % THERMAL_BUFFER_SIZE;
  
  float max_gradient = 0;
  for (int y = 0; y < 23; y++) {
    for (int x = 0; x < 31; x++) {
      int current = y * 32 + x;
      int right = y * 32 + (x + 1);
      int down = (y + 1) * 32 + x;
      
      float grad_x = abs(thermal_history[latest_index][right] - thermal_history[latest_index][current]);
      float grad_y = abs(thermal_history[latest_index][down] - thermal_history[latest_index][current]);
      float gradient = sqrt(grad_x * grad_x + grad_y * grad_y);
      
      if (gradient > max_gradient) {
        max_gradient = gradient;
      }
    }
  }
  
  return constrain(max_gradient / 100.0, 0.0, 1.0);
}

float calculatePrintSpeed() {
  // Estimate print speed from flow rate and layer changes
  static unsigned long last_layer_time = 0;
  static uint16_t last_layer = 0;
  
  if (latest_sensor_data.current_layer > last_layer) {
    unsigned long layer_time = millis() - last_layer_time;
    float speed = 1.0 / (layer_time / 60000.0); // layers per minute
    last_layer_time = millis();
    last_layer = latest_sensor_data.current_layer;
    return constrain(speed / 10.0, 0.0, 1.0); // Normalize
  }
  
  return 0.5; // Default
}

// Communication callbacks
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.println("MQTT message received: " + message);
  
  if (String(topic) == "printer/commands") {
    handleMQTTCommand(message);
  } else if (String(topic) == "printer/config") {
    handleMQTTConfig(message);
  }
}

void onWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, 
                     AwsEventType type, void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", 
                    client->id(), client->remoteIP().toString().c_str());
      // Send initial data to new client
      sendDataToWebSocketClients();
      break;
      
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
      
    case WS_EVT_DATA:
      handleWebSocketData(client, data, len);
      break;
      
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void handleWebSocketData(AsyncWebSocketClient *client, uint8_t *data, size_t len) {
  data[len] = 0; // Null terminate
  String message = (char*)data;
  
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, message);
  
  if (error) {
    client->text("{\"error\":\"Invalid JSON\"}");
    return;
  }
  
  String command = doc["command"];
  
  if (command == "get_thermal") {
    sendThermalDataToClient(client);
  } else if (command == "pause_print") {
    sendCommandToArduino("PAUSE");
  } else if (command == "resume_print") {
    sendCommandToArduino("RESUME");
  } else if (command == "emergency_stop") {
    sendCommandToArduino("EMERGENCY_STOP");
  }
}

// Utility functions
void reconnectWiFi() {
  static unsigned long last_attempt = 0;
  if (millis() - last_attempt > 10000) { // Try every 10 seconds
    Serial.println("Reconnecting to WiFi...");
    WiFi.reconnect();
    last_attempt = millis();
  }
}

void reconnectMQTT() {
  static unsigned long last_attempt = 0;
  if (millis() - last_attempt > 5000) { // Try every 5 seconds
    if (mqtt.connect("ESP32_PrintMonitor")) {
      Serial.println("MQTT reconnected");
      mqtt.subscribe("printer/commands");
      mqtt.subscribe("printer/config");
    }
    last_attempt = millis();
  }
}

void soundAlert() {
  // Sound buzzer pattern for alert
  for (int i = 0; i < 3; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    delay(200);
  }
}

void handleUserButton() {
  static bool last_button_state = HIGH;
  static unsigned long button_press_time = 0;
  
  bool current_state = digitalRead(USER_BUTTON_PIN);
  
  if (last_button_state == HIGH && current_state == LOW) {
    button_press_time = millis();
  } else if (last_button_state == LOW && current_state == HIGH) {
    unsigned long press_duration = millis() - button_press_time;
    
    if (press_duration > 3000) {
      // Long press: Reset WiFi settings
      Serial.println("Long press detected - Resetting WiFi settings");
      resetWiFiSettings();
    } else if (press_duration > 100) {
      // Short press: Toggle status
      Serial.println("Short press detected - Toggling status");
      toggleStatus();
    }
  }
  
  last_button_state = current_state;
}

void sendCommandToArduino(String command) {
  Serial2.println(command);
  Serial.println("Sent to Arduino: " + command);
}

// Additional helper functions...
void initializeMetrics() {
  system_metrics.cpu_usage = 0;
  system_metrics.memory_usage = 0;
  system_metrics.wifi_signal_strength = 0;
  system_metrics.uptime = 0;
  system_metrics.total_predictions = 0;
  system_metrics.successful_predictions = 0;
}