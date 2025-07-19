/*
 * Program 22: Environmental Test Chamber
 * 
 * Professional programmable environmental stress testing chamber
 * with temperature, humidity, and UV exposure control for
 * accelerated life testing (ALT), HALT, and HASS procedures
 * 
 * Features:
 * - Temperature: -20°C to +85°C (±0.5°C)
 * - Humidity: 10-90% RH (±2%)
 * - UV-A/UV-B exposure with dosage control
 * - Programmable test profiles
 * - MIL-STD-810G compliance
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>
#include <PID_v1.h>
#include <UTFT.h>
#include <URTouch.h>
#include <ArduinoJson.h>
#include <Adafruit_BME680.h>
#include <LiquidCrystal_I2C.h>

// Pin definitions
#define TEMP_SENSOR_PIN 2
#define HUMIDITY_SENSOR_PIN 3
#define PELTIER_HOT_PIN 4
#define PELTIER_COLD_PIN 5
#define FAN_INTAKE_PIN 6
#define FAN_EXHAUST_PIN 7
#define HUMIDIFIER_PIN 8
#define DEHUMIDIFIER_PIN 9
#define UV_A_PIN 10
#define UV_B_PIN 11
#define HEATER_PIN 12
#define COOLER_PIN 13
#define WATER_PUMP_PIN 14
#define DRAIN_VALVE_PIN 15
#define DOOR_INTERLOCK_PIN 18
#define EMERGENCY_STOP_PIN 19
#define UV_INTERLOCK_PIN 20
#define OVER_TEMP_PIN 21
#define WATER_LEVEL_PIN 22
#define CONDENSATE_LEVEL_PIN 23
#define SD_CS_PIN 53
#define TFT_RS 38
#define TFT_WR 39
#define TFT_CS 40
#define TFT_RST 41

// ESP32 communication
#define ESP32_SERIAL Serial3
#define ESP32_BAUD 115200

// System constants
const float MIN_TEMPERATURE = -20.0;       // Minimum temperature in °C
const float MAX_TEMPERATURE = 85.0;        // Maximum temperature in °C
const float MIN_HUMIDITY = 10.0;           // Minimum humidity in %RH
const float MAX_HUMIDITY = 90.0;           // Maximum humidity in %RH
const float MAX_UV_IRRADIANCE = 1000.0;    // Maximum UV irradiance in W/m²
const float CHAMBER_VOLUME = 0.1;          // Chamber volume in m³
const float TEMP_RAMP_RATE = 5.0;          // Maximum temperature ramp rate °C/min
const float HUMIDITY_RAMP_RATE = 10.0;     // Maximum humidity ramp rate %RH/min

// Test profile structure
struct TestProfile {
    String profile_name;
    uint8_t num_steps;
    float step_temperature[20];    // Temperature for each step
    float step_humidity[20];       // Humidity for each step
    float step_uv_irradiance[20];  // UV irradiance for each step
    uint32_t step_duration[20];    // Duration for each step in seconds
    float ramp_rate[20];           // Ramp rate for each step
    bool cycle_repeat;             // Whether to repeat the cycle
    uint16_t cycle_count;          // Number of cycles to perform
    String test_standard;          // Applicable test standard
};

// Current environmental conditions
struct EnvironmentalData {
    float temperature;             // Current temperature in °C
    float humidity;                // Current humidity in %RH
    float uv_irradiance;           // Current UV irradiance in W/m²
    float pressure;                // Current pressure in hPa
    float dew_point;               // Calculated dew point in °C
    float water_level;             // Water reservoir level in %
    float condensate_level;        // Condensate level in %
    uint32_t timestamp;            // Timestamp of reading
};

// Test execution state
struct TestState {
    bool test_running;             // Test execution flag
    bool profile_loaded;           // Profile loaded flag
    uint8_t current_step;          // Current step in profile
    uint16_t current_cycle;        // Current cycle number
    uint32_t step_start_time;      // Start time of current step
    uint32_t test_start_time;      // Start time of entire test
    float target_temperature;     // Target temperature for current step
    float target_humidity;         // Target humidity for current step
    float target_uv_irradiance;    // Target UV irradiance for current step
    String specimen_id;            // Test specimen identifier
    String test_standard;          // Test standard being followed
};

// Control system parameters
struct ControlParameters {
    // Temperature PID parameters
    double temp_kp, temp_ki, temp_kd;
    double temp_setpoint, temp_input, temp_output;
    
    // Humidity PID parameters
    double humid_kp, humid_ki, humid_kd;
    double humid_setpoint, humid_input, humid_output;
    
    // UV control parameters
    double uv_kp, uv_ki, uv_kd;
    double uv_setpoint, uv_input, uv_output;
};

// Global objects
OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature temp_sensors(&oneWire);
DHT humidity_sensor(HUMIDITY_SENSOR_PIN, DHT22);
Adafruit_BME680 bme680;
UTFT tft(ILI9341_16, TFT_RS, TFT_WR, TFT_CS, TFT_RST);
URTouch touch(7, 8, 9, 10, 11);

// PID controllers
PID temp_pid(&temp_input, &temp_output, &temp_setpoint, 2.0, 0.1, 0.05, DIRECT);
PID humid_pid(&humid_input, &humid_output, &humid_setpoint, 1.0, 0.05, 0.02, DIRECT);
PID uv_pid(&uv_input, &uv_output, &uv_setpoint, 0.5, 0.1, 0.01, DIRECT);

// Test variables
TestProfile current_profile;
TestState test_state;
EnvironmentalData current_conditions;
ControlParameters control_params;

// Safety flags
bool emergency_stop_active = false;
bool door_open = false;
bool over_temperature = false;
bool water_overflow = false;
bool uv_safety_ok = true;

// Data logging
File data_file;
File profile_file;

void setup() {
    Serial.begin(115200);
    ESP32_SERIAL.begin(ESP32_BAUD);
    
    Serial.println(F("Environmental Test Chamber v2.0"));
    Serial.println(F("Initializing system..."));
    
    // Initialize pins
    pinMode(PELTIER_HOT_PIN, OUTPUT);
    pinMode(PELTIER_COLD_PIN, OUTPUT);
    pinMode(FAN_INTAKE_PIN, OUTPUT);
    pinMode(FAN_EXHAUST_PIN, OUTPUT);
    pinMode(HUMIDIFIER_PIN, OUTPUT);
    pinMode(DEHUMIDIFIER_PIN, OUTPUT);
    pinMode(UV_A_PIN, OUTPUT);
    pinMode(UV_B_PIN, OUTPUT);
    pinMode(HEATER_PIN, OUTPUT);
    pinMode(COOLER_PIN, OUTPUT);
    pinMode(WATER_PUMP_PIN, OUTPUT);
    pinMode(DRAIN_VALVE_PIN, OUTPUT);
    
    pinMode(DOOR_INTERLOCK_PIN, INPUT_PULLUP);
    pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
    pinMode(UV_INTERLOCK_PIN, INPUT_PULLUP);
    pinMode(OVER_TEMP_PIN, INPUT_PULLUP);
    pinMode(WATER_LEVEL_PIN, INPUT_PULLUP);
    pinMode(CONDENSATE_LEVEL_PIN, INPUT_PULLUP);
    
    // Attach interrupts
    attachInterrupt(digitalPinToInterrupt(EMERGENCY_STOP_PIN), emergencyStopISR, FALLING);
    attachInterrupt(digitalPinToInterrupt(DOOR_INTERLOCK_PIN), doorInterlockISR, CHANGE);
    attachInterrupt(digitalPinToInterrupt(OVER_TEMP_PIN), overTempISR, FALLING);
    
    // Initialize sensors
    temp_sensors.begin();
    humidity_sensor.begin();
    
    if (!bme680.begin()) {
        Serial.println(F("BME680 initialization failed"));
    } else {
        bme680.setTemperatureOversampling(BME680_OS_8X);
        bme680.setHumidityOversampling(BME680_OS_2X);
        bme680.setPressureOversampling(BME680_OS_4X);
        bme680.setIIRFilterSize(BME680_FILTER_SIZE_3);
        bme680.setGasHeater(320, 150);
    }
    
    // Initialize display
    tft.InitLCD();
    tft.clrScr();
    tft.setFont(BigFont);
    touch.InitTouch();
    touch.setPrecision(PREC_MEDIUM);
    
    // Initialize SD card
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println(F("SD card initialization failed"));
        displayError("SD Card Error");
    } else {
        Serial.println(F("SD card initialized"));
    }
    
    // Initialize PID controllers
    temp_pid.SetMode(AUTOMATIC);
    temp_pid.SetOutputLimits(-100, 100);
    temp_pid.SetSampleTime(1000);
    
    humid_pid.SetMode(AUTOMATIC);
    humid_pid.SetOutputLimits(-100, 100);
    humid_pid.SetSampleTime(2000);
    
    uv_pid.SetMode(AUTOMATIC);
    uv_pid.SetOutputLimits(0, 100);
    uv_pid.SetSampleTime(1000);
    
    // Initialize test state
    test_state.test_running = false;
    test_state.profile_loaded = false;
    test_state.current_step = 0;
    test_state.current_cycle = 0;
    
    // Display startup screen
    displayStartupScreen();
    
    // Perform system check
    performSystemCheck();
    
    // Load default profile
    loadDefaultProfile();
    
    Serial.println(F("System ready"));
}

void loop() {
    // Check emergency conditions
    if (emergency_stop_active) {
        handleEmergencyStop();
        return;
    }
    
    // Check safety interlocks
    checkSafetyInterlocks();
    
    // Read environmental sensors
    readEnvironmentalSensors();
    
    // Execute test profile if running
    if (test_state.test_running) {
        executeTestProfile();
    }
    
    // Update control systems
    updateTemperatureControl();
    updateHumidityControl();
    updateUVControl();
    
    // Handle display and touch
    if (touch.dataAvailable()) {
        handleTouchInput();
    }
    
    // Update display
    static uint32_t last_display_update = 0;
    if (millis() - last_display_update > 1000) {
        updateDisplay();
        last_display_update = millis();
    }
    
    // Log data
    static uint32_t last_data_log = 0;
    if (millis() - last_data_log > 10000) { // Log every 10 seconds
        logEnvironmentalData();
        last_data_log = millis();
    }
    
    // Send data to ESP32
    static uint32_t last_esp32_send = 0;
    if (millis() - last_esp32_send > 5000) { // Send every 5 seconds
        sendDataToESP32();
        last_esp32_send = millis();
    }
    
    // Process serial commands
    if (Serial.available()) {
        processSerialCommand();
    }
    
    // Process ESP32 messages
    if (ESP32_SERIAL.available()) {
        processESP32Message();
    }
}

void readEnvironmentalSensors() {
    // Read temperature sensors
    temp_sensors.requestTemperatures();
    current_conditions.temperature = temp_sensors.getTempCByIndex(0);
    
    // Read humidity sensor
    current_conditions.humidity = humidity_sensor.readHumidity();
    
    // Read BME680 environmental sensor
    if (bme680.performReading()) {
        current_conditions.pressure = bme680.pressure / 100.0; // Convert to hPa
        
        // Calculate dew point
        current_conditions.dew_point = calculateDewPoint(current_conditions.temperature, 
                                                        current_conditions.humidity);
    }
    
    // Read UV sensor (photodiode with calibration)
    int uv_raw = analogRead(A0);
    current_conditions.uv_irradiance = uv_raw * 0.5; // Calibration factor
    
    // Read water levels
    current_conditions.water_level = digitalRead(WATER_LEVEL_PIN) ? 0 : 100;
    current_conditions.condensate_level = digitalRead(CONDENSATE_LEVEL_PIN) ? 0 : 100;
    
    // Update timestamp
    current_conditions.timestamp = millis();
}

void executeTestProfile() {
    if (!test_state.profile_loaded) {
        return;
    }
    
    // Check if current step is complete
    uint32_t step_elapsed = millis() - test_state.step_start_time;
    uint32_t step_duration = current_profile.step_duration[test_state.current_step] * 1000;
    
    if (step_elapsed >= step_duration) {
        // Move to next step
        test_state.current_step++;
        
        if (test_state.current_step >= current_profile.num_steps) {
            // Cycle complete
            test_state.current_cycle++;
            
            if (current_profile.cycle_repeat && 
                test_state.current_cycle < current_profile.cycle_count) {
                // Start next cycle
                test_state.current_step = 0;
                test_state.step_start_time = millis();
                Serial.print(F("Starting cycle "));
                Serial.println(test_state.current_cycle + 1);
            } else {
                // Test complete
                endTest();
                return;
            }
        } else {
            test_state.step_start_time = millis();
        }
        
        // Update targets for new step
        updateStepTargets();
        
        Serial.print(F("Step "));
        Serial.print(test_state.current_step + 1);
        Serial.print(F(" of "));
        Serial.println(current_profile.num_steps);
    }
    
    // Ramp to target values
    rampToTargets();
}

void updateStepTargets() {
    uint8_t step = test_state.current_step;
    
    test_state.target_temperature = current_profile.step_temperature[step];
    test_state.target_humidity = current_profile.step_humidity[step];
    test_state.target_uv_irradiance = current_profile.step_uv_irradiance[step];
    
    // Validate targets
    test_state.target_temperature = constrain(test_state.target_temperature, 
                                             MIN_TEMPERATURE, MAX_TEMPERATURE);
    test_state.target_humidity = constrain(test_state.target_humidity, 
                                          MIN_HUMIDITY, MAX_HUMIDITY);
    test_state.target_uv_irradiance = constrain(test_state.target_uv_irradiance, 
                                               0, MAX_UV_IRRADIANCE);
}

void rampToTargets() {
    float temp_diff = test_state.target_temperature - current_conditions.temperature;
    float humid_diff = test_state.target_humidity - current_conditions.humidity;
    float uv_diff = test_state.target_uv_irradiance - current_conditions.uv_irradiance;
    
    // Calculate ramp rates
    float temp_ramp = current_profile.ramp_rate[test_state.current_step];
    if (temp_ramp == 0) temp_ramp = TEMP_RAMP_RATE;
    
    float humid_ramp = HUMIDITY_RAMP_RATE;
    float uv_ramp = 100.0; // Fast UV ramping
    
    // Apply ramping limits
    float max_temp_change = temp_ramp / 60.0; // Per second
    float max_humid_change = humid_ramp / 60.0;
    float max_uv_change = uv_ramp / 60.0;
    
    // Update setpoints with ramping
    if (abs(temp_diff) > max_temp_change) {
        temp_setpoint += (temp_diff > 0) ? max_temp_change : -max_temp_change;
    } else {
        temp_setpoint = test_state.target_temperature;
    }
    
    if (abs(humid_diff) > max_humid_change) {
        humid_setpoint += (humid_diff > 0) ? max_humid_change : -max_humid_change;
    } else {
        humid_setpoint = test_state.target_humidity;
    }
    
    if (abs(uv_diff) > max_uv_change) {
        uv_setpoint += (uv_diff > 0) ? max_uv_change : -max_uv_change;
    } else {
        uv_setpoint = test_state.target_uv_irradiance;
    }
}

void updateTemperatureControl() {
    // Update PID input
    temp_input = current_conditions.temperature;
    
    // Compute PID output
    temp_pid.Compute();
    
    // Apply control outputs
    if (temp_output > 0) {
        // Heating mode
        analogWrite(HEATER_PIN, map(temp_output, 0, 100, 0, 255));
        analogWrite(PELTIER_HOT_PIN, map(temp_output, 0, 100, 0, 255));
        analogWrite(COOLER_PIN, 0);
        analogWrite(PELTIER_COLD_PIN, 0);
    } else {
        // Cooling mode
        analogWrite(HEATER_PIN, 0);
        analogWrite(PELTIER_HOT_PIN, 0);
        analogWrite(COOLER_PIN, map(-temp_output, 0, 100, 0, 255));
        analogWrite(PELTIER_COLD_PIN, map(-temp_output, 0, 100, 0, 255));
    }
    
    // Control circulation fans
    int fan_speed = map(abs(temp_output), 0, 100, 100, 255);
    analogWrite(FAN_INTAKE_PIN, fan_speed);
    analogWrite(FAN_EXHAUST_PIN, fan_speed);
}

void updateHumidityControl() {
    // Update PID input
    humid_input = current_conditions.humidity;
    
    // Compute PID output
    humid_pid.Compute();
    
    // Apply control outputs
    if (humid_output > 0) {
        // Humidification mode
        analogWrite(HUMIDIFIER_PIN, map(humid_output, 0, 100, 0, 255));
        digitalWrite(DEHUMIDIFIER_PIN, LOW);
        digitalWrite(WATER_PUMP_PIN, HIGH);
    } else {
        // Dehumidification mode
        digitalWrite(HUMIDIFIER_PIN, LOW);
        analogWrite(DEHUMIDIFIER_PIN, map(-humid_output, 0, 100, 0, 255));
        digitalWrite(WATER_PUMP_PIN, LOW);
    }
    
    // Manage condensate drainage
    if (current_conditions.condensate_level > 80) {
        digitalWrite(DRAIN_VALVE_PIN, HIGH);
    } else if (current_conditions.condensate_level < 20) {
        digitalWrite(DRAIN_VALVE_PIN, LOW);
    }
}

void updateUVControl() {
    // Update PID input
    uv_input = current_conditions.uv_irradiance;
    
    // Compute PID output
    uv_pid.Compute();
    
    // Apply UV control (only if safety interlocks are OK)
    if (uv_safety_ok && !door_open) {
        analogWrite(UV_A_PIN, map(uv_output, 0, 100, 0, 255));
        analogWrite(UV_B_PIN, map(uv_output * 0.4, 0, 100, 0, 255)); // UV-B is 40% of UV-A
    } else {
        analogWrite(UV_A_PIN, 0);
        analogWrite(UV_B_PIN, 0);
    }
}

void startTest() {
    if (!test_state.profile_loaded) {
        displayError("No Profile Loaded");
        return;
    }
    
    if (door_open) {
        displayError("Door Open");
        return;
    }
    
    if (current_conditions.water_level < 10) {
        displayError("Low Water Level");
        return;
    }
    
    // Initialize test state
    test_state.test_running = true;
    test_state.current_step = 0;
    test_state.current_cycle = 0;
    test_state.step_start_time = millis();
    test_state.test_start_time = millis();
    
    // Update targets for first step
    updateStepTargets();
    
    // Create data file
    String filename = "TEST_" + test_state.specimen_id + "_" + 
                     String(millis() / 1000) + ".csv";
    data_file = SD.open(filename, FILE_WRITE);
    if (data_file) {
        writeDataHeader();
    }
    
    // Send test start message
    sendTestStartMessage();
    
    Serial.println(F("Test started"));
}

void endTest() {
    test_state.test_running = false;
    
    // Turn off all outputs
    analogWrite(HEATER_PIN, 0);
    analogWrite(COOLER_PIN, 0);
    analogWrite(PELTIER_HOT_PIN, 0);
    analogWrite(PELTIER_COLD_PIN, 0);
    analogWrite(HUMIDIFIER_PIN, 0);
    analogWrite(DEHUMIDIFIER_PIN, 0);
    analogWrite(UV_A_PIN, 0);
    analogWrite(UV_B_PIN, 0);
    
    // Keep fans running for cooldown
    analogWrite(FAN_INTAKE_PIN, 150);
    analogWrite(FAN_EXHAUST_PIN, 150);
    
    // Close data file
    if (data_file) {
        data_file.close();
    }
    
    // Generate test report
    generateTestReport();
    
    // Send test end message
    sendTestEndMessage();
    
    Serial.println(F("Test completed"));
}

void loadDefaultProfile() {
    // Load a default HALT profile
    current_profile.profile_name = "HALT_Default";
    current_profile.num_steps = 6;
    current_profile.cycle_repeat = true;
    current_profile.cycle_count = 10;
    current_profile.test_standard = "MIL-STD-810G";
    
    // Step 1: Cold temperature
    current_profile.step_temperature[0] = -20.0;
    current_profile.step_humidity[0] = 20.0;
    current_profile.step_uv_irradiance[0] = 0.0;
    current_profile.step_duration[0] = 1800; // 30 minutes
    current_profile.ramp_rate[0] = 5.0;
    
    // Step 2: Cold soak
    current_profile.step_temperature[1] = -20.0;
    current_profile.step_humidity[1] = 20.0;
    current_profile.step_uv_irradiance[1] = 0.0;
    current_profile.step_duration[1] = 3600; // 1 hour
    current_profile.ramp_rate[1] = 0.0;
    
    // Step 3: Transition to hot
    current_profile.step_temperature[2] = 85.0;
    current_profile.step_humidity[2] = 85.0;
    current_profile.step_uv_irradiance[2] = 0.0;
    current_profile.step_duration[2] = 1800; // 30 minutes
    current_profile.ramp_rate[2] = 5.0;
    
    // Step 4: Hot/humid soak
    current_profile.step_temperature[3] = 85.0;
    current_profile.step_humidity[3] = 85.0;
    current_profile.step_uv_irradiance[3] = 0.0;
    current_profile.step_duration[3] = 3600; // 1 hour
    current_profile.ramp_rate[3] = 0.0;
    
    // Step 5: UV exposure
    current_profile.step_temperature[4] = 60.0;
    current_profile.step_humidity[4] = 50.0;
    current_profile.step_uv_irradiance[4] = 500.0;
    current_profile.step_duration[4] = 7200; // 2 hours
    current_profile.ramp_rate[4] = 2.0;
    
    // Step 6: Return to ambient
    current_profile.step_temperature[5] = 25.0;
    current_profile.step_humidity[5] = 50.0;
    current_profile.step_uv_irradiance[5] = 0.0;
    current_profile.step_duration[5] = 1800; // 30 minutes
    current_profile.ramp_rate[5] = 2.0;
    
    test_state.profile_loaded = true;
}

void checkSafetyInterlocks() {
    // Check door interlock
    door_open = digitalRead(DOOR_INTERLOCK_PIN) == HIGH;
    
    // Check UV safety
    uv_safety_ok = digitalRead(UV_INTERLOCK_PIN) == LOW;
    
    // Check over temperature
    over_temperature = digitalRead(OVER_TEMP_PIN) == HIGH;
    
    // Check water overflow
    water_overflow = digitalRead(CONDENSATE_LEVEL_PIN) == HIGH;
    
    // Handle safety violations
    if (door_open && test_state.test_running) {
        // Pause test but don't stop
        analogWrite(UV_A_PIN, 0);
        analogWrite(UV_B_PIN, 0);
        displayWarning("Door Open - UV Disabled");
    }
    
    if (over_temperature) {
        emergency_stop_active = true;
        displayError("Over Temperature");
    }
    
    if (water_overflow) {
        digitalWrite(WATER_PUMP_PIN, LOW);
        digitalWrite(DRAIN_VALVE_PIN, HIGH);
        displayWarning("Water Overflow");
    }
}

void logEnvironmentalData() {
    if (data_file) {
        data_file.print(millis() - test_state.test_start_time);
        data_file.print(",");
        data_file.print(test_state.current_step);
        data_file.print(",");
        data_file.print(test_state.current_cycle);
        data_file.print(",");
        data_file.print(current_conditions.temperature, 2);
        data_file.print(",");
        data_file.print(current_conditions.humidity, 2);
        data_file.print(",");
        data_file.print(current_conditions.uv_irradiance, 2);
        data_file.print(",");
        data_file.print(current_conditions.pressure, 2);
        data_file.print(",");
        data_file.print(current_conditions.dew_point, 2);
        data_file.print(",");
        data_file.print(test_state.target_temperature, 2);
        data_file.print(",");
        data_file.print(test_state.target_humidity, 2);
        data_file.print(",");
        data_file.print(test_state.target_uv_irradiance, 2);
        data_file.print(",");
        data_file.print(temp_output, 2);
        data_file.print(",");
        data_file.print(humid_output, 2);
        data_file.print(",");
        data_file.println(uv_output, 2);
        data_file.flush();
    }
}

void writeDataHeader() {
    if (data_file) {
        data_file.println("# Environmental Test Chamber Data");
        data_file.print("# Profile: ");
        data_file.println(current_profile.profile_name);
        data_file.print("# Specimen ID: ");
        data_file.println(test_state.specimen_id);
        data_file.print("# Test Standard: ");
        data_file.println(current_profile.test_standard);
        data_file.print("# Start Time: ");
        data_file.println(getTimestamp());
        data_file.println("# ");
        data_file.println("Time(ms),Step,Cycle,Temp(C),Humidity(%),UV(W/m2),Pressure(hPa),DewPoint(C),TempTarget(C),HumidTarget(%),UVTarget(W/m2),TempOutput,HumidOutput,UVOutput");
    }
}

void generateTestReport() {
    String report_filename = "REPORT_" + test_state.specimen_id + "_" + 
                           String(millis() / 1000) + ".txt";
    File report_file = SD.open(report_filename, FILE_WRITE);
    
    if (report_file) {
        report_file.println("ENVIRONMENTAL TEST REPORT");
        report_file.println("========================");
        report_file.println();
        report_file.print("Test Date: ");
        report_file.println(getTimestamp());
        report_file.print("Specimen ID: ");
        report_file.println(test_state.specimen_id);
        report_file.print("Test Profile: ");
        report_file.println(current_profile.profile_name);
        report_file.print("Test Standard: ");
        report_file.println(current_profile.test_standard);
        report_file.println();
        
        report_file.println("Test Parameters:");
        report_file.print("  Temperature Range: ");
        report_file.print(MIN_TEMPERATURE);
        report_file.print("°C to ");
        report_file.print(MAX_TEMPERATURE);
        report_file.println("°C");
        report_file.print("  Humidity Range: ");
        report_file.print(MIN_HUMIDITY);
        report_file.print("% to ");
        report_file.print(MAX_HUMIDITY);
        report_file.println("%");
        report_file.print("  UV Irradiance: ");
        report_file.print(MAX_UV_IRRADIANCE);
        report_file.println(" W/m²");
        report_file.println();
        
        report_file.println("Test Results:");
        report_file.print("  Total Cycles: ");
        report_file.println(test_state.current_cycle);
        report_file.print("  Total Steps: ");
        report_file.println(test_state.current_step);
        report_file.print("  Test Duration: ");
        report_file.print((millis() - test_state.test_start_time) / 60000.0);
        report_file.println(" minutes");
        report_file.print("  Final Temperature: ");
        report_file.print(current_conditions.temperature);
        report_file.println("°C");
        report_file.print("  Final Humidity: ");
        report_file.print(current_conditions.humidity);
        report_file.println("%");
        report_file.println();
        
        report_file.println("Compliance: MIL-STD-810G Method 501/502");
        report_file.close();
    }
}

float calculateDewPoint(float temperature, float humidity) {
    // Magnus formula for dew point calculation
    float a = 17.27;
    float b = 237.7;
    float alpha = ((a * temperature) / (b + temperature)) + log(humidity / 100.0);
    float dew_point = (b * alpha) / (a - alpha);
    return dew_point;
}

// Display functions
void displayStartupScreen() {
    tft.fillScr(VGA_BLACK);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_BLACK);
    
    tft.print("ENVIRONMENTAL", CENTER, 50);
    tft.print("TEST CHAMBER", CENTER, 80);
    tft.print("v2.0", CENTER, 110);
    
    tft.setFont(SmallFont);
    tft.print("MIL-STD-810G Compliant", CENTER, 150);
    tft.print("Initializing...", CENTER, 200);
}

void updateDisplay() {
    tft.setFont(BigFont);
    tft.setColor(VGA_WHITE);
    
    // Clear display area
    tft.fillRect(0, 30, 480, 250);
    
    // Display current conditions
    tft.print("Temp: ", 10, 40);
    tft.printNumF(current_conditions.temperature, 1, 100, 40);
    tft.print("C", 180, 40);
    
    tft.print("Humid: ", 10, 70);
    tft.printNumF(current_conditions.humidity, 1, 100, 70);
    tft.print("%", 180, 70);
    
    tft.print("UV: ", 10, 100);
    tft.printNumF(current_conditions.uv_irradiance, 1, 100, 100);
    tft.print("W/m2", 180, 100);
    
    // Display targets if test running
    if (test_state.test_running) {
        tft.print("Target: ", 250, 40);
        tft.printNumF(test_state.target_temperature, 1, 320, 40);
        tft.print("C", 400, 40);
        
        tft.print("Target: ", 250, 70);
        tft.printNumF(test_state.target_humidity, 1, 320, 70);
        tft.print("%", 400, 70);
        
        tft.print("Target: ", 250, 100);
        tft.printNumF(test_state.target_uv_irradiance, 1, 320, 100);
        
        // Display test progress
        tft.print("Step: ", 10, 130);
        tft.printNumI(test_state.current_step + 1, 80, 130);
        tft.print("/", 110, 130);
        tft.printNumI(current_profile.num_steps, 130, 130);
        
        tft.print("Cycle: ", 200, 130);
        tft.printNumI(test_state.current_cycle + 1, 270, 130);
        tft.print("/", 300, 130);
        tft.printNumI(current_profile.cycle_count, 320, 130);
    }
    
    // Display status indicators
    tft.setColor(test_state.test_running ? VGA_GREEN : VGA_RED);
    tft.fillCircle(450, 40, 8);
    
    tft.setColor(door_open ? VGA_RED : VGA_GREEN);
    tft.fillCircle(450, 70, 8);
    
    tft.setColor(uv_safety_ok ? VGA_GREEN : VGA_RED);
    tft.fillCircle(450, 100, 8);
}

void displayError(String message) {
    tft.setColor(VGA_RED);
    tft.fillRect(0, 210, 480, 240);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_RED);
    tft.print(message, CENTER, 220);
    delay(3000);
    tft.setBackColor(VGA_BLACK);
    tft.fillRect(0, 210, 480, 240);
}

void displayWarning(String message) {
    tft.setColor(VGA_YELLOW);
    tft.fillRect(0, 210, 480, 240);
    tft.setColor(VGA_BLACK);
    tft.setBackColor(VGA_YELLOW);
    tft.print(message, CENTER, 220);
    delay(2000);
    tft.setBackColor(VGA_BLACK);
    tft.fillRect(0, 210, 480, 240);
}

// Communication functions
void sendDataToESP32() {
    StaticJsonDocument<512> doc;
    
    doc["type"] = "environmental_data";
    doc["timestamp"] = current_conditions.timestamp;
    doc["temperature"] = current_conditions.temperature;
    doc["humidity"] = current_conditions.humidity;
    doc["uv_irradiance"] = current_conditions.uv_irradiance;
    doc["pressure"] = current_conditions.pressure;
    doc["dew_point"] = current_conditions.dew_point;
    doc["water_level"] = current_conditions.water_level;
    doc["test_running"] = test_state.test_running;
    doc["current_step"] = test_state.current_step;
    doc["current_cycle"] = test_state.current_cycle;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendTestStartMessage() {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "test_start";
    doc["specimen_id"] = test_state.specimen_id;
    doc["profile_name"] = current_profile.profile_name;
    doc["test_standard"] = current_profile.test_standard;
    doc["num_steps"] = current_profile.num_steps;
    doc["cycle_count"] = current_profile.cycle_count;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendTestEndMessage() {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "test_end";
    doc["specimen_id"] = test_state.specimen_id;
    doc["total_cycles"] = test_state.current_cycle;
    doc["total_steps"] = test_state.current_step;
    doc["duration"] = millis() - test_state.test_start_time;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

// Interrupt service routines
void emergencyStopISR() {
    emergency_stop_active = true;
}

void doorInterlockISR() {
    door_open = digitalRead(DOOR_INTERLOCK_PIN) == HIGH;
}

void overTempISR() {
    over_temperature = true;
    emergency_stop_active = true;
}

void handleEmergencyStop() {
    // Turn off all outputs immediately
    analogWrite(HEATER_PIN, 0);
    analogWrite(COOLER_PIN, 0);
    analogWrite(PELTIER_HOT_PIN, 0);
    analogWrite(PELTIER_COLD_PIN, 0);
    analogWrite(HUMIDIFIER_PIN, 0);
    analogWrite(DEHUMIDIFIER_PIN, 0);
    analogWrite(UV_A_PIN, 0);
    analogWrite(UV_B_PIN, 0);
    
    // Keep fans running for safety
    analogWrite(FAN_INTAKE_PIN, 255);
    analogWrite(FAN_EXHAUST_PIN, 255);
    
    // Open drain valve
    digitalWrite(DRAIN_VALVE_PIN, HIGH);
    
    // Display emergency message
    tft.fillScr(VGA_RED);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_RED);
    tft.print("EMERGENCY STOP", CENTER, 100);
    tft.print("System Shutdown", CENTER, 130);
    
    // Stop test
    test_state.test_running = false;
    
    // Wait for reset
    while (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        delay(100);
    }
    
    // Reset flags
    emergency_stop_active = false;
    over_temperature = false;
    
    // Return to normal display
    tft.fillScr(VGA_BLACK);
    displayStartupScreen();
}

void handleTouchInput() {
    int x, y;
    touch.read();
    x = touch.getX();
    y = touch.getY();
    
    // Define button areas
    if (y > 260 && y < 310) {
        if (x > 10 && x < 110) { // Start button
            if (!test_state.test_running) {
                test_state.specimen_id = "SPEC001";
                startTest();
            }
        } else if (x > 130 && x < 230) { // Stop button
            if (test_state.test_running) {
                endTest();
            }
        } else if (x > 250 && x < 350) { // Profile button
            showProfileMenu();
        } else if (x > 370 && x < 470) { // Settings button
            showSettingsMenu();
        }
    }
}

void showProfileMenu() {
    // Display profile selection menu
    tft.fillScr(VGA_BLACK);
    tft.setColor(VGA_WHITE);
    tft.print("SELECT PROFILE", CENTER, 20);
    
    tft.print("1. HALT Standard", 50, 60);
    tft.print("2. HASS Screening", 50, 90);
    tft.print("3. UV Weathering", 50, 120);
    tft.print("4. Thermal Cycling", 50, 150);
    tft.print("5. Custom Profile", 50, 180);
}

void showSettingsMenu() {
    // Display settings menu
    tft.fillScr(VGA_BLACK);
    tft.setColor(VGA_WHITE);
    tft.print("SETTINGS", CENTER, 20);
    
    tft.print("1. PID Parameters", 50, 60);
    tft.print("2. Calibration", 50, 90);
    tft.print("3. Safety Limits", 50, 120);
    tft.print("4. Network Config", 50, 150);
    tft.print("5. System Info", 50, 180);
}

void performSystemCheck() {
    bool system_ok = true;
    
    // Check temperature sensors
    temp_sensors.requestTemperatures();
    float temp1 = temp_sensors.getTempCByIndex(0);
    if (temp1 == DEVICE_DISCONNECTED_C) {
        Serial.println(F("Temperature sensor 1 error"));
        system_ok = false;
    }
    
    // Check humidity sensor
    float humidity = humidity_sensor.readHumidity();
    if (isnan(humidity)) {
        Serial.println(F("Humidity sensor error"));
        system_ok = false;
    }
    
    // Check BME680
    if (!bme680.performReading()) {
        Serial.println(F("BME680 sensor error"));
        system_ok = false;
    }
    
    // Check safety interlocks
    if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        Serial.println(F("Emergency stop active"));
        system_ok = false;
    }
    
    if (!system_ok) {
        displayError("System Check Failed");
    }
}

void processSerialCommand() {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "START") {
        test_state.specimen_id = "SERIAL001";
        startTest();
    } else if (command == "STOP") {
        endTest();
    } else if (command == "STATUS") {
        printStatus();
    } else if (command.startsWith("SPECIMEN")) {
        int space_pos = command.indexOf(' ');
        if (space_pos > 0) {
            test_state.specimen_id = command.substring(space_pos + 1);
        }
    }
}

void processESP32Message() {
    String message = ESP32_SERIAL.readStringUntil('\n');
    StaticJsonDocument<256> doc;
    
    DeserializationError error = deserializeJson(doc, message);
    if (error) {
        return;
    }
    
    String type = doc["type"];
    
    if (type == "command") {
        String cmd = doc["command"];
        if (cmd == "start") {
            test_state.specimen_id = doc["specimen_id"];
            startTest();
        } else if (cmd == "stop") {
            endTest();
        }
    } else if (type == "profile_update") {
        // Load new profile from ESP32
        loadProfileFromESP32(doc);
    }
}

void loadProfileFromESP32(JsonDocument& profile_doc) {
    // Load profile parameters from ESP32
    current_profile.profile_name = profile_doc["name"].as<String>();
    current_profile.num_steps = profile_doc["num_steps"];
    current_profile.cycle_count = profile_doc["cycle_count"];
    current_profile.cycle_repeat = profile_doc["cycle_repeat"];
    
    for (int i = 0; i < current_profile.num_steps; i++) {
        current_profile.step_temperature[i] = profile_doc["steps"][i]["temperature"];
        current_profile.step_humidity[i] = profile_doc["steps"][i]["humidity"];
        current_profile.step_uv_irradiance[i] = profile_doc["steps"][i]["uv_irradiance"];
        current_profile.step_duration[i] = profile_doc["steps"][i]["duration"];
        current_profile.ramp_rate[i] = profile_doc["steps"][i]["ramp_rate"];
    }
    
    test_state.profile_loaded = true;
    Serial.println(F("Profile loaded from ESP32"));
}

void printStatus() {
    Serial.println(F("=== Environmental Test Chamber Status ==="));
    Serial.print(F("Test Running: "));
    Serial.println(test_state.test_running ? "Yes" : "No");
    Serial.print(F("Temperature: "));
    Serial.print(current_conditions.temperature);
    Serial.println(F("°C"));
    Serial.print(F("Humidity: "));
    Serial.print(current_conditions.humidity);
    Serial.println(F("%"));
    Serial.print(F("UV Irradiance: "));
    Serial.print(current_conditions.uv_irradiance);
    Serial.println(F(" W/m²"));
    Serial.print(F("Pressure: "));
    Serial.print(current_conditions.pressure);
    Serial.println(F(" hPa"));
    
    if (test_state.test_running) {
        Serial.print(F("Profile: "));
        Serial.println(current_profile.profile_name);
        Serial.print(F("Step: "));
        Serial.print(test_state.current_step + 1);
        Serial.print(F("/"));
        Serial.println(current_profile.num_steps);
        Serial.print(F("Cycle: "));
        Serial.print(test_state.current_cycle + 1);
        Serial.print(F("/"));
        Serial.println(current_profile.cycle_count);
    }
    
    Serial.println(F("======================================="));
}

String getTimestamp() {
    // In real implementation, use RTC module
    return String(millis() / 1000) + "s";
}