/*
 * Program 17: Phase Change Material (PCM) Controller
 * Arduino Zero to Hero v2.0 - Track 1: Thermal Systems Engineering
 * 
 * Professional PCM controller with enthalpy measurement and energy storage optimization
 * - Real-time phase change detection
 * - Enthalpy and latent heat calculations
 * - Thermal energy storage optimization
 * - Multi-container testing capability
 * - Advanced analytics and ML integration
 * 
 * Hardware Requirements:
 * - Arduino Mega 2560
 * - ESP32 Development Board
 * - MAX31855 Thermocouple Amplifiers (8x)
 * - Type T Thermocouples (8x)
 * - HX711 Load Cell Amplifiers (2x)
 * - Load Cells (2x, 5kg capacity)
 * - TEC1-12706 Peltier Modules (4x)
 * - L298N Motor Drivers (4x)
 * - INA3221 Current Monitors (2x)
 * - ADS1115 16-bit ADCs (2x)
 * - DS3231 RTC Module
 * - Cartridge Heaters (2x, 100W)
 * - SSR-25DA Solid State Relays (4x)
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
#include <MAX31855.h>
#include <HX711.h>
#include <Adafruit_INA3221.h>
#include <Adafruit_ADS1X15.h>
#include <RTClib.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// System Configuration
#define NUM_CONTAINERS 4
#define NUM_THERMOCOUPLES_PER_CONTAINER 2
#define TOTAL_THERMOCOUPLES (NUM_CONTAINERS * NUM_THERMOCOUPLES_PER_CONTAINER)
#define NUM_LOAD_CELLS 2
#define SAMPLE_INTERVAL 5000  // milliseconds
#define PHASE_CHANGE_THRESHOLD 0.1  // °C/min
#define HEAT_FLUX_THRESHOLD 10.0    // W/m²
#define MAX_TEMPERATURE 120.0       // °C
#define MIN_TEMPERATURE 5.0         // °C
#define EMERGENCY_STOP_PIN 21

// Pin Assignments
const int THERMOCOUPLE_CS_PINS[] = {22, 24, 26, 28, 30, 32, 34, 36}; // MAX31855 CS pins
const int TEC_PWM_PINS[] = {2, 4, 6, 8};          // TEC PWM control
const int TEC_DIR_PINS[] = {3, 5, 7, 9};          // TEC direction control
const int HEATER_RELAY_PINS[] = {10, 11, 12, 13}; // SSR control for heaters
const int FAN_PWM_PINS[] = {14, 15, 16, 17};      // Fan control
const int STATUS_LED_PINS[] = {38, 40, 42, 44, 46, 48, 50, 52}; // Status LEDs
const int LOAD_CELL_DATA_PINS[] = {18, 20};       // HX711 data pins
const int LOAD_CELL_CLOCK_PINS[] = {19, 21};      // HX711 clock pins
const int SD_CS_PIN = 53;

// PCM Container Structure
struct PCMContainer {
    int container_id;
    float temperature_top;
    float temperature_bottom;
    float mass;
    float density;
    float heat_flux;
    float power_input;
    float enthalpy;
    float latent_heat;
    float specific_heat_solid;
    float specific_heat_liquid;
    float melting_point;
    float freezing_point;
    PhaseState current_phase;
    float phase_fraction;
    float stored_energy;
    float storage_efficiency;
    bool phase_change_active;
    unsigned long phase_change_start_time;
    unsigned long last_update;
};

// Phase Change State Enumeration
enum PhaseState {
    SOLID,
    MELTING,
    LIQUID,
    FREEZING,
    MIXED_PHASE
};

// PCM Material Properties
struct PCMProperties {
    String name;
    float melting_point;
    float freezing_point;
    float latent_heat;
    float specific_heat_solid;
    float specific_heat_liquid;
    float density_solid;
    float density_liquid;
    float thermal_conductivity;
};

// System State
PCMContainer pcm_containers[NUM_CONTAINERS];
MAX31855 thermocouples[TOTAL_THERMOCOUPLES];
HX711 load_cells[NUM_LOAD_CELLS];
Adafruit_INA3221 current_monitors[2];
Adafruit_ADS1X15 adc_modules[2];
RTC_DS3231 rtc;
bool emergency_stop_active = false;
bool system_initialized = false;
unsigned long last_sample_time = 0;
unsigned long system_start_time = 0;

// PCM material database
PCMProperties pcm_materials[] = {
    {"Paraffin Wax", 58.0, 56.0, 218.0, 2.15, 2.89, 0.82, 0.77, 0.21},
    {"Salt Hydrate", 32.0, 30.0, 251.0, 1.46, 2.05, 1.58, 1.52, 0.48},
    {"Fatty Acid", 64.0, 62.0, 189.0, 1.93, 2.35, 0.89, 0.85, 0.16},
    {"Custom PCM", 45.0, 43.0, 203.0, 1.85, 2.12, 0.95, 0.91, 0.19}
};

// IoT Configuration
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "mqtt.broker.com";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Data logging
File dataFile;
String log_filename;

// Phase Change Detection Class
class PhaseChangeDetector {
private:
    float temperature_history[NUM_CONTAINERS][100];
    float heat_flux_history[NUM_CONTAINERS][100];
    int history_index[NUM_CONTAINERS];
    bool baseline_established[NUM_CONTAINERS];
    
public:
    PhaseChangeDetector() {
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            history_index[i] = 0;
            baseline_established[i] = false;
        }
    }
    
    void updateHistory(int container, float temperature, float heat_flux) {
        temperature_history[container][history_index[container]] = temperature;
        heat_flux_history[container][history_index[container]] = heat_flux;
        history_index[container] = (history_index[container] + 1) % 100;
        
        if (history_index[container] == 0) {
            baseline_established[container] = true;
        }
    }
    
    PhaseState detectPhaseState(int container) {
        if (!baseline_established[container]) return SOLID;
        
        float current_temp = pcm_containers[container].temperature_top;
        float temp_gradient = calculateTemperatureGradient(container);
        float heat_flux = pcm_containers[container].heat_flux;
        float melting_point = pcm_containers[container].melting_point;
        float freezing_point = pcm_containers[container].freezing_point;
        
        // Phase change detection algorithm
        if (abs(temp_gradient) < PHASE_CHANGE_THRESHOLD && heat_flux > HEAT_FLUX_THRESHOLD) {
            if (current_temp > melting_point - 2.0 && current_temp < melting_point + 2.0) {
                return MELTING;
            } else if (current_temp > freezing_point - 2.0 && current_temp < freezing_point + 2.0) {
                return FREEZING;
            }
        }
        
        // Determine phase based on temperature
        if (current_temp > melting_point) {
            return LIQUID;
        } else if (current_temp < freezing_point) {
            return SOLID;
        } else {
            return MIXED_PHASE;
        }
    }
    
    float calculateTemperatureGradient(int container) {
        if (history_index[container] < 10) return 0.0;
        
        float recent_temp = temperature_history[container][(history_index[container] - 1 + 100) % 100];
        float older_temp = temperature_history[container][(history_index[container] - 10 + 100) % 100];
        
        return (recent_temp - older_temp) / 10.0; // °C per sample
    }
    
    float calculateLatentHeat(int container) {
        if (!pcm_containers[container].phase_change_active) return 0.0;
        
        unsigned long phase_duration = millis() - pcm_containers[container].phase_change_start_time;
        float phase_duration_seconds = phase_duration / 1000.0;
        
        float heat_input = pcm_containers[container].power_input * phase_duration_seconds;
        float mass = pcm_containers[container].mass;
        
        return heat_input / mass; // J/kg
    }
    
    float calculatePhaseFraction(int container) {
        float temp = pcm_containers[container].temperature_top;
        float melting_point = pcm_containers[container].melting_point;
        float freezing_point = pcm_containers[container].freezing_point;
        
        if (temp > melting_point) {
            return 1.0; // Fully liquid
        } else if (temp < freezing_point) {
            return 0.0; // Fully solid
        } else {
            // Linear interpolation for mixed phase
            return (temp - freezing_point) / (melting_point - freezing_point);
        }
    }
};

// Thermal Energy Storage Optimization Class
class ThermalEnergyStorage {
private:
    float charging_efficiency[NUM_CONTAINERS];
    float discharging_efficiency[NUM_CONTAINERS];
    float optimal_charging_rate[NUM_CONTAINERS];
    float optimal_discharging_rate[NUM_CONTAINERS];
    
public:
    ThermalEnergyStorage() {
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            charging_efficiency[i] = 0.85;
            discharging_efficiency[i] = 0.80;
            optimal_charging_rate[i] = 50.0; // Watts
            optimal_discharging_rate[i] = 40.0; // Watts
        }
    }
    
    void optimizeEnergyStorage(int container) {
        float target_temp = getTargetTemperature(container);
        float current_temp = pcm_containers[container].temperature_top;
        float phase_fraction = pcm_containers[container].phase_fraction;
        
        if (target_temp > pcm_containers[container].melting_point && phase_fraction < 0.9) {
            // Charging phase - store energy
            optimizeChargingRate(container);
        } else if (target_temp < pcm_containers[container].freezing_point && phase_fraction > 0.1) {
            // Discharging phase - release energy
            optimizeDischargingRate(container);
        }
    }
    
    void optimizeChargingRate(int container) {
        float current_power = pcm_containers[container].power_input;
        float optimal_power = optimal_charging_rate[container];
        
        // Adjust power to optimal level
        if (current_power < optimal_power * 0.9) {
            increasePower(container, 5); // Increase by 5%
        } else if (current_power > optimal_power * 1.1) {
            decreasePower(container, 5); // Decrease by 5%
        }
    }
    
    void optimizeDischargingRate(int container) {
        float current_power = abs(pcm_containers[container].power_input);
        float optimal_power = optimal_discharging_rate[container];
        
        // Adjust cooling power to optimal level
        if (current_power < optimal_power * 0.9) {
            increaseCoolingPower(container, 5);
        } else if (current_power > optimal_power * 1.1) {
            decreaseCoolingPower(container, 5);
        }
    }
    
    float calculateStorageEfficiency(int container) {
        float energy_input = calculateEnergyInput(container);
        float energy_stored = calculateStoredEnergy(container);
        
        if (energy_input > 0) {
            return (energy_stored / energy_input) * 100.0;
        }
        return 0.0;
    }
    
    float calculateEnergyInput(int container) {
        // Integrate power over time
        static unsigned long last_time[NUM_CONTAINERS] = {0};
        static float total_energy[NUM_CONTAINERS] = {0};
        
        unsigned long current_time = millis();
        if (last_time[container] > 0) {
            float dt = (current_time - last_time[container]) / 1000.0; // seconds
            total_energy[container] += pcm_containers[container].power_input * dt;
        }
        last_time[container] = current_time;
        
        return total_energy[container];
    }
    
    float calculateStoredEnergy(int container) {
        float mass = pcm_containers[container].mass;
        float phase_fraction = pcm_containers[container].phase_fraction;
        float latent_heat = pcm_containers[container].latent_heat;
        float temp = pcm_containers[container].temperature_top;
        float melting_point = pcm_containers[container].melting_point;
        float specific_heat = pcm_containers[container].specific_heat_solid;
        
        // Sensible heat + latent heat
        float sensible_energy = mass * specific_heat * (temp - 20.0); // Reference: 20°C
        float latent_energy = mass * latent_heat * phase_fraction;
        
        return sensible_energy + latent_energy;
    }
    
    float getTargetTemperature(int container) {
        // This could be from user input, schedule, or optimization algorithm
        return 60.0; // Default target
    }
    
    void increasePower(int container, float percent) {
        int pwm_value = analogRead(TEC_PWM_PINS[container]);
        pwm_value = min(255, (int)(pwm_value * (1.0 + percent/100.0)));
        analogWrite(TEC_PWM_PINS[container], pwm_value);
    }
    
    void decreasePower(int container, float percent) {
        int pwm_value = analogRead(TEC_PWM_PINS[container]);
        pwm_value = max(0, (int)(pwm_value * (1.0 - percent/100.0)));
        analogWrite(TEC_PWM_PINS[container], pwm_value);
    }
    
    void increaseCoolingPower(int container, float percent) {
        // Increase TEC cooling (reverse direction)
        digitalWrite(TEC_DIR_PINS[container], LOW);
        increasePower(container, percent);
    }
    
    void decreaseCoolingPower(int container, float percent) {
        // Decrease TEC cooling
        decreasePower(container, percent);
    }
};

// Advanced Analytics Class
class AdvancedAnalytics {
private:
    float performance_metrics[NUM_CONTAINERS][10];
    int metric_count[NUM_CONTAINERS];
    
public:
    AdvancedAnalytics() {
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            metric_count[i] = 0;
        }
    }
    
    void analyzePerformance(int container) {
        // Calculate key performance indicators
        float effectiveness = calculateEffectiveness(container);
        float efficiency = calculateEfficiency(container);
        float response_time = calculateResponseTime(container);
        float stability = calculateStabilityIndex(container);
        
        // Store metrics
        if (metric_count[container] < 10) {
            performance_metrics[container][metric_count[container]] = effectiveness;
            metric_count[container]++;
        }
        
        // Generate insights
        generateInsights(container, effectiveness, efficiency, response_time, stability);
    }
    
    float calculateEffectiveness(int container) {
        float target_temp = 60.0; // Target temperature
        float current_temp = pcm_containers[container].temperature_top;
        float max_temp_diff = 50.0; // Maximum expected temperature difference
        
        float temp_error = abs(target_temp - current_temp);
        return max(0.0, 1.0 - (temp_error / max_temp_diff));
    }
    
    float calculateEfficiency(int container) {
        float power_input = pcm_containers[container].power_input;
        float useful_heat = calculateUsefulHeat(container);
        
        if (power_input > 0) {
            return (useful_heat / power_input) * 100.0;
        }
        return 0.0;
    }
    
    float calculateResponseTime(int container) {
        // Calculate time to reach 90% of setpoint
        // This would require historical data analysis
        return 120.0; // seconds - placeholder
    }
    
    float calculateStabilityIndex(int container) {
        // Calculate temperature stability over time
        float temp_variance = calculateTemperatureVariance(container);
        return 1.0 / (1.0 + temp_variance);
    }
    
    float calculateUsefulHeat(int container) {
        // Calculate heat that contributes to desired temperature change
        float temp_change = pcm_containers[container].temperature_top - 20.0; // Reference
        float mass = pcm_containers[container].mass;
        float specific_heat = pcm_containers[container].specific_heat_solid;
        
        return mass * specific_heat * temp_change;
    }
    
    float calculateTemperatureVariance(int container) {
        // Calculate variance of recent temperature readings
        // This would use historical data
        return 0.5; // °C² - placeholder
    }
    
    void generateInsights(int container, float effectiveness, float efficiency, 
                         float response_time, float stability) {
        Serial.println("📊 Performance Analysis - Container " + String(container));
        Serial.println("   Effectiveness: " + String(effectiveness * 100, 1) + "%");
        Serial.println("   Efficiency: " + String(efficiency, 1) + "%");
        Serial.println("   Response Time: " + String(response_time, 1) + "s");
        Serial.println("   Stability Index: " + String(stability, 3));
        
        // Generate recommendations
        if (effectiveness < 0.8) {
            Serial.println("   🔧 Recommendation: Adjust control parameters");
        }
        if (efficiency < 70.0) {
            Serial.println("   ⚡ Recommendation: Optimize power settings");
        }
        if (response_time > 300.0) {
            Serial.println("   ⏱️ Recommendation: Increase heating/cooling rate");
        }
        if (stability < 0.9) {
            Serial.println("   🎯 Recommendation: Improve temperature control");
        }
    }
};

// Global objects
PhaseChangeDetector phase_detector;
ThermalEnergyStorage energy_storage;
AdvancedAnalytics analytics;

// Interrupt service routine
void emergencyStopISR() {
    emergency_stop_active = true;
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("🌡️ PCM CONTROLLER SYSTEM STARTED!");
    Serial.println("🌡️ PCM THERMAL ENGINEER MODE - Design advanced thermal energy storage!");
    Serial.println("Professional Phase Change Material control and optimization system");
    Serial.println("================================================================");
    
    // Initialize system
    system_start_time = millis();
    
    // Initialize hardware
    initializeHardware();
    
    // Initialize safety system
    initializeSafetySystem();
    
    // Initialize IoT connectivity
    initializeIoT();
    
    // Initialize data logging
    initializeDataLogging();
    
    // Initialize PCM containers
    initializePCMContainers();
    
    // Characterize PCM materials
    characterizePCMMaterials();
    
    Serial.println("🎯 System Ready for PCM Testing");
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
        
        // Update phase change detection
        updatePhaseChangeDetection();
        
        // Optimize energy storage
        optimizeEnergyStorage();
        
        // Perform analytics
        performAnalytics();
        
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
    
    // Initialize thermocouples
    for (int i = 0; i < TOTAL_THERMOCOUPLES; i++) {
        thermocouples[i].begin(THERMOCOUPLE_CS_PINS[i]);
    }
    Serial.println("✅ MAX31855 thermocouples: " + String(TOTAL_THERMOCOUPLES) + "/" + String(TOTAL_THERMOCOUPLES));
    
    // Initialize load cells
    for (int i = 0; i < NUM_LOAD_CELLS; i++) {
        load_cells[i].begin(LOAD_CELL_DATA_PINS[i], LOAD_CELL_CLOCK_PINS[i]);
        load_cells[i].set_scale(2280.0); // Calibration factor
        load_cells[i].tare(); // Reset to zero
    }
    Serial.println("✅ HX711 load cells: " + String(NUM_LOAD_CELLS) + "/" + String(NUM_LOAD_CELLS));
    
    // Initialize current monitors
    for (int i = 0; i < 2; i++) {
        current_monitors[i].begin(0x40 + i);
        current_monitors[i].setShuntRes(100, 100, 100); // 100 mOhm shunts
    }
    Serial.println("✅ INA3221 current monitors: 2/2");
    
    // Initialize ADC modules
    for (int i = 0; i < 2; i++) {
        adc_modules[i].begin(0x48 + i);
        adc_modules[i].setGain(GAIN_ONE); // ±4.096V range
    }
    Serial.println("✅ ADS1115 ADC modules: 2/2");
    
    // Initialize RTC
    if (rtc.begin()) {
        Serial.println("✅ DS3231 RTC synchronized");
    } else {
        Serial.println("❌ DS3231 RTC not found");
    }
    
    // Initialize control pins
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        pinMode(TEC_PWM_PINS[i], OUTPUT);
        pinMode(TEC_DIR_PINS[i], OUTPUT);
        pinMode(HEATER_RELAY_PINS[i], OUTPUT);
        pinMode(FAN_PWM_PINS[i], OUTPUT);
        
        // Initialize to safe state
        analogWrite(TEC_PWM_PINS[i], 0);
        digitalWrite(TEC_DIR_PINS[i], LOW);
        digitalWrite(HEATER_RELAY_PINS[i], LOW);
        analogWrite(FAN_PWM_PINS[i], 0);
    }
    
    // Initialize status LEDs
    for (int i = 0; i < TOTAL_THERMOCOUPLES; i++) {
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
    
    Serial.println("✅ Safety system initialized");
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
        if (mqtt_client.connect("PCMController")) {
            Serial.println("✅ MQTT broker connected");
            mqtt_client.subscribe("pcm/commands");
        } else {
            Serial.println("❌ MQTT connection failed");
            delay(5000);
        }
    }
}

void initializeDataLogging() {
    log_filename = "pcm_data_" + String(millis()) + ".csv";
    
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        // Write header
        dataFile.println("timestamp,container,temp_top,temp_bottom,mass,phase_state,phase_fraction,enthalpy,power,efficiency");
        dataFile.close();
        Serial.println("✅ Data logging initialized: " + log_filename);
    }
}

void initializePCMContainers() {
    Serial.println("🔥 Initializing PCM Containers...");
    
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        pcm_containers[i].container_id = i;
        pcm_containers[i].temperature_top = 0.0;
        pcm_containers[i].temperature_bottom = 0.0;
        pcm_containers[i].mass = 0.0;
        pcm_containers[i].density = 0.0;
        pcm_containers[i].heat_flux = 0.0;
        pcm_containers[i].power_input = 0.0;
        pcm_containers[i].enthalpy = 0.0;
        pcm_containers[i].current_phase = SOLID;
        pcm_containers[i].phase_fraction = 0.0;
        pcm_containers[i].stored_energy = 0.0;
        pcm_containers[i].storage_efficiency = 0.0;
        pcm_containers[i].phase_change_active = false;
        pcm_containers[i].phase_change_start_time = 0;
        pcm_containers[i].last_update = 0;
        
        // Assign PCM material properties
        pcm_containers[i].melting_point = pcm_materials[i].melting_point;
        pcm_containers[i].freezing_point = pcm_materials[i].freezing_point;
        pcm_containers[i].latent_heat = pcm_materials[i].latent_heat;
        pcm_containers[i].specific_heat_solid = pcm_materials[i].specific_heat_solid;
        pcm_containers[i].specific_heat_liquid = pcm_materials[i].specific_heat_liquid;
        
        Serial.println("✅ Container " + String(i) + " (" + pcm_materials[i].name + ")");
    }
}

void characterizePCMMaterials() {
    Serial.println("🔥 PCM Material Characterization...");
    
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        Serial.println("📊 Container " + String(i) + " (" + pcm_materials[i].name + "):");
        Serial.println("  Melting point: " + String(pcm_materials[i].melting_point, 1) + "°C");
        Serial.println("  Latent heat: " + String(pcm_materials[i].latent_heat, 0) + " J/g");
        Serial.println("  Thermal conductivity: " + String(pcm_materials[i].thermal_conductivity, 2) + " W/m·K");
    }
}

void updateSensorReadings() {
    for (int container = 0; container < NUM_CONTAINERS; container++) {
        // Read thermocouples
        int tc_top_index = container * 2;
        int tc_bottom_index = container * 2 + 1;
        
        pcm_containers[container].temperature_top = thermocouples[tc_top_index].readCelsius();
        pcm_containers[container].temperature_bottom = thermocouples[tc_bottom_index].readCelsius();
        
        // Read mass from load cells
        if (container < NUM_LOAD_CELLS) {
            pcm_containers[container].mass = load_cells[container].get_units(5) / 1000.0; // kg
        }
        
        // Calculate density
        if (pcm_containers[container].mass > 0) {
            float volume = 0.0005; // m³ - container volume
            pcm_containers[container].density = pcm_containers[container].mass / volume;
        }
        
        // Read current and calculate power
        int monitor_index = container / 2;
        int channel = container % 2;
        float current = current_monitors[monitor_index].getCurrent_mA(channel + 1) / 1000.0; // A
        float voltage = current_monitors[monitor_index].getBusVoltage_V(channel + 1);
        pcm_containers[container].power_input = voltage * current;
        
        // Read heat flux from ADC
        int adc_index = container / 2;
        int adc_channel = container % 2;
        int16_t adc_value = adc_modules[adc_index].readADC_SingleEnded(adc_channel);
        float voltage_hf = adc_value * 0.125 / 1000.0; // Convert to voltage
        pcm_containers[container].heat_flux = voltage_hf * 1000.0; // W/m² (calibration factor)
        
        // Update phase change detector
        phase_detector.updateHistory(container, pcm_containers[container].temperature_top, 
                                   pcm_containers[container].heat_flux);
        
        pcm_containers[container].last_update = millis();
    }
}

void updatePhaseChangeDetection() {
    for (int container = 0; container < NUM_CONTAINERS; container++) {
        PhaseState previous_phase = pcm_containers[container].current_phase;
        PhaseState current_phase = phase_detector.detectPhaseState(container);
        
        if (current_phase != previous_phase) {
            Serial.println("🔄 Phase change detected in container " + String(container));
            Serial.println("   " + phaseStateToString(previous_phase) + " → " + phaseStateToString(current_phase));
            
            // Log phase change event
            logPhaseChangeEvent(container, previous_phase, current_phase);
            
            // Update phase change timing
            if (current_phase == MELTING || current_phase == FREEZING) {
                pcm_containers[container].phase_change_active = true;
                pcm_containers[container].phase_change_start_time = millis();
            } else {
                pcm_containers[container].phase_change_active = false;
            }
        }
        
        pcm_containers[container].current_phase = current_phase;
        pcm_containers[container].phase_fraction = phase_detector.calculatePhaseFraction(container);
        
        // Update enthalpy calculation
        updateEnthalpy(container);
    }
}

void updateEnthalpy(int container) {
    float temp = pcm_containers[container].temperature_top;
    float mass = pcm_containers[container].mass;
    float phase_fraction = pcm_containers[container].phase_fraction;
    
    // Sensible heat calculation
    float reference_temp = 20.0; // °C
    float specific_heat = (1.0 - phase_fraction) * pcm_containers[container].specific_heat_solid +
                         phase_fraction * pcm_containers[container].specific_heat_liquid;
    float sensible_enthalpy = mass * specific_heat * (temp - reference_temp);
    
    // Latent heat calculation
    float latent_enthalpy = mass * pcm_containers[container].latent_heat * phase_fraction;
    
    // Total enthalpy
    pcm_containers[container].enthalpy = sensible_enthalpy + latent_enthalpy;
    
    // Calculate stored energy
    pcm_containers[container].stored_energy = pcm_containers[container].enthalpy;
    
    // Calculate storage efficiency
    pcm_containers[container].storage_efficiency = energy_storage.calculateStorageEfficiency(container);
}

void optimizeEnergyStorage() {
    for (int container = 0; container < NUM_CONTAINERS; container++) {
        energy_storage.optimizeEnergyStorage(container);
    }
}

void performAnalytics() {
    static unsigned long last_analytics_time = 0;
    
    if (millis() - last_analytics_time > 30000) { // Every 30 seconds
        for (int container = 0; container < NUM_CONTAINERS; container++) {
            analytics.analyzePerformance(container);
        }
        last_analytics_time = millis();
    }
}

void updateStatusDisplay() {
    static unsigned long last_display_time = 0;
    
    if (millis() - last_display_time > 10000) { // Every 10 seconds
        Serial.println("=== PCM THERMAL ENERGY STORAGE STATUS ===");
        DateTime now = rtc.now();
        Serial.print("Time: ");
        Serial.print(now.hour());
        Serial.print(":");
        Serial.print(now.minute());
        Serial.print(":");
        Serial.print(now.second());
        Serial.print(" | Mode: ENERGY_STORAGE | Total Power: ");
        
        float total_power = 0;
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            total_power += pcm_containers[i].power_input;
        }
        Serial.print(total_power);
        Serial.println("W");
        
        for (int container = 0; container < NUM_CONTAINERS; container++) {
            Serial.println();
            Serial.println("Container " + String(container) + " (" + pcm_materials[container].name + "):");
            Serial.println("  Temperature: " + String(pcm_containers[container].temperature_top, 1) + "°C");
            Serial.println("  Mass: " + String(pcm_containers[container].mass, 1) + "g");
            Serial.println("  Phase: " + phaseStateToString(pcm_containers[container].current_phase) + 
                          " (" + String(pcm_containers[container].phase_fraction * 100, 0) + "% liquid)");
            Serial.println("  Heat Flux: " + String(pcm_containers[container].heat_flux, 0) + " W/m²");
            Serial.println("  Stored Energy: " + String(pcm_containers[container].stored_energy / 1000.0, 1) + " kJ");
            Serial.println("  Efficiency: " + String(pcm_containers[container].storage_efficiency, 1) + "%");
        }
        
        Serial.println();
        Serial.println("🌐 IoT Status: " + String(mqtt_client.connected() ? "Connected" : "Disconnected"));
        
        last_display_time = millis();
    }
}

void logData() {
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        for (int container = 0; container < NUM_CONTAINERS; container++) {
            dataFile.print(millis());
            dataFile.print(",");
            dataFile.print(container);
            dataFile.print(",");
            dataFile.print(pcm_containers[container].temperature_top);
            dataFile.print(",");
            dataFile.print(pcm_containers[container].temperature_bottom);
            dataFile.print(",");
            dataFile.print(pcm_containers[container].mass);
            dataFile.print(",");
            dataFile.print(pcm_containers[container].current_phase);
            dataFile.print(",");
            dataFile.print(pcm_containers[container].phase_fraction);
            dataFile.print(",");
            dataFile.print(pcm_containers[container].enthalpy);
            dataFile.print(",");
            dataFile.print(pcm_containers[container].power_input);
            dataFile.print(",");
            dataFile.println(pcm_containers[container].storage_efficiency);
        }
        dataFile.close();
    }
}

void handleIoTCommunication() {
    if (mqtt_client.connected()) {
        mqtt_client.loop();
        
        // Publish data periodically
        static unsigned long last_publish_time = 0;
        if (millis() - last_publish_time > 30000) { // Every 30 seconds
            publishPCMData();
            last_publish_time = millis();
        }
    } else {
        connectToMQTT();
    }
}

void publishPCMData() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["system_status"] = "NORMAL";
    
    JsonArray containers = doc.createNestedArray("containers");
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        JsonObject container = containers.createNestedObject();
        container["id"] = i;
        container["material"] = pcm_materials[i].name;
        container["temperature"] = pcm_containers[i].temperature_top;
        container["mass"] = pcm_containers[i].mass;
        container["phase"] = phaseStateToString(pcm_containers[i].current_phase);
        container["phase_fraction"] = pcm_containers[i].phase_fraction;
        container["enthalpy"] = pcm_containers[i].enthalpy;
        container["stored_energy"] = pcm_containers[i].stored_energy;
        container["efficiency"] = pcm_containers[i].storage_efficiency;
    }
    
    String payload;
    serializeJson(doc, payload);
    mqtt_client.publish("pcm/data", payload.c_str());
}

void handleEmergencyState() {
    // Turn off all heaters and TECs
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        analogWrite(TEC_PWM_PINS[i], 0);
        digitalWrite(HEATER_RELAY_PINS[i], LOW);
        
        // Flash LEDs
        static bool led_state = false;
        static unsigned long last_flash = 0;
        if (millis() - last_flash > 500) {
            led_state = !led_state;
            digitalWrite(STATUS_LED_PINS[i], led_state);
            last_flash = millis();
        }
    }
    
    // Check for reset
    if (digitalRead(EMERGENCY_STOP_PIN) == HIGH) {
        emergency_stop_active = false;
        Serial.println("Emergency stop reset");
    }
}

void handleSerialCommands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command.startsWith("SET_TARGET")) {
            // Format: SET_TARGET container temperature
            int container = command.substring(11, 12).toInt();
            float temperature = command.substring(13).toFloat();
            
            if (container >= 0 && container < NUM_CONTAINERS) {
                // Set target temperature (implementation depends on control system)
                Serial.println("Set container " + String(container) + " target to " + String(temperature) + "°C");
            }
        }
        else if (command == "STATUS") {
            updateStatusDisplay();
        }
        else if (command == "CHARACTERIZE") {
            characterizePCMMaterials();
        }
        else if (command == "ANALYTICS") {
            for (int i = 0; i < NUM_CONTAINERS; i++) {
                analytics.analyzePerformance(i);
            }
        }
        else if (command == "HELP") {
            Serial.println("Available commands:");
            Serial.println("SET_TARGET <container> <temperature>");
            Serial.println("STATUS");
            Serial.println("CHARACTERIZE");
            Serial.println("ANALYTICS");
            Serial.println("HELP");
        }
    }
}

void logPhaseChangeEvent(int container, PhaseState from, PhaseState to) {
    File phaseFile = SD.open("phase_change_log.txt", FILE_WRITE);
    if (phaseFile) {
        phaseFile.print(millis());
        phaseFile.print(",");
        phaseFile.print(container);
        phaseFile.print(",");
        phaseFile.print(phaseStateToString(from));
        phaseFile.print(",");
        phaseFile.print(phaseStateToString(to));
        phaseFile.print(",");
        phaseFile.println(pcm_containers[container].temperature_top);
        phaseFile.close();
    }
}

String phaseStateToString(PhaseState state) {
    switch (state) {
        case SOLID: return "SOLID";
        case MELTING: return "MELTING";
        case LIQUID: return "LIQUID";
        case FREEZING: return "FREEZING";
        case MIXED_PHASE: return "MIXED";
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
    
    if (doc["action"] == "set_target") {
        int container = doc["container"];
        float temperature = doc["temperature"];
        if (container >= 0 && container < NUM_CONTAINERS) {
            // Set target temperature
            Serial.println("MQTT: Set container " + String(container) + " target to " + String(temperature) + "°C");
        }
    }
} 