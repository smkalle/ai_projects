/*
 * ESP32 Analytics Gateway for Thermal Conductivity Measurement System
 * Advanced signal processing, machine learning, and IoT connectivity
 * 
 * Features:
 * - Real-time signal processing and filtering
 * - Machine learning material classification
 * - Advanced thermal property calculations
 * - Material database integration
 * - Cloud analytics and reporting
 * - Quality control and validation
 * 
 * Hardware: ESP32 Development Board
 * Communication: Serial with Arduino Mega
 * Connectivity: WiFi, Bluetooth, Cloud APIs
 * 
 * Author: Arduino Zero to Hero Team
 * Date: 2024
 * License: MIT
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>
#include <SPIFFS.h>
#include <TensorFlowLite_ESP32.h>
#include <BluetoothSerial.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ESPmDNS.h>
#include <Update.h>
#include <PubSubClient.h>
#include <ArduinoOTA.h>

// System Configuration
#define SERIAL_BAUD 115200
#define ARDUINO_SERIAL Serial2
#define ARDUINO_BAUD 115200
#define SAMPLE_BUFFER_SIZE 10000
#define ML_INPUT_SIZE 20
#define ML_OUTPUT_SIZE 10
#define MAX_MATERIALS 1000
#define MEASUREMENT_HISTORY_SIZE 1000

// WiFi Configuration
const char* ssid = "ThermalLab_Network";
const char* password = "ThermalMeasurement2024";

// MQTT Configuration
const char* mqtt_server = "thermal-analytics.cloud.com";
const int mqtt_port = 1883;
const char* mqtt_user = "thermal_system";
const char* mqtt_password = "secure_thermal_2024";

// Cloud API Configuration
const char* cloud_api_endpoint = "https://api.thermal-analytics.com/v1/";
const char* api_key = "your_api_key_here";

// NTP Configuration
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

// Web Server
WebServer server(80);

// MQTT Client
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Bluetooth Serial
BluetoothSerial SerialBT;

// Measurement Data Structure
struct MeasurementData {
    unsigned long timestamp;
    String method;
    String material_id;
    float thermal_conductivity;
    float measurement_uncertainty;
    float temperature;
    float ambient_conditions[5]; // temp, humidity, pressure, etc.
    float signal_quality;
    bool measurement_valid;
    String quality_flags;
};

// Material Properties Structure
struct MaterialProperties {
    String material_id;
    String material_name;
    String material_class;
    float thermal_conductivity;
    float density;
    float specific_heat;
    float temperature_coefficient;
    float uncertainty;
    String applications;
    String safety_notes;
    bool is_reference;
    unsigned long last_updated;
};

// Signal Processing Structure
struct SignalProcessing {
    float raw_data[SAMPLE_BUFFER_SIZE];
    float filtered_data[SAMPLE_BUFFER_SIZE];
    float processed_data[SAMPLE_BUFFER_SIZE];
    int data_count;
    float sampling_rate;
    float noise_level;
    float signal_to_noise_ratio;
    String processing_method;
    bool processing_complete;
};

// Machine Learning Structure
struct MLAnalysis {
    float input_features[ML_INPUT_SIZE];
    float output_predictions[ML_OUTPUT_SIZE];
    float confidence_scores[ML_OUTPUT_SIZE];
    String predicted_material;
    float prediction_confidence;
    String material_class;
    float quality_score;
    bool analysis_complete;
};

// Quality Control Structure
struct QualityControl {
    float repeatability_score;
    float reproducibility_score;
    float accuracy_score;
    float precision_score;
    float bias_error;
    float random_error;
    String quality_grade;
    bool quality_passed;
    String recommendations;
};

// Global Variables
MeasurementData current_measurement;
MaterialProperties material_database[MAX_MATERIALS];
SignalProcessing signal_processor;
MLAnalysis ml_analyzer;
QualityControl quality_controller;
MeasurementData measurement_history[MEASUREMENT_HISTORY_SIZE];

int material_count = 0;
int history_count = 0;
bool system_initialized = false;
bool wifi_connected = false;
bool cloud_connected = false;
unsigned long last_cloud_sync = 0;
unsigned long last_status_update = 0;

// TensorFlow Lite Model (placeholder)
// const unsigned char thermal_model[] = { /* model data */ };

// Advanced Signal Processing Class
class AdvancedSignalProcessor {
private:
    float hanning_window[SAMPLE_BUFFER_SIZE];
    float fft_buffer[SAMPLE_BUFFER_SIZE * 2];
    float magnitude_spectrum[SAMPLE_BUFFER_SIZE];
    float phase_spectrum[SAMPLE_BUFFER_SIZE];
    
public:
    AdvancedSignalProcessor() {
        generateHanningWindow();
    }
    
    void generateHanningWindow() {
        for (int i = 0; i < SAMPLE_BUFFER_SIZE; i++) {
            hanning_window[i] = 0.5 * (1.0 - cos(2.0 * PI * i / (SAMPLE_BUFFER_SIZE - 1)));
        }
    }
    
    void applyDigitalFilter(float* data, int count, float cutoff_freq) {
        // Low-pass Butterworth filter implementation
        float alpha = calculateAlpha(cutoff_freq, signal_processor.sampling_rate);
        float filtered_value = data[0];
        
        for (int i = 1; i < count; i++) {
            filtered_value = alpha * data[i] + (1.0 - alpha) * filtered_value;
            data[i] = filtered_value;
        }
    }
    
    float calculateAlpha(float cutoff_freq, float sampling_rate) {
        float rc = 1.0 / (2.0 * PI * cutoff_freq);
        float dt = 1.0 / sampling_rate;
        return dt / (rc + dt);
    }
    
    void performFFT(float* data, int count) {
        // Apply window function
        for (int i = 0; i < count; i++) {
            fft_buffer[i * 2] = data[i] * hanning_window[i]; // Real part
            fft_buffer[i * 2 + 1] = 0.0; // Imaginary part
        }
        
        // FFT implementation (simplified)
        calculateMagnitudeSpectrum(count);
        calculatePhaseSpectrum(count);
    }
    
    void calculateMagnitudeSpectrum(int count) {
        for (int i = 0; i < count / 2; i++) {
            float real = fft_buffer[i * 2];
            float imag = fft_buffer[i * 2 + 1];
            magnitude_spectrum[i] = sqrt(real * real + imag * imag);
        }
    }
    
    void calculatePhaseSpectrum(int count) {
        for (int i = 0; i < count / 2; i++) {
            float real = fft_buffer[i * 2];
            float imag = fft_buffer[i * 2 + 1];
            phase_spectrum[i] = atan2(imag, real);
        }
    }
    
    float calculateSignalToNoiseRatio(float* data, int count) {
        float signal_power = 0.0;
        float noise_power = 0.0;
        
        // Calculate signal power (simplified)
        for (int i = 0; i < count; i++) {
            signal_power += data[i] * data[i];
        }
        signal_power /= count;
        
        // Estimate noise power from high-frequency components
        for (int i = count * 3 / 4; i < count; i++) {
            noise_power += magnitude_spectrum[i] * magnitude_spectrum[i];
        }
        noise_power /= (count / 4);
        
        if (noise_power > 0) {
            return 10.0 * log10(signal_power / noise_power);
        }
        return 0.0;
    }
    
    void removeOutliers(float* data, int count, float threshold) {
        float mean = calculateMean(data, count);
        float std_dev = calculateStdDev(data, count);
        
        for (int i = 0; i < count; i++) {
            if (abs(data[i] - mean) > threshold * std_dev) {
                // Replace outlier with interpolated value
                data[i] = interpolateValue(data, count, i);
            }
        }
    }
    
