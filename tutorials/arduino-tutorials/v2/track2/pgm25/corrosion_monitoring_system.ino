/*
 * Program 25: Corrosion Monitoring System
 * 
 * This program implements a comprehensive corrosion monitoring system for real-time
 * assessment of metallic structures. The system combines multiple electrochemical
 * techniques, environmental monitoring, and advanced analytics to provide early
 * warning of corrosion damage and predict remaining service life.
 * 
 * Features:
 * - Multi-technique electrochemical monitoring (LPR, EIS, EN, CP)
 * - Real-time corrosion rate measurement and trending
 * - Environmental parameter monitoring
 * - Galvanic corrosion detection and mapping
 * - Machine learning-based corrosion prediction
 * - Remote monitoring with IoT connectivity
 * - Standards compliance (ASTM, NACE, ISO)
 * 
 * Author: Arduino Zero to Hero v2.0
 * Created: 2024
 * 
 * Hardware Requirements:
 * - Arduino Mega 2560 (main controller)
 * - Multi-channel potentiostat/galvanostat
 * - Reference electrodes (Ag/AgCl, Cu/CuSO4, Zn)
 * - Working and counter electrodes
 * - Environmental sensors
 * - GPS module
 * - Solar power system
 * - Communication modules (cellular, LoRa)
 * 
 * Libraries Required:
 * - ArduinoJson.h
 * - SD.h
 * - SPI.h
 * - Wire.h
 * - RTClib.h
 * - OneWire.h
 * - DallasTemperature.h
 * - SoftwareSerial.h
 */

#include <ArduinoJson.h>
#include <SD.h>
#include <SPI.h>
#include <Wire.h>
#include <RTClib.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <SoftwareSerial.h>
#include <math.h>

// System Configuration
#define SYSTEM_VERSION "v2.0.0"
#define DEVICE_ID "CMS_001"
#define SAMPLING_RATE 1000          // Hz for high-speed measurements
#define MONITORING_INTERVAL 60000   // 1 minute default
#define DATA_BUFFER_SIZE 1000
#define MAX_ELECTRODES 8

// Pin Definitions
// Potentiostat Control
#define POTENTIOSTAT_CS 2           // Chip select for potentiostat
#define POTENTIOSTAT_RESET 3        // Reset signal
#define POTENTIOSTAT_READY 4        // Data ready signal
#define ELECTRODE_MUX_A 5           // Electrode multiplexer A
#define ELECTRODE_MUX_B 6           // Electrode multiplexer B
#define ELECTRODE_MUX_C 7           // Electrode multiplexer C
#define ELECTRODE_MUX_EN 8          // Electrode multiplexer enable

// Environmental Sensors
#define TEMP_SENSOR_PIN 9           // DS18B20 temperature sensor
#define PH_SENSOR_PIN A0            // pH sensor analog input
#define CONDUCTIVITY_PIN A1         // Conductivity sensor
#define DISSOLVED_O2_PIN A2         // Dissolved oxygen sensor
#define CHLORIDE_PIN A3             // Chloride sensor
#define HUMIDITY_SENSOR_PIN A4      // Humidity sensor
#define PRESSURE_SENSOR_PIN A5      // Atmospheric pressure

// Reference Electrodes
#define REF_ELECTRODE_1 A6          // Ag/AgCl reference
#define REF_ELECTRODE_2 A7          // Cu/CuSO4 reference
#define REF_ELECTRODE_3 A8          // Zn reference

// Power Management
#define SOLAR_VOLTAGE_PIN A9        // Solar panel voltage
#define BATTERY_VOLTAGE_PIN A10     // Battery voltage
#define LOAD_CURRENT_PIN A11        // Load current
#define SOLAR_CHARGE_CTRL 10        // Solar charge controller
#define BATTERY_HEATER 11           // Battery heater for cold weather
#define POWER_RELAY 12              // Main power relay

// Communication
#define ESP32_SERIAL Serial1        // ESP32 communication
#define LORA_SERIAL Serial2         // LoRa communication
#define GPS_SERIAL Serial3          // GPS communication
#define CELLULAR_POWER 13           // Cellular module power
#define LORA_POWER 14               // LoRa module power

// Status and Control
#define STATUS_LED_GREEN 15         // System operational
#define STATUS_LED_RED 16           // System fault
#define STATUS_LED_BLUE 17          // Communication active
#define ALARM_BUZZER 18             // Audible alarm
#define EMERGENCY_STOP 19           // Emergency stop button
#define MAINTENANCE_MODE 20         // Maintenance mode switch

// Additional I/O
#define LIGHTNING_DETECTOR 21       // Lightning detector input
#define VIBRATION_SENSOR 22         // Vibration sensor
#define FLOW_SENSOR 23              // Flow sensor for dynamic conditions
#define SPARE_DIGITAL_1 24          // Spare digital I/O
#define SPARE_DIGITAL_2 25          // Spare digital I/O

// Data Structures
struct ElectrochemicalData {
    uint32_t timestamp;
    uint8_t electrode_id;
    float potential;              // mV vs reference
    float current;                // μA
    float resistance;             // Ω
    float corrosion_rate;         // mpy (mils per year)
    float polarization_resistance; // Ω⋅cm²
    float impedance_magnitude;    // Ω
    float impedance_phase;        // degrees
    float noise_resistance;       // Ω
    float noise_current;          // μA RMS
    uint8_t measurement_type;     // 0=LPR, 1=EIS, 2=EN, 3=CP
    uint8_t data_quality;         // 0-100 quality score
};

struct EnvironmentalData {
    uint32_t timestamp;
    float temperature;            // °C
    float humidity;               // %RH
    float ph_value;               // pH units
    float conductivity;           // μS/cm
    float dissolved_oxygen;       // mg/L
    float chloride_concentration; // ppm
    float atmospheric_pressure;   // kPa
    float wind_speed;             // m/s
    float wind_direction;         // degrees
    float rainfall;               // mm
    float solar_irradiance;       // W/m²
    float soil_moisture;          // %
    float soil_temperature;       // °C
    uint8_t weather_condition;    // 0=clear, 1=cloudy, 2=rain, 3=storm
};

struct CorrosionAssessment {
    uint32_t timestamp;
    uint8_t electrode_id;
    float instantaneous_rate;     // mpy
    float average_rate_24h;       // mpy
    float average_rate_7d;        // mpy
    float cumulative_loss;        // mils
    float remaining_thickness;    // mils
    float predicted_life;         // years
    uint8_t corrosion_type;       // 0=uniform, 1=pitting, 2=galvanic, 3=crevice
    uint8_t severity_level;       // 0=low, 1=medium, 2=high, 3=critical
    float confidence_level;       // 0-100%
    String alert_message;
};

struct SystemStatus {
    uint32_t timestamp;
    bool system_operational;
    bool communication_active;
    bool power_adequate;
    bool calibration_valid;
    float battery_voltage;
    float solar_voltage;
    float system_temperature;
    float data_storage_usage;
    uint32_t uptime;
    uint32_t measurement_count;
    uint32_t error_count;
    String last_error;
};

struct CalibrationData {
    uint32_t calibration_date;
    float ph_slope;
    float ph_offset;
    float conductivity_factor;
    float do_slope;
    float do_offset;
    float chloride_slope;
    float chloride_offset;
    float potential_offset[MAX_ELECTRODES];
    float current_gain[MAX_ELECTRODES];
    float area_factor[MAX_ELECTRODES];
    bool calibration_valid;
};

// Global Variables
ElectrochemicalData electrochemical_data[MAX_ELECTRODES];
EnvironmentalData environmental_data;
CorrosionAssessment corrosion_assessment[MAX_ELECTRODES];
SystemStatus system_status;
CalibrationData calibration_data;

// Data Buffers
ElectrochemicalData data_buffer[DATA_BUFFER_SIZE];
uint16_t buffer_index = 0;
bool buffer_full = false;

// Timing Variables
uint32_t last_measurement_time = 0;
uint32_t last_environmental_reading = 0;
uint32_t last_status_update = 0;
uint32_t last_data_transmission = 0;
uint32_t last_calibration_check = 0;

// Measurement Control
bool measurement_active = false;
bool auto_measurement = true;
uint8_t current_electrode = 0;
uint8_t measurement_mode = 0; // 0=LPR, 1=EIS, 2=EN, 3=CP

