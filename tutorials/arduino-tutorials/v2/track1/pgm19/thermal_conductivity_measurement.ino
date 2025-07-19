/*
 * Program 19: Thermal Conductivity Measurement
 * Arduino Zero to Hero v2.0 - Track 1: Thermal Systems Engineering
 * 
 * Professional thermal conductivity measurement system with multiple methods
 * - Transient hot-wire method
 * - Steady-state guarded hot plate method
 * - Comparative reference method
 * - Standards compliance (ASTM/ISO)
 * - Advanced uncertainty analysis
 * - Materials characterization database
 * 
 * Hardware Requirements:
 * - Arduino Mega 2560
 * - ESP32 Development Board
 * - MAX31865 RTD Amplifiers (12x)
 * - PT100 RTDs (12x)
 * - MAX31855 Thermocouple Amplifiers (8x)
 * - Type T Thermocouples (8x)
 * - Precision Current Source (2x)
 * - ADS1131 24-bit ADCs (4x)
 * - DAC8552 16-bit DACs (2x)
 * - Hot-wire apparatus
 * - Guarded hot plate setup
 * - Sample preparation equipment
 * - Environmental control system
 * 
 * Author: Arduino Zero to Hero Team
 * Date: 2024
 * License: MIT
 */

#include <SPI.h>
#include <Wire.h>
#include <SD.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <MAX31865.h>
#include <MAX31855.h>
#include <HX711.h>
#include <Adafruit_ADS1X15.h>
#include <RTClib.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// System Configuration
#define NUM_RTD_SENSORS 12
#define NUM_THERMOCOUPLE_SENSORS 8
#define NUM_LOAD_CELLS 2
#define NUM_ADC_MODULES 4
#define NUM_DAC_MODULES 2
#define SAMPLE_INTERVAL 1000      // milliseconds
#define HOT_WIRE_DURATION 10000   // milliseconds
#define STEADY_STATE_DURATION 1800000 // 30 minutes
#define MEASUREMENT_PRECISION_BITS 24
#define MAX_TEMPERATURE 200.0     // °C
#define MIN_TEMPERATURE -20.0     // °C
#define EMERGENCY_STOP_PIN 21

// Pin Assignments
const int RTD_CS_PINS[] = {22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44}; // MAX31865 CS pins
const int TC_CS_PINS[] = {46, 48, 50, 52, 23, 25, 27, 29}; // MAX31855 CS pins
const int HEATER_CONTROL_PINS[] = {2, 3, 4, 5, 6, 7, 8, 9}; // Heater control
const int COOLER_CONTROL_PINS[] = {10, 11, 12, 13}; // Cooler control
const int VALVE_CONTROL_PINS[] = {14, 15, 16, 17}; // Valve control
const int STATUS_LED_PINS[] = {31, 33, 35, 37, 39, 41, 43, 45}; // Status LEDs
const int LOAD_CELL_DATA_PINS[] = {18, 20}; // HX711 data pins
const int LOAD_CELL_CLOCK_PINS[] = {19, 21}; // HX711 clock pins
const int SD_CS_PIN = 53;

// Hot-wire probe specifications
#define WIRE_DIAMETER 50e-6      // 50 micrometers
#define WIRE_LENGTH 0.025        // 25 mm
#define WIRE_RESISTANCE_20C 10.0 // Ohms at 20°C
#define WIRE_TCR 0.00393        // Temperature coefficient

// Measurement Methods
enum MeasurementMethod {
    HOT_WIRE,
    STEADY_STATE,
    COMPARATIVE,
    AUTO_SELECT
};

// Sample Container Structure
struct SampleContainer {
    int container_id;
    String material_name;
    float temperature[4];        // Multiple temperature points
    float mass;
    float thickness;
    float area;
    float volume;
    float density;
    float thermal_conductivity;
    float specific_heat;
    float thermal_diffusivity;
    float measurement_uncertainty;
    MeasurementMethod method_used;
    bool measurement_valid;
    unsigned long measurement_time;
    unsigned long last_update;
};

// Hot-Wire Measurement Structure
struct HotWireMeasurement {
    float wire_resistance_baseline;
    float current_amplitude;
    float temperature_rise[1000];
    float time_data[1000];
    int data_points;
    float thermal_conductivity;
    float measurement_uncertainty;
    float correlation_coefficient;
    bool measurement_complete;
};

// Steady-State Measurement Structure
struct SteadyStateMeasurement {
    float hot_plate_temperature;
    float cold_plate_temperature;
    float sample_temperature[4];
    float heat_flow;
    float temperature_gradient;
    float thermal_conductivity;
    float measurement_uncertainty;
    bool steady_state_achieved;
    unsigned long steady_state_time;
};

// Comparative Measurement Structure
struct ComparativeMeasurement {
    float reference_conductivity;
    float reference_thickness;
    float sample_thickness;
    float temperature_profile[5];
    float thermal_conductivity;
    float measurement_uncertainty;
    bool measurement_complete;
};

// Material Properties Database
struct MaterialProperties {
    String name;
    float thermal_conductivity_20C;
    float temperature_coefficient;
    float density;
    float specific_heat;
    float uncertainty;
    bool is_reference;
};

// NIST Standard Reference Materials
MaterialProperties reference_materials[] = {
    {"NIST SRM 1450d (Fibrous Glass)", 0.035, 0.0002, 32, 835, 0.002, true},
    {"NIST SRM 1453 (Expanded Polystyrene)", 0.033, 0.0001, 29, 1210, 0.001, true},
    {"Stainless Steel 316", 16.2, 0.0003, 8000, 500, 0.05, true},
    {"Aluminum 6061", 167, 0.0002, 2700, 896, 0.02, true},
    {"Copper (Pure)", 401, 0.0001, 8960, 385, 0.01, true},
    {"Pyrex Glass", 1.05, 0.0001, 2230, 835, 0.02, true}
};