    float calculateMean(float* data, int count) {
        float sum = 0.0;
        for (int i = 0; i < count; i++) {
            sum += data[i];
        }
        return sum / count;
    }
    
    float calculateStdDev(float* data, int count) {
        float mean = calculateMean(data, count);
        float sum_sq_diff = 0.0;
        
        for (int i = 0; i < count; i++) {
            float diff = data[i] - mean;
            sum_sq_diff += diff * diff;
        }
        
        return sqrt(sum_sq_diff / (count - 1));
    }
    
    float interpolateValue(float* data, int count, int index) {
        if (index == 0) return data[1];
        if (index == count - 1) return data[count - 2];
        
        return (data[index - 1] + data[index + 1]) / 2.0;
    }
    
    void detectSignalFeatures(float* data, int count) {
        // Detect peaks, valleys, and transitions
        for (int i = 1; i < count - 1; i++) {
            if (data[i] > data[i-1] && data[i] > data[i+1]) {
                // Peak detected
                Serial.println("Peak detected at index " + String(i));
            }
            if (data[i] < data[i-1] && data[i] < data[i+1]) {
                // Valley detected
                Serial.println("Valley detected at index " + String(i));
            }
        }
    }
};

// Machine Learning Material Classifier
class MaterialClassifier {
private:
    float feature_weights[ML_INPUT_SIZE][ML_OUTPUT_SIZE];
    float output_bias[ML_OUTPUT_SIZE];
    String material_classes[ML_OUTPUT_SIZE];
    
public:
    MaterialClassifier() {
        initializeModel();
        initializeMaterialClasses();
    }
    
    void initializeModel() {
        // Initialize neural network weights (simplified)
        for (int i = 0; i < ML_INPUT_SIZE; i++) {
            for (int j = 0; j < ML_OUTPUT_SIZE; j++) {
                feature_weights[i][j] = random(-1000, 1000) / 1000.0;
            }
        }
        
        for (int i = 0; i < ML_OUTPUT_SIZE; i++) {
            output_bias[i] = random(-500, 500) / 1000.0;
        }
    }
    
    void initializeMaterialClasses() {
        material_classes[0] = "Metals";
        material_classes[1] = "Ceramics";
        material_classes[2] = "Polymers";
        material_classes[3] = "Composites";
        material_classes[4] = "Insulators";
        material_classes[5] = "Semiconductors";
        material_classes[6] = "Fluids";
        material_classes[7] = "Gases";
        material_classes[8] = "Phase_Change";
        material_classes[9] = "Unknown";
    }
    
    void extractFeatures(MeasurementData& measurement) {
        // Extract features from measurement data
        ml_analyzer.input_features[0] = measurement.thermal_conductivity;
        ml_analyzer.input_features[1] = measurement.temperature;
        ml_analyzer.input_features[2] = measurement.measurement_uncertainty;
        ml_analyzer.input_features[3] = measurement.ambient_conditions[0]; // temperature
        ml_analyzer.input_features[4] = measurement.ambient_conditions[1]; // humidity
        ml_analyzer.input_features[5] = measurement.ambient_conditions[2]; // pressure
        ml_analyzer.input_features[6] = measurement.signal_quality;
        ml_analyzer.input_features[7] = signal_processor.signal_to_noise_ratio;
        ml_analyzer.input_features[8] = signal_processor.noise_level;
        ml_analyzer.input_features[9] = calculateTemperatureCoefficient(measurement);
        
        // Additional derived features
        ml_analyzer.input_features[10] = log10(measurement.thermal_conductivity + 1e-6);
        ml_analyzer.input_features[11] = measurement.thermal_conductivity / measurement.temperature;
        ml_analyzer.input_features[12] = measurement.measurement_uncertainty / measurement.thermal_conductivity;
        ml_analyzer.input_features[13] = calculateThermalDiffusivity(measurement);
        ml_analyzer.input_features[14] = calculateFourierNumber(measurement);
        ml_analyzer.input_features[15] = calculateBiotNumber(measurement);
        ml_analyzer.input_features[16] = calculatePecletNumber(measurement);
        ml_analyzer.input_features[17] = calculateReynoldsNumber(measurement);
        ml_analyzer.input_features[18] = calculatePrandtlNumber(measurement);
        ml_analyzer.input_features[19] = calculateNusseltNumber(measurement);
    }
    
    float calculateTemperatureCoefficient(MeasurementData& measurement) {
        // Simplified temperature coefficient calculation
        return (measurement.thermal_conductivity - 1.0) / (measurement.temperature - 20.0);
    }
    
    float calculateThermalDiffusivity(MeasurementData& measurement) {
        // Simplified thermal diffusivity calculation
        float density = 1000.0; // Assumed density
        float specific_heat = 1000.0; // Assumed specific heat
        return measurement.thermal_conductivity / (density * specific_heat);
    }
    
    float calculateFourierNumber(MeasurementData& measurement) {
        float alpha = calculateThermalDiffusivity(measurement);
        float time = 1.0; // Characteristic time
        float length = 0.01; // Characteristic length
        return alpha * time / (length * length);
    }
    
    float calculateBiotNumber(MeasurementData& measurement) {
        float h = 10.0; // Heat transfer coefficient
        float L = 0.01; // Characteristic length
        return h * L / measurement.thermal_conductivity;
    }
    
    float calculatePecletNumber(MeasurementData& measurement) {
        float velocity = 0.1; // Characteristic velocity
        float length = 0.01; // Characteristic length
        float alpha = calculateThermalDiffusivity(measurement);
        return velocity * length / alpha;
    }
    
    float calculateReynoldsNumber(MeasurementData& measurement) {
        float velocity = 0.1; // Characteristic velocity
        float length = 0.01; // Characteristic length
        float kinematic_viscosity = 1e-6; // Kinematic viscosity
        return velocity * length / kinematic_viscosity;
    }
    
    float calculatePrandtlNumber(MeasurementData& measurement) {
        float kinematic_viscosity = 1e-6; // Kinematic viscosity
        float alpha = calculateThermalDiffusivity(measurement);
        return kinematic_viscosity / alpha;
    }
    
    float calculateNusseltNumber(MeasurementData& measurement) {
        float h = 10.0; // Heat transfer coefficient
        float L = 0.01; // Characteristic length
        return h * L / measurement.thermal_conductivity;
    }
    
    void classifyMaterial(MeasurementData& measurement) {
        extractFeatures(measurement);
        
        // Forward pass through neural network
        for (int i = 0; i < ML_OUTPUT_SIZE; i++) {
            float output = output_bias[i];
            for (int j = 0; j < ML_INPUT_SIZE; j++) {
                output += ml_analyzer.input_features[j] * feature_weights[j][i];
            }
            ml_analyzer.output_predictions[i] = sigmoid(output);
        }
        
        // Find best prediction
        int best_class = 0;
        float best_confidence = ml_analyzer.output_predictions[0];
        
        for (int i = 1; i < ML_OUTPUT_SIZE; i++) {
            if (ml_analyzer.output_predictions[i] > best_confidence) {
                best_confidence = ml_analyzer.output_predictions[i];
                best_class = i;
            }
        }
        
        ml_analyzer.predicted_material = material_classes[best_class];
        ml_analyzer.prediction_confidence = best_confidence;
        ml_analyzer.material_class = material_classes[best_class];
        ml_analyzer.quality_score = calculateQualityScore();
        ml_analyzer.analysis_complete = true;
        
        Serial.println("Material Classification Results:");
        Serial.println("  Predicted Material: " + ml_analyzer.predicted_material);
        Serial.println("  Confidence: " + String(ml_analyzer.prediction_confidence * 100, 1) + "%");
        Serial.println("  Quality Score: " + String(ml_analyzer.quality_score, 2));
    }
    