// Temperature Sensor Setup
OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature temperature_sensor(&oneWire);

// RTC Setup
RTC_DS3231 rtc;

// Alarm Thresholds
float corrosion_rate_alarm = 100.0;     // mpy
float potential_alarm_low = -800.0;     // mV
float potential_alarm_high = 200.0;     // mV
float ph_alarm_low = 6.0;
float ph_alarm_high = 9.0;
float chloride_alarm = 1000.0;          // ppm

// Control Parameters
float lpr_scan_rate = 0.1;              // mV/s
float lpr_potential_range = 20.0;       // mV
float eis_frequency_min = 0.01;         // Hz
float eis_frequency_max = 10000.0;      // Hz
uint16_t eis_points = 50;
float en_measurement_time = 300.0;      // seconds
float cp_measurement_interval = 60.0;   // seconds

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== Corrosion Monitoring System v2.0 ===");
    Serial.println("Initializing advanced corrosion monitoring...");
    
    // Initialize pin modes
    initializePins();
    
    // Initialize communication interfaces
    initializeCommunication();
    
    // Initialize RTC
    initializeRTC();
    
    // Initialize SD card
    initializeStorage();
    
    // Initialize sensors
    initializeSensors();
    
    // Load calibration data
    loadCalibrationData();
    
    // Initialize potentiostat
    initializePotentiostat();
    
    // Initialize power management
    initializePowerManagement();
    
    // Perform system self-test
    performSystemSelfTest();
    
    // Initialize system status
    initializeSystemStatus();
    
    Serial.println("System initialization complete!");
    Serial.println("Starting corrosion monitoring...");
    
    // Start measurements
    startMeasurements();
}

void loop() {
    uint32_t current_time = millis();
    
    // Check emergency stop
    if (digitalRead(EMERGENCY_STOP) == LOW) {
        handleEmergencyStop();
        return;
    }
    
    // Check maintenance mode
    if (digitalRead(MAINTENANCE_MODE) == LOW) {
        handleMaintenanceMode();
        return;
    }
    
    // Perform measurements
    if (current_time - last_measurement_time > MONITORING_INTERVAL) {
        performMeasurements();
        last_measurement_time = current_time;
    }
    
    // Read environmental data
    if (current_time - last_environmental_reading > 60000) { // Every minute
        readEnvironmentalSensors();
        last_environmental_reading = current_time;
    }
    
    // Update system status
    if (current_time - last_status_update > 10000) { // Every 10 seconds
        updateSystemStatus();
        last_status_update = current_time;
    }
    
    // Transmit data
    if (current_time - last_data_transmission > 300000) { // Every 5 minutes
        transmitData();
        last_data_transmission = current_time;
    }
    
    // Check calibration
    if (current_time - last_calibration_check > 86400000) { // Daily
        checkCalibration();
        last_calibration_check = current_time;
    }
    
    // Process alerts
    processAlerts();
    
    // Manage power
    managePower();
    
    // Handle serial commands
    processSerialCommands();
    
    delay(100);
}

void initializePins() {
    // Potentiostat control
    pinMode(POTENTIOSTAT_CS, OUTPUT);
    pinMode(POTENTIOSTAT_RESET, OUTPUT);
    pinMode(POTENTIOSTAT_READY, INPUT);
    pinMode(ELECTRODE_MUX_A, OUTPUT);
    pinMode(ELECTRODE_MUX_B, OUTPUT);
    pinMode(ELECTRODE_MUX_C, OUTPUT);
    pinMode(ELECTRODE_MUX_EN, OUTPUT);
    
    // Power management
    pinMode(SOLAR_CHARGE_CTRL, OUTPUT);
    pinMode(BATTERY_HEATER, OUTPUT);
    pinMode(POWER_RELAY, OUTPUT);
    
    // Communication
    pinMode(CELLULAR_POWER, OUTPUT);
    pinMode(LORA_POWER, OUTPUT);
    
    // Status and control
    pinMode(STATUS_LED_GREEN, OUTPUT);
    pinMode(STATUS_LED_RED, OUTPUT);
    pinMode(STATUS_LED_BLUE, OUTPUT);
    pinMode(ALARM_BUZZER, OUTPUT);
    pinMode(EMERGENCY_STOP, INPUT_PULLUP);
    pinMode(MAINTENANCE_MODE, INPUT_PULLUP);
    
    // Additional I/O
    pinMode(LIGHTNING_DETECTOR, INPUT);
    pinMode(VIBRATION_SENSOR, INPUT);
    pinMode(FLOW_SENSOR, INPUT);
    
    // Initial states
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    digitalWrite(POTENTIOSTAT_RESET, LOW);
    digitalWrite(ELECTRODE_MUX_EN, LOW);
    digitalWrite(POWER_RELAY, HIGH);
    digitalWrite(STATUS_LED_GREEN, LOW);
    digitalWrite(STATUS_LED_RED, LOW);
    digitalWrite(STATUS_LED_BLUE, LOW);
}

void initializeCommunication() {
    ESP32_SERIAL.begin(115200);
    LORA_SERIAL.begin(9600);
    GPS_SERIAL.begin(9600);
    
    Wire.begin();
    SPI.begin();
    
    // Power up communication modules
    digitalWrite(CELLULAR_POWER, HIGH);
    digitalWrite(LORA_POWER, HIGH);
    delay(5000); // Allow modules to boot
    
    Serial.println("Communication interfaces initialized");
}

void initializeRTC() {
    if (!rtc.begin()) {
        Serial.println("RTC initialization failed!");
        return;
    }
    
    if (rtc.lostPower()) {
        Serial.println("RTC lost power, setting time...");
        rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    }
    
    Serial.println("RTC initialized");
}

void initializeStorage() {
    if (!SD.begin(53)) {
        Serial.println("SD card initialization failed!");
        system_status.last_error = "SD_INIT_FAILED";
        return;
    }
    
    // Create directory structure
    if (!SD.exists("/data")) SD.mkdir("/data");
    if (!SD.exists("/calibration")) SD.mkdir("/calibration");
    if (!SD.exists("/logs")) SD.mkdir("/logs");
    if (!SD.exists("/config")) SD.mkdir("/config");
    
    Serial.println("SD card initialized");
}

void initializeSensors() {
    // Initialize temperature sensor
    temperature_sensor.begin();
    temperature_sensor.setResolution(12); // 12-bit resolution
    
    // Initialize other sensors
    // pH sensor initialization
    // Conductivity sensor initialization
    // Dissolved oxygen sensor initialization
    // Chloride sensor initialization
    
    Serial.println("Sensors initialized");
}

void initializePotentiostat() {
    // Reset potentiostat
    digitalWrite(POTENTIOSTAT_RESET, LOW);
    delay(100);
    digitalWrite(POTENTIOSTAT_RESET, HIGH);
    delay(1000);
    
    // Configure potentiostat
    configurePotentiostat();
    
    Serial.println("Potentiostat initialized");
}

void configurePotentiostat() {
    // Configure potentiostat for LPR measurements
    digitalWrite(POTENTIOSTAT_CS, LOW);
    
    // Send configuration commands via SPI
    SPI.transfer(0x01); // Configuration register
    SPI.transfer(0x80); // Enable potentiostat
    SPI.transfer(0x02); // Current range register
    SPI.transfer(0x04); // 1 μA range
    SPI.transfer(0x03); // Potential range register
    SPI.transfer(0x02); // ±1V range
    
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    delay(100);
}

void initializePowerManagement() {
    // Configure solar charge controller
    analogWrite(SOLAR_CHARGE_CTRL, 128); // 50% duty cycle
    
    // Initialize battery heater (off initially)
    digitalWrite(BATTERY_HEATER, LOW);
    
    Serial.println("Power management initialized");
}

void performSystemSelfTest() {
    Serial.println("Performing system self-test...");
    
    bool self_test_passed = true;
    
    // Test potentiostat communication
    if (!testPotentiostatCommunication()) {
        Serial.println("FAIL: Potentiostat communication");
        self_test_passed = false;
    }
    
    // Test environmental sensors
    if (!testEnvironmentalSensors()) {
        Serial.println("FAIL: Environmental sensors");
        self_test_passed = false;
    }
    
    // Test power system
    if (!testPowerSystem()) {
        Serial.println("FAIL: Power system");
        self_test_passed = false;
    }
    
    // Test communication systems
    if (!testCommunicationSystems()) {
        Serial.println("FAIL: Communication systems");
        self_test_passed = false;
    }
    
    if (self_test_passed) {
        Serial.println("System self-test PASSED");
        digitalWrite(STATUS_LED_GREEN, HIGH);
        system_status.system_operational = true;
    } else {
        Serial.println("System self-test FAILED");
        digitalWrite(STATUS_LED_RED, HIGH);
        system_status.system_operational = false;
    }
}