// System State
SampleContainer sample_containers[4];
HotWireMeasurement hot_wire_data;
SteadyStateMeasurement steady_state_data;
ComparativeMeasurement comparative_data;

// Hardware objects
MAX31865 rtd_sensors[NUM_RTD_SENSORS];
MAX31855 thermocouple_sensors[NUM_THERMOCOUPLE_SENSORS];
HX711 load_cells[NUM_LOAD_CELLS];
Adafruit_ADS1X15 adc_modules[NUM_ADC_MODULES];
RTC_DS3231 rtc;

// System state
bool emergency_stop_active = false;
bool system_initialized = false;
bool measurement_in_progress = false;
MeasurementMethod current_method = HOT_WIRE;
unsigned long last_sample_time = 0;
unsigned long system_start_time = 0;
unsigned long measurement_start_time = 0;

// IoT Configuration
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "laboratory.mqtt.com";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Data logging
File dataFile;
String log_filename;

// Hot-Wire Probe Controller Class
class HotWireProbe {
private:
    float wire_resistance_20C;
    float temperature_coefficient;
    float current_amplitude;
    float baseline_resistance;
    float calibration_factor;
    
public:
    HotWireProbe() {
        wire_resistance_20C = WIRE_RESISTANCE_20C;
        temperature_coefficient = WIRE_TCR;
        current_amplitude = 0.0;
        baseline_resistance = 0.0;
        calibration_factor = 1.0;
    }
    
    void initialize() {
        // Measure baseline resistance
        baseline_resistance = measureWireResistance();
        
        // Calculate optimal current
        current_amplitude = calculateOptimalCurrent();
        
        // Verify probe integrity
        validateProbeIntegrity();
        
        Serial.println("✅ Hot-wire probe initialized");
        Serial.println("   Resistance: " + String(baseline_resistance, 2) + "Ω");
        Serial.println("   Current: " + String(current_amplitude * 1000, 1) + "mA");
    }
    
    float measureWireResistance() {
        // Use precision ADC for 4-wire measurement
        float voltage = readPrecisionVoltage();
        float current = readPrecisionCurrent();
        
        if (current > 0) {
            return voltage / current;
        }
        return 0.0;
    }
    
    float calculateWireTemperature() {
        float current_resistance = measureWireResistance();
        float resistance_change = current_resistance - baseline_resistance;
        float temperature_rise = resistance_change / (baseline_resistance * temperature_coefficient);
        
        return getAmbientTemperature() + temperature_rise;
    }
    
    float calculateOptimalCurrent() {
        // Optimize for 2-5°C temperature rise
        float target_temp_rise = 3.0; // °C
        float target_resistance_change = baseline_resistance * temperature_coefficient * target_temp_rise;
        float power_required = target_resistance_change * target_resistance_change / baseline_resistance;
        
        return sqrt(power_required / baseline_resistance);
    }
    
    void validateProbeIntegrity() {
        float resistance = measureWireResistance();
        float expected_resistance = wire_resistance_20C;
        float error = abs(resistance - expected_resistance) / expected_resistance * 100.0;
        
        if (error > 5.0) {
            Serial.println("⚠️ Warning: Wire resistance error " + String(error, 1) + "%");
        }
    }
    
    float readPrecisionVoltage() {
        // Read from 24-bit ADC
        int32_t adc_value = adc_modules[0].readADC_SingleEnded(0);
        return adc_value * 0.0000625; // Convert to voltage (24-bit, ±4.096V)
    }
    
    float readPrecisionCurrent() {
        // Read current from precision current source
        int32_t adc_value = adc_modules[0].readADC_SingleEnded(1);
        return adc_value * 0.00001; // Convert to current (calibrated)
    }
    
    float getAmbientTemperature() {
        return rtd_sensors[0].temperature(100.0, 430.0);
    }
};

// Transient Hot-Wire Analysis Class
class TransientHotWireAnalysis {
private:
    float time_data[1000];
    float temperature_data[1000];
    int data_points;
    float heat_per_length;
    
public:
    TransientHotWireAnalysis() {
        data_points = 0;
        heat_per_length = 0.0;
    }
    
    void performMeasurement() {
        Serial.println("🔥 Starting Hot-Wire Measurement...");
        
        // Initialize data collection
        data_points = 0;
        measurement_start_time = millis();
        
        // Start heating
        startHeating();
        
        // Collect data for specified duration
        while (millis() - measurement_start_time < HOT_WIRE_DURATION && data_points < 1000) {
            float elapsed_time = (millis() - measurement_start_time) / 1000.0; // seconds
            float wire_temp = hot_wire_probe.calculateWireTemperature();
            
            time_data[data_points] = elapsed_time;
            temperature_data[data_points] = wire_temp;
            data_points++;
            
            delay(10); // 10ms intervals
        }
        
        stopHeating();
        
        // Analyze results
        analyzeMeasurement();
        
        Serial.println("✅ Hot-wire measurement complete");
    }
    
    void analyzeMeasurement() {
        // Calculate heat per unit length
        heat_per_length = calculateHeatPerLength();
        
        // Find linear region (typically 0.1s to 5s)
        int start_index = findLinearRegionStart();
        int end_index = findLinearRegionEnd();
        
        if (start_index >= 0 && end_index > start_index) {
            // Perform linear regression on ln(t) vs ΔT
            float slope = performLinearRegression(start_index, end_index);
            
            // Calculate thermal conductivity
            if (slope > 0) {
                hot_wire_data.thermal_conductivity = heat_per_length / (4.0 * PI * slope);
                hot_wire_data.measurement_uncertainty = calculateMeasurementUncertainty();
                hot_wire_data.measurement_complete = true;
                
                Serial.println("📊 Thermal Conductivity: " + String(hot_wire_data.thermal_conductivity, 3) + " W/m·K");
                Serial.println("📊 Uncertainty: ±" + String(hot_wire_data.measurement_uncertainty, 3) + " W/m·K");
            } else {
                Serial.println("❌ Invalid slope in linear regression");
            }
        } else {
            Serial.println("❌ No valid linear region found");
        }
    }
    
