/*
 * Program 23: Acoustic Emission Monitor - ESP32 Wireless Gateway
 * 
 * This program implements a wireless gateway for the acoustic emission monitoring system,
 * providing IoT connectivity, cloud data transmission, and distributed sensor network
 * capabilities for structural health monitoring applications.
 * 
 * Features:
 * - High-speed data transmission to cloud platforms
 * - Real-time streaming of AE events
 * - Distributed sensor network coordination
 * - Advanced analytics and machine learning integration
 * - Remote monitoring and control capabilities
 * - GPS-synchronized data collection
 * 
 * Author: Arduino Zero to Hero v2.0
 * Created: 2024
 * 
 * Hardware Requirements:
 * - ESP32 DevKit V1
 * - WiFi connection
 * - MQTT broker access
 * - Cloud storage account
 * - GPS module (for time sync)
 * 
 * Libraries Required:
 * - WiFi.h
 * - WiFiClientSecure.h
 * - ArduinoJson.h
 * - PubSubClient.h
 * - HTTPClient.h
 * - AsyncTCP.h
 * - ESPAsyncWebServer.h
 * - SPIFFS.h
 * - TinyGPS++.h
 * - mbedtls/md.h
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <HTTPClient.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include <TinyGPS++.h>
#include <mbedtls/md.h>

// Network Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Configuration
const char* mqtt_server = "your-mqtt-broker.com";
const int mqtt_port = 8883;
const char* mqtt_user = "ae_monitor";
const char* mqtt_password = "your_mqtt_password";
const char* mqtt_client_id = "ae_monitor_node_01";

// Cloud Configuration
const char* cloud_endpoint = "https://api.yourcloud.com";
const char* api_key = "your_api_key";
const char* device_id = "ae_monitor_001";

// Pin Definitions
#define ARDUINO_SERIAL_TX 17
#define ARDUINO_SERIAL_RX 16
#define STATUS_LED_WIFI 2
#define STATUS_LED_CLOUD 4
#define STATUS_LED_DATA 5
#define STATUS_LED_ERROR 18
#define GPS_SERIAL_TX 21
#define GPS_SERIAL_RX 22
#define EMERGENCY_STOP 19
#define SYSTEM_RESET 23

// Communication Parameters
#define ARDUINO_BAUD_RATE 921600
#define GPS_BAUD_RATE 38400
#define BUFFER_SIZE 8192
#define MAX_RETRY_COUNT 3
#define DATA_TIMEOUT 5000

// Data Structures
struct AEEvent {
    uint32_t timestamp;
    uint8_t channel;
    float amplitude;
    float energy;
    float duration;
    float rise_time;
    float frequency_peak;
    float frequency_centroid;
    uint32_t counts;
    float x_position;
    float y_position;
    float z_position;
    uint8_t classification;
    float confidence;
    String event_id;
};

struct SystemStatus {
    bool wifi_connected;
    bool mqtt_connected;
    bool cloud_connected;
    bool gps_synchronized;
    uint32_t events_processed;
    uint32_t events_transmitted;
    uint32_t transmission_errors;
    float battery_voltage;
    float signal_strength;
    uint32_t uptime;
    String firmware_version;
};

struct NetworkConfig {
    String ssid;
    String password;
    String mqtt_server;
    int mqtt_port;
    String mqtt_user;
    String mqtt_password;
    String cloud_endpoint;
    String api_key;
    String device_id;
    bool ssl_enabled;
    int transmission_interval;
    int buffer_size;
};

// Global Variables
WiFiClient wifi_client;
WiFiClientSecure secure_client;
PubSubClient mqtt_client(wifi_client);
AsyncWebServer web_server(80);
TinyGPSPlus gps;

HardwareSerial arduino_serial(2);
HardwareSerial gps_serial(1);

SystemStatus system_status;
NetworkConfig network_config;

// Data Buffers
QueueHandle_t event_queue;
QueueHandle_t transmission_queue;
TaskHandle_t data_processing_task;
TaskHandle_t cloud_transmission_task;
TaskHandle_t mqtt_handler_task;

// Timing Variables
uint32_t last_heartbeat = 0;
uint32_t last_status_update = 0;
uint32_t last_gps_sync = 0;
uint32_t connection_check_interval = 30000; // 30 seconds
uint32_t heartbeat_interval = 60000; // 1 minute
uint32_t status_update_interval = 5000; // 5 seconds

// Statistics
uint32_t total_events_received = 0;
uint32_t total_events_transmitted = 0;
uint32_t total_transmission_errors = 0;
uint32_t total_reconnections = 0;

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== ESP32 Acoustic Emission Wireless Gateway ===");
    Serial.println("Initializing system...");
    
    // Initialize pin modes
    pinMode(STATUS_LED_WIFI, OUTPUT);
    pinMode(STATUS_LED_CLOUD, OUTPUT);
    pinMode(STATUS_LED_DATA, OUTPUT);
    pinMode(STATUS_LED_ERROR, OUTPUT);
    pinMode(EMERGENCY_STOP, INPUT_PULLUP);
    pinMode(SYSTEM_RESET, INPUT_PULLUP);
    
    // Initialize status LEDs
    digitalWrite(STATUS_LED_WIFI, LOW);
    digitalWrite(STATUS_LED_CLOUD, LOW);
    digitalWrite(STATUS_LED_DATA, LOW);
    digitalWrite(STATUS_LED_ERROR, LOW);
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("SPIFFS initialization failed!");
        return;
    }
    
    // Load configuration
    loadConfiguration();
    
    // Initialize serial communications
    arduino_serial.begin(ARDUINO_BAUD_RATE, SERIAL_8N1, ARDUINO_SERIAL_RX, ARDUINO_SERIAL_TX);
    gps_serial.begin(GPS_BAUD_RATE, SERIAL_8N1, GPS_SERIAL_RX, GPS_SERIAL_TX);
    
    // Initialize queues
    event_queue = xQueueCreate(100, sizeof(AEEvent));
    transmission_queue = xQueueCreate(50, sizeof(AEEvent));
    
    // Initialize network connections
    initializeWiFi();
    initializeMQTT();
    initializeWebServer();
    
    // Initialize system status
    system_status.wifi_connected = false;
    system_status.mqtt_connected = false;
    system_status.cloud_connected = false;
    system_status.gps_synchronized = false;
    system_status.events_processed = 0;
    system_status.events_transmitted = 0;
    system_status.transmission_errors = 0;
    system_status.firmware_version = "v2.0.0";
    
    // Start background tasks
    xTaskCreatePinnedToCore(
        dataProcessingTask,
        "DataProcessing",
        8192,
        NULL,
        2,
        &data_processing_task,
        0
    );
    
    xTaskCreatePinnedToCore(
        cloudTransmissionTask,
        "CloudTransmission",
        8192,
        NULL,
        1,
        &cloud_transmission_task,
        1
    );
    
    xTaskCreatePinnedToCore(
        mqttHandlerTask,
        "MQTTHandler",
        4096,
        NULL,
        1,
        &mqtt_handler_task,
        1
    );
    
    Serial.println("System initialization complete!");
    Serial.println("Ready for acoustic emission monitoring...");
}

void loop() {
    uint32_t current_time = millis();
    
    // Check emergency stop
    if (digitalRead(EMERGENCY_STOP) == LOW) {
        handleEmergencyStop();
        return;
    }
    
    // Check system reset
    if (digitalRead(SYSTEM_RESET) == LOW) {
        ESP.restart();
    }
    
    // Update GPS
    updateGPS();
    
    // Connection maintenance
    if (current_time - last_heartbeat > connection_check_interval) {
        maintainConnections();
        last_heartbeat = current_time;
    }
    
    // Send heartbeat
    if (current_time - last_heartbeat > heartbeat_interval) {
        sendHeartbeat();
        last_heartbeat = current_time;
    }
    
    // Update status
    if (current_time - last_status_update > status_update_interval) {
        updateSystemStatus();
        last_status_update = current_time;
    }
    
    // Handle MQTT
    if (mqtt_client.connected()) {
        mqtt_client.loop();
    }
    
    delay(100);
}

void initializeWiFi() {
    Serial.print("Connecting to WiFi");
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("WiFi connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        system_status.wifi_connected = true;
        digitalWrite(STATUS_LED_WIFI, HIGH);
    } else {
        Serial.println();
        Serial.println("WiFi connection failed!");
        system_status.wifi_connected = false;
        digitalWrite(STATUS_LED_ERROR, HIGH);
    }
}

void initializeMQTT() {
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    
    connectMQTT();
}

void connectMQTT() {
    while (!mqtt_client.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        if (mqtt_client.connect(mqtt_client_id, mqtt_user, mqtt_password)) {
            Serial.println("connected");
            system_status.mqtt_connected = true;
            
            // Subscribe to control topics
            mqtt_client.subscribe("ae_monitor/control/+");
            mqtt_client.subscribe("ae_monitor/config/+");
            mqtt_client.subscribe("ae_monitor/calibration/+");
            
            // Publish online status
            publishStatus();
            
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqtt_client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.print("MQTT message received [");
    Serial.print(topic);
    Serial.print("]: ");
    Serial.println(message);
    
    // Parse and handle control commands
    handleMQTTCommand(String(topic), message);
}

void handleMQTTCommand(String topic, String message) {
    StaticJsonDocument<512> doc;
    deserializeJson(doc, message);
    
    if (topic.indexOf("control") > 0) {
        String command = doc["command"];
        
        if (command == "start_acquisition") {
            sendCommandToArduino("{\"command\":\"start_acquisition\"}");
        } else if (command == "stop_acquisition") {
            sendCommandToArduino("{\"command\":\"stop_acquisition\"}");
        } else if (command == "calibrate_sensors") {
            sendCommandToArduino("{\"command\":\"calibrate_sensors\"}");
        } else if (command == "reset_system") {
            sendCommandToArduino("{\"command\":\"reset_system\"}");
        } else if (command == "get_status") {
            publishStatus();
        }
    } else if (topic.indexOf("config") > 0) {
        // Handle configuration updates
        updateConfiguration(doc);
    }
}

void sendCommandToArduino(String command) {
    arduino_serial.println(command);
    Serial.println("Command sent to Arduino: " + command);
}

void dataProcessingTask(void* parameter) {
    AEEvent event;
    
    while (true) {
        if (arduino_serial.available()) {
            String data = arduino_serial.readStringUntil('\n');
            
            if (parseAEEvent(data, event)) {
                // Add to processing queue
                if (xQueueSend(event_queue, &event, 0) == pdTRUE) {
                    total_events_received++;
                    digitalWrite(STATUS_LED_DATA, !digitalRead(STATUS_LED_DATA));
                }
            }
        }
        
        // Process events from queue
        if (xQueueReceive(event_queue, &event, 0) == pdTRUE) {
            processAEEvent(event);
            system_status.events_processed++;
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

bool parseAEEvent(String data, AEEvent& event) {
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, data);
    
    if (error) {
        Serial.print("JSON parsing failed: ");
        Serial.println(error.c_str());
        return false;
    }
    
    if (doc["type"] == "ae_event") {
        event.timestamp = doc["timestamp"];
        event.channel = doc["channel"];
        event.amplitude = doc["amplitude"];
        event.energy = doc["energy"];
        event.duration = doc["duration"];
        event.rise_time = doc["rise_time"];
        event.frequency_peak = doc["frequency_peak"];
        event.frequency_centroid = doc["frequency_centroid"];
        event.counts = doc["counts"];
        event.x_position = doc["x_position"];
        event.y_position = doc["y_position"];
        event.z_position = doc["z_position"];
        event.classification = doc["classification"];
        event.confidence = doc["confidence"];
        event.event_id = doc["event_id"].as<String>();
        
        return true;
    }
    
    return false;
}

void processAEEvent(AEEvent event) {
    // Add GPS timestamp if available
    if (gps.time.isValid()) {
        // Convert GPS time to Unix timestamp
        event.timestamp = getGPSTimestamp();
    }
    
    // Add to transmission queue
    if (xQueueSend(transmission_queue, &event, 0) == pdTRUE) {
        // Event queued for transmission
    } else {
        Serial.println("Transmission queue full!");
    }
    
    // Real-time MQTT transmission for critical events
    if (event.amplitude > 80.0 || event.classification == 1) { // High amplitude or crack
        publishRealTimeEvent(event);
    }
}

void cloudTransmissionTask(void* parameter) {
    AEEvent events[10];
    int event_count = 0;
    uint32_t last_transmission = 0;
    
    while (true) {
        // Collect events for batch transmission
        while (event_count < 10 && xQueueReceive(transmission_queue, &events[event_count], 0) == pdTRUE) {
            event_count++;
        }
        
        // Transmit batch if we have events or enough time has passed
        if (event_count > 0 && (event_count >= 10 || millis() - last_transmission > 10000)) {
            if (system_status.wifi_connected) {
                transmitEventsToCloud(events, event_count);
                last_transmission = millis();
            }
            event_count = 0;
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void transmitEventsToCloud(AEEvent* events, int count) {
    HTTPClient http;
    http.begin(cloud_endpoint);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    http.addHeader("X-Device-ID", device_id);
    
    StaticJsonDocument<4096> doc;
    JsonArray event_array = doc.createNestedArray("events");
    
    for (int i = 0; i < count; i++) {
        JsonObject event_obj = event_array.createNestedObject();
        event_obj["timestamp"] = events[i].timestamp;
        event_obj["channel"] = events[i].channel;
        event_obj["amplitude"] = events[i].amplitude;
        event_obj["energy"] = events[i].energy;
        event_obj["duration"] = events[i].duration;
        event_obj["rise_time"] = events[i].rise_time;
        event_obj["frequency_peak"] = events[i].frequency_peak;
        event_obj["frequency_centroid"] = events[i].frequency_centroid;
        event_obj["counts"] = events[i].counts;
        event_obj["x_position"] = events[i].x_position;
        event_obj["y_position"] = events[i].y_position;
        event_obj["z_position"] = events[i].z_position;
        event_obj["classification"] = events[i].classification;
        event_obj["confidence"] = events[i].confidence;
        event_obj["event_id"] = events[i].event_id;
    }
    
    doc["device_id"] = device_id;
    doc["batch_timestamp"] = millis();
    doc["event_count"] = count;
    
    String json_string;
    serializeJson(doc, json_string);
    
    int response_code = http.POST(json_string);
    
    if (response_code == 200) {
        system_status.events_transmitted += count;
        total_events_transmitted += count;
        digitalWrite(STATUS_LED_CLOUD, HIGH);
        Serial.printf("Successfully transmitted %d events to cloud\n", count);
    } else {
        system_status.transmission_errors++;
        total_transmission_errors++;
        digitalWrite(STATUS_LED_ERROR, HIGH);
        Serial.printf("Cloud transmission failed: %d\n", response_code);
    }
    
    http.end();
}

void publishRealTimeEvent(AEEvent event) {
    if (!mqtt_client.connected()) {
        return;
    }
    
    StaticJsonDocument<512> doc;
    doc["timestamp"] = event.timestamp;
    doc["channel"] = event.channel;
    doc["amplitude"] = event.amplitude;
    doc["energy"] = event.energy;
    doc["duration"] = event.duration;
    doc["x_position"] = event.x_position;
    doc["y_position"] = event.y_position;
    doc["z_position"] = event.z_position;
    doc["classification"] = event.classification;
    doc["confidence"] = event.confidence;
    doc["event_id"] = event.event_id;
    doc["priority"] = "high";
    
    String json_string;
    serializeJson(doc, json_string);
    
    String topic = "ae_monitor/events/realtime/" + String(device_id);
    mqtt_client.publish(topic.c_str(), json_string.c_str());
}

void mqttHandlerTask(void* parameter) {
    while (true) {
        if (system_status.mqtt_connected) {
            mqtt_client.loop();
        } else {
            connectMQTT();
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void updateGPS() {
    while (gps_serial.available() > 0) {
        if (gps.encode(gps_serial.read())) {
            if (gps.time.isValid() && gps.date.isValid()) {
                system_status.gps_synchronized = true;
                last_gps_sync = millis();
            }
        }
    }
    
    // Check if GPS sync is stale
    if (millis() - last_gps_sync > 300000) { // 5 minutes
        system_status.gps_synchronized = false;
    }
}

uint32_t getGPSTimestamp() {
    if (!gps.time.isValid() || !gps.date.isValid()) {
        return millis();
    }
    
    // Convert GPS date/time to Unix timestamp
    struct tm timeinfo;
    timeinfo.tm_year = gps.date.year() - 1900;
    timeinfo.tm_mon = gps.date.month() - 1;
    timeinfo.tm_mday = gps.date.day();
    timeinfo.tm_hour = gps.time.hour();
    timeinfo.tm_min = gps.time.minute();
    timeinfo.tm_sec = gps.time.second();
    
    return mktime(&timeinfo);
}

void initializeWebServer() {
    // Serve static files
    web_server.serveStatic("/", SPIFFS, "/");
    
    // API endpoints
    web_server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest* request) {
        AsyncResponseStream* response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<512> doc;
        doc["wifi_connected"] = system_status.wifi_connected;
        doc["mqtt_connected"] = system_status.mqtt_connected;
        doc["cloud_connected"] = system_status.cloud_connected;
        doc["gps_synchronized"] = system_status.gps_synchronized;
        doc["events_processed"] = system_status.events_processed;
        doc["events_transmitted"] = system_status.events_transmitted;
        doc["transmission_errors"] = system_status.transmission_errors;
        doc["uptime"] = millis() / 1000;
        doc["firmware_version"] = system_status.firmware_version;
        doc["free_heap"] = ESP.getFreeHeap();
        doc["signal_strength"] = WiFi.RSSI();
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/events", HTTP_GET, [](AsyncWebServerRequest* request) {
        // Return recent events (implementation depends on storage)
        request->send(200, "application/json", "{\"events\":[]}");
    });
    
    web_server.on("/api/control", HTTP_POST, [](AsyncWebServerRequest* request) {
        // Handle control commands
        request->send(200, "application/json", "{\"status\":\"ok\"}");
    });
    
    web_server.begin();
    Serial.println("Web server started");
}

void maintainConnections() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        system_status.wifi_connected = false;
        digitalWrite(STATUS_LED_WIFI, LOW);
        Serial.println("WiFi disconnected, attempting reconnection...");
        WiFi.reconnect();
        total_reconnections++;
    } else {
        system_status.wifi_connected = true;
        digitalWrite(STATUS_LED_WIFI, HIGH);
    }
    
    // Check MQTT connection
    if (!mqtt_client.connected()) {
        system_status.mqtt_connected = false;
        connectMQTT();
    }
    
    // Test cloud connectivity
    testCloudConnection();
}

void testCloudConnection() {
    HTTPClient http;
    http.begin(cloud_endpoint + "/health");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    
    int response_code = http.GET();
    
    if (response_code == 200) {
        system_status.cloud_connected = true;
        digitalWrite(STATUS_LED_CLOUD, HIGH);
        digitalWrite(STATUS_LED_ERROR, LOW);
    } else {
        system_status.cloud_connected = false;
        digitalWrite(STATUS_LED_CLOUD, LOW);
        digitalWrite(STATUS_LED_ERROR, HIGH);
    }
    
    http.end();
}

void updateSystemStatus() {
    system_status.uptime = millis() / 1000;
    system_status.battery_voltage = analogRead(A0) * 3.3 / 4095.0 * 2.0; // Voltage divider
    system_status.signal_strength = WiFi.RSSI();
}

void sendHeartbeat() {
    if (!mqtt_client.connected()) {
        return;
    }
    
    StaticJsonDocument<256> doc;
    doc["device_id"] = device_id;
    doc["timestamp"] = millis();
    doc["uptime"] = system_status.uptime;
    doc["events_processed"] = system_status.events_processed;
    doc["events_transmitted"] = system_status.events_transmitted;
    doc["signal_strength"] = system_status.signal_strength;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["firmware_version"] = system_status.firmware_version;
    
    String json_string;
    serializeJson(doc, json_string);
    
    String topic = "ae_monitor/heartbeat/" + String(device_id);
    mqtt_client.publish(topic.c_str(), json_string.c_str());
}

void publishStatus() {
    if (!mqtt_client.connected()) {
        return;
    }
    
    StaticJsonDocument<512> doc;
    doc["device_id"] = device_id;
    doc["timestamp"] = millis();
    doc["wifi_connected"] = system_status.wifi_connected;
    doc["mqtt_connected"] = system_status.mqtt_connected;
    doc["cloud_connected"] = system_status.cloud_connected;
    doc["gps_synchronized"] = system_status.gps_synchronized;
    doc["events_processed"] = system_status.events_processed;
    doc["events_transmitted"] = system_status.events_transmitted;
    doc["transmission_errors"] = system_status.transmission_errors;
    doc["uptime"] = system_status.uptime;
    doc["firmware_version"] = system_status.firmware_version;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["signal_strength"] = system_status.signal_strength;
    doc["battery_voltage"] = system_status.battery_voltage;
    
    String json_string;
    serializeJson(doc, json_string);
    
    String topic = "ae_monitor/status/" + String(device_id);
    mqtt_client.publish(topic.c_str(), json_string.c_str());
}

void handleEmergencyStop() {
    Serial.println("EMERGENCY STOP ACTIVATED!");
    
    // Stop all data processing
    vTaskSuspend(data_processing_task);
    vTaskSuspend(cloud_transmission_task);
    
    // Send emergency stop command to Arduino
    sendCommandToArduino("{\"command\":\"emergency_stop\"}");
    
    // Publish emergency alert
    if (mqtt_client.connected()) {
        StaticJsonDocument<256> doc;
        doc["device_id"] = device_id;
        doc["timestamp"] = millis();
        doc["alert_type"] = "emergency_stop";
        doc["description"] = "Emergency stop button activated";
        
        String json_string;
        serializeJson(doc, json_string);
        
        String topic = "ae_monitor/alerts/" + String(device_id);
        mqtt_client.publish(topic.c_str(), json_string.c_str());
    }
    
    // Flash error LED
    while (digitalRead(EMERGENCY_STOP) == LOW) {
        digitalWrite(STATUS_LED_ERROR, HIGH);
        delay(250);
        digitalWrite(STATUS_LED_ERROR, LOW);
        delay(250);
    }
    
    // Resume normal operation
    vTaskResume(data_processing_task);
    vTaskResume(cloud_transmission_task);
    
    Serial.println("Emergency stop cleared - resuming normal operation");
}

void loadConfiguration() {
    // Load configuration from SPIFFS
    if (SPIFFS.exists("/config.json")) {
        File config_file = SPIFFS.open("/config.json", "r");
        if (config_file) {
            StaticJsonDocument<1024> doc;
            deserializeJson(doc, config_file);
            
            // Load network configuration
            // Implementation depends on specific requirements
            
            config_file.close();
        }
    }
}

void updateConfiguration(JsonDocument& config) {
    // Update configuration and save to SPIFFS
    File config_file = SPIFFS.open("/config.json", "w");
    if (config_file) {
        serializeJson(config, config_file);
        config_file.close();
        
        Serial.println("Configuration updated");
    }
}

// Performance monitoring functions
void printPerformanceStats() {
    Serial.println("\n=== Performance Statistics ===");
    Serial.printf("Total Events Received: %u\n", total_events_received);
    Serial.printf("Total Events Transmitted: %u\n", total_events_transmitted);
    Serial.printf("Total Transmission Errors: %u\n", total_transmission_errors);
    Serial.printf("Total Reconnections: %u\n", total_reconnections);
    Serial.printf("Uptime: %u seconds\n", system_status.uptime);
    Serial.printf("Free Heap: %u bytes\n", ESP.getFreeHeap());
    Serial.printf("Signal Strength: %d dBm\n", (int)system_status.signal_strength);
    Serial.printf("Battery Voltage: %.2f V\n", system_status.battery_voltage);
    Serial.println("===============================\n");
}

// OTA Update functionality
void handleOTAUpdate() {
    // Implementation for Over-The-Air updates
    // This would typically involve downloading firmware from cloud
    // and updating the ESP32 flash memory
}

// Data integrity checking
bool verifyDataIntegrity(AEEvent& event) {
    // Check for reasonable values
    if (event.amplitude < 0 || event.amplitude > 100) return false;
    if (event.energy < 0 || event.energy > 1000) return false;
    if (event.duration < 0 || event.duration > 10000) return false;
    if (event.frequency_peak < 0 || event.frequency_peak > 1000000) return false;
    
    return true;
}

// Watchdog timer management
void resetWatchdog() {
    esp_task_wdt_reset();
}

void setup() {
    // Previous setup code...
    
    // Initialize watchdog timer
    esp_task_wdt_init(60, true); // 60 second timeout
    esp_task_wdt_add(NULL);
    
    // Performance monitoring timer
    xTaskCreate(performanceMonitorTask, "Performance", 2048, NULL, 1, NULL);
}

void performanceMonitorTask(void* parameter) {
    while (true) {
        printPerformanceStats();
        vTaskDelay(pdMS_TO_TICKS(60000)); // Print every minute
    }
}