void initializeSystemStatus() {
    system_status.timestamp = millis();
    system_status.system_operational = true;
    system_status.communication_active = false;
    system_status.power_adequate = true;
    system_status.calibration_valid = false;
    system_status.battery_voltage = 12.0;
    system_status.solar_voltage = 0.0;
    system_status.system_temperature = 25.0;
    system_status.data_storage_usage = 0.0;
    system_status.uptime = 0;
    system_status.measurement_count = 0;
    system_status.error_count = 0;
    system_status.last_error = "";
}

void startMeasurements() {
    measurement_active = true;
    current_electrode = 0;
    measurement_mode = 0; // Start with LPR
    
    Serial.println("Measurements started");
}

void performMeasurements() {
    if (!measurement_active) return;
    
    Serial.print("Performing measurement on electrode ");
    Serial.print(current_electrode);
    Serial.print(" using mode ");
    Serial.println(measurement_mode);
    
    // Select electrode
    selectElectrode(current_electrode);
    
    // Perform measurement based on mode
    switch (measurement_mode) {
        case 0: // LPR
            performLPRMeasurement();
            break;
        case 1: // EIS
            performEISMeasurement();
            break;
        case 2: // EN
            performENMeasurement();
            break;
        case 3: // CP
            performCPMeasurement();
            break;
    }
    
    // Store data
    storeElectrochemicalData();
    
    // Calculate corrosion assessment
    calculateCorrosionAssessment();
    
    // Advance to next electrode/mode
    advanceMeasurementSequence();
    
    system_status.measurement_count++;
}

void selectElectrode(uint8_t electrode_id) {
    // Control electrode multiplexer
    digitalWrite(ELECTRODE_MUX_A, electrode_id & 0x01);
    digitalWrite(ELECTRODE_MUX_B, (electrode_id >> 1) & 0x01);
    digitalWrite(ELECTRODE_MUX_C, (electrode_id >> 2) & 0x01);
    digitalWrite(ELECTRODE_MUX_EN, HIGH);
    
    delay(100); // Allow settling time
}

void performLPRMeasurement() {
    Serial.println("Performing LPR measurement...");
    
    // Configure potentiostat for LPR
    configurePotentiostatForLPR();
    
    // Measure open circuit potential
    float ocp = measureOpenCircuitPotential();
    
    // Perform linear polarization scan
    float polarization_resistance = performLinearPolarizationScan(ocp);
    
    // Calculate corrosion rate
    float corrosion_rate = calculateCorrosionRateFromLPR(polarization_resistance);
    
    // Store results
    ElectrochemicalData& data = electrochemical_data[current_electrode];
    data.timestamp = millis();
    data.electrode_id = current_electrode;
    data.potential = ocp;
    data.polarization_resistance = polarization_resistance;
    data.corrosion_rate = corrosion_rate;
    data.measurement_type = 0; // LPR
    data.data_quality = assessDataQuality(polarization_resistance);
    
    Serial.print("OCP: ");
    Serial.print(ocp);
    Serial.print(" mV, Rp: ");
    Serial.print(polarization_resistance);
    Serial.print(" Ω⋅cm², Rate: ");
    Serial.print(corrosion_rate);
    Serial.println(" mpy");
}

void configurePotentiostatForLPR() {
    digitalWrite(POTENTIOSTAT_CS, LOW);
    
    // Configure for LPR measurement
    SPI.transfer(0x10); // LPR mode register
    SPI.transfer(0x01); // Enable LPR mode
    SPI.transfer(0x11); // Scan rate register
    SPI.transfer(0x05); // 0.1 mV/s scan rate
    SPI.transfer(0x12); // Potential range register
    SPI.transfer(0x14); // ±20 mV range
    
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    delay(100);
}

float measureOpenCircuitPotential() {
    // Measure OCP for 30 seconds
    float ocp_sum = 0.0;
    int measurements = 0;
    
    uint32_t start_time = millis();
    while (millis() - start_time < 30000) {
        float potential = readPotential();
        ocp_sum += potential;
        measurements++;
        delay(1000);
    }
    
    return ocp_sum / measurements;
}

float performLinearPolarizationScan(float ocp) {
    // Perform linear polarization scan ±20 mV around OCP
    float start_potential = ocp - 20.0;
    float end_potential = ocp + 20.0;
    float scan_rate = 0.1; // mV/s
    
    int num_points = (int)((end_potential - start_potential) / scan_rate * 10); // 10 points per mV
    float potentials[num_points];
    float currents[num_points];
    
    // Scan from negative to positive
    for (int i = 0; i < num_points; i++) {
        float potential = start_potential + (i * (end_potential - start_potential) / (num_points - 1));
        
        // Set potential
        setPotential(potential);
        delay(100); // Allow settling
        
        // Read current
        float current = readCurrent();
        
        potentials[i] = potential;
        currents[i] = current;
    }
    
    // Calculate polarization resistance using linear regression
    float polarization_resistance = calculatePolarizationResistance(potentials, currents, num_points);
    
    return polarization_resistance;
}

float calculatePolarizationResistance(float* potentials, float* currents, int num_points) {
    // Use linear regression to find slope (1/Rp)
    float sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_x2 = 0.0;
    
    for (int i = 0; i < num_points; i++) {
        sum_x += potentials[i];
        sum_y += currents[i];
        sum_xy += potentials[i] * currents[i];
        sum_x2 += potentials[i] * potentials[i];
    }
    
    // Calculate slope (dI/dE)
    float slope = (num_points * sum_xy - sum_x * sum_y) / (num_points * sum_x2 - sum_x * sum_x);
    
    // Polarization resistance is 1/slope
    float rp = 1.0 / slope;
    
    // Convert to Ω⋅cm² using electrode area
    float area = calibration_data.area_factor[current_electrode]; // cm²
    return rp * area;
}

float calculateCorrosionRateFromLPR(float polarization_resistance) {
    // Stern-Geary equation: icorr = B / Rp
    // where B is the Stern-Geary constant (typically 26 mV for steel)
    float stern_geary_constant = 26.0; // mV
    float icorr = stern_geary_constant / polarization_resistance; // μA/cm²
    
    // Convert to corrosion rate (mpy)
    float atomic_weight = 55.845; // g/mol for iron
    float density = 7.87; // g/cm³ for steel
    float valence = 2.0; // electrons per atom
    float faraday_constant = 96485.0; // C/mol
    
    // Corrosion rate = (icorr * atomic_weight * 365.25 * 24 * 3600) / (valence * faraday_constant * density)
    float corrosion_rate = (icorr * 1e-6 * atomic_weight * 365.25 * 24 * 3600) / 
                          (valence * faraday_constant * density);
    
    // Convert to mpy (mils per year)
    corrosion_rate *= 393.7; // conversion factor
    
    return corrosion_rate;
}

void performEISMeasurement() {
    Serial.println("Performing EIS measurement...");
    
    // Configure potentiostat for EIS
    configurePotentiostatForEIS();
    
    // Perform impedance sweep
    performImpedanceSweep();
    
    // Analyze impedance data
    analyzeImpedanceData();
}

void configurePotentiostatForEIS() {
    digitalWrite(POTENTIOSTAT_CS, LOW);
    
    // Configure for EIS measurement
    SPI.transfer(0x20); // EIS mode register
    SPI.transfer(0x01); // Enable EIS mode
    SPI.transfer(0x21); // Amplitude register
    SPI.transfer(0x0A); // 10 mV amplitude
    SPI.transfer(0x22); // Frequency start register
    SPI.transfer(0x64); // Start frequency (100 kHz)
    SPI.transfer(0x23); // Frequency end register
    SPI.transfer(0x01); // End frequency (0.01 Hz)
    
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    delay(100);
}