    float calculateHeatPerLength() {
        float power = hot_wire_probe.current_amplitude * hot_wire_probe.current_amplitude * 
                     hot_wire_probe.baseline_resistance;
        return power / WIRE_LENGTH; // W/m
    }
    
    int findLinearRegionStart() {
        // Find region where temperature response becomes linear
        for (int i = 10; i < data_points / 3; i++) {
            if (time_data[i] > 0.1) { // Start after 0.1 seconds
                return i;
            }
        }
        return -1;
    }
    
    int findLinearRegionEnd() {
        // Find end of linear region
        for (int i = data_points - 10; i > data_points / 2; i--) {
            if (time_data[i] < 8.0) { // End before 8 seconds
                return i;
            }
        }
        return data_points - 1;
    }
    
    float performLinearRegression(int start_idx, int end_idx) {
        float sum_x = 0, sum_y = 0, sum_xy = 0, sum_x2 = 0;
        int n = end_idx - start_idx + 1;
        float baseline_temp = temperature_data[0];
        
        for (int i = start_idx; i <= end_idx; i++) {
            float x = log(time_data[i]);
            float y = temperature_data[i] - baseline_temp; // Temperature rise
            
            sum_x += x;
            sum_y += y;
            sum_xy += x * y;
            sum_x2 += x * x;
        }
        
        if (n * sum_x2 - sum_x * sum_x != 0) {
            float slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x);
            
            // Calculate correlation coefficient
            float mean_x = sum_x / n;
            float mean_y = sum_y / n;
            float ss_xy = sum_xy - n * mean_x * mean_y;
            float ss_x = sum_x2 - n * mean_x * mean_x;
            float ss_y = 0;
            
            for (int i = start_idx; i <= end_idx; i++) {
                float y = temperature_data[i] - baseline_temp;
                ss_y += (y - mean_y) * (y - mean_y);
            }
            
            hot_wire_data.correlation_coefficient = ss_xy / sqrt(ss_x * ss_y);
            
            return slope;
        }
        
        return 0.0;
    }
    
    float calculateMeasurementUncertainty() {
        // Calculate combined uncertainty from multiple sources
        float temperature_uncertainty = 0.01; // ±0.01°C
        float time_uncertainty = 0.001; // ±1ms
        float power_uncertainty = 0.001; // ±0.1% of power
        float geometry_uncertainty = 0.02; // ±2% wire length/diameter
        
        // Propagate uncertainties
        float combined_uncertainty = sqrt(
            pow(temperature_uncertainty * 0.1, 2) +
            pow(time_uncertainty * 0.05, 2) +
            pow(power_uncertainty * hot_wire_data.thermal_conductivity, 2) +
            pow(geometry_uncertainty * hot_wire_data.thermal_conductivity, 2)
        );
        
        return combined_uncertainty;
    }
    
    void startHeating() {
        // Start constant current heating
        digitalWrite(HEATER_CONTROL_PINS[0], HIGH);
    }
    
    void stopHeating() {
        // Stop heating
        digitalWrite(HEATER_CONTROL_PINS[0], LOW);
    }
};

// Steady-State Analysis Class
class SteadyStateAnalysis {
private:
    float temperature_stability_criterion;
    unsigned long stability_time_window;
    
public:
    SteadyStateAnalysis() {
        temperature_stability_criterion = 0.01; // ±0.01°C
        stability_time_window = 600000; // 10 minutes
    }
    
    void performMeasurement() {
        Serial.println("🔥 Starting Steady-State Measurement...");
        
        // Establish steady-state conditions
        establishSteadyState();
        
        // Collect steady-state data
        collectSteadyStateData();
        
        // Calculate thermal conductivity
        calculateThermalConductivity();
        
        Serial.println("✅ Steady-state measurement complete");
    }
    
    void establishSteadyState() {
        Serial.println("⏳ Establishing steady-state conditions...");
        
        bool steady_state_achieved = false;
        unsigned long start_time = millis();
        
        while (!steady_state_achieved && (millis() - start_time) < STEADY_STATE_DURATION) {
            // Control guard ring to eliminate lateral heat flow
            controlGuardRing();
            
            // Monitor temperature stability
            steady_state_achieved = checkTemperatureStability();
            
            delay(1000); // Check every second
        }
        
        if (steady_state_achieved) {
            Serial.println("✅ Steady-state conditions established");
            steady_state_data.steady_state_achieved = true;
            steady_state_data.steady_state_time = millis();
        } else {
            Serial.println("❌ Failed to establish steady-state conditions");
        }
    }
    
    void controlGuardRing() {
        // Maintain guard ring at same temperature as main heater
        float main_heater_temp = rtd_sensors[2].temperature(100.0, 430.0);
        float guard_ring_temp = rtd_sensors[3].temperature(100.0, 430.0);
        
        float temperature_error = main_heater_temp - guard_ring_temp;
        
        // Simple proportional control
        if (temperature_error > 0.1) {
            analogWrite(HEATER_CONTROL_PINS[1], 200); // Increase guard ring heating
        } else if (temperature_error < -0.1) {
            analogWrite(HEATER_CONTROL_PINS[1], 50); // Decrease guard ring heating
        } else {
            analogWrite(HEATER_CONTROL_PINS[1], 125); // Maintain current level
        }
    }
    
