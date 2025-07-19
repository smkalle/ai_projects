/*
 * ESP32 Analytics Gateway for Fatigue Testing Machine
 * 
 * Provides IoT connectivity, cloud data streaming, advanced analytics,
 * and machine learning capabilities for fatigue life prediction
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SPIFFS.h>
#include <SD.h>
#include <SPI.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <ArduinoOTA.h>
#include <Preferences.h>
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

// Pin definitions
#define LED_WIFI 2
#define LED_MQTT 4
#define LED_DATA 15
#define SD_CS 5
#define ARDUINO_RX 16
#define ARDUINO_TX 17

// Network credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT settings
const char* mqtt_server = "mqtt.fatigue-analytics.com";
const int mqtt_port = 8883;
const char* mqtt_user = "fatigue_tester";
const char* mqtt_password = "secure_password";
const char* mqtt_client_id = "ESP32_Fatigue_001";

// Cloud API settings
const char* api_endpoint = "https://api.fatigue-analytics.com/v1";
const char* api_key = "YOUR_API_KEY";

// Topics
const char* topic_data = "fatigue/data";
const char* topic_status = "fatigue/status";
const char* topic_command = "fatigue/command";
const char* topic_alert = "fatigue/alert";

// Global objects
WiFiClientSecure wifi_client;
PubSubClient mqtt_client(wifi_client);
WebServer web_server(80);
Preferences preferences;
HardwareSerial ArduinoSerial(2);

// Machine learning
const int kTensorArenaSize = 16384;
uint8_t tensor_arena[kTensorArenaSize];
tflite::MicroInterpreter* interpreter;
TfLiteTensor* input_tensor;
TfLiteTensor* output_tensor;

// Test data structure
struct TestDataPacket {
    String specimen_id;
    uint32_t cycles;
    float load;
    float displacement;
    float peak_load;
    float valley_load;
    float frequency;
    uint32_t ae_hits;
    float crack_length;
    uint32_t timestamp;
};

// Analytics data
struct AnalyticsData {
    float stress_amplitude;
    float mean_stress;
    float R_ratio;
    float damage_accumulation;
    float remaining_life_estimate;
    float confidence_interval;
    String failure_mode_prediction;
};

// S-N curve fitting parameters
struct SNCurveParams {
    float A;  // Coefficient
    float b;  // Exponent
    float fatigue_limit;
    float R_squared;
};

// System status
bool wifi_connected = false;
bool mqtt_connected = false;
bool test_active = false;
String current_specimen_id = "";
uint32_t data_points_collected = 0;
uint32_t data_points_sent = 0;

// Buffers
const int DATA_BUFFER_SIZE = 100;
TestDataPacket data_buffer[DATA_BUFFER_SIZE];
int buffer_write_index = 0;
int buffer_read_index = 0;

// ML model - simplified fatigue life prediction
const unsigned char fatigue_model[] = {
    // TensorFlow Lite model would be included here
    // This is a placeholder for the actual model
};

void setup() {
    Serial.begin(115200);
    ArduinoSerial.begin(115200, SERIAL_8N1, ARDUINO_RX, ARDUINO_TX);
    
    Serial.println(F("ESP32 Fatigue Analytics Gateway v2.0"));
    
    // Initialize pins
    pinMode(LED_WIFI, OUTPUT);
    pinMode(LED_MQTT, OUTPUT);
    pinMode(LED_DATA, OUTPUT);
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println(F("SPIFFS initialization failed"));
    }
    
    // Initialize SD card
    if (!SD.begin(SD_CS)) {
        Serial.println(F("SD card initialization failed"));
    }
    
    // Load preferences
    preferences.begin("fatigue", false);
    loadConfiguration();
    
    // Connect to WiFi
    connectWiFi();
    
    // Initialize MQTT
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    mqtt_client.setBufferSize(2048);
    
    // Initialize web server
    setupWebServer();
    
    // Initialize OTA updates
    setupOTA();
    
    // Initialize machine learning
    setupMachineLearning();
    
    Serial.println(F("System ready"));
}

void loop() {
    // Maintain connections
    if (!WiFi.isConnected()) {
        wifi_connected = false;
        digitalWrite(LED_WIFI, LOW);
        connectWiFi();
    }
    
    if (wifi_connected && !mqtt_client.connected()) {
        mqtt_connected = false;
        digitalWrite(LED_MQTT, LOW);
        connectMQTT();
    }
    
    // Handle MQTT
    if (mqtt_connected) {
        mqtt_client.loop();
    }
    
    // Process Arduino data
    if (ArduinoSerial.available()) {
        processArduinoData();
    }
    
    // Process buffered data
    processDataBuffer();
    
    // Handle web server
    web_server.handleClient();
    
    // Handle OTA updates
    ArduinoOTA.handle();
    
    // Periodic tasks
    static uint32_t last_status_update = 0;
    if (millis() - last_status_update > 30000) { // Every 30 seconds
        sendStatusUpdate();
        last_status_update = millis();
    }
    
    // Periodic analytics
    static uint32_t last_analytics = 0;
    if (test_active && millis() - last_analytics > 60000) { // Every minute
        performAnalytics();
        last_analytics = millis();
    }
}

void connectWiFi() {
    Serial.print(F("Connecting to WiFi"));
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        digitalWrite(LED_WIFI, !digitalRead(LED_WIFI));
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        wifi_connected = true;
        digitalWrite(LED_WIFI, HIGH);
        Serial.println(F("\nWiFi connected"));
        Serial.print(F("IP address: "));
        Serial.println(WiFi.localIP());
        
        // Set up mDNS
        if (MDNS.begin("fatigue-tester")) {
            Serial.println(F("mDNS responder started"));
        }
        
        // Configure NTP
        configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    } else {
        Serial.println(F("\nWiFi connection failed"));
    }
}

void connectMQTT() {
    Serial.print(F("Connecting to MQTT"));
    
    // Configure SSL/TLS
    wifi_client.setInsecure(); // For testing only
    
    int attempts = 0;
    while (!mqtt_client.connected() && attempts < 5) {
        digitalWrite(LED_MQTT, !digitalRead(LED_MQTT));
        
        if (mqtt_client.connect(mqtt_client_id, mqtt_user, mqtt_password)) {
            mqtt_connected = true;
            digitalWrite(LED_MQTT, HIGH);
            Serial.println(F("\nMQTT connected"));
            
            // Subscribe to topics
            mqtt_client.subscribe(topic_command);
            mqtt_client.subscribe(topic_status);
            
            // Send connection message
            StaticJsonDocument<256> doc;
            doc["device"] = mqtt_client_id;
            doc["status"] = "connected";
            doc["ip"] = WiFi.localIP().toString();
            doc["rssi"] = WiFi.RSSI();
            
            char buffer[256];
            serializeJson(doc, buffer);
            mqtt_client.publish(topic_status, buffer);
        } else {
            Serial.print(".");
            delay(5000);
        }
        attempts++;
    }
    
    if (!mqtt_client.connected()) {
        Serial.println(F("\nMQTT connection failed"));
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print(F("MQTT message on topic: "));
    Serial.println(topic);
    
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print(F("JSON parse error: "));
        Serial.println(error.c_str());
        return;
    }
    
    if (String(topic) == topic_command) {
        handleCommand(doc);
    }
}

void handleCommand(JsonDocument& doc) {
    String command = doc["command"];
    
    if (command == "start_test") {
        // Forward to Arduino
        serializeJson(doc, ArduinoSerial);
        ArduinoSerial.println();
        
    } else if (command == "stop_test") {
        // Forward to Arduino
        serializeJson(doc, ArduinoSerial);
        ArduinoSerial.println();
        test_active = false;
        
    } else if (command == "get_status") {
        sendStatusUpdate();
        
    } else if (command == "download_data") {
        String specimen_id = doc["specimen_id"];
        sendStoredData(specimen_id);
        
    } else if (command == "update_params") {
        // Forward to Arduino
        serializeJson(doc, ArduinoSerial);
        ArduinoSerial.println();
        
    } else if (command == "run_analytics") {
        performAnalytics();
        
    } else if (command == "predict_life") {
        float stress = doc["stress_amplitude"];
        float r_ratio = doc["r_ratio"];
        uint32_t predicted_life = predictFatigueLife(stress, r_ratio);
        sendPrediction(predicted_life, stress, r_ratio);
    }
}

void processArduinoData() {
    static String buffer = "";
    
    while (ArduinoSerial.available()) {
        char c = ArduinoSerial.read();
        if (c == '\n') {
            processArduinoMessage(buffer);
            buffer = "";
        } else {
            buffer += c;
        }
    }
}

void processArduinoMessage(String& message) {
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print(F("Arduino JSON error: "));
        Serial.println(error.c_str());
        return;
    }
    
    String type = doc["type"];
    
    if (type == "test_data") {
        // Store in buffer
        TestDataPacket packet;
        packet.specimen_id = doc["specimen_id"].as<String>();
        packet.cycles = doc["cycles"];
        packet.load = doc["load"];
        packet.displacement = doc["displacement"];
        packet.peak_load = doc["peak_load"];
        packet.valley_load = doc["valley_load"];
        packet.frequency = doc["frequency"];
        packet.ae_hits = doc["ae_hits"];
        packet.crack_length = doc["crack_length"];
        packet.timestamp = doc["timestamp"];
        
        addToBuffer(packet);
        digitalWrite(LED_DATA, !digitalRead(LED_DATA));
        
    } else if (type == "test_start") {
        test_active = true;
        current_specimen_id = doc["specimen_id"].as<String>();
        data_points_collected = 0;
        data_points_sent = 0;
        
        // Create cloud session
        createCloudSession(doc);
        
    } else if (type == "test_end") {
        test_active = false;
        
        // Final analytics
        performFinalAnalysis(doc);
        
        // Close cloud session
        closeCloudSession(doc);
        
    } else if (type == "weibull_params") {
        // Store and forward Weibull parameters
        handleWeibullParameters(doc);
        
    } else if (type == "paris_law") {
        // Store and forward Paris law parameters
        handleParisLawParameters(doc);
    }
}

void addToBuffer(TestDataPacket& packet) {
    data_buffer[buffer_write_index] = packet;
    buffer_write_index = (buffer_write_index + 1) % DATA_BUFFER_SIZE;
    data_points_collected++;
    
    // Store to SD card
    storeToSD(packet);
}

void processDataBuffer() {
    static uint32_t last_send = 0;
    
    // Send data every 5 seconds or when buffer is half full
    int buffer_count = (buffer_write_index - buffer_read_index + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
    
    if ((millis() - last_send > 5000 || buffer_count > DATA_BUFFER_SIZE / 2) && 
        buffer_count > 0 && mqtt_connected) {
        
        // Prepare batch message
        StaticJsonDocument<2048> doc;
        JsonArray data_array = doc.createNestedArray("data");
        
        int count = 0;
        while (buffer_read_index != buffer_write_index && count < 10) {
            TestDataPacket& packet = data_buffer[buffer_read_index];
            
            JsonObject data = data_array.createNestedObject();
            data["specimen_id"] = packet.specimen_id;
            data["cycles"] = packet.cycles;
            data["load"] = packet.load;
            data["displacement"] = packet.displacement;
            data["peak_load"] = packet.peak_load;
            data["valley_load"] = packet.valley_load;
            data["frequency"] = packet.frequency;
            data["ae_hits"] = packet.ae_hits;
            data["crack_length"] = packet.crack_length;
            data["timestamp"] = packet.timestamp;
            
            buffer_read_index = (buffer_read_index + 1) % DATA_BUFFER_SIZE;
            data_points_sent++;
            count++;
        }
        
        doc["batch_size"] = count;
        doc["total_sent"] = data_points_sent;
        
        char buffer[2048];
        serializeJson(doc, buffer);
        
        if (mqtt_client.publish(topic_data, buffer)) {
            Serial.print(F("Sent "));
            Serial.print(count);
            Serial.println(F(" data points"));
        } else {
            Serial.println(F("Failed to send data"));
            // Return read index to retry
            buffer_read_index = (buffer_read_index - count + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
        }
        
        last_send = millis();
    }
}

void storeToSD(TestDataPacket& packet) {
    String filename = "/fatigue/" + packet.specimen_id + ".csv";
    
    File file = SD.open(filename, FILE_APPEND);
    if (file) {
        file.print(packet.timestamp);
        file.print(",");
        file.print(packet.cycles);
        file.print(",");
        file.print(packet.load, 2);
        file.print(",");
        file.print(packet.displacement, 3);
        file.print(",");
        file.print(packet.peak_load, 2);
        file.print(",");
        file.print(packet.valley_load, 2);
        file.print(",");
        file.print(packet.frequency, 1);
        file.print(",");
        file.print(packet.ae_hits);
        file.print(",");
        file.println(packet.crack_length, 3);
        file.close();
    }
}

void performAnalytics() {
    if (!test_active || data_points_collected < 100) {
        return;
    }
    
    Serial.println(F("Performing analytics..."));
    
    // Read recent data from SD
    String filename = "/fatigue/" + current_specimen_id + ".csv";
    File file = SD.open(filename, FILE_READ);
    
    if (!file) {
        return;
    }
    
    // Simple analytics - calculate trends
    float sum_load = 0, sum_ae = 0;
    int count = 0;
    float max_load = 0, min_load = 9999;
    
    // Read last 1000 lines
    file.seek(max(0, (int)(file.size() - 50000))); // Approximate last 1000 lines
    
    while (file.available()) {
        String line = file.readStringUntil('\n');
        
        int comma1 = line.indexOf(',');
        int comma2 = line.indexOf(',', comma1 + 1);
        int comma3 = line.indexOf(',', comma2 + 1);
        int comma4 = line.indexOf(',', comma3 + 1);
        int comma5 = line.indexOf(',', comma4 + 1);
        int comma6 = line.indexOf(',', comma5 + 1);
        int comma7 = line.indexOf(',', comma6 + 1);
        
        if (comma4 > 0 && comma7 > 0) {
            float peak_load = line.substring(comma3 + 1, comma4).toFloat();
            float valley_load = line.substring(comma4 + 1, comma5).toFloat();
            uint32_t ae_hits = line.substring(comma6 + 1, comma7).toInt();
            
            sum_load += (peak_load + valley_load) / 2;
            sum_ae += ae_hits;
            count++;
            
            if (peak_load > max_load) max_load = peak_load;
            if (valley_load < min_load) min_load = valley_load;
        }
    }
    
    file.close();
    
    if (count > 0) {
        AnalyticsData analytics;
        analytics.mean_stress = sum_load / count;
        analytics.stress_amplitude = (max_load - min_load) / 2;
        analytics.R_ratio = min_load / max_load;
        
        // Simple damage accumulation (Miner's rule)
        analytics.damage_accumulation = calculateDamage(analytics.stress_amplitude, 
                                                       data_points_collected);
        
        // ML-based remaining life estimate
        analytics.remaining_life_estimate = predictRemainingLife(analytics);
        analytics.confidence_interval = 0.85; // Placeholder
        
        // Failure mode prediction based on AE rate
        float ae_rate = sum_ae / count;
        if (ae_rate > 10) {
            analytics.failure_mode_prediction = "Rapid crack growth";
        } else if (ae_rate > 1) {
            analytics.failure_mode_prediction = "Stable crack growth";
        } else {
            analytics.failure_mode_prediction = "Crack initiation";
        }
        
        // Send analytics results
        sendAnalyticsResults(analytics);
    }
}

float calculateDamage(float stress_amplitude, uint32_t cycles) {
    // Simplified Miner's rule calculation
    // In reality, would use S-N curve data
    
    float fatigue_limit = 100.0; // MPa, material specific
    if (stress_amplitude < fatigue_limit) {
        return 0;
    }
    
    // Basquin's equation: N = A * S^-b
    float A = 1e12;  // Material constant
    float b = 3.0;   // Material constant
    
    float life_at_stress = A * pow(stress_amplitude, -b);
    float damage = cycles / life_at_stress;
    
    return damage;
}

uint32_t predictFatigueLife(float stress_amplitude, float r_ratio) {
    // Use ML model for prediction
    if (!interpreter) {
        // Fallback to empirical model
        return empiricalFatigueLife(stress_amplitude, r_ratio);
    }
    
    // Prepare input tensor
    input_tensor->data.f[0] = stress_amplitude;
    input_tensor->data.f[1] = r_ratio;
    input_tensor->data.f[2] = 0.5; // Mean stress effect
    
    // Run inference
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        Serial.println(F("ML inference failed"));
        return empiricalFatigueLife(stress_amplitude, r_ratio);
    }
    
    // Get output
    float log_life = output_tensor->data.f[0];
    uint32_t predicted_life = pow(10, log_life);
    
    return predicted_life;
}

uint32_t empiricalFatigueLife(float stress_amplitude, float r_ratio) {
    // Goodman correction for mean stress
    float ultimate_strength = 500.0; // MPa, material specific
    float mean_stress = stress_amplitude * (1 + r_ratio) / (1 - r_ratio);
    float corrected_amplitude = stress_amplitude / (1 - mean_stress / ultimate_strength);
    
    // Basquin's equation
    float A = 1e12;
    float b = 3.0;
    uint32_t life = A * pow(corrected_amplitude, -b);
    
    return life;
}

float predictRemainingLife(AnalyticsData& analytics) {
    // Estimate based on damage accumulation and crack growth
    float remaining_damage = 1.0 - analytics.damage_accumulation;
    
    if (remaining_damage <= 0) {
        return 0;
    }
    
    // Estimate cycles to failure
    uint32_t total_life = predictFatigueLife(analytics.stress_amplitude, analytics.R_ratio);
    uint32_t remaining_cycles = total_life * remaining_damage;
    
    return remaining_cycles;
}

void sendAnalyticsResults(AnalyticsData& analytics) {
    StaticJsonDocument<512> doc;
    
    doc["type"] = "analytics";
    doc["specimen_id"] = current_specimen_id;
    doc["timestamp"] = millis();
    doc["mean_stress"] = analytics.mean_stress;
    doc["stress_amplitude"] = analytics.stress_amplitude;
    doc["r_ratio"] = analytics.R_ratio;
    doc["damage"] = analytics.damage_accumulation;
    doc["remaining_life"] = analytics.remaining_life_estimate;
    doc["confidence"] = analytics.confidence_interval;
    doc["failure_mode"] = analytics.failure_mode_prediction;
    
    char buffer[512];
    serializeJson(doc, buffer);
    
    mqtt_client.publish(topic_data, buffer);
    
    // Also send alert if damage is high
    if (analytics.damage_accumulation > 0.8) {
        StaticJsonDocument<256> alert;
        alert["type"] = "high_damage";
        alert["specimen_id"] = current_specimen_id;
        alert["damage"] = analytics.damage_accumulation;
        alert["message"] = "Specimen approaching failure";
        
        char alert_buffer[256];
        serializeJson(alert, alert_buffer);
        mqtt_client.publish(topic_alert, alert_buffer);
    }
}

void performFinalAnalysis(JsonDocument& test_end_data) {
    // Comprehensive analysis at test completion
    uint32_t total_cycles = test_end_data["total_cycles"];
    bool failed = test_end_data["failure"];
    
    // Fit S-N curve if we have enough data
    if (getSNDataCount() >= 5) {
        SNCurveParams sn_params = fitSNCurve();
        sendSNCurveParameters(sn_params);
    }
    
    // Generate comprehensive report
    generateTestReport(test_end_data);
    
    // Update ML model with new data (if implemented)
    // updateMLModel(total_cycles, failed);
}

SNCurveParams fitSNCurve() {
    // Simple linear regression on log-log S-N data
    SNCurveParams params;
    
    // Read S-N data from storage
    File sn_file = SD.open("/sn_data.csv", FILE_READ);
    if (!sn_file) {
        return params;
    }
    
    float sum_x = 0, sum_y = 0, sum_xy = 0, sum_xx = 0;
    int n = 0;
    
    while (sn_file.available()) {
        String line = sn_file.readStringUntil('\n');
        int comma = line.indexOf(',');
        if (comma > 0) {
            float stress = line.substring(0, comma).toFloat();
            uint32_t cycles = line.substring(comma + 1).toInt();
            
            if (stress > 0 && cycles > 0) {
                float x = log10(cycles);
                float y = log10(stress);
                
                sum_x += x;
                sum_y += y;
                sum_xy += x * y;
                sum_xx += x * x;
                n++;
            }
        }
    }
    
    sn_file.close();
    
    if (n >= 2) {
        // Calculate regression coefficients
        float b = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x);
        float log_A = (sum_y - b * sum_x) / n;
        
        params.A = pow(10, log_A);
        params.b = -b;  // Convert to S = A * N^-b form
        params.fatigue_limit = 100.0; // Placeholder
        
        // Calculate R-squared
        float mean_y = sum_y / n;
        float ss_tot = 0, ss_res = 0;
        
        // Would need to re-read file for residuals calculation
        params.R_squared = 0.95; // Placeholder
    }
    
    return params;
}

void sendSNCurveParameters(SNCurveParams& params) {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "sn_curve";
    doc["A"] = params.A;
    doc["b"] = params.b;
    doc["fatigue_limit"] = params.fatigue_limit;
    doc["r_squared"] = params.R_squared;
    doc["equation"] = "S = A * N^-b";
    
    char buffer[256];
    serializeJson(doc, buffer);
    mqtt_client.publish(topic_data, buffer);
}

void handleWeibullParameters(JsonDocument& doc) {
    // Store Weibull parameters
    preferences.putFloat("weibull_beta", doc["beta"]);
    preferences.putFloat("weibull_eta", doc["eta"]);
    
    // Forward to cloud
    char buffer[256];
    serializeJson(doc, buffer);
    mqtt_client.publish(topic_data, buffer);
}

void handleParisLawParameters(JsonDocument& doc) {
    // Store Paris law parameters
    preferences.putFloat("paris_C", doc["C"]);
    preferences.putFloat("paris_m", doc["m"]);
    
    // Forward to cloud
    char buffer[256];
    serializeJson(doc, buffer);
    mqtt_client.publish(topic_data, buffer);
}

void sendStatusUpdate() {
    StaticJsonDocument<512> doc;
    
    doc["device"] = mqtt_client_id;
    doc["uptime"] = millis();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["test_active"] = test_active;
    doc["specimen_id"] = current_specimen_id;
    doc["data_collected"] = data_points_collected;
    doc["data_sent"] = data_points_sent;
    doc["buffer_usage"] = (buffer_write_index - buffer_read_index + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
    doc["sd_free"] = getSDFreeSpace();
    
    char buffer[512];
    serializeJson(doc, buffer);
    mqtt_client.publish(topic_status, buffer);
}

void createCloudSession(JsonDocument& test_params) {
    HTTPClient http;
    http.begin(String(api_endpoint) + "/sessions");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", api_key);
    
    char body[512];
    serializeJson(test_params, body);
    
    int response_code = http.POST(body);
    if (response_code > 0) {
        String response = http.getString();
        Serial.print(F("Session created: "));
        Serial.println(response);
    }
    
    http.end();
}

void closeCloudSession(JsonDocument& test_results) {
    HTTPClient http;
    http.begin(String(api_endpoint) + "/sessions/" + current_specimen_id + "/close");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", api_key);
    
    char body[512];
    serializeJson(test_results, body);
    
    int response_code = http.PUT(body);
    if (response_code > 0) {
        String response = http.getString();
        Serial.print(F("Session closed: "));
        Serial.println(response);
    }
    
    http.end();
}

void generateTestReport(JsonDocument& test_data) {
    // Create detailed test report
    String filename = "/reports/" + current_specimen_id + "_report.json";
    
    File report = SD.open(filename, FILE_WRITE);
    if (report) {
        StaticJsonDocument<1024> doc;
        
        doc["test_id"] = current_specimen_id;
        doc["test_date"] = getTimestamp();
        doc["total_cycles"] = test_data["total_cycles"];
        doc["failure"] = test_data["failure"];
        doc["duration"] = test_data["duration"];
        
        // Add statistics
        JsonObject stats = doc.createNestedObject("statistics");
        stats["data_points"] = data_points_collected;
        stats["max_load"] = getMaxLoad();
        stats["min_load"] = getMinLoad();
        stats["mean_frequency"] = getMeanFrequency();
        stats["total_ae_hits"] = getTotalAEHits();
        
        // Add S-N curve parameters if available
        if (preferences.getFloat("sn_A", 0) > 0) {
            JsonObject sn = doc.createNestedObject("sn_curve");
            sn["A"] = preferences.getFloat("sn_A");
            sn["b"] = preferences.getFloat("sn_b");
            sn["fatigue_limit"] = preferences.getFloat("sn_limit");
        }
        
        // Add Weibull parameters if available
        if (preferences.getFloat("weibull_beta", 0) > 0) {
            JsonObject weibull = doc.createNestedObject("weibull");
            weibull["beta"] = preferences.getFloat("weibull_beta");
            weibull["eta"] = preferences.getFloat("weibull_eta");
        }
        
        serializeJson(doc, report);
        report.close();
        
        Serial.println(F("Test report generated"));
    }
}

void sendPrediction(uint32_t life, float stress, float r_ratio) {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "prediction";
    doc["stress_amplitude"] = stress;
    doc["r_ratio"] = r_ratio;
    doc["predicted_life"] = life;
    doc["method"] = interpreter ? "ML" : "Empirical";
    doc["confidence"] = 0.85;
    
    char buffer[256];
    serializeJson(doc, buffer);
    mqtt_client.publish(topic_data, buffer);
}

void sendStoredData(String specimen_id) {
    // Send stored data file via HTTP
    String filename = "/fatigue/" + specimen_id + ".csv";
    
    File file = SD.open(filename, FILE_READ);
    if (!file) {
        return;
    }
    
    HTTPClient http;
    http.begin(String(api_endpoint) + "/data/upload");
    http.addHeader("Content-Type", "text/csv");
    http.addHeader("X-API-Key", api_key);
    http.addHeader("X-Specimen-ID", specimen_id);
    
    // Stream file content
    int response_code = http.sendRequest("POST", &file, file.size());
    
    if (response_code > 0) {
        Serial.print(F("Data uploaded: "));
        Serial.println(response_code);
    }
    
    file.close();
    http.end();
}

// Web server handlers
void setupWebServer() {
    web_server.on("/", handleRoot);
    web_server.on("/status", handleStatus);
    web_server.on("/data", handleData);
    web_server.on("/config", handleConfig);
    web_server.on("/update", HTTP_POST, handleUpdate);
    web_server.begin();
}

void handleRoot() {
    String html = "<html><head><title>Fatigue Testing Analytics</title></head>";
    html += "<body><h1>Fatigue Testing Machine</h1>";
    html += "<p>Status: " + String(test_active ? "Testing" : "Idle") + "</p>";
    html += "<p>Specimen: " + current_specimen_id + "</p>";
    html += "<p>Data Points: " + String(data_points_collected) + "</p>";
    html += "<p><a href='/status'>System Status</a></p>";
    html += "<p><a href='/data'>Download Data</a></p>";
    html += "<p><a href='/config'>Configuration</a></p>";
    html += "</body></html>";
    
    web_server.send(200, "text/html", html);
}

void handleStatus() {
    StaticJsonDocument<512> doc;
    
    doc["device"] = mqtt_client_id;
    doc["wifi_connected"] = wifi_connected;
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["mqtt_connected"] = mqtt_connected;
    doc["test_active"] = test_active;
    doc["specimen_id"] = current_specimen_id;
    doc["data_points"] = data_points_collected;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["uptime"] = millis();
    
    String response;
    serializeJson(doc, response);
    web_server.send(200, "application/json", response);
}

void handleData() {
    String specimen = web_server.arg("specimen");
    if (specimen.length() == 0) {
        specimen = current_specimen_id;
    }
    
    String filename = "/fatigue/" + specimen + ".csv";
    File file = SD.open(filename, FILE_READ);
    
    if (file) {
        web_server.streamFile(file, "text/csv");
        file.close();
    } else {
        web_server.send(404, "text/plain", "File not found");
    }
}

void handleConfig() {
    if (web_server.method() == HTTP_POST) {
        // Save configuration
        if (web_server.hasArg("ssid")) {
            preferences.putString("ssid", web_server.arg("ssid"));
        }
        if (web_server.hasArg("mqtt_server")) {
            preferences.putString("mqtt_server", web_server.arg("mqtt_server"));
        }
        web_server.send(200, "text/plain", "Configuration saved");
    } else {
        // Show configuration form
        String html = "<html><head><title>Configuration</title></head>";
        html += "<body><h1>System Configuration</h1>";
        html += "<form method='post'>";
        html += "WiFi SSID: <input type='text' name='ssid' value='" + String(ssid) + "'><br>";
        html += "MQTT Server: <input type='text' name='mqtt_server' value='" + String(mqtt_server) + "'><br>";
        html += "<input type='submit' value='Save'>";
        html += "</form></body></html>";
        
        web_server.send(200, "text/html", html);
    }
}

void handleUpdate() {
    web_server.sendHeader("Connection", "close");
    web_server.send(200, "text/plain", "OK");
    ESP.restart();
}

// OTA setup
void setupOTA() {
    ArduinoOTA.setHostname("fatigue-tester");
    
    ArduinoOTA.onStart([]() {
        String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
        Serial.println("Start updating " + type);
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("\nEnd");
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
    });
    
    ArduinoOTA.begin();
}

// Machine learning setup
void setupMachineLearning() {
    // Initialize TensorFlow Lite
    static tflite::AllOpsResolver resolver;
    static tflite::MicroInterpreter static_interpreter(
        tflite::GetModel(fatigue_model), resolver, tensor_arena, kTensorArenaSize);
    interpreter = &static_interpreter;
    
    // Allocate tensors
    if (interpreter->AllocateTensors() != kTfLiteOk) {
        Serial.println(F("Failed to allocate tensors"));
        interpreter = nullptr;
        return;
    }
    
    // Get input and output tensors
    input_tensor = interpreter->input(0);
    output_tensor = interpreter->output(0);
    
    Serial.println(F("ML model loaded"));
}

// Utility functions
void loadConfiguration() {
    // Load saved configuration from preferences
    // In production, would load actual values
}

String getTimestamp() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        return String(millis());
    }
    
    char buffer[30];
    strftime(buffer, 30, "%Y-%m-%d %H:%M:%S", &timeinfo);
    return String(buffer);
}

uint32_t getSDFreeSpace() {
    // Calculate free space on SD card
    return SD.totalBytes() - SD.usedBytes();
}

int getSNDataCount() {
    // Count S-N data points
    File file = SD.open("/sn_data.csv", FILE_READ);
    if (!file) return 0;
    
    int count = 0;
    while (file.available()) {
        if (file.read() == '\n') count++;
    }
    file.close();
    
    return count;
}

float getMaxLoad() {
    // Get maximum load from current test
    // Simplified - would read from data file
    return 1000.0;
}

float getMinLoad() {
    // Get minimum load from current test
    return 100.0;
}

float getMeanFrequency() {
    // Get mean frequency from current test
    return 10.0;
}

uint32_t getTotalAEHits() {
    // Get total AE hits from current test
    return 1234;
}