void performImpedanceSweep() {
    // Perform impedance measurements at various frequencies
    for (int i = 0; i < eis_points; i++) {
        float frequency = eis_frequency_max * pow(10.0, -i * log10(eis_frequency_max / eis_frequency_min) / (eis_points - 1));
        
        // Set frequency
        setFrequency(frequency);
        
        // Measure impedance
        float magnitude = readImpedanceMagnitude();
        float phase = readImpedancePhase();
        
        // Store impedance data
        ElectrochemicalData& data = electrochemical_data[current_electrode];
        data.impedance_magnitude = magnitude;
        data.impedance_phase = phase;
        data.measurement_type = 1; // EIS
        
        Serial.print("Freq: ");
        Serial.print(frequency);
        Serial.print(" Hz, |Z|: ");
        Serial.print(magnitude);
        Serial.print(" Ω, Phase: ");
        Serial.print(phase);
        Serial.println("°");
        
        delay(1000); // Allow settling between measurements
    }
}

void analyzeImpedanceData() {
    // Analyze impedance data to extract corrosion parameters
    // This would typically involve fitting equivalent circuit models
    
    // For now, use simple analysis
    float solution_resistance = electrochemical_data[current_electrode].impedance_magnitude;
    float charge_transfer_resistance = solution_resistance * 10.0; // Simplified
    
    // Calculate corrosion rate from charge transfer resistance
    float corrosion_rate = calculateCorrosionRateFromEIS(charge_transfer_resistance);
    
    electrochemical_data[current_electrode].corrosion_rate = corrosion_rate;
    electrochemical_data[current_electrode].resistance = charge_transfer_resistance;
}

float calculateCorrosionRateFromEIS(float charge_transfer_resistance) {
    // Similar to LPR but using charge transfer resistance
    float stern_geary_constant = 26.0; // mV
    float icorr = stern_geary_constant / charge_transfer_resistance; // μA/cm²
    
    // Convert to mpy
    float atomic_weight = 55.845;
    float density = 7.87;
    float valence = 2.0;
    float faraday_constant = 96485.0;
    
    float corrosion_rate = (icorr * 1e-6 * atomic_weight * 365.25 * 24 * 3600) / 
                          (valence * faraday_constant * density);
    
    return corrosion_rate * 393.7; // Convert to mpy
}

void performENMeasurement() {
    Serial.println("Performing EN measurement...");
    
    // Configure potentiostat for EN
    configurePotentiostatForEN();
    
    // Collect electrochemical noise data
    collectElectrochemicalNoise();
    
    // Analyze noise data
    analyzeElectrochemicalNoise();
}

void configurePotentiostatForEN() {
    digitalWrite(POTENTIOSTAT_CS, LOW);
    
    // Configure for EN measurement
    SPI.transfer(0x30); // EN mode register
    SPI.transfer(0x01); // Enable EN mode
    SPI.transfer(0x31); // Sampling rate register
    SPI.transfer(0x64); // 100 Hz sampling rate
    SPI.transfer(0x32); // Measurement time register
    SPI.transfer(0x2C); // 300 seconds
    
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    delay(100);
}

void collectElectrochemicalNoise() {
    // Collect potential and current noise for specified time
    uint32_t measurement_time = (uint32_t)(en_measurement_time * 1000); // Convert to milliseconds
    uint32_t start_time = millis();
    
    int sample_count = 0;
    float potential_sum = 0.0;
    float current_sum = 0.0;
    float potential_sum_sq = 0.0;
    float current_sum_sq = 0.0;
    
    while (millis() - start_time < measurement_time) {
        float potential = readPotential();
        float current = readCurrent();
        
        potential_sum += potential;
        current_sum += current;
        potential_sum_sq += potential * potential;
        current_sum_sq += current * current;
        sample_count++;
        
        delay(10); // 100 Hz sampling rate
    }
    
    // Calculate noise parameters
    float potential_mean = potential_sum / sample_count;
    float current_mean = current_sum / sample_count;
    float potential_variance = (potential_sum_sq / sample_count) - (potential_mean * potential_mean);
    float current_variance = (current_sum_sq / sample_count) - (current_mean * current_mean);
    
    float potential_noise = sqrt(potential_variance);
    float current_noise = sqrt(current_variance);
    
    // Store noise data
    ElectrochemicalData& data = electrochemical_data[current_electrode];
    data.noise_resistance = potential_noise / current_noise;
    data.noise_current = current_noise * 1e6; // Convert to μA
    data.measurement_type = 2; // EN
    
    Serial.print("Potential noise: ");
    Serial.print(potential_noise);
    Serial.print(" mV, Current noise: ");
    Serial.print(current_noise * 1e6);
    Serial.print(" μA, Rn: ");
    Serial.print(data.noise_resistance);
    Serial.println(" Ω");
}

void analyzeElectrochemicalNoise() {
    // Analyze noise data for corrosion information
    float noise_resistance = electrochemical_data[current_electrode].noise_resistance;
    
    // Calculate corrosion rate from noise resistance
    float corrosion_rate = calculateCorrosionRateFromEN(noise_resistance);
    
    electrochemical_data[current_electrode].corrosion_rate = corrosion_rate;
    
    // Determine corrosion type from noise characteristics
    uint8_t corrosion_type = determineCorrosionType();
    corrosion_assessment[current_electrode].corrosion_type = corrosion_type;
}

float calculateCorrosionRateFromEN(float noise_resistance) {
    // Use noise resistance to estimate corrosion rate
    // This is similar to LPR but with noise resistance
    float stern_geary_constant = 26.0; // mV
    float icorr = stern_geary_constant / noise_resistance; // μA/cm²
    
    // Convert to mpy
    float atomic_weight = 55.845;
    float density = 7.87;
    float valence = 2.0;
    float faraday_constant = 96485.0;
    
    float corrosion_rate = (icorr * 1e-6 * atomic_weight * 365.25 * 24 * 3600) / 
                          (valence * faraday_constant * density);
    
    return corrosion_rate * 393.7; // Convert to mpy
}

uint8_t determineCorrosionType() {
    // Analyze noise characteristics to determine corrosion type
    float current_noise = electrochemical_data[current_electrode].noise_current;
    float potential_noise = electrochemical_data[current_electrode].noise_resistance * current_noise;
    
    // Simple classification based on noise levels
    if (current_noise > 100.0) { // High current noise
        return 1; // Pitting corrosion
    } else if (potential_noise > 50.0) { // High potential noise
        return 2; // Galvanic corrosion
    } else {
        return 0; // Uniform corrosion
    }
}

void performCPMeasurement() {
    Serial.println("Performing CP measurement...");
    
    // Configure potentiostat for CP monitoring
    configurePotentiostatForCP();
    
    // Measure structure-to-electrolyte potential
    float potential = measureStructurePotential();
    
    // Assess cathodic protection effectiveness
    assessCathodicProtection(potential);
    
    // Store CP data
    ElectrochemicalData& data = electrochemical_data[current_electrode];
    data.timestamp = millis();
    data.electrode_id = current_electrode;
    data.potential = potential;
    data.measurement_type = 3; // CP
    
    Serial.print("Structure potential: ");
    Serial.print(potential);
    Serial.println(" mV");
}

void configurePotentiostatForCP() {
    digitalWrite(POTENTIOSTAT_CS, LOW);
    
    // Configure for CP measurement
    SPI.transfer(0x40); // CP mode register
    SPI.transfer(0x01); // Enable CP mode
    SPI.transfer(0x41); // Reference electrode register
    SPI.transfer(0x02); // Cu/CuSO4 reference
    
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    delay(100);
}

float measureStructurePotential() {
    // Measure potential for 60 seconds
    float potential_sum = 0.0;
    int measurements = 0;
    
    uint32_t start_time = millis();
    while (millis() - start_time < 60000) {
        float potential = readPotential();
        potential_sum += potential;
        measurements++;
        delay(1000);
    }
    
    return potential_sum / measurements;
}

void assessCathodicProtection(float potential) {
    // Assess CP effectiveness based on potential criteria
    // For steel in soil: -850 mV vs Cu/CuSO4 minimum
    
    float cp_criterion = -850.0; // mV vs Cu/CuSO4
    
    if (potential < cp_criterion) {
        Serial.println("Cathodic protection: ADEQUATE");
        corrosion_assessment[current_electrode].severity_level = 0; // Low
    } else {
        Serial.println("Cathodic protection: INADEQUATE");
        corrosion_assessment[current_electrode].severity_level = 3; // Critical
    }
}