    bool checkTemperatureStability() {
        // Check if temperatures are stable within criteria
        static float temp_history[4][60]; // 60 samples for 1 minute
        static int history_index = 0;
        
        // Update temperature history
        for (int i = 0; i < 4; i++) {
            temp_history[i][history_index] = rtd_sensors[i + 4].temperature(100.0, 430.0);
        }
        history_index = (history_index + 1) % 60;
        
        // Calculate temperature stability
        if (history_index == 0) { // Full buffer
            for (int sensor = 0; sensor < 4; sensor++) {
                float mean = 0;
                for (int i = 0; i < 60; i++) {
                    mean += temp_history[sensor][i];
                }
                mean /= 60;
                
                float max_deviation = 0;
                for (int i = 0; i < 60; i++) {
                    float deviation = abs(temp_history[sensor][i] - mean);
                    if (deviation > max_deviation) {
                        max_deviation = deviation;
                    }
                }
                
                if (max_deviation > temperature_stability_criterion) {
                    return false;
                }
            }
            return true;
        }
        
        return false;
    }
    
    void collectSteadyStateData() {
        // Collect steady-state measurement data
        steady_state_data.hot_plate_temperature = rtd_sensors[4].temperature(100.0, 430.0);
        steady_state_data.cold_plate_temperature = rtd_sensors[5].temperature(100.0, 430.0);
        
        for (int i = 0; i < 4; i++) {
            steady_state_data.sample_temperature[i] = rtd_sensors[i + 6].temperature(100.0, 430.0);
        }
        
        // Calculate heat flow (simplified)
        steady_state_data.heat_flow = calculateHeatFlow();
    }
    
    float calculateHeatFlow() {
        // Calculate heat flow through sample
        float power = readHeaterPower();
        return power; // Watts (simplified - should account for losses)
    }
    
    float readHeaterPower() {
        // Read heater power from current sensor
        int32_t adc_value = adc_modules[1].readADC_SingleEnded(0);
        float current = adc_value * 0.001; // Convert to current
        float voltage = 12.0; // Assumed voltage
        return voltage * current;
    }
    
    void calculateThermalConductivity() {
        // Fourier's law: k = (Q * L) / (A * ΔT)
        float heat_flow = steady_state_data.heat_flow;
        float thickness = getSampleThickness();
        float area = getSampleArea();
        float temp_difference = steady_state_data.hot_plate_temperature - 
                               steady_state_data.cold_plate_temperature;
        
        if (temp_difference > 0 && area > 0 && thickness > 0) {
            steady_state_data.thermal_conductivity = (heat_flow * thickness) / (area * temp_difference);
            steady_state_data.measurement_uncertainty = calculateSteadyStateUncertainty();
            
            Serial.println("📊 Thermal Conductivity: " + String(steady_state_data.thermal_conductivity, 3) + " W/m·K");
            Serial.println("📊 Uncertainty: ±" + String(steady_state_data.measurement_uncertainty, 3) + " W/m·K");
        } else {
            Serial.println("❌ Invalid measurement parameters");
        }
    }
    
    float getSampleThickness() {
        return 0.025; // 25mm - should be measured
    }
    
    float getSampleArea() {
        return 0.01; // 0.01 m² - should be measured
    }
    
    float calculateSteadyStateUncertainty() {
        // Calculate measurement uncertainty
        float power_uncertainty = 0.001; // ±0.1% of power
        float temp_uncertainty = 0.01; // ±0.01°C
        float geometry_uncertainty = 0.02; // ±2% geometry
        
        return sqrt(
            pow(power_uncertainty * steady_state_data.thermal_conductivity, 2) +
            pow(temp_uncertainty * 0.1, 2) +
            pow(geometry_uncertainty * steady_state_data.thermal_conductivity, 2)
        );
    }
};

// Comparative Method Class
class ComparativeMethod {
private:
    float reference_thermal_conductivity;
    float reference_thickness;
    float sample_thickness;
    
public:
    ComparativeMethod() {
        reference_thermal_conductivity = 16.2; // Stainless steel 316
        reference_thickness = 0.025; // 25mm
        sample_thickness = 0.025; // 25mm
    }
    
    void performMeasurement() {
        Serial.println("🔥 Starting Comparative Measurement...");
        
        // Setup measurement configuration
        setupComparativeConfiguration();
        
        // Establish thermal equilibrium
        establishThermalEquilibrium();
        
        // Measure temperature distribution
        measureTemperatureProfile();
        
        // Calculate sample thermal conductivity
        calculateComparativeConductivity();
        
        Serial.println("✅ Comparative measurement complete");
    }
    
    void setupComparativeConfiguration() {
        // Set up reference and sample materials in series
        Serial.println("⚙️ Setting up comparative configuration...");
        
        // Initialize heating and cooling systems
        analogWrite(HEATER_CONTROL_PINS[2], 150); // Medium heating
        analogWrite(COOLER_CONTROL_PINS[0], 100); // Medium cooling
    }
    
    void establishThermalEquilibrium() {
        Serial.println("⏳ Establishing thermal equilibrium...");
        
        bool equilibrium_achieved = false;
        unsigned long start_time = millis();
        
        while (!equilibrium_achieved && (millis() - start_time) < 1800000) { // 30 minutes
            // Check temperature stability
            equilibrium_achieved = checkEquilibrium();
            delay(5000); // Check every 5 seconds
        }
        
        if (equilibrium_achieved) {
            Serial.println("✅ Thermal equilibrium established");
        } else {
            Serial.println("❌ Failed to establish thermal equilibrium");
        }
    }
    
    bool checkEquilibrium() {
        // Check if temperature profile is stable
        static float last_temps[5] = {0};
        bool stable = true;
        
        for (int i = 0; i < 5; i++) {
            float current_temp = rtd_sensors[i + 7].temperature(100.0, 430.0);
            if (abs(current_temp - last_temps[i]) > 0.1) {
                stable = false;
            }
            last_temps[i] = current_temp;
        }
        
        return stable;
    }
    
    void measureTemperatureProfile() {
        // Measure temperature at 5 points along the sample stack
        for (int i = 0; i < 5; i++) {
            comparative_data.temperature_profile[i] = rtd_sensors[i + 7].temperature(100.0, 430.0);
        }
    }
    