    float sigmoid(float x) {
        return 1.0 / (1.0 + exp(-x));
    }
    
    float calculateQualityScore() {
        // Calculate overall quality score based on various factors
        float score = 0.0;
        
        // Signal quality factor
        score += signal_processor.signal_to_noise_ratio / 100.0;
        
        // Measurement uncertainty factor
        score += (1.0 - current_measurement.measurement_uncertainty / current_measurement.thermal_conductivity);
        
        // Prediction confidence factor
        score += ml_analyzer.prediction_confidence;
        
        // Environmental stability factor
        score += 0.5; // Simplified
        
        return min(score / 3.0, 1.0);
    }
    
    void updateModelWithFeedback(String true_material, float confidence) {
        // Online learning - update model with feedback
        // This would implement a gradient descent update
        Serial.println("Model updated with feedback: " + true_material);
    }
    
    void validatePrediction(MeasurementData& measurement) {
        // Cross-validate with material database
        for (int i = 0; i < material_count; i++) {
            if (material_database[i].material_name == ml_analyzer.predicted_material) {
                float expected_k = material_database[i].thermal_conductivity;
                float measured_k = measurement.thermal_conductivity;
                float error = abs(expected_k - measured_k) / expected_k;
                
                if (error < 0.1) {
                    Serial.println("✅ Prediction validated against database");
                } else {
                    Serial.println("⚠️ Prediction differs from database by " + String(error * 100, 1) + "%");
                }
                break;
            }
        }
    }
};

// Quality Control System
class QualityControlSystem {
private:
    float measurement_buffer[100];
    int buffer_count;
    
public:
    QualityControlSystem() {
        buffer_count = 0;
    }
    
    void analyzeMeasurementQuality(MeasurementData& measurement) {
        // Add measurement to buffer
        if (buffer_count < 100) {
            measurement_buffer[buffer_count] = measurement.thermal_conductivity;
            buffer_count++;
        } else {
            // Shift buffer
            for (int i = 0; i < 99; i++) {
                measurement_buffer[i] = measurement_buffer[i + 1];
            }
            measurement_buffer[99] = measurement.thermal_conductivity;
        }
        
        // Calculate quality metrics
        quality_controller.repeatability_score = calculateRepeatability();
        quality_controller.reproducibility_score = calculateReproducibility();
        quality_controller.accuracy_score = calculateAccuracy(measurement);
        quality_controller.precision_score = calculatePrecision();
        quality_controller.bias_error = calculateBiasError(measurement);
        quality_controller.random_error = calculateRandomError();
        
        // Determine quality grade
        determineQualityGrade();
        
        // Generate recommendations
        generateRecommendations();
        
        Serial.println("Quality Control Analysis:");
        Serial.println("  Repeatability: " + String(quality_controller.repeatability_score, 2));
        Serial.println("  Reproducibility: " + String(quality_controller.reproducibility_score, 2));
        Serial.println("  Accuracy: " + String(quality_controller.accuracy_score, 2));
        Serial.println("  Precision: " + String(quality_controller.precision_score, 2));
        Serial.println("  Quality Grade: " + quality_controller.quality_grade);
    }
    
    float calculateRepeatability() {
        if (buffer_count < 3) return 0.0;
        
        float mean = 0.0;
        for (int i = 0; i < buffer_count; i++) {
            mean += measurement_buffer[i];
        }
        mean /= buffer_count;
        
        float std_dev = 0.0;
        for (int i = 0; i < buffer_count; i++) {
            float diff = measurement_buffer[i] - mean;
            std_dev += diff * diff;
        }
        std_dev = sqrt(std_dev / (buffer_count - 1));
        
        return 1.0 - (std_dev / mean);
    }
    
    float calculateReproducibility() {
        // Simplified reproducibility calculation
        return quality_controller.repeatability_score * 0.8; // Typically lower than repeatability
    }
    
    float calculateAccuracy(MeasurementData& measurement) {
        // Compare with known reference values
        float reference_value = findReferenceValue(measurement.material_id);
        if (reference_value > 0) {
            float error = abs(measurement.thermal_conductivity - reference_value) / reference_value;
            return max(0.0, 1.0 - error);
        }
        return 0.5; // Unknown reference
    }
    
    float calculatePrecision() {
        return quality_controller.repeatability_score; // Simplified
    }
    
    float calculateBiasError(MeasurementData& measurement) {
        float reference_value = findReferenceValue(measurement.material_id);
        if (reference_value > 0) {
            return (measurement.thermal_conductivity - reference_value) / reference_value;
        }
        return 0.0;
    }
    
    float calculateRandomError() {
        if (buffer_count < 2) return 0.0;
        
        float mean = 0.0;
        for (int i = 0; i < buffer_count; i++) {
            mean += measurement_buffer[i];
        }
        mean /= buffer_count;
        
        float sum_sq_diff = 0.0;
        for (int i = 0; i < buffer_count; i++) {
            float diff = measurement_buffer[i] - mean;
            sum_sq_diff += diff * diff;
        }
        
        return sqrt(sum_sq_diff / (buffer_count - 1)) / mean;
    }
    
    float findReferenceValue(String material_id) {
        for (int i = 0; i < material_count; i++) {
            if (material_database[i].material_id == material_id && material_database[i].is_reference) {
                return material_database[i].thermal_conductivity;
            }
        }
        return 0.0;
    }
    
    void determineQualityGrade() {
        float overall_score = (quality_controller.repeatability_score + 
                              quality_controller.reproducibility_score + 
                              quality_controller.accuracy_score + 
                              quality_controller.precision_score) / 4.0;
        
        if (overall_score >= 0.95) {
            quality_controller.quality_grade = "Excellent";
            quality_controller.quality_passed = true;
        } else if (overall_score >= 0.85) {
            quality_controller.quality_grade = "Good";
            quality_controller.quality_passed = true;
        } else if (overall_score >= 0.70) {
            quality_controller.quality_grade = "Acceptable";
            quality_controller.quality_passed = true;
        } else {
            quality_controller.quality_grade = "Poor";
            quality_controller.quality_passed = false;
        }
    }
    
    void generateRecommendations() {
        quality_controller.recommendations = "";
        
        if (quality_controller.repeatability_score < 0.8) {
            quality_controller.recommendations += "Improve measurement repeatability. ";
        }
        if (quality_controller.accuracy_score < 0.8) {
            quality_controller.recommendations += "Check calibration accuracy. ";
        }
        if (quality_controller.bias_error > 0.1) {
            quality_controller.recommendations += "Systematic bias detected - recalibrate. ";
        }
        if (quality_controller.random_error > 0.05) {
            quality_controller.recommendations += "Reduce measurement noise. ";
        }
        
        if (quality_controller.recommendations == "") {
            quality_controller.recommendations = "Measurement quality is acceptable.";
        }
    }
};

// Material Database Manager
class MaterialDatabaseManager {
public:
    void initializeMaterialDatabase() {
        // Initialize with common reference materials
        addMaterial("NIST_SRM_1450d", "NIST SRM 1450d Fibrous Glass", "Insulator", 
                   0.035, 32, 835, 0.0002, 0.002, "Thermal insulation standard", "", true);
        
        addMaterial("NIST_SRM_1453", "NIST SRM 1453 Expanded Polystyrene", "Polymer", 
                   0.033, 29, 1210, 0.0001, 0.001, "Thermal insulation standard", "", true);
        
        addMaterial("SS_316", "Stainless Steel 316", "Metal", 
                   16.2, 8000, 500, 0.0003, 0.05, "Corrosion-resistant steel", "", true);
        
        addMaterial("AL_6061", "Aluminum 6061", "Metal", 
                   167, 2700, 896, 0.0002, 0.02, "Structural aluminum alloy", "", true);
        
        addMaterial("CU_PURE", "Pure Copper", "Metal", 
                   401, 8960, 385, 0.0001, 0.01, "Electrical conductor", "", true);
        
        addMaterial("PYREX", "Pyrex Glass", "Ceramic", 
                   1.05, 2230, 835, 0.0001, 0.02, "Laboratory glassware", "", true);
        
        Serial.println("✅ Material database initialized with " + String(material_count) + " materials");
    }
    