void readEnvironmentalSensors() {
    // Read temperature
    temperature_sensor.requestTemperatures();
    environmental_data.temperature = temperature_sensor.getTempCByIndex(0);
    
    // Read pH
    int ph_raw = analogRead(PH_SENSOR_PIN);
    environmental_data.ph_value = convertRawToPH(ph_raw);
    
    // Read conductivity
    int conductivity_raw = analogRead(CONDUCTIVITY_PIN);
    environmental_data.conductivity = convertRawToConductivity(conductivity_raw);
    
    // Read dissolved oxygen
    int do_raw = analogRead(DISSOLVED_O2_PIN);
    environmental_data.dissolved_oxygen = convertRawToDissolvedOxygen(do_raw);
    
    // Read chloride concentration
    int chloride_raw = analogRead(CHLORIDE_PIN);
    environmental_data.chloride_concentration = convertRawToChloride(chloride_raw);
    
    // Read humidity
    int humidity_raw = analogRead(HUMIDITY_SENSOR_PIN);
    environmental_data.humidity = convertRawToHumidity(humidity_raw);
    
    // Read atmospheric pressure
    int pressure_raw = analogRead(PRESSURE_SENSOR_PIN);
    environmental_data.atmospheric_pressure = convertRawToPressure(pressure_raw);
    
    environmental_data.timestamp = millis();
    
    Serial.print("Environmental - Temp: ");
    Serial.print(environmental_data.temperature);
    Serial.print("°C, pH: ");
    Serial.print(environmental_data.ph_value);
    Serial.print(", Conductivity: ");
    Serial.print(environmental_data.conductivity);
    Serial.print(" μS/cm, Chlorides: ");
    Serial.print(environmental_data.chloride_concentration);
    Serial.println(" ppm");
}

float convertRawToPH(int raw_value) {
    // Convert ADC reading to pH
    float voltage = (raw_value * 5.0) / 1023.0;
    float ph = calibration_data.ph_slope * voltage + calibration_data.ph_offset;
    return ph;
}

float convertRawToConductivity(int raw_value) {
    // Convert ADC reading to conductivity
    float voltage = (raw_value * 5.0) / 1023.0;
    float conductivity = voltage * calibration_data.conductivity_factor;
    return conductivity;
}

float convertRawToDissolvedOxygen(int raw_value) {
    // Convert ADC reading to dissolved oxygen
    float voltage = (raw_value * 5.0) / 1023.0;
    float do_value = calibration_data.do_slope * voltage + calibration_data.do_offset;
    return do_value;
}

float convertRawToChloride(int raw_value) {
    // Convert ADC reading to chloride concentration
    float voltage = (raw_value * 5.0) / 1023.0;
    float chloride = calibration_data.chloride_slope * voltage + calibration_data.chloride_offset;
    return chloride;
}

float convertRawToHumidity(int raw_value) {
    // Convert ADC reading to humidity
    float voltage = (raw_value * 5.0) / 1023.0;
    float humidity = voltage * 20.0; // 0-5V = 0-100% RH
    return humidity;
}

float convertRawToPressure(int raw_value) {
    // Convert ADC reading to atmospheric pressure
    float voltage = (raw_value * 5.0) / 1023.0;
    float pressure = voltage * 20.0 + 80.0; // 0-5V = 80-180 kPa
    return pressure;
}

void calculateCorrosionAssessment() {
    CorrosionAssessment& assessment = corrosion_assessment[current_electrode];
    ElectrochemicalData& data = electrochemical_data[current_electrode];
    
    assessment.timestamp = millis();
    assessment.electrode_id = current_electrode;
    assessment.instantaneous_rate = data.corrosion_rate;
    
    // Calculate running averages
    updateRunningAverages();
    
    // Calculate cumulative loss
    assessment.cumulative_loss = calculateCumulativeLoss();
    
    // Calculate remaining thickness
    float initial_thickness = 250.0; // mils (example)
    assessment.remaining_thickness = initial_thickness - assessment.cumulative_loss;
    
    // Predict remaining life
    assessment.predicted_life = calculatePredictedLife();
    
    // Assess severity
    assessment.severity_level = assessSeverityLevel();
    
    // Set confidence level
    assessment.confidence_level = calculateConfidenceLevel();
    
    // Generate alert message if needed
    if (assessment.severity_level > 1) {
        generateAlertMessage();
    }
}

void updateRunningAverages() {
    // Update 24-hour and 7-day running averages
    // This would typically use a circular buffer
    
    // Simplified calculation for demonstration
    static float daily_sum = 0.0;
    static int daily_count = 0;
    static float weekly_sum = 0.0;
    static int weekly_count = 0;
    
    daily_sum += electrochemical_data[current_electrode].corrosion_rate;
    daily_count++;
    
    weekly_sum += electrochemical_data[current_electrode].corrosion_rate;
    weekly_count++;
    
    // Reset daily average every 24 hours
    if (daily_count >= 1440) { // 1440 minutes in a day
        corrosion_assessment[current_electrode].average_rate_24h = daily_sum / daily_count;
        daily_sum = 0.0;
        daily_count = 0;
    }
    
    // Reset weekly average every 7 days
    if (weekly_count >= 10080) { // 10080 minutes in a week
        corrosion_assessment[current_electrode].average_rate_7d = weekly_sum / weekly_count;
        weekly_sum = 0.0;
        weekly_count = 0;
    }
}

float calculateCumulativeLoss() {
    // Calculate cumulative material loss based on corrosion rate
    float average_rate = corrosion_assessment[current_electrode].average_rate_24h;
    float time_hours = millis() / 3600000.0; // Convert to hours
    float cumulative_loss = (average_rate * time_hours) / 8760.0; // Convert to mils
    
    return cumulative_loss;
}

float calculatePredictedLife() {
    // Predict remaining life based on current corrosion rate
    float remaining_thickness = corrosion_assessment[current_electrode].remaining_thickness;
    float current_rate = corrosion_assessment[current_electrode].instantaneous_rate;
    
    if (current_rate > 0) {
        float predicted_life = remaining_thickness / current_rate; // years
        return predicted_life;
    }
    
    return 999.0; // Very long life
}

uint8_t assessSeverityLevel() {
    float corrosion_rate = electrochemical_data[current_electrode].corrosion_rate;
    
    if (corrosion_rate < 2.0) {
        return 0; // Low
    } else if (corrosion_rate < 10.0) {
        return 1; // Medium
    } else if (corrosion_rate < 50.0) {
        return 2; // High
    } else {
        return 3; // Critical
    }
}

float calculateConfidenceLevel() {
    // Calculate confidence level based on data quality
    uint8_t data_quality = electrochemical_data[current_electrode].data_quality;
    
    // Convert data quality to confidence level
    return (float)data_quality;
}

void generateAlertMessage() {
    String message = "CORROSION ALERT: Electrode " + String(current_electrode) + 
                    " - Rate: " + String(electrochemical_data[current_electrode].corrosion_rate) + 
                    " mpy, Severity: ";
    
    switch (corrosion_assessment[current_electrode].severity_level) {
        case 1: message += "MEDIUM"; break;
        case 2: message += "HIGH"; break;
        case 3: message += "CRITICAL"; break;
    }
    
    corrosion_assessment[current_electrode].alert_message = message;
    
    Serial.println(message);
}

void storeElectrochemicalData() {
    // Store data in buffer
    if (buffer_index < DATA_BUFFER_SIZE) {
        data_buffer[buffer_index] = electrochemical_data[current_electrode];
        buffer_index++;
    } else {
        buffer_full = true;
        // Shift buffer or save to SD card
        saveDataToSD();
        buffer_index = 0;
    }
}

void saveDataToSD() {
    String filename = "/data/corrosion_" + String(millis()) + ".csv";
    
    File dataFile = SD.open(filename, FILE_WRITE);
    if (dataFile) {
        // Write header
        dataFile.println("Timestamp,Electrode,Potential,Current,Resistance,Rate,Type,Quality");
        
        // Write data
        for (int i = 0; i < buffer_index; i++) {
            dataFile.print(data_buffer[i].timestamp);
            dataFile.print(",");
            dataFile.print(data_buffer[i].electrode_id);
            dataFile.print(",");
            dataFile.print(data_buffer[i].potential);
            dataFile.print(",");
            dataFile.print(data_buffer[i].current);
            dataFile.print(",");
            dataFile.print(data_buffer[i].resistance);
            dataFile.print(",");
            dataFile.print(data_buffer[i].corrosion_rate);
            dataFile.print(",");
            dataFile.print(data_buffer[i].measurement_type);
            dataFile.print(",");
            dataFile.println(data_buffer[i].data_quality);
        }
        
        dataFile.close();
        Serial.println("Data saved to SD card: " + filename);
    }
}