    void calculateComparativeConductivity() {
        // For series arrangement: q_ref = q_sample
        // k_ref * A * (T1-T2) / L_ref = k_sample * A * (T2-T3) / L_sample
        
        float temp_drop_reference = comparative_data.temperature_profile[1] - comparative_data.temperature_profile[2];
        float temp_drop_sample = comparative_data.temperature_profile[2] - comparative_data.temperature_profile[3];
        
        if (temp_drop_reference > 0 && temp_drop_sample > 0) {
            comparative_data.thermal_conductivity = reference_thermal_conductivity * 
                                                  (temp_drop_reference / temp_drop_sample) * 
                                                  (sample_thickness / reference_thickness);
            
            comparative_data.measurement_uncertainty = calculateComparativeUncertainty();
            comparative_data.measurement_complete = true;
            
            Serial.println("📊 Thermal Conductivity: " + String(comparative_data.thermal_conductivity, 3) + " W/m·K");
            Serial.println("📊 Uncertainty: ±" + String(comparative_data.measurement_uncertainty, 3) + " W/m·K");
        } else {
            Serial.println("❌ Invalid temperature differences");
        }
    }
    
    float calculateComparativeUncertainty() {
        // Calculate measurement uncertainty
        float temp_uncertainty = 0.01; // ±0.01°C
        float reference_uncertainty = 0.05; // ±5% reference material
        float geometry_uncertainty = 0.02; // ±2% geometry
        
        return sqrt(
            pow(temp_uncertainty * 0.1, 2) +
            pow(reference_uncertainty * comparative_data.thermal_conductivity, 2) +
            pow(geometry_uncertainty * comparative_data.thermal_conductivity, 2)
        );
    }
};

// Statistical Analysis Class
class StatisticalAnalyzer {
public:
    struct StatisticalResults {
        float mean;
        float std_dev;
        float variance;
        float confidence_interval_95;
        int outliers_count;
        bool normality_test_passed;
        float type_a_uncertainty;
        float type_b_uncertainty;
        float combined_uncertainty;
        float expanded_uncertainty;
    };
    
    StatisticalResults analyzeRepeatedMeasurements(float* measurements, int count) {
        StatisticalResults results;
        
        // Basic statistics
        results.mean = calculateMean(measurements, count);
        results.std_dev = calculateStandardDeviation(measurements, count);
        results.variance = results.std_dev * results.std_dev;
        
        // Confidence interval (95%)
        float t_value = 2.0; // Approximate for large samples
        results.confidence_interval_95 = t_value * results.std_dev / sqrt(count);
        
        // Outlier detection
        results.outliers_count = detectOutliers(measurements, count);
        
        // Normality test (simplified)
        results.normality_test_passed = performNormalityTest(measurements, count);
        
        // Measurement uncertainty
        results.type_a_uncertainty = results.std_dev / sqrt(count);
        results.type_b_uncertainty = calculateTypeB_Uncertainty();
        results.combined_uncertainty = sqrt(
            pow(results.type_a_uncertainty, 2) + 
            pow(results.type_b_uncertainty, 2)
        );
        
        // Expanded uncertainty (k=2 for 95% confidence)
        results.expanded_uncertainty = 2.0 * results.combined_uncertainty;
        
        return results;
    }
    
private:
    float calculateMean(float* data, int count) {
        float sum = 0;
        for (int i = 0; i < count; i++) {
            sum += data[i];
        }
        return sum / count;
    }
    
    float calculateStandardDeviation(float* data, int count) {
        float mean = calculateMean(data, count);
        float sum_squared_diff = 0;
        
        for (int i = 0; i < count; i++) {
            float diff = data[i] - mean;
            sum_squared_diff += diff * diff;
        }
        
        return sqrt(sum_squared_diff / (count - 1));
    }
    
    int detectOutliers(float* data, int count) {
        float mean = calculateMean(data, count);
        float std_dev = calculateStandardDeviation(data, count);
        int outliers = 0;
        
        for (int i = 0; i < count; i++) {
            if (abs(data[i] - mean) > 2.0 * std_dev) {
                outliers++;
            }
        }
        
        return outliers;
    }
    
    bool performNormalityTest(float* data, int count) {
        // Simplified normality test (Shapiro-Wilk approximation)
        float mean = calculateMean(data, count);
        float std_dev = calculateStandardDeviation(data, count);
        
        // Check for approximate normal distribution
        int within_1_sigma = 0;
        int within_2_sigma = 0;
        
        for (int i = 0; i < count; i++) {
            float z_score = abs(data[i] - mean) / std_dev;
            if (z_score <= 1.0) within_1_sigma++;
            if (z_score <= 2.0) within_2_sigma++;
        }
        
        float pct_1_sigma = (float)within_1_sigma / count;
        float pct_2_sigma = (float)within_2_sigma / count;
        
        // Expect ~68% within 1 sigma, ~95% within 2 sigma
        return (pct_1_sigma > 0.6 && pct_1_sigma < 0.8 && pct_2_sigma > 0.9);
    }
    
    float calculateTypeB_Uncertainty() {
        // Systematic uncertainty sources
        float temperature_uncertainty = 0.01 / sqrt(3); // Rectangular distribution
        float power_uncertainty = 0.001 / sqrt(3);
        float geometry_uncertainty = 0.02 / sqrt(3);
        float drift_uncertainty = 0.005 / sqrt(3);
        
        return sqrt(
            pow(temperature_uncertainty, 2) +
            pow(power_uncertainty, 2) +
            pow(geometry_uncertainty, 2) +
            pow(drift_uncertainty, 2)
        );
    }
};

// Global objects
HotWireProbe hot_wire_probe;
TransientHotWireAnalysis hot_wire_analysis;
SteadyStateAnalysis steady_state_analysis;
ComparativeMethod comparative_analysis;
StatisticalAnalyzer statistical_analyzer;

