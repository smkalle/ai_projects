/*
 * ESP32 IoT Gateway for Multi-Zone Thermal Management System
 * Program 16: Arduino Zero to Hero v2.0
 * 
 * Advanced analytics and cloud connectivity for thermal system
 * - WiFi connectivity and MQTT communication
 * - Advanced signal processing and analytics
 * - Machine learning for predictive control
 * - Cloud data storage and visualization
 * - Mobile app integration
 * 
 * Hardware: ESP32 Development Board
 * Communication: Serial with Arduino Mega
 * 
 * Author: Arduino Zero to Hero v2.0
 * Date: 2024
 * Version: 1.0
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WebServer.h>
#include <SPIFFS.h>
#include <ArduinoOTA.h>
#include <BluetoothSerial.h>
#include <esp_task_wdt.h>

// =============================================================================
// CONFIGURATION
// =============================================================================

// Network Configuration
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_username = "thermal_system";
const char* mqtt_password = "thermal_password";

// Cloud Configuration
const char* influxdb_url = "http://your-influxdb-server:8086";
const char* influxdb_database = "thermal_data";
const char* influxdb_username = "admin";
const char* influxdb_password = "password";

// System Configuration
#define SERIAL_BAUD 115200
#define WATCHDOG_TIMEOUT 10000  // 10 seconds
#define DATA_BUFFER_SIZE 1000
#define PREDICTION_WINDOW 60    // 60 data points for prediction

// =============================================================================
// GLOBAL OBJECTS
// =============================================================================

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WebServer webServer(80);
BluetoothSerial SerialBT;
HTTPClient httpClient;

// =============================================================================
// DATA STRUCTURES
// =============================================================================

struct ThermalData {
    unsigned long timestamp;
    float temperature[4];
    float setpoint[4];
    float current[4];
    float power[4];
    float total_power;
    float system_efficiency;
    bool safety_active[4];
    bool emergency_stop;
};

struct SystemStatus {
    bool wifi_connected;
    bool mqtt_connected;
    bool arduino_connected;
    unsigned long last_data_received;
    unsigned long uptime;
    float cpu_usage;
    float memory_usage;
};

struct MLPrediction {
    float predicted_temperature[4];
    float confidence_level;
    float time_to_setpoint[4];
    bool maintenance_needed;
    float energy_optimization_factor;
};

// =============================================================================
// GLOBAL VARIABLES
// =============================================================================

ThermalData currentData;
ThermalData dataBuffer[DATA_BUFFER_SIZE];
int dataBufferIndex = 0;
SystemStatus systemStatus;
MLPrediction mlPrediction;

unsigned long lastDataReceived = 0;
unsigned long lastCloudUpload = 0;
unsigned long lastPrediction = 0;
unsigned long lastStatusUpdate = 0;

bool bluetoothEnabled = false;
bool otaEnabled = false;
String deviceId = "thermal_system_001";

// =============================================================================
// SETUP FUNCTION
// =============================================================================

void setup() {
    Serial.begin(SERIAL_BAUD);
    Serial.println("ESP32 IoT Gateway Starting...");
    
    // Initialize watchdog
    esp_task_wdt_init(WATCHDOG_TIMEOUT, true);
    esp_task_wdt_add(NULL);
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("SPIFFS initialization failed");
    }
    
    // Initialize system status
    initializeSystemStatus();
    
    // Initialize networking
    setupWiFi();
    setupMQTT();
    setupWebServer();
    
    // Initialize OTA updates
    setupOTA();
    
    // Initialize Bluetooth (optional)
    setupBluetooth();
    
    // Initialize machine learning
    initializeMachineLearning();
    
    Serial.println("ESP32 IoT Gateway Ready");
    Serial.println("Waiting for data from Arduino...");
}

// =============================================================================
// MAIN LOOP
// =============================================================================

void loop() {
    // Reset watchdog
    esp_task_wdt_reset();
    
    // Handle WiFi reconnection
    if (WiFi.status() != WL_CONNECTED) {
        reconnectWiFi();
    }
    
    // Handle MQTT connection
    if (!mqttClient.connected()) {
        reconnectMQTT();
    }
    mqttClient.loop();
    
    // Handle OTA updates
    ArduinoOTA.handle();
    
    // Handle web server
    webServer.handleClient();
    
    // Process data from Arduino
    processArduinoData();
    
    // Perform analytics and predictions
    if (millis() - lastPrediction > 30000) {  // Every 30 seconds
        performAnalytics();
        lastPrediction = millis();
    }
    
    // Upload to cloud
    if (millis() - lastCloudUpload > 60000) {  // Every minute
        uploadToCloud();
        lastCloudUpload = millis();
    }
    
    // Update system status
    if (millis() - lastStatusUpdate > 5000) {  // Every 5 seconds
        updateSystemStatus();
        lastStatusUpdate = millis();
    }
    
    // Handle Bluetooth commands
    if (bluetoothEnabled) {
        handleBluetoothCommands();
    }
    
    delay(100);  // Small delay to prevent overwhelming
}

// =============================================================================
// INITIALIZATION FUNCTIONS
// =============================================================================

void initializeSystemStatus() {
    systemStatus.wifi_connected = false;
    systemStatus.mqtt_connected = false;
    systemStatus.arduino_connected = false;
    systemStatus.last_data_received = 0;
    systemStatus.uptime = millis();
    systemStatus.cpu_usage = 0.0;
    systemStatus.memory_usage = 0.0;
    
    // Initialize data structures
    memset(&currentData, 0, sizeof(currentData));
    memset(&mlPrediction, 0, sizeof(mlPrediction));
}

void setupWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    Serial.print("Connecting to WiFi");
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.print("WiFi connected! IP: ");
        Serial.println(WiFi.localIP());
        systemStatus.wifi_connected = true;
    } else {
        Serial.println();
        Serial.println("WiFi connection failed!");
    }
}

void setupMQTT() {
    mqttClient.setServer(mqtt_server, mqtt_port);
    mqttClient.setCallback(mqttCallback);
    mqttClient.setBufferSize(1024);  // Increase buffer for large messages
    
    reconnectMQTT();
}

void setupWebServer() {
    // Serve main dashboard
    webServer.on("/", HTTP_GET, []() {
        webServer.send(200, "text/html", generateDashboardHTML());
    });
    
    // API endpoints
    webServer.on("/api/status", HTTP_GET, handleAPIStatus);
    webServer.on("/api/data", HTTP_GET, handleAPIData);
    webServer.on("/api/predictions", HTTP_GET, handleAPIPredictions);
    webServer.on("/api/control", HTTP_POST, handleAPIControl);
    
    // File serving
    webServer.on("/style.css", HTTP_GET, []() {
        webServer.send(200, "text/css", generateCSS());
    });
    
    webServer.on("/script.js", HTTP_GET, []() {
        webServer.send(200, "application/javascript", generateJavaScript());
    });
    
    webServer.begin();
    Serial.println("Web server started on port 80");
}

void setupOTA() {
    ArduinoOTA.setHostname("thermal-gateway");
    ArduinoOTA.setPassword("thermal_ota_password");
    
    ArduinoOTA.onStart([]() {
        Serial.println("OTA Update Starting...");
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("OTA Update Complete!");
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("OTA Progress: %u%%\n", (progress * 100) / total);
    });
    
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("OTA Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });
    
    ArduinoOTA.begin();
    otaEnabled = true;
    Serial.println("OTA updates enabled");
}

void setupBluetooth() {
    if (SerialBT.begin("ThermalSystem")) {
        bluetoothEnabled = true;
        Serial.println("Bluetooth enabled: ThermalSystem");
    } else {
        Serial.println("Bluetooth initialization failed");
    }
}

void initializeMachineLearning() {
    // Initialize ML prediction models
    mlPrediction.confidence_level = 0.0;
    for (int i = 0; i < 4; i++) {
        mlPrediction.predicted_temperature[i] = 25.0;
        mlPrediction.time_to_setpoint[i] = 0.0;
    }
    mlPrediction.maintenance_needed = false;
    mlPrediction.energy_optimization_factor = 1.0;
    
    Serial.println("Machine learning models initialized");
}

// =============================================================================
// COMMUNICATION FUNCTIONS
// =============================================================================

void processArduinoData() {
    if (Serial.available()) {
        String jsonString = Serial.readStringUntil('\n');
        jsonString.trim();
        
        if (jsonString.length() > 0) {
            parseArduinoData(jsonString);
            lastDataReceived = millis();
            systemStatus.arduino_connected = true;
            systemStatus.last_data_received = lastDataReceived;
        }
    }
    
    // Check for communication timeout
    if (millis() - lastDataReceived > 10000) {  // 10 seconds timeout
        systemStatus.arduino_connected = false;
    }
}

void parseArduinoData(String jsonString) {
    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, jsonString);
    
    if (error) {
        Serial.print("JSON parsing error: ");
        Serial.println(error.c_str());
        return;
    }
    
    // Extract data
    currentData.timestamp = doc["timestamp"];
    currentData.total_power = doc["total_power"];
    currentData.system_efficiency = doc["system_efficiency"];
    currentData.emergency_stop = doc["emergency_stop"];
    
    // Extract zone data
    JsonArray zones = doc["zones"];
    for (int i = 0; i < 4 && i < zones.size(); i++) {
        currentData.temperature[i] = zones[i]["temperature"];
        currentData.setpoint[i] = zones[i]["setpoint"];
        currentData.current[i] = zones[i]["current"];
        currentData.power[i] = zones[i]["power"];
        currentData.safety_active[i] = zones[i]["safety_active"];
    }
    
    // Store in buffer for analytics
    storeDataInBuffer(currentData);
    
    // Publish to MQTT
    publishToMQTT();
}

void storeDataInBuffer(ThermalData data) {
    dataBuffer[dataBufferIndex] = data;
    dataBufferIndex = (dataBufferIndex + 1) % DATA_BUFFER_SIZE;
}

void reconnectWiFi() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Reconnecting to WiFi...");
        WiFi.disconnect();
        WiFi.reconnect();
        
        int attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 10) {
            delay(500);
            attempts++;
        }
        
        systemStatus.wifi_connected = (WiFi.status() == WL_CONNECTED);
    }
}

void reconnectMQTT() {
    while (!mqttClient.connected()) {
        Serial.println("Connecting to MQTT...");
        
        if (mqttClient.connect(deviceId.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("MQTT connected");
            systemStatus.mqtt_connected = true;
            
            // Subscribe to control topics
            mqttClient.subscribe("thermal/control/+");
            mqttClient.subscribe("thermal/setpoint/+");
            mqttClient.subscribe("thermal/config/+");
            
        } else {
            Serial.print("MQTT connection failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" retrying in 5 seconds");
            systemStatus.mqtt_connected = false;
            delay(5000);
        }
    }
}

void publishToMQTT() {
    if (!mqttClient.connected()) return;
    
    // Publish current data
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = currentData.timestamp;
    doc["total_power"] = currentData.total_power;
    doc["system_efficiency"] = currentData.system_efficiency;
    doc["emergency_stop"] = currentData.emergency_stop;
    
    JsonArray zones = doc.createNestedArray("zones");
    for (int i = 0; i < 4; i++) {
        JsonObject zone = zones.createNestedObject();
        zone["id"] = i;
        zone["temperature"] = currentData.temperature[i];
        zone["setpoint"] = currentData.setpoint[i];
        zone["current"] = currentData.current[i];
        zone["power"] = currentData.power[i];
        zone["safety_active"] = currentData.safety_active[i];
    }
    
    String payload;
    serializeJson(doc, payload);
    mqttClient.publish("thermal/data", payload.c_str());
    
    // Publish system status
    publishSystemStatus();
    
    // Publish predictions
    publishPredictions();
}

void publishSystemStatus() {
    StaticJsonDocument<512> doc;
    doc["device_id"] = deviceId;
    doc["wifi_connected"] = systemStatus.wifi_connected;
    doc["mqtt_connected"] = systemStatus.mqtt_connected;
    doc["arduino_connected"] = systemStatus.arduino_connected;
    doc["uptime"] = millis() - systemStatus.uptime;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["cpu_frequency"] = ESP.getCpuFreqMHz();
    doc["wifi_rssi"] = WiFi.RSSI();
    
    String payload;
    serializeJson(doc, payload);
    mqttClient.publish("thermal/system/status", payload.c_str());
}

void publishPredictions() {
    StaticJsonDocument<512> doc;
    doc["timestamp"] = millis();
    doc["confidence_level"] = mlPrediction.confidence_level;
    doc["maintenance_needed"] = mlPrediction.maintenance_needed;
    doc["energy_optimization_factor"] = mlPrediction.energy_optimization_factor;
    
    JsonArray predictions = doc.createNestedArray("predictions");
    for (int i = 0; i < 4; i++) {
        JsonObject pred = predictions.createNestedObject();
        pred["zone"] = i;
        pred["predicted_temperature"] = mlPrediction.predicted_temperature[i];
        pred["time_to_setpoint"] = mlPrediction.time_to_setpoint[i];
    }
    
    String payload;
    serializeJson(doc, payload);
    mqttClient.publish("thermal/predictions", payload.c_str());
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    String topicStr = String(topic);
    Serial.print("MQTT received: ");
    Serial.print(topicStr);
    Serial.print(" = ");
    Serial.println(message);
    
    // Forward control commands to Arduino
    if (topicStr.startsWith("thermal/control/") || topicStr.startsWith("thermal/setpoint/")) {
        Serial.println(message);  // Send to Arduino via serial
    }
    
    // Handle configuration commands
    if (topicStr.startsWith("thermal/config/")) {
        handleConfigCommand(topicStr, message);
    }
}

// =============================================================================
// ANALYTICS AND MACHINE LEARNING
// =============================================================================

void performAnalytics() {
    // Calculate trends
    calculateTrends();
    
    // Predict future temperatures
    predictTemperatures();
    
    // Analyze energy efficiency
    analyzeEnergyEfficiency();
    
    // Check for maintenance needs
    checkMaintenanceNeeds();
    
    // Optimize energy consumption
    optimizeEnergyConsumption();
    
    Serial.println("Analytics completed");
}

void calculateTrends() {
    // Calculate temperature trends for each zone
    for (int zone = 0; zone < 4; zone++) {
        float trend = calculateTemperatureTrend(zone);
        
        // Store trend information
        // This would typically be stored in a more sophisticated data structure
        Serial.print("Zone ");
        Serial.print(zone);
        Serial.print(" trend: ");
        Serial.print(trend);
        Serial.println("°C/min");
    }
}

float calculateTemperatureTrend(int zone) {
    if (dataBufferIndex < 10) return 0.0;  // Not enough data
    
    float sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;
    int n = min(dataBufferIndex, 30);  // Use last 30 data points
    
    for (int i = 0; i < n; i++) {
        int idx = (dataBufferIndex - 1 - i + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
        float x = i;
        float y = dataBuffer[idx].temperature[zone];
        
        sum_x += x;
        sum_y += y;
        sum_xy += x * y;
        sum_x2 += x * x;
    }
    
    // Linear regression slope
    float slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);
    
    // Convert to °C/min (assuming 1 minute between samples)
    return slope;
}

void predictTemperatures() {
    for (int zone = 0; zone < 4; zone++) {
        // Simple linear prediction based on current trend
        float trend = calculateTemperatureTrend(zone);
        float current_temp = currentData.temperature[zone];
        float setpoint = currentData.setpoint[zone];
        
        // Predict temperature in 5 minutes
        mlPrediction.predicted_temperature[zone] = current_temp + (trend * 5.0);
        
        // Estimate time to reach setpoint
        if (abs(trend) > 0.1) {
            mlPrediction.time_to_setpoint[zone] = abs(setpoint - current_temp) / abs(trend);
        } else {
            mlPrediction.time_to_setpoint[zone] = 999.0;  // Very long time
        }
    }
    
    // Calculate confidence level based on data consistency
    mlPrediction.confidence_level = calculatePredictionConfidence();
}

float calculatePredictionConfidence() {
    if (dataBufferIndex < 20) return 0.0;
    
    float total_variance = 0.0;
    for (int zone = 0; zone < 4; zone++) {
        float variance = calculateTemperatureVariance(zone);
        total_variance += variance;
    }
    
    // Lower variance = higher confidence
    float confidence = max(0.0, 1.0 - (total_variance / 100.0));
    return confidence;
}

float calculateTemperatureVariance(int zone) {
    if (dataBufferIndex < 10) return 100.0;
    
    float sum = 0.0;
    float sum_sq = 0.0;
    int n = min(dataBufferIndex, 20);
    
    for (int i = 0; i < n; i++) {
        int idx = (dataBufferIndex - 1 - i + DATA_BUFFER_SIZE) % DATA_BUFFER_SIZE;
        float temp = dataBuffer[idx].temperature[zone];
        sum += temp;
        sum_sq += temp * temp;
    }
    
    float mean = sum / n;
    float variance = (sum_sq / n) - (mean * mean);
    
    return variance;
}

void analyzeEnergyEfficiency() {
    float total_energy = 0.0;
    float total_thermal_performance = 0.0;
    
    for (int zone = 0; zone < 4; zone++) {
        total_energy += currentData.power[zone];
        
        // Calculate thermal performance (inverse of temperature error)
        float error = abs(currentData.temperature[zone] - currentData.setpoint[zone]);
        float performance = 1.0 / (1.0 + error);
        total_thermal_performance += performance;
    }
    
    // Energy efficiency = thermal performance / energy consumption
    if (total_energy > 0) {
        float efficiency = total_thermal_performance / total_energy;
        mlPrediction.energy_optimization_factor = efficiency;
    }
}

void checkMaintenanceNeeds() {
    // Check for maintenance indicators
    bool needs_maintenance = false;
    
    // Check for persistent temperature errors
    for (int zone = 0; zone < 4; zone++) {
        float error = abs(currentData.temperature[zone] - currentData.setpoint[zone]);
        if (error > 5.0) {  // More than 5°C error
            needs_maintenance = true;
            break;
        }
    }
    
    // Check for high power consumption
    if (currentData.total_power > 500.0) {  // More than 500W
        needs_maintenance = true;
    }
    
    // Check for frequent safety activations
    int safety_count = 0;
    for (int zone = 0; zone < 4; zone++) {
        if (currentData.safety_active[zone]) {
            safety_count++;
        }
    }
    
    if (safety_count > 1) {  // More than 1 zone in safety mode
        needs_maintenance = true;
    }
    
    mlPrediction.maintenance_needed = needs_maintenance;
}

void optimizeEnergyConsumption() {
    // Analyze energy usage patterns and suggest optimizations
    
    // Calculate average power per zone
    float avg_power = currentData.total_power / 4.0;
    
    // Identify zones with high power consumption
    for (int zone = 0; zone < 4; zone++) {
        if (currentData.power[zone] > avg_power * 1.5) {
            // High power zone - suggest optimization
            Serial.print("Zone ");
            Serial.print(zone);
            Serial.println(" using high power - optimization needed");
        }
    }
    
    // Calculate optimization factor
    float target_power = 300.0;  // Target total power consumption
    if (currentData.total_power > target_power) {
        mlPrediction.energy_optimization_factor = target_power / currentData.total_power;
    } else {
        mlPrediction.energy_optimization_factor = 1.0;
    }
}

// =============================================================================
// CLOUD INTEGRATION
// =============================================================================

void uploadToCloud() {
    if (WiFi.status() != WL_CONNECTED) return;
    
    // Upload to InfluxDB
    uploadToInfluxDB();
    
    // Upload to custom cloud service
    uploadToCustomCloud();
    
    Serial.println("Cloud upload completed");
}

void uploadToInfluxDB() {
    httpClient.begin(influxdb_url + "/write?db=" + influxdb_database);
    httpClient.addHeader("Content-Type", "application/x-www-form-urlencoded");
    
    String data = "thermal_data,device=" + deviceId + " ";
    data += "total_power=" + String(currentData.total_power) + ",";
    data += "system_efficiency=" + String(currentData.system_efficiency) + ",";
    data += "emergency_stop=" + String(currentData.emergency_stop ? "true" : "false");
    
    for (int i = 0; i < 4; i++) {
        data += ",zone" + String(i) + "_temp=" + String(currentData.temperature[i]);
        data += ",zone" + String(i) + "_setpoint=" + String(currentData.setpoint[i]);
        data += ",zone" + String(i) + "_current=" + String(currentData.current[i]);
        data += ",zone" + String(i) + "_power=" + String(currentData.power[i]);
    }
    
    data += " " + String(currentData.timestamp * 1000000);  // Convert to nanoseconds
    
    int httpResponseCode = httpClient.POST(data);
    
    if (httpResponseCode > 0) {
        Serial.print("InfluxDB upload response: ");
        Serial.println(httpResponseCode);
    } else {
        Serial.print("InfluxDB upload error: ");
        Serial.println(httpClient.errorToString(httpResponseCode));
    }
    
    httpClient.end();
}

void uploadToCustomCloud() {
    // Implement custom cloud service upload
    // This would typically be a REST API call
    
    StaticJsonDocument<1024> doc;
    doc["device_id"] = deviceId;
    doc["timestamp"] = currentData.timestamp;
    doc["total_power"] = currentData.total_power;
    doc["system_efficiency"] = currentData.system_efficiency;
    
    JsonArray zones = doc.createNestedArray("zones");
    for (int i = 0; i < 4; i++) {
        JsonObject zone = zones.createNestedObject();
        zone["id"] = i;
        zone["temperature"] = currentData.temperature[i];
        zone["setpoint"] = currentData.setpoint[i];
        zone["current"] = currentData.current[i];
        zone["power"] = currentData.power[i];
    }
    
    String payload;
    serializeJson(doc, payload);
    
    // Example API call (replace with actual endpoint)
    httpClient.begin("https://api.yourcloudservice.com/thermal/data");
    httpClient.addHeader("Content-Type", "application/json");
    httpClient.addHeader("Authorization", "Bearer your_api_token");
    
    int httpResponseCode = httpClient.POST(payload);
    
    if (httpResponseCode > 0) {
        Serial.print("Cloud API response: ");
        Serial.println(httpResponseCode);
    } else {
        Serial.print("Cloud API error: ");
        Serial.println(httpClient.errorToString(httpResponseCode));
    }
    
    httpClient.end();
}

// =============================================================================
// WEB SERVER HANDLERS
// =============================================================================

void handleAPIStatus() {
    StaticJsonDocument<512> doc;
    doc["device_id"] = deviceId;
    doc["wifi_connected"] = systemStatus.wifi_connected;
    doc["mqtt_connected"] = systemStatus.mqtt_connected;
    doc["arduino_connected"] = systemStatus.arduino_connected;
    doc["uptime"] = millis() - systemStatus.uptime;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["total_heap"] = ESP.getHeapSize();
    doc["cpu_frequency"] = ESP.getCpuFreqMHz();
    doc["wifi_rssi"] = WiFi.RSSI();
    doc["last_data_received"] = systemStatus.last_data_received;
    
    String response;
    serializeJson(doc, response);
    
    webServer.send(200, "application/json", response);
}

void handleAPIData() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = currentData.timestamp;
    doc["total_power"] = currentData.total_power;
    doc["system_efficiency"] = currentData.system_efficiency;
    doc["emergency_stop"] = currentData.emergency_stop;
    
    JsonArray zones = doc.createNestedArray("zones");
    for (int i = 0; i < 4; i++) {
        JsonObject zone = zones.createNestedObject();
        zone["id"] = i;
        zone["temperature"] = currentData.temperature[i];
        zone["setpoint"] = currentData.setpoint[i];
        zone["current"] = currentData.current[i];
        zone["power"] = currentData.power[i];
        zone["safety_active"] = currentData.safety_active[i];
    }
    
    String response;
    serializeJson(doc, response);
    
    webServer.send(200, "application/json", response);
}

void handleAPIPredictions() {
    StaticJsonDocument<512> doc;
    doc["timestamp"] = millis();
    doc["confidence_level"] = mlPrediction.confidence_level;
    doc["maintenance_needed"] = mlPrediction.maintenance_needed;
    doc["energy_optimization_factor"] = mlPrediction.energy_optimization_factor;
    
    JsonArray predictions = doc.createNestedArray("predictions");
    for (int i = 0; i < 4; i++) {
        JsonObject pred = predictions.createNestedObject();
        pred["zone"] = i;
        pred["predicted_temperature"] = mlPrediction.predicted_temperature[i];
        pred["time_to_setpoint"] = mlPrediction.time_to_setpoint[i];
    }
    
    String response;
    serializeJson(doc, response);
    
    webServer.send(200, "application/json", response);
}

void handleAPIControl() {
    if (webServer.hasArg("plain")) {
        String body = webServer.arg("plain");
        
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, body);
        
        if (!error) {
            String command = doc["command"];
            
            if (command == "set_setpoint") {
                int zone = doc["zone"];
                float setpoint = doc["setpoint"];
                
                // Send command to Arduino
                String arduinoCommand = "SET " + String(zone) + " " + String(setpoint);
                Serial.println(arduinoCommand);
                
                webServer.send(200, "application/json", "{\"status\":\"success\"}");
            } else if (command == "reset_system") {
                Serial.println("RESET");
                webServer.send(200, "application/json", "{\"status\":\"success\"}");
            } else {
                webServer.send(400, "application/json", "{\"error\":\"unknown_command\"}");
            }
        } else {
            webServer.send(400, "application/json", "{\"error\":\"invalid_json\"}");
        }
    } else {
        webServer.send(400, "application/json", "{\"error\":\"no_data\"}");
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

void updateSystemStatus() {
    systemStatus.wifi_connected = (WiFi.status() == WL_CONNECTED);
    systemStatus.mqtt_connected = mqttClient.connected();
    systemStatus.cpu_usage = getCPUUsage();
    systemStatus.memory_usage = getMemoryUsage();
}

float getCPUUsage() {
    // Simplified CPU usage calculation
    // In a real implementation, this would be more sophisticated
    return 50.0;  // Placeholder
}

float getMemoryUsage() {
    size_t free_heap = ESP.getFreeHeap();
    size_t total_heap = ESP.getHeapSize();
    return ((float)(total_heap - free_heap) / total_heap) * 100.0;
}

void handleConfigCommand(String topic, String message) {
    if (topic == "thermal/config/wifi") {
        // Handle WiFi configuration
        Serial.println("WiFi config received");
    } else if (topic == "thermal/config/mqtt") {
        // Handle MQTT configuration
        Serial.println("MQTT config received");
    } else if (topic == "thermal/config/update") {
        // Handle firmware update
        Serial.println("Update config received");
    }
}

void handleBluetoothCommands() {
    if (SerialBT.available()) {
        String command = SerialBT.readString();
        command.trim();
        
        if (command == "STATUS") {
            SerialBT.println("System Status:");
            SerialBT.println("WiFi: " + String(systemStatus.wifi_connected ? "Connected" : "Disconnected"));
            SerialBT.println("MQTT: " + String(systemStatus.mqtt_connected ? "Connected" : "Disconnected"));
            SerialBT.println("Arduino: " + String(systemStatus.arduino_connected ? "Connected" : "Disconnected"));
            SerialBT.println("Uptime: " + String((millis() - systemStatus.uptime) / 1000) + "s");
        } else if (command == "DATA") {
            SerialBT.println("Current Data:");
            SerialBT.println("Total Power: " + String(currentData.total_power) + "W");
            SerialBT.println("System Efficiency: " + String(currentData.system_efficiency) + "%");
            for (int i = 0; i < 4; i++) {
                SerialBT.println("Zone " + String(i) + ": " + String(currentData.temperature[i]) + "°C");
            }
        } else if (command.startsWith("SET")) {
            // Forward to Arduino
            Serial.println(command);
            SerialBT.println("Command sent to Arduino");
        } else {
            SerialBT.println("Unknown command. Available: STATUS, DATA, SET");
        }
    }
}

// =============================================================================
// HTML/CSS/JS GENERATION
// =============================================================================

String generateDashboardHTML() {
    return R"(
<!DOCTYPE html>
<html>
<head>
    <title>Thermal Management Dashboard</title>
    <link rel="stylesheet" href="/style.css">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <div class="container">
        <h1>🌡️ Multi-Zone Thermal Management System</h1>
        
        <div class="status-bar">
            <div class="status-item">
                <span class="status-label">WiFi:</span>
                <span class="status-value" id="wifi-status">-</span>
            </div>
            <div class="status-item">
                <span class="status-label">MQTT:</span>
                <span class="status-value" id="mqtt-status">-</span>
            </div>
            <div class="status-item">
                <span class="status-label">Arduino:</span>
                <span class="status-value" id="arduino-status">-</span>
            </div>
            <div class="status-item">
                <span class="status-label">Uptime:</span>
                <span class="status-value" id="uptime">-</span>
            </div>
        </div>
        
        <div class="system-overview">
            <div class="metric">
                <h3>Total Power</h3>
                <div class="metric-value" id="total-power">-</div>
                <div class="metric-unit">W</div>
            </div>
            <div class="metric">
                <h3>System Efficiency</h3>
                <div class="metric-value" id="system-efficiency">-</div>
                <div class="metric-unit">%</div>
            </div>
        </div>
        
        <div class="zones-container">
            <div class="zone-card" id="zone-0">
                <h3>Zone 0</h3>
                <div class="zone-temp" id="zone-0-temp">-</div>
                <div class="zone-setpoint">→ <span id="zone-0-setpoint">-</span>°C</div>
                <div class="zone-power"><span id="zone-0-power">-</span>W</div>
                <div class="zone-controls">
                    <input type="number" id="zone-0-input" min="15" max="85" step="0.1">
                    <button onclick="setZoneSetpoint(0)">Set</button>
                </div>
            </div>
            
            <div class="zone-card" id="zone-1">
                <h3>Zone 1</h3>
                <div class="zone-temp" id="zone-1-temp">-</div>
                <div class="zone-setpoint">→ <span id="zone-1-setpoint">-</span>°C</div>
                <div class="zone-power"><span id="zone-1-power">-</span>W</div>
                <div class="zone-controls">
                    <input type="number" id="zone-1-input" min="15" max="85" step="0.1">
                    <button onclick="setZoneSetpoint(1)">Set</button>
                </div>
            </div>
            
            <div class="zone-card" id="zone-2">
                <h3>Zone 2</h3>
                <div class="zone-temp" id="zone-2-temp">-</div>
                <div class="zone-setpoint">→ <span id="zone-2-setpoint">-</span>°C</div>
                <div class="zone-power"><span id="zone-2-power">-</span>W</div>
                <div class="zone-controls">
                    <input type="number" id="zone-2-input" min="15" max="85" step="0.1">
                    <button onclick="setZoneSetpoint(2)">Set</button>
                </div>
            </div>
            
            <div class="zone-card" id="zone-3">
                <h3>Zone 3</h3>
                <div class="zone-temp" id="zone-3-temp">-</div>
                <div class="zone-setpoint">→ <span id="zone-3-setpoint">-</span>°C</div>
                <div class="zone-power"><span id="zone-3-power">-</span>W</div>
                <div class="zone-controls">
                    <input type="number" id="zone-3-input" min="15" max="85" step="0.1">
                    <button onclick="setZoneSetpoint(3)">Set</button>
                </div>
            </div>
        </div>
        
        <div class="predictions-section">
            <h2>🔮 Predictions</h2>
            <div class="predictions-grid">
                <div class="prediction-item">
                    <h4>Confidence Level</h4>
                    <div class="prediction-value" id="confidence-level">-</div>
                </div>
                <div class="prediction-item">
                    <h4>Maintenance Needed</h4>
                    <div class="prediction-value" id="maintenance-needed">-</div>
                </div>
                <div class="prediction-item">
                    <h4>Energy Optimization</h4>
                    <div class="prediction-value" id="energy-optimization">-</div>
                </div>
            </div>
        </div>
        
        <div class="emergency-controls">
            <button class="emergency-btn" onclick="emergencyStop()">🚨 Emergency Stop</button>
            <button class="reset-btn" onclick="resetSystem()">🔄 Reset System</button>
        </div>
    </div>
    
    <script src="/script.js"></script>
</body>
</html>
    )";
}

String generateCSS() {
    return R"(
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

h1 {
    text-align: center;
    margin-bottom: 30px;
    font-size: 2.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.status-bar {
    display: flex;
    justify-content: space-around;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 30px;
    backdrop-filter: blur(10px);
}

.status-item {
    text-align: center;
}

.status-label {
    display: block;
    font-size: 0.9em;
    opacity: 0.8;
}

.status-value {
    display: block;
    font-size: 1.2em;
    font-weight: bold;
    margin-top: 5px;
}

.system-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.metric {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
}

.metric h3 {
    margin-bottom: 10px;
    opacity: 0.9;
}

.metric-value {
    font-size: 2.5em;
    font-weight: bold;
    color: #4CAF50;
}

.metric-unit {
    font-size: 1.2em;
    opacity: 0.7;
}

.zones-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.zone-card {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    backdrop-filter: blur(10px);
    border: 2px solid transparent;
    transition: all 0.3s ease;
}

.zone-card:hover {
    border-color: rgba(255,255,255,0.3);
    transform: translateY(-2px);
}

.zone-card h3 {
    margin-bottom: 15px;
    color: #FFD700;
}

.zone-temp {
    font-size: 2.5em;
    font-weight: bold;
    color: #4CAF50;
    margin-bottom: 5px;
}

.zone-temp::after {
    content: "°C";
    font-size: 0.6em;
    opacity: 0.7;
}

.zone-setpoint {
    font-size: 1.2em;
    margin-bottom: 5px;
    opacity: 0.8;
}

.zone-power {
    font-size: 1.1em;
    margin-bottom: 15px;
    opacity: 0.8;
}

.zone-controls {
    display: flex;
    gap: 10px;
    align-items: center;
}

.zone-controls input {
    flex: 1;
    padding: 8px;
    border: none;
    border-radius: 5px;
    background: rgba(255,255,255,0.2);
    color: white;
}

.zone-controls input::placeholder {
    color: rgba(255,255,255,0.7);
}

.zone-controls button {
    padding: 8px 15px;
    border: none;
    border-radius: 5px;
    background: #4CAF50;
    color: white;
    cursor: pointer;
    transition: background 0.3s ease;
}

.zone-controls button:hover {
    background: #45a049;
}

.predictions-section {
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 30px;
    backdrop-filter: blur(10px);
}

.predictions-section h2 {
    margin-bottom: 20px;
    text-align: center;
}

.predictions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.prediction-item {
    text-align: center;
    padding: 15px;
    background: rgba(255,255,255,0.05);
    border-radius: 8px;
}

.prediction-item h4 {
    margin-bottom: 10px;
    opacity: 0.9;
}

.prediction-value {
    font-size: 1.5em;
    font-weight: bold;
    color: #FFD700;
}

.emergency-controls {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 30px;
}

.emergency-btn {
    padding: 15px 30px;
    font-size: 1.1em;
    border: none;
    border-radius: 8px;
    background: #f44336;
    color: white;
    cursor: pointer;
    transition: background 0.3s ease;
}

.emergency-btn:hover {
    background: #d32f2f;
}

.reset-btn {
    padding: 15px 30px;
    font-size: 1.1em;
    border: none;
    border-radius: 8px;
    background: #2196F3;
    color: white;
    cursor: pointer;
    transition: background 0.3s ease;
}

.reset-btn:hover {
    background: #1976D2;
}

@media (max-width: 768px) {
    .status-bar {
        flex-direction: column;
        gap: 10px;
    }
    
    .zones-container {
        grid-template-columns: 1fr;
    }
    
    .emergency-controls {
        flex-direction: column;
        align-items: center;
    }
}
    )";
}

String generateJavaScript() {
    return R"(
let lastUpdateTime = 0;
const UPDATE_INTERVAL = 2000; // 2 seconds

// Start updating data
updateData();
setInterval(updateData, UPDATE_INTERVAL);

function updateData() {
    // Update system status
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('wifi-status').textContent = data.wifi_connected ? 'Connected' : 'Disconnected';
            document.getElementById('mqtt-status').textContent = data.mqtt_connected ? 'Connected' : 'Disconnected';
            document.getElementById('arduino-status').textContent = data.arduino_connected ? 'Connected' : 'Disconnected';
            document.getElementById('uptime').textContent = formatUptime(data.uptime);
            
            // Update status colors
            updateStatusColors(data);
        })
        .catch(error => console.error('Error fetching status:', error));
    
    // Update thermal data
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-power').textContent = data.total_power.toFixed(1);
            document.getElementById('system-efficiency').textContent = data.system_efficiency.toFixed(1);
            
            // Update zone data
            for (let i = 0; i < 4; i++) {
                if (data.zones[i]) {
                    const zone = data.zones[i];
                    document.getElementById(`zone-${i}-temp`).textContent = zone.temperature.toFixed(1);
                    document.getElementById(`zone-${i}-setpoint`).textContent = zone.setpoint.toFixed(1);
                    document.getElementById(`zone-${i}-power`).textContent = zone.power.toFixed(1);
                    
                    // Update zone card colors based on safety status
                    const zoneCard = document.getElementById(`zone-${i}`);
                    if (zone.safety_active) {
                        zoneCard.style.borderColor = '#f44336';
                        zoneCard.style.backgroundColor = 'rgba(244, 67, 54, 0.1)';
                    } else {
                        zoneCard.style.borderColor = 'transparent';
                        zoneCard.style.backgroundColor = 'rgba(255,255,255,0.1)';
                    }
                }
            }
        })
        .catch(error => console.error('Error fetching data:', error));
    
    // Update predictions
    fetch('/api/predictions')
        .then(response => response.json())
        .then(data => {
            document.getElementById('confidence-level').textContent = (data.confidence_level * 100).toFixed(1) + '%';
            document.getElementById('maintenance-needed').textContent = data.maintenance_needed ? 'Yes' : 'No';
            document.getElementById('energy-optimization').textContent = (data.energy_optimization_factor * 100).toFixed(1) + '%';
            
            // Update prediction colors
            const confidenceElement = document.getElementById('confidence-level');
            if (data.confidence_level > 0.8) {
                confidenceElement.style.color = '#4CAF50';
            } else if (data.confidence_level > 0.5) {
                confidenceElement.style.color = '#FFD700';
            } else {
                confidenceElement.style.color = '#f44336';
            }
            
            const maintenanceElement = document.getElementById('maintenance-needed');
            maintenanceElement.style.color = data.maintenance_needed ? '#f44336' : '#4CAF50';
        })
        .catch(error => console.error('Error fetching predictions:', error));
}

function updateStatusColors(data) {
    const wifiElement = document.getElementById('wifi-status');
    const mqttElement = document.getElementById('mqtt-status');
    const arduinoElement = document.getElementById('arduino-status');
    
    wifiElement.style.color = data.wifi_connected ? '#4CAF50' : '#f44336';
    mqttElement.style.color = data.mqtt_connected ? '#4CAF50' : '#f44336';
    arduinoElement.style.color = data.arduino_connected ? '#4CAF50' : '#f44336';
}

function formatUptime(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
        return `${days}d ${hours % 24}h`;
    } else if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
    } else {
        return `${minutes}m ${seconds % 60}s`;
    }
}

function setZoneSetpoint(zone) {
    const input = document.getElementById(`zone-${zone}-input`);
    const setpoint = parseFloat(input.value);
    
    if (isNaN(setpoint) || setpoint < 15 || setpoint > 85) {
        alert('Please enter a valid setpoint between 15°C and 85°C');
        return;
    }
    
    const command = {
        command: 'set_setpoint',
        zone: zone,
        setpoint: setpoint
    };
    
    fetch('/api/control', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(command)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log(`Zone ${zone} setpoint set to ${setpoint}°C`);
            input.value = '';
        } else {
            alert('Error setting setpoint: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error setting setpoint');
    });
}

function emergencyStop() {
    if (confirm('Are you sure you want to activate emergency stop?')) {
        const command = {
            command: 'emergency_stop'
        };
        
        fetch('/api/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(command)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Emergency stop activated');
            } else {
                alert('Error activating emergency stop: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error activating emergency stop');
        });
    }
}

function resetSystem() {
    if (confirm('Are you sure you want to reset the system?')) {
        const command = {
            command: 'reset_system'
        };
        
        fetch('/api/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(command)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('System reset successful');
            } else {
                alert('Error resetting system: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error resetting system');
        });
    }
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 'r') {
        event.preventDefault();
        resetSystem();
    } else if (event.ctrlKey && event.key === 'e') {
        event.preventDefault();
        emergencyStop();
    }
});

// Add visual feedback for connectivity
function updateConnectivityStatus() {
    const statusBar = document.querySelector('.status-bar');
    
    // Check if all systems are connected
    const wifiConnected = document.getElementById('wifi-status').textContent === 'Connected';
    const mqttConnected = document.getElementById('mqtt-status').textContent === 'Connected';
    const arduinoConnected = document.getElementById('arduino-status').textContent === 'Connected';
    
    if (wifiConnected && mqttConnected && arduinoConnected) {
        statusBar.style.borderLeft = '5px solid #4CAF50';
    } else {
        statusBar.style.borderLeft = '5px solid #f44336';
    }
}

// Update connectivity status every few seconds
setInterval(updateConnectivityStatus, 3000);
    )";
}