/*
 * Program 29: Composite Curing Controller - ESP32 Cure Kinetics Gateway
 * 
 * Advanced IoT gateway implementing real-time cure kinetics modeling,
 * digital twin synchronization, and aerospace-grade process optimization
 * for composite autoclave control systems.
 * 
 * Features:
 * - Real-time Kamal-Sourour cure kinetics modeling
 * - Multi-zone thermal analysis and prediction
 * - Resin viscosity tracking and gelation prediction
 * - Residual stress and warpage modeling
 * - MQTT telemetry with aerospace compliance
 * - Machine learning optimization engine
 * - Digital twin synchronization
 * - Cloud analytics integration
 * 
 * Hardware: ESP32 DevKit V1
 * Communication: Serial (Arduino Mega), WiFi, MQTT
 * Processing: TensorFlow Lite for edge inference
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>
#include <SPIFFS.h>
#include <time.h>
#include <math.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

// Network Configuration
const char* ssid = "CompositeManufacturing_2.4G";
const char* password = "AerospaceGrade2024!";
const char* mqtt_server = "mqtt.composite-analytics.com";
const int mqtt_port = 8883;
const char* device_id = "ESP32_CureKinetics_001";

// TensorFlow Lite Configuration
constexpr int kTensorArenaSize = 60000;
uint8_t tensor_arena[kTensorArenaSize];

// System Objects
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WebServer webServer(80);
tflite::MicroErrorReporter tflErrorReporter;
const tflite::Model* tflModel;
tflite::MicroInterpreter* tflInterpreter;
TfLiteTensor* input;
TfLiteTensor* output;

// Data Structures
struct CureKineticsState {
    float degree_of_cure;              // α (0-1)
    float cure_rate;                   // dα/dt (1/s)
    float resin_viscosity;             // η (Pa·s)
    float glass_transition_temp;       // Tg (°C)
    float gel_time;                    // Time to gelation (s)
    float vitrification_time;          // Time to vitrification (s)
    bool gelation_reached;
    bool vitrification_reached;
    unsigned long last_update;
    float confidence_level;
};

struct MaterialProperties {
    char material_name[32];
    float arrhenius_a;                 // Pre-exponential factor
    float activation_energy;           // Ea (J/mol)
    float reaction_order_m;            // Autocatalytic order
    float reaction_order_n;            // Normal order
    float tg_uncured;                 // Tg0 (°C)
    float tg_fully_cured;             // Tg∞ (°C)
    float lambda_parameter;           // DiBenedetto parameter
    float viscosity_infinity;         // η∞ (Pa·s)
    float viscosity_activation;       // Eη (J/mol)
    float gel_point_alpha;            // αgel
    float vitrification_factor;       // C1 parameter
    float density_uncured;            // ρ0 (kg/m³)
    float density_cured;              // ρ∞ (kg/m³)
    float thermal_expansion_coeff;    // α (1/K)
    float shrinkage_factor;           // Linear shrinkage
};

struct ThermalState {
    float zone_temperatures[12];       // °C
    float average_temperature;         // °C
    float temperature_uniformity;      // ±°C
    float heating_rate;               // °C/min
    float thermal_mass;               // J/K
    float heat_capacity;              // J/(kg·K)
    unsigned long last_update;
};

struct ProcessOptimization {
    float optimal_heating_rate;        // °C/min
    float predicted_cycle_time;        // minutes
    float energy_consumption;          // kWh
    float quality_score;              // 0-100
    float residual_stress_level;      // MPa
    float warpage_prediction;         // mm
    int optimization_iterations;
    float cost_function_value;
    bool optimization_complete;
};

struct DigitalTwinData {
    float virtual_temperature_profile[12][1000];  // Historical data
    float virtual_cure_progression[1000];
    float virtual_stress_field[100][100];        // 2D stress map
    float virtual_warpage_map[100][100];         // 2D warpage map
    int data_points;
    unsigned long last_sync;
    bool sync_enabled;
    float model_accuracy;
};

// Global Variables
CureKineticsState cure_state;
MaterialProperties current_material;
ThermalState thermal_state;
ProcessOptimization process_opt;
DigitalTwinData digital_twin;

// Constants
const float GAS_CONSTANT = 8.314;     // J/(mol·K)
const float KELVIN_OFFSET = 273.15;
const int MAX_ZONES = 12;
const int DATA_BUFFER_SIZE = 1000;
const unsigned long MQTT_PUBLISH_INTERVAL = 5000;
const unsigned long CURE_UPDATE_INTERVAL = 1000;
const unsigned long OPTIMIZATION_INTERVAL = 30000;

// Machine Learning Parameters
float ml_input_buffer[50];
float ml_output_buffer[10];
int ml_feature_count = 0;
bool ml_model_loaded = false;

// Communication Buffers
char mqtt_buffer[2048];
char serial_buffer[1024];
String incoming_serial_data = "";

// Timing Variables
unsigned long last_mqtt_publish = 0;
unsigned long last_cure_update = 0;
unsigned long last_optimization = 0;
unsigned long last_digital_twin_sync = 0;

void setup() {
    Serial.begin(115200);
    Serial.println("ESP32 Composite Cure Kinetics Gateway Starting...");
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("SPIFFS initialization failed!");
        return;
    }
    
    // Initialize default material properties (AS4/3501-6 Carbon/Epoxy)
    initializeDefaultMaterial();
    
    // Initialize system states
    initializeSystemStates();
    
    // Initialize TensorFlow Lite
    initializeTensorFlowLite();
    
    // Initialize WiFi
    initializeWiFi();
    
    // Initialize MQTT
    initializeMQTT();
    
    // Initialize web server
    initializeWebServer();
    
    // Initialize time synchronization
    initializeTimeSync();
    
    Serial.println("ESP32 Cure Kinetics Gateway Ready!");
    Serial.println("Material: " + String(current_material.material_name));
    Serial.println("WiFi IP: " + WiFi.localIP().toString());
}

void loop() {
    // Handle WiFi and MQTT connections
    if (!WiFi.isConnected()) {
        reconnectWiFi();
    }
    
    if (!mqttClient.connected()) {
        reconnectMQTT();
    }
    mqttClient.loop();
    
    // Handle web server
    webServer.handleClient();
    
    // Process serial communication with Arduino Mega
    processSerialCommunication();
    
    // Update cure kinetics model
    if (millis() - last_cure_update > CURE_UPDATE_INTERVAL) {
        updateCureKineticsModel();
        last_cure_update = millis();
    }
    
    // Perform process optimization
    if (millis() - last_optimization > OPTIMIZATION_INTERVAL) {
        runProcessOptimization();
        last_optimization = millis();
    }
    
    // Synchronize digital twin
    if (millis() - last_digital_twin_sync > 10000) {
        synchronizeDigitalTwin();
        last_digital_twin_sync = millis();
    }
    
    // Publish MQTT data
    if (millis() - last_mqtt_publish > MQTT_PUBLISH_INTERVAL) {
        publishMQTTData();
        last_mqtt_publish = millis();
    }
    
    // Run machine learning inference
    if (ml_model_loaded && ml_feature_count >= 50) {
        runMLInference();
    }
    
    delay(100);
}

void initializeDefaultMaterial() {
    strcpy(current_material.material_name, "AS4/3501-6");
    current_material.arrhenius_a = 2.101e9;           // 1/s
    current_material.activation_energy = 69430;       // J/mol
    current_material.reaction_order_m = 0.47;
    current_material.reaction_order_n = 1.45;
    current_material.tg_uncured = -15.0;             // °C
    current_material.tg_fully_cured = 215.0;         // °C
    current_material.lambda_parameter = 0.87;
    current_material.viscosity_infinity = 5.11e-6;   // Pa·s
    current_material.viscosity_activation = 48000;   // J/mol
    current_material.gel_point_alpha = 0.47;
    current_material.vitrification_factor = 2.3;
    current_material.density_uncured = 1260;         // kg/m³
    current_material.density_cured = 1580;           // kg/m³
    current_material.thermal_expansion_coeff = 5.5e-5; // 1/K
    current_material.shrinkage_factor = 0.028;       // 2.8%
}

void initializeSystemStates() {
    // Initialize cure kinetics state
    cure_state.degree_of_cure = 0.0;
    cure_state.cure_rate = 0.0;
    cure_state.resin_viscosity = current_material.viscosity_infinity;
    cure_state.glass_transition_temp = current_material.tg_uncured;
    cure_state.gel_time = 0.0;
    cure_state.vitrification_time = 0.0;
    cure_state.gelation_reached = false;
    cure_state.vitrification_reached = false;
    cure_state.last_update = millis();
    cure_state.confidence_level = 0.95;
    
    // Initialize thermal state
    for (int i = 0; i < MAX_ZONES; i++) {
        thermal_state.zone_temperatures[i] = 25.0;
    }
    thermal_state.average_temperature = 25.0;
    thermal_state.temperature_uniformity = 0.0;
    thermal_state.heating_rate = 0.0;
    thermal_state.thermal_mass = 15000;              // J/K
    thermal_state.heat_capacity = 1200;              // J/(kg·K)
    thermal_state.last_update = millis();
    
    // Initialize process optimization
    process_opt.optimal_heating_rate = 2.0;          // °C/min
    process_opt.predicted_cycle_time = 480;          // minutes
    process_opt.energy_consumption = 0.0;
    process_opt.quality_score = 0.0;
    process_opt.residual_stress_level = 0.0;
    process_opt.warpage_prediction = 0.0;
    process_opt.optimization_iterations = 0;
    process_opt.cost_function_value = 1000.0;
    process_opt.optimization_complete = false;
    
    // Initialize digital twin
    digital_twin.data_points = 0;
    digital_twin.last_sync = millis();
    digital_twin.sync_enabled = true;
    digital_twin.model_accuracy = 0.0;
}

void initializeTensorFlowLite() {
    Serial.println("Initializing TensorFlow Lite...");
    
    // Load model from SPIFFS (placeholder - model would be stored separately)
    ml_model_loaded = false;  // Set to true when actual model is loaded
    
    if (ml_model_loaded) {
        static tflite::AllOpsResolver resolver;
        
        static tflite::MicroInterpreter static_interpreter(
            tflModel, resolver, tensor_arena, kTensorArenaSize, &tflErrorReporter);
        tflInterpreter = &static_interpreter;
        
        TfLiteStatus allocate_status = tflInterpreter->AllocateTensors();
        if (allocate_status != kTfLiteOk) {
            Serial.println("AllocateTensors() failed");
            ml_model_loaded = false;
            return;
        }
        
        input = tflInterpreter->input(0);
        output = tflInterpreter->output(0);
        
        Serial.println("TensorFlow Lite initialized successfully");
    } else {
        Serial.println("ML model not loaded - running in analytical mode");
    }
}

void initializeWiFi() {
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
        Serial.println("WiFi connected!");
        Serial.print("IP address: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println();
        Serial.println("WiFi connection failed!");
    }
}

void initializeMQTT() {
    mqttClient.setServer(mqtt_server, mqtt_port);
    mqttClient.setCallback(mqttCallback);
    reconnectMQTT();
}

void initializeWebServer() {
    // Serve cure kinetics data
    webServer.on("/api/cure-kinetics", HTTP_GET, []() {
        DynamicJsonDocument doc(1024);
        doc["degree_of_cure"] = cure_state.degree_of_cure;
        doc["cure_rate"] = cure_state.cure_rate;
        doc["resin_viscosity"] = cure_state.resin_viscosity;
        doc["glass_transition_temp"] = cure_state.glass_transition_temp;
        doc["gel_time"] = cure_state.gel_time;
        doc["vitrification_time"] = cure_state.vitrification_time;
        doc["gelation_reached"] = cure_state.gelation_reached;
        doc["vitrification_reached"] = cure_state.vitrification_reached;
        doc["confidence_level"] = cure_state.confidence_level;
        
        String response;
        serializeJson(doc, response);
        webServer.send(200, "application/json", response);
    });
    
    // Serve thermal data
    webServer.on("/api/thermal", HTTP_GET, []() {
        DynamicJsonDocument doc(2048);
        JsonArray zones = doc.createNestedArray("zone_temperatures");
        for (int i = 0; i < MAX_ZONES; i++) {
            zones.add(thermal_state.zone_temperatures[i]);
        }
        doc["average_temperature"] = thermal_state.average_temperature;
        doc["temperature_uniformity"] = thermal_state.temperature_uniformity;
        doc["heating_rate"] = thermal_state.heating_rate;
        
        String response;
        serializeJson(doc, response);
        webServer.send(200, "application/json", response);
    });
    
    // Serve optimization data
    webServer.on("/api/optimization", HTTP_GET, []() {
        DynamicJsonDocument doc(1024);
        doc["optimal_heating_rate"] = process_opt.optimal_heating_rate;
        doc["predicted_cycle_time"] = process_opt.predicted_cycle_time;
        doc["energy_consumption"] = process_opt.energy_consumption;
        doc["quality_score"] = process_opt.quality_score;
        doc["residual_stress_level"] = process_opt.residual_stress_level;
        doc["warpage_prediction"] = process_opt.warpage_prediction;
        doc["optimization_complete"] = process_opt.optimization_complete;
        
        String response;
        serializeJson(doc, response);
        webServer.send(200, "application/json", response);
    });
    
    webServer.begin();
    Serial.println("Web server started on port 80");
}

void initializeTimeSync() {
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
    Serial.println("Time synchronization initialized");
}

void processSerialCommunication() {
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
            parseSerialData(incoming_serial_data);
            incoming_serial_data = "";
        } else {
            incoming_serial_data += c;
        }
    }
}

void parseSerialData(String data) {
    DynamicJsonDocument doc(2048);
    DeserializationError error = deserializeJson(doc, data);
    
    if (error) {
        Serial.println("JSON parsing failed: " + String(error.c_str()));
        return;
    }
    
    // Update thermal state
    if (doc.containsKey("thermal_data")) {
        JsonObject thermal = doc["thermal_data"];
        JsonArray zones = thermal["zone_temperatures"];
        
        for (int i = 0; i < MAX_ZONES && i < zones.size(); i++) {
            thermal_state.zone_temperatures[i] = zones[i];
        }
        thermal_state.average_temperature = thermal["average_temperature"];
        thermal_state.temperature_uniformity = thermal["temperature_uniformity"];
        thermal_state.heating_rate = thermal["heating_rate"];
        thermal_state.last_update = millis();
    }
    
    // Update process parameters
    if (doc.containsKey("process_data")) {
        JsonObject process = doc["process_data"];
        // Process additional parameters as needed
    }
    
    // Prepare ML features
    if (ml_feature_count < 50) {
        ml_input_buffer[ml_feature_count++] = thermal_state.average_temperature;
        if (ml_feature_count < 50) {
            ml_input_buffer[ml_feature_count++] = cure_state.degree_of_cure;
        }
    }
}

void updateCureKineticsModel() {
    float dt = (millis() - cure_state.last_update) / 1000.0;  // Convert to seconds
    float temperature_kelvin = thermal_state.average_temperature + KELVIN_OFFSET;
    
    // Calculate Arrhenius rate constant
    float k = current_material.arrhenius_a * 
              exp(-current_material.activation_energy / (GAS_CONSTANT * temperature_kelvin));
    
    // Calculate cure rate using Kamal-Sourour model
    float alpha = cure_state.degree_of_cure;
    cure_state.cure_rate = k * pow(alpha, current_material.reaction_order_m) * 
                           pow(1.0 - alpha, current_material.reaction_order_n);
    
    // Update degree of cure
    cure_state.degree_of_cure += cure_state.cure_rate * dt;
    cure_state.degree_of_cure = constrain(cure_state.degree_of_cure, 0.0, 1.0);
    
    // Calculate glass transition temperature using DiBenedetto equation
    cure_state.glass_transition_temp = current_material.tg_uncured + 
        (current_material.tg_fully_cured - current_material.tg_uncured) * 
        current_material.lambda_parameter * alpha / 
        (1.0 + (current_material.lambda_parameter - 1.0) * alpha);
    
    // Calculate resin viscosity
    float viscosity_temp_term = exp(current_material.viscosity_activation / 
                                   (GAS_CONSTANT * temperature_kelvin));
    float viscosity_cure_term = pow(current_material.gel_point_alpha / 
                                   (current_material.gel_point_alpha - alpha), 
                                   current_material.vitrification_factor);
    cure_state.resin_viscosity = current_material.viscosity_infinity * 
                                viscosity_temp_term * viscosity_cure_term;
    
    // Check gelation point
    if (!cure_state.gelation_reached && alpha >= current_material.gel_point_alpha) {
        cure_state.gelation_reached = true;
        cure_state.gel_time = millis() / 1000.0;
        Serial.println("Gelation point reached at alpha = " + String(alpha));
    }
    
    // Check vitrification
    if (!cure_state.vitrification_reached && 
        thermal_state.average_temperature <= cure_state.glass_transition_temp + 5.0) {
        cure_state.vitrification_reached = true;
        cure_state.vitrification_time = millis() / 1000.0;
        Serial.println("Vitrification reached at T = " + String(thermal_state.average_temperature) + 
                      "°C, Tg = " + String(cure_state.glass_transition_temp) + "°C");
    }
    
    cure_state.last_update = millis();
}

void runProcessOptimization() {
    process_opt.optimization_iterations++;
    
    // Calculate optimal heating rate based on cure kinetics
    float target_cure_rate = 0.001;  // 1/s optimal cure rate
    float current_k = current_material.arrhenius_a * 
                     exp(-current_material.activation_energy / 
                         (GAS_CONSTANT * (thermal_state.average_temperature + KELVIN_OFFSET)));
    
    float alpha = cure_state.degree_of_cure;
    float current_cure_potential = pow(alpha, current_material.reaction_order_m) * 
                                  pow(1.0 - alpha, current_material.reaction_order_n);
    
    if (current_cure_potential > 0) {
        float required_k = target_cure_rate / current_cure_potential;
        float required_temp = -current_material.activation_energy / 
                             (GAS_CONSTANT * log(required_k / current_material.arrhenius_a)) - 
                             KELVIN_OFFSET;
        
        // Calculate optimal heating rate
        float temp_difference = required_temp - thermal_state.average_temperature;
        process_opt.optimal_heating_rate = constrain(temp_difference / 5.0, 0.5, 5.0);  // °C/min
    }
    
    // Predict cycle time
    float remaining_cure = 1.0 - cure_state.degree_of_cure;
    if (cure_state.cure_rate > 0) {
        process_opt.predicted_cycle_time = (remaining_cure / cure_state.cure_rate) / 60.0;  // minutes
    }
    
    // Calculate energy consumption
    float power_per_zone = 3000;  // Watts per heating zone
    float efficiency = 0.85;
    process_opt.energy_consumption = (MAX_ZONES * power_per_zone * 
                                     process_opt.predicted_cycle_time / 60.0 / efficiency) / 1000.0;  // kWh
    
    // Calculate quality score (0-100)
    float temp_uniformity_score = 100 * exp(-abs(thermal_state.temperature_uniformity) / 5.0);
    float cure_rate_score = 100 * exp(-abs(cure_state.cure_rate - target_cure_rate) / target_cure_rate);
    process_opt.quality_score = (temp_uniformity_score + cure_rate_score) / 2.0;
    
    // Predict residual stress
    float thermal_stress = current_material.thermal_expansion_coeff * 
                          abs(thermal_state.average_temperature - 25.0) * 200000;  // MPa (E=200GPa)
    float cure_stress = current_material.shrinkage_factor * 200000;  // MPa
    process_opt.residual_stress_level = thermal_stress + cure_stress;
    
    // Predict warpage
    process_opt.warpage_prediction = process_opt.residual_stress_level * 0.001 * 
                                    thermal_state.temperature_uniformity;  // mm
    
    // Update cost function
    float previous_cost = process_opt.cost_function_value;
    process_opt.cost_function_value = process_opt.energy_consumption * 10 + 
                                     process_opt.residual_stress_level * 0.1 + 
                                     abs(process_opt.warpage_prediction) * 100 + 
                                     (100 - process_opt.quality_score);
    
    // Check optimization convergence
    if (abs(process_opt.cost_function_value - previous_cost) < 0.1) {
        process_opt.optimization_complete = true;
    }
    
    Serial.println("Optimization iteration " + String(process_opt.optimization_iterations) + 
                  " - Cost: " + String(process_opt.cost_function_value));
}

void synchronizeDigitalTwin() {
    if (!digital_twin.sync_enabled) return;
    
    // Store current data point in virtual arrays
    int idx = digital_twin.data_points % DATA_BUFFER_SIZE;
    
    for (int i = 0; i < MAX_ZONES; i++) {
        digital_twin.virtual_temperature_profile[i][idx] = thermal_state.zone_temperatures[i];
    }
    digital_twin.virtual_cure_progression[idx] = cure_state.degree_of_cure;
    
    // Update 2D stress and warpage maps (simplified simulation)
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 100; j++) {
            float x_factor = sin(2 * PI * i / 100.0);
            float y_factor = cos(2 * PI * j / 100.0);
            
            digital_twin.virtual_stress_field[i][j] = process_opt.residual_stress_level * 
                                                     (1.0 + 0.1 * x_factor * y_factor);
            digital_twin.virtual_warpage_map[i][j] = process_opt.warpage_prediction * 
                                                    (1.0 + 0.05 * x_factor * y_factor);
        }
    }
    
    digital_twin.data_points++;
    digital_twin.last_sync = millis();
    
    // Calculate model accuracy based on prediction vs actual
    float prediction_error = abs(thermal_state.average_temperature - 
                                getPredictedTemperature()) / thermal_state.average_temperature;
    digital_twin.model_accuracy = 100 * (1.0 - prediction_error);
    
    Serial.println("Digital twin synchronized - Accuracy: " + String(digital_twin.model_accuracy) + "%");
}

float getPredictedTemperature() {
    // Simplified temperature prediction based on heating rate
    return thermal_state.average_temperature + 
           (process_opt.optimal_heating_rate * (millis() - thermal_state.last_update) / 60000.0);
}

void runMLInference() {
    if (!ml_model_loaded) return;
    
    // Copy features to input tensor
    for (int i = 0; i < 50; i++) {
        input->data.f[i] = ml_input_buffer[i];
    }
    
    // Run inference
    TfLiteStatus invoke_status = tflInterpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        Serial.println("Invoke failed");
        return;
    }
    
    // Process output
    for (int i = 0; i < 10; i++) {
        ml_output_buffer[i] = output->data.f[i];
    }
    
    // Update confidence level based on ML prediction
    cure_state.confidence_level = ml_output_buffer[0];
    
    // Reset feature buffer
    ml_feature_count = 0;
    
    Serial.println("ML inference completed - Confidence: " + String(cure_state.confidence_level));
}

void publishMQTTData() {
    if (!mqttClient.connected()) return;
    
    DynamicJsonDocument doc(2048);
    doc["timestamp"] = millis();
    doc["device_id"] = device_id;
    
    // Cure kinetics data
    JsonObject cure = doc.createNestedObject("cure_kinetics");
    cure["degree_of_cure"] = cure_state.degree_of_cure;
    cure["cure_rate"] = cure_state.cure_rate;
    cure["resin_viscosity"] = cure_state.resin_viscosity;
    cure["glass_transition_temp"] = cure_state.glass_transition_temp;
    cure["gelation_reached"] = cure_state.gelation_reached;
    cure["vitrification_reached"] = cure_state.vitrification_reached;
    cure["confidence_level"] = cure_state.confidence_level;
    
    // Thermal data
    JsonObject thermal = doc.createNestedObject("thermal");
    JsonArray zones = thermal.createNestedArray("zone_temperatures");
    for (int i = 0; i < MAX_ZONES; i++) {
        zones.add(thermal_state.zone_temperatures[i]);
    }
    thermal["average_temperature"] = thermal_state.average_temperature;
    thermal["temperature_uniformity"] = thermal_state.temperature_uniformity;
    thermal["heating_rate"] = thermal_state.heating_rate;
    
    // Optimization data
    JsonObject optimization = doc.createNestedObject("optimization");
    optimization["optimal_heating_rate"] = process_opt.optimal_heating_rate;
    optimization["predicted_cycle_time"] = process_opt.predicted_cycle_time;
    optimization["energy_consumption"] = process_opt.energy_consumption;
    optimization["quality_score"] = process_opt.quality_score;
    optimization["residual_stress_level"] = process_opt.residual_stress_level;
    optimization["warpage_prediction"] = process_opt.warpage_prediction;
    
    // Digital twin data
    JsonObject twin = doc.createNestedObject("digital_twin");
    twin["model_accuracy"] = digital_twin.model_accuracy;
    twin["data_points"] = digital_twin.data_points;
    twin["sync_enabled"] = digital_twin.sync_enabled;
    
    String payload;
    serializeJson(doc, payload);
    
    mqttClient.publish("composite/cure-kinetics/data", payload.c_str());
    mqttClient.publish("composite/cure-kinetics/status", "online");
    
    // Send control recommendations back to Arduino
    sendControlRecommendations();
}

void sendControlRecommendations() {
    DynamicJsonDocument doc(1024);
    doc["type"] = "control_recommendations";
    doc["optimal_heating_rate"] = process_opt.optimal_heating_rate;
    doc["target_temperature"] = thermal_state.average_temperature + 
                               (process_opt.optimal_heating_rate * 5.0 / 60.0);  // 5-minute prediction
    doc["quality_alert"] = process_opt.quality_score < 80.0;
    doc["gelation_warning"] = !cure_state.gelation_reached && 
                             cure_state.degree_of_cure > (current_material.gel_point_alpha - 0.05);
    doc["vitrification_warning"] = !cure_state.vitrification_reached && 
                                  (thermal_state.average_temperature < cure_state.glass_transition_temp + 10.0);
    
    String response;
    serializeJson(doc, response);
    Serial.println(response);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("MQTT message received: " + String(topic) + " - " + message);
    
    // Handle material changes
    if (String(topic) == "composite/cure-kinetics/material") {
        updateMaterialProperties(message);
    }
    
    // Handle process commands
    if (String(topic) == "composite/cure-kinetics/command") {
        processCommand(message);
    }
}

void updateMaterialProperties(String materialData) {
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, materialData);
    
    if (!error) {
        if (doc.containsKey("material_name")) {
            strcpy(current_material.material_name, doc["material_name"]);
        }
        if (doc.containsKey("arrhenius_a")) {
            current_material.arrhenius_a = doc["arrhenius_a"];
        }
        if (doc.containsKey("activation_energy")) {
            current_material.activation_energy = doc["activation_energy"];
        }
        // Update other properties as needed
        
        Serial.println("Material properties updated: " + String(current_material.material_name));
    }
}

void processCommand(String command) {
    DynamicJsonDocument doc(512);
    DeserializationError error = deserializeJson(doc, command);
    
    if (!error) {
        String cmd = doc["command"];
        
        if (cmd == "reset_cure") {
            cure_state.degree_of_cure = 0.0;
            cure_state.gelation_reached = false;
            cure_state.vitrification_reached = false;
            Serial.println("Cure state reset");
        } else if (cmd == "sync_digital_twin") {
            digital_twin.sync_enabled = doc["enabled"];
            Serial.println("Digital twin sync: " + String(digital_twin.sync_enabled));
        } else if (cmd == "optimize_process") {
            process_opt.optimization_complete = false;
            process_opt.optimization_iterations = 0;
            Serial.println("Process optimization started");
        }
    }
}

void reconnectWiFi() {
    if (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(ssid, password);
        Serial.println("Reconnecting to WiFi...");
    }
}

void reconnectMQTT() {
    while (!mqttClient.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        if (mqttClient.connect(device_id)) {
            Serial.println("connected");
            
            // Subscribe to topics
            mqttClient.subscribe("composite/cure-kinetics/material");
            mqttClient.subscribe("composite/cure-kinetics/command");
            mqttClient.subscribe("composite/cure-kinetics/config");
            
            // Publish online status
            mqttClient.publish("composite/cure-kinetics/status", "online");
            
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}