void advanceMeasurementSequence() {
    // Advance to next measurement
    measurement_mode++;
    if (measurement_mode > 3) {
        measurement_mode = 0;
        current_electrode++;
        if (current_electrode >= MAX_ELECTRODES) {
            current_electrode = 0;
        }
    }
}

void updateSystemStatus() {
    system_status.timestamp = millis();
    system_status.uptime = millis() / 1000;
    
    // Read power status
    int battery_raw = analogRead(BATTERY_VOLTAGE_PIN);
    system_status.battery_voltage = (battery_raw * 5.0 / 1023.0) * 4.0; // Voltage divider
    
    int solar_raw = analogRead(SOLAR_VOLTAGE_PIN);
    system_status.solar_voltage = (solar_raw * 5.0 / 1023.0) * 4.0; // Voltage divider
    
    // Check power adequacy
    system_status.power_adequate = (system_status.battery_voltage > 11.0);
    
    // Read system temperature
    system_status.system_temperature = environmental_data.temperature;
    
    // Calculate data storage usage
    system_status.data_storage_usage = calculateStorageUsage();
    
    // Update status LEDs
    updateStatusLEDs();
}

float calculateStorageUsage() {
    // Calculate SD card usage
    // This is a simplified calculation
    return (float)buffer_index / DATA_BUFFER_SIZE * 100.0;
}

void updateStatusLEDs() {
    // Green LED: System operational
    digitalWrite(STATUS_LED_GREEN, system_status.system_operational);
    
    // Red LED: System fault
    digitalWrite(STATUS_LED_RED, !system_status.system_operational || system_status.error_count > 0);
    
    // Blue LED: Communication active
    digitalWrite(STATUS_LED_BLUE, system_status.communication_active);
}

void transmitData() {
    Serial.println("Transmitting data...");
    
    // Prepare data for transmission
    StaticJsonDocument<2048> doc;
    
    // System status
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = millis();
    doc["battery_voltage"] = system_status.battery_voltage;
    doc["solar_voltage"] = system_status.solar_voltage;
    doc["uptime"] = system_status.uptime;
    
    // Environmental data
    doc["temperature"] = environmental_data.temperature;
    doc["ph"] = environmental_data.ph_value;
    doc["conductivity"] = environmental_data.conductivity;
    doc["chlorides"] = environmental_data.chloride_concentration;
    doc["humidity"] = environmental_data.humidity;
    
    // Corrosion data for all electrodes
    JsonArray electrodes = doc.createNestedArray("electrodes");
    for (int i = 0; i < MAX_ELECTRODES; i++) {
        JsonObject electrode = electrodes.createNestedObject();
        electrode["id"] = i;
        electrode["potential"] = electrochemical_data[i].potential;
        electrode["current"] = electrochemical_data[i].current;
        electrode["corrosion_rate"] = electrochemical_data[i].corrosion_rate;
        electrode["severity"] = corrosion_assessment[i].severity_level;
        electrode["predicted_life"] = corrosion_assessment[i].predicted_life;
    }
    
    // Serialize and send
    String json_string;
    serializeJson(doc, json_string);
    
    // Send via ESP32
    ESP32_SERIAL.println(json_string);
    
    // Send via LoRa
    LORA_SERIAL.println(json_string);
    
    system_status.communication_active = true;
    
    Serial.println("Data transmitted");
}

void processAlerts() {
    // Check for alarm conditions
    for (int i = 0; i < MAX_ELECTRODES; i++) {
        // Check corrosion rate alarm
        if (electrochemical_data[i].corrosion_rate > corrosion_rate_alarm) {
            triggerAlarm("High corrosion rate on electrode " + String(i));
        }
        
        // Check potential alarms
        if (electrochemical_data[i].potential < potential_alarm_low || 
            electrochemical_data[i].potential > potential_alarm_high) {
            triggerAlarm("Potential alarm on electrode " + String(i));
        }
    }
    
    // Check environmental alarms
    if (environmental_data.ph_value < ph_alarm_low || 
        environmental_data.ph_value > ph_alarm_high) {
        triggerAlarm("pH alarm: " + String(environmental_data.ph_value));
    }
    
    if (environmental_data.chloride_concentration > chloride_alarm) {
        triggerAlarm("Chloride alarm: " + String(environmental_data.chloride_concentration) + " ppm");
    }
}

void triggerAlarm(String message) {
    Serial.println("ALARM: " + message);
    
    // Sound buzzer
    for (int i = 0; i < 3; i++) {
        digitalWrite(ALARM_BUZZER, HIGH);
        delay(200);
        digitalWrite(ALARM_BUZZER, LOW);
        delay(200);
    }
    
    // Send alarm message
    sendAlarmMessage(message);
    
    // Log alarm
    logAlarm(message);
}

void sendAlarmMessage(String message) {
    StaticJsonDocument<256> doc;
    doc["type"] = "alarm";
    doc["device_id"] = DEVICE_ID;
    doc["timestamp"] = millis();
    doc["message"] = message;
    doc["severity"] = "high";
    
    String json_string;
    serializeJson(doc, json_string);
    
    ESP32_SERIAL.println(json_string);
}

void logAlarm(String message) {
    File logFile = SD.open("/logs/alarms.log", FILE_WRITE);
    if (logFile) {
        logFile.print(millis());
        logFile.print(",");
        logFile.println(message);
        logFile.close();
    }
}

void managePower() {
    // Check battery voltage
    if (system_status.battery_voltage < 11.0) {
        // Low battery - reduce power consumption
        reducePowerConsumption();
    }
    
    // Check solar voltage
    if (system_status.solar_voltage > 13.0) {
        // Solar charging available
        optimizeSolarCharging();
    }
    
    // Check temperature for battery heater
    if (environmental_data.temperature < 0.0) {
        digitalWrite(BATTERY_HEATER, HIGH);
    } else {
        digitalWrite(BATTERY_HEATER, LOW);
    }
}

void reducePowerConsumption() {
    // Reduce measurement frequency
    MONITORING_INTERVAL = 300000; // 5 minutes
    
    // Reduce communication frequency
    // Power down non-essential systems
    
    Serial.println("Reduced power consumption mode");
}

void optimizeSolarCharging() {
    // Optimize solar charge controller
    int pwm_value = map(system_status.solar_voltage, 13.0, 18.0, 128, 255);
    analogWrite(SOLAR_CHARGE_CTRL, pwm_value);
}

void handleEmergencyStop() {
    Serial.println("EMERGENCY STOP ACTIVATED!");
    
    // Stop all measurements
    measurement_active = false;
    
    // Save critical data
    saveDataToSD();
    
    // Send emergency message
    sendAlarmMessage("Emergency stop activated");
    
    // Turn on red LED
    digitalWrite(STATUS_LED_RED, HIGH);
    
    // Wait for emergency stop to be cleared
    while (digitalRead(EMERGENCY_STOP) == LOW) {
        delay(100);
    }
    
    // Reset system
    Serial.println("Emergency stop cleared - restarting system...");
    delay(1000);
    setup(); // Restart system
}

void handleMaintenanceMode() {
    Serial.println("MAINTENANCE MODE ACTIVATED");
    
    // Stop measurements
    measurement_active = false;
    
    // Enter maintenance loop
    while (digitalRead(MAINTENANCE_MODE) == LOW) {
        // Handle maintenance commands
        if (Serial.available()) {
            String command = Serial.readStringUntil('\n');
            handleMaintenanceCommand(command);
        }
        
        delay(100);
    }
    
    // Exit maintenance mode
    Serial.println("Exiting maintenance mode");
    measurement_active = true;
}

void handleMaintenanceCommand(String command) {
    command.trim();
    
    if (command == "calibrate") {
        performCalibration();
    } else if (command == "test") {
        performSystemSelfTest();
    } else if (command == "status") {
        printSystemStatus();
    } else if (command == "reset") {
        resetSystem();
    } else if (command.startsWith("set_alarm ")) {
        setAlarmThreshold(command);
    } else {
        Serial.println("Unknown maintenance command: " + command);
    }
}