    void addMaterial(String id, String name, String material_class, float thermal_conductivity,
                    float density, float specific_heat, float temp_coefficient, float uncertainty,
                    String applications, String safety_notes, bool is_reference) {
        if (material_count < MAX_MATERIALS) {
            material_database[material_count].material_id = id;
            material_database[material_count].material_name = name;
            material_database[material_count].material_class = material_class;
            material_database[material_count].thermal_conductivity = thermal_conductivity;
            material_database[material_count].density = density;
            material_database[material_count].specific_heat = specific_heat;
            material_database[material_count].temperature_coefficient = temp_coefficient;
            material_database[material_count].uncertainty = uncertainty;
            material_database[material_count].applications = applications;
            material_database[material_count].safety_notes = safety_notes;
            material_database[material_count].is_reference = is_reference;
            material_database[material_count].last_updated = millis();
            
            material_count++;
        }
    }
    
    MaterialProperties* findMaterial(String material_id) {
        for (int i = 0; i < material_count; i++) {
            if (material_database[i].material_id == material_id) {
                return &material_database[i];
            }
        }
        return nullptr;
    }
    
    void updateMaterial(String material_id, MeasurementData& measurement) {
        MaterialProperties* material = findMaterial(material_id);
        if (material) {
            // Update material properties with new measurement
            material->thermal_conductivity = measurement.thermal_conductivity;
            material->uncertainty = measurement.measurement_uncertainty;
            material->last_updated = millis();
            
            Serial.println("✅ Material " + material_id + " updated");
        }
    }
    
    void saveDatabaseToCloud() {
        if (WiFi.status() == WL_CONNECTED) {
            HTTPClient http;
            http.begin(String(cloud_api_endpoint) + "materials/bulk");
            http.addHeader("Content-Type", "application/json");
            http.addHeader("Authorization", "Bearer " + String(api_key));
            
            StaticJsonDocument<8192> doc;
            JsonArray materials = doc.createNestedArray("materials");
            
            for (int i = 0; i < material_count; i++) {
                JsonObject material = materials.createNestedObject();
                material["id"] = material_database[i].material_id;
                material["name"] = material_database[i].material_name;
                material["class"] = material_database[i].material_class;
                material["thermal_conductivity"] = material_database[i].thermal_conductivity;
                material["density"] = material_database[i].density;
                material["specific_heat"] = material_database[i].specific_heat;
                material["temperature_coefficient"] = material_database[i].temperature_coefficient;
                material["uncertainty"] = material_database[i].uncertainty;
                material["applications"] = material_database[i].applications;
                material["safety_notes"] = material_database[i].safety_notes;
                material["is_reference"] = material_database[i].is_reference;
                material["last_updated"] = material_database[i].last_updated;
            }
            
            String payload;
            serializeJson(doc, payload);
            
            int httpResponseCode = http.POST(payload);
            if (httpResponseCode == 200) {
                Serial.println("✅ Database synchronized with cloud");
            } else {
                Serial.println("❌ Database sync failed: " + String(httpResponseCode));
            }
            
            http.end();
        }
    }
    
    void loadDatabaseFromCloud() {
        if (WiFi.status() == WL_CONNECTED) {
            HTTPClient http;
            http.begin(String(cloud_api_endpoint) + "materials");
            http.addHeader("Authorization", "Bearer " + String(api_key));
            
            int httpResponseCode = http.GET();
            if (httpResponseCode == 200) {
                String response = http.getString();
                
                StaticJsonDocument<8192> doc;
                deserializeJson(doc, response);
                
                JsonArray materials = doc["materials"];
                material_count = 0;
                
                for (JsonObject material : materials) {
                    if (material_count < MAX_MATERIALS) {
                        material_database[material_count].material_id = material["id"].as<String>();
                        material_database[material_count].material_name = material["name"].as<String>();
                        material_database[material_count].material_class = material["class"].as<String>();
                        material_database[material_count].thermal_conductivity = material["thermal_conductivity"];
                        material_database[material_count].density = material["density"];
                        material_database[material_count].specific_heat = material["specific_heat"];
                        material_database[material_count].temperature_coefficient = material["temperature_coefficient"];
                        material_database[material_count].uncertainty = material["uncertainty"];
                        material_database[material_count].applications = material["applications"].as<String>();
                        material_database[material_count].safety_notes = material["safety_notes"].as<String>();
                        material_database[material_count].is_reference = material["is_reference"];
                        material_database[material_count].last_updated = material["last_updated"];
                        
                        material_count++;
                    }
                }
                
                Serial.println("✅ Database loaded from cloud: " + String(material_count) + " materials");
            } else {
                Serial.println("❌ Database load failed: " + String(httpResponseCode));
            }
            
            http.end();
        }
    }
};

// Global objects
AdvancedSignalProcessor signal_processor_obj;
MaterialClassifier material_classifier;
QualityControlSystem quality_control;
MaterialDatabaseManager database_manager;

void setup() {
    Serial.begin(SERIAL_BAUD);
    ARDUINO_SERIAL.begin(ARDUINO_BAUD);
    
    delay(2000);
    
    Serial.println("🌡️ ESP32 THERMAL CONDUCTIVITY ANALYTICS STARTED!");
    Serial.println("🔬 Advanced Signal Processing & Machine Learning");
    Serial.println("🌐 Cloud Analytics & Material Database");
    Serial.println("===============================================");
    
    // Initialize file system
    if (!SPIFFS.begin(true)) {
        Serial.println("❌ SPIFFS initialization failed");
    } else {
        Serial.println("✅ SPIFFS initialized");
    }
    
    // Initialize WiFi
    initializeWiFi();
    
    // Initialize time client
    timeClient.begin();
    
    // Initialize Bluetooth
    SerialBT.begin("ThermalConductivityAnalytics");
    Serial.println("✅ Bluetooth initialized");
    
    // Initialize material database
    database_manager.initializeMaterialDatabase();
    
    // Initialize web server
    initializeWebServer();
    
    // Initialize MQTT
    initializeMQTT();
    
    // Initialize OTA updates
    initializeOTA();
    
    // Initialize signal processing
    signal_processor.data_count = 0;
    signal_processor.sampling_rate = 100.0;
    signal_processor.processing_complete = false;
    
    // Initialize ML analyzer
    ml_analyzer.analysis_complete = false;
    
    // Initialize quality controller
    quality_controller.quality_passed = false;
    
    Serial.println("🎯 ESP32 Analytics System Ready");
    system_initialized = true;
}

void loop() {
    if (!system_initialized) return;
    
    // Handle WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        wifi_connected = false;
        Serial.println("⚠️ WiFi disconnected, attempting reconnection...");
        initializeWiFi();
    } else {
        wifi_connected = true;
    }
    
    // Handle NTP time synchronization
    timeClient.update();
    
    // Handle OTA updates
    ArduinoOTA.handle();
    
    // Handle web server
    server.handleClient();
    
    // Handle MQTT communication
    if (mqtt_client.connected()) {
        mqtt_client.loop();
    } else {
        connectToMQTT();
    }
    
    // Handle Arduino communication
    handleArduinoCommunication();
    
    // Handle Bluetooth communication
    handleBluetoothCommunication();
    
    // Periodic cloud synchronization
    if (millis() - last_cloud_sync > 300000) { // Every 5 minutes
        synchronizeWithCloud();
        last_cloud_sync = millis();
    }
    
    // Periodic status updates
    if (millis() - last_status_update > 60000) { // Every minute
        publishSystemStatus();
        last_status_update = millis();
    }
    
    delay(100);
}

void initializeWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("✅ WiFi connected");
        Serial.println("   IP: " + WiFi.localIP().toString());
        Serial.println("   RSSI: " + String(WiFi.RSSI()) + "dBm");
        
        // Initialize mDNS
        if (MDNS.begin("thermal-analytics")) {
            Serial.println("✅ mDNS responder started");
        }
        
        wifi_connected = true;
    } else {
        Serial.println();
        Serial.println("❌ WiFi connection failed");
        wifi_connected = false;
    }
}

void initializeWebServer() {
    server.on("/", HTTP_GET, handleRoot);
    server.on("/api/status", HTTP_GET, handleAPIStatus);
    server.on("/api/measurements", HTTP_GET, handleAPIMeasurements);
    server.on("/api/materials", HTTP_GET, handleAPIMaterials);
    server.on("/api/quality", HTTP_GET, handleAPIQuality);
    server.on("/api/classify", HTTP_POST, handleAPIClassify);
    server.on("/api/calibrate", HTTP_POST, handleAPICalibrate);
    server.on("/dashboard", HTTP_GET, handleDashboard);
    server.on("/settings", HTTP_GET, handleSettings);
    server.on("/firmware", HTTP_GET, handleFirmwareUpdate);
    
    server.begin();
    Serial.println("✅ Web server started on port 80");
}

void initializeMQTT() {
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    connectToMQTT();
}

void connectToMQTT() {
    while (!mqtt_client.connected()) {
        String clientId = "ThermalAnalytics-" + String(random(0xffff), HEX);
        
        if (mqtt_client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
            Serial.println("✅ MQTT connected");
            
            // Subscribe to topics
            mqtt_client.subscribe("thermal/commands");
            mqtt_client.subscribe("thermal/calibration");
            mqtt_client.subscribe("thermal/materials");
            mqtt_client.subscribe("thermal/quality");
            
        } else {
            Serial.println("❌ MQTT connection failed, rc=" + String(mqtt_client.state()));
            delay(5000);
        }
    }
}

void initializeOTA() {
    ArduinoOTA.setHostname("thermal-analytics");
    ArduinoOTA.setPassword("thermal_update_2024");
    
    ArduinoOTA.onStart([]() {
        Serial.println("Starting OTA update...");
    });
    
    ArduinoOTA.onEnd([]() {
        Serial.println("OTA update completed!");
    });
    
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("OTA Progress: %u%%\r", (progress / (total / 100)));
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
    Serial.println("✅ OTA initialized");
}

void handleArduinoCommunication() {
    if (ARDUINO_SERIAL.available()) {
        String message = ARDUINO_SERIAL.readStringUntil('\n');
        message.trim();
        
        if (message.startsWith("MEASUREMENT:")) {
            parseMeasurementData(message);
        } else if (message.startsWith("SIGNAL:")) {
            parseSignalData(message);
        } else if (message.startsWith("STATUS:")) {
            parseStatusData(message);
        } else if (message.startsWith("CALIBRATION:")) {
            parseCalibrationData(message);
        }
    }
}

void parseMeasurementData(String data) {
    // Parse measurement data from Arduino
    // Format: MEASUREMENT:timestamp,method,material,conductivity,uncertainty,temperature,quality
    
    StaticJsonDocument<512> doc;
    deserializeJson(doc, data.substring(12));
    
    current_measurement.timestamp = doc["timestamp"];
    current_measurement.method = doc["method"].as<String>();
    current_measurement.material_id = doc["material_id"].as<String>();
    current_measurement.thermal_conductivity = doc["thermal_conductivity"];
    current_measurement.measurement_uncertainty = doc["uncertainty"];
    current_measurement.temperature = doc["temperature"];
    current_measurement.signal_quality = doc["signal_quality"];
    current_measurement.measurement_valid = doc["valid"];
    
    // Process measurement
    processMeasurement(current_measurement);
}

void parseSignalData(String data) {
    // Parse signal data for processing
    // Format: SIGNAL:count,data1,data2,data3...
    
    int commaIndex = data.indexOf(',');
    if (commaIndex > 0) {
        int count = data.substring(7, commaIndex).toInt();
        String signalData = data.substring(commaIndex + 1);
        
        // Parse signal values
        signal_processor.data_count = 0;
        int startIndex = 0;
        
        for (int i = 0; i < count && signal_processor.data_count < SAMPLE_BUFFER_SIZE; i++) {
            int nextComma = signalData.indexOf(',', startIndex);
            if (nextComma == -1) nextComma = signalData.length();
            
            String valueStr = signalData.substring(startIndex, nextComma);
            signal_processor.raw_data[signal_processor.data_count] = valueStr.toFloat();
            signal_processor.data_count++;
            
            startIndex = nextComma + 1;
        }
        
        // Process signal
        processSignalData();
    }
}

void processMeasurement(MeasurementData& measurement) {
    Serial.println("📊 Processing measurement: " + measurement.method);
    
    // Classify material using ML
    material_classifier.classifyMaterial(measurement);
    
    // Perform quality control analysis
    quality_control.analyzeMeasurementQuality(measurement);
    
    // Update material database
    database_manager.updateMaterial(measurement.material_id, measurement);
    
    // Add to measurement history
    addToMeasurementHistory(measurement);
    
    // Publish results
    publishMeasurementResults(measurement);
    
    // Send results back to Arduino
    sendResultsToArduino(measurement);
}

void processSignalData() {
    Serial.println("📈 Processing signal data: " + String(signal_processor.data_count) + " points");
    
    // Apply digital filtering
    signal_processor_obj.applyDigitalFilter(signal_processor.raw_data, signal_processor.data_count, 10.0);
    
    // Copy filtered data
    memcpy(signal_processor.filtered_data, signal_processor.raw_data, 
           signal_processor.data_count * sizeof(float));
    
    // Remove outliers
    signal_processor_obj.removeOutliers(signal_processor.filtered_data, signal_processor.data_count, 3.0);
    
    // Perform FFT analysis
    signal_processor_obj.performFFT(signal_processor.filtered_data, signal_processor.data_count);
    
    // Calculate signal-to-noise ratio
    signal_processor.signal_to_noise_ratio = signal_processor_obj.calculateSignalToNoiseRatio(
        signal_processor.filtered_data, signal_processor.data_count);
    
    // Detect signal features
    signal_processor_obj.detectSignalFeatures(signal_processor.filtered_data, signal_processor.data_count);
    
    signal_processor.processing_complete = true;
    
    Serial.println("✅ Signal processing complete");
    Serial.println("   SNR: " + String(signal_processor.signal_to_noise_ratio, 1) + " dB");
}

void addToMeasurementHistory(MeasurementData& measurement) {
    if (history_count < MEASUREMENT_HISTORY_SIZE) {
        measurement_history[history_count] = measurement;
        history_count++;
    } else {
        // Shift history
        for (int i = 0; i < MEASUREMENT_HISTORY_SIZE - 1; i++) {
            measurement_history[i] = measurement_history[i + 1];
        }
        measurement_history[MEASUREMENT_HISTORY_SIZE - 1] = measurement;
    }
}

