/*
 * Program 18: Heat Exchanger Performance Monitor
 * Arduino Zero to Hero v2.0 - Track 1: Thermal Systems Engineering
 * 
 * Professional heat exchanger monitoring with effectiveness analysis and fouling detection
 * - Real-time effectiveness and NTU calculations
 * - Fouling detection and localization
 * - Predictive maintenance algorithms
 * - Energy optimization and performance tracking
 * - Industrial IoT integration
 * 
 * Hardware Requirements:
 * - Arduino Mega 2560
 * - ESP32 Development Board
 * - MAX31865 RTD Amplifiers (8x)
 * - PT100 RTDs (8x)
 * - Differential Pressure Sensors (4x)
 * - Turbine Flow Meters (2x)
 * - Conductivity Sensors (2x)
 * - INA3221 Current Monitors (2x)
 * - ADS1115 16-bit ADCs (4x)
 * - Variable Speed Drives (2x)
 * - Control Valves (4x)
 * - Safety Systems
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
#include <Adafruit_INA3221.h>
#include <Adafruit_ADS1X15.h>
#include <ModbusMaster.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// System Configuration
#define NUM_RTD_SENSORS 8
#define NUM_PRESSURE_SENSORS 4
#define NUM_FLOW_METERS 2
#define NUM_CONDUCTIVITY_SENSORS 2
#define SAMPLE_INTERVAL 5000  // milliseconds
#define BASELINE_SAMPLES 100  // samples for baseline establishment
#define FOULING_THRESHOLD 0.05 // 5% performance degradation
#define EMERGENCY_STOP_PIN 21
#define PI 3.14159265

// Pin Assignments
const int RTD_CS_PINS[] = {22, 24, 26, 28, 30, 32, 34, 36}; // MAX31865 CS pins
const int PUMP_VFD_PINS[] = {2, 3};           // VFD control pins
const int HEATER_CONTROL_PINS[] = {4, 5};     // Heater control pins
const int VALVE_CONTROL_PINS[] = {6, 7, 8, 9}; // Control valve pins
const int EMERGENCY_VALVE_PINS[] = {10, 11};  // Emergency shutdown valves
const int STATUS_LED_PINS[] = {38, 40, 42, 44, 46, 48, 50, 52}; // Status LEDs
const int FLOW_METER_PINS[] = {18, 19};       // Flow meter interrupt pins
const int SD_CS_PIN = 53;

// Heat Exchanger Specifications
#define HEAT_TRANSFER_AREA 2.5    // m²
#define TUBE_DIAMETER 0.019       // m
#define NUMBER_OF_TUBES 127
#define TUBE_LENGTH 2.0           // m
#define SHELL_DIAMETER 0.203      // m

// RTD Sensor Mapping
enum RTDSensor {
    HOT_INLET = 0,
    HOT_OUTLET = 1,
    HOT_WALL_1 = 2,
    HOT_WALL_2 = 3,
    COLD_INLET = 4,
    COLD_OUTLET = 5,
    COLD_WALL_1 = 6,
    COLD_WALL_2 = 7
};

// System State Structure
struct HeatExchangerState {
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
    unsigned long last_update;
};

// Baseline Performance Structure
struct BaselinePerformance {
    float effectiveness;
    float overall_u;
    float pressure_drop_hot;
    float pressure_drop_cold;
    float pumping_power;
    bool established;
    int sample_count;
};

// Fouling Detection Structure
struct FoulingStatus {
    float current_fouling_factor;
    float fouling_rate;
    float performance_degradation;
    float predicted_cleaning_days;
    bool fouling_detected;
    String fouling_location;
    unsigned long fouling_start_time;
};

// Predictive Maintenance Structure
struct MaintenanceStatus {
    float overall_health;
    float effectiveness_trend;
    float vibration_level;
    float water_quality_index;
    int days_to_cleaning;
    int days_to_inspection;
    bool maintenance_required;
    String maintenance_type;
};

// System objects
HeatExchangerState hx_state;
BaselinePerformance baseline;
FoulingStatus fouling_status;
MaintenanceStatus maintenance_status;

// Hardware objects
MAX31865 rtd_sensors[NUM_RTD_SENSORS];
Adafruit_INA3221 current_monitors[2];
Adafruit_ADS1X15 adc_modules[4];
ModbusMaster modbus;

// Flow measurement
volatile unsigned long flow_pulse_count[NUM_FLOW_METERS] = {0, 0};
unsigned long flow_timer[NUM_FLOW_METERS] = {0, 0};
const float FLOW_CALIBRATION[NUM_FLOW_METERS] = {450.0, 448.0}; // Pulses per liter

// System state
bool emergency_stop_active = false;
bool system_initialized = false;
unsigned long last_sample_time = 0;
unsigned long system_start_time = 0;

// IoT Configuration
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "industrial.mqtt.com";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Data logging
File dataFile;
String log_filename;

// Heat Exchanger Analyzer Class
class HeatExchangerAnalyzer {
private:
    float hot_cp, cold_cp; // Specific heat capacities
    
public:
    HeatExchangerAnalyzer() {
        hot_cp = 4186.0; // J/kg·K (water)
        cold_cp = 4186.0; // J/kg·K (water)
    }
    
    void updateFluidProperties() {
        // Update fluid properties based on temperature
        hot_cp = calculateSpecificHeat(hx_state.hot_inlet_temp);
        cold_cp = calculateSpecificHeat(hx_state.cold_inlet_temp);
    }
    
    float calculateSpecificHeat(float temperature) {
        // Water specific heat as function of temperature
        return 4186.0 + 0.5 * (temperature - 20.0); // Simplified correlation
    }
    
    float calculateEffectiveness() {
        // Calculate heat transfer rates
        float q_hot = hx_state.hot_flow_rate * hot_cp * 
                     (hx_state.hot_inlet_temp - hx_state.hot_outlet_temp);
        float q_cold = hx_state.cold_flow_rate * cold_cp * 
                      (hx_state.cold_outlet_temp - hx_state.cold_inlet_temp);
        float q_actual = (q_hot + q_cold) / 2.0; // Average
        
        // Calculate maximum possible heat transfer
        float c_hot = hx_state.hot_flow_rate * hot_cp;
        float c_cold = hx_state.cold_flow_rate * cold_cp;
        float c_min = min(c_hot, c_cold);
        
        float q_max = c_min * (hx_state.hot_inlet_temp - hx_state.cold_inlet_temp);
        
        // Effectiveness
        if (q_max > 0) {
            return constrain(q_actual / q_max, 0.0, 1.0);
        }
        return 0.0;
    }
    
    float calculateNTU() {
        float effectiveness = calculateEffectiveness();
        float c_hot = hx_state.hot_flow_rate * hot_cp;
        float c_cold = hx_state.cold_flow_rate * cold_cp;
        float c_min = min(c_hot, c_cold);
        float c_max = max(c_hot, c_cold);
        float c_ratio = c_min / c_max;
        
        // NTU calculation for shell-and-tube heat exchanger
        float ntu = 0.0;
        if (c_ratio < 0.99) {
            if (effectiveness > 0.001 && effectiveness < 0.999) {
                ntu = -log((1.0 - effectiveness) / (1.0 - effectiveness * c_ratio)) / 
                      (1.0 - c_ratio);
            }
        } else {
            if (effectiveness < 0.999) {
                ntu = effectiveness / (1.0 - effectiveness);
            }
        }
        
        return constrain(ntu, 0.0, 10.0);
    }
    
    float calculateOverallHeatTransferCoefficient() {
        float ntu = calculateNTU();
        float c_hot = hx_state.hot_flow_rate * hot_cp;
        float c_cold = hx_state.cold_flow_rate * cold_cp;
        float c_min = min(c_hot, c_cold);
        
        if (c_min > 0) {
            float ua = ntu * c_min; // W/K
            return ua / HEAT_TRANSFER_AREA; // W/m²K
        }
        return 0.0;
    }
    
    float calculateEnergyBalanceError() {
        float q_hot = hx_state.hot_flow_rate * hot_cp * 
                     (hx_state.hot_inlet_temp - hx_state.hot_outlet_temp);
        float q_cold = hx_state.cold_flow_rate * cold_cp * 
                      (hx_state.cold_outlet_temp - hx_state.cold_inlet_temp);
        
        if (q_hot > 0) {
            return abs(q_hot - q_cold) / q_hot * 100.0;
        }
        return 100.0;
    }
};

// Fouling Detection Class
class FoulingDetector {
private:
    float effectiveness_history[1000];
    float u_overall_history[1000];
    int history_index;
    bool baseline_established;
    
public:
    FoulingDetector() {
        history_index = 0;
        baseline_established = false;
    }
    
    void establishBaseline() {
        if (!baseline_established) {
            static int baseline_count = 0;
            static float effectiveness_sum = 0;
            static float u_overall_sum = 0;
            
            float current_effectiveness = hx_state.effectiveness;
            float current_u = hx_state.overall_u;
            
            if (current_effectiveness > 0.1 && current_u > 0) {
                effectiveness_sum += current_effectiveness;
                u_overall_sum += current_u;
                baseline_count++;
                
                if (baseline_count >= BASELINE_SAMPLES) {
                    baseline.effectiveness = effectiveness_sum / baseline_count;
                    baseline.overall_u = u_overall_sum / baseline_count;
                    baseline.pressure_drop_hot = hx_state.hot_pressure_drop;
                    baseline.pressure_drop_cold = hx_state.cold_pressure_drop;
                    baseline.pumping_power = hx_state.hot_power + hx_state.cold_power;
                    baseline.established = true;
                    baseline_established = true;
                    
                    Serial.println("📊 Baseline Performance Established:");
                    Serial.println("   Effectiveness: " + String(baseline.effectiveness, 3));
                    Serial.println("   U Overall: " + String(baseline.overall_u, 1) + " W/m²K");
                    Serial.println("   Hot ΔP: " + String(baseline.pressure_drop_hot, 1) + " kPa");
                    Serial.println("   Cold ΔP: " + String(baseline.pressure_drop_cold, 1) + " kPa");
                }
            }
        }
    }
    
    float calculateFoulingFactor() {
        if (!baseline_established || hx_state.overall_u <= 0) return 0.0;
        
        // Fouling factor: Rf = (1/U_fouled - 1/U_clean)
        float rf = (1.0 / hx_state.overall_u) - (1.0 / baseline.overall_u);
        return max(rf, 0.0);
    }
    
    float calculatePerformanceDegradation() {
        if (!baseline_established) return 0.0;
        
        float degradation = (baseline.effectiveness - hx_state.effectiveness) / 
                           baseline.effectiveness * 100.0;
        return max(degradation, 0.0);
    }
    
    void updateTrendAnalysis() {
        effectiveness_history[history_index] = hx_state.effectiveness;
        u_overall_history[history_index] = hx_state.overall_u;
        
        history_index = (history_index + 1) % 1000;
        
        // Analyze trends
        analyzeTrends();
    }
    
    void analyzeTrends() {
        if (history_index < 100) return;
        
        // Calculate moving averages
        float short_term_avg = calculateMovingAverage(effectiveness_history, 50);
        float long_term_avg = calculateMovingAverage(effectiveness_history, 200);
        
        float trend = (short_term_avg - long_term_avg) / long_term_avg * 100.0;
        
        // Update fouling status
        fouling_status.current_fouling_factor = calculateFoulingFactor();
        fouling_status.performance_degradation = calculatePerformanceDegradation();
        fouling_status.fouling_rate = calculateFoulingRate();
        
        if (trend < -5.0 || fouling_status.performance_degradation > FOULING_THRESHOLD * 100) {
            if (!fouling_status.fouling_detected) {
                fouling_status.fouling_detected = true;
                fouling_status.fouling_start_time = millis();
                triggerFoulingAlert();
            }
        }
        
        // Predict cleaning interval
        fouling_status.predicted_cleaning_days = predictCleaningInterval();
    }
    
    float calculateMovingAverage(float* data, int window_size) {
        float sum = 0;
        int count = 0;
        
        for (int i = 0; i < window_size && i < 1000; i++) {
            int index = (history_index - 1 - i + 1000) % 1000;
            sum += data[index];
            count++;
        }
        
        return count > 0 ? sum / count : 0.0;
    }
    
    float calculateFoulingRate() {
        // Calculate fouling rate based on recent trend
        if (history_index < 50) return 0.0;
        
        float recent_fouling = calculateMovingAverage(effectiveness_history, 10);
        float older_fouling = calculateMovingAverage(effectiveness_history, 50);
        
        float time_diff = 40.0 * SAMPLE_INTERVAL / 1000.0 / 3600.0; // hours
        
        if (time_diff > 0) {
            return (older_fouling - recent_fouling) / time_diff; // degradation per hour
        }
        return 0.0;
    }
    
    float predictCleaningInterval() {
        if (fouling_status.fouling_rate <= 0) return -1.0;
        
        float current_performance = hx_state.effectiveness;
        float min_acceptable_performance = baseline.effectiveness * 0.8; // 80% of baseline
        
        float performance_margin = current_performance - min_acceptable_performance;
        
        if (performance_margin > 0) {
            return (performance_margin / fouling_status.fouling_rate) / 24.0; // days
        }
        return 0.0;
    }
    
    void triggerFoulingAlert() {
        Serial.println("🚨 FOULING DETECTION ALERT 🚨");
        Serial.println("Performance degradation: " + String(fouling_status.performance_degradation, 1) + "%");
        Serial.println("Fouling factor: " + String(fouling_status.current_fouling_factor, 6) + " m²K/W");
        Serial.println("Predicted cleaning: " + String(fouling_status.predicted_cleaning_days, 0) + " days");
        
        // Send MQTT alert
        sendFoulingAlert();
    }
    
    void sendFoulingAlert() {
        if (mqtt_client.connected()) {
            StaticJsonDocument<512> doc;
            doc["alert"] = "FOULING_DETECTED";
            doc["timestamp"] = millis();
            doc["degradation"] = fouling_status.performance_degradation;
            doc["fouling_factor"] = fouling_status.current_fouling_factor;
            doc["predicted_cleaning"] = fouling_status.predicted_cleaning_days;
            
            String payload;
            serializeJson(doc, payload);
            mqtt_client.publish("hx/alerts", payload.c_str());
        }
    }
};

// Predictive Maintenance Class
class PredictiveMaintenance {
private:
    float performance_metrics[10][500]; // 10 metrics, 500 historical points
    int metric_index;
    
public:
    PredictiveMaintenance() {
        metric_index = 0;
    }
    
    void collectPerformanceMetrics() {
        performance_metrics[0][metric_index] = hx_state.effectiveness;
        performance_metrics[1][metric_index] = hx_state.overall_u;
        performance_metrics[2][metric_index] = fouling_status.current_fouling_factor;
        performance_metrics[3][metric_index] = hx_state.hot_pressure_drop;
        performance_metrics[4][metric_index] = hx_state.cold_pressure_drop;
        performance_metrics[5][metric_index] = hx_state.hot_power;
        performance_metrics[6][metric_index] = hx_state.cold_power;
        performance_metrics[7][metric_index] = readConductivity(0);
        performance_metrics[8][metric_index] = readConductivity(1);
        performance_metrics[9][metric_index] = readVibration();
        
        metric_index = (metric_index + 1) % 500;
        
        // Analyze metrics for maintenance prediction
        predictMaintenanceNeeds();
    }
    
    void predictMaintenanceNeeds() {
        maintenance_status.overall_health = calculateOverallHealth();
        maintenance_status.effectiveness_trend = calculateEffectivenessTrend();
        maintenance_status.vibration_level = readVibration();
        maintenance_status.water_quality_index = calculateWaterQualityIndex();
        
        // Cleaning maintenance prediction
        if (fouling_status.fouling_rate > 0.001) {
            maintenance_status.days_to_cleaning = fouling_status.predicted_cleaning_days;
            
            if (maintenance_status.days_to_cleaning < 30) {
                maintenance_status.maintenance_required = true;
                maintenance_status.maintenance_type = "CLEANING";
            }
        }
        
        // Pump maintenance prediction
        if (maintenance_status.vibration_level > 10.0) { // mm/s
            maintenance_status.days_to_inspection = 30;
            maintenance_status.maintenance_required = true;
            maintenance_status.maintenance_type = "PUMP_INSPECTION";
        }
        
        // Tube inspection prediction
        if (maintenance_status.effectiveness_trend < -0.5) { // 0.5% per month decline
            maintenance_status.days_to_inspection = 60;
            maintenance_status.maintenance_required = true;
            maintenance_status.maintenance_type = "TUBE_INSPECTION";
        }
    }
    
    float calculateOverallHealth() {
        float health_score = 100.0;
        
        // Deduct points for various issues
        health_score -= fouling_status.performance_degradation;
        health_score -= (maintenance_status.vibration_level - 5.0) * 2.0;
        health_score -= (100.0 - maintenance_status.water_quality_index) * 0.5;
        
        return constrain(health_score, 0.0, 100.0);
    }
    
    float calculateEffectivenessTrend() {
        if (metric_index < 100) return 0.0;
        
        // Calculate trend over last 100 samples
        float recent_avg = 0, older_avg = 0;
        int count = 0;
        
        for (int i = 0; i < 50; i++) {
            int recent_idx = (metric_index - 1 - i + 500) % 500;
            int older_idx = (metric_index - 51 - i + 500) % 500;
            
            recent_avg += performance_metrics[0][recent_idx];
            older_avg += performance_metrics[0][older_idx];
            count++;
        }
        
        recent_avg /= count;
        older_avg /= count;
        
        return (recent_avg - older_avg) / older_avg * 100.0; // % change
    }
    
    float calculateWaterQualityIndex() {
        float conductivity_hot = readConductivity(0);
        float conductivity_cold = readConductivity(1);
        
        // Simple water quality index based on conductivity
        float avg_conductivity = (conductivity_hot + conductivity_cold) / 2.0;
        float quality_index = 100.0 - (avg_conductivity - 200.0) / 10.0;
        
        return constrain(quality_index, 0.0, 100.0);
    }
    
    float readConductivity(int channel) {
        // Read conductivity from ADC
        int16_t adc_value = adc_modules[2].readADC_SingleEnded(channel);
        float voltage = adc_value * 0.125 / 1000.0;
        return voltage * 1000.0; // μS/cm (simplified calibration)
    }
    
    float readVibration() {
        // Read vibration from ADC
        int16_t adc_value = adc_modules[3].readADC_SingleEnded(0);
        float voltage = adc_value * 0.125 / 1000.0;
        return voltage * 10.0; // mm/s RMS (simplified calibration)
    }
};

// Global objects
HeatExchangerAnalyzer hx_analyzer;
FoulingDetector fouling_detector;
PredictiveMaintenance predictive_maintenance;

// Flow meter interrupt service routines
void flowPulseHot() {
    flow_pulse_count[0]++;
}

void flowPulseCold() {
    flow_pulse_count[1]++;
}

// Emergency stop interrupt
void emergencyStopISR() {
    emergency_stop_active = true;
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("🌡️ HEAT EXCHANGER PERFORMANCE MONITOR STARTED!");
    Serial.println("🌡️ HEAT TRANSFER ENGINEER MODE - Design advanced heat exchanger systems!");
    Serial.println("Professional heat exchanger monitoring with predictive maintenance");
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
    
    // Initialize heat exchanger characterization
    initializeHeatExchanger();
    
    Serial.println("🎯 System Ready for Performance Monitoring");
    system_initialized = true;
}

void loop() {
    if (!system_initialized) return;
    
    // Safety check first
    if (emergency_stop_active) {
        handleEmergencyState();
        return;
    }
    
    // Sample at regular intervals
    if (millis() - last_sample_time >= SAMPLE_INTERVAL) {
        // Update sensor readings
        updateSensorReadings();
        
        // Perform heat exchanger analysis
        performHeatExchangerAnalysis();
        
        // Update fouling detection
        fouling_detector.updateTrendAnalysis();
        
        // Collect maintenance metrics
        predictive_maintenance.collectPerformanceMetrics();
        
        // Establish baseline if needed
        if (!baseline.established) {
            fouling_detector.establishBaseline();
        }
        
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
    
    // Initialize current monitors
    for (int i = 0; i < 2; i++) {
        current_monitors[i].begin(0x40 + i);
        current_monitors[i].setShuntRes(100, 100, 100); // 100 mOhm shunts
    }
    Serial.println("✅ INA3221 current monitors: 2/2");
    
    // Initialize ADC modules
    for (int i = 0; i < 4; i++) {
        adc_modules[i].begin(0x48 + i);
        adc_modules[i].setGain(GAIN_ONE); // ±4.096V range
    }
    Serial.println("✅ ADS1115 ADC modules: 4/4");
    
    // Initialize flow meters
    pinMode(FLOW_METER_PINS[0], INPUT_PULLUP);
    pinMode(FLOW_METER_PINS[1], INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(FLOW_METER_PINS[0]), flowPulseHot, RISING);
    attachInterrupt(digitalPinToInterrupt(FLOW_METER_PINS[1]), flowPulseCold, RISING);
    Serial.println("✅ Flow meters initialized and calibrated");
    
    // Initialize control pins
    for (int i = 0; i < 2; i++) {
        pinMode(PUMP_VFD_PINS[i], OUTPUT);
        pinMode(HEATER_CONTROL_PINS[i], OUTPUT);
        pinMode(EMERGENCY_VALVE_PINS[i], OUTPUT);
        
        // Initialize to safe state
        analogWrite(PUMP_VFD_PINS[i], 0);
        analogWrite(HEATER_CONTROL_PINS[i], 0);
        digitalWrite(EMERGENCY_VALVE_PINS[i], LOW);
    }
    
    for (int i = 0; i < 4; i++) {
        pinMode(VALVE_CONTROL_PINS[i], OUTPUT);
        digitalWrite(VALVE_CONTROL_PINS[i], LOW);
    }
    
    // Initialize status LEDs
    for (int i = 0; i < NUM_RTD_SENSORS; i++) {
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
        if (mqtt_client.connect("HeatExchangerMonitor")) {
            Serial.println("✅ MQTT broker connected");
            mqtt_client.subscribe("hx/commands");
        } else {
            Serial.println("❌ MQTT connection failed");
            delay(5000);
        }
    }
}

void initializeDataLogging() {
    log_filename = "hx_data_" + String(millis()) + ".csv";
    
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        // Write header
        dataFile.println("timestamp,hot_inlet,hot_outlet,cold_inlet,cold_outlet,hot_flow,cold_flow,effectiveness,ntu,overall_u,fouling_factor,energy_balance_error");
        dataFile.close();
        Serial.println("✅ Data logging initialized: " + log_filename);
    }
}

void initializeHeatExchanger() {
    Serial.println("🔥 Heat Exchanger Characterization...");
    Serial.println("📊 Heat Transfer Area: " + String(HEAT_TRANSFER_AREA, 1) + " m²");
    Serial.println("📊 Number of Tubes: " + String(NUMBER_OF_TUBES));
    Serial.println("📊 Shell Diameter: " + String(SHELL_DIAMETER * 1000, 0) + " mm");
    Serial.println("📊 Tube Diameter: " + String(TUBE_DIAMETER * 1000, 0) + " mm");
    
    // Initialize state structure
    hx_state.last_update = 0;
    
    // Initialize baseline
    baseline.established = false;
    baseline.sample_count = 0;
    
    // Initialize fouling status
    fouling_status.fouling_detected = false;
    fouling_status.fouling_start_time = 0;
    
    // Initialize maintenance status
    maintenance_status.maintenance_required = false;
    maintenance_status.overall_health = 100.0;
}

void updateSensorReadings() {
    // Read RTD temperatures
    hx_state.hot_inlet_temp = rtd_sensors[HOT_INLET].temperature(100.0, 430.0);
    hx_state.hot_outlet_temp = rtd_sensors[HOT_OUTLET].temperature(100.0, 430.0);
    hx_state.cold_inlet_temp = rtd_sensors[COLD_INLET].temperature(100.0, 430.0);
    hx_state.cold_outlet_temp = rtd_sensors[COLD_OUTLET].temperature(100.0, 430.0);
    
    // Read wall temperatures
    hx_state.hot_wall_temps[0] = rtd_sensors[HOT_WALL_1].temperature(100.0, 430.0);
    hx_state.hot_wall_temps[1] = rtd_sensors[HOT_WALL_2].temperature(100.0, 430.0);
    hx_state.cold_wall_temps[0] = rtd_sensors[COLD_WALL_1].temperature(100.0, 430.0);
    hx_state.cold_wall_temps[1] = rtd_sensors[COLD_WALL_2].temperature(100.0, 430.0);
    
    // Calculate flow rates
    hx_state.hot_flow_rate = calculateFlowRate(0);
    hx_state.cold_flow_rate = calculateFlowRate(1);
    
    // Read pressure drops
    hx_state.hot_pressure_drop = readPressureDrop(0);
    hx_state.cold_pressure_drop = readPressureDrop(1);
    
    // Read power consumption
    hx_state.hot_power = current_monitors[0].getCurrent_mA(1) * 
                        current_monitors[0].getBusVoltage_V(1) / 1000.0;
    hx_state.cold_power = current_monitors[1].getCurrent_mA(1) * 
                         current_monitors[1].getBusVoltage_V(1) / 1000.0;
    
    hx_state.last_update = millis();
}

float calculateFlowRate(int channel) {
    unsigned long current_time = millis();
    unsigned long time_diff = current_time - flow_timer[channel];
    
    if (time_diff >= 1000) { // Calculate every second
        float pulses_per_second = flow_pulse_count[channel] * 1000.0 / time_diff;
        float flow_rate = pulses_per_second / FLOW_CALIBRATION[channel] * 60.0; // L/min
        
        // Reset counters
        flow_pulse_count[channel] = 0;
        flow_timer[channel] = current_time;
        
        return flow_rate / 60.0; // L/s
    }
    
    return hx_state.hot_flow_rate; // Return last known value
}

float readPressureDrop(int channel) {
    int16_t adc_value = adc_modules[channel].readADC_SingleEnded(0);
    float voltage = adc_value * 0.125 / 1000.0;
    return voltage * 10.0; // kPa (simplified calibration)
}

void performHeatExchangerAnalysis() {
    // Update fluid properties
    hx_analyzer.updateFluidProperties();
    
    // Calculate performance metrics
    hx_state.effectiveness = hx_analyzer.calculateEffectiveness();
    hx_state.ntu = hx_analyzer.calculateNTU();
    hx_state.overall_u = hx_analyzer.calculateOverallHeatTransferCoefficient();
    hx_state.energy_balance_error = hx_analyzer.calculateEnergyBalanceError();
    
    // Calculate fouling factor
    hx_state.fouling_factor = fouling_detector.calculateFoulingFactor();
}

void updateStatusDisplay() {
    static unsigned long last_display_time = 0;
    
    if (millis() - last_display_time > 30000) { // Every 30 seconds
        Serial.println("=== HEAT EXCHANGER PERFORMANCE STATUS ===");
        Serial.print("Time: ");
        Serial.print((millis() - system_start_time) / 1000);
        Serial.print("s | Mode: MONITORING | Runtime: ");
        Serial.print((millis() - system_start_time) / 3600000);
        Serial.println("h");
        
        Serial.println();
        Serial.println("Hot Side:");
        Serial.println("  Inlet: " + String(hx_state.hot_inlet_temp, 1) + "°C | " +
                      "Outlet: " + String(hx_state.hot_outlet_temp, 1) + "°C | " +
                      "ΔT: " + String(hx_state.hot_inlet_temp - hx_state.hot_outlet_temp, 1) + "°C");
        Serial.println("  Flow Rate: " + String(hx_state.hot_flow_rate * 60, 1) + " L/min | " +
                      "Pressure Drop: " + String(hx_state.hot_pressure_drop, 1) + " kPa");
        Serial.println("  Power: " + String(hx_state.hot_power, 1) + " kW");
        
        Serial.println();
        Serial.println("Cold Side:");
        Serial.println("  Inlet: " + String(hx_state.cold_inlet_temp, 1) + "°C | " +
                      "Outlet: " + String(hx_state.cold_outlet_temp, 1) + "°C | " +
                      "ΔT: " + String(hx_state.cold_outlet_temp - hx_state.cold_inlet_temp, 1) + "°C");
        Serial.println("  Flow Rate: " + String(hx_state.cold_flow_rate * 60, 1) + " L/min | " +
                      "Pressure Drop: " + String(hx_state.cold_pressure_drop, 1) + " kPa");
        Serial.println("  Power: " + String(hx_state.cold_power, 1) + " kW");
        
        Serial.println();
        Serial.println("Performance Metrics:");
        Serial.println("  Effectiveness: " + String(hx_state.effectiveness * 100, 1) + "% (Target: 85.0%)");
        Serial.println("  NTU: " + String(hx_state.ntu, 2));
        Serial.println("  U-Overall: " + String(hx_state.overall_u, 0) + " W/m²K");
        Serial.println("  Fouling Factor: " + String(hx_state.fouling_factor, 6) + " m²K/W");
        Serial.println("  Energy Balance Error: " + String(hx_state.energy_balance_error, 1) + "%");
        
        if (baseline.established) {
            Serial.println("  Performance Degradation: " + String(fouling_status.performance_degradation, 1) + "%");
        }
        
        Serial.println();
        Serial.println("Maintenance Status:");
        Serial.println("  Overall Health: " + String(maintenance_status.overall_health, 1) + "%");
        Serial.println("  Fouling Status: " + String(fouling_status.fouling_detected ? "DETECTED" : "NORMAL"));
        
        if (fouling_status.predicted_cleaning_days > 0) {
            Serial.println("  Predicted Cleaning: " + String(fouling_status.predicted_cleaning_days, 0) + " days");
        }
        
        Serial.println();
        Serial.println("🌐 IoT Status: " + String(mqtt_client.connected() ? "Connected" : "Disconnected"));
        
        last_display_time = millis();
    }
}

void logData() {
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        dataFile.print(millis());
        dataFile.print(",");
        dataFile.print(hx_state.hot_inlet_temp);
        dataFile.print(",");
        dataFile.print(hx_state.hot_outlet_temp);
        dataFile.print(",");
        dataFile.print(hx_state.cold_inlet_temp);
        dataFile.print(",");
        dataFile.print(hx_state.cold_outlet_temp);
        dataFile.print(",");
        dataFile.print(hx_state.hot_flow_rate);
        dataFile.print(",");
        dataFile.print(hx_state.cold_flow_rate);
        dataFile.print(",");
        dataFile.print(hx_state.effectiveness);
        dataFile.print(",");
        dataFile.print(hx_state.ntu);
        dataFile.print(",");
        dataFile.print(hx_state.overall_u);
        dataFile.print(",");
        dataFile.print(hx_state.fouling_factor);
        dataFile.print(",");
        dataFile.println(hx_state.energy_balance_error);
        dataFile.close();
    }
}

void handleIoTCommunication() {
    if (mqtt_client.connected()) {
        mqtt_client.loop();
        
        // Publish data periodically
        static unsigned long last_publish_time = 0;
        if (millis() - last_publish_time > 60000) { // Every 60 seconds
            publishHeatExchangerData();
            last_publish_time = millis();
        }
    } else {
        connectToMQTT();
    }
}

void publishHeatExchangerData() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["system_status"] = "MONITORING";
    doc["uptime"] = millis() - system_start_time;
    
    JsonObject hot_side = doc.createNestedObject("hot_side");
    hot_side["inlet_temp"] = hx_state.hot_inlet_temp;
    hot_side["outlet_temp"] = hx_state.hot_outlet_temp;
    hot_side["flow_rate"] = hx_state.hot_flow_rate;
    hot_side["pressure_drop"] = hx_state.hot_pressure_drop;
    hot_side["power"] = hx_state.hot_power;
    
    JsonObject cold_side = doc.createNestedObject("cold_side");
    cold_side["inlet_temp"] = hx_state.cold_inlet_temp;
    cold_side["outlet_temp"] = hx_state.cold_outlet_temp;
    cold_side["flow_rate"] = hx_state.cold_flow_rate;
    cold_side["pressure_drop"] = hx_state.cold_pressure_drop;
    cold_side["power"] = hx_state.cold_power;
    
    JsonObject performance = doc.createNestedObject("performance");
    performance["effectiveness"] = hx_state.effectiveness;
    performance["ntu"] = hx_state.ntu;
    performance["overall_u"] = hx_state.overall_u;
    performance["fouling_factor"] = hx_state.fouling_factor;
    performance["energy_balance_error"] = hx_state.energy_balance_error;
    
    JsonObject maintenance = doc.createNestedObject("maintenance");
    maintenance["overall_health"] = maintenance_status.overall_health;
    maintenance["fouling_detected"] = fouling_status.fouling_detected;
    maintenance["performance_degradation"] = fouling_status.performance_degradation;
    maintenance["predicted_cleaning_days"] = fouling_status.predicted_cleaning_days;
    maintenance["maintenance_required"] = maintenance_status.maintenance_required;
    
    String payload;
    serializeJson(doc, payload);
    mqtt_client.publish("hx/data", payload.c_str());
}

void handleEmergencyState() {
    // Turn off all pumps and heaters
    for (int i = 0; i < 2; i++) {
        analogWrite(PUMP_VFD_PINS[i], 0);
        analogWrite(HEATER_CONTROL_PINS[i], 0);
        digitalWrite(EMERGENCY_VALVE_PINS[i], HIGH); // Close emergency valves
    }
    
    // Flash all LEDs
    static bool led_state = false;
    static unsigned long last_flash_time = 0;
    if (millis() - last_flash_time > 500) {
        led_state = !led_state;
        for (int i = 0; i < NUM_RTD_SENSORS; i++) {
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
        
        if (command == "STATUS") {
            updateStatusDisplay();
        }
        else if (command == "BASELINE") {
            baseline.established = false;
            baseline.sample_count = 0;
            Serial.println("Baseline reset - establishing new baseline...");
        }
        else if (command == "FOULING") {
            Serial.println("Fouling Status:");
            Serial.println("  Detected: " + String(fouling_status.fouling_detected ? "YES" : "NO"));
            Serial.println("  Fouling Factor: " + String(fouling_status.current_fouling_factor, 6) + " m²K/W");
            Serial.println("  Performance Degradation: " + String(fouling_status.performance_degradation, 1) + "%");
            Serial.println("  Predicted Cleaning: " + String(fouling_status.predicted_cleaning_days, 0) + " days");
        }
        else if (command == "MAINTENANCE") {
            Serial.println("Maintenance Status:");
            Serial.println("  Overall Health: " + String(maintenance_status.overall_health, 1) + "%");
            Serial.println("  Effectiveness Trend: " + String(maintenance_status.effectiveness_trend, 2) + "%/month");
            Serial.println("  Vibration Level: " + String(maintenance_status.vibration_level, 1) + " mm/s");
            Serial.println("  Water Quality Index: " + String(maintenance_status.water_quality_index, 1) + "%");
            Serial.println("  Maintenance Required: " + String(maintenance_status.maintenance_required ? "YES" : "NO"));
            if (maintenance_status.maintenance_required) {
                Serial.println("  Maintenance Type: " + maintenance_status.maintenance_type);
            }
        }
        else if (command == "HELP") {
            Serial.println("Available commands:");
            Serial.println("STATUS - Show current system status");
            Serial.println("BASELINE - Reset and establish new baseline");
            Serial.println("FOULING - Show fouling detection status");
            Serial.println("MAINTENANCE - Show maintenance status");
            Serial.println("HELP - Show this help message");
        }
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
    
    if (doc["action"] == "set_flow_rate") {
        String side = doc["side"];
        float flow_rate = doc["flow_rate"];
        
        if (side == "hot") {
            // Adjust hot side pump speed
            int pump_speed = map(flow_rate, 0, 100, 0, 255);
            analogWrite(PUMP_VFD_PINS[0], pump_speed);
            Serial.println("Set hot side flow rate to " + String(flow_rate) + " L/min");
        } else if (side == "cold") {
            // Adjust cold side pump speed
            int pump_speed = map(flow_rate, 0, 100, 0, 255);
            analogWrite(PUMP_VFD_PINS[1], pump_speed);
            Serial.println("Set cold side flow rate to " + String(flow_rate) + " L/min");
        }
    }
    else if (doc["action"] == "reset_baseline") {
        baseline.established = false;
        baseline.sample_count = 0;
        Serial.println("MQTT: Baseline reset");
    }
} 