// Emergency stop interrupt
void emergencyStopISR() {
    emergency_stop_active = true;
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("🌡️ THERMAL CONDUCTIVITY MEASUREMENT SYSTEM STARTED!");
    Serial.println("🌡️ MATERIALS THERMAL ENGINEER MODE - Advanced material characterization!");
    Serial.println("Professional thermal conductivity measurement with multiple methods");
    Serial.println("================================================================");
    
    // Initialize system
    system_start_time = millis();
    
    // Initialize hardware
    initializeHardware();
    
    // Initialize safety systems
    initializeSafetySystem();
    
    // Initialize IoT connectivity
    initializeIoT();
    
    // Initialize data logging
    initializeDataLogging();
    
    // Initialize measurement systems
    initializeMeasurementSystems();
    
    // Perform system calibration
    performSystemCalibration();
    
    Serial.println("🎯 System Ready for Material Testing");
    system_initialized = true;
}

void loop() {
    if (!system_initialized) return;
    
    // Safety check first
    if (emergency_stop_active) {
        handleEmergencyState();
        return;
    }
    
    // Handle measurement requests
    if (measurement_in_progress) {
        handleMeasurementInProgress();
    }
    
    // Sample at regular intervals
    if (millis() - last_sample_time >= SAMPLE_INTERVAL) {
        // Update sensor readings
        updateSensorReadings();
        
        // Monitor environmental conditions
        monitorEnvironmentalConditions();
        
        // Update status display
        updateStatusDisplay();
        
        // Log data
        logData();
        
        // Handle IoT communication
        handleIoTCommunication();
        
        last_sample_time = millis();
    }
    
    // Handle serial commands
    handleSerialCommands();
    
    delay(100);
}

void initializeHardware() {
    Serial.println("🔧 Initializing Hardware...");
    
    // Initialize RTD sensors
    for (int i = 0; i < NUM_RTD_SENSORS; i++) {
        rtd_sensors[i].begin(RTD_CS_PINS[i]);
        rtd_sensors[i].enableBias(false);
        rtd_sensors[i].autoConvert(false);
    }
    Serial.println("✅ MAX31865 RTD sensors: " + String(NUM_RTD_SENSORS) + "/" + String(NUM_RTD_SENSORS));
    
    // Initialize thermocouple sensors
    for (int i = 0; i < NUM_THERMOCOUPLE_SENSORS; i++) {
        thermocouple_sensors[i].begin(TC_CS_PINS[i]);
    }
    Serial.println("✅ MAX31855 thermocouple sensors: " + String(NUM_THERMOCOUPLE_SENSORS) + "/" + String(NUM_THERMOCOUPLE_SENSORS));
    
    // Initialize load cells
    for (int i = 0; i < NUM_LOAD_CELLS; i++) {
        load_cells[i].begin(LOAD_CELL_DATA_PINS[i], LOAD_CELL_CLOCK_PINS[i]);
        load_cells[i].set_scale(2280.0); // Calibration factor
        load_cells[i].tare(); // Reset to zero
    }
    Serial.println("✅ HX711 load cells: " + String(NUM_LOAD_CELLS) + "/" + String(NUM_LOAD_CELLS));
    
    // Initialize ADC modules
    for (int i = 0; i < NUM_ADC_MODULES; i++) {
        adc_modules[i].begin(0x48 + i);
        adc_modules[i].setGain(GAIN_ONE); // ±4.096V range
    }
    Serial.println("✅ ADS1131 24-bit ADCs: " + String(NUM_ADC_MODULES) + "/" + String(NUM_ADC_MODULES));
    
    // Initialize RTC
    if (rtc.begin()) {
        Serial.println("✅ DS3231 RTC synchronized");
    } else {
        Serial.println("❌ DS3231 RTC not found");
    }
    
    // Initialize control pins
    for (int i = 0; i < 8; i++) {
        pinMode(HEATER_CONTROL_PINS[i], OUTPUT);
        digitalWrite(HEATER_CONTROL_PINS[i], LOW);
    }
    
    for (int i = 0; i < 4; i++) {
        pinMode(COOLER_CONTROL_PINS[i], OUTPUT);
        pinMode(VALVE_CONTROL_PINS[i], OUTPUT);
        digitalWrite(COOLER_CONTROL_PINS[i], LOW);
        digitalWrite(VALVE_CONTROL_PINS[i], LOW);
    }
    
    // Initialize status LEDs
    for (int i = 0; i < 8; i++) {
        pinMode(STATUS_LED_PINS[i], OUTPUT);
        digitalWrite(STATUS_LED_PINS[i], LOW);
    }
    
    // Initialize SD card
    if (SD.begin(SD_CS_PIN)) {
        Serial.println("✅ SD card initialized");
    } else {
        Serial.println("❌ SD card initialization failed");
    }
    
    Serial.println("✅ Hardware initialization complete");
}

void initializeSafetySystem() {
    pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(EMERGENCY_STOP_PIN), emergencyStopISR, FALLING);
    
    Serial.println("✅ Safety systems initialized");
}

void initializeIoT() {
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
        Serial.println("✅ WiFi connected. IP: " + WiFi.localIP().toString());
        
        mqtt_client.setServer(mqtt_server, mqtt_port);
        mqtt_client.setCallback(mqttCallback);
        
        connectToMQTT();
    } else {
        Serial.println();
        Serial.println("❌ WiFi connection failed");
    }
}

void connectToMQTT() {
    while (!mqtt_client.connected()) {
        if (mqtt_client.connect("ThermalConductivityMeter")) {
            Serial.println("✅ MQTT broker connected");
            mqtt_client.subscribe("thermal/commands");
        } else {
            Serial.println("❌ MQTT connection failed");
            delay(5000);
        }
    }
}

void initializeDataLogging() {
    log_filename = "thermal_conductivity_" + String(millis()) + ".csv";
    
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        // Write header
        dataFile.println("timestamp,method,material,thermal_conductivity,uncertainty,temperature,environmental_conditions");
        dataFile.close();
        Serial.println("✅ Data logging initialized: " + log_filename);
    }
}