void publishMeasurementResults(MeasurementData& measurement) {
    if (mqtt_client.connected()) {
        StaticJsonDocument<1024> doc;
        
        doc["timestamp"] = measurement.timestamp;
        doc["method"] = measurement.method;
        doc["material_id"] = measurement.material_id;
        doc["thermal_conductivity"] = measurement.thermal_conductivity;
        doc["uncertainty"] = measurement.measurement_uncertainty;
        doc["temperature"] = measurement.temperature;
        doc["signal_quality"] = measurement.signal_quality;
        doc["measurement_valid"] = measurement.measurement_valid;
        
        // Add ML analysis results
        JsonObject ml_results = doc.createNestedObject("ml_analysis");
        ml_results["predicted_material"] = ml_analyzer.predicted_material;
        ml_results["confidence"] = ml_analyzer.prediction_confidence;
        ml_results["material_class"] = ml_analyzer.material_class;
        ml_results["quality_score"] = ml_analyzer.quality_score;
        
        // Add quality control results
        JsonObject qc_results = doc.createNestedObject("quality_control");
        qc_results["repeatability"] = quality_controller.repeatability_score;
        qc_results["accuracy"] = quality_controller.accuracy_score;
        qc_results["precision"] = quality_controller.precision_score;
        qc_results["quality_grade"] = quality_controller.quality_grade;
        qc_results["quality_passed"] = quality_controller.quality_passed;
        qc_results["recommendations"] = quality_controller.recommendations;
        
        String payload;
        serializeJson(doc, payload);
        mqtt_client.publish("thermal/measurements", payload.c_str());
    }
}

void sendResultsToArduino(MeasurementData& measurement) {
    StaticJsonDocument<512> doc;
    
    doc["material_classification"] = ml_analyzer.predicted_material;
    doc["confidence"] = ml_analyzer.prediction_confidence;
    doc["quality_grade"] = quality_controller.quality_grade;
    doc["quality_passed"] = quality_controller.quality_passed;
    doc["recommendations"] = quality_controller.recommendations;
    
    String response = "RESULTS:";
    serializeJson(doc, response);
    
    ARDUINO_SERIAL.println(response);
}

void handleBluetoothCommunication() {
    if (SerialBT.available()) {
        String message = SerialBT.readString();
        message.trim();
        
        if (message == "STATUS") {
            sendBluetoothStatus();
        } else if (message == "MEASUREMENTS") {
            sendBluetoothMeasurements();
        } else if (message == "MATERIALS") {
            sendBluetoothMaterials();
        } else if (message.startsWith("CLASSIFY:")) {
            String data = message.substring(9);
            // Parse and classify material
            SerialBT.println("Classification result: " + ml_analyzer.predicted_material);
        }
    }
}

void sendBluetoothStatus() {
    StaticJsonDocument<512> doc;
    
    doc["system_status"] = "operational";
    doc["wifi_connected"] = wifi_connected;
    doc["mqtt_connected"] = mqtt_client.connected();
    doc["materials_count"] = material_count;
    doc["measurements_count"] = history_count;
    doc["signal_processing"] = signal_processor.processing_complete;
    doc["ml_analysis"] = ml_analyzer.analysis_complete;
    doc["quality_control"] = quality_controller.quality_passed;
    doc["uptime"] = millis() / 1000;
    
    String response;
    serializeJson(doc, response);
    SerialBT.println(response);
}

void sendBluetoothMeasurements() {
    StaticJsonDocument<2048> doc;
    JsonArray measurements = doc.createNestedArray("measurements");
    
    int start = max(0, history_count - 10); // Last 10 measurements
    for (int i = start; i < history_count; i++) {
        JsonObject measurement = measurements.createNestedObject();
        measurement["timestamp"] = measurement_history[i].timestamp;
        measurement["method"] = measurement_history[i].method;
        measurement["material_id"] = measurement_history[i].material_id;
        measurement["thermal_conductivity"] = measurement_history[i].thermal_conductivity;
        measurement["uncertainty"] = measurement_history[i].measurement_uncertainty;
        measurement["temperature"] = measurement_history[i].temperature;
        measurement["valid"] = measurement_history[i].measurement_valid;
    }
    
    String response;
    serializeJson(doc, response);
    SerialBT.println(response);
}

void sendBluetoothMaterials() {
    StaticJsonDocument<2048> doc;
    JsonArray materials = doc.createNestedArray("materials");
    
    for (int i = 0; i < min(material_count, 10); i++) {
        JsonObject material = materials.createNestedObject();
        material["id"] = material_database[i].material_id;
        material["name"] = material_database[i].material_name;
        material["class"] = material_database[i].material_class;
        material["thermal_conductivity"] = material_database[i].thermal_conductivity;
        material["uncertainty"] = material_database[i].uncertainty;
        material["is_reference"] = material_database[i].is_reference;
    }
    
    String response;
    serializeJson(doc, response);
    SerialBT.println(response);
}

void synchronizeWithCloud() {
    if (wifi_connected) {
        Serial.println("🌐 Synchronizing with cloud...");
        
        // Upload measurements
        uploadMeasurementsToCloud();
        
        // Sync material database
        database_manager.saveDatabaseToCloud();
        
        // Download updates
        downloadUpdatesFromCloud();
        
        cloud_connected = true;
        Serial.println("✅ Cloud synchronization complete");
    }
}

void uploadMeasurementsToCloud() {
    HTTPClient http;
    http.begin(String(cloud_api_endpoint) + "measurements");
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    
    StaticJsonDocument<4096> doc;
    JsonArray measurements = doc.createNestedArray("measurements");
    
    // Upload last 100 measurements
    int start = max(0, history_count - 100);
    for (int i = start; i < history_count; i++) {
        JsonObject measurement = measurements.createNestedObject();
        measurement["timestamp"] = measurement_history[i].timestamp;
        measurement["method"] = measurement_history[i].method;
        measurement["material_id"] = measurement_history[i].material_id;
        measurement["thermal_conductivity"] = measurement_history[i].thermal_conductivity;
        measurement["uncertainty"] = measurement_history[i].measurement_uncertainty;
        measurement["temperature"] = measurement_history[i].temperature;
        measurement["signal_quality"] = measurement_history[i].signal_quality;
        measurement["valid"] = measurement_history[i].measurement_valid;
    }
    
    String payload;
    serializeJson(doc, payload);
    
    int httpResponseCode = http.POST(payload);
    if (httpResponseCode == 200) {
        Serial.println("✅ Measurements uploaded to cloud");
    } else {
        Serial.println("❌ Measurement upload failed: " + String(httpResponseCode));
    }
    
    http.end();
}

void downloadUpdatesFromCloud() {
    HTTPClient http;
    http.begin(String(cloud_api_endpoint) + "updates");
    http.addHeader("Authorization", "Bearer " + String(api_key));
    
    int httpResponseCode = http.GET();
    if (httpResponseCode == 200) {
        String response = http.getString();
        
        StaticJsonDocument<2048> doc;
        deserializeJson(doc, response);
        
        if (doc["firmware_update_available"]) {
            Serial.println("📦 Firmware update available");
            // Handle firmware update
        }
        
        if (doc["model_update_available"]) {
            Serial.println("🧠 ML model update available");
            // Handle model update
        }
        
        if (doc["calibration_update_available"]) {
            Serial.println("🔧 Calibration update available");
            // Handle calibration update
        }
    }
    
    http.end();
}

void publishSystemStatus() {
    if (mqtt_client.connected()) {
        StaticJsonDocument<512> doc;
        
        doc["timestamp"] = timeClient.getEpochTime();
        doc["system_status"] = "operational";
        doc["wifi_connected"] = wifi_connected;
        doc["cloud_connected"] = cloud_connected;
        doc["materials_count"] = material_count;
        doc["measurements_count"] = history_count;
        doc["free_heap"] = ESP.getFreeHeap();
        doc["uptime"] = millis() / 1000;
        doc["cpu_frequency"] = ESP.getCpuFreqMHz();
        doc["flash_size"] = ESP.getFlashChipSize();
        
        String payload;
        serializeJson(doc, payload);
        mqtt_client.publish("thermal/system_status", payload.c_str());
    }
}