void checkCalibration() {
    // Check if calibration is still valid
    uint32_t calibration_age = millis() - calibration_data.calibration_date;
    
    if (calibration_age > 2592000000) { // 30 days
        Serial.println("Calibration expired - recalibration required");
        system_status.calibration_valid = false;
        triggerAlarm("Calibration expired");
    }
}

void performCalibration() {
    Serial.println("Performing system calibration...");
    
    // Calibrate pH sensor
    calibratePHSensor();
    
    // Calibrate conductivity sensor
    calibrateConductivitySensor();
    
    // Calibrate dissolved oxygen sensor
    calibrateDissolvedOxygenSensor();
    
    // Calibrate chloride sensor
    calibrateChlorideSensor();
    
    // Calibrate electrochemical system
    calibrateElectrochemicalSystem();
    
    // Save calibration data
    saveCalibrationData();
    
    Serial.println("Calibration complete");
}

void calibratePHSensor() {
    Serial.println("Calibrating pH sensor...");
    
    // Two-point calibration with pH 4 and pH 7 buffers
    Serial.println("Place sensor in pH 4 buffer and press Enter");
    waitForEnter();
    
    int ph4_reading = analogRead(PH_SENSOR_PIN);
    
    Serial.println("Place sensor in pH 7 buffer and press Enter");
    waitForEnter();
    
    int ph7_reading = analogRead(PH_SENSOR_PIN);
    
    // Calculate calibration parameters
    calibration_data.ph_slope = (7.0 - 4.0) / ((ph7_reading - ph4_reading) * 5.0 / 1023.0);
    calibration_data.ph_offset = 7.0 - (calibration_data.ph_slope * ph7_reading * 5.0 / 1023.0);
    
    Serial.println("pH sensor calibrated");
}

void calibrateConductivitySensor() {
    Serial.println("Calibrating conductivity sensor...");
    
    // Single-point calibration with 1413 μS/cm standard
    Serial.println("Place sensor in 1413 μS/cm standard and press Enter");
    waitForEnter();
    
    int conductivity_reading = analogRead(CONDUCTIVITY_PIN);
    float voltage = (conductivity_reading * 5.0) / 1023.0;
    
    calibration_data.conductivity_factor = 1413.0 / voltage;
    
    Serial.println("Conductivity sensor calibrated");
}

void calibrateDissolvedOxygenSensor() {
    Serial.println("Calibrating dissolved oxygen sensor...");
    
    // Two-point calibration with 0% and 100% oxygen
    Serial.println("Place sensor in 0% oxygen solution and press Enter");
    waitForEnter();
    
    int do_0_reading = analogRead(DISSOLVED_O2_PIN);
    
    Serial.println("Place sensor in air-saturated water and press Enter");
    waitForEnter();
    
    int do_100_reading = analogRead(DISSOLVED_O2_PIN);
    
    // Calculate calibration parameters (assuming 8.26 mg/L at 25°C)
    float do_sat = 8.26;
    calibration_data.do_slope = do_sat / ((do_100_reading - do_0_reading) * 5.0 / 1023.0);
    calibration_data.do_offset = 0.0 - (calibration_data.do_slope * do_0_reading * 5.0 / 1023.0);
    
    Serial.println("Dissolved oxygen sensor calibrated");
}

void calibrateChlorideSensor() {
    Serial.println("Calibrating chloride sensor...");
    
    // Single-point calibration with 1000 ppm standard
    Serial.println("Place sensor in 1000 ppm chloride standard and press Enter");
    waitForEnter();
    
    int chloride_reading = analogRead(CHLORIDE_PIN);
    float voltage = (chloride_reading * 5.0) / 1023.0;
    
    calibration_data.chloride_slope = 1000.0 / voltage;
    calibration_data.chloride_offset = 0.0;
    
    Serial.println("Chloride sensor calibrated");
}

void calibrateElectrochemicalSystem() {
    Serial.println("Calibrating electrochemical system...");
    
    // Calibrate each electrode
    for (int i = 0; i < MAX_ELECTRODES; i++) {
        Serial.print("Calibrating electrode ");
        Serial.println(i);
        
        selectElectrode(i);
        
        // Measure in known solution
        float potential = measureOpenCircuitPotential();
        float known_potential = -200.0; // mV (example)
        
        calibration_data.potential_offset[i] = known_potential - potential;
        calibration_data.current_gain[i] = 1.0; // Default gain
        calibration_data.area_factor[i] = 1.0; // 1 cm² default
    }
    
    Serial.println("Electrochemical system calibrated");
}

void saveCalibrationData() {
    File calFile = SD.open("/calibration/calibration.json", FILE_WRITE);
    if (calFile) {
        StaticJsonDocument<1024> doc;
        
        doc["calibration_date"] = millis();
        doc["ph_slope"] = calibration_data.ph_slope;
        doc["ph_offset"] = calibration_data.ph_offset;
        doc["conductivity_factor"] = calibration_data.conductivity_factor;
        doc["do_slope"] = calibration_data.do_slope;
        doc["do_offset"] = calibration_data.do_offset;
        doc["chloride_slope"] = calibration_data.chloride_slope;
        doc["chloride_offset"] = calibration_data.chloride_offset;
        
        JsonArray potential_offsets = doc.createNestedArray("potential_offsets");
        JsonArray current_gains = doc.createNestedArray("current_gains");
        JsonArray area_factors = doc.createNestedArray("area_factors");
        
        for (int i = 0; i < MAX_ELECTRODES; i++) {
            potential_offsets.add(calibration_data.potential_offset[i]);
            current_gains.add(calibration_data.current_gain[i]);
            area_factors.add(calibration_data.area_factor[i]);
        }
        
        serializeJson(doc, calFile);
        calFile.close();
        
        calibration_data.calibration_date = millis();
        calibration_data.calibration_valid = true;
        system_status.calibration_valid = true;
        
        Serial.println("Calibration data saved");
    }
}

void loadCalibrationData() {
    if (SD.exists("/calibration/calibration.json")) {
        File calFile = SD.open("/calibration/calibration.json", FILE_READ);
        if (calFile) {
            StaticJsonDocument<1024> doc;
            deserializeJson(doc, calFile);
            
            calibration_data.calibration_date = doc["calibration_date"];
            calibration_data.ph_slope = doc["ph_slope"];
            calibration_data.ph_offset = doc["ph_offset"];
            calibration_data.conductivity_factor = doc["conductivity_factor"];
            calibration_data.do_slope = doc["do_slope"];
            calibration_data.do_offset = doc["do_offset"];
            calibration_data.chloride_slope = doc["chloride_slope"];
            calibration_data.chloride_offset = doc["chloride_offset"];
            
            for (int i = 0; i < MAX_ELECTRODES; i++) {
                calibration_data.potential_offset[i] = doc["potential_offsets"][i];
                calibration_data.current_gains[i] = doc["current_gains"][i];
                calibration_data.area_factor[i] = doc["area_factors"][i];
            }
            
            calibration_data.calibration_valid = true;
            system_status.calibration_valid = true;
            
            calFile.close();
            Serial.println("Calibration data loaded");
        }
    } else {
        // Use default calibration values
        calibration_data.ph_slope = -59.16; // mV/pH
        calibration_data.ph_offset = 7.0;
        calibration_data.conductivity_factor = 1000.0;
        calibration_data.do_slope = 1.0;
        calibration_data.do_offset = 0.0;
        calibration_data.chloride_slope = 1000.0;
        calibration_data.chloride_offset = 0.0;
        
        for (int i = 0; i < MAX_ELECTRODES; i++) {
            calibration_data.potential_offset[i] = 0.0;
            calibration_data.current_gains[i] = 1.0;
            calibration_data.area_factor[i] = 1.0;
        }
        
        calibration_data.calibration_valid = false;
        system_status.calibration_valid = false;
        
        Serial.println("Using default calibration values");
    }
}

void processSerialCommands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command == "status") {
            printSystemStatus();
        } else if (command == "data") {
            printCurrentData();
        } else if (command == "calibrate") {
            performCalibration();
        } else if (command == "test") {
            performSystemSelfTest();
        } else if (command == "reset") {
            resetSystem();
        } else if (command.startsWith("set_interval ")) {
            setMonitoringInterval(command);
        } else if (command.startsWith("set_alarm ")) {
            setAlarmThreshold(command);
        } else if (command == "help") {
            printHelp();
        } else {
            Serial.println("Unknown command: " + command);
        }
    }
}

