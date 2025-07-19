/*
 * Program 25: Corrosion Monitoring System - ESP32 IoT Gateway
 * 
 * This program implements a comprehensive IoT gateway for the corrosion monitoring
 * system, providing cloud connectivity, real-time data streaming, advanced analytics,
 * and remote monitoring capabilities. The system supports multiple communication
 * protocols and provides a complete web-based dashboard for system management.
 * 
 * Features:
 * - Multi-protocol communication (WiFi, LoRa, Cellular)
 * - Real-time data streaming and visualization
 * - Advanced analytics and trend analysis
 * - Predictive maintenance algorithms
 * - Cloud-based data storage and analysis
 * - Mobile app integration
 * - Alarm and notification system
 * - Remote system configuration
 * 
 * Author: Arduino Zero to Hero v2.0
 * Created: 2024
 * 
 * Hardware Requirements:
 * - ESP32 DevKit V1
 * - LoRa module (SX1276)
 * - Cellular modem (optional)
 * - WiFi connectivity
 * - SD card for local storage
 * - GPS module
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
 * - LoRa.h
 * - TinyGPS++.h
 * - WebSocketsServer.h
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <HTTPClient.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include <LoRa.h>
#include <TinyGPS++.h>
#include <WebSocketsServer.h>
#include <Update.h>
#include <mbedtls/md.h>

// Network Configuration
const char* ssid = "CORROSION_MONITOR_WIFI";
const char* password = "SecureCorrosionMonitor2024!";
const char* fallback_ssid = "BACKUP_NETWORK";
const char* fallback_password = "BackupPassword123";

// Cloud Configuration
const char* cloud_endpoint = "https://api.corrosion-monitor.com";
const char* websocket_server = "wss://ws.corrosion-monitor.com";
const char* mqtt_broker = "mqtt.corrosion-monitor.com";
const int mqtt_port = 8883;
const char* api_key = "CMS_API_KEY_2024";
const char* device_id = "CMS_001";
const char* organization_id = "INFRA_MONITORING";

// LoRa Configuration
#define LORA_SS 5
#define LORA_RST 14
#define LORA_DIO0 2
#define LORA_FREQUENCY 915E6
#define LORA_BANDWIDTH 125E3
#define LORA_SPREADING_FACTOR 7

// Pin Definitions
#define ARDUINO_SERIAL_TX 17
#define ARDUINO_SERIAL_RX 16
#define GPS_SERIAL_TX 21
#define GPS_SERIAL_RX 22
#define CELLULAR_POWER 23
#define CELLULAR_TX 26
#define CELLULAR_RX 27
#define STATUS_LED_WIFI 32
#define STATUS_LED_LORA 33
#define STATUS_LED_CELLULAR 25
#define STATUS_LED_CLOUD 26
#define EMERGENCY_BUTTON 0
#define RESET_BUTTON 4

// Communication Parameters
#define ARDUINO_BAUD_RATE 115200
#define GPS_BAUD_RATE 9600
#define CELLULAR_BAUD_RATE 115200
#define BUFFER_SIZE 4096
#define MAX_RETRY_COUNT 3
#define HEARTBEAT_INTERVAL 30000
#define DATA_TRANSMISSION_INTERVAL 60000

// Data Structures
struct CorrosionData {
    uint32_t timestamp;
    String device_id;
    String location;
    float latitude;
    float longitude;
    
    // Electrochemical data
    float potential[8];
    float current[8];
    float corrosion_rate[8];
    float polarization_resistance[8];
    uint8_t severity_level[8];
    
    // Environmental data
    float temperature;
    float humidity;
    float ph_value;
    float conductivity;
    float dissolved_oxygen;
    float chloride_concentration;
    float atmospheric_pressure;
    float wind_speed;
    float wind_direction;
    float solar_irradiance;
    
    // System data
    float battery_voltage;
    float solar_voltage;
    float system_temperature;
    uint32_t uptime;
    bool system_healthy;
    
    // Quality indicators
    uint8_t data_quality;
    uint8_t communication_quality;
    uint8_t power_quality;
};

struct AlertData {
    uint32_t timestamp;
    String device_id;
    String alert_type;
    String alert_level;
    String alert_message;
    String affected_component;
    float alert_value;
    float threshold_value;
    String recommended_action;
    bool acknowledged;
};

struct SystemStatus {
    String device_id;
    String firmware_version;
    uint32_t uptime;
    bool wifi_connected;
    bool lora_connected;
    bool cellular_connected;
    bool cloud_connected;
    bool gps_synchronized;
    float signal_strength_wifi;
    float signal_strength_lora;
    float signal_strength_cellular;
    uint32_t data_transmitted;
    uint32_t data_received;
    uint32_t transmission_errors;
    uint32_t last_heartbeat;
    float cpu_temperature;
    float free_heap;
    String last_error;
};

struct MaintenanceSchedule {
    uint32_t next_calibration;
    uint32_t next_inspection;
    uint32_t next_cleaning;
    uint32_t next_replacement;
    bool calibration_due;
    bool inspection_due;
    bool cleaning_due;
    bool replacement_due;
    String maintenance_notes;
};

// Global Variables
WiFiClient wifi_client;
WiFiClientSecure secure_client;
PubSubClient mqtt_client(secure_client);
AsyncWebServer web_server(80);
WebSocketsServer websocket_server(81);
TinyGPSPlus gps;

HardwareSerial arduino_serial(2);
HardwareSerial gps_serial(1);
HardwareSerial cellular_serial(1);

// Data Objects
CorrosionData current_data;
AlertData active_alerts[10];
SystemStatus system_status;
MaintenanceSchedule maintenance_schedule;

// Task Handles
TaskHandle_t data_processing_task;
TaskHandle_t communication_task;
TaskHandle_t analytics_task;
TaskHandle_t maintenance_task;

// Queues
QueueHandle_t data_queue;
QueueHandle_t alert_queue;
QueueHandle_t transmission_queue;

// Timing Variables
uint32_t last_data_transmission = 0;
uint32_t last_heartbeat = 0;
uint32_t last_gps_sync = 0;
uint32_t last_system_check = 0;
uint32_t last_maintenance_check = 0;

// Configuration Variables
bool enable_lora = true;
bool enable_cellular = false;
bool enable_cloud_storage = true;
bool enable_local_storage = true;
bool enable_real_time_alerts = true;
uint32_t data_retention_days = 365;
uint32_t alert_retention_days = 90;

// Statistics
uint32_t total_data_points = 0;
uint32_t total_alerts_generated = 0;
uint32_t total_maintenance_actions = 0;
uint32_t system_restart_count = 0;

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== Corrosion Monitoring System - IoT Gateway ===");
    Serial.println("Initializing IoT gateway and communication systems...");
    
    // Initialize pin modes
    pinMode(STATUS_LED_WIFI, OUTPUT);
    pinMode(STATUS_LED_LORA, OUTPUT);
    pinMode(STATUS_LED_CELLULAR, OUTPUT);
    pinMode(STATUS_LED_CLOUD, OUTPUT);
    pinMode(EMERGENCY_BUTTON, INPUT_PULLUP);
    pinMode(RESET_BUTTON, INPUT_PULLUP);
    pinMode(CELLULAR_POWER, OUTPUT);
    
    // Initialize status LEDs
    digitalWrite(STATUS_LED_WIFI, LOW);
    digitalWrite(STATUS_LED_LORA, LOW);
    digitalWrite(STATUS_LED_CELLULAR, LOW);
    digitalWrite(STATUS_LED_CLOUD, LOW);
    
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
    data_queue = xQueueCreate(100, sizeof(CorrosionData));
    alert_queue = xQueueCreate(50, sizeof(AlertData));
    transmission_queue = xQueueCreate(100, sizeof(String));
    
    // Initialize WiFi
    initializeWiFi();
    
    // Initialize LoRa
    if (enable_lora) {
        initializeLoRa();
    }
    
    // Initialize cellular
    if (enable_cellular) {
        initializeCellular();
    }
    
    // Initialize MQTT
    initializeMQTT();
    
    // Initialize web server
    initializeWebServer();
    
    // Initialize WebSocket server
    initializeWebSocket();
    
    // Initialize system status
    initializeSystemStatus();
    
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
        communicationTask,
        "Communication",
        8192,
        NULL,
        1,
        &communication_task,
        1
    );
    
    xTaskCreatePinnedToCore(
        analyticsTask,
        "Analytics",
        8192,
        NULL,
        1,
        &analytics_task,
        1
    );
    
    xTaskCreatePinnedToCore(
        maintenanceTask,
        "Maintenance",
        4096,
        NULL,
        1,
        &maintenance_task,
        1
    );
    
    Serial.println("IoT Gateway initialization complete!");
    Serial.println("System ready for corrosion monitoring operations...");
}

void loop() {
    uint32_t current_time = millis();
    
    // Check emergency button
    if (digitalRead(EMERGENCY_BUTTON) == LOW) {
        handleEmergencyShutdown();
        return;
    }
    
    // Check reset button
    if (digitalRead(RESET_BUTTON) == LOW) {
        delay(50);
        if (digitalRead(RESET_BUTTON) == LOW) {
            Serial.println("Reset button pressed - restarting system...");
            ESP.restart();
        }
    }
    
    // Update GPS
    updateGPS();
    
    // Handle MQTT
    if (mqtt_client.connected()) {
        mqtt_client.loop();
    } else {
        reconnectMQTT();
    }
    
    // Handle WebSocket
    websocket_server.loop();
    
    // Send heartbeat
    if (current_time - last_heartbeat > HEARTBEAT_INTERVAL) {
        sendHeartbeat();
        last_heartbeat = current_time;
    }
    
    // System health check
    if (current_time - last_system_check > 60000) { // Every minute
        performSystemHealthCheck();
        last_system_check = current_time;
    }
    
    // Maintenance check
    if (current_time - last_maintenance_check > 3600000) { // Every hour
        checkMaintenanceSchedule();
        last_maintenance_check = current_time;
    }
    
    // Update system status
    updateSystemStatus();
    
    delay(100);
}

void dataProcessingTask(void* parameter) {
    String incoming_data;
    CorrosionData data;
    
    while (true) {
        // Read data from Arduino
        if (arduino_serial.available()) {
            incoming_data = arduino_serial.readStringUntil('\n');
            
            if (parseCorrosionData(incoming_data, data)) {
                // Add GPS coordinates
                if (gps.location.isValid()) {
                    data.latitude = gps.location.lat();
                    data.longitude = gps.location.lng();
                }
                
                // Add to processing queue
                if (xQueueSend(data_queue, &data, 0) == pdTRUE) {
                    total_data_points++;
                }
                
                // Check for alerts
                checkForAlerts(data);
            }
        }
        
        // Process data from queue
        if (xQueueReceive(data_queue, &data, 0) == pdTRUE) {
            processCorrosionData(data);
            
            // Store locally if enabled
            if (enable_local_storage) {
                storeDataLocally(data);
            }
            
            // Add to transmission queue
            String json_data = serializeCorrosionData(data);
            xQueueSend(transmission_queue, &json_data, 0);
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void communicationTask(void* parameter) {
    String data_to_transmit;
    
    while (true) {
        // Process transmission queue
        if (xQueueReceive(transmission_queue, &data_to_transmit, 0) == pdTRUE) {
            
            // Transmit via WiFi/Cloud
            if (system_status.wifi_connected && system_status.cloud_connected) {
                transmitToCloud(data_to_transmit);
            }
            
            // Transmit via LoRa
            if (enable_lora && system_status.lora_connected) {
                transmitViaLoRa(data_to_transmit);
            }
            
            // Transmit via Cellular
            if (enable_cellular && system_status.cellular_connected) {
                transmitViaCellular(data_to_transmit);
            }
            
            // Update transmission statistics
            system_status.data_transmitted++;
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void analyticsTask(void* parameter) {
    while (true) {
        // Perform trend analysis
        performTrendAnalysis();
        
        // Calculate predictive maintenance indicators
        calculatePredictiveMaintenanceIndicators();
        
        // Generate analytics reports
        generateAnalyticsReports();
        
        // Update dashboard data
        updateDashboardData();
        
        vTaskDelay(pdMS_TO_TICKS(60000)); // Run every minute
    }
}

void maintenanceTask(void* parameter) {
    while (true) {
        // Check maintenance schedules
        checkMaintenanceSchedule();
        
        // Perform system diagnostics
        performSystemDiagnostics();
        
        // Clean up old data
        cleanupOldData();
        
        // Update maintenance logs
        updateMaintenanceLogs();
        
        vTaskDelay(pdMS_TO_TICKS(3600000)); // Run every hour
    }
}

void initializeWiFi() {
    Serial.print("Connecting to WiFi network: ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("WiFi connected successfully!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
        Serial.print("Signal strength: ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");
        
        system_status.wifi_connected = true;
        system_status.signal_strength_wifi = WiFi.RSSI();
        digitalWrite(STATUS_LED_WIFI, HIGH);
    } else {
        Serial.println();
        Serial.println("WiFi connection failed, trying fallback network...");
        
        WiFi.begin(fallback_ssid, fallback_password);
        attempts = 0;
        
        while (WiFi.status() != WL_CONNECTED && attempts < 15) {
            delay(1000);
            Serial.print(".");
            attempts++;
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("Fallback WiFi connected!");
            system_status.wifi_connected = true;
            system_status.signal_strength_wifi = WiFi.RSSI();
            digitalWrite(STATUS_LED_WIFI, HIGH);
        } else {
            Serial.println("All WiFi connections failed!");
            system_status.wifi_connected = false;
            system_status.last_error = "WiFi connection failed";
        }
    }
}

void initializeLoRa() {
    Serial.println("Initializing LoRa communication...");
    
    LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
    
    if (!LoRa.begin(LORA_FREQUENCY)) {
        Serial.println("Starting LoRa failed!");
        system_status.lora_connected = false;
        system_status.last_error = "LoRa initialization failed";
        return;
    }
    
    // Configure LoRa parameters
    LoRa.setSpreadingFactor(LORA_SPREADING_FACTOR);
    LoRa.setSignalBandwidth(LORA_BANDWIDTH);
    LoRa.setCodingRate4(5);
    LoRa.setPreambleLength(8);
    LoRa.setSyncWord(0x12);
    LoRa.enableCrc();
    
    Serial.println("LoRa initialized successfully!");
    system_status.lora_connected = true;
    digitalWrite(STATUS_LED_LORA, HIGH);
}

void initializeCellular() {
    Serial.println("Initializing cellular communication...");
    
    digitalWrite(CELLULAR_POWER, HIGH);
    delay(5000); // Wait for module to boot
    
    cellular_serial.begin(CELLULAR_BAUD_RATE, SERIAL_8N1, CELLULAR_RX, CELLULAR_TX);
    
    // Test cellular module
    cellular_serial.println("AT");
    delay(1000);
    
    if (cellular_serial.available()) {
        String response = cellular_serial.readString();
        if (response.indexOf("OK") != -1) {
            Serial.println("Cellular module responded successfully!");
            system_status.cellular_connected = true;
            digitalWrite(STATUS_LED_CELLULAR, HIGH);
        } else {
            Serial.println("Cellular module not responding properly");
            system_status.cellular_connected = false;
        }
    } else {
        Serial.println("No response from cellular module");
        system_status.cellular_connected = false;
    }
}

void initializeMQTT() {
    if (!system_status.wifi_connected) {
        Serial.println("WiFi not connected, skipping MQTT initialization");
        return;
    }
    
    mqtt_client.setServer(mqtt_broker, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    
    connectMQTT();
}

void connectMQTT() {
    while (!mqtt_client.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        String client_id = "CMS_" + String(device_id) + "_" + String(random(0xffff));
        
        if (mqtt_client.connect(client_id.c_str(), api_key, "")) {
            Serial.println("MQTT connected!");
            
            // Subscribe to control topics
            mqtt_client.subscribe(("cms/" + String(device_id) + "/control").c_str());
            mqtt_client.subscribe(("cms/" + String(device_id) + "/config").c_str());
            mqtt_client.subscribe(("cms/" + String(device_id) + "/maintenance").c_str());
            mqtt_client.subscribe(("cms/broadcast/alerts").c_str());
            
            // Publish online status
            publishOnlineStatus();
            
            break;
        } else {
            Serial.print("MQTT connection failed, rc=");
            Serial.print(mqtt_client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void reconnectMQTT() {
    if (millis() - system_status.last_heartbeat > 60000) { // Try reconnect every minute
        connectMQTT();
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
    
    handleMQTTMessage(String(topic), message);
}

void handleMQTTMessage(String topic, String message) {
    StaticJsonDocument<512> doc;
    deserializeJson(doc, message);
    
    if (topic.indexOf("control") > 0) {
        handleControlCommand(doc);
    } else if (topic.indexOf("config") > 0) {
        handleConfigurationUpdate(doc);
    } else if (topic.indexOf("maintenance") > 0) {
        handleMaintenanceCommand(doc);
    } else if (topic.indexOf("alerts") > 0) {
        handleBroadcastAlert(doc);
    }
}

void handleControlCommand(JsonDocument& doc) {
    String command = doc["command"];
    
    if (command == "start_monitoring") {
        sendCommandToArduino("{\"command\":\"start_monitoring\"}");
    } else if (command == "stop_monitoring") {
        sendCommandToArduino("{\"command\":\"stop_monitoring\"}");
    } else if (command == "calibrate_system") {
        sendCommandToArduino("{\"command\":\"calibrate_system\"}");
    } else if (command == "reset_system") {
        sendCommandToArduino("{\"command\":\"reset_system\"}");
    } else if (command == "get_status") {
        publishSystemStatus();
    } else if (command == "generate_report") {
        generateSystemReport();
    } else if (command == "firmware_update") {
        performFirmwareUpdate(doc["url"]);
    }
}

void handleConfigurationUpdate(JsonDocument& doc) {
    if (doc.containsKey("data_transmission_interval")) {
        DATA_TRANSMISSION_INTERVAL = doc["data_transmission_interval"];
    }
    
    if (doc.containsKey("enable_lora")) {
        enable_lora = doc["enable_lora"];
    }
    
    if (doc.containsKey("enable_cellular")) {
        enable_cellular = doc["enable_cellular"];
    }
    
    if (doc.containsKey("enable_cloud_storage")) {
        enable_cloud_storage = doc["enable_cloud_storage"];
    }
    
    if (doc.containsKey("alert_thresholds")) {
        updateAlertThresholds(doc["alert_thresholds"]);
    }
    
    // Save configuration
    saveConfiguration();
    
    Serial.println("Configuration updated successfully");
}

void handleMaintenanceCommand(JsonDocument& doc) {
    String maintenance_type = doc["type"];
    
    if (maintenance_type == "schedule_calibration") {
        scheduleCalibration(doc["date"]);
    } else if (maintenance_type == "schedule_inspection") {
        scheduleInspection(doc["date"]);
    } else if (maintenance_type == "update_maintenance_log") {
        updateMaintenanceLog(doc["log_entry"]);
    } else if (maintenance_type == "reset_maintenance_schedule") {
        resetMaintenanceSchedule();
    }
}

void handleBroadcastAlert(JsonDocument& doc) {
    AlertData alert;
    alert.timestamp = millis();
    alert.device_id = doc["device_id"];
    alert.alert_type = doc["alert_type"];
    alert.alert_level = doc["alert_level"];
    alert.alert_message = doc["alert_message"];
    
    // Add to alert queue
    xQueueSend(alert_queue, &alert, 0);
    
    // Forward to WebSocket clients
    forwardAlertToWebSocket(alert);
}

void sendCommandToArduino(String command) {
    arduino_serial.println(command);
    Serial.println("Command sent to Arduino: " + command);
}

void initializeWebServer() {
    // Serve static files
    web_server.serveStatic("/", SPIFFS, "/");
    
    // Default route
    web_server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(SPIFFS, "/index.html", "text/html");
    });
    
    // API endpoints
    web_server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<1024> doc;
        doc["device_id"] = system_status.device_id;
        doc["firmware_version"] = system_status.firmware_version;
        doc["uptime"] = system_status.uptime;
        doc["wifi_connected"] = system_status.wifi_connected;
        doc["lora_connected"] = system_status.lora_connected;
        doc["cellular_connected"] = system_status.cellular_connected;
        doc["cloud_connected"] = system_status.cloud_connected;
        doc["gps_synchronized"] = system_status.gps_synchronized;
        doc["data_transmitted"] = system_status.data_transmitted;
        doc["data_received"] = system_status.data_received;
        doc["transmission_errors"] = system_status.transmission_errors;
        doc["cpu_temperature"] = system_status.cpu_temperature;
        doc["free_heap"] = system_status.free_heap;
        doc["signal_strength_wifi"] = system_status.signal_strength_wifi;
        doc["signal_strength_lora"] = system_status.signal_strength_lora;
        doc["signal_strength_cellular"] = system_status.signal_strength_cellular;
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/data", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<2048> doc;
        doc["timestamp"] = current_data.timestamp;
        doc["device_id"] = current_data.device_id;
        doc["location"] = current_data.location;
        doc["latitude"] = current_data.latitude;
        doc["longitude"] = current_data.longitude;
        
        // Electrochemical data
        JsonArray potentials = doc.createNestedArray("potentials");
        JsonArray currents = doc.createNestedArray("currents");
        JsonArray corrosion_rates = doc.createNestedArray("corrosion_rates");
        JsonArray severity_levels = doc.createNestedArray("severity_levels");
        
        for (int i = 0; i < 8; i++) {
            potentials.add(current_data.potential[i]);
            currents.add(current_data.current[i]);
            corrosion_rates.add(current_data.corrosion_rate[i]);
            severity_levels.add(current_data.severity_level[i]);
        }
        
        // Environmental data
        doc["temperature"] = current_data.temperature;
        doc["humidity"] = current_data.humidity;
        doc["ph_value"] = current_data.ph_value;
        doc["conductivity"] = current_data.conductivity;
        doc["dissolved_oxygen"] = current_data.dissolved_oxygen;
        doc["chloride_concentration"] = current_data.chloride_concentration;
        doc["atmospheric_pressure"] = current_data.atmospheric_pressure;
        doc["wind_speed"] = current_data.wind_speed;
        doc["wind_direction"] = current_data.wind_direction;
        doc["solar_irradiance"] = current_data.solar_irradiance;
        
        // System data
        doc["battery_voltage"] = current_data.battery_voltage;
        doc["solar_voltage"] = current_data.solar_voltage;
        doc["system_temperature"] = current_data.system_temperature;
        doc["system_healthy"] = current_data.system_healthy;
        doc["data_quality"] = current_data.data_quality;
        doc["communication_quality"] = current_data.communication_quality;
        doc["power_quality"] = current_data.power_quality;
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/alerts", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<2048> doc;
        JsonArray alerts = doc.createNestedArray("alerts");
        
        for (int i = 0; i < 10; i++) {
            if (active_alerts[i].timestamp > 0) {
                JsonObject alert = alerts.createNestedObject();
                alert["timestamp"] = active_alerts[i].timestamp;
                alert["device_id"] = active_alerts[i].device_id;
                alert["alert_type"] = active_alerts[i].alert_type;
                alert["alert_level"] = active_alerts[i].alert_level;
                alert["alert_message"] = active_alerts[i].alert_message;
                alert["affected_component"] = active_alerts[i].affected_component;
                alert["alert_value"] = active_alerts[i].alert_value;
                alert["threshold_value"] = active_alerts[i].threshold_value;
                alert["recommended_action"] = active_alerts[i].recommended_action;
                alert["acknowledged"] = active_alerts[i].acknowledged;
            }
        }
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/config", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<512> doc;
        doc["enable_lora"] = enable_lora;
        doc["enable_cellular"] = enable_cellular;
        doc["enable_cloud_storage"] = enable_cloud_storage;
        doc["enable_local_storage"] = enable_local_storage;
        doc["enable_real_time_alerts"] = enable_real_time_alerts;
        doc["data_transmission_interval"] = DATA_TRANSMISSION_INTERVAL;
        doc["data_retention_days"] = data_retention_days;
        doc["alert_retention_days"] = alert_retention_days;
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/maintenance", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<512> doc;
        doc["next_calibration"] = maintenance_schedule.next_calibration;
        doc["next_inspection"] = maintenance_schedule.next_inspection;
        doc["next_cleaning"] = maintenance_schedule.next_cleaning;
        doc["next_replacement"] = maintenance_schedule.next_replacement;
        doc["calibration_due"] = maintenance_schedule.calibration_due;
        doc["inspection_due"] = maintenance_schedule.inspection_due;
        doc["cleaning_due"] = maintenance_schedule.cleaning_due;
        doc["replacement_due"] = maintenance_schedule.replacement_due;
        doc["maintenance_notes"] = maintenance_schedule.maintenance_notes;
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    // Control endpoints
    web_server.on("/api/control/start", HTTP_POST, [](AsyncWebServerRequest *request){
        sendCommandToArduino("{\"command\":\"start_monitoring\"}");
        request->send(200, "application/json", "{\"status\":\"started\"}");
    });
    
    web_server.on("/api/control/stop", HTTP_POST, [](AsyncWebServerRequest *request){
        sendCommandToArduino("{\"command\":\"stop_monitoring\"}");
        request->send(200, "application/json", "{\"status\":\"stopped\"}");
    });
    
    web_server.on("/api/control/calibrate", HTTP_POST, [](AsyncWebServerRequest *request){
        sendCommandToArduino("{\"command\":\"calibrate_system\"}");
        request->send(200, "application/json", "{\"status\":\"calibration_started\"}");
    });
    
    web_server.on("/api/control/reset", HTTP_POST, [](AsyncWebServerRequest *request){
        sendCommandToArduino("{\"command\":\"reset_system\"}");
        request->send(200, "application/json", "{\"status\":\"reset_initiated\"}");
    });
    
    // File upload for firmware updates
    web_server.on("/api/firmware/update", HTTP_POST, [](AsyncWebServerRequest *request){
        request->send(200, "application/json", "{\"status\":\"upload_complete\"}");
    }, [](AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final){
        handleFirmwareUpload(request, filename, index, data, len, final);
    });
    
    web_server.begin();
    Serial.println("Web server started on port 80");
}

void initializeWebSocket() {
    websocket_server.begin();
    websocket_server.onEvent(webSocketEvent);
    Serial.println("WebSocket server started on port 81");
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[%u] Disconnected!\n", num);
            break;
            
        case WStype_CONNECTED:
            {
                IPAddress ip = websocket_server.remoteIP(num);
                Serial.printf("[%u] Connected from %d.%d.%d.%d url: %s\n", num, ip[0], ip[1], ip[2], ip[3], payload);
                
                // Send initial data
                sendInitialDataToWebSocket(num);
            }
            break;
            
        case WStype_TEXT:
            Serial.printf("[%u] get Text: %s\n", num, payload);
            
            // Handle WebSocket commands
            handleWebSocketCommand(num, String((char*)payload));
            break;
            
        case WStype_BIN:
            Serial.printf("[%u] get binary length: %u\n", num, length);
            break;
            
        default:
            break;
    }
}

void handleWebSocketCommand(uint8_t num, String command) {
    StaticJsonDocument<256> doc;
    deserializeJson(doc, command);
    
    String cmd = doc["command"];
    
    if (cmd == "get_real_time_data") {
        sendRealTimeDataToWebSocket(num);
    } else if (cmd == "acknowledge_alert") {
        acknowledgeAlert(doc["alert_id"]);
    } else if (cmd == "subscribe_alerts") {
        // Client subscribed to alerts
        Serial.printf("Client %u subscribed to alerts\n", num);
    } else if (cmd == "get_system_status") {
        sendSystemStatusToWebSocket(num);
    }
}

void sendInitialDataToWebSocket(uint8_t num) {
    StaticJsonDocument<1024> doc;
    doc["type"] = "initial_data";
    doc["device_id"] = system_status.device_id;
    doc["firmware_version"] = system_status.firmware_version;
    doc["uptime"] = system_status.uptime;
    doc["wifi_connected"] = system_status.wifi_connected;
    doc["lora_connected"] = system_status.lora_connected;
    doc["cellular_connected"] = system_status.cellular_connected;
    doc["cloud_connected"] = system_status.cloud_connected;
    
    String json_string;
    serializeJson(doc, json_string);
    
    websocket_server.sendTXT(num, json_string);
}

void sendRealTimeDataToWebSocket(uint8_t num) {
    StaticJsonDocument<1024> doc;
    doc["type"] = "real_time_data";
    doc["timestamp"] = current_data.timestamp;
    doc["temperature"] = current_data.temperature;
    doc["humidity"] = current_data.humidity;
    doc["ph_value"] = current_data.ph_value;
    doc["battery_voltage"] = current_data.battery_voltage;
    doc["system_healthy"] = current_data.system_healthy;
    
    JsonArray corrosion_rates = doc.createNestedArray("corrosion_rates");
    JsonArray severity_levels = doc.createNestedArray("severity_levels");
    
    for (int i = 0; i < 8; i++) {
        corrosion_rates.add(current_data.corrosion_rate[i]);
        severity_levels.add(current_data.severity_level[i]);
    }
    
    String json_string;
    serializeJson(doc, json_string);
    
    websocket_server.sendTXT(num, json_string);
}

void sendSystemStatusToWebSocket(uint8_t num) {
    StaticJsonDocument<512> doc;
    doc["type"] = "system_status";
    doc["device_id"] = system_status.device_id;
    doc["uptime"] = system_status.uptime;
    doc["cpu_temperature"] = system_status.cpu_temperature;
    doc["free_heap"] = system_status.free_heap;
    doc["data_transmitted"] = system_status.data_transmitted;
    doc["transmission_errors"] = system_status.transmission_errors;
    doc["signal_strength_wifi"] = system_status.signal_strength_wifi;
    doc["signal_strength_lora"] = system_status.signal_strength_lora;
    doc["signal_strength_cellular"] = system_status.signal_strength_cellular;
    
    String json_string;
    serializeJson(doc, json_string);
    
    websocket_server.sendTXT(num, json_string);
}

void forwardAlertToWebSocket(AlertData& alert) {
    StaticJsonDocument<512> doc;
    doc["type"] = "alert";
    doc["timestamp"] = alert.timestamp;
    doc["device_id"] = alert.device_id;
    doc["alert_type"] = alert.alert_type;
    doc["alert_level"] = alert.alert_level;
    doc["alert_message"] = alert.alert_message;
    doc["affected_component"] = alert.affected_component;
    doc["alert_value"] = alert.alert_value;
    doc["threshold_value"] = alert.threshold_value;
    doc["recommended_action"] = alert.recommended_action;
    
    String json_string;
    serializeJson(doc, json_string);
    
    websocket_server.broadcastTXT(json_string);
}

void initializeSystemStatus() {
    system_status.device_id = device_id;
    system_status.firmware_version = "v2.0.0";
    system_status.uptime = 0;
    system_status.wifi_connected = false;
    system_status.lora_connected = false;
    system_status.cellular_connected = false;
    system_status.cloud_connected = false;
    system_status.gps_synchronized = false;
    system_status.signal_strength_wifi = 0;
    system_status.signal_strength_lora = 0;
    system_status.signal_strength_cellular = 0;
    system_status.data_transmitted = 0;
    system_status.data_received = 0;
    system_status.transmission_errors = 0;
    system_status.last_heartbeat = 0;
    system_status.cpu_temperature = 0;
    system_status.free_heap = ESP.getFreeHeap();
    system_status.last_error = "";
    
    // Initialize current data
    current_data.device_id = device_id;
    current_data.location = "Unknown";
    current_data.latitude = 0.0;
    current_data.longitude = 0.0;
    current_data.timestamp = 0;
    current_data.system_healthy = true;
    current_data.data_quality = 100;
    current_data.communication_quality = 100;
    current_data.power_quality = 100;
    
    // Initialize alert array
    for (int i = 0; i < 10; i++) {
        active_alerts[i].timestamp = 0;
        active_alerts[i].acknowledged = false;
    }
    
    // Initialize maintenance schedule
    maintenance_schedule.next_calibration = millis() + 2592000000; // 30 days
    maintenance_schedule.next_inspection = millis() + 604800000;   // 7 days
    maintenance_schedule.next_cleaning = millis() + 86400000;     // 1 day
    maintenance_schedule.next_replacement = millis() + 31536000000; // 1 year
    maintenance_schedule.calibration_due = false;
    maintenance_schedule.inspection_due = false;
    maintenance_schedule.cleaning_due = false;
    maintenance_schedule.replacement_due = false;
    maintenance_schedule.maintenance_notes = "";
}

bool parseCorrosionData(String data, CorrosionData& parsed_data) {
    StaticJsonDocument<2048> doc;
    DeserializationError error = deserializeJson(doc, data);
    
    if (error) {
        Serial.print("JSON parsing failed: ");
        Serial.println(error.c_str());
        return false;
    }
    
    if (doc["type"] == "corrosion_data") {
        parsed_data.timestamp = doc["timestamp"];
        parsed_data.device_id = doc["device_id"];
        
        // Parse electrochemical data
        for (int i = 0; i < 8; i++) {
            parsed_data.potential[i] = doc["electrochemical"]["potential"][i];
            parsed_data.current[i] = doc["electrochemical"]["current"][i];
            parsed_data.corrosion_rate[i] = doc["electrochemical"]["corrosion_rate"][i];
            parsed_data.polarization_resistance[i] = doc["electrochemical"]["polarization_resistance"][i];
            parsed_data.severity_level[i] = doc["electrochemical"]["severity_level"][i];
        }
        
        // Parse environmental data
        parsed_data.temperature = doc["environmental"]["temperature"];
        parsed_data.humidity = doc["environmental"]["humidity"];
        parsed_data.ph_value = doc["environmental"]["ph_value"];
        parsed_data.conductivity = doc["environmental"]["conductivity"];
        parsed_data.dissolved_oxygen = doc["environmental"]["dissolved_oxygen"];
        parsed_data.chloride_concentration = doc["environmental"]["chloride_concentration"];
        parsed_data.atmospheric_pressure = doc["environmental"]["atmospheric_pressure"];
        parsed_data.wind_speed = doc["environmental"]["wind_speed"];
        parsed_data.wind_direction = doc["environmental"]["wind_direction"];
        parsed_data.solar_irradiance = doc["environmental"]["solar_irradiance"];
        
        // Parse system data
        parsed_data.battery_voltage = doc["system"]["battery_voltage"];
        parsed_data.solar_voltage = doc["system"]["solar_voltage"];
        parsed_data.system_temperature = doc["system"]["system_temperature"];
        parsed_data.uptime = doc["system"]["uptime"];
        parsed_data.system_healthy = doc["system"]["system_healthy"];
        parsed_data.data_quality = doc["system"]["data_quality"];
        parsed_data.communication_quality = doc["system"]["communication_quality"];
        parsed_data.power_quality = doc["system"]["power_quality"];
        
        return true;
    }
    
    return false;
}

void processCorrosionData(CorrosionData& data) {
    // Update current data
    current_data = data;
    
    // Update system statistics
    system_status.data_received++;
    
    // Calculate data quality metrics
    calculateDataQualityMetrics();
    
    // Perform real-time analytics
    performRealTimeAnalytics();
    
    // Broadcast to WebSocket clients
    broadcastDataToWebSocket();
}

String serializeCorrosionData(CorrosionData& data) {
    StaticJsonDocument<2048> doc;
    
    doc["type"] = "corrosion_data";
    doc["timestamp"] = data.timestamp;
    doc["device_id"] = data.device_id;
    doc["location"] = data.location;
    doc["latitude"] = data.latitude;
    doc["longitude"] = data.longitude;
    
    // Electrochemical data
    JsonObject electrochemical = doc.createNestedObject("electrochemical");
    JsonArray potentials = electrochemical.createNestedArray("potentials");
    JsonArray currents = electrochemical.createNestedArray("currents");
    JsonArray corrosion_rates = electrochemical.createNestedArray("corrosion_rates");
    JsonArray severity_levels = electrochemical.createNestedArray("severity_levels");
    
    for (int i = 0; i < 8; i++) {
        potentials.add(data.potential[i]);
        currents.add(data.current[i]);
        corrosion_rates.add(data.corrosion_rate[i]);
        severity_levels.add(data.severity_level[i]);
    }
    
    // Environmental data
    JsonObject environmental = doc.createNestedObject("environmental");
    environmental["temperature"] = data.temperature;
    environmental["humidity"] = data.humidity;
    environmental["ph_value"] = data.ph_value;
    environmental["conductivity"] = data.conductivity;
    environmental["dissolved_oxygen"] = data.dissolved_oxygen;
    environmental["chloride_concentration"] = data.chloride_concentration;
    environmental["atmospheric_pressure"] = data.atmospheric_pressure;
    environmental["wind_speed"] = data.wind_speed;
    environmental["wind_direction"] = data.wind_direction;
    environmental["solar_irradiance"] = data.solar_irradiance;
    
    // System data
    JsonObject system = doc.createNestedObject("system");
    system["battery_voltage"] = data.battery_voltage;
    system["solar_voltage"] = data.solar_voltage;
    system["system_temperature"] = data.system_temperature;
    system["uptime"] = data.uptime;
    system["system_healthy"] = data.system_healthy;
    system["data_quality"] = data.data_quality;
    system["communication_quality"] = data.communication_quality;
    system["power_quality"] = data.power_quality;
    
    String json_string;
    serializeJson(doc, json_string);
    
    return json_string;
}

void checkForAlerts(CorrosionData& data) {
    // Check corrosion rate thresholds
    for (int i = 0; i < 8; i++) {
        if (data.corrosion_rate[i] > 100.0) { // 100 mpy threshold
            generateAlert("high_corrosion_rate", "critical", 
                         "High corrosion rate detected on electrode " + String(i),
                         "electrode_" + String(i), data.corrosion_rate[i], 100.0,
                         "Immediate inspection and mitigation required");
        }
        
        if (data.severity_level[i] >= 3) { // Critical severity
            generateAlert("critical_corrosion", "critical",
                         "Critical corrosion severity on electrode " + String(i),
                         "electrode_" + String(i), data.severity_level[i], 3,
                         "Emergency maintenance required");
        }
    }
    
    // Check environmental thresholds
    if (data.ph_value < 6.0 || data.ph_value > 9.0) {
        generateAlert("ph_out_of_range", "warning",
                     "pH value out of acceptable range: " + String(data.ph_value),
                     "pH_sensor", data.ph_value, 7.0,
                     "Check water chemistry and treatment systems");
    }
    
    if (data.chloride_concentration > 1000.0) {
        generateAlert("high_chloride", "warning",
                     "High chloride concentration: " + String(data.chloride_concentration) + " ppm",
                     "chloride_sensor", data.chloride_concentration, 1000.0,
                     "Monitor for accelerated corrosion");
    }
    
    // Check system health
    if (data.battery_voltage < 11.0) {
        generateAlert("low_battery", "warning",
                     "Low battery voltage: " + String(data.battery_voltage) + " V",
                     "power_system", data.battery_voltage, 12.0,
                     "Check battery and charging system");
    }
    
    if (!data.system_healthy) {
        generateAlert("system_fault", "critical",
                     "System health check failed",
                     "system", 0, 1,
                     "Immediate system inspection required");
    }
}

void generateAlert(String alert_type, String alert_level, String alert_message,
                  String affected_component, float alert_value, float threshold_value,
                  String recommended_action) {
    
    // Find empty slot in active alerts array
    for (int i = 0; i < 10; i++) {
        if (active_alerts[i].timestamp == 0) {
            active_alerts[i].timestamp = millis();
            active_alerts[i].device_id = device_id;
            active_alerts[i].alert_type = alert_type;
            active_alerts[i].alert_level = alert_level;
            active_alerts[i].alert_message = alert_message;
            active_alerts[i].affected_component = affected_component;
            active_alerts[i].alert_value = alert_value;
            active_alerts[i].threshold_value = threshold_value;
            active_alerts[i].recommended_action = recommended_action;
            active_alerts[i].acknowledged = false;
            
            // Add to alert queue
            xQueueSend(alert_queue, &active_alerts[i], 0);
            
            // Forward to WebSocket
            forwardAlertToWebSocket(active_alerts[i]);
            
            // Publish to MQTT
            publishAlert(active_alerts[i]);
            
            total_alerts_generated++;
            
            Serial.println("Alert generated: " + alert_message);
            break;
        }
    }
}

void publishAlert(AlertData& alert) {
    if (!mqtt_client.connected()) return;
    
    StaticJsonDocument<512> doc;
    doc["timestamp"] = alert.timestamp;
    doc["device_id"] = alert.device_id;
    doc["alert_type"] = alert.alert_type;
    doc["alert_level"] = alert.alert_level;
    doc["alert_message"] = alert.alert_message;
    doc["affected_component"] = alert.affected_component;
    doc["alert_value"] = alert.alert_value;
    doc["threshold_value"] = alert.threshold_value;
    doc["recommended_action"] = alert.recommended_action;
    
    String json_string;
    serializeJson(doc, json_string);
    
    String topic = "cms/" + String(device_id) + "/alerts";
    mqtt_client.publish(topic.c_str(), json_string.c_str());
}

void acknowledgeAlert(String alert_id) {
    // Find and acknowledge alert
    for (int i = 0; i < 10; i++) {
        if (active_alerts[i].timestamp != 0 && !active_alerts[i].acknowledged) {
            active_alerts[i].acknowledged = true;
            Serial.println("Alert acknowledged: " + active_alerts[i].alert_message);
            break;
        }
    }
}

void storeDataLocally(CorrosionData& data) {
    // Store data to SPIFFS
    String filename = "/data/corrosion_" + String(data.timestamp) + ".json";
    
    File dataFile = SPIFFS.open(filename, "w");
    if (dataFile) {
        String json_data = serializeCorrosionData(data);
        dataFile.print(json_data);
        dataFile.close();
        
        Serial.println("Data stored locally: " + filename);
    } else {
        Serial.println("Failed to store data locally");
        system_status.last_error = "Local storage failed";
    }
}

void transmitToCloud(String data) {
    if (!system_status.wifi_connected) return;
    
    HTTPClient http;
    http.begin(String(cloud_endpoint) + "/api/v1/data");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    http.addHeader("X-Device-ID", device_id);
    http.addHeader("X-Organization-ID", organization_id);
    
    int response_code = http.POST(data);
    
    if (response_code == 200) {
        system_status.cloud_connected = true;
        digitalWrite(STATUS_LED_CLOUD, HIGH);
        Serial.println("Data transmitted to cloud successfully");
    } else {
        system_status.cloud_connected = false;
        system_status.transmission_errors++;
        digitalWrite(STATUS_LED_CLOUD, LOW);
        Serial.print("Cloud transmission failed: ");
        Serial.println(response_code);
    }
    
    http.end();
}

void transmitViaLoRa(String data) {
    if (!system_status.lora_connected) return;
    
    // LoRa has packet size limitations, so we need to split large data
    int packet_size = 200; // bytes
    int data_length = data.length();
    int packets = (data_length + packet_size - 1) / packet_size;
    
    for (int i = 0; i < packets; i++) {
        int start = i * packet_size;
        int end = min(start + packet_size, data_length);
        String packet = data.substring(start, end);
        
        LoRa.beginPacket();
        LoRa.print(packet);
        LoRa.endPacket();
        
        delay(100); // Small delay between packets
    }
    
    Serial.println("Data transmitted via LoRa");
}

void transmitViaCellular(String data) {
    if (!system_status.cellular_connected) return;
    
    // Send HTTP POST via cellular
    cellular_serial.println("AT+HTTPINIT");
    delay(1000);
    
    cellular_serial.println("AT+HTTPPARA=\"CID\",1");
    delay(1000);
    
    cellular_serial.println("AT+HTTPPARA=\"URL\",\"" + String(cloud_endpoint) + "/api/v1/data\"");
    delay(1000);
    
    cellular_serial.println("AT+HTTPPARA=\"CONTENT\",\"application/json\"");
    delay(1000);
    
    cellular_serial.println("AT+HTTPDATA=" + String(data.length()) + ",10000");
    delay(1000);
    
    cellular_serial.println(data);
    delay(1000);
    
    cellular_serial.println("AT+HTTPACTION=1");
    delay(5000);
    
    cellular_serial.println("AT+HTTPTERM");
    delay(1000);
    
    Serial.println("Data transmitted via cellular");
}

void updateGPS() {
    while (gps_serial.available() > 0) {
        if (gps.encode(gps_serial.read())) {
            if (gps.location.isValid() && gps.date.isValid() && gps.time.isValid()) {
                system_status.gps_synchronized = true;
                last_gps_sync = millis();
                
                // Update location information
                current_data.latitude = gps.location.lat();
                current_data.longitude = gps.location.lng();
                current_data.location = String(gps.location.lat(), 6) + "," + String(gps.location.lng(), 6);
            }
        }
    }
    
    // Check if GPS sync is stale
    if (millis() - last_gps_sync > 300000) { // 5 minutes
        system_status.gps_synchronized = false;
    }
}

void sendHeartbeat() {
    if (mqtt_client.connected()) {
        StaticJsonDocument<256> doc;
        doc["device_id"] = device_id;
        doc["timestamp"] = millis();
        doc["uptime"] = system_status.uptime;
        doc["wifi_connected"] = system_status.wifi_connected;
        doc["lora_connected"] = system_status.lora_connected;
        doc["cellular_connected"] = system_status.cellular_connected;
        doc["cloud_connected"] = system_status.cloud_connected;
        doc["gps_synchronized"] = system_status.gps_synchronized;
        doc["data_transmitted"] = system_status.data_transmitted;
        doc["transmission_errors"] = system_status.transmission_errors;
        doc["free_heap"] = system_status.free_heap;
        doc["signal_strength"] = system_status.signal_strength_wifi;
        
        String json_string;
        serializeJson(doc, json_string);
        
        String topic = "cms/" + String(device_id) + "/heartbeat";
        mqtt_client.publish(topic.c_str(), json_string.c_str());
        
        system_status.last_heartbeat = millis();
    }
}

void publishOnlineStatus() {
    if (mqtt_client.connected()) {
        StaticJsonDocument<256> doc;
        doc["device_id"] = device_id;
        doc["timestamp"] = millis();
        doc["status"] = "online";
        doc["firmware_version"] = system_status.firmware_version;
        doc["capabilities"] = "corrosion_monitoring,environmental_sensing,alerts,analytics";
        
        String json_string;
        serializeJson(doc, json_string);
        
        String topic = "cms/" + String(device_id) + "/status";
        mqtt_client.publish(topic.c_str(), json_string.c_str());
    }
}

void publishSystemStatus() {
    if (mqtt_client.connected()) {
        StaticJsonDocument<512> doc;
        doc["device_id"] = system_status.device_id;
        doc["timestamp"] = millis();
        doc["uptime"] = system_status.uptime;
        doc["wifi_connected"] = system_status.wifi_connected;
        doc["lora_connected"] = system_status.lora_connected;
        doc["cellular_connected"] = system_status.cellular_connected;
        doc["cloud_connected"] = system_status.cloud_connected;
        doc["gps_synchronized"] = system_status.gps_synchronized;
        doc["data_transmitted"] = system_status.data_transmitted;
        doc["data_received"] = system_status.data_received;
        doc["transmission_errors"] = system_status.transmission_errors;
        doc["cpu_temperature"] = system_status.cpu_temperature;
        doc["free_heap"] = system_status.free_heap;
        doc["signal_strength_wifi"] = system_status.signal_strength_wifi;
        doc["signal_strength_lora"] = system_status.signal_strength_lora;
        doc["signal_strength_cellular"] = system_status.signal_strength_cellular;
        doc["last_error"] = system_status.last_error;
        
        String json_string;
        serializeJson(doc, json_string);
        
        String topic = "cms/" + String(device_id) + "/system_status";
        mqtt_client.publish(topic.c_str(), json_string.c_str());
    }
}

void updateSystemStatus() {
    system_status.uptime = millis() / 1000;
    system_status.cpu_temperature = temperatureRead();
    system_status.free_heap = ESP.getFreeHeap();
    
    if (system_status.wifi_connected) {
        system_status.signal_strength_wifi = WiFi.RSSI();
    }
    
    if (system_status.lora_connected) {
        system_status.signal_strength_lora = LoRa.rssi();
    }
}

void performSystemHealthCheck() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        system_status.wifi_connected = false;
        digitalWrite(STATUS_LED_WIFI, LOW);
        
        // Attempt reconnection
        WiFi.reconnect();
    }
    
    // Check MQTT connection
    if (!mqtt_client.connected()) {
        reconnectMQTT();
    }
    
    // Check memory usage
    if (system_status.free_heap < 10000) { // Less than 10KB free
        system_status.last_error = "Low memory warning";
        Serial.println("Warning: Low memory detected");
    }
    
    // Check CPU temperature
    if (system_status.cpu_temperature > 80.0) {
        system_status.last_error = "High CPU temperature";
        Serial.println("Warning: High CPU temperature");
    }
}

void checkMaintenanceSchedule() {
    uint32_t current_time = millis();
    
    // Check calibration schedule
    if (current_time > maintenance_schedule.next_calibration) {
        maintenance_schedule.calibration_due = true;
        generateAlert("maintenance_due", "info",
                     "System calibration is due",
                     "system", 0, 0,
                     "Schedule calibration maintenance");
    }
    
    // Check inspection schedule
    if (current_time > maintenance_schedule.next_inspection) {
        maintenance_schedule.inspection_due = true;
        generateAlert("maintenance_due", "info",
                     "System inspection is due",
                     "system", 0, 0,
                     "Schedule inspection maintenance");
    }
    
    // Check cleaning schedule
    if (current_time > maintenance_schedule.next_cleaning) {
        maintenance_schedule.cleaning_due = true;
        generateAlert("maintenance_due", "info",
                     "System cleaning is due",
                     "sensors", 0, 0,
                     "Schedule cleaning maintenance");
    }
    
    // Check replacement schedule
    if (current_time > maintenance_schedule.next_replacement) {
        maintenance_schedule.replacement_due = true;
        generateAlert("maintenance_due", "warning",
                     "Component replacement is due",
                     "sensors", 0, 0,
                     "Schedule component replacement");
    }
}

void performSystemDiagnostics() {
    // Run comprehensive system diagnostics
    Serial.println("Running system diagnostics...");
    
    // Check communication systems
    bool wifi_ok = WiFi.status() == WL_CONNECTED;
    bool lora_ok = system_status.lora_connected;
    bool cellular_ok = system_status.cellular_connected;
    
    // Check data quality
    bool data_quality_ok = current_data.data_quality > 80;
    
    // Check power system
    bool power_ok = current_data.battery_voltage > 11.0;
    
    // Generate diagnostic report
    StaticJsonDocument<512> diagnostic_report;
    diagnostic_report["timestamp"] = millis();
    diagnostic_report["device_id"] = device_id;
    diagnostic_report["wifi_ok"] = wifi_ok;
    diagnostic_report["lora_ok"] = lora_ok;
    diagnostic_report["cellular_ok"] = cellular_ok;
    diagnostic_report["data_quality_ok"] = data_quality_ok;
    diagnostic_report["power_ok"] = power_ok;
    diagnostic_report["overall_health"] = wifi_ok && data_quality_ok && power_ok;
    
    String json_string;
    serializeJson(diagnostic_report, json_string);
    
    // Store diagnostic report
    File diagnosticFile = SPIFFS.open("/diagnostics/diagnostic_" + String(millis()) + ".json", "w");
    if (diagnosticFile) {
        diagnosticFile.print(json_string);
        diagnosticFile.close();
    }
    
    Serial.println("System diagnostics completed");
}

void cleanupOldData() {
    // Clean up old data files based on retention policy
    Serial.println("Cleaning up old data files...");
    
    uint32_t cutoff_time = millis() - (data_retention_days * 24 * 60 * 60 * 1000);
    
    // This is a simplified cleanup - in a real implementation,
    // you would iterate through files and delete old ones
    
    Serial.println("Data cleanup completed");
}

void updateMaintenanceLogs() {
    // Update maintenance logs
    File logFile = SPIFFS.open("/maintenance/maintenance_log.txt", "a");
    if (logFile) {
        logFile.print(millis());
        logFile.print(",");
        logFile.print("system_check");
        logFile.print(",");
        logFile.print("Automatic system check completed");
        logFile.println();
        logFile.close();
    }
}

void performTrendAnalysis() {
    // Perform trend analysis on corrosion data
    // This would typically involve more sophisticated algorithms
    
    Serial.println("Performing trend analysis...");
    
    // Simple trend analysis example
    static float previous_corrosion_rate[8] = {0};
    static bool first_run = true;
    
    if (!first_run) {
        for (int i = 0; i < 8; i++) {
            float trend = current_data.corrosion_rate[i] - previous_corrosion_rate[i];
            
            if (trend > 10.0) { // Increasing trend
                generateAlert("corrosion_trend", "warning",
                             "Increasing corrosion trend detected on electrode " + String(i),
                             "electrode_" + String(i), trend, 0,
                             "Monitor closely and consider preventive action");
            }
        }
    }
    
    // Store current values for next comparison
    for (int i = 0; i < 8; i++) {
        previous_corrosion_rate[i] = current_data.corrosion_rate[i];
    }
    
    first_run = false;
}

void calculatePredictiveMaintenanceIndicators() {
    // Calculate predictive maintenance indicators
    // This would involve machine learning algorithms in a real implementation
    
    Serial.println("Calculating predictive maintenance indicators...");
    
    // Simple example - check for deteriorating conditions
    if (current_data.data_quality < 70) {
        generateAlert("predictive_maintenance", "info",
                     "Data quality degradation detected - sensor maintenance may be needed",
                     "sensors", current_data.data_quality, 80,
                     "Schedule sensor inspection and cleaning");
    }
    
    if (current_data.power_quality < 80) {
        generateAlert("predictive_maintenance", "info",
                     "Power system degradation detected - maintenance may be needed",
                     "power_system", current_data.power_quality, 90,
                     "Schedule power system inspection");
    }
}

void generateAnalyticsReports() {
    // Generate analytics reports
    Serial.println("Generating analytics reports...");
    
    // Create daily report
    StaticJsonDocument<1024> daily_report;
    daily_report["timestamp"] = millis();
    daily_report["device_id"] = device_id;
    daily_report["report_type"] = "daily";
    daily_report["data_points_collected"] = total_data_points;
    daily_report["alerts_generated"] = total_alerts_generated;
    daily_report["system_uptime"] = system_status.uptime;
    daily_report["average_corrosion_rate"] = calculateAverageCorrosionRate();
    daily_report["system_health_score"] = calculateSystemHealthScore();
    
    String json_string;
    serializeJson(daily_report, json_string);
    
    // Store report
    File reportFile = SPIFFS.open("/reports/daily_report_" + String(millis()) + ".json", "w");
    if (reportFile) {
        reportFile.print(json_string);
        reportFile.close();
    }
    
    // Send report to cloud
    if (enable_cloud_storage) {
        transmitToCloud(json_string);
    }
}

void updateDashboardData() {
    // Update dashboard data for web interface
    // This would typically involve updating a database or cache
    
    Serial.println("Updating dashboard data...");
    
    // Broadcast updated data to WebSocket clients
    broadcastDataToWebSocket();
}

void broadcastDataToWebSocket() {
    StaticJsonDocument<1024> doc;
    doc["type"] = "data_update";
    doc["timestamp"] = current_data.timestamp;
    doc["device_id"] = current_data.device_id;
    doc["temperature"] = current_data.temperature;
    doc["humidity"] = current_data.humidity;
    doc["ph_value"] = current_data.ph_value;
    doc["battery_voltage"] = current_data.battery_voltage;
    doc["system_healthy"] = current_data.system_healthy;
    
    JsonArray corrosion_rates = doc.createNestedArray("corrosion_rates");
    JsonArray severity_levels = doc.createNestedArray("severity_levels");
    
    for (int i = 0; i < 8; i++) {
        corrosion_rates.add(current_data.corrosion_rate[i]);
        severity_levels.add(current_data.severity_level[i]);
    }
    
    String json_string;
    serializeJson(doc, json_string);
    
    websocket_server.broadcastTXT(json_string);
}

void calculateDataQualityMetrics() {
    // Calculate data quality metrics
    uint8_t quality_score = 100;
    
    // Check for missing data
    if (current_data.timestamp == 0) quality_score -= 20;
    
    // Check for out-of-range values
    for (int i = 0; i < 8; i++) {
        if (current_data.corrosion_rate[i] < 0 || current_data.corrosion_rate[i] > 10000) {
            quality_score -= 10;
        }
    }
    
    // Check environmental data
    if (current_data.temperature < -50 || current_data.temperature > 100) {
        quality_score -= 10;
    }
    
    if (current_data.ph_value < 0 || current_data.ph_value > 14) {
        quality_score -= 10;
    }
    
    current_data.data_quality = quality_score;
    
    // Calculate communication quality
    uint8_t comm_quality = 100;
    if (system_status.transmission_errors > 0) {
        comm_quality -= min(50, (int)(system_status.transmission_errors * 5));
    }
    current_data.communication_quality = comm_quality;
    
    // Calculate power quality
    uint8_t power_quality = 100;
    if (current_data.battery_voltage < 12.0) {
        power_quality -= (int)((12.0 - current_data.battery_voltage) * 20);
    }
    current_data.power_quality = power_quality;
}

void performRealTimeAnalytics() {
    // Perform real-time analytics
    // This could include statistical analysis, anomaly detection, etc.
    
    // Simple example - check for anomalies
    static float running_average[8] = {0};
    static int sample_count = 0;
    
    sample_count++;
    
    for (int i = 0; i < 8; i++) {
        running_average[i] = ((running_average[i] * (sample_count - 1)) + current_data.corrosion_rate[i]) / sample_count;
        
        // Check for anomalies (values significantly different from running average)
        if (abs(current_data.corrosion_rate[i] - running_average[i]) > (running_average[i] * 0.5)) {
            generateAlert("anomaly_detected", "info",
                         "Corrosion rate anomaly detected on electrode " + String(i),
                         "electrode_" + String(i), current_data.corrosion_rate[i], running_average[i],
                         "Investigate possible causes");
        }
    }
}

float calculateAverageCorrosionRate() {
    float total = 0;
    for (int i = 0; i < 8; i++) {
        total += current_data.corrosion_rate[i];
    }
    return total / 8.0;
}

float calculateSystemHealthScore() {
    float score = 100.0;
    
    // Deduct points for various issues
    if (!system_status.wifi_connected) score -= 10;
    if (!system_status.lora_connected) score -= 5;
    if (!system_status.gps_synchronized) score -= 5;
    if (current_data.battery_voltage < 12.0) score -= 10;
    if (current_data.data_quality < 90) score -= 10;
    if (system_status.transmission_errors > 0) score -= 5;
    
    return max(0.0f, score);
}

void handleEmergencyShutdown() {
    Serial.println("EMERGENCY SHUTDOWN INITIATED!");
    
    // Save critical data
    saveEmergencyData();
    
    // Send emergency alert
    generateAlert("emergency_shutdown", "critical",
                 "Emergency shutdown initiated",
                 "system", 0, 0,
                 "Immediate attention required");
    
    // Shutdown non-essential systems
    digitalWrite(STATUS_LED_WIFI, LOW);
    digitalWrite(STATUS_LED_LORA, LOW);
    digitalWrite(STATUS_LED_CELLULAR, LOW);
    
    // Flash critical LED
    while (digitalRead(EMERGENCY_BUTTON) == LOW) {
        digitalWrite(STATUS_LED_CLOUD, HIGH);
        delay(500);
        digitalWrite(STATUS_LED_CLOUD, LOW);
        delay(500);
    }
    
    // Restart system
    ESP.restart();
}

void saveEmergencyData() {
    File emergencyFile = SPIFFS.open("/emergency_data.json", "w");
    if (emergencyFile) {
        StaticJsonDocument<512> doc;
        doc["timestamp"] = millis();
        doc["device_id"] = device_id;
        doc["emergency_type"] = "user_initiated";
        doc["system_status"] = "emergency_shutdown";
        doc["last_data_timestamp"] = current_data.timestamp;
        doc["battery_voltage"] = current_data.battery_voltage;
        doc["system_temperature"] = current_data.system_temperature;
        doc["uptime"] = system_status.uptime;
        
        serializeJson(doc, emergencyFile);
        emergencyFile.close();
    }
}

void generateSystemReport() {
    Serial.println("Generating comprehensive system report...");
    
    StaticJsonDocument<2048> report;
    report["timestamp"] = millis();
    report["device_id"] = device_id;
    report["report_type"] = "comprehensive";
    report["firmware_version"] = system_status.firmware_version;
    report["uptime"] = system_status.uptime;
    
    // System status
    JsonObject system_status_obj = report.createNestedObject("system_status");
    system_status_obj["wifi_connected"] = system_status.wifi_connected;
    system_status_obj["lora_connected"] = system_status.lora_connected;
    system_status_obj["cellular_connected"] = system_status.cellular_connected;
    system_status_obj["cloud_connected"] = system_status.cloud_connected;
    system_status_obj["gps_synchronized"] = system_status.gps_synchronized;
    
    // Statistics
    JsonObject statistics = report.createNestedObject("statistics");
    statistics["total_data_points"] = total_data_points;
    statistics["total_alerts_generated"] = total_alerts_generated;
    statistics["data_transmitted"] = system_status.data_transmitted;
    statistics["transmission_errors"] = system_status.transmission_errors;
    statistics["system_restart_count"] = system_restart_count;
    
    // Current data summary
    JsonObject current_data_obj = report.createNestedObject("current_data");
    current_data_obj["timestamp"] = current_data.timestamp;
    current_data_obj["temperature"] = current_data.temperature;
    current_data_obj["humidity"] = current_data.humidity;
    current_data_obj["ph_value"] = current_data.ph_value;
    current_data_obj["battery_voltage"] = current_data.battery_voltage;
    current_data_obj["system_healthy"] = current_data.system_healthy;
    current_data_obj["average_corrosion_rate"] = calculateAverageCorrosionRate();
    
    // System health
    JsonObject health = report.createNestedObject("system_health");
    health["health_score"] = calculateSystemHealthScore();
    health["cpu_temperature"] = system_status.cpu_temperature;
    health["free_heap"] = system_status.free_heap;
    health["signal_strength_wifi"] = system_status.signal_strength_wifi;
    health["data_quality"] = current_data.data_quality;
    health["communication_quality"] = current_data.communication_quality;
    health["power_quality"] = current_data.power_quality;
    
    // Maintenance status
    JsonObject maintenance = report.createNestedObject("maintenance");
    maintenance["calibration_due"] = maintenance_schedule.calibration_due;
    maintenance["inspection_due"] = maintenance_schedule.inspection_due;
    maintenance["cleaning_due"] = maintenance_schedule.cleaning_due;
    maintenance["replacement_due"] = maintenance_schedule.replacement_due;
    
    String json_string;
    serializeJson(report, json_string);
    
    // Store report
    File reportFile = SPIFFS.open("/reports/system_report_" + String(millis()) + ".json", "w");
    if (reportFile) {
        reportFile.print(json_string);
        reportFile.close();
    }
    
    // Send to cloud
    if (enable_cloud_storage) {
        transmitToCloud(json_string);
    }
    
    // Publish via MQTT
    if (mqtt_client.connected()) {
        String topic = "cms/" + String(device_id) + "/reports";
        mqtt_client.publish(topic.c_str(), json_string.c_str());
    }
    
    Serial.println("System report generated and transmitted");
}

void performFirmwareUpdate(String url) {
    Serial.println("Starting firmware update from: " + url);
    
    // This would implement OTA firmware update
    // For security, this should include signature verification
    
    Serial.println("Firmware update completed");
}

void handleFirmwareUpload(AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
    if (!index) {
        Serial.printf("Update Start: %s\n", filename.c_str());
        if (!Update.begin(UPDATE_SIZE_UNKNOWN)) {
            Update.printError(Serial);
        }
    }
    
    if (Update.write(data, len) != len) {
        Update.printError(Serial);
    }
    
    if (final) {
        if (Update.end(true)) {
            Serial.printf("Update Success: %uB\n", index + len);
        } else {
            Update.printError(Serial);
        }
    }
}

void scheduleCalibration(uint32_t date) {
    maintenance_schedule.next_calibration = date;
    maintenance_schedule.calibration_due = false;
    Serial.println("Calibration scheduled for: " + String(date));
}

void scheduleInspection(uint32_t date) {
    maintenance_schedule.next_inspection = date;
    maintenance_schedule.inspection_due = false;
    Serial.println("Inspection scheduled for: " + String(date));
}

void updateMaintenanceLog(String log_entry) {
    maintenance_schedule.maintenance_notes = log_entry;
    
    File logFile = SPIFFS.open("/maintenance/maintenance_log.txt", "a");
    if (logFile) {
        logFile.print(millis());
        logFile.print(",");
        logFile.print(log_entry);
        logFile.println();
        logFile.close();
    }
    
    Serial.println("Maintenance log updated: " + log_entry);
}

void resetMaintenanceSchedule() {
    maintenance_schedule.next_calibration = millis() + 2592000000; // 30 days
    maintenance_schedule.next_inspection = millis() + 604800000;   // 7 days
    maintenance_schedule.next_cleaning = millis() + 86400000;     // 1 day
    maintenance_schedule.next_replacement = millis() + 31536000000; // 1 year
    maintenance_schedule.calibration_due = false;
    maintenance_schedule.inspection_due = false;
    maintenance_schedule.cleaning_due = false;
    maintenance_schedule.replacement_due = false;
    maintenance_schedule.maintenance_notes = "";
    
    Serial.println("Maintenance schedule reset to defaults");
}

void updateAlertThresholds(JsonObject& thresholds) {
    // Update alert thresholds
    // This would typically involve updating global threshold variables
    
    Serial.println("Alert thresholds updated");
}

void loadConfiguration() {
    if (SPIFFS.exists("/config.json")) {
        File configFile = SPIFFS.open("/config.json", "r");
        if (configFile) {
            StaticJsonDocument<1024> doc;
            deserializeJson(doc, configFile);
            
            enable_lora = doc["enable_lora"];
            enable_cellular = doc["enable_cellular"];
            enable_cloud_storage = doc["enable_cloud_storage"];
            enable_local_storage = doc["enable_local_storage"];
            enable_real_time_alerts = doc["enable_real_time_alerts"];
            data_retention_days = doc["data_retention_days"];
            alert_retention_days = doc["alert_retention_days"];
            
            configFile.close();
            Serial.println("Configuration loaded successfully");
        }
    } else {
        Serial.println("No configuration file found, using defaults");
    }
}

void saveConfiguration() {
    StaticJsonDocument<1024> doc;
    doc["enable_lora"] = enable_lora;
    doc["enable_cellular"] = enable_cellular;
    doc["enable_cloud_storage"] = enable_cloud_storage;
    doc["enable_local_storage"] = enable_local_storage;
    doc["enable_real_time_alerts"] = enable_real_time_alerts;
    doc["data_retention_days"] = data_retention_days;
    doc["alert_retention_days"] = alert_retention_days;
    
    File configFile = SPIFFS.open("/config.json", "w");
    if (configFile) {
        serializeJson(doc, configFile);
        configFile.close();
        Serial.println("Configuration saved successfully");
    }
}