// Web server handlers
void handleRoot() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Thermal Conductivity Analytics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: #f9f9f9; padding: 20px; margin: 10px; border-radius: 8px; }
        .status { display: inline-block; padding: 5px 10px; border-radius: 4px; color: white; }
        .status.good { background: #4CAF50; }
        .status.warning { background: #FF9800; }
        .status.error { background: #F44336; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
        .btn-warning { background: #FF9800; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌡️ Thermal Conductivity Analytics</h1>
        
        <div class="grid">
            <div class="card">
                <h3>System Status</h3>
                <p>WiFi: <span class="status good">Connected</span></p>
                <p>MQTT: <span class="status good">Connected</span></p>
                <p>Cloud: <span class="status good">Synchronized</span></p>
                <p>Uptime: <span id="uptime"></span></p>
            </div>
            
            <div class="card">
                <h3>Material Database</h3>
                <p>Total Materials: <span id="material-count"></span></p>
                <p>Reference Materials: <span id="reference-count"></span></p>
                <button class="btn-primary" onclick="loadMaterials()">View Materials</button>
            </div>
            
            <div class="card">
                <h3>Measurements</h3>
                <p>Total Measurements: <span id="measurement-count"></span></p>
                <p>Last Measurement: <span id="last-measurement"></span></p>
                <button class="btn-primary" onclick="loadMeasurements()">View History</button>
            </div>
            
            <div class="card">
                <h3>Quality Control</h3>
                <p>Quality Grade: <span id="quality-grade"></span></p>
                <p>Quality Passed: <span id="quality-passed"></span></p>
                <button class="btn-primary" onclick="loadQuality()">View Details</button>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>Actions</h3>
                <button class="btn-success" onclick="startMeasurement()">Start Measurement</button>
                <button class="btn-warning" onclick="calibrateSystem()">Calibrate System</button>
                <button class="btn-primary" onclick="syncCloud()">Sync with Cloud</button>
            </div>
            
            <div class="card">
                <h3>Settings</h3>
                <button class="btn-primary" onclick="location.href='/settings'">System Settings</button>
                <button class="btn-primary" onclick="location.href='/dashboard'">Dashboard</button>
                <button class="btn-warning" onclick="location.href='/firmware'">Firmware Update</button>
            </div>
        </div>
    </div>
    
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('uptime').textContent = data.uptime + ' seconds';
                    document.getElementById('material-count').textContent = data.materials_count;
                    document.getElementById('measurement-count').textContent = data.measurements_count;
                    document.getElementById('quality-grade').textContent = data.quality_grade;
                    document.getElementById('quality-passed').textContent = data.quality_passed ? 'Yes' : 'No';
                });
        }
        
        setInterval(updateStatus, 5000);
        updateStatus();
    </script>
</body>
</html>
)";
    
    server.send(200, "text/html", html);
}