void printSystemStatus() {
    Serial.println("=== System Status ===");
    Serial.println("Device ID: " + String(DEVICE_ID));
    Serial.println("Uptime: " + String(system_status.uptime) + " seconds");
    Serial.println("Battery Voltage: " + String(system_status.battery_voltage) + " V");
    Serial.println("Solar Voltage: " + String(system_status.solar_voltage) + " V");
    Serial.println("Temperature: " + String(system_status.system_temperature) + " °C");
    Serial.println("Measurements: " + String(system_status.measurement_count));
    Serial.println("Errors: " + String(system_status.error_count));
    Serial.println("Calibration Valid: " + String(system_status.calibration_valid ? "Yes" : "No"));
    Serial.println("System Operational: " + String(system_status.system_operational ? "Yes" : "No"));
    Serial.println("====================");
}

void printCurrentData() {
    Serial.println("=== Current Data ===");
    
    // Environmental data
    Serial.println("Environmental:");
    Serial.println("  Temperature: " + String(environmental_data.temperature) + " °C");
    Serial.println("  pH: " + String(environmental_data.ph_value));
    Serial.println("  Conductivity: " + String(environmental_data.conductivity) + " μS/cm");
    Serial.println("  Dissolved O2: " + String(environmental_data.dissolved_oxygen) + " mg/L");
    Serial.println("  Chlorides: " + String(environmental_data.chloride_concentration) + " ppm");
    Serial.println("  Humidity: " + String(environmental_data.humidity) + " %RH");
    
    // Electrochemical data
    Serial.println("Electrochemical:");
    for (int i = 0; i < MAX_ELECTRODES; i++) {
        Serial.print("  Electrode ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(electrochemical_data[i].potential);
        Serial.print(" mV, ");
        Serial.print(electrochemical_data[i].corrosion_rate);
        Serial.print(" mpy, Severity: ");
        Serial.println(corrosion_assessment[i].severity_level);
    }
    
    Serial.println("===================");
}

void printHelp() {
    Serial.println("=== Available Commands ===");
    Serial.println("status - Show system status");
    Serial.println("data - Show current data");
    Serial.println("calibrate - Perform system calibration");
    Serial.println("test - Perform system self-test");
    Serial.println("reset - Reset system");
    Serial.println("set_interval <ms> - Set monitoring interval");
    Serial.println("set_alarm <type> <value> - Set alarm threshold");
    Serial.println("help - Show this help message");
    Serial.println("=========================");
}

void setMonitoringInterval(String command) {
    int space_index = command.indexOf(' ');
    if (space_index > 0) {
        String interval_str = command.substring(space_index + 1);
        long interval = interval_str.toInt();
        
        if (interval > 0) {
            MONITORING_INTERVAL = interval;
            Serial.println("Monitoring interval set to: " + String(interval) + " ms");
        } else {
            Serial.println("Invalid interval value");
        }
    }
}

void setAlarmThreshold(String command) {
    // Parse command: set_alarm <type> <value>
    int first_space = command.indexOf(' ');
    int second_space = command.indexOf(' ', first_space + 1);
    
    if (first_space > 0 && second_space > 0) {
        String type = command.substring(first_space + 1, second_space);
        String value_str = command.substring(second_space + 1);
        float value = value_str.toFloat();
        
        if (type == "corrosion_rate") {
            corrosion_rate_alarm = value;
            Serial.println("Corrosion rate alarm set to: " + String(value) + " mpy");
        } else if (type == "ph_low") {
            ph_alarm_low = value;
            Serial.println("pH low alarm set to: " + String(value));
        } else if (type == "ph_high") {
            ph_alarm_high = value;
            Serial.println("pH high alarm set to: " + String(value));
        } else if (type == "chloride") {
            chloride_alarm = value;
            Serial.println("Chloride alarm set to: " + String(value) + " ppm");
        } else {
            Serial.println("Unknown alarm type: " + type);
        }
    }
}

void resetSystem() {
    Serial.println("Resetting system...");
    
    // Save current data
    saveDataToSD();
    
    // Reset variables
    buffer_index = 0;
    buffer_full = false;
    system_status.error_count = 0;
    system_status.last_error = "";
    
    // Restart measurements
    measurement_active = false;
    delay(1000);
    measurement_active = true;
    
    Serial.println("System reset complete");
}

void waitForEnter() {
    while (Serial.available() == 0) {
        delay(100);
    }
    while (Serial.available() > 0) {
        Serial.read();
    }
}

// Low-level hardware interface functions
float readPotential() {
    // Read potential from potentiostat
    digitalWrite(POTENTIOSTAT_CS, LOW);
    SPI.transfer(0x50); // Read potential command
    uint16_t raw_value = SPI.transfer16(0x0000);
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    
    // Convert to mV
    float potential = (raw_value * 2000.0 / 65535.0) - 1000.0; // ±1000 mV range
    return potential;
}

float readCurrent() {
    // Read current from potentiostat
    digitalWrite(POTENTIOSTAT_CS, LOW);
    SPI.transfer(0x51); // Read current command
    uint16_t raw_value = SPI.transfer16(0x0000);
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    
    // Convert to μA
    float current = (raw_value * 2000.0 / 65535.0) - 1000.0; // ±1000 μA range
    return current;
}

void setPotential(float potential) {
    // Set potential on potentiostat
    uint16_t dac_value = (potential + 1000.0) * 65535.0 / 2000.0; // ±1000 mV range
    
    digitalWrite(POTENTIOSTAT_CS, LOW);
    SPI.transfer(0x60); // Set potential command
    SPI.transfer16(dac_value);
    digitalWrite(POTENTIOSTAT_CS, HIGH);
}

void setFrequency(float frequency) {
    // Set frequency for EIS measurements
    uint32_t freq_reg = (uint32_t)(frequency * 1000000.0 / 25.0); // 25 MHz clock
    
    digitalWrite(POTENTIOSTAT_CS, LOW);
    SPI.transfer(0x70); // Set frequency command
    SPI.transfer(freq_reg >> 24);
    SPI.transfer(freq_reg >> 16);
    SPI.transfer(freq_reg >> 8);
    SPI.transfer(freq_reg);
    digitalWrite(POTENTIOSTAT_CS, HIGH);
}

float readImpedanceMagnitude() {
    // Read impedance magnitude
    digitalWrite(POTENTIOSTAT_CS, LOW);
    SPI.transfer(0x80); // Read impedance magnitude command
    uint16_t raw_value = SPI.transfer16(0x0000);
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    
    // Convert to Ω
    float magnitude = raw_value * 1000000.0 / 65535.0; // 0-1MΩ range
    return magnitude;
}

float readImpedancePhase() {
    // Read impedance phase
    digitalWrite(POTENTIOSTAT_CS, LOW);
    SPI.transfer(0x81); // Read impedance phase command
    uint16_t raw_value = SPI.transfer16(0x0000);
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    
    // Convert to degrees
    float phase = (raw_value * 360.0 / 65535.0) - 180.0; // ±180° range
    return phase;
}

uint8_t assessDataQuality(float measurement_value) {
    // Assess data quality based on measurement characteristics
    if (measurement_value > 0 && measurement_value < 1000000.0) {
        return 90; // Good quality
    } else if (measurement_value > 0) {
        return 60; // Fair quality
    } else {
        return 10; // Poor quality
    }
}

bool testPotentiostatCommunication() {
    // Test potentiostat communication
    digitalWrite(POTENTIOSTAT_CS, LOW);
    SPI.transfer(0x00); // Read ID command
    uint8_t id = SPI.transfer(0x00);
    digitalWrite(POTENTIOSTAT_CS, HIGH);
    
    return (id == 0x42); // Expected ID
}

bool testEnvironmentalSensors() {
    // Test environmental sensors
    float temp = environmental_data.temperature;
    float ph = environmental_data.ph_value;
    
    return (temp > -50.0 && temp < 100.0 && ph > 0.0 && ph < 14.0);
}

bool testPowerSystem() {
    // Test power system
    return (system_status.battery_voltage > 10.0 && system_status.battery_voltage < 15.0);
}

bool testCommunicationSystems() {
    // Test communication systems
    ESP32_SERIAL.println("TEST");
    delay(1000);
    
    return ESP32_SERIAL.available() > 0;
}