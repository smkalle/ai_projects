/*
 * Program 17: ESP32 Analytics Gateway for PCM Controller
 * Arduino Zero to Hero v2.0 - Track 1: Thermal Systems Engineering
 * 
 * Advanced analytics gateway with machine learning for PCM optimization
 * - Real-time data processing and analytics
 * - TensorFlow Lite edge inference
 * - Cloud integration and remote monitoring
 * - Predictive maintenance algorithms
 * - Performance optimization
 * 
 * Hardware: ESP32 Development Board
 * 
 * Author: Arduino Zero to Hero Team
 * Date: 2024
 * License: MIT
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <SPIFFS.h>
#include <HTTPClient.h>
#include <TensorFlowLite_ESP32.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <tensorflow/lite/version.h>

// Network Configuration
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "mqtt.broker.com";
const int mqtt_port = 1883;
const char* cloud_endpoint = "https://api.thermalcloud.com";
const char* api_key = "your_api_key";

// PCM Analytics Configuration
#define NUM_CONTAINERS 4
#define MAX_HISTORY_SIZE 1000
#define PREDICTION_WINDOW 10
#define ANALYTICS_INTERVAL 30000  // 30 seconds
#define CLOUD_SYNC_INTERVAL 300000 // 5 minutes

// ML Model Configuration
#define TENSOR_ARENA_SIZE 30000
#define ML_INPUT_SIZE 20
#define ML_OUTPUT_SIZE 8

// Global objects
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);
WebServer web_server(80);
WebSocketsServer websocket_server(81);
HTTPClient http_client;

// TensorFlow Lite objects
tflite::MicroErrorReporter tflite_error_reporter;
const tflite::Model* tflite_model = nullptr;
tflite::MicroInterpreter* tflite_interpreter = nullptr;
TfLiteTensor* tflite_input = nullptr;
TfLiteTensor* tflite_output = nullptr;
tflite::AllOpsResolver tflite_resolver;

// Tensor arena for TensorFlow Lite
uint8_t tensor_arena[TENSOR_ARENA_SIZE];

// PCM Data Structure
struct PCMData {
    unsigned long timestamp;
    float temperature_top;
    float temperature_bottom;
    float mass;
    float heat_flux;
    float power_input;
    float enthalpy;
    float phase_fraction;
    float storage_efficiency;
    String phase_state;
};

// Analytics Data Structure
struct AnalyticsData {
    float effectiveness;
    float efficiency;
    float response_time;
    float stability_index;
    float energy_density;
    float thermal_conductivity;
    float heat_transfer_coefficient;
    float performance_score;
};

// System State
PCMData pcm_data[NUM_CONTAINERS];
PCMData history[NUM_CONTAINERS][MAX_HISTORY_SIZE];
int history_index[NUM_CONTAINERS] = {0};
AnalyticsData analytics[NUM_CONTAINERS];
bool system_ready = false;
unsigned long last_analytics_time = 0;
unsigned long last_cloud_sync = 0;
unsigned long last_ml_prediction = 0;

// Machine Learning Class
class PCMAnalyticsML {
private:
    float prediction_buffer[NUM_CONTAINERS][PREDICTION_WINDOW];
    float feature_buffer[ML_INPUT_SIZE];
    bool model_loaded = false;
    
public:
    PCMAnalyticsML() {
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            for (int j = 0; j < PREDICTION_WINDOW; j++) {
                prediction_buffer[i][j] = 0.0;
            }
        }
    }
    
    bool loadModel() {
        // Load TensorFlow Lite model from SPIFFS
        File model_file = SPIFFS.open("/pcm_model.tflite", "r");
        if (!model_file) {
            Serial.println("Failed to open model file");
            return false;
        }
        
        size_t model_size = model_file.size();
        uint8_t* model_data = (uint8_t*)malloc(model_size);
        model_file.readBytes((char*)model_data, model_size);
        model_file.close();
        
        // Initialize TensorFlow Lite model
        tflite_model = tflite::GetModel(model_data);
        if (tflite_model->version() != TFLITE_SCHEMA_VERSION) {
            Serial.println("Model schema version mismatch");
            free(model_data);
            return false;
        }
        
        // Create interpreter
        static tflite::MicroInterpreter static_interpreter(
            tflite_model, tflite_resolver, tensor_arena, TENSOR_ARENA_SIZE, &tflite_error_reporter);
        tflite_interpreter = &static_interpreter;
        
        if (tflite_interpreter->AllocateTensors() != kTfLiteOk) {
            Serial.println("Failed to allocate tensors");
            free(model_data);
            return false;
        }
        
        // Get input and output tensors
        tflite_input = tflite_interpreter->input(0);
        tflite_output = tflite_interpreter->output(0);
        
        model_loaded = true;
        Serial.println("✅ ML model loaded successfully");
        return true;
    }
    
    void predictPhaseChange(int container) {
        if (!model_loaded) return;
        
        // Prepare input features
        prepareFeatures(container);
        
        // Copy features to input tensor
        for (int i = 0; i < ML_INPUT_SIZE; i++) {
            tflite_input->data.f[i] = feature_buffer[i];
        }
        
        // Run inference
        if (tflite_interpreter->Invoke() != kTfLiteOk) {
            Serial.println("Failed to invoke ML model");
            return;
        }
        
        // Process output
        processMLOutput(container);
    }
    
    void prepareFeatures(int container) {
        // Feature engineering for ML model
        int idx = 0;
        
        // Current measurements
        feature_buffer[idx++] = pcm_data[container].temperature_top;
        feature_buffer[idx++] = pcm_data[container].temperature_bottom;
        feature_buffer[idx++] = pcm_data[container].mass;
        feature_buffer[idx++] = pcm_data[container].heat_flux;
        feature_buffer[idx++] = pcm_data[container].power_input;
        feature_buffer[idx++] = pcm_data[container].phase_fraction;
        feature_buffer[idx++] = pcm_data[container].storage_efficiency;
        
        // Temperature gradients
        feature_buffer[idx++] = calculateTemperatureGradient(container);
        feature_buffer[idx++] = calculateHeatFluxGradient(container);
        
        // Statistical features
        feature_buffer[idx++] = calculateMeanTemperature(container);
        feature_buffer[idx++] = calculateTemperatureVariance(container);
        feature_buffer[idx++] = calculateHeatFluxMean(container);
        feature_buffer[idx++] = calculateHeatFluxVariance(container);
        
        // Time-based features
        feature_buffer[idx++] = calculateDwellTime(container);
        feature_buffer[idx++] = calculateCycleCount(container);
        
        // Derived features
        feature_buffer[idx++] = calculateThermalDiffusivity(container);
        feature_buffer[idx++] = calculateBiotNumber(container);
        feature_buffer[idx++] = calculateFourierNumber(container);
        
        // System state
        feature_buffer[idx++] = analytics[container].effectiveness;
        feature_buffer[idx++] = analytics[container].performance_score;
    }
    
    void processMLOutput(int container) {
        // Process ML model output
        float* output = tflite_output->data.f;
        
        // Predictions: [phase_change_probability, optimal_power, efficiency_prediction, 
        //              time_to_phase_change, thermal_conductivity, heat_capacity, 
        //              optimal_temperature, maintenance_score]
        
        float phase_change_prob = output[0];
        float optimal_power = output[1];
        float predicted_efficiency = output[2];
        float time_to_phase_change = output[3];
        float thermal_conductivity = output[4];
        float heat_capacity = output[5];
        float optimal_temperature = output[6];
        float maintenance_score = output[7];
        
        // Update analytics with predictions
        analytics[container].thermal_conductivity = thermal_conductivity;
        analytics[container].efficiency = predicted_efficiency;
        
        // Send predictions to Arduino
        sendPredictions(container, phase_change_prob, optimal_power, predicted_efficiency, 
                       time_to_phase_change, optimal_temperature, maintenance_score);
        
        // Log predictions
        logMLPredictions(container, output);
    }
    
    float calculateTemperatureGradient(int container) {
        if (history_index[container] < 10) return 0.0;
        
        int current_idx = (history_index[container] - 1 + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
        int prev_idx = (history_index[container] - 10 + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
        
        float dt = (history[container][current_idx].timestamp - history[container][prev_idx].timestamp) / 1000.0;
        float dT = history[container][current_idx].temperature_top - history[container][prev_idx].temperature_top;
        
        return dT / dt; // °C/s
    }
    
    float calculateHeatFluxGradient(int container) {
        if (history_index[container] < 10) return 0.0;
        
        int current_idx = (history_index[container] - 1 + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
        int prev_idx = (history_index[container] - 10 + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
        
        float dt = (history[container][current_idx].timestamp - history[container][prev_idx].timestamp) / 1000.0;
        float dq = history[container][current_idx].heat_flux - history[container][prev_idx].heat_flux;
        
        return dq / dt; // W/m²/s
    }
    
    float calculateMeanTemperature(int container) {
        if (history_index[container] < 10) return pcm_data[container].temperature_top;
        
        float sum = 0.0;
        int count = min(50, history_index[container]);
        
        for (int i = 0; i < count; i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            sum += history[container][idx].temperature_top;
        }
        
        return sum / count;
    }
    
    float calculateTemperatureVariance(int container) {
        if (history_index[container] < 10) return 0.0;
        
        float mean = calculateMeanTemperature(container);
        float sum_sq = 0.0;
        int count = min(50, history_index[container]);
        
        for (int i = 0; i < count; i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            float diff = history[container][idx].temperature_top - mean;
            sum_sq += diff * diff;
        }
        
        return sum_sq / count;
    }
    
    float calculateHeatFluxMean(int container) {
        if (history_index[container] < 10) return pcm_data[container].heat_flux;
        
        float sum = 0.0;
        int count = min(50, history_index[container]);
        
        for (int i = 0; i < count; i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            sum += history[container][idx].heat_flux;
        }
        
        return sum / count;
    }
    
    float calculateHeatFluxVariance(int container) {
        if (history_index[container] < 10) return 0.0;
        
        float mean = calculateHeatFluxMean(container);
        float sum_sq = 0.0;
        int count = min(50, history_index[container]);
        
        for (int i = 0; i < count; i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            float diff = history[container][idx].heat_flux - mean;
            sum_sq += diff * diff;
        }
        
        return sum_sq / count;
    }
    
    float calculateDwellTime(int container) {
        // Calculate time spent in current phase
        if (history_index[container] < 10) return 0.0;
        
        String current_phase = pcm_data[container].phase_state;
        float dwell_time = 0.0;
        
        for (int i = 0; i < min(100, history_index[container]); i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            if (history[container][idx].phase_state == current_phase) {
                dwell_time += 5.0; // 5 second intervals
            } else {
                break;
            }
        }
        
        return dwell_time;
    }
    
    float calculateCycleCount(int container) {
        // Count phase change cycles
        if (history_index[container] < 20) return 0.0;
        
        int cycles = 0;
        String last_phase = "";
        
        for (int i = 0; i < min(500, history_index[container]); i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            String phase = history[container][idx].phase_state;
            
            if (phase != last_phase && last_phase != "") {
                cycles++;
            }
            last_phase = phase;
        }
        
        return cycles;
    }
    
    float calculateThermalDiffusivity(int container) {
        // Simplified thermal diffusivity calculation
        float thermal_conductivity = 0.2; // W/m·K (typical for PCM)
        float density = 800; // kg/m³
        float specific_heat = 2000; // J/kg·K
        
        return thermal_conductivity / (density * specific_heat);
    }
    
    float calculateBiotNumber(int container) {
        // Biot number for heat transfer analysis
        float heat_transfer_coeff = 25.0; // W/m²·K
        float characteristic_length = 0.05; // m
        float thermal_conductivity = 0.2; // W/m·K
        
        return (heat_transfer_coeff * characteristic_length) / thermal_conductivity;
    }
    
    float calculateFourierNumber(int container) {
        // Fourier number for transient analysis
        float thermal_diffusivity = calculateThermalDiffusivity(container);
        float time = 300.0; // seconds
        float characteristic_length = 0.05; // m
        
        return (thermal_diffusivity * time) / (characteristic_length * characteristic_length);
    }
};

// Advanced Analytics Class
class AdvancedAnalytics {
private:
    float performance_history[NUM_CONTAINERS][100];
    int perf_history_index[NUM_CONTAINERS];
    
public:
    AdvancedAnalytics() {
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            perf_history_index[i] = 0;
        }
    }
    
    void analyzePerformance(int container) {
        // Calculate comprehensive performance metrics
        analytics[container].effectiveness = calculateEffectiveness(container);
        analytics[container].efficiency = calculateEfficiency(container);
        analytics[container].response_time = calculateResponseTime(container);
        analytics[container].stability_index = calculateStabilityIndex(container);
        analytics[container].energy_density = calculateEnergyDensity(container);
        analytics[container].heat_transfer_coefficient = calculateHeatTransferCoeff(container);
        analytics[container].performance_score = calculatePerformanceScore(container);
        
        // Store performance history
        performance_history[container][perf_history_index[container]] = analytics[container].performance_score;
        perf_history_index[container] = (perf_history_index[container] + 1) % 100;
        
        // Generate insights
        generateInsights(container);
    }
    
    float calculateEffectiveness(int container) {
        // NTU-effectiveness method
        float target_temp = 60.0; // °C
        float inlet_temp = 20.0; // °C
        float outlet_temp = pcm_data[container].temperature_top;
        
        float effectiveness = (outlet_temp - inlet_temp) / (target_temp - inlet_temp);
        return constrain(effectiveness, 0.0, 1.0);
    }
    
    float calculateEfficiency(int container) {
        // Energy storage efficiency
        float useful_energy = pcm_data[container].enthalpy;
        float input_energy = pcm_data[container].power_input * 300.0; // 5 minutes
        
        if (input_energy > 0) {
            return (useful_energy / input_energy) * 100.0;
        }
        return 0.0;
    }
    
    float calculateResponseTime(int container) {
        // Time to reach 90% of setpoint
        // This requires historical analysis - simplified here
        return 180.0; // seconds
    }
    
    float calculateStabilityIndex(int container) {
        // Temperature stability measure
        float variance = calculateTemperatureVariance(container);
        return 1.0 / (1.0 + variance);
    }
    
    float calculateEnergyDensity(int container) {
        // Energy density (J/kg)
        if (pcm_data[container].mass > 0) {
            return pcm_data[container].enthalpy / pcm_data[container].mass;
        }
        return 0.0;
    }
    
    float calculateHeatTransferCoeff(int container) {
        // Heat transfer coefficient calculation
        float q = pcm_data[container].heat_flux;
        float delta_T = pcm_data[container].temperature_top - pcm_data[container].temperature_bottom;
        
        if (delta_T > 0) {
            return q / delta_T;
        }
        return 0.0;
    }
    
    float calculatePerformanceScore(int container) {
        // Weighted performance score
        float score = 0.0;
        score += analytics[container].effectiveness * 0.25;
        score += (analytics[container].efficiency / 100.0) * 0.25;
        score += analytics[container].stability_index * 0.20;
        score += constrain(analytics[container].energy_density / 300000.0, 0.0, 1.0) * 0.15;
        score += constrain(analytics[container].heat_transfer_coefficient / 100.0, 0.0, 1.0) * 0.15;
        
        return score * 100.0;
    }
    
    float calculateTemperatureVariance(int container) {
        if (history_index[container] < 10) return 0.0;
        
        float mean = 0.0;
        int count = min(50, history_index[container]);
        
        // Calculate mean
        for (int i = 0; i < count; i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            mean += history[container][idx].temperature_top;
        }
        mean /= count;
        
        // Calculate variance
        float variance = 0.0;
        for (int i = 0; i < count; i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            float diff = history[container][idx].temperature_top - mean;
            variance += diff * diff;
        }
        
        return variance / count;
    }
    
    void generateInsights(int container) {
        Serial.println("📊 Advanced Analytics - Container " + String(container));
        Serial.println("   Performance Score: " + String(analytics[container].performance_score, 1) + "%");
        Serial.println("   Effectiveness: " + String(analytics[container].effectiveness, 3));
        Serial.println("   Efficiency: " + String(analytics[container].efficiency, 1) + "%");
        Serial.println("   Energy Density: " + String(analytics[container].energy_density / 1000.0, 1) + " kJ/kg");
        Serial.println("   Heat Transfer Coeff: " + String(analytics[container].heat_transfer_coefficient, 1) + " W/m²·K");
        Serial.println("   Stability Index: " + String(analytics[container].stability_index, 3));
        
        // Generate recommendations
        if (analytics[container].performance_score < 70.0) {
            Serial.println("   🔧 Recommendation: Optimize operating conditions");
        }
        if (analytics[container].efficiency < 60.0) {
            Serial.println("   ⚡ Recommendation: Reduce thermal losses");
        }
        if (analytics[container].stability_index < 0.8) {
            Serial.println("   🎯 Recommendation: Improve temperature control");
        }
    }
};

// Cloud Integration Class
class CloudIntegration {
private:
    String device_id;
    String session_id;
    
public:
    CloudIntegration() {
        device_id = "pcm_controller_" + String(ESP.getChipId());
        session_id = String(millis());
    }
    
    void syncData() {
        if (WiFi.status() != WL_CONNECTED) return;
        
        // Prepare data payload
        StaticJsonDocument<2048> doc;
        doc["device_id"] = device_id;
        doc["session_id"] = session_id;
        doc["timestamp"] = millis();
        
        JsonArray containers = doc.createNestedArray("containers");
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            JsonObject container = containers.createNestedObject();
            container["id"] = i;
            container["temperature_top"] = pcm_data[i].temperature_top;
            container["temperature_bottom"] = pcm_data[i].temperature_bottom;
            container["mass"] = pcm_data[i].mass;
            container["heat_flux"] = pcm_data[i].heat_flux;
            container["power_input"] = pcm_data[i].power_input;
            container["enthalpy"] = pcm_data[i].enthalpy;
            container["phase_fraction"] = pcm_data[i].phase_fraction;
            container["phase_state"] = pcm_data[i].phase_state;
            container["storage_efficiency"] = pcm_data[i].storage_efficiency;
            container["performance_score"] = analytics[i].performance_score;
            container["effectiveness"] = analytics[i].effectiveness;
            container["efficiency"] = analytics[i].efficiency;
            container["energy_density"] = analytics[i].energy_density;
        }
        
        // Send to cloud
        String payload;
        serializeJson(doc, payload);
        
        http_client.begin(String(cloud_endpoint) + "/api/pcm/data");
        http_client.addHeader("Content-Type", "application/json");
        http_client.addHeader("Authorization", "Bearer " + String(api_key));
        
        int response_code = http_client.POST(payload);
        
        if (response_code == 200) {
            Serial.println("✅ Data synced to cloud");
        } else {
            Serial.println("❌ Cloud sync failed: " + String(response_code));
        }
        
        http_client.end();
    }
    
    void downloadModelUpdates() {
        if (WiFi.status() != WL_CONNECTED) return;
        
        // Check for model updates
        http_client.begin(String(cloud_endpoint) + "/api/models/pcm/latest");
        http_client.addHeader("Authorization", "Bearer " + String(api_key));
        
        int response_code = http_client.GET();
        
        if (response_code == 200) {
            String response = http_client.getString();
            StaticJsonDocument<512> doc;
            deserializeJson(doc, response);
            
            String model_version = doc["version"];
            String model_url = doc["download_url"];
            
            // Download and update model if newer version available
            if (model_version != getStoredModelVersion()) {
                downloadAndUpdateModel(model_url, model_version);
            }
        }
        
        http_client.end();
    }
    
    String getStoredModelVersion() {
        File version_file = SPIFFS.open("/model_version.txt", "r");
        if (version_file) {
            String version = version_file.readString();
            version_file.close();
            return version;
        }
        return "0.0.0";
    }
    
    void downloadAndUpdateModel(String url, String version) {
        Serial.println("📥 Downloading model update: " + version);
        
        http_client.begin(url);
        int response_code = http_client.GET();
        
        if (response_code == 200) {
            File model_file = SPIFFS.open("/pcm_model.tflite", "w");
            if (model_file) {
                http_client.writeToStream(&model_file);
                model_file.close();
                
                // Update version file
                File version_file = SPIFFS.open("/model_version.txt", "w");
                if (version_file) {
                    version_file.print(version);
                    version_file.close();
                }
                
                Serial.println("✅ Model updated successfully");
            }
        }
        
        http_client.end();
    }
};

// Global objects
PCMAnalyticsML ml_analytics;
AdvancedAnalytics advanced_analytics;
CloudIntegration cloud_integration;

void setup() {
    Serial.begin(115200);
    Serial2.begin(115200, SERIAL_8N1, 16, 17); // Communication with Arduino
    delay(2000);
    
    Serial.println("🧠 PCM ANALYTICS GATEWAY STARTED!");
    Serial.println("🧠 Advanced AI-driven thermal energy storage analytics");
    Serial.println("================================================================");
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("❌ SPIFFS initialization failed");
        return;
    }
    Serial.println("✅ SPIFFS initialized");
    
    // Connect to WiFi
    connectToWiFi();
    
    // Initialize MQTT
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    connectToMQTT();
    
    // Initialize web server
    setupWebServer();
    
    // Initialize WebSocket server
    websocket_server.begin();
    websocket_server.onEvent(webSocketEvent);
    
    // Load ML model
    ml_analytics.loadModel();
    
    // Download latest model from cloud
    cloud_integration.downloadModelUpdates();
    
    Serial.println("🎯 Analytics Gateway Ready");
    system_ready = true;
}

void loop() {
    if (!system_ready) return;
    
    // Handle web server
    web_server.handleClient();
    
    // Handle WebSocket
    websocket_server.loop();
    
    // Handle MQTT
    if (mqtt_client.connected()) {
        mqtt_client.loop();
    } else {
        connectToMQTT();
    }
    
    // Process serial data from Arduino
    processArduinoData();
    
    // Perform analytics
    if (millis() - last_analytics_time > ANALYTICS_INTERVAL) {
        performAnalytics();
        last_analytics_time = millis();
    }
    
    // ML predictions
    if (millis() - last_ml_prediction > 10000) { // Every 10 seconds
        performMLPredictions();
        last_ml_prediction = millis();
    }
    
    // Cloud synchronization
    if (millis() - last_cloud_sync > CLOUD_SYNC_INTERVAL) {
        cloud_integration.syncData();
        last_cloud_sync = millis();
    }
    
    delay(100);
}

void connectToWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("✅ WiFi connected: " + WiFi.localIP().toString());
    } else {
        Serial.println();
        Serial.println("❌ WiFi connection failed");
    }
}

void connectToMQTT() {
    while (!mqtt_client.connected()) {
        if (mqtt_client.connect("PCMAnalyticsGateway")) {
            Serial.println("✅ MQTT connected");
            mqtt_client.subscribe("pcm/data");
            mqtt_client.subscribe("pcm/commands");
        } else {
            Serial.println("❌ MQTT connection failed");
            delay(5000);
        }
    }
}

void processArduinoData() {
    if (Serial2.available()) {
        String data = Serial2.readStringUntil('\n');
        data.trim();
        
        // Parse JSON data from Arduino
        StaticJsonDocument<1024> doc;
        DeserializationError error = deserializeJson(doc, data);
        
        if (error) {
            Serial.println("JSON parsing failed: " + String(error.c_str()));
            return;
        }
        
        // Update PCM data
        JsonArray containers = doc["containers"];
        for (int i = 0; i < NUM_CONTAINERS && i < containers.size(); i++) {
            JsonObject container = containers[i];
            
            pcm_data[i].timestamp = millis();
            pcm_data[i].temperature_top = container["temperature_top"];
            pcm_data[i].temperature_bottom = container["temperature_bottom"];
            pcm_data[i].mass = container["mass"];
            pcm_data[i].heat_flux = container["heat_flux"];
            pcm_data[i].power_input = container["power_input"];
            pcm_data[i].enthalpy = container["enthalpy"];
            pcm_data[i].phase_fraction = container["phase_fraction"];
            pcm_data[i].storage_efficiency = container["storage_efficiency"];
            pcm_data[i].phase_state = container["phase_state"].as<String>();
            
            // Store in history
            history[i][history_index[i]] = pcm_data[i];
            history_index[i] = (history_index[i] + 1) % MAX_HISTORY_SIZE;
        }
        
        // Broadcast to WebSocket clients
        broadcastDataToClients();
    }
}

void performAnalytics() {
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        advanced_analytics.analyzePerformance(i);
    }
    
    // Publish analytics to MQTT
    publishAnalytics();
}

void performMLPredictions() {
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        ml_analytics.predictPhaseChange(i);
    }
}

void publishAnalytics() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["device_id"] = "pcm_analytics_gateway";
    
    JsonArray containers = doc.createNestedArray("analytics");
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        JsonObject container = containers.createNestedObject();
        container["id"] = i;
        container["effectiveness"] = analytics[i].effectiveness;
        container["efficiency"] = analytics[i].efficiency;
        container["response_time"] = analytics[i].response_time;
        container["stability_index"] = analytics[i].stability_index;
        container["energy_density"] = analytics[i].energy_density;
        container["thermal_conductivity"] = analytics[i].thermal_conductivity;
        container["heat_transfer_coefficient"] = analytics[i].heat_transfer_coefficient;
        container["performance_score"] = analytics[i].performance_score;
    }
    
    String payload;
    serializeJson(doc, payload);
    mqtt_client.publish("pcm/analytics", payload.c_str());
}

void sendPredictions(int container, float phase_change_prob, float optimal_power, 
                    float predicted_efficiency, float time_to_phase_change, 
                    float optimal_temperature, float maintenance_score) {
    
    StaticJsonDocument<256> doc;
    doc["container"] = container;
    doc["phase_change_probability"] = phase_change_prob;
    doc["optimal_power"] = optimal_power;
    doc["predicted_efficiency"] = predicted_efficiency;
    doc["time_to_phase_change"] = time_to_phase_change;
    doc["optimal_temperature"] = optimal_temperature;
    doc["maintenance_score"] = maintenance_score;
    
    String payload;
    serializeJson(doc, payload);
    
    // Send to Arduino
    Serial2.println(payload);
    
    // Publish to MQTT
    mqtt_client.publish("pcm/predictions", payload.c_str());
}

void logMLPredictions(int container, float* predictions) {
    File log_file = SPIFFS.open("/ml_predictions.log", "a");
    if (log_file) {
        log_file.print(millis());
        log_file.print(",");
        log_file.print(container);
        for (int i = 0; i < ML_OUTPUT_SIZE; i++) {
            log_file.print(",");
            log_file.print(predictions[i]);
        }
        log_file.println();
        log_file.close();
    }
}

void broadcastDataToClients() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["type"] = "pcm_data";
    
    JsonArray containers = doc.createNestedArray("data");
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        JsonObject container = containers.createNestedObject();
        container["id"] = i;
        container["temperature_top"] = pcm_data[i].temperature_top;
        container["temperature_bottom"] = pcm_data[i].temperature_bottom;
        container["mass"] = pcm_data[i].mass;
        container["heat_flux"] = pcm_data[i].heat_flux;
        container["power_input"] = pcm_data[i].power_input;
        container["phase_fraction"] = pcm_data[i].phase_fraction;
        container["phase_state"] = pcm_data[i].phase_state;
        container["performance_score"] = analytics[i].performance_score;
    }
    
    String payload;
    serializeJson(doc, payload);
    websocket_server.broadcastTXT(payload);
}

void setupWebServer() {
    // Serve static files
    web_server.serveStatic("/", SPIFFS, "/");
    
    // API endpoints
    web_server.on("/api/status", HTTP_GET, handleStatus);
    web_server.on("/api/analytics", HTTP_GET, handleAnalytics);
    web_server.on("/api/predictions", HTTP_GET, handlePredictions);
    web_server.on("/api/history", HTTP_GET, handleHistory);
    web_server.on("/api/export", HTTP_GET, handleExport);
    
    web_server.begin();
    Serial.println("✅ Web server started on port 80");
}

void handleStatus() {
    StaticJsonDocument<512> doc;
    doc["status"] = "running";
    doc["uptime"] = millis();
    doc["free_heap"] = ESP.getFreeHeap();
    doc["wifi_connected"] = WiFi.status() == WL_CONNECTED;
    doc["mqtt_connected"] = mqtt_client.connected();
    doc["containers"] = NUM_CONTAINERS;
    
    String response;
    serializeJson(doc, response);
    web_server.send(200, "application/json", response);
}

void handleAnalytics() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    
    JsonArray containers = doc.createNestedArray("analytics");
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        JsonObject container = containers.createNestedObject();
        container["id"] = i;
        container["effectiveness"] = analytics[i].effectiveness;
        container["efficiency"] = analytics[i].efficiency;
        container["energy_density"] = analytics[i].energy_density;
        container["performance_score"] = analytics[i].performance_score;
    }
    
    String response;
    serializeJson(doc, response);
    web_server.send(200, "application/json", response);
}

void handlePredictions() {
    // Return latest ML predictions
    StaticJsonDocument<512> doc;
    doc["timestamp"] = millis();
    doc["predictions"] = "Latest ML predictions would be here";
    
    String response;
    serializeJson(doc, response);
    web_server.send(200, "application/json", response);
}

void handleHistory() {
    int container = web_server.arg("container").toInt();
    int points = web_server.arg("points").toInt();
    
    if (points <= 0) points = 100;
    if (container < 0 || container >= NUM_CONTAINERS) {
        web_server.send(400, "application/json", "{\"error\":\"Invalid container\"}");
        return;
    }
    
    StaticJsonDocument<2048> doc;
    doc["container"] = container;
    doc["points"] = points;
    
    JsonArray data = doc.createNestedArray("history");
    int count = min(points, history_index[container]);
    
    for (int i = 0; i < count; i++) {
        int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
        JsonObject point = data.createNestedObject();
        point["timestamp"] = history[container][idx].timestamp;
        point["temperature"] = history[container][idx].temperature_top;
        point["phase_fraction"] = history[container][idx].phase_fraction;
        point["power"] = history[container][idx].power_input;
    }
    
    String response;
    serializeJson(doc, response);
    web_server.send(200, "application/json", response);
}

void handleExport() {
    // Export data as CSV
    String csv = "timestamp,container,temperature_top,temperature_bottom,mass,heat_flux,power_input,enthalpy,phase_fraction,phase_state,efficiency\n";
    
    for (int container = 0; container < NUM_CONTAINERS; container++) {
        int count = min(100, history_index[container]);
        for (int i = 0; i < count; i++) {
            int idx = (history_index[container] - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            csv += String(history[container][idx].timestamp) + ",";
            csv += String(container) + ",";
            csv += String(history[container][idx].temperature_top) + ",";
            csv += String(history[container][idx].temperature_bottom) + ",";
            csv += String(history[container][idx].mass) + ",";
            csv += String(history[container][idx].heat_flux) + ",";
            csv += String(history[container][idx].power_input) + ",";
            csv += String(history[container][idx].enthalpy) + ",";
            csv += String(history[container][idx].phase_fraction) + ",";
            csv += history[container][idx].phase_state + ",";
            csv += String(history[container][idx].storage_efficiency) + "\n";
        }
    }
    
    web_server.send(200, "text/csv", csv);
}

void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.println("WebSocket client disconnected");
            break;
        case WStype_CONNECTED:
            Serial.println("WebSocket client connected");
            break;
        case WStype_TEXT:
            // Handle commands from web interface
            handleWebSocketCommand(num, (char*)payload);
            break;
        default:
            break;
    }
}

void handleWebSocketCommand(uint8_t num, String command) {
    StaticJsonDocument<256> doc;
    deserializeJson(doc, command);
    
    String action = doc["action"];
    
    if (action == "get_status") {
        // Send current status
        broadcastDataToClients();
    } else if (action == "set_target") {
        int container = doc["container"];
        float temperature = doc["temperature"];
        
        // Forward command to Arduino
        StaticJsonDocument<128> cmd;
        cmd["action"] = "set_target";
        cmd["container"] = container;
        cmd["temperature"] = temperature;
        
        String payload;
        serializeJson(cmd, payload);
        Serial2.println(payload);
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("MQTT received: " + message);
    
    if (String(topic) == "pcm/commands") {
        // Forward commands to Arduino
        Serial2.println(message);
    }
}

This advanced ESP32 analytics gateway provides comprehensive AI-driven analysis, cloud integration, and real-time monitoring capabilities for the PCM thermal energy storage system.