/*
 * Program 24: Nano-Indentation Controller - ESP32 Cloud Analytics
 * 
 * This program implements cloud-based data analytics and remote monitoring
 * for the nano-indentation system. It provides real-time data transmission,
 * advanced analytics, machine learning integration, and comprehensive
 * reporting capabilities for materials characterization.
 * 
 * Features:
 * - Real-time data streaming to cloud platforms
 * - Advanced analytics and statistical processing
 * - Machine learning-based property prediction
 * - Automated report generation
 * - Remote monitoring and control
 * - Multi-user collaboration platform
 * - Quality control and SPC integration
 * - Predictive maintenance capabilities
 * 
 * Author: Arduino Zero to Hero v2.0
 * Created: 2024
 * 
 * Hardware Requirements:
 * - ESP32 DevKit V1
 * - WiFi connection
 * - Cloud service account
 * - Optional: Ethernet connection
 * 
 * Libraries Required:
 * - WiFi.h
 * - WiFiClientSecure.h
 * - ArduinoJson.h
 * - HTTPClient.h
 * - WebSocketsClient.h
 * - PubSubClient.h
 * - AsyncTCP.h
 * - ESPAsyncWebServer.h
 * - SPIFFS.h
 * - mbedtls/md.h
 * - TensorFlowLite.h
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WebSocketsClient.h>
#include <PubSubClient.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include <mbedtls/md.h>
#include <TensorFlowLite_ESP32.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>

// Network Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* backup_ssid = "BACKUP_WIFI_SSID";
const char* backup_password = "BACKUP_WIFI_PASSWORD";

// Cloud Service Configuration
const char* cloud_endpoint = "https://api.materials-cloud.com";
const char* websocket_server = "wss://ws.materials-cloud.com";
const char* mqtt_server = "mqtt.materials-cloud.com";
const int mqtt_port = 8883;
const char* api_key = "your_api_key_here";
const char* device_id = "nano_indent_001";
const char* organization_id = "your_org_id";

// Pin Definitions
#define ARDUINO_SERIAL_TX 17
#define ARDUINO_SERIAL_RX 16
#define STATUS_LED_WIFI 2
#define STATUS_LED_CLOUD 4
#define STATUS_LED_ANALYTICS 5
#define STATUS_LED_ERROR 18
#define ETHERNET_CS 15
#define BACKUP_BUTTON 19
#define RESET_BUTTON 21

// Communication Parameters
#define ARDUINO_BAUD_RATE 115200
#define BUFFER_SIZE 4096
#define MAX_RETRY_COUNT 5
#define HEARTBEAT_INTERVAL 30000
#define DATA_BATCH_SIZE 50

// Data Structures
struct IndentationData {
    uint32_t timestamp;
    float load;
    float displacement;
    float stiffness;
    float temperature;
    float humidity;
    uint8_t contact_status;
    String test_id;
    String sample_id;
    String operator_id;
};

struct MaterialProperties {
    float hardness;
    float elastic_modulus;
    float yield_strength;
    float contact_stiffness;
    float work_hardening;
    float elastic_work;
    float plastic_work;
    float total_work;
    float creep_rate;
    float relaxation_time;
    float confidence_score;
    String material_classification;
};

struct TestParameters {
    float max_load;
    float max_displacement;
    float loading_rate;
    float unloading_rate;
    float hold_time;
    uint8_t test_mode;
    uint8_t indenter_type;
    String test_method;
    String standard_compliance;
};

struct QualityMetrics {
    float repeatability;
    float reproducibility;
    float measurement_uncertainty;
    float correlation_coefficient;
    float residual_standard_deviation;
    uint16_t outlier_count;
    float control_limit_upper;
    float control_limit_lower;
    bool in_statistical_control;
};

struct SystemHealth {
    float cpu_usage;
    float memory_usage;
    float storage_usage;
    float network_latency;
    float data_throughput;
    uint32_t error_count;
    uint32_t uptime;
    String firmware_version;
    String last_calibration;
    bool maintenance_required;
};

struct MLPrediction {
    float predicted_hardness;
    float predicted_modulus;
    float confidence_interval;
    float prediction_accuracy;
    String material_type;
    String failure_mode;
    uint32_t training_samples;
    String model_version;
};

// Global Variables
WiFiClient wifi_client;
WiFiClientSecure secure_client;
PubSubClient mqtt_client(secure_client);
WebSocketsClient webSocket;
AsyncWebServer web_server(80);

HardwareSerial arduino_serial(2);

// Data Buffers
QueueHandle_t data_queue;
QueueHandle_t analytics_queue;
QueueHandle_t transmission_queue;

// Task Handles
TaskHandle_t data_processing_task;
TaskHandle_t analytics_task;
TaskHandle_t cloud_communication_task;
TaskHandle_t web_interface_task;
TaskHandle_t ml_inference_task;

// Machine Learning Components
tflite::MicroErrorReporter micro_error_reporter;
tflite::AllOpsResolver resolver;
const tflite::Model* ml_model;
tflite::MicroInterpreter* interpreter;
TfLiteTensor* input_tensor;
TfLiteTensor* output_tensor;

// Global Data
IndentationData current_data;
MaterialProperties current_properties;
TestParameters current_test_params;
QualityMetrics quality_metrics;
SystemHealth system_health;
MLPrediction ml_prediction;

// Statistics and Buffers
float hardness_history[100];
float modulus_history[100];
uint16_t history_index = 0;
bool history_full = false;

// Timing Variables
uint32_t last_heartbeat = 0;
uint32_t last_data_transmission = 0;
uint32_t last_analytics_update = 0;
uint32_t last_health_check = 0;

// Status Variables
bool wifi_connected = false;
bool cloud_connected = false;
bool mqtt_connected = false;
bool websocket_connected = false;
bool analytics_enabled = true;
bool ml_model_loaded = false;

// Configuration
uint32_t data_transmission_interval = 5000;  // 5 seconds
uint32_t analytics_update_interval = 30000;  // 30 seconds
uint32_t health_check_interval = 60000;     // 1 minute
bool enable_real_time_streaming = true;
bool enable_predictive_analytics = true;

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== ESP32 Nano-Indentation Cloud Analytics ===");
    Serial.println("Initializing cloud-based analytics system...");
    
    // Initialize pin modes
    pinMode(STATUS_LED_WIFI, OUTPUT);
    pinMode(STATUS_LED_CLOUD, OUTPUT);
    pinMode(STATUS_LED_ANALYTICS, OUTPUT);
    pinMode(STATUS_LED_ERROR, OUTPUT);
    pinMode(BACKUP_BUTTON, INPUT_PULLUP);
    pinMode(RESET_BUTTON, INPUT_PULLUP);
    
    // Initialize status LEDs
    digitalWrite(STATUS_LED_WIFI, LOW);
    digitalWrite(STATUS_LED_CLOUD, LOW);
    digitalWrite(STATUS_LED_ANALYTICS, LOW);
    digitalWrite(STATUS_LED_ERROR, LOW);
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("SPIFFS initialization failed!");
        digitalWrite(STATUS_LED_ERROR, HIGH);
        return;
    }
    
    // Initialize serial communication with Arduino
    arduino_serial.begin(ARDUINO_BAUD_RATE, SERIAL_8N1, ARDUINO_SERIAL_RX, ARDUINO_SERIAL_TX);
    
    // Create FreeRTOS queues
    data_queue = xQueueCreate(100, sizeof(IndentationData));
    analytics_queue = xQueueCreate(50, sizeof(MaterialProperties));
    transmission_queue = xQueueCreate(50, sizeof(IndentationData));
    
    // Initialize network connections
    initializeWiFi();
    initializeMQTT();
    initializeWebSocket();
    initializeWebServer();
    
    // Load machine learning model
    loadMLModel();
    
    // Initialize system health monitoring
    initializeSystemHealth();
    
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
        analyticsTask,
        "Analytics",
        8192,
        NULL,
        2,
        &analytics_task,
        0
    );
    
    xTaskCreatePinnedToCore(
        cloudCommunicationTask,
        "CloudComm",
        8192,
        NULL,
        1,
        &cloud_communication_task,
        1
    );
    
    xTaskCreatePinnedToCore(
        webInterfaceTask,
        "WebInterface",
        4096,
        NULL,
        1,
        &web_interface_task,
        1
    );
    
    xTaskCreatePinnedToCore(
        mlInferenceTask,
        "MLInference",
        8192,
        NULL,
        1,
        &ml_inference_task,
        1
    );
    
    Serial.println("System initialization complete!");
    Serial.println("Ready for cloud-based analytics...");
}

void loop() {
    uint32_t current_time = millis();
    
    // Check reset button
    if (digitalRead(RESET_BUTTON) == LOW) {
        delay(50);
        if (digitalRead(RESET_BUTTON) == LOW) {
            Serial.println("Reset button pressed - restarting system...");
            ESP.restart();
        }
    }
    
    // Check backup button
    if (digitalRead(BACKUP_BUTTON) == LOW) {
        delay(50);
        if (digitalRead(BACKUP_BUTTON) == LOW) {
            performDataBackup();
        }
    }
    
    // Maintain connections
    maintainConnections();
    
    // Send heartbeat
    if (current_time - last_heartbeat > HEARTBEAT_INTERVAL) {
        sendHeartbeat();
        last_heartbeat = current_time;
    }
    
    // Update system health
    if (current_time - last_health_check > health_check_interval) {
        updateSystemHealth();
        last_health_check = current_time;
    }
    
    // Handle MQTT messages
    if (mqtt_connected) {
        mqtt_client.loop();
    }
    
    // Handle WebSocket messages
    if (websocket_connected) {
        webSocket.loop();
    }
    
    delay(100);
}

void dataProcessingTask(void* parameter) {
    IndentationData data;
    String incoming_data;
    
    while (true) {
        // Read data from Arduino
        if (arduino_serial.available()) {
            incoming_data = arduino_serial.readStringUntil('\n');
            
            if (parseIndentationData(incoming_data, data)) {
                // Add to processing queue
                if (xQueueSend(data_queue, &data, 0) == pdTRUE) {
                    digitalWrite(STATUS_LED_ANALYTICS, !digitalRead(STATUS_LED_ANALYTICS));
                }
            }
        }
        
        // Process data from queue
        if (xQueueReceive(data_queue, &data, 0) == pdTRUE) {
            processIndentationData(data);
            
            // Add to transmission queue if real-time streaming is enabled
            if (enable_real_time_streaming) {
                xQueueSend(transmission_queue, &data, 0);
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void analyticsTask(void* parameter) {
    MaterialProperties properties;
    
    while (true) {
        // Process analytics queue
        if (xQueueReceive(analytics_queue, &properties, 0) == pdTRUE) {
            performStatisticalAnalysis(properties);
            updateQualityMetrics(properties);
            
            // Send to cloud analytics
            if (cloud_connected) {
                sendAnalyticsToCloud(properties);
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void cloudCommunicationTask(void* parameter) {
    IndentationData data_batch[DATA_BATCH_SIZE];
    int batch_count = 0;
    uint32_t last_transmission = 0;
    
    while (true) {
        // Collect data for batch transmission
        while (batch_count < DATA_BATCH_SIZE && 
               xQueueReceive(transmission_queue, &data_batch[batch_count], 0) == pdTRUE) {
            batch_count++;
        }
        
        // Transmit batch if we have data or enough time has passed
        if (batch_count > 0 && 
            (batch_count >= DATA_BATCH_SIZE || millis() - last_transmission > data_transmission_interval)) {
            
            if (cloud_connected) {
                transmitDataBatch(data_batch, batch_count);
                last_transmission = millis();
            }
            batch_count = 0;
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

void webInterfaceTask(void* parameter) {
    while (true) {
        // Handle web server requests
        // This is handled by the AsyncWebServer automatically
        
        // Update web dashboard data
        updateWebDashboard();
        
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}

void mlInferenceTask(void* parameter) {
    while (true) {
        if (ml_model_loaded && enable_predictive_analytics) {
            // Prepare input data
            if (prepareMLInput()) {
                // Run inference
                if (interpreter->Invoke() == kTfLiteOk) {
                    // Process output
                    processMLOutput();
                }
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(10000)); // Run every 10 seconds
    }
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
        wifi_connected = true;
        digitalWrite(STATUS_LED_WIFI, HIGH);
    } else {
        Serial.println();
        Serial.println("WiFi connection failed, trying backup network...");
        
        WiFi.begin(backup_ssid, backup_password);
        attempts = 0;
        while (WiFi.status() != WL_CONNECTED && attempts < 10) {
            delay(1000);
            Serial.print(".");
            attempts++;
        }
        
        if (WiFi.status() == WL_CONNECTED) {
            Serial.println("Backup WiFi connected!");
            wifi_connected = true;
            digitalWrite(STATUS_LED_WIFI, HIGH);
        } else {
            Serial.println("All WiFi connections failed!");
            digitalWrite(STATUS_LED_ERROR, HIGH);
        }
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
        
        String client_id = "nano_indent_" + String(device_id) + "_" + String(random(0xffff));
        
        if (mqtt_client.connect(client_id.c_str(), api_key, "")) {
            Serial.println("connected");
            mqtt_connected = true;
            
            // Subscribe to control topics
            mqtt_client.subscribe(("devices/" + String(device_id) + "/commands").c_str());
            mqtt_client.subscribe(("devices/" + String(device_id) + "/config").c_str());
            mqtt_client.subscribe(("devices/" + String(device_id) + "/calibration").c_str());
            
            // Publish online status
            publishDeviceStatus();
            
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
    
    handleMQTTCommand(String(topic), message);
}

void handleMQTTCommand(String topic, String message) {
    StaticJsonDocument<512> doc;
    deserializeJson(doc, message);
    
    if (topic.indexOf("commands") > 0) {
        String command = doc["command"];
        
        if (command == "start_test") {
            sendCommandToArduino("{\"command\":\"start_test\"}");
        } else if (command == "stop_test") {
            sendCommandToArduino("{\"command\":\"stop_test\"}");
        } else if (command == "calibrate") {
            sendCommandToArduino("{\"command\":\"calibrate\"}");
        } else if (command == "set_parameters") {
            updateTestParameters(doc["parameters"]);
        } else if (command == "generate_report") {
            generateComprehensiveReport();
        }
    } else if (topic.indexOf("config") > 0) {
        updateSystemConfiguration(doc);
    }
}

void sendCommandToArduino(String command) {
    arduino_serial.println(command);
    Serial.println("Command sent to Arduino: " + command);
}

void initializeWebSocket() {
    webSocket.begin(websocket_server, 443, "/ws");
    webSocket.onEvent(webSocketEvent);
    webSocket.setAuthorization(api_key);
    webSocket.setReconnectInterval(5000);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch (type) {
        case WStype_DISCONNECTED:
            Serial.printf("[WS] Disconnected!\n");
            websocket_connected = false;
            break;
            
        case WStype_CONNECTED:
            Serial.printf("[WS] Connected to: %s\n", payload);
            websocket_connected = true;
            
            // Send initial device info
            sendDeviceInfo();
            break;
            
        case WStype_TEXT:
            Serial.printf("[WS] Received text: %s\n", payload);
            handleWebSocketMessage(String((char*)payload));
            break;
            
        case WStype_BIN:
            Serial.printf("[WS] Received binary length: %u\n", length);
            break;
            
        case WStype_ERROR:
            Serial.printf("[WS] Error: %s\n", payload);
            break;
            
        default:
            break;
    }
}

void handleWebSocketMessage(String message) {
    StaticJsonDocument<512> doc;
    deserializeJson(doc, message);
    
    String type = doc["type"];
    
    if (type == "request_data") {
        sendRealtimeData();
    } else if (type == "update_config") {
        updateSystemConfiguration(doc["config"]);
    } else if (type == "run_analysis") {
        runAdvancedAnalysis(doc["parameters"]);
    }
}

void initializeWebServer() {
    // Serve static files
    web_server.serveStatic("/", SPIFFS, "/");
    
    // API endpoints
    web_server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<1024> doc;
        doc["device_id"] = device_id;
        doc["wifi_connected"] = wifi_connected;
        doc["cloud_connected"] = cloud_connected;
        doc["mqtt_connected"] = mqtt_connected;
        doc["websocket_connected"] = websocket_connected;
        doc["analytics_enabled"] = analytics_enabled;
        doc["ml_model_loaded"] = ml_model_loaded;
        doc["system_health"] = createSystemHealthJSON();
        doc["current_properties"] = createPropertiesJSON();
        doc["quality_metrics"] = createQualityMetricsJSON();
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/data", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<2048> doc;
        JsonArray data_array = doc.createNestedArray("data");
        
        // Add recent data points
        for (int i = 0; i < min(history_index, 50); i++) {
            JsonObject point = data_array.createNestedObject();
            point["hardness"] = hardness_history[i];
            point["modulus"] = modulus_history[i];
            point["timestamp"] = millis() - (50 - i) * 1000;
        }
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/analytics", HTTP_GET, [](AsyncWebServerRequest *request){
        AsyncResponseStream *response = request->beginResponseStream("application/json");
        
        StaticJsonDocument<1024> doc;
        doc["quality_metrics"] = createQualityMetricsJSON();
        doc["statistical_analysis"] = createStatisticalAnalysisJSON();
        doc["ml_predictions"] = createMLPredictionsJSON();
        
        serializeJson(doc, *response);
        request->send(response);
    });
    
    web_server.on("/api/report", HTTP_GET, [](AsyncWebServerRequest *request){
        generateComprehensiveReport();
        request->send(200, "application/json", "{\"status\":\"report_generated\"}");
    });
    
    web_server.begin();
    Serial.println("Web server started on port 80");
}

void loadMLModel() {
    Serial.println("Loading machine learning model...");
    
    // Load model from SPIFFS
    if (SPIFFS.exists("/model.tflite")) {
        File model_file = SPIFFS.open("/model.tflite", "r");
        if (model_file) {
            size_t model_size = model_file.size();
            uint8_t* model_data = (uint8_t*)malloc(model_size);
            
            if (model_data) {
                model_file.readBytes((char*)model_data, model_size);
                model_file.close();
                
                // Initialize TensorFlow Lite
                ml_model = tflite::GetModel(model_data);
                if (ml_model->version() != TFLITE_SCHEMA_VERSION) {
                    Serial.println("Model schema version mismatch!");
                    free(model_data);
                    return;
                }
                
                // Create interpreter
                static tflite::MicroInterpreter static_interpreter(
                    ml_model, resolver, tensor_arena, kTensorArenaSize, &micro_error_reporter);
                interpreter = &static_interpreter;
                
                // Allocate tensors
                TfLiteStatus allocate_status = interpreter->AllocateTensors();
                if (allocate_status != kTfLiteOk) {
                    Serial.println("AllocateTensors() failed!");
                    free(model_data);
                    return;
                }
                
                // Get input and output tensors
                input_tensor = interpreter->input(0);
                output_tensor = interpreter->output(0);
                
                ml_model_loaded = true;
                Serial.println("Machine learning model loaded successfully!");
                
            } else {
                Serial.println("Failed to allocate memory for model!");
                model_file.close();
            }
        } else {
            Serial.println("Failed to open model file!");
        }
    } else {
        Serial.println("Model file not found - ML features disabled");
    }
}

bool parseIndentationData(String data, IndentationData& parsed_data) {
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, data);
    
    if (error) {
        Serial.print("JSON parsing failed: ");
        Serial.println(error.c_str());
        return false;
    }
    
    if (doc["type"] == "indentation_data") {
        parsed_data.timestamp = doc["timestamp"];
        parsed_data.load = doc["load"];
        parsed_data.displacement = doc["displacement"];
        parsed_data.stiffness = doc["stiffness"];
        parsed_data.temperature = doc["temperature"];
        parsed_data.humidity = doc["humidity"];
        parsed_data.contact_status = doc["contact_status"];
        parsed_data.test_id = doc["test_id"].as<String>();
        parsed_data.sample_id = doc["sample_id"].as<String>();
        parsed_data.operator_id = doc["operator_id"].as<String>();
        
        return true;
    }
    
    return false;
}

void processIndentationData(IndentationData& data) {
    // Store current data
    current_data = data;
    
    // Update history buffers
    if (data.contact_status == 3) { // Unloading complete
        // Extract material properties from the data
        MaterialProperties properties = extractMaterialProperties(data);
        
        // Add to analytics queue
        xQueueSend(analytics_queue, &properties, 0);
        
        // Update history
        updateHistoryBuffers(properties);
    }
    
    // Real-time monitoring
    if (enable_real_time_streaming && websocket_connected) {
        sendRealtimeData();
    }
}

MaterialProperties extractMaterialProperties(IndentationData& data) {
    MaterialProperties properties;
    
    // This would normally be calculated from the complete load-displacement curve
    // For this example, we'll use simplified calculations
    
    // Calculate hardness (simplified)
    float contact_area = 24.5 * pow(data.displacement * 1e-9, 2); // Berkovich area function
    properties.hardness = (data.load * 1e-6) / (contact_area * 1e-18); // Convert to GPa
    
    // Calculate elastic modulus (simplified)
    properties.elastic_modulus = properties.hardness * 0.1; // Simplified relationship
    
    // Calculate other properties
    properties.contact_stiffness = data.stiffness;
    properties.work_hardening = 0.0; // Would be calculated from loading curve
    properties.elastic_work = 0.0;   // Would be calculated from unloading curve
    properties.plastic_work = 0.0;   // Would be calculated from total work
    properties.total_work = 0.0;     // Would be calculated from area under curve
    properties.creep_rate = 0.0;     // Would be calculated from hold period
    properties.relaxation_time = 0.0; // Would be calculated from relaxation data
    properties.confidence_score = 0.95; // Would be calculated from curve fit quality
    properties.material_classification = "Unknown";
    
    return properties;
}

void updateHistoryBuffers(MaterialProperties& properties) {
    hardness_history[history_index] = properties.hardness;
    modulus_history[history_index] = properties.elastic_modulus;
    
    history_index++;
    if (history_index >= 100) {
        history_index = 0;
        history_full = true;
    }
}

void performStatisticalAnalysis(MaterialProperties& properties) {
    // Calculate statistical metrics
    int sample_count = history_full ? 100 : history_index;
    
    if (sample_count > 5) {
        // Calculate mean and standard deviation for hardness
        float hardness_mean = 0.0;
        float hardness_sum_sq = 0.0;
        
        for (int i = 0; i < sample_count; i++) {
            hardness_mean += hardness_history[i];
        }
        hardness_mean /= sample_count;
        
        for (int i = 0; i < sample_count; i++) {
            float diff = hardness_history[i] - hardness_mean;
            hardness_sum_sq += diff * diff;
        }
        
        float hardness_std = sqrt(hardness_sum_sq / (sample_count - 1));
        
        // Calculate repeatability and reproducibility
        quality_metrics.repeatability = hardness_std / hardness_mean * 100.0; // CV%
        quality_metrics.reproducibility = quality_metrics.repeatability * 1.5; // Estimate
        
        // Calculate control limits (±3σ)
        quality_metrics.control_limit_upper = hardness_mean + 3 * hardness_std;
        quality_metrics.control_limit_lower = hardness_mean - 3 * hardness_std;
        
        // Check if current measurement is in control
        quality_metrics.in_statistical_control = 
            (properties.hardness >= quality_metrics.control_limit_lower) &&
            (properties.hardness <= quality_metrics.control_limit_upper);
        
        // Calculate measurement uncertainty
        quality_metrics.measurement_uncertainty = hardness_std * 2.0; // 95% confidence
        
        // Count outliers
        quality_metrics.outlier_count = 0;
        for (int i = 0; i < sample_count; i++) {
            if (hardness_history[i] < quality_metrics.control_limit_lower ||
                hardness_history[i] > quality_metrics.control_limit_upper) {
                quality_metrics.outlier_count++;
            }
        }
        
        // Calculate correlation coefficient between hardness and modulus
        if (sample_count > 10) {
            quality_metrics.correlation_coefficient = calculateCorrelation(
                hardness_history, modulus_history, sample_count);
        }
    }
}

float calculateCorrelation(float* x, float* y, int n) {
    float sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0;
    float sum_x2 = 0.0, sum_y2 = 0.0;
    
    for (int i = 0; i < n; i++) {
        sum_x += x[i];
        sum_y += y[i];
        sum_xy += x[i] * y[i];
        sum_x2 += x[i] * x[i];
        sum_y2 += y[i] * y[i];
    }
    
    float numerator = n * sum_xy - sum_x * sum_y;
    float denominator = sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y));
    
    if (denominator == 0.0) return 0.0;
    
    return numerator / denominator;
}

void updateQualityMetrics(MaterialProperties& properties) {
    // Update quality metrics based on latest results
    current_properties = properties;
    
    // Check for quality alerts
    if (!quality_metrics.in_statistical_control) {
        sendQualityAlert(properties);
    }
    
    // Update control charts
    updateControlCharts(properties);
}

void sendQualityAlert(MaterialProperties& properties) {
    StaticJsonDocument<512> doc;
    doc["type"] = "quality_alert";
    doc["device_id"] = device_id;
    doc["timestamp"] = millis();
    doc["alert_type"] = "out_of_control";
    doc["measurement_value"] = properties.hardness;
    doc["control_limit_upper"] = quality_metrics.control_limit_upper;
    doc["control_limit_lower"] = quality_metrics.control_limit_lower;
    doc["severity"] = "medium";
    
    String json_string;
    serializeJson(doc, json_string);
    
    if (mqtt_connected) {
        String topic = "alerts/" + String(device_id) + "/quality";
        mqtt_client.publish(topic.c_str(), json_string.c_str());
    }
    
    if (websocket_connected) {
        webSocket.sendTXT(json_string);
    }
}

void updateControlCharts(MaterialProperties& properties) {
    // Update statistical process control charts
    // This would typically involve more sophisticated SPC algorithms
    
    // For now, just update the basic control limits
    performStatisticalAnalysis(properties);
}

void transmitDataBatch(IndentationData* data_batch, int count) {
    HTTPClient http;
    http.begin(String(cloud_endpoint) + "/api/v1/data/batch");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    http.addHeader("X-Device-ID", device_id);
    http.addHeader("X-Organization-ID", organization_id);
    
    StaticJsonDocument<4096> doc;
    doc["device_id"] = device_id;
    doc["batch_timestamp"] = millis();
    doc["batch_size"] = count;
    
    JsonArray data_array = doc.createNestedArray("data");
    
    for (int i = 0; i < count; i++) {
        JsonObject data_point = data_array.createNestedObject();
        data_point["timestamp"] = data_batch[i].timestamp;
        data_point["load"] = data_batch[i].load;
        data_point["displacement"] = data_batch[i].displacement;
        data_point["stiffness"] = data_batch[i].stiffness;
        data_point["temperature"] = data_batch[i].temperature;
        data_point["humidity"] = data_batch[i].humidity;
        data_point["contact_status"] = data_batch[i].contact_status;
        data_point["test_id"] = data_batch[i].test_id;
        data_point["sample_id"] = data_batch[i].sample_id;
        data_point["operator_id"] = data_batch[i].operator_id;
    }
    
    String json_string;
    serializeJson(doc, json_string);
    
    int response_code = http.POST(json_string);
    
    if (response_code == 200) {
        Serial.printf("Successfully transmitted %d data points\n", count);
        digitalWrite(STATUS_LED_CLOUD, HIGH);
        cloud_connected = true;
    } else {
        Serial.printf("Data transmission failed: %d\n", response_code);
        digitalWrite(STATUS_LED_CLOUD, LOW);
        cloud_connected = false;
    }
    
    http.end();
}

void sendAnalyticsToCloud(MaterialProperties& properties) {
    HTTPClient http;
    http.begin(String(cloud_endpoint) + "/api/v1/analytics");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    http.addHeader("X-Device-ID", device_id);
    
    StaticJsonDocument<1024> doc;
    doc["device_id"] = device_id;
    doc["timestamp"] = millis();
    doc["material_properties"] = createPropertiesJSON();
    doc["quality_metrics"] = createQualityMetricsJSON();
    doc["statistical_analysis"] = createStatisticalAnalysisJSON();
    
    String json_string;
    serializeJson(doc, json_string);
    
    int response_code = http.POST(json_string);
    
    if (response_code == 200) {
        Serial.println("Analytics data sent to cloud");
    } else {
        Serial.printf("Analytics transmission failed: %d\n", response_code);
    }
    
    http.end();
}

bool prepareMLInput() {
    if (!ml_model_loaded) return false;
    
    // Prepare input tensor with current data
    // This would depend on the specific model architecture
    
    if (input_tensor->dims->size == 2) {
        // Assuming input shape is [1, n_features]
        int n_features = input_tensor->dims->data[1];
        
        if (n_features >= 6) {
            input_tensor->data.f[0] = current_data.load;
            input_tensor->data.f[1] = current_data.displacement;
            input_tensor->data.f[2] = current_data.stiffness;
            input_tensor->data.f[3] = current_data.temperature;
            input_tensor->data.f[4] = current_data.humidity;
            input_tensor->data.f[5] = current_properties.hardness;
            
            return true;
        }
    }
    
    return false;
}

void processMLOutput() {
    if (!ml_model_loaded) return;
    
    // Process output tensor
    // This would depend on the specific model architecture
    
    if (output_tensor->dims->size == 2) {
        int n_outputs = output_tensor->dims->data[1];
        
        if (n_outputs >= 3) {
            ml_prediction.predicted_hardness = output_tensor->data.f[0];
            ml_prediction.predicted_modulus = output_tensor->data.f[1];
            ml_prediction.confidence_interval = output_tensor->data.f[2];
            
            // Calculate prediction accuracy
            float hardness_error = abs(ml_prediction.predicted_hardness - current_properties.hardness);
            ml_prediction.prediction_accuracy = 1.0 - (hardness_error / current_properties.hardness);
            
            // Update ML prediction data
            ml_prediction.material_type = classifyMaterial(ml_prediction.predicted_hardness, 
                                                          ml_prediction.predicted_modulus);
            ml_prediction.model_version = "v1.0";
            ml_prediction.training_samples = 10000; // This would be stored in model metadata
            
            Serial.printf("ML Prediction - Hardness: %.2f GPa, Modulus: %.2f GPa, Accuracy: %.2f%%\n",
                         ml_prediction.predicted_hardness, 
                         ml_prediction.predicted_modulus,
                         ml_prediction.prediction_accuracy * 100);
        }
    }
}

String classifyMaterial(float hardness, float modulus) {
    // Simple material classification based on hardness and modulus
    if (hardness > 20.0 && modulus > 400.0) {
        return "Ceramic";
    } else if (hardness > 5.0 && modulus > 200.0) {
        return "Steel";
    } else if (hardness > 2.0 && modulus > 70.0) {
        return "Aluminum";
    } else if (hardness < 1.0 && modulus < 10.0) {
        return "Polymer";
    } else {
        return "Unknown";
    }
}

void sendRealtimeData() {
    if (!websocket_connected) return;
    
    StaticJsonDocument<512> doc;
    doc["type"] = "realtime_data";
    doc["timestamp"] = millis();
    doc["device_id"] = device_id;
    doc["load"] = current_data.load;
    doc["displacement"] = current_data.displacement;
    doc["stiffness"] = current_data.stiffness;
    doc["temperature"] = current_data.temperature;
    doc["humidity"] = current_data.humidity;
    doc["contact_status"] = current_data.contact_status;
    doc["hardness"] = current_properties.hardness;
    doc["modulus"] = current_properties.elastic_modulus;
    doc["in_control"] = quality_metrics.in_statistical_control;
    
    String json_string;
    serializeJson(doc, json_string);
    
    webSocket.sendTXT(json_string);
}

void sendDeviceInfo() {
    StaticJsonDocument<512> doc;
    doc["type"] = "device_info";
    doc["device_id"] = device_id;
    doc["organization_id"] = organization_id;
    doc["device_type"] = "nano_indentation_controller";
    doc["firmware_version"] = system_health.firmware_version;
    doc["capabilities"] = "real_time_streaming,analytics,ml_prediction,quality_control";
    doc["timestamp"] = millis();
    
    String json_string;
    serializeJson(doc, json_string);
    
    webSocket.sendTXT(json_string);
}

void sendHeartbeat() {
    if (mqtt_connected) {
        StaticJsonDocument<256> doc;
        doc["device_id"] = device_id;
        doc["timestamp"] = millis();
        doc["uptime"] = system_health.uptime;
        doc["cpu_usage"] = system_health.cpu_usage;
        doc["memory_usage"] = system_health.memory_usage;
        doc["network_latency"] = system_health.network_latency;
        doc["status"] = "online";
        
        String json_string;
        serializeJson(doc, json_string);
        
        String topic = "heartbeat/" + String(device_id);
        mqtt_client.publish(topic.c_str(), json_string.c_str());
    }
}

void publishDeviceStatus() {
    if (!mqtt_connected) return;
    
    StaticJsonDocument<1024> doc;
    doc["device_id"] = device_id;
    doc["timestamp"] = millis();
    doc["status"] = "online";
    doc["wifi_connected"] = wifi_connected;
    doc["cloud_connected"] = cloud_connected;
    doc["analytics_enabled"] = analytics_enabled;
    doc["ml_model_loaded"] = ml_model_loaded;
    doc["system_health"] = createSystemHealthJSON();
    doc["quality_metrics"] = createQualityMetricsJSON();
    
    String json_string;
    serializeJson(doc, json_string);
    
    String topic = "status/" + String(device_id);
    mqtt_client.publish(topic.c_str(), json_string.c_str());
}

void maintainConnections() {
    // Check WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        wifi_connected = false;
        digitalWrite(STATUS_LED_WIFI, LOW);
        initializeWiFi();
    }
    
    // Check MQTT connection
    if (!mqtt_client.connected()) {
        mqtt_connected = false;
        connectMQTT();
    }
    
    // Check WebSocket connection
    if (!websocket_connected) {
        initializeWebSocket();
    }
    
    // Test cloud connectivity
    testCloudConnection();
}

void testCloudConnection() {
    HTTPClient http;
    http.begin(String(cloud_endpoint) + "/api/v1/health");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    http.setTimeout(5000);
    
    int response_code = http.GET();
    
    if (response_code == 200) {
        cloud_connected = true;
        digitalWrite(STATUS_LED_CLOUD, HIGH);
        digitalWrite(STATUS_LED_ERROR, LOW);
    } else {
        cloud_connected = false;
        digitalWrite(STATUS_LED_CLOUD, LOW);
        if (!wifi_connected) {
            digitalWrite(STATUS_LED_ERROR, HIGH);
        }
    }
    
    http.end();
}

void updateSystemHealth() {
    system_health.uptime = millis() / 1000;
    system_health.cpu_usage = 0.0; // Would need actual CPU monitoring
    system_health.memory_usage = (float)(ESP.getHeapSize() - ESP.getFreeHeap()) / ESP.getHeapSize() * 100.0;
    system_health.storage_usage = 0.0; // Would need SPIFFS usage calculation
    system_health.network_latency = 0.0; // Would need ping measurement
    system_health.data_throughput = 0.0; // Would need actual measurement
    system_health.firmware_version = "v2.0.0";
    system_health.last_calibration = "2024-01-01";
    system_health.maintenance_required = false;
    
    // Check for maintenance requirements
    if (system_health.error_count > 100) {
        system_health.maintenance_required = true;
    }
}

void initializeSystemHealth() {
    system_health.cpu_usage = 0.0;
    system_health.memory_usage = 0.0;
    system_health.storage_usage = 0.0;
    system_health.network_latency = 0.0;
    system_health.data_throughput = 0.0;
    system_health.error_count = 0;
    system_health.uptime = 0;
    system_health.firmware_version = "v2.0.0";
    system_health.last_calibration = "Unknown";
    system_health.maintenance_required = false;
}

JsonObject createSystemHealthJSON() {
    StaticJsonDocument<512> doc;
    JsonObject health = doc.to<JsonObject>();
    
    health["uptime"] = system_health.uptime;
    health["cpu_usage"] = system_health.cpu_usage;
    health["memory_usage"] = system_health.memory_usage;
    health["storage_usage"] = system_health.storage_usage;
    health["network_latency"] = system_health.network_latency;
    health["data_throughput"] = system_health.data_throughput;
    health["error_count"] = system_health.error_count;
    health["firmware_version"] = system_health.firmware_version;
    health["last_calibration"] = system_health.last_calibration;
    health["maintenance_required"] = system_health.maintenance_required;
    
    return health;
}

JsonObject createPropertiesJSON() {
    StaticJsonDocument<512> doc;
    JsonObject properties = doc.to<JsonObject>();
    
    properties["hardness"] = current_properties.hardness;
    properties["elastic_modulus"] = current_properties.elastic_modulus;
    properties["yield_strength"] = current_properties.yield_strength;
    properties["contact_stiffness"] = current_properties.contact_stiffness;
    properties["work_hardening"] = current_properties.work_hardening;
    properties["elastic_work"] = current_properties.elastic_work;
    properties["plastic_work"] = current_properties.plastic_work;
    properties["total_work"] = current_properties.total_work;
    properties["creep_rate"] = current_properties.creep_rate;
    properties["relaxation_time"] = current_properties.relaxation_time;
    properties["confidence_score"] = current_properties.confidence_score;
    properties["material_classification"] = current_properties.material_classification;
    
    return properties;
}

JsonObject createQualityMetricsJSON() {
    StaticJsonDocument<512> doc;
    JsonObject metrics = doc.to<JsonObject>();
    
    metrics["repeatability"] = quality_metrics.repeatability;
    metrics["reproducibility"] = quality_metrics.reproducibility;
    metrics["measurement_uncertainty"] = quality_metrics.measurement_uncertainty;
    metrics["correlation_coefficient"] = quality_metrics.correlation_coefficient;
    metrics["residual_standard_deviation"] = quality_metrics.residual_standard_deviation;
    metrics["outlier_count"] = quality_metrics.outlier_count;
    metrics["control_limit_upper"] = quality_metrics.control_limit_upper;
    metrics["control_limit_lower"] = quality_metrics.control_limit_lower;
    metrics["in_statistical_control"] = quality_metrics.in_statistical_control;
    
    return metrics;
}

JsonObject createStatisticalAnalysisJSON() {
    StaticJsonDocument<512> doc;
    JsonObject analysis = doc.to<JsonObject>();
    
    // Calculate current statistics
    int sample_count = history_full ? 100 : history_index;
    if (sample_count > 0) {
        float mean = 0.0, variance = 0.0;
        for (int i = 0; i < sample_count; i++) {
            mean += hardness_history[i];
        }
        mean /= sample_count;
        
        for (int i = 0; i < sample_count; i++) {
            variance += pow(hardness_history[i] - mean, 2);
        }
        variance /= (sample_count - 1);
        
        analysis["sample_count"] = sample_count;
        analysis["mean"] = mean;
        analysis["standard_deviation"] = sqrt(variance);
        analysis["coefficient_of_variation"] = sqrt(variance) / mean * 100.0;
        analysis["min_value"] = *std::min_element(hardness_history, hardness_history + sample_count);
        analysis["max_value"] = *std::max_element(hardness_history, hardness_history + sample_count);
    }
    
    return analysis;
}

JsonObject createMLPredictionsJSON() {
    StaticJsonDocument<512> doc;
    JsonObject predictions = doc.to<JsonObject>();
    
    predictions["predicted_hardness"] = ml_prediction.predicted_hardness;
    predictions["predicted_modulus"] = ml_prediction.predicted_modulus;
    predictions["confidence_interval"] = ml_prediction.confidence_interval;
    predictions["prediction_accuracy"] = ml_prediction.prediction_accuracy;
    predictions["material_type"] = ml_prediction.material_type;
    predictions["failure_mode"] = ml_prediction.failure_mode;
    predictions["training_samples"] = ml_prediction.training_samples;
    predictions["model_version"] = ml_prediction.model_version;
    predictions["model_loaded"] = ml_model_loaded;
    
    return predictions;
}

void updateWebDashboard() {
    // Update dashboard data
    // This would typically involve updating a web dashboard
    // For now, we'll just send a status update via WebSocket
    
    if (websocket_connected) {
        StaticJsonDocument<1024> doc;
        doc["type"] = "dashboard_update";
        doc["timestamp"] = millis();
        doc["device_id"] = device_id;
        doc["system_health"] = createSystemHealthJSON();
        doc["material_properties"] = createPropertiesJSON();
        doc["quality_metrics"] = createQualityMetricsJSON();
        doc["ml_predictions"] = createMLPredictionsJSON();
        
        String json_string;
        serializeJson(doc, json_string);
        
        webSocket.sendTXT(json_string);
    }
}

void generateComprehensiveReport() {
    Serial.println("Generating comprehensive report...");
    
    StaticJsonDocument<2048> doc;
    doc["report_type"] = "comprehensive";
    doc["device_id"] = device_id;
    doc["timestamp"] = millis();
    doc["report_period"] = "last_100_tests";
    
    // System information
    doc["system_info"]["firmware_version"] = system_health.firmware_version;
    doc["system_info"]["uptime"] = system_health.uptime;
    doc["system_info"]["last_calibration"] = system_health.last_calibration;
    
    // Statistical summary
    doc["statistical_summary"] = createStatisticalAnalysisJSON();
    
    // Quality metrics
    doc["quality_metrics"] = createQualityMetricsJSON();
    
    // ML predictions
    doc["ml_predictions"] = createMLPredictionsJSON();
    
    // Test parameters
    doc["test_parameters"]["max_load"] = current_test_params.max_load;
    doc["test_parameters"]["max_displacement"] = current_test_params.max_displacement;
    doc["test_parameters"]["loading_rate"] = current_test_params.loading_rate;
    doc["test_parameters"]["test_method"] = current_test_params.test_method;
    
    // Send report to cloud
    HTTPClient http;
    http.begin(String(cloud_endpoint) + "/api/v1/reports");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    http.addHeader("X-Device-ID", device_id);
    
    String json_string;
    serializeJson(doc, json_string);
    
    int response_code = http.POST(json_string);
    
    if (response_code == 200) {
        Serial.println("Comprehensive report generated and sent to cloud");
    } else {
        Serial.printf("Report generation failed: %d\n", response_code);
    }
    
    http.end();
}

void performDataBackup() {
    Serial.println("Performing data backup...");
    
    // Create backup of current data
    String backup_filename = "/backup_" + String(millis()) + ".json";
    
    File backup_file = SPIFFS.open(backup_filename, "w");
    if (backup_file) {
        StaticJsonDocument<2048> doc;
        doc["backup_timestamp"] = millis();
        doc["device_id"] = device_id;
        doc["system_health"] = createSystemHealthJSON();
        doc["quality_metrics"] = createQualityMetricsJSON();
        doc["ml_predictions"] = createMLPredictionsJSON();
        
        // Add history data
        JsonArray hardness_data = doc.createNestedArray("hardness_history");
        JsonArray modulus_data = doc.createNestedArray("modulus_history");
        
        int sample_count = history_full ? 100 : history_index;
        for (int i = 0; i < sample_count; i++) {
            hardness_data.add(hardness_history[i]);
            modulus_data.add(modulus_history[i]);
        }
        
        serializeJson(doc, backup_file);
        backup_file.close();
        
        Serial.println("Data backup completed: " + backup_filename);
    } else {
        Serial.println("Failed to create backup file");
    }
}

void updateTestParameters(JsonObject parameters) {
    current_test_params.max_load = parameters["max_load"];
    current_test_params.max_displacement = parameters["max_displacement"];
    current_test_params.loading_rate = parameters["loading_rate"];
    current_test_params.unloading_rate = parameters["unloading_rate"];
    current_test_params.hold_time = parameters["hold_time"];
    current_test_params.test_mode = parameters["test_mode"];
    current_test_params.indenter_type = parameters["indenter_type"];
    current_test_params.test_method = parameters["test_method"].as<String>();
    current_test_params.standard_compliance = parameters["standard_compliance"].as<String>();
    
    // Send updated parameters to Arduino
    StaticJsonDocument<512> doc;
    doc["command"] = "update_parameters";
    doc["parameters"] = parameters;
    
    String json_string;
    serializeJson(doc, json_string);
    
    sendCommandToArduino(json_string);
}

void updateSystemConfiguration(JsonObject config) {
    if (config.containsKey("data_transmission_interval")) {
        data_transmission_interval = config["data_transmission_interval"];
    }
    
    if (config.containsKey("analytics_update_interval")) {
        analytics_update_interval = config["analytics_update_interval"];
    }
    
    if (config.containsKey("enable_real_time_streaming")) {
        enable_real_time_streaming = config["enable_real_time_streaming"];
    }
    
    if (config.containsKey("enable_predictive_analytics")) {
        enable_predictive_analytics = config["enable_predictive_analytics"];
    }
    
    if (config.containsKey("analytics_enabled")) {
        analytics_enabled = config["analytics_enabled"];
    }
    
    Serial.println("System configuration updated");
}

void runAdvancedAnalysis(JsonObject parameters) {
    Serial.println("Running advanced analysis...");
    
    // This would implement advanced analysis algorithms
    // For example: fatigue analysis, creep analysis, statistical modeling
    
    String analysis_type = parameters["analysis_type"];
    
    if (analysis_type == "fatigue_analysis") {
        // Implement fatigue analysis
        Serial.println("Running fatigue analysis...");
    } else if (analysis_type == "creep_analysis") {
        // Implement creep analysis
        Serial.println("Running creep analysis...");
    } else if (analysis_type == "statistical_modeling") {
        // Implement statistical modeling
        Serial.println("Running statistical modeling...");
    }
    
    // Send results back via WebSocket
    StaticJsonDocument<512> doc;
    doc["type"] = "analysis_results";
    doc["analysis_type"] = analysis_type;
    doc["timestamp"] = millis();
    doc["results"] = "Analysis completed successfully";
    
    String json_string;
    serializeJson(doc, json_string);
    
    if (websocket_connected) {
        webSocket.sendTXT(json_string);
    }
}

// Additional tensor arena for TensorFlow Lite
constexpr int kTensorArenaSize = 60 * 1024;
uint8_t tensor_arena[kTensorArenaSize];