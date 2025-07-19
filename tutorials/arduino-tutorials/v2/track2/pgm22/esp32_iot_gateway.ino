/*
 * ESP32 IoT Gateway for Environmental Test Chamber
 * 
 * Provides cloud connectivity, remote monitoring, test profile management,
 * and advanced analytics for environmental stress testing
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
#include <AsyncWebSocket.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <time.h>

// Pin definitions
#define LED_WIFI 2
#define LED_MQTT 4
#define LED_STATUS 15
#define SD_CS 5
#define ARDUINO_RX 16
#define ARDUINO_TX 17
#define RELAY_CONTROL 18
#define SPARE_OUTPUT 19

// Network credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT settings
const char* mqtt_server = "mqtt.environmental-test.com";
const int mqtt_port = 8883;
const char* mqtt_user = "env_chamber";
const char* mqtt_password = "secure_env_password";
const char* mqtt_client_id = "ESP32_EnvChamber_001";

// Cloud API settings
const char* api_endpoint = "https://api.environmental-test.com/v1";
const char* api_key = "YOUR_API_KEY";

// NTP settings
const char* ntp_server = "pool.ntp.org";
const long gmt_offset_sec = 0;
const int daylight_offset_sec = 0;

// Topics
const char* topic_data = "env/data";
const char* topic_status = "env/status";
const char* topic_command = "env/command";
const char* topic_alert = "env/alert";
const char* topic_profile = "env/profile";

// Global objects
WiFiClientSecure wifi_client;
PubSubClient mqtt_client(wifi_client);
AsyncWebServer web_server(80);
AsyncWebSocket websocket("/ws");
Preferences preferences;
HardwareSerial ArduinoSerial(2);

// Environmental data structure
struct EnvironmentalData {
    float temperature;
    float humidity;
    float uv_irradiance;
    float pressure;
    float dew_point;
    float water_level;
    bool test_running;
    uint8_t current_step;
    uint16_t current_cycle;
    uint32_t timestamp;
};

// Test profile structure
struct TestProfile {
    String name;
    String description;
    String standard;
    uint8_t num_steps;
    struct {
        float temperature;
        float humidity;
        float uv_irradiance;
        uint32_t duration;
        float ramp_rate;
    } steps[20];
    bool cycle_repeat;
    uint16_t cycle_count;
    String created_by;
    uint32_t created_time;
};

// Alert structure
struct Alert {
    String type;
    String message;
    uint8_t severity;  // 1=Info, 2=Warning, 3=Critical
    uint32_t timestamp;
    bool acknowledged;
};

// System status
bool wifi_connected = false;
bool mqtt_connected = false;
bool arduino_connected = false;
bool test_active = false;
String current_specimen_id = "";
uint32_t data_points_collected = 0;
uint32_t alerts_generated = 0;

// Data buffers
const int DATA_BUFFER_SIZE = 500;
const int ALERT_BUFFER_SIZE = 100;
EnvironmentalData data_buffer[DATA_BUFFER_SIZE];
Alert alert_buffer[ALERT_BUFFER_SIZE];
int data_write_index = 0;
int alert_write_index = 0;

// Predefined test profiles
const int NUM_PREDEFINED_PROFILES = 5;
TestProfile predefined_profiles[NUM_PREDEFINED_PROFILES];

void setup() {
    Serial.begin(115200);
    ArduinoSerial.begin(115200, SERIAL_8N1, ARDUINO_RX, ARDUINO_TX);
    
    Serial.println(F("ESP32 Environmental Test Chamber Gateway v2.0"));
    
    // Initialize pins
    pinMode(LED_WIFI, OUTPUT);
    pinMode(LED_MQTT, OUTPUT);
    pinMode(LED_STATUS, OUTPUT);
    pinMode(RELAY_CONTROL, OUTPUT);
    pinMode(SPARE_OUTPUT, OUTPUT);
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println(F("SPIFFS initialization failed"));
    }
    
    // Initialize SD card
    if (!SD.begin(SD_CS)) {
        Serial.println(F("SD card initialization failed"));
    }
    
    // Load preferences
    preferences.begin("env_chamber", false);
    loadConfiguration();
    
    // Initialize predefined profiles
    initializePredefinedProfiles();
    
    // Connect to WiFi
    connectWiFi();
    
    // Initialize time
    configTime(gmt_offset_sec, daylight_offset_sec, ntp_server);
    
    // Initialize MQTT
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    mqtt_client.setBufferSize(4096);
    
    // Initialize web server
    setupWebServer();
    
    // Initialize WebSocket
    websocket.onEvent(onWebSocketEvent);
    web_server.addHandler(&websocket);
    
    // Initialize OTA updates
    setupOTA();
    
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
    
    // Process data buffer
    processDataBuffer();
    
    // Process alerts
    processAlerts();
    
    // Update WebSocket clients
    updateWebSocketClients();
    
    // Handle OTA updates
    ArduinoOTA.handle();
    
    // Periodic tasks
    static uint32_t last_status_update = 0;
    if (millis() - last_status_update > 30000) { // Every 30 seconds
        sendStatusUpdate();
        last_status_update = millis();
    }
    
    // Check system health
    static uint32_t last_health_check = 0;
    if (millis() - last_health_check > 60000) { // Every minute
        performHealthCheck();
        last_health_check = millis();
    }
    
    // Update status LED
    digitalWrite(LED_STATUS, millis() % 2000 < 100);
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
        if (MDNS.begin("env-chamber")) {
            Serial.println(F("mDNS responder started"));
        }
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
            mqtt_client.subscribe(topic_profile);
            
            // Send connection message
            sendConnectionMessage();
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
    
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        Serial.print(F("JSON parse error: "));
        Serial.println(error.c_str());
        return;
    }
    
    if (String(topic) == topic_command) {
        handleCommand(doc);
    } else if (String(topic) == topic_profile) {
        handleProfileUpdate(doc);
    }
}

void handleCommand(JsonDocument& doc) {
    String command = doc["command"];
    
    if (command == "start_test") {
        String specimen_id = doc["specimen_id"];
        String profile_name = doc["profile_name"];
        
        // Forward to Arduino
        StaticJsonDocument<256> cmd_doc;
        cmd_doc["type"] = "command";
        cmd_doc["command"] = "start";
        cmd_doc["specimen_id"] = specimen_id;
        cmd_doc["profile_name"] = profile_name;
        
        serializeJson(cmd_doc, ArduinoSerial);
        ArduinoSerial.println();
        
        current_specimen_id = specimen_id;
        test_active = true;
        
    } else if (command == "stop_test") {
        StaticJsonDocument<256> cmd_doc;
        cmd_doc["type"] = "command";
        cmd_doc["command"] = "stop";
        
        serializeJson(cmd_doc, ArduinoSerial);
        ArduinoSerial.println();
        
        test_active = false;
        
    } else if (command == "load_profile") {
        String profile_name = doc["profile_name"];
        loadAndSendProfile(profile_name);
        
    } else if (command == "emergency_stop") {
        // Immediate emergency stop
        digitalWrite(RELAY_CONTROL, HIGH); // Activate emergency relay
        
        StaticJsonDocument<256> cmd_doc;
        cmd_doc["type"] = "emergency_stop";
        
        serializeJson(cmd_doc, ArduinoSerial);
        ArduinoSerial.println();
        
        generateAlert("Emergency stop activated", 3);
        
    } else if (command == "get_data") {
        String specimen_id = doc["specimen_id"];
        String start_time = doc["start_time"];
        String end_time = doc["end_time"];
        
        sendHistoricalData(specimen_id, start_time, end_time);
        
    } else if (command == "update_config") {
        updateConfiguration(doc);
        
    } else if (command == "calibrate") {
        String sensor_type = doc["sensor_type"];
        performRemoteCalibration(sensor_type);
    }
}

void handleProfileUpdate(JsonDocument& doc) {
    String action = doc["action"];
    
    if (action == "upload") {
        TestProfile profile;
        profile.name = doc["name"].as<String>();
        profile.description = doc["description"].as<String>();
        profile.standard = doc["standard"].as<String>();
        profile.num_steps = doc["num_steps"];
        profile.cycle_repeat = doc["cycle_repeat"];
        profile.cycle_count = doc["cycle_count"];
        profile.created_by = doc["created_by"].as<String>();
        profile.created_time = doc["created_time"];
        
        // Extract steps
        for (int i = 0; i < profile.num_steps; i++) {
            profile.steps[i].temperature = doc["steps"][i]["temperature"];
            profile.steps[i].humidity = doc["steps"][i]["humidity"];
            profile.steps[i].uv_irradiance = doc["steps"][i]["uv_irradiance"];
            profile.steps[i].duration = doc["steps"][i]["duration"];
            profile.steps[i].ramp_rate = doc["steps"][i]["ramp_rate"];
        }
        
        // Save profile to SPIFFS
        saveProfile(profile);
        
        // Send to Arduino
        forwardProfileToArduino(profile);
        
    } else if (action == "delete") {
        String profile_name = doc["name"];
        deleteProfile(profile_name);
        
    } else if (action == "list") {
        sendProfileList();
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
    
    if (type == "environmental_data") {
        // Store environmental data
        EnvironmentalData data;
        data.temperature = doc["temperature"];
        data.humidity = doc["humidity"];
        data.uv_irradiance = doc["uv_irradiance"];
        data.pressure = doc["pressure"];
        data.dew_point = doc["dew_point"];
        data.water_level = doc["water_level"];
        data.test_running = doc["test_running"];
        data.current_step = doc["current_step"];
        data.current_cycle = doc["current_cycle"];
        data.timestamp = doc["timestamp"];
        
        addDataToBuffer(data);
        arduino_connected = true;
        
    } else if (type == "test_start") {
        test_active = true;
        current_specimen_id = doc["specimen_id"].as<String>();
        
        // Create cloud test session
        createCloudTestSession(doc);
        
    } else if (type == "test_end") {
        test_active = false;
        
        // Close cloud test session
        closeCloudTestSession(doc);
        
        // Generate test report
        generateTestReport(doc);
        
    } else if (type == "alert") {
        String alert_type = doc["alert_type"];
        String message = doc["message"];
        uint8_t severity = doc["severity"];
        
        generateAlert(alert_type + ": " + message, severity);
        
    } else if (type == "status") {
        // Update system status
        updateSystemStatus(doc);
    }
}

void addDataToBuffer(EnvironmentalData& data) {
    data_buffer[data_write_index] = data;
    data_write_index = (data_write_index + 1) % DATA_BUFFER_SIZE;
    data_points_collected++;
    
    // Store to SD card
    storeDataToSD(data);
}

void processDataBuffer() {
    static uint32_t last_send = 0;
    
    // Send data every 10 seconds
    if (millis() - last_send > 10000 && mqtt_connected) {
        sendBufferedData();
        last_send = millis();
    }
}

void sendBufferedData() {
    // Prepare batch data message
    StaticJsonDocument<2048> doc;
    JsonArray data_array = doc.createNestedArray("data");
    
    // Send last 10 data points
    int start_index = (data_write_index - 10 + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
    
    for (int i = 0; i < 10; i++) {
        int index = (start_index + i) % DATA_BUFFER_SIZE;
        EnvironmentalData& data = data_buffer[index];
        
        JsonObject data_obj = data_array.createNestedObject();
        data_obj["temperature"] = data.temperature;
        data_obj["humidity"] = data.humidity;
        data_obj["uv_irradiance"] = data.uv_irradiance;
        data_obj["pressure"] = data.pressure;
        data_obj["dew_point"] = data.dew_point;
        data_obj["water_level"] = data.water_level;
        data_obj["test_running"] = data.test_running;
        data_obj["current_step"] = data.current_step;
        data_obj["current_cycle"] = data.current_cycle;
        data_obj["timestamp"] = data.timestamp;
    }
    
    doc["specimen_id"] = current_specimen_id;
    doc["batch_size"] = 10;
    doc["total_points"] = data_points_collected;
    
    char buffer[2048];
    serializeJson(doc, buffer);
    
    mqtt_client.publish(topic_data, buffer);
}

void storeDataToSD(EnvironmentalData& data) {
    String filename = "/env_data/" + current_specimen_id + ".csv";
    
    File file = SD.open(filename, FILE_APPEND);
    if (file) {
        file.print(data.timestamp);
        file.print(",");
        file.print(data.temperature, 2);
        file.print(",");
        file.print(data.humidity, 2);
        file.print(",");
        file.print(data.uv_irradiance, 2);
        file.print(",");
        file.print(data.pressure, 2);
        file.print(",");
        file.print(data.dew_point, 2);
        file.print(",");
        file.print(data.water_level, 1);
        file.print(",");
        file.print(data.test_running ? 1 : 0);
        file.print(",");
        file.print(data.current_step);
        file.print(",");
        file.println(data.current_cycle);
        file.close();
    }
}

void generateAlert(String message, uint8_t severity) {
    Alert alert;
    alert.type = "SYSTEM";
    alert.message = message;
    alert.severity = severity;
    alert.timestamp = millis();
    alert.acknowledged = false;
    
    // Add to alert buffer
    alert_buffer[alert_write_index] = alert;
    alert_write_index = (alert_write_index + 1) % ALERT_BUFFER_SIZE;
    alerts_generated++;
    
    // Send alert immediately
    sendAlert(alert);
    
    Serial.print(F("Alert generated: "));
    Serial.println(message);
}

void sendAlert(Alert& alert) {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "alert";
    doc["alert_type"] = alert.type;
    doc["message"] = alert.message;
    doc["severity"] = alert.severity;
    doc["timestamp"] = alert.timestamp;
    doc["specimen_id"] = current_specimen_id;
    
    char buffer[256];
    serializeJson(doc, buffer);
    
    mqtt_client.publish(topic_alert, buffer);
}

void processAlerts() {
    // Process and escalate unacknowledged alerts
    static uint32_t last_alert_check = 0;
    
    if (millis() - last_alert_check > 60000) { // Every minute
        checkForUnacknowledgedAlerts();
        last_alert_check = millis();
    }
}

void checkForUnacknowledgedAlerts() {
    uint32_t current_time = millis();
    
    for (int i = 0; i < ALERT_BUFFER_SIZE; i++) {
        Alert& alert = alert_buffer[i];
        
        if (!alert.acknowledged && alert.severity >= 2) {
            // Escalate warnings and critical alerts after 5 minutes
            if (current_time - alert.timestamp > 300000) {
                escalateAlert(alert);
            }
        }
    }
}

void escalateAlert(Alert& alert) {
    // Escalate alert by increasing severity and resending
    if (alert.severity < 3) {
        alert.severity++;
        alert.message = "ESCALATED: " + alert.message;
        sendAlert(alert);
    }
}

void initializePredefinedProfiles() {
    // HALT Profile
    predefined_profiles[0].name = "HALT_Standard";
    predefined_profiles[0].description = "Highly Accelerated Life Test";
    predefined_profiles[0].standard = "MIL-STD-810G";
    predefined_profiles[0].num_steps = 6;
    predefined_profiles[0].cycle_repeat = true;
    predefined_profiles[0].cycle_count = 10;
    
    // Define HALT steps
    predefined_profiles[0].steps[0] = {-20.0, 20.0, 0.0, 1800, 5.0};
    predefined_profiles[0].steps[1] = {-20.0, 20.0, 0.0, 3600, 0.0};
    predefined_profiles[0].steps[2] = {85.0, 85.0, 0.0, 1800, 5.0};
    predefined_profiles[0].steps[3] = {85.0, 85.0, 0.0, 3600, 0.0};
    predefined_profiles[0].steps[4] = {60.0, 50.0, 500.0, 7200, 2.0};
    predefined_profiles[0].steps[5] = {25.0, 50.0, 0.0, 1800, 2.0};
    
    // HASS Profile
    predefined_profiles[1].name = "HASS_Screening";
    predefined_profiles[1].description = "Highly Accelerated Stress Screening";
    predefined_profiles[1].standard = "MIL-STD-810G";
    predefined_profiles[1].num_steps = 4;
    predefined_profiles[1].cycle_repeat = true;
    predefined_profiles[1].cycle_count = 5;
    
    // Define HASS steps
    predefined_profiles[1].steps[0] = {-10.0, 30.0, 0.0, 900, 10.0};
    predefined_profiles[1].steps[1] = {70.0, 80.0, 0.0, 900, 10.0};
    predefined_profiles[1].steps[2] = {70.0, 80.0, 250.0, 1800, 0.0};
    predefined_profiles[1].steps[3] = {25.0, 50.0, 0.0, 600, 5.0};
    
    // UV Weathering Profile
    predefined_profiles[2].name = "UV_Weathering";
    predefined_profiles[2].description = "UV Weathering Test";
    predefined_profiles[2].standard = "ASTM G154";
    predefined_profiles[2].num_steps = 2;
    predefined_profiles[2].cycle_repeat = true;
    predefined_profiles[2].cycle_count = 100;
    
    // Define UV weathering steps
    predefined_profiles[2].steps[0] = {60.0, 50.0, 750.0, 14400, 1.0}; // 4 hours UV
    predefined_profiles[2].steps[1] = {50.0, 95.0, 0.0, 14400, 1.0};   // 4 hours condensation
    
    // Thermal Cycling Profile
    predefined_profiles[3].name = "Thermal_Cycling";
    predefined_profiles[3].description = "Standard Thermal Cycling";
    predefined_profiles[3].standard = "IEC 60068-2-14";
    predefined_profiles[3].num_steps = 4;
    predefined_profiles[3].cycle_repeat = true;
    predefined_profiles[3].cycle_count = 1000;
    
    // Define thermal cycling steps
    predefined_profiles[3].steps[0] = {-40.0, 20.0, 0.0, 1800, 1.0};
    predefined_profiles[3].steps[1] = {-40.0, 20.0, 0.0, 1800, 0.0};
    predefined_profiles[3].steps[2] = {85.0, 20.0, 0.0, 1800, 1.0};
    predefined_profiles[3].steps[3] = {85.0, 20.0, 0.0, 1800, 0.0};
    
    // Custom Profile Template
    predefined_profiles[4].name = "Custom_Template";
    predefined_profiles[4].description = "User Customizable Profile";
    predefined_profiles[4].standard = "User Defined";
    predefined_profiles[4].num_steps = 1;
    predefined_profiles[4].cycle_repeat = false;
    predefined_profiles[4].cycle_count = 1;
    
    // Define custom template step
    predefined_profiles[4].steps[0] = {25.0, 50.0, 0.0, 3600, 1.0};
}

void loadAndSendProfile(String profile_name) {
    // First check predefined profiles
    for (int i = 0; i < NUM_PREDEFINED_PROFILES; i++) {
        if (predefined_profiles[i].name == profile_name) {
            forwardProfileToArduino(predefined_profiles[i]);
            return;
        }
    }
    
    // Check stored profiles
    String filename = "/profiles/" + profile_name + ".json";
    File file = SPIFFS.open(filename, "r");
    
    if (file) {
        String profile_json = file.readString();
        file.close();
        
        StaticJsonDocument<2048> doc;
        deserializeJson(doc, profile_json);
        
        TestProfile profile;
        profile.name = doc["name"];
        profile.description = doc["description"];
        profile.standard = doc["standard"];
        profile.num_steps = doc["num_steps"];
        profile.cycle_repeat = doc["cycle_repeat"];
        profile.cycle_count = doc["cycle_count"];
        
        for (int i = 0; i < profile.num_steps; i++) {
            profile.steps[i].temperature = doc["steps"][i]["temperature"];
            profile.steps[i].humidity = doc["steps"][i]["humidity"];
            profile.steps[i].uv_irradiance = doc["steps"][i]["uv_irradiance"];
            profile.steps[i].duration = doc["steps"][i]["duration"];
            profile.steps[i].ramp_rate = doc["steps"][i]["ramp_rate"];
        }
        
        forwardProfileToArduino(profile);
    } else {
        generateAlert("Profile not found: " + profile_name, 2);
    }
}

void forwardProfileToArduino(TestProfile& profile) {
    StaticJsonDocument<2048> doc;
    
    doc["type"] = "profile_update";
    doc["name"] = profile.name;
    doc["description"] = profile.description;
    doc["standard"] = profile.standard;
    doc["num_steps"] = profile.num_steps;
    doc["cycle_repeat"] = profile.cycle_repeat;
    doc["cycle_count"] = profile.cycle_count;
    
    JsonArray steps = doc.createNestedArray("steps");
    for (int i = 0; i < profile.num_steps; i++) {
        JsonObject step = steps.createNestedObject();
        step["temperature"] = profile.steps[i].temperature;
        step["humidity"] = profile.steps[i].humidity;
        step["uv_irradiance"] = profile.steps[i].uv_irradiance;
        step["duration"] = profile.steps[i].duration;
        step["ramp_rate"] = profile.steps[i].ramp_rate;
    }
    
    serializeJson(doc, ArduinoSerial);
    ArduinoSerial.println();
}

void saveProfile(TestProfile& profile) {
    String filename = "/profiles/" + profile.name + ".json";
    
    StaticJsonDocument<2048> doc;
    doc["name"] = profile.name;
    doc["description"] = profile.description;
    doc["standard"] = profile.standard;
    doc["num_steps"] = profile.num_steps;
    doc["cycle_repeat"] = profile.cycle_repeat;
    doc["cycle_count"] = profile.cycle_count;
    doc["created_by"] = profile.created_by;
    doc["created_time"] = profile.created_time;
    
    JsonArray steps = doc.createNestedArray("steps");
    for (int i = 0; i < profile.num_steps; i++) {
        JsonObject step = steps.createNestedObject();
        step["temperature"] = profile.steps[i].temperature;
        step["humidity"] = profile.steps[i].humidity;
        step["uv_irradiance"] = profile.steps[i].uv_irradiance;
        step["duration"] = profile.steps[i].duration;
        step["ramp_rate"] = profile.steps[i].ramp_rate;
    }
    
    File file = SPIFFS.open(filename, "w");
    if (file) {
        serializeJson(doc, file);
        file.close();
        Serial.println("Profile saved: " + profile.name);
    } else {
        generateAlert("Failed to save profile: " + profile.name, 2);
    }
}

void deleteProfile(String profile_name) {
    String filename = "/profiles/" + profile_name + ".json";
    
    if (SPIFFS.remove(filename)) {
        Serial.println("Profile deleted: " + profile_name);
    } else {
        generateAlert("Failed to delete profile: " + profile_name, 2);
    }
}

void sendProfileList() {
    StaticJsonDocument<1024> doc;
    JsonArray profiles = doc.createNestedArray("profiles");
    
    // Add predefined profiles
    for (int i = 0; i < NUM_PREDEFINED_PROFILES; i++) {
        JsonObject profile = profiles.createNestedObject();
        profile["name"] = predefined_profiles[i].name;
        profile["description"] = predefined_profiles[i].description;
        profile["standard"] = predefined_profiles[i].standard;
        profile["type"] = "predefined";
    }
    
    // Add stored profiles
    File root = SPIFFS.open("/profiles");
    File file = root.openNextFile();
    
    while (file) {
        if (!file.isDirectory()) {
            String filename = file.name();
            if (filename.endsWith(".json")) {
                String profile_name = filename.substring(0, filename.length() - 5);
                
                JsonObject profile = profiles.createNestedObject();
                profile["name"] = profile_name;
                profile["type"] = "custom";
            }
        }
        file = root.openNextFile();
    }
    
    char buffer[1024];
    serializeJson(doc, buffer);
    
    mqtt_client.publish(topic_profile, buffer);
}

void setupWebServer() {
    // Serve static files
    web_server.serveStatic("/", SPIFFS, "/www/");
    
    // API endpoints
    web_server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request) {
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<512> doc;
        doc["wifi_connected"] = wifi_connected;
        doc["mqtt_connected"] = mqtt_connected;
        doc["arduino_connected"] = arduino_connected;
        doc["test_active"] = test_active;
        doc["specimen_id"] = current_specimen_id;
        doc["data_points"] = data_points_collected;
        doc["alerts"] = alerts_generated;
        doc["uptime"] = millis();
        doc["free_heap"] = ESP.getFreeHeap();
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/profiles", HTTP_GET, [](AsyncWebServerRequest *request) {
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<1024> doc;
        JsonArray profiles = doc.createNestedArray("profiles");
        
        for (int i = 0; i < NUM_PREDEFINED_PROFILES; i++) {
            JsonObject profile = profiles.createNestedObject();
            profile["name"] = predefined_profiles[i].name;
            profile["description"] = predefined_profiles[i].description;
            profile["standard"] = predefined_profiles[i].standard;
        }
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/data", HTTP_GET, [](AsyncWebServerRequest *request) {
        String specimen_id = request->getParam("specimen_id")->value();
        
        // Return recent data for specimen
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<2048> doc;
        JsonArray data_array = doc.createNestedArray("data");
        
        // Add last 50 data points
        int start_index = (data_write_index - 50 + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
        
        for (int i = 0; i < 50; i++) {
            int index = (start_index + i) % DATA_BUFFER_SIZE;
            EnvironmentalData& data = data_buffer[index];
            
            JsonObject data_obj = data_array.createNestedObject();
            data_obj["timestamp"] = data.timestamp;
            data_obj["temperature"] = data.temperature;
            data_obj["humidity"] = data.humidity;
            data_obj["uv_irradiance"] = data.uv_irradiance;
            data_obj["pressure"] = data.pressure;
        }
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.begin();
}

void onWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, 
                     AwsEventType type, void *arg, uint8_t *data, size_t len) {
    if (type == WS_EVT_CONNECT) {
        Serial.printf("WebSocket client #%u connected\n", client->id());
    } else if (type == WS_EVT_DISCONNECT) {
        Serial.printf("WebSocket client #%u disconnected\n", client->id());
    } else if (type == WS_EVT_DATA) {
        AwsFrameInfo *info = (AwsFrameInfo*)arg;
        if (info->final && info->index == 0 && info->len == len) {
            if (info->opcode == WS_TEXT) {
                String message = "";
                for (size_t i = 0; i < len; i++) {
                    message += (char)data[i];
                }
                
                // Handle WebSocket commands
                handleWebSocketMessage(client, message);
            }
        }
    }
}

void handleWebSocketMessage(AsyncWebSocketClient *client, String message) {
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        return;
    }
    
    String command = doc["command"];
    
    if (command == "get_status") {
        sendWebSocketStatus(client);
    } else if (command == "start_test") {
        // Handle start test command
        String specimen_id = doc["specimen_id"];
        String profile_name = doc["profile_name"];
        
        // Forward to Arduino
        StaticJsonDocument<256> cmd_doc;
        cmd_doc["type"] = "command";
        cmd_doc["command"] = "start";
        cmd_doc["specimen_id"] = specimen_id;
        cmd_doc["profile_name"] = profile_name;
        
        serializeJson(cmd_doc, ArduinoSerial);
        ArduinoSerial.println();
    }
}

void sendWebSocketStatus(AsyncWebSocketClient *client) {
    StaticJsonDocument<512> doc;
    doc["type"] = "status";
    doc["wifi_connected"] = wifi_connected;
    doc["mqtt_connected"] = mqtt_connected;
    doc["test_active"] = test_active;
    doc["specimen_id"] = current_specimen_id;
    
    // Add current environmental data
    if (data_write_index > 0) {
        int last_index = (data_write_index - 1 + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
        EnvironmentalData& data = data_buffer[last_index];
        
        doc["temperature"] = data.temperature;
        doc["humidity"] = data.humidity;
        doc["uv_irradiance"] = data.uv_irradiance;
        doc["pressure"] = data.pressure;
        doc["current_step"] = data.current_step;
        doc["current_cycle"] = data.current_cycle;
    }
    
    String response;
    serializeJson(doc, response);
    client->text(response);
}

void updateWebSocketClients() {
    static uint32_t last_update = 0;
    
    if (millis() - last_update > 5000) { // Update every 5 seconds
        if (websocket.count() > 0) {
            StaticJsonDocument<256> doc;
            doc["type"] = "data_update";
            
            if (data_write_index > 0) {
                int last_index = (data_write_index - 1 + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
                EnvironmentalData& data = data_buffer[last_index];
                
                doc["temperature"] = data.temperature;
                doc["humidity"] = data.humidity;
                doc["uv_irradiance"] = data.uv_irradiance;
                doc["pressure"] = data.pressure;
                doc["test_running"] = data.test_running;
                doc["current_step"] = data.current_step;
                doc["current_cycle"] = data.current_cycle;
            }
            
            String message;
            serializeJson(doc, message);
            websocket.textAll(message);
        }
        
        last_update = millis();
    }
}

void sendConnectionMessage() {
    StaticJsonDocument<256> doc;
    
    doc["device"] = mqtt_client_id;
    doc["status"] = "connected";
    doc["ip"] = WiFi.localIP().toString();
    doc["rssi"] = WiFi.RSSI();
    doc["firmware"] = "v2.0";
    doc["capabilities"] = "temperature,humidity,uv,pressure";
    
    char buffer[256];
    serializeJson(doc, buffer);
    mqtt_client.publish(topic_status, buffer);
}

void sendStatusUpdate() {
    StaticJsonDocument<512> doc;
    
    doc["device"] = mqtt_client_id;
    doc["uptime"] = millis();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["arduino_connected"] = arduino_connected;
    doc["test_active"] = test_active;
    doc["specimen_id"] = current_specimen_id;
    doc["data_points"] = data_points_collected;
    doc["alerts"] = alerts_generated;
    
    char buffer[512];
    serializeJson(doc, buffer);
    mqtt_client.publish(topic_status, buffer);
}

void createCloudTestSession(JsonDocument& test_data) {
    HTTPClient http;
    http.begin(String(api_endpoint) + "/sessions");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", api_key);
    
    char body[512];
    serializeJson(test_data, body);
    
    int response_code = http.POST(body);
    if (response_code > 0) {
        String response = http.getString();
        Serial.print(F("Cloud session created: "));
        Serial.println(response);
    } else {
        generateAlert("Failed to create cloud session", 2);
    }
    
    http.end();
}

void closeCloudTestSession(JsonDocument& test_data) {
    HTTPClient http;
    http.begin(String(api_endpoint) + "/sessions/" + current_specimen_id + "/close");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-API-Key", api_key);
    
    char body[512];
    serializeJson(test_data, body);
    
    int response_code = http.PUT(body);
    if (response_code > 0) {
        String response = http.getString();
        Serial.print(F("Cloud session closed: "));
        Serial.println(response);
    }
    
    http.end();
}

void generateTestReport(JsonDocument& test_data) {
    // Generate comprehensive test report
    String filename = "/reports/" + current_specimen_id + "_report.json";
    
    File report = SD.open(filename, FILE_WRITE);
    if (report) {
        StaticJsonDocument<1024> doc;
        
        doc["test_id"] = current_specimen_id;
        doc["test_date"] = getTimestamp();
        doc["profile_name"] = test_data["profile_name"];
        doc["total_cycles"] = test_data["total_cycles"];
        doc["total_steps"] = test_data["total_steps"];
        doc["duration"] = test_data["duration"];
        
        // Add environmental statistics
        JsonObject env_stats = doc.createNestedObject("environmental_stats");
        env_stats["avg_temperature"] = calculateAverageTemperature();
        env_stats["max_temperature"] = calculateMaxTemperature();
        env_stats["min_temperature"] = calculateMinTemperature();
        env_stats["avg_humidity"] = calculateAverageHumidity();
        env_stats["max_humidity"] = calculateMaxHumidity();
        env_stats["min_humidity"] = calculateMinHumidity();
        env_stats["total_uv_dose"] = calculateTotalUVDose();
        
        // Add compliance information
        JsonObject compliance = doc.createNestedObject("compliance");
        compliance["standards"] = "MIL-STD-810G, ASTM G154";
        compliance["calibration_date"] = getCalibrationDate();
        compliance["operator"] = "ESP32 Automated System";
        
        serializeJson(doc, report);
        report.close();
        
        Serial.println(F("Test report generated"));
    }
}

void performHealthCheck() {
    // Check Arduino communication
    if (millis() - last_arduino_message > 120000) { // 2 minutes
        arduino_connected = false;
        generateAlert("Arduino communication lost", 3);
    }
    
    // Check WiFi signal strength
    if (WiFi.RSSI() < -80) {
        generateAlert("Weak WiFi signal: " + String(WiFi.RSSI()) + " dBm", 2);
    }
    
    // Check free heap
    if (ESP.getFreeHeap() < 50000) {
        generateAlert("Low memory: " + String(ESP.getFreeHeap()) + " bytes", 2);
    }
    
    // Check SD card space
    if (SD.totalBytes() - SD.usedBytes() < 100000000) { // 100MB
        generateAlert("Low SD card space", 2);
    }
}

void setupOTA() {
    ArduinoOTA.setHostname("env-chamber");
    
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

// Utility functions
void loadConfiguration() {
    // Load configuration from preferences
    // Implementation depends on specific requirements
}

void updateConfiguration(JsonDocument& config) {
    // Update system configuration
    // Implementation depends on specific requirements
}

void performRemoteCalibration(String sensor_type) {
    // Perform remote sensor calibration
    // Implementation depends on sensor type
}

void sendHistoricalData(String specimen_id, String start_time, String end_time) {
    // Send historical data for specified time range
    // Implementation depends on data storage format
}

void updateSystemStatus(JsonDocument& status) {
    // Update system status from Arduino
    // Implementation depends on status format
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

String getCalibrationDate() {
    // Return last calibration date
    return preferences.getString("last_calibration", "Not calibrated");
}

float calculateAverageTemperature() {
    // Calculate average temperature from buffer
    float sum = 0;
    int count = 0;
    
    for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
        if (data_buffer[i].timestamp > 0) {
            sum += data_buffer[i].temperature;
            count++;
        }
    }
    
    return count > 0 ? sum / count : 0;
}

float calculateMaxTemperature() {
    float max_temp = -100;
    
    for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
        if (data_buffer[i].timestamp > 0 && data_buffer[i].temperature > max_temp) {
            max_temp = data_buffer[i].temperature;
        }
    }
    
    return max_temp;
}

float calculateMinTemperature() {
    float min_temp = 200;
    
    for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
        if (data_buffer[i].timestamp > 0 && data_buffer[i].temperature < min_temp) {
            min_temp = data_buffer[i].temperature;
        }
    }
    
    return min_temp;
}

float calculateAverageHumidity() {
    float sum = 0;
    int count = 0;
    
    for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
        if (data_buffer[i].timestamp > 0) {
            sum += data_buffer[i].humidity;
            count++;
        }
    }
    
    return count > 0 ? sum / count : 0;
}

float calculateMaxHumidity() {
    float max_humidity = 0;
    
    for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
        if (data_buffer[i].timestamp > 0 && data_buffer[i].humidity > max_humidity) {
            max_humidity = data_buffer[i].humidity;
        }
    }
    
    return max_humidity;
}

float calculateMinHumidity() {
    float min_humidity = 100;
    
    for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
        if (data_buffer[i].timestamp > 0 && data_buffer[i].humidity < min_humidity) {
            min_humidity = data_buffer[i].humidity;
        }
    }
    
    return min_humidity;
}

float calculateTotalUVDose() {
    float total_dose = 0;
    
    for (int i = 0; i < DATA_BUFFER_SIZE; i++) {
        if (data_buffer[i].timestamp > 0) {
            total_dose += data_buffer[i].uv_irradiance * 10; // 10 second intervals
        }
    }
    
    return total_dose;
}

uint32_t last_arduino_message = 0;