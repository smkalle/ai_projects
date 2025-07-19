/*
 * Program 18: ESP32 Analytics Gateway for Heat Exchanger Performance Monitor
 * Arduino Zero to Hero v2.0 - Track 1: Thermal Systems Engineering
 * 
 * Advanced analytics and machine learning for heat exchanger optimization
 * - Real-time fouling detection and prediction
 * - Energy efficiency optimization algorithms
 * - Predictive maintenance with ML models
 * - Advanced heat transfer analysis
 * - Cloud integration and remote monitoring
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
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <FFT.h>
#include <TensorFlowLite_ESP32.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>

// Network Configuration
const char* ssid = "IndustrialWiFi";
const char* password = "YourIndustrialPassword";
const char* mqtt_server = "industrial.mqtt.com";
const int mqtt_port = 1883;
const char* cloud_endpoint = "https://api.thermalanalytics.com";
const char* api_key = "your_industrial_api_key";

// System Configuration
#define MAX_HISTORY_SIZE 2000
#define ANALYTICS_INTERVAL 30000      // 30 seconds
#define CLOUD_SYNC_INTERVAL 300000    // 5 minutes
#define PREDICTION_INTERVAL 60000     // 1 minute
#define ALARM_CHECK_INTERVAL 10000    // 10 seconds

// Machine Learning Configuration
#define TENSOR_ARENA_SIZE 60000
#define ML_INPUT_SIZE 24
#define ML_OUTPUT_SIZE 6
#define FFT_SIZE 256

// Global objects
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);
AsyncWebServer web_server(80);
WebSocketsServer websocket_server(81);
HTTPClient http_client;

// TensorFlow Lite objects
tflite::MicroErrorReporter tflite_error_reporter;
const tflite::Model* fouling_model = nullptr;
const tflite::Model* maintenance_model = nullptr;
tflite::MicroInterpreter* fouling_interpreter = nullptr;
tflite::MicroInterpreter* maintenance_interpreter = nullptr;
TfLiteTensor* fouling_input = nullptr;
TfLiteTensor* fouling_output = nullptr;
TfLiteTensor* maintenance_input = nullptr;
TfLiteTensor* maintenance_output = nullptr;
tflite::AllOpsResolver tflite_resolver;

// Tensor arena for TensorFlow Lite
uint8_t tensor_arena[TENSOR_ARENA_SIZE];

// Heat Exchanger Data Structure
struct HeatExchangerData {
    unsigned long timestamp;
    float hot_inlet_temp;
    float hot_outlet_temp;
    float cold_inlet_temp;
    float cold_outlet_temp;
    float hot_wall_temps[2];
    float cold_wall_temps[2];
    float hot_flow_rate;
    float cold_flow_rate;
    float hot_pressure_drop;
    float cold_pressure_drop;
    float hot_power;
    float cold_power;
    float effectiveness;
    float ntu;
    float overall_u;
    float fouling_factor;
    float energy_balance_error;
    float vibration_levels[4];
    float conductivity[2];
    float ph_levels[2];
};

// Advanced Analytics Structure
struct AdvancedAnalytics {
    float fouling_prediction;
    float maintenance_score;
    float energy_efficiency;
    float performance_index;
    float reliability_score;
    float optimal_flow_hot;
    float optimal_flow_cold;
    float predicted_cleaning_days;
    float predicted_maintenance_days;
    String fouling_type;
    String maintenance_priority;
    float cost_savings_potential;
};

// Performance Optimization Structure
struct PerformanceOptimization {
    float current_efficiency;
    float maximum_efficiency;
    float efficiency_improvement;
    float energy_savings_kwh;
    float cost_savings_usd;
    float optimal_hot_temp;
    float optimal_cold_temp;
    float optimal_flow_ratio;
    bool optimization_active;
    String optimization_strategy;
};

// System State
HeatExchangerData current_data;
HeatExchangerData history[MAX_HISTORY_SIZE];
int history_index = 0;
AdvancedAnalytics analytics;
PerformanceOptimization optimization;
bool system_ready = false;
unsigned long last_analytics_time = 0;
unsigned long last_cloud_sync = 0;
unsigned long last_prediction_time = 0;
unsigned long last_alarm_check = 0;

// Machine Learning and Analytics Classes

class FoulingAnalyticsML {
private:
    float feature_buffer[ML_INPUT_SIZE];
    float fouling_trend_buffer[50];
    int trend_index = 0;
    bool model_loaded = false;
    
public:
    bool loadFoulingModel() {
        // Load fouling prediction model from SPIFFS
        File model_file = SPIFFS.open("/fouling_model.tflite", "r");
        if (!model_file) {
            Serial.println("Failed to open fouling model file");
            return false;
        }
        
        size_t model_size = model_file.size();
        uint8_t* model_data = (uint8_t*)malloc(model_size);
        model_file.readBytes((char*)model_data, model_size);
        model_file.close();
        
        // Initialize TensorFlow Lite model
        fouling_model = tflite::GetModel(model_data);
        if (fouling_model->version() != TFLITE_SCHEMA_VERSION) {
            Serial.println("Fouling model schema version mismatch");
            free(model_data);
            return false;
        }
        
        // Create interpreter
        static tflite::MicroInterpreter static_interpreter(
            fouling_model, tflite_resolver, tensor_arena, TENSOR_ARENA_SIZE/2, &tflite_error_reporter);
        fouling_interpreter = &static_interpreter;
        
        if (fouling_interpreter->AllocateTensors() != kTfLiteOk) {
            Serial.println("Failed to allocate fouling tensors");
            free(model_data);
            return false;
        }
        
        // Get input and output tensors
        fouling_input = fouling_interpreter->input(0);
        fouling_output = fouling_interpreter->output(0);
        
        model_loaded = true;
        Serial.println("✅ Fouling ML model loaded successfully");
        return true;
    }
    
    void predictFouling() {
        if (!model_loaded) return;
        
        // Prepare input features
        prepareFoulingFeatures();
        
        // Copy features to input tensor
        for (int i = 0; i < ML_INPUT_SIZE; i++) {
            fouling_input->data.f[i] = feature_buffer[i];
        }
        
        // Run inference
        if (fouling_interpreter->Invoke() != kTfLiteOk) {
            Serial.println("Failed to invoke fouling ML model");
            return;
        }
        
        // Process output
        processFoulingOutput();
    }
    
    void prepareFoulingFeatures() {
        int idx = 0;
        
        // Current measurements
        feature_buffer[idx++] = current_data.hot_inlet_temp;
        feature_buffer[idx++] = current_data.hot_outlet_temp;
        feature_buffer[idx++] = current_data.cold_inlet_temp;
        feature_buffer[idx++] = current_data.cold_outlet_temp;
        feature_buffer[idx++] = current_data.hot_flow_rate;
        feature_buffer[idx++] = current_data.cold_flow_rate;
        feature_buffer[idx++] = current_data.hot_pressure_drop;
        feature_buffer[idx++] = current_data.cold_pressure_drop;
        feature_buffer[idx++] = current_data.effectiveness;
        feature_buffer[idx++] = current_data.overall_u;
        feature_buffer[idx++] = current_data.fouling_factor;
        
        // Water quality indicators
        feature_buffer[idx++] = current_data.conductivity[0];
        feature_buffer[idx++] = current_data.conductivity[1];
        feature_buffer[idx++] = current_data.ph_levels[0];
        feature_buffer[idx++] = current_data.ph_levels[1];
        
        // Derived features
        feature_buffer[idx++] = calculateReynoldsNumber(0); // Hot side
        feature_buffer[idx++] = calculateReynoldsNumber(1); // Cold side
        feature_buffer[idx++] = calculatePrandtlNumber(0); // Hot side
        feature_buffer[idx++] = calculatePrandtlNumber(1); // Cold side
        feature_buffer[idx++] = calculateHeatTransferRate();
        feature_buffer[idx++] = calculateTemperatureEffectiveness();
        feature_buffer[idx++] = calculateFoulingRate();
        feature_buffer[idx++] = calculateOperatingTime();
        
        // Statistical features
        feature_buffer[idx++] = calculateEffectivenessVariance();
    }
    
    void processFoulingOutput() {
        // Process ML model output
        float* output = fouling_output->data.f;
        
        // Outputs: [fouling_probability, fouling_rate, cleaning_days, 
        //          fouling_type_index, severity_score, location_confidence]
        
        analytics.fouling_prediction = output[0];
        float fouling_rate = output[1];
        analytics.predicted_cleaning_days = output[2];
        int fouling_type_idx = (int)output[3];
        float severity_score = output[4];
        float location_confidence = output[5];
        
        // Map fouling type
        String fouling_types[] = {"SCALING", "CORROSION", "BIOLOGICAL", "PARTICULATE", "CHEMICAL"};
        if (fouling_type_idx >= 0 && fouling_type_idx < 5) {
            analytics.fouling_type = fouling_types[fouling_type_idx];
        }
        
        // Update fouling trend
        fouling_trend_buffer[trend_index] = analytics.fouling_prediction;
        trend_index = (trend_index + 1) % 50;
        
        // Generate insights
        generateFoulingInsights(severity_score, location_confidence);
        
        // Log predictions
        logMLPredictions("fouling", output);
    }
    
    float calculateReynoldsNumber(int side) {
        float flow_rate = (side == 0) ? current_data.hot_flow_rate : current_data.cold_flow_rate;
        float temp = (side == 0) ? 
            (current_data.hot_inlet_temp + current_data.hot_outlet_temp) / 2.0 :
            (current_data.cold_inlet_temp + current_data.cold_outlet_temp) / 2.0;
        
        // Simplified Reynolds number calculation
        float density = calculateWaterDensity(temp);
        float viscosity = calculateWaterViscosity(temp);
        float velocity = flow_rate / (3.14159 * 0.0095 * 0.0095); // Pipe area
        float diameter = 0.019; // Tube diameter
        
        return (density * velocity * diameter) / viscosity;
    }
    
    float calculatePrandtlNumber(int side) {
        float temp = (side == 0) ? 
            (current_data.hot_inlet_temp + current_data.hot_outlet_temp) / 2.0 :
            (current_data.cold_inlet_temp + current_data.cold_outlet_temp) / 2.0;
        
        float viscosity = calculateWaterViscosity(temp);
        float specific_heat = 4186.0; // J/kg·K
        float thermal_conductivity = 0.6; // W/m·K
        
        return (viscosity * specific_heat) / thermal_conductivity;
    }
    
    float calculateHeatTransferRate() {
        float cp = 4186.0; // J/kg·K
        float hot_rate = current_data.hot_flow_rate * 1000 * cp * 
                        (current_data.hot_inlet_temp - current_data.hot_outlet_temp);
        float cold_rate = current_data.cold_flow_rate * 1000 * cp * 
                         (current_data.cold_outlet_temp - current_data.cold_inlet_temp);
        
        return (hot_rate + cold_rate) / 2.0; // W
    }
    
    float calculateTemperatureEffectiveness() {
        float hot_delta = current_data.hot_inlet_temp - current_data.hot_outlet_temp;
        float cold_delta = current_data.cold_outlet_temp - current_data.cold_inlet_temp;
        float max_delta = current_data.hot_inlet_temp - current_data.cold_inlet_temp;
        
        if (max_delta > 0) {
            return (hot_delta + cold_delta) / (2.0 * max_delta);
        }
        return 0.0;
    }
    
    float calculateFoulingRate() {
        if (history_index < 10) return 0.0;
        
        float recent_fouling = 0.0;
        float older_fouling = 0.0;
        
        for (int i = 0; i < 5; i++) {
            int recent_idx = (history_index - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            int older_idx = (history_index - 6 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            recent_fouling += history[recent_idx].fouling_factor;
            older_fouling += history[older_idx].fouling_factor;
        }
        
        return (recent_fouling - older_fouling) / 5.0; // Change in fouling factor
    }
    
    float calculateOperatingTime() {
        return (millis() - system_ready) / 3600000.0; // Hours
    }
    
    float calculateEffectivenessVariance() {
        if (history_index < 20) return 0.0;
        
        float sum = 0.0;
        float sum_sq = 0.0;
        int count = min(50, history_index);
        
        for (int i = 0; i < count; i++) {
            int idx = (history_index - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            float value = history[idx].effectiveness;
            sum += value;
            sum_sq += value * value;
        }
        
        float mean = sum / count;
        float variance = (sum_sq / count) - (mean * mean);
        
        return variance;
    }
    
    float calculateWaterDensity(float temp) {
        return 1000.0 - 0.0178 * abs(temp - 4.0); // kg/m³
    }
    
    float calculateWaterViscosity(float temp) {
        return 0.001 * exp(1.3272 * (293.15 - temp) / (temp + 168.15)); // Pa·s
    }
    
    void generateFoulingInsights(float severity, float confidence) {
        Serial.println("🔍 Fouling Analysis Results:");
        Serial.println("   Fouling Probability: " + String(analytics.fouling_prediction * 100, 1) + "%");
        Serial.println("   Fouling Type: " + analytics.fouling_type);
        Serial.println("   Severity Score: " + String(severity, 2));
        Serial.println("   Location Confidence: " + String(confidence * 100, 1) + "%");
        Serial.println("   Predicted Cleaning: " + String(analytics.predicted_cleaning_days, 0) + " days");
        
        // Generate recommendations
        if (analytics.fouling_prediction > 0.8) {
            Serial.println("   🚨 Recommendation: Immediate cleaning required");
        } else if (analytics.fouling_prediction > 0.6) {
            Serial.println("   ⚠️ Recommendation: Schedule cleaning within 2 weeks");
        } else if (analytics.fouling_prediction > 0.4) {
            Serial.println("   📋 Recommendation: Monitor closely, plan cleaning");
        }
    }
};

class MaintenanceAnalyticsML {
private:
    float maintenance_features[ML_INPUT_SIZE];
    bool maintenance_model_loaded = false;
    
public:
    bool loadMaintenanceModel() {
        // Load maintenance prediction model from SPIFFS
        File model_file = SPIFFS.open("/maintenance_model.tflite", "r");
        if (!model_file) {
            Serial.println("Failed to open maintenance model file");
            return false;
        }
        
        size_t model_size = model_file.size();
        uint8_t* model_data = (uint8_t*)malloc(model_size);
        model_file.readBytes((char*)model_data, model_size);
        model_file.close();
        
        // Initialize TensorFlow Lite model
        maintenance_model = tflite::GetModel(model_data);
        if (maintenance_model->version() != TFLITE_SCHEMA_VERSION) {
            Serial.println("Maintenance model schema version mismatch");
            free(model_data);
            return false;
        }
        
        // Create interpreter
        static tflite::MicroInterpreter static_interpreter(
            maintenance_model, tflite_resolver, tensor_arena + TENSOR_ARENA_SIZE/2, 
            TENSOR_ARENA_SIZE/2, &tflite_error_reporter);
        maintenance_interpreter = &static_interpreter;
        
        if (maintenance_interpreter->AllocateTensors() != kTfLiteOk) {
            Serial.println("Failed to allocate maintenance tensors");
            free(model_data);
            return false;
        }
        
        // Get input and output tensors
        maintenance_input = maintenance_interpreter->input(0);
        maintenance_output = maintenance_interpreter->output(0);
        
        maintenance_model_loaded = true;
        Serial.println("✅ Maintenance ML model loaded successfully");
        return true;
    }
    
    void predictMaintenance() {
        if (!maintenance_model_loaded) return;
        
        // Prepare input features
        prepareMaintenanceFeatures();
        
        // Copy features to input tensor
        for (int i = 0; i < ML_INPUT_SIZE; i++) {
            maintenance_input->data.f[i] = maintenance_features[i];
        }
        
        // Run inference
        if (maintenance_interpreter->Invoke() != kTfLiteOk) {
            Serial.println("Failed to invoke maintenance ML model");
            return;
        }
        
        // Process output
        processMaintenanceOutput();
    }
    
    void prepareMaintenanceFeatures() {
        int idx = 0;
        
        // Performance metrics
        maintenance_features[idx++] = current_data.effectiveness;
        maintenance_features[idx++] = current_data.overall_u;
        maintenance_features[idx++] = current_data.fouling_factor;
        maintenance_features[idx++] = current_data.energy_balance_error;
        
        // Vibration analysis
        for (int i = 0; i < 4; i++) {
            maintenance_features[idx++] = current_data.vibration_levels[i];
        }
        
        // Power consumption
        maintenance_features[idx++] = current_data.hot_power;
        maintenance_features[idx++] = current_data.cold_power;
        maintenance_features[idx++] = current_data.hot_power + current_data.cold_power;
        
        // Flow characteristics
        maintenance_features[idx++] = current_data.hot_flow_rate;
        maintenance_features[idx++] = current_data.cold_flow_rate;
        maintenance_features[idx++] = current_data.hot_pressure_drop;
        maintenance_features[idx++] = current_data.cold_pressure_drop;
        
        // Temperature analysis
        maintenance_features[idx++] = current_data.hot_inlet_temp - current_data.hot_outlet_temp;
        maintenance_features[idx++] = current_data.cold_outlet_temp - current_data.cold_inlet_temp;
        
        // Derived maintenance indicators
        maintenance_features[idx++] = calculateVibrationTrend();
        maintenance_features[idx++] = calculatePowerTrend();
        maintenance_features[idx++] = calculateEfficiencyTrend();
        maintenance_features[idx++] = calculateOperatingStress();
        maintenance_features[idx++] = calculateWearIndicator();
        maintenance_features[idx++] = calculateOperatingHours();
    }
    
    void processMaintenanceOutput() {
        // Process ML model output
        float* output = maintenance_output->data.f;
        
        // Outputs: [maintenance_score, days_to_maintenance, pump_health, 
        //          heat_exchanger_health, priority_level, cost_factor]
        
        analytics.maintenance_score = output[0];
        analytics.predicted_maintenance_days = output[1];
        float pump_health = output[2];
        float hx_health = output[3];
        int priority_level = (int)output[4];
        float cost_factor = output[5];
        
        // Map priority level
        String priorities[] = {"LOW", "MEDIUM", "HIGH", "CRITICAL", "EMERGENCY"};
        if (priority_level >= 0 && priority_level < 5) {
            analytics.maintenance_priority = priorities[priority_level];
        }
        
        // Calculate reliability score
        analytics.reliability_score = (pump_health + hx_health) / 2.0 * 100.0;
        
        // Generate maintenance insights
        generateMaintenanceInsights(pump_health, hx_health, cost_factor);
        
        // Log predictions
        logMLPredictions("maintenance", output);
    }
    
    float calculateVibrationTrend() {
        if (history_index < 10) return 0.0;
        
        float recent_vibration = 0.0;
        float older_vibration = 0.0;
        
        for (int i = 0; i < 5; i++) {
            int recent_idx = (history_index - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            int older_idx = (history_index - 6 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            
            for (int j = 0; j < 4; j++) {
                recent_vibration += history[recent_idx].vibration_levels[j];
                older_vibration += history[older_idx].vibration_levels[j];
            }
        }
        
        return (recent_vibration - older_vibration) / 20.0; // Change in average vibration
    }
    
    float calculatePowerTrend() {
        if (history_index < 10) return 0.0;
        
        float recent_power = 0.0;
        float older_power = 0.0;
        
        for (int i = 0; i < 5; i++) {
            int recent_idx = (history_index - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            int older_idx = (history_index - 6 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            
            recent_power += history[recent_idx].hot_power + history[recent_idx].cold_power;
            older_power += history[older_idx].hot_power + history[older_idx].cold_power;
        }
        
        return (recent_power - older_power) / 5.0; // Change in total power
    }
    
    float calculateEfficiencyTrend() {
        if (history_index < 10) return 0.0;
        
        float recent_efficiency = 0.0;
        float older_efficiency = 0.0;
        
        for (int i = 0; i < 5; i++) {
            int recent_idx = (history_index - 1 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            int older_idx = (history_index - 6 - i + MAX_HISTORY_SIZE) % MAX_HISTORY_SIZE;
            
            recent_efficiency += history[recent_idx].effectiveness;
            older_efficiency += history[older_idx].effectiveness;
        }
        
        return (recent_efficiency - older_efficiency) / 5.0; // Change in effectiveness
    }
    
    float calculateOperatingStress() {
        // Calculate operating stress based on conditions
        float temperature_stress = (current_data.hot_inlet_temp - 60.0) / 40.0; // Normalized
        float pressure_stress = (current_data.hot_pressure_drop - 20.0) / 30.0; // Normalized
        float flow_stress = (current_data.hot_flow_rate - 50.0) / 30.0; // Normalized
        
        return (temperature_stress + pressure_stress + flow_stress) / 3.0;
    }
    
    float calculateWearIndicator() {
        // Simple wear indicator based on multiple factors
        float vibration_wear = (current_data.vibration_levels[0] + current_data.vibration_levels[1]) / 2.0 / 10.0;
        float pressure_wear = (current_data.hot_pressure_drop + current_data.cold_pressure_drop) / 2.0 / 50.0;
        float efficiency_wear = (0.9 - current_data.effectiveness) / 0.2;
        
        return (vibration_wear + pressure_wear + efficiency_wear) / 3.0;
    }
    
    float calculateOperatingHours() {
        return (millis() - system_ready) / 3600000.0; // Hours
    }
    
    void generateMaintenanceInsights(float pump_health, float hx_health, float cost_factor) {
        Serial.println("🔧 Maintenance Analysis Results:");
        Serial.println("   Maintenance Score: " + String(analytics.maintenance_score * 100, 1) + "%");
        Serial.println("   Pump Health: " + String(pump_health * 100, 1) + "%");
        Serial.println("   Heat Exchanger Health: " + String(hx_health * 100, 1) + "%");
        Serial.println("   Priority: " + analytics.maintenance_priority);
        Serial.println("   Predicted Maintenance: " + String(analytics.predicted_maintenance_days, 0) + " days");
        Serial.println("   Cost Factor: " + String(cost_factor, 2));
        
        // Generate specific recommendations
        if (pump_health < 0.7) {
            Serial.println("   🔧 Recommendation: Inspect pump bearings and impeller");
        }
        if (hx_health < 0.7) {
            Serial.println("   🧽 Recommendation: Schedule heat exchanger cleaning");
        }
        if (analytics.maintenance_score > 0.8) {
            Serial.println("   🚨 Recommendation: Immediate maintenance required");
        }
    }
};

class PerformanceOptimizer {
private:
    float optimization_history[10][100];
    int optimization_index = 0;
    
public:
    void optimizePerformance() {
        // Calculate current performance
        optimization.current_efficiency = calculateCurrentEfficiency();
        optimization.maximum_efficiency = calculateMaximumEfficiency();
        optimization.efficiency_improvement = optimization.maximum_efficiency - optimization.current_efficiency;
        
        // Calculate optimal operating conditions
        findOptimalConditions();
        
        // Calculate energy and cost savings
        calculateSavings();
        
        // Generate optimization strategy
        generateOptimizationStrategy();
        
        // Store optimization history
        storeOptimizationHistory();
    }
    
    float calculateCurrentEfficiency() {
        float thermal_efficiency = current_data.effectiveness * 100.0;
        float pumping_efficiency = calculatePumpingEfficiency();
        float overall_efficiency = (thermal_efficiency + pumping_efficiency) / 2.0;
        
        return overall_efficiency;
    }
    
    float calculateMaximumEfficiency() {
        // Theoretical maximum efficiency based on current conditions
        float max_thermal = 95.0; // 95% thermal efficiency
        float max_pumping = 85.0; // 85% pumping efficiency
        float max_overall = (max_thermal + max_pumping) / 2.0;
        
        return max_overall;
    }
    
    float calculatePumpingEfficiency() {
        float total_power = current_data.hot_power + current_data.cold_power;
        float hydraulic_power = calculateHydraulicPower();
        
        if (total_power > 0) {
            return (hydraulic_power / total_power) * 100.0;
        }
        return 0.0;
    }
    
    float calculateHydraulicPower() {
        // Simplified hydraulic power calculation
        float hot_hydraulic = current_data.hot_flow_rate * current_data.hot_pressure_drop * 1000.0;
        float cold_hydraulic = current_data.cold_flow_rate * current_data.cold_pressure_drop * 1000.0;
        
        return hot_hydraulic + cold_hydraulic; // Watts
    }
    
    void findOptimalConditions() {
        // Use gradient descent to find optimal flow rates
        optimization.optimal_flow_hot = optimizeFlowRate(0);
        optimization.optimal_flow_cold = optimizeFlowRate(1);
        
        // Calculate optimal temperatures
        optimization.optimal_hot_temp = current_data.hot_inlet_temp; // Maintain current
        optimization.optimal_cold_temp = current_data.cold_inlet_temp; // Maintain current
        
        // Calculate optimal flow ratio
        optimization.optimal_flow_ratio = optimization.optimal_flow_hot / optimization.optimal_flow_cold;
    }
    
    float optimizeFlowRate(int side) {
        float current_flow = (side == 0) ? current_data.hot_flow_rate : current_data.cold_flow_rate;
        float optimal_flow = current_flow;
        float max_efficiency = 0.0;
        
        // Test different flow rates
        for (float flow = current_flow * 0.8; flow <= current_flow * 1.2; flow += current_flow * 0.05) {
            float efficiency = evaluateEfficiencyAtFlow(side, flow);
            if (efficiency > max_efficiency) {
                max_efficiency = efficiency;
                optimal_flow = flow;
            }
        }
        
        return optimal_flow;
    }
    
    float evaluateEfficiencyAtFlow(int side, float flow) {
        // Simplified efficiency evaluation
        float reynolds = calculateReynolds(side, flow);
        float nusselt = calculateNusselt(reynolds);
        float heat_transfer_coeff = calculateHeatTransferCoeff(nusselt);
        
        // Estimate effectiveness with new flow
        float new_effectiveness = estimateEffectiveness(side, flow, heat_transfer_coeff);
        
        // Calculate pumping power
        float pumping_power = estimatePumpingPower(side, flow);
        
        // Overall efficiency
        float thermal_efficiency = new_effectiveness * 100.0;
        float pumping_efficiency = 1000.0 / pumping_power; // Simplified
        
        return (thermal_efficiency + pumping_efficiency) / 2.0;
    }
    
    float calculateReynolds(int side, float flow) {
        float temp = (side == 0) ? 
            (current_data.hot_inlet_temp + current_data.hot_outlet_temp) / 2.0 :
            (current_data.cold_inlet_temp + current_data.cold_outlet_temp) / 2.0;
        
        float density = 1000.0; // kg/m³
        float viscosity = 0.001; // Pa·s
        float diameter = 0.019; // m
        float velocity = flow / (3.14159 * diameter * diameter / 4.0);
        
        return (density * velocity * diameter) / viscosity;
    }
    
    float calculateNusselt(float reynolds) {
        // Simplified Nusselt number correlation
        float prandtl = 7.0; // Approximate for water
        return 0.023 * pow(reynolds, 0.8) * pow(prandtl, 0.4);
    }
    
    float calculateHeatTransferCoeff(float nusselt) {
        float thermal_conductivity = 0.6; // W/m·K
        float diameter = 0.019; // m
        
        return nusselt * thermal_conductivity / diameter;
    }
    
    float estimateEffectiveness(int side, float flow, float h) {
        // Simplified effectiveness estimation
        float ua = h * 2.5; // Heat transfer area
        float c_hot = flow * 4186.0; // Hot side heat capacity rate
        float c_cold = current_data.cold_flow_rate * 4186.0; // Cold side heat capacity rate
        float c_min = min(c_hot, c_cold);
        
        float ntu = ua / c_min;
        float effectiveness = 1.0 - exp(-ntu);
        
        return min(effectiveness, 0.95);
    }
    
    float estimatePumpingPower(int side, float flow) {
        // Simplified pumping power estimation
        float pressure_drop = 10.0 + flow * flow * 0.1; // kPa
        return flow * pressure_drop * 1000.0; // Watts
    }
    
    void calculateSavings() {
        float efficiency_gain = optimization.efficiency_improvement;
        float power_reduction = efficiency_gain * 0.01 * (current_data.hot_power + current_data.cold_power);
        
        optimization.energy_savings_kwh = power_reduction * 24.0 / 1000.0; // kWh per day
        optimization.cost_savings_usd = optimization.energy_savings_kwh * 0.10; // $0.10 per kWh
        
        // Annual savings
        analytics.cost_savings_potential = optimization.cost_savings_usd * 365.0;
    }
    
    void generateOptimizationStrategy() {
        if (optimization.efficiency_improvement > 5.0) {
            optimization.optimization_strategy = "AGGRESSIVE_OPTIMIZATION";
        } else if (optimization.efficiency_improvement > 2.0) {
            optimization.optimization_strategy = "MODERATE_OPTIMIZATION";
        } else {
            optimization.optimization_strategy = "FINE_TUNING";
        }
        
        optimization.optimization_active = optimization.efficiency_improvement > 1.0;
    }
    
    void storeOptimizationHistory() {
        optimization_history[0][optimization_index] = optimization.current_efficiency;
        optimization_history[1][optimization_index] = optimization.maximum_efficiency;
        optimization_history[2][optimization_index] = optimization.optimal_flow_hot;
        optimization_history[3][optimization_index] = optimization.optimal_flow_cold;
        optimization_history[4][optimization_index] = optimization.energy_savings_kwh;
        
        optimization_index = (optimization_index + 1) % 100;
    }
};

class CloudIntegration {
private:
    String device_id;
    String session_id;
    
public:
    CloudIntegration() {
        device_id = "hx_monitor_" + String(ESP.getChipId());
        session_id = String(millis());
    }
    
    void syncData() {
        if (WiFi.status() != WL_CONNECTED) return;
        
        // Prepare comprehensive data payload
        StaticJsonDocument<4096> doc;
        doc["device_id"] = device_id;
        doc["session_id"] = session_id;
        doc["timestamp"] = millis();
        doc["system_type"] = "heat_exchanger_monitor";
        
        // Current measurements
        JsonObject measurements = doc.createNestedObject("measurements");
        measurements["hot_inlet_temp"] = current_data.hot_inlet_temp;
        measurements["hot_outlet_temp"] = current_data.hot_outlet_temp;
        measurements["cold_inlet_temp"] = current_data.cold_inlet_temp;
        measurements["cold_outlet_temp"] = current_data.cold_outlet_temp;
        measurements["hot_flow_rate"] = current_data.hot_flow_rate;
        measurements["cold_flow_rate"] = current_data.cold_flow_rate;
        measurements["hot_pressure_drop"] = current_data.hot_pressure_drop;
        measurements["cold_pressure_drop"] = current_data.cold_pressure_drop;
        measurements["effectiveness"] = current_data.effectiveness;
        measurements["overall_u"] = current_data.overall_u;
        measurements["fouling_factor"] = current_data.fouling_factor;
        
        // Analytics results
        JsonObject analytics_obj = doc.createNestedObject("analytics");
        analytics_obj["fouling_prediction"] = analytics.fouling_prediction;
        analytics_obj["maintenance_score"] = analytics.maintenance_score;
        analytics_obj["performance_index"] = analytics.performance_index;
        analytics_obj["reliability_score"] = analytics.reliability_score;
        analytics_obj["predicted_cleaning_days"] = analytics.predicted_cleaning_days;
        analytics_obj["predicted_maintenance_days"] = analytics.predicted_maintenance_days;
        analytics_obj["fouling_type"] = analytics.fouling_type;
        analytics_obj["maintenance_priority"] = analytics.maintenance_priority;
        
        // Optimization results
        JsonObject optimization_obj = doc.createNestedObject("optimization");
        optimization_obj["current_efficiency"] = optimization.current_efficiency;
        optimization_obj["maximum_efficiency"] = optimization.maximum_efficiency;
        optimization_obj["efficiency_improvement"] = optimization.efficiency_improvement;
        optimization_obj["energy_savings_kwh"] = optimization.energy_savings_kwh;
        optimization_obj["cost_savings_usd"] = optimization.cost_savings_usd;
        optimization_obj["optimization_strategy"] = optimization.optimization_strategy;
        
        // Send to cloud
        String payload;
        serializeJson(doc, payload);
        
        http_client.begin(String(cloud_endpoint) + "/api/hx/analytics");
        http_client.addHeader("Content-Type", "application/json");
        http_client.addHeader("Authorization", "Bearer " + String(api_key));
        
        int response_code = http_client.POST(payload);
        
        if (response_code == 200) {
            Serial.println("✅ Analytics data synced to cloud");
            handleCloudResponse();
        } else {
            Serial.println("❌ Cloud sync failed: " + String(response_code));
        }
        
        http_client.end();
    }
    
    void handleCloudResponse() {
        String response = http_client.getString();
        StaticJsonDocument<1024> doc;
        
        if (deserializeJson(doc, response) == DeserializationError::Ok) {
            // Process cloud recommendations
            if (doc.containsKey("recommendations")) {
                JsonArray recommendations = doc["recommendations"];
                for (JsonObject recommendation : recommendations) {
                    String type = recommendation["type"];
                    String action = recommendation["action"];
                    float value = recommendation["value"];
                    
                    Serial.println("☁️ Cloud Recommendation: " + type + " - " + action + " (" + String(value) + ")");
                    
                    // Send recommendation to Arduino
                    sendRecommendationToArduino(type, action, value);
                }
            }
            
            // Process model updates
            if (doc.containsKey("model_updates")) {
                JsonArray updates = doc["model_updates"];
                for (JsonObject update : updates) {
                    String model_name = update["model"];
                    String version = update["version"];
                    String download_url = update["url"];
                    
                    Serial.println("📥 Model update available: " + model_name + " v" + version);
                    // Could implement automatic model updates here
                }
            }
        }
    }
    
    void sendRecommendationToArduino(String type, String action, float value) {
        StaticJsonDocument<256> doc;
        doc["type"] = "cloud_recommendation";
        doc["recommendation_type"] = type;
        doc["action"] = action;
        doc["value"] = value;
        doc["timestamp"] = millis();
        
        String payload;
        serializeJson(doc, payload);
        
        // Send to Arduino via serial
        Serial2.println(payload);
    }
};

// Global objects
FoulingAnalyticsML fouling_analytics;
MaintenanceAnalyticsML maintenance_analytics;
PerformanceOptimizer performance_optimizer;
CloudIntegration cloud_integration;

void setup() {
    Serial.begin(115200);
    Serial2.begin(115200); // Communication with Arduino
    delay(2000);
    
    Serial.println("🧠 HEAT EXCHANGER ANALYTICS GATEWAY STARTED!");
    Serial.println("🧠 Advanced AI-driven heat exchanger optimization and analytics");
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
    
    // Load ML models
    fouling_analytics.loadFoulingModel();
    maintenance_analytics.loadMaintenanceModel();
    
    // Initialize system state
    system_ready = true;
    
    Serial.println("🎯 Analytics Gateway Ready");
}

void loop() {
    if (!system_ready) return;
    
    // Handle web server
    websocket_server.loop();
    
    // Handle MQTT
    if (mqtt_client.connected()) {
        mqtt_client.loop();
    } else {
        connectToMQTT();
    }
    
    // Process data from Arduino
    processArduinoData();
    
    // Perform analytics
    if (millis() - last_analytics_time > ANALYTICS_INTERVAL) {
        performAnalytics();
        last_analytics_time = millis();
    }
    
    // ML predictions
    if (millis() - last_prediction_time > PREDICTION_INTERVAL) {
        performMLPredictions();
        last_prediction_time = millis();
    }
    
    // Cloud synchronization
    if (millis() - last_cloud_sync > CLOUD_SYNC_INTERVAL) {
        cloud_integration.syncData();
        last_cloud_sync = millis();
    }
    
    // Alarm checks
    if (millis() - last_alarm_check > ALARM_CHECK_INTERVAL) {
        checkAlarms();
        last_alarm_check = millis();
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
        if (mqtt_client.connect("HeatExchangerAnalytics")) {
            Serial.println("✅ MQTT connected");
            mqtt_client.subscribe("hx/data");
            mqtt_client.subscribe("hx/commands");
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
        StaticJsonDocument<2048> doc;
        DeserializationError error = deserializeJson(doc, data);
        
        if (error) {
            Serial.println("JSON parsing failed: " + String(error.c_str()));
            return;
        }
        
        // Update current data
        current_data.timestamp = millis();
        current_data.hot_inlet_temp = doc["hot_inlet_temp"] | 0.0;
        current_data.hot_outlet_temp = doc["hot_outlet_temp"] | 0.0;
        current_data.cold_inlet_temp = doc["cold_inlet_temp"] | 0.0;
        current_data.cold_outlet_temp = doc["cold_outlet_temp"] | 0.0;
        current_data.hot_flow_rate = doc["hot_flow_rate"] | 0.0;
        current_data.cold_flow_rate = doc["cold_flow_rate"] | 0.0;
        current_data.hot_pressure_drop = doc["hot_pressure_drop"] | 0.0;
        current_data.cold_pressure_drop = doc["cold_pressure_drop"] | 0.0;
        current_data.hot_power = doc["hot_power"] | 0.0;
        current_data.cold_power = doc["cold_power"] | 0.0;
        current_data.effectiveness = doc["effectiveness"] | 0.0;
        current_data.overall_u = doc["overall_u"] | 0.0;
        current_data.fouling_factor = doc["fouling_factor"] | 0.0;
        current_data.energy_balance_error = doc["energy_balance_error"] | 0.0;
        
        // Store in history
        history[history_index] = current_data;
        history_index = (history_index + 1) % MAX_HISTORY_SIZE;
        
        // Broadcast to WebSocket clients
        broadcastDataToClients();
    }
}

void performAnalytics() {
    // Calculate performance index
    analytics.performance_index = calculatePerformanceIndex();
    
    // Calculate energy efficiency
    analytics.energy_efficiency = calculateEnergyEfficiency();
    
    // Update analytics
    Serial.println("📊 Analytics Update:");
    Serial.println("   Performance Index: " + String(analytics.performance_index, 1));
    Serial.println("   Energy Efficiency: " + String(analytics.energy_efficiency, 1) + "%");
    Serial.println("   Reliability Score: " + String(analytics.reliability_score, 1) + "%");
}

void performMLPredictions() {
    // Fouling prediction
    fouling_analytics.predictFouling();
    
    // Maintenance prediction
    maintenance_analytics.predictMaintenance();
    
    // Performance optimization
    performance_optimizer.optimizePerformance();
    
    // Publish results
    publishMLResults();
}

void checkAlarms() {
    // Check for critical conditions
    if (analytics.fouling_prediction > 0.9) {
        triggerAlarm("CRITICAL_FOULING", analytics.fouling_prediction);
    }
    
    if (analytics.maintenance_score > 0.8) {
        triggerAlarm("MAINTENANCE_REQUIRED", analytics.maintenance_score);
    }
    
    if (current_data.effectiveness < 0.6) {
        triggerAlarm("LOW_EFFECTIVENESS", current_data.effectiveness);
    }
}

float calculatePerformanceIndex() {
    float effectiveness_score = current_data.effectiveness * 100.0;
    float efficiency_score = analytics.energy_efficiency;
    float reliability_score = analytics.reliability_score;
    
    return (effectiveness_score + efficiency_score + reliability_score) / 3.0;
}

float calculateEnergyEfficiency() {
    float thermal_power = calculateThermalPower();
    float electrical_power = current_data.hot_power + current_data.cold_power;
    
    if (electrical_power > 0) {
        return (thermal_power / electrical_power) * 100.0;
    }
    return 0.0;
}

float calculateThermalPower() {
    float cp = 4186.0; // J/kg·K
    float hot_thermal = current_data.hot_flow_rate * 1000 * cp * 
                       (current_data.hot_inlet_temp - current_data.hot_outlet_temp);
    float cold_thermal = current_data.cold_flow_rate * 1000 * cp * 
                        (current_data.cold_outlet_temp - current_data.cold_inlet_temp);
    
    return (hot_thermal + cold_thermal) / 2.0; // W
}

void publishMLResults() {
    if (mqtt_client.connected()) {
        StaticJsonDocument<1024> doc;
        doc["timestamp"] = millis();
        doc["device_id"] = "hx_analytics_gateway";
        
        JsonObject fouling = doc.createNestedObject("fouling");
        fouling["prediction"] = analytics.fouling_prediction;
        fouling["type"] = analytics.fouling_type;
        fouling["cleaning_days"] = analytics.predicted_cleaning_days;
        
        JsonObject maintenance = doc.createNestedObject("maintenance");
        maintenance["score"] = analytics.maintenance_score;
        maintenance["priority"] = analytics.maintenance_priority;
        maintenance["maintenance_days"] = analytics.predicted_maintenance_days;
        
        JsonObject performance = doc.createNestedObject("performance");
        performance["index"] = analytics.performance_index;
        performance["energy_efficiency"] = analytics.energy_efficiency;
        performance["reliability"] = analytics.reliability_score;
        
        String payload;
        serializeJson(doc, payload);
        mqtt_client.publish("hx/analytics", payload.c_str());
    }
}

void triggerAlarm(String alarm_type, float value) {
    Serial.println("🚨 ALARM: " + alarm_type + " - " + String(value, 3));
    
    if (mqtt_client.connected()) {
        StaticJsonDocument<256> doc;
        doc["alarm_type"] = alarm_type;
        doc["value"] = value;
        doc["timestamp"] = millis();
        doc["severity"] = "HIGH";
        
        String payload;
        serializeJson(doc, payload);
        mqtt_client.publish("hx/alarms", payload.c_str());
    }
}

void broadcastDataToClients() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["type"] = "hx_data";
    
    JsonObject data = doc.createNestedObject("data");
    data["effectiveness"] = current_data.effectiveness;
    data["fouling_factor"] = current_data.fouling_factor;
    data["hot_inlet_temp"] = current_data.hot_inlet_temp;
    data["cold_inlet_temp"] = current_data.cold_inlet_temp;
    data["hot_flow_rate"] = current_data.hot_flow_rate;
    data["cold_flow_rate"] = current_data.cold_flow_rate;
    data["performance_index"] = analytics.performance_index;
    data["fouling_prediction"] = analytics.fouling_prediction;
    data["maintenance_score"] = analytics.maintenance_score;
    
    String payload;
    serializeJson(doc, payload);
    websocket_server.broadcastTXT(payload);
}

void setupWebServer() {
    // Serve static files
    web_server.serveStatic("/", SPIFFS, "/");
    
    // API endpoints
    web_server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request) {
        StaticJsonDocument<512> doc;
        doc["status"] = "running";
        doc["uptime"] = millis();
        doc["free_heap"] = ESP.getFreeHeap();
        doc["wifi_connected"] = WiFi.status() == WL_CONNECTED;
        doc["mqtt_connected"] = mqtt_client.connected();
        
        String response;
        serializeJson(doc, response);
        request->send(200, "application/json", response);
    });
    
    web_server.on("/api/analytics", HTTP_GET, [](AsyncWebServerRequest *request) {
        StaticJsonDocument<1024> doc;
        doc["timestamp"] = millis();
        doc["performance_index"] = analytics.performance_index;
        doc["energy_efficiency"] = analytics.energy_efficiency;
        doc["fouling_prediction"] = analytics.fouling_prediction;
        doc["maintenance_score"] = analytics.maintenance_score;
        doc["reliability_score"] = analytics.reliability_score;
        
        String response;
        serializeJson(doc, response);
        request->send(200, "application/json", response);
    });
    
    web_server.begin();
    Serial.println("✅ Web server started on port 80");
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
    
    if (action == "get_analytics") {
        // Send current analytics
        broadcastDataToClients();
    } else if (action == "trigger_prediction") {
        // Trigger ML prediction
        performMLPredictions();
    } else if (action == "reset_baseline") {
        // Reset baseline (send to Arduino)
        Serial2.println("{\"action\":\"reset_baseline\"}");
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("MQTT received: " + message);
    
    if (String(topic) == "hx/data") {
        // Process data from Arduino via MQTT
        processArduinoData();
    } else if (String(topic) == "hx/commands") {
        // Forward commands to Arduino
        Serial2.println(message);
    }
}

void logMLPredictions(String model_type, float* predictions) {
    File log_file = SPIFFS.open("/ml_predictions.log", "a");
    if (log_file) {
        log_file.print(millis());
        log_file.print(",");
        log_file.print(model_type);
        for (int i = 0; i < 6; i++) {
            log_file.print(",");
            log_file.print(predictions[i]);
        }
        log_file.println();
        log_file.close();
    }
}

This advanced ESP32 analytics gateway provides comprehensive machine learning-based analysis, optimization, and predictive capabilities for professional heat exchanger systems.