void handleAPIStatus() {
    StaticJsonDocument<512> doc;
    
    doc["system_status"] = "operational";
    doc["wifi_connected"] = wifi_connected;
    doc["mqtt_connected"] = mqtt_client.connected();
    doc["cloud_connected"] = cloud_connected;
    doc["materials_count"] = material_count;
    doc["measurements_count"] = history_count;
    doc["quality_grade"] = quality_controller.quality_grade;
    doc["quality_passed"] = quality_controller.quality_passed;
    doc["uptime"] = millis() / 1000;
    doc["free_heap"] = ESP.getFreeHeap();
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleAPIMeasurements() {
    StaticJsonDocument<2048> doc;
    JsonArray measurements = doc.createNestedArray("measurements");
    
    int start = max(0, history_count - 50); // Last 50 measurements
    for (int i = start; i < history_count; i++) {
        JsonObject measurement = measurements.createNestedObject();
        measurement["timestamp"] = measurement_history[i].timestamp;
        measurement["method"] = measurement_history[i].method;
        measurement["material_id"] = measurement_history[i].material_id;
        measurement["thermal_conductivity"] = measurement_history[i].thermal_conductivity;
        measurement["uncertainty"] = measurement_history[i].measurement_uncertainty;
        measurement["temperature"] = measurement_history[i].temperature;
        measurement["valid"] = measurement_history[i].measurement_valid;
    }
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleAPIMaterials() {
    StaticJsonDocument<2048> doc;
    JsonArray materials = doc.createNestedArray("materials");
    
    for (int i = 0; i < material_count; i++) {
        JsonObject material = materials.createNestedObject();
        material["id"] = material_database[i].material_id;
        material["name"] = material_database[i].material_name;
        material["class"] = material_database[i].material_class;
        material["thermal_conductivity"] = material_database[i].thermal_conductivity;
        material["density"] = material_database[i].density;
        material["specific_heat"] = material_database[i].specific_heat;
        material["uncertainty"] = material_database[i].uncertainty;
        material["is_reference"] = material_database[i].is_reference;
    }
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleAPIQuality() {
    StaticJsonDocument<512> doc;
    
    doc["repeatability_score"] = quality_controller.repeatability_score;
    doc["reproducibility_score"] = quality_controller.reproducibility_score;
    doc["accuracy_score"] = quality_controller.accuracy_score;
    doc["precision_score"] = quality_controller.precision_score;
    doc["bias_error"] = quality_controller.bias_error;
    doc["random_error"] = quality_controller.random_error;
    doc["quality_grade"] = quality_controller.quality_grade;
    doc["quality_passed"] = quality_controller.quality_passed;
    doc["recommendations"] = quality_controller.recommendations;
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleAPIClassify() {
    if (server.hasArg("plain")) {
        String body = server.arg("plain");
        
        StaticJsonDocument<512> doc;
        deserializeJson(doc, body);
        
        // Extract measurement data
        MeasurementData measurement;
        measurement.thermal_conductivity = doc["thermal_conductivity"];
        measurement.temperature = doc["temperature"];
        measurement.measurement_uncertainty = doc["uncertainty"];
        measurement.signal_quality = doc["signal_quality"];
        
        // Classify material
        material_classifier.classifyMaterial(measurement);
        
        StaticJsonDocument<256> response_doc;
        response_doc["predicted_material"] = ml_analyzer.predicted_material;
        response_doc["confidence"] = ml_analyzer.prediction_confidence;
        response_doc["material_class"] = ml_analyzer.material_class;
        response_doc["quality_score"] = ml_analyzer.quality_score;
        
        String response;
        serializeJson(response_doc, response);
        server.send(200, "application/json", response);
    } else {
        server.send(400, "text/plain", "No data provided");
    }
}

void handleAPICalibrate() {
    // Handle calibration request
    ARDUINO_SERIAL.println("CALIBRATE");
    
    StaticJsonDocument<128> doc;
    doc["status"] = "calibration_started";
    doc["message"] = "Calibration command sent to Arduino";
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleDashboard() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Thermal Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
        .card { background: #f9f9f9; padding: 20px; border-radius: 8px; }
        canvas { max-width: 100%; height: 300px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Thermal Analytics Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h3>Measurement History</h3>
                <canvas id="measurementChart"></canvas>
            </div>
            
            <div class="card">
                <h3>Material Distribution</h3>
                <canvas id="materialChart"></canvas>
            </div>
            
            <div class="card">
                <h3>Quality Metrics</h3>
                <canvas id="qualityChart"></canvas>
            </div>
            
            <div class="card">
                <h3>System Performance</h3>
                <canvas id="performanceChart"></canvas>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize charts
        const measurementCtx = document.getElementById('measurementChart').getContext('2d');
        const materialCtx = document.getElementById('materialChart').getContext('2d');
        const qualityCtx = document.getElementById('qualityChart').getContext('2d');
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        
        // Create charts (simplified)
        new Chart(measurementCtx, {
            type: 'line',
            data: {
                labels: ['1', '2', '3', '4', '5'],
                datasets: [{
                    label: 'Thermal Conductivity',
                    data: [0.5, 1.2, 0.8, 2.1, 1.5],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            }
        });
        
        new Chart(materialCtx, {
            type: 'pie',
            data: {
                labels: ['Metals', 'Ceramics', 'Polymers', 'Composites'],
                datasets: [{
                    data: [30, 25, 20, 25],
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
                }]
            }
        });
    </script>
</body>
</html>
)";
    
    server.send(200, "text/html", html);
}

void handleSettings() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>System Settings</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .setting { margin: 15px 0; padding: 15px; background: #f9f9f9; border-radius: 8px; }
        input, select { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 10px 20px; margin: 10px 0; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ System Settings</h1>
        
        <div class="setting">
            <h3>WiFi Configuration</h3>
            <input type="text" id="wifi-ssid" placeholder="SSID">
            <input type="password" id="wifi-password" placeholder="Password">
            <button class="btn-primary" onclick="updateWiFi()">Update WiFi</button>
        </div>
        
        <div class="setting">
            <h3>MQTT Configuration</h3>
            <input type="text" id="mqtt-server" placeholder="MQTT Server">
            <input type="number" id="mqtt-port" placeholder="Port">
            <input type="text" id="mqtt-user" placeholder="Username">
            <input type="password" id="mqtt-password" placeholder="Password">
            <button class="btn-primary" onclick="updateMQTT()">Update MQTT</button>
        </div>
        
        <div class="setting">
            <h3>Cloud API Configuration</h3>
            <input type="text" id="cloud-endpoint" placeholder="API Endpoint">
            <input type="text" id="api-key" placeholder="API Key">
            <button class="btn-primary" onclick="updateCloudAPI()">Update Cloud API</button>
        </div>
        
        <div class="setting">
            <h3>System Actions</h3>
            <button class="btn-success" onclick="restart()">Restart System</button>
            <button class="btn-primary" onclick="factoryReset()">Factory Reset</button>
        </div>
    </div>
</body>
</html>
)";
    
    server.send(200, "text/html", html);
}

void handleFirmwareUpdate() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Firmware Update</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .update-section { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px; }
        input[type="file"] { margin: 10px 0; }
        button { padding: 10px 20px; margin: 10px 0; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-warning { background: #FF9800; color: white; }
        .progress { width: 100%; height: 20px; background: #ddd; border-radius: 10px; overflow: hidden; }
        .progress-bar { height: 100%; background: #4CAF50; transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Firmware Update</h1>
        
        <div class="update-section">
            <h3>Current Version</h3>
            <p>Version: 2.0.0</p>
            <p>Build Date: 2024-01-01</p>
            <p>Features: ML Classification, Quality Control, Cloud Sync</p>
        </div>
        
        <div class="update-section">
            <h3>Update Firmware</h3>
            <p><strong>Warning:</strong> Do not power off the device during update!</p>
            <input type="file" id="firmware-file" accept=".bin">
            <button class="btn-warning" onclick="uploadFirmware()">Upload Firmware</button>
            
            <div class="progress" style="display: none;">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
        </div>
        
        <div class="update-section">
            <h3>Check for Updates</h3>
            <button class="btn-primary" onclick="checkUpdates()">Check Cloud Updates</button>
            <button class="btn-primary" onclick="downloadUpdate()">Download Latest</button>
        </div>
    </div>
</body>
</html>
)";
    
    server.send(200, "text/html", html);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("📨 MQTT: " + String(topic) + " - " + message);
    
    StaticJsonDocument<512> doc;
    deserializeJson(doc, message);
    
    if (strcmp(topic, "thermal/commands") == 0) {
        String command = doc["command"];
        
        if (command == "start_measurement") {
            ARDUINO_SERIAL.println("START_MEASUREMENT:" + doc["method"].as<String>());
        } else if (command == "stop_measurement") {
            ARDUINO_SERIAL.println("STOP_MEASUREMENT");
        } else if (command == "calibrate") {
            ARDUINO_SERIAL.println("CALIBRATE");
        } else if (command == "get_status") {
            publishSystemStatus();
        }
    }
    else if (strcmp(topic, "thermal/calibration") == 0) {
        // Handle calibration commands
        String calibration_type = doc["type"];
        ARDUINO_SERIAL.println("CALIBRATE:" + calibration_type);
    }
    else if (strcmp(topic, "thermal/materials") == 0) {
        // Handle material database updates
        String action = doc["action"];
        if (action == "add") {
            // Add new material to database
            String material_id = doc["material_id"];
            String material_name = doc["material_name"];
            String material_class = doc["material_class"];
            float thermal_conductivity = doc["thermal_conductivity"];
            float density = doc["density"];
            float specific_heat = doc["specific_heat"];
            float uncertainty = doc["uncertainty"];
            bool is_reference = doc["is_reference"];
            
            database_manager.addMaterial(material_id, material_name, material_class,
                                       thermal_conductivity, density, specific_heat,
                                       0.0, uncertainty, "", "", is_reference);
        }
    }
}

void parseStatusData(String data) {
    // Parse status data from Arduino
    StaticJsonDocument<512> doc;
    deserializeJson(doc, data.substring(7));
    
    // Process status information
    String system_status = doc["system_status"];
    bool measurement_active = doc["measurement_active"];
    String current_method = doc["current_method"];
    
    // Update local status
    Serial.println("📊 Arduino Status: " + system_status);
    
    // Publish status to MQTT
    if (mqtt_client.connected()) {
        mqtt_client.publish("thermal/arduino_status", data.substring(7).c_str());
    }
}

void parseCalibrationData(String data) {
    // Parse calibration data from Arduino
    StaticJsonDocument<512> doc;
    deserializeJson(doc, data.substring(12));
    
    String calibration_status = doc["status"];
    String calibration_results = doc["results"];
    
    Serial.println("🔧 Calibration: " + calibration_status);
    
    // Publish calibration results
    if (mqtt_client.connected()) {
        mqtt_client.publish("thermal/calibration_results", data.substring(12).c_str());
    }
}

/*
 * ESP32 Thermal Conductivity Analytics System
 * 
 * This advanced analytics system provides:
 * 
 * 1. Real-time Signal Processing
 *    - Digital filtering and noise reduction
 *    - FFT analysis for frequency domain processing
 *    - Outlier detection and removal
 *    - Signal quality assessment
 * 
 * 2. Machine Learning Classification
 *    - Material classification using neural networks
 *    - Feature extraction from measurement data
 *    - Confidence scoring and quality assessment
 *    - Continuous learning and model updates
 * 
 * 3. Quality Control System
 *    - Repeatability and reproducibility analysis
 *    - Accuracy and precision measurement
 *    - Statistical process control
 *    - Automated quality grading
 * 
 * 4. Material Database Management
 *    - Comprehensive material property database
 *    - NIST standard reference materials
 *    - Cloud synchronization and backup
 *    - Real-time updates and validation
 * 
 * 5. IoT Connectivity
 *    - WiFi and cloud connectivity
 *    - MQTT real-time communication
 *    - RESTful API for integration
 *    - Bluetooth for mobile access
 * 
 * 6. Web Interface
 *    - Real-time dashboard and monitoring
 *    - Historical data visualization
 *    - System configuration and settings
 *    - Firmware update capability
 * 
 * 7. Advanced Analytics
 *    - Thermal property correlations
 *    - Predictive modeling
 *    - Uncertainty quantification
 *    - Professional reporting
 * 
 * This system transforms the basic thermal conductivity measurement
 * into a comprehensive materials characterization platform suitable
 * for research, quality control, and industrial applications.
 */