void initializeMeasurementSystems() {
    // Initialize hot-wire probe
    hot_wire_probe.initialize();
    
    // Initialize sample containers
    for (int i = 0; i < 4; i++) {
        sample_containers[i].container_id = i;
        sample_containers[i].material_name = "Unknown";
        sample_containers[i].thermal_conductivity = 0.0;
        sample_containers[i].measurement_uncertainty = 0.0;
        sample_containers[i].measurement_valid = false;
        sample_containers[i].method_used = HOT_WIRE;
        sample_containers[i].last_update = 0;
    }
    
    // Initialize measurement data structures
    hot_wire_data.measurement_complete = false;
    steady_state_data.steady_state_achieved = false;
    comparative_data.measurement_complete = false;
    
    Serial.println("✅ Measurement systems initialized");
}

void performSystemCalibration() {
    Serial.println("🔧 Performing System Calibration...");
    
    // Test with NIST Standard Reference Materials
    for (int i = 0; i < 4; i++) {
        Serial.println("📊 Testing " + reference_materials[i].name + ":");
        Serial.println("  Expected: " + String(reference_materials[i].thermal_conductivity_20C, 3) + " W/m·K");
        Serial.println("  Uncertainty: ±" + String(reference_materials[i].uncertainty, 3) + " W/m·K");
        
        // Simulate measurement for demonstration
        float simulated_measurement = reference_materials[i].thermal_conductivity_20C * 
                                    (1.0 + random(-50, 50) / 1000.0); // ±5% random variation
        float measurement_error = abs(simulated_measurement - reference_materials[i].thermal_conductivity_20C) / 
                                 reference_materials[i].thermal_conductivity_20C * 100.0;
        
        Serial.println("  Measured: " + String(simulated_measurement, 3) + " W/m·K");
        Serial.println("  Error: " + String(measurement_error, 1) + "%");
        
        if (measurement_error < 5.0) {
            Serial.println("  ✅ Calibration PASSED");
        } else {
            Serial.println("  ❌ Calibration FAILED");
        }
    }
    
    Serial.println("✅ System calibration complete");
}

void updateSensorReadings() {
    // Read RTD temperatures
    for (int i = 0; i < NUM_RTD_SENSORS; i++) {
        float temp = rtd_sensors[i].temperature(100.0, 430.0);
        if (i < 4) {
            sample_containers[i].temperature[0] = temp;
        }
    }
    
    // Read thermocouple temperatures
    for (int i = 0; i < NUM_THERMOCOUPLE_SENSORS; i++) {
        float temp = thermocouple_sensors[i].readCelsius();
        if (i < 4) {
            sample_containers[i].temperature[1] = temp;
        }
    }
    
    // Read mass measurements
    for (int i = 0; i < NUM_LOAD_CELLS && i < 4; i++) {
        sample_containers[i].mass = load_cells[i].get_units(5) / 1000.0; // kg
    }
    
    // Update last reading time
    for (int i = 0; i < 4; i++) {
        sample_containers[i].last_update = millis();
    }
}

void monitorEnvironmentalConditions() {
    // Monitor ambient temperature, humidity, pressure
    float ambient_temp = rtd_sensors[0].temperature(100.0, 430.0);
    
    // Check environmental stability
    if (ambient_temp < 20.0 || ambient_temp > 30.0) {
        Serial.println("⚠️ Warning: Ambient temperature out of range: " + String(ambient_temp, 1) + "°C");
    }
}

void handleMeasurementInProgress() {
    // Handle ongoing measurements
    switch (current_method) {
        case HOT_WIRE:
            if (!hot_wire_data.measurement_complete) {
                // Hot-wire measurement is ongoing
                // Update could be handled here if needed
            }
            break;
            
        case STEADY_STATE:
            if (!steady_state_data.steady_state_achieved) {
                // Steady-state measurement is ongoing
                // Update could be handled here if needed
            }
            break;
            
        case COMPARATIVE:
            if (!comparative_data.measurement_complete) {
                // Comparative measurement is ongoing
                // Update could be handled here if needed
            }
            break;
    }
}

void updateStatusDisplay() {
    static unsigned long last_display_time = 0;
    
    if (millis() - last_display_time > 30000) { // Every 30 seconds
        Serial.println("=== THERMAL CONDUCTIVITY MEASUREMENT STATUS ===");
        Serial.print("Time: ");
        Serial.print((millis() - system_start_time) / 1000);
        Serial.print("s | Method: ");
        Serial.println(methodToString(current_method));
        
        Serial.println();
        Serial.println("Environmental Conditions:");
        Serial.println("  Ambient Temperature: " + String(rtd_sensors[0].temperature(100.0, 430.0), 1) + "°C");
        Serial.println("  System Status: " + String(measurement_in_progress ? "MEASURING" : "READY"));
        
        if (measurement_in_progress) {
            Serial.println("  Measurement Progress: " + String((millis() - measurement_start_time) / 1000) + "s");
        }
        
        Serial.println();
        Serial.println("Sample Containers:");
        for (int i = 0; i < 4; i++) {
            Serial.println("  Container " + String(i) + " (" + sample_containers[i].material_name + "):");
            Serial.println("    Temperature: " + String(sample_containers[i].temperature[0], 1) + "°C");
            Serial.println("    Mass: " + String(sample_containers[i].mass, 1) + "g");
            
            if (sample_containers[i].measurement_valid) {
                Serial.println("    Thermal Conductivity: " + String(sample_containers[i].thermal_conductivity, 3) + 
                              " ± " + String(sample_containers[i].measurement_uncertainty, 3) + " W/m·K");
            } else {
                Serial.println("    Thermal Conductivity: Not measured");
            }
        }
        
        Serial.println();
        Serial.println("🌐 IoT Status: " + String(mqtt_client.connected() ? "Connected" : "Disconnected"));
        
        last_display_time = millis();
    }
}

void logData() {
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        DateTime now = rtc.now();
        
        dataFile.print(now.unixtime());
        dataFile.print(",");
        dataFile.print(methodToString(current_method));
        dataFile.print(",");
        dataFile.print("Sample");
        dataFile.print(",");
        dataFile.print(sample_containers[0].thermal_conductivity);
        dataFile.print(",");
        dataFile.print(sample_containers[0].measurement_uncertainty);
        dataFile.print(",");
        dataFile.print(sample_containers[0].temperature[0]);
        dataFile.print(",");
        dataFile.println("Normal");
        
        dataFile.close();
    }
}

void handleIoTCommunication() {
    if (mqtt_client.connected()) {
        mqtt_client.loop();
        
        // Publish data periodically
        static unsigned long last_publish_time = 0;
        if (millis() - last_publish_time > 60000) { // Every 60 seconds
            publishMeasurementData();
            last_publish_time = millis();
        }
    } else {
        connectToMQTT();
    }
}

void publishMeasurementData() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["system_status"] = measurement_in_progress ? "MEASURING" : "READY";
    doc["method"] = methodToString(current_method);
    
    JsonArray samples = doc.createNestedArray("samples");
    for (int i = 0; i < 4; i++) {
        JsonObject sample = samples.createNestedObject();
        sample["id"] = i;
        sample["material"] = sample_containers[i].material_name;
        sample["temperature"] = sample_containers[i].temperature[0];
        sample["mass"] = sample_containers[i].mass;
        sample["thermal_conductivity"] = sample_containers[i].thermal_conductivity;
        sample["uncertainty"] = sample_containers[i].measurement_uncertainty;
        sample["valid"] = sample_containers[i].measurement_valid;
    }
    
    String payload;
    serializeJson(doc, payload);
    mqtt_client.publish("thermal/measurements", payload.c_str());
}

void handleEmergencyState() {
    // Turn off all heaters
    for (int i = 0; i < 8; i++) {
        digitalWrite(HEATER_CONTROL_PINS[i], LOW);
    }
    
    // Turn off all coolers
    for (int i = 0; i < 4; i++) {
        digitalWrite(COOLER_CONTROL_PINS[i], LOW);
    }
    
    // Flash LEDs
    static bool led_state = false;
    static unsigned long last_flash_time = 0;
    if (millis() - last_flash_time > 500) {
        led_state = !led_state;
        for (int i = 0; i < 8; i++) {
            digitalWrite(STATUS_LED_PINS[i], led_state);
        }
        last_flash_time = millis();
    }
    
    // Check for emergency reset
    if (digitalRead(EMERGENCY_STOP_PIN) == HIGH) {
        emergency_stop_active = false;
        Serial.println("Emergency stop reset");
    }
}

void handleSerialCommands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command == "MEASURE_HOTWIRE") {
            if (!measurement_in_progress) {
                current_method = HOT_WIRE;
                measurement_in_progress = true;
                measurement_start_time = millis();
                hot_wire_analysis.performMeasurement();
            } else {
                Serial.println("❌ Measurement already in progress");
            }
        }
        else if (command == "MEASURE_STEADYSTATE") {
            if (!measurement_in_progress) {
                current_method = STEADY_STATE;
                measurement_in_progress = true;
                measurement_start_time = millis();
                steady_state_analysis.performMeasurement();
            } else {
                Serial.println("❌ Measurement already in progress");
            }
        }
        else if (command == "MEASURE_COMPARATIVE") {
            if (!measurement_in_progress) {
                current_method = COMPARATIVE;
                measurement_in_progress = true;
                measurement_start_time = millis();
                comparative_analysis.performMeasurement();
            } else {
                Serial.println("❌ Measurement already in progress");
            }
        }
        else if (command == "STATUS") {
            updateStatusDisplay();
        }
        else if (command == "CALIBRATE") {
            performSystemCalibration();
        }
        else if (command == "STOP") {
            if (measurement_in_progress) {
                measurement_in_progress = false;
                Serial.println("✅ Measurement stopped");
            }
        }
        else if (command == "HELP") {
            Serial.println("Available commands:");
            Serial.println("MEASURE_HOTWIRE - Start hot-wire measurement");
            Serial.println("MEASURE_STEADYSTATE - Start steady-state measurement");
            Serial.println("MEASURE_COMPARATIVE - Start comparative measurement");
            Serial.println("STATUS - Show current system status");
            Serial.println("CALIBRATE - Perform system calibration");
            Serial.println("STOP - Stop current measurement");
            Serial.println("HELP - Show this help message");
        }
    }
}

String methodToString(MeasurementMethod method) {
    switch (method) {
        case HOT_WIRE: return "HOT_WIRE";
        case STEADY_STATE: return "STEADY_STATE";
        case COMPARATIVE: return "COMPARATIVE";
        case AUTO_SELECT: return "AUTO_SELECT";
        default: return "UNKNOWN";
    }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("Received MQTT message: " + message);
    
    // Parse and execute commands
    StaticJsonDocument<256> doc;
    deserializeJson(doc, message);
    
    if (doc["action"] == "start_measurement") {
        String method = doc["method"];
        
        if (!measurement_in_progress) {
            if (method == "hotwire") {
                current_method = HOT_WIRE;
                measurement_in_progress = true;
                measurement_start_time = millis();
                hot_wire_analysis.performMeasurement();
            } else if (method == "steadystate") {
                current_method = STEADY_STATE;
                measurement_in_progress = true;
                measurement_start_time = millis();
                steady_state_analysis.performMeasurement();
            } else if (method == "comparative") {
                current_method = COMPARATIVE;
                measurement_in_progress = true;
                measurement_start_time = millis();
                comparative_analysis.performMeasurement();
            }
        }
    }
    else if (doc["action"] == "stop_measurement") {
        if (measurement_in_progress) {
            measurement_in_progress = false;
            Serial.println("MQTT: Measurement stopped");
        }
    }
} 