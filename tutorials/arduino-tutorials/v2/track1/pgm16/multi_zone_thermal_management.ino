/*
 * Program 16: Multi-Zone Thermal Management System
 * Arduino Zero to Hero v2.0 - Track 1: Thermal Systems Engineering
 * 
 * Professional battery thermal management system with predictive control
 * - 4-zone independent temperature control
 * - Model predictive control (MPC) algorithm
 * - Cloud-based monitoring dashboard
 * - Thermal runaway protection
 * - Energy optimization
 * 
 * Hardware Requirements:
 * - Arduino Mega 2560
 * - MAX31855 Thermocouple Amplifiers (8x)
 * - Type K Thermocouples (8x)
 * - TEC1-12706 Peltier Modules (8x)
 * - L298N Motor Drivers (4x)
 * - INA219 Current Sensors (4x)
 * - Emergency stop button
 * - Status LEDs (12x)
 * - ESP32 for IoT connectivity
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
#include <PID_v1.h>
#include <MAX31855.h>
#include <Adafruit_INA219.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// System Configuration
#define NUM_ZONES 4
#define NUM_SENSORS_PER_ZONE 2
#define TOTAL_SENSORS (NUM_ZONES * NUM_SENSORS_PER_ZONE)
#define SAMPLE_INTERVAL 1000  // milliseconds
#define PREDICTION_HORIZON 10 // steps
#define CONTROL_HORIZON 5     // steps
#define MAX_TEMPERATURE 85.0  // °C
#define MIN_TEMPERATURE 15.0  // °C
#define MAX_CURRENT 3.0       // A
#define EMERGENCY_STOP_PIN 21

// Pin Assignments
const int TEC_PWM_PINS[] = {2, 4, 6, 8, 10, 12, 14, 16};        // TEC control pins
const int TEC_DIR_PINS[] = {3, 5, 7, 9, 11, 13, 15, 17};        // TEC direction pins
const int STATUS_LED_PINS[] = {22, 24, 26, 28, 30, 32, 34, 36}; // Status LEDs
const int THERMOCOUPLE_CS_PINS[] = {38, 40, 42, 44, 46, 48, 50, 52}; // MAX31855 CS pins
const int SD_CS_PIN = 53;

// Thermal Zone Structure
struct ThermalZone {
    int zone_id;
    float temperature[NUM_SENSORS_PER_ZONE];
    float setpoint;
    float control_output;
    float current;
    float power;
    float thermal_resistance;
    float thermal_capacitance;
    bool safety_fault;
    unsigned long last_update;
    PID pid_controller;
    double pid_input, pid_output, pid_setpoint;
};

// Phase Change Detection
struct PhaseChangeState {
    bool phase_change_detected;
    float melting_point;
    float freezing_point;
    float latent_heat;
    float phase_fraction; // 0=solid, 1=liquid
    float enthalpy;
};

// System State
ThermalZone thermal_zones[NUM_ZONES];
PhaseChangeState phase_states[NUM_ZONES];
MAX31855 thermocouples[TOTAL_SENSORS];
Adafruit_INA219 current_sensors[NUM_ZONES];
bool emergency_stop_active = false;
bool system_initialized = false;
unsigned long last_sample_time = 0;
unsigned long system_start_time = 0;

// PID Parameters
double kp = 2.0, ki = 0.1, kd = 0.5;

// IoT Configuration
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "mqtt.broker.com";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Data Logging
File dataFile;
String log_filename;

// Safety System Class
class SafetySystem {
private:
    bool emergency_stop_triggered;
    bool overtemp_detected;
    bool overcurrent_detected;
    bool communication_fault;
    unsigned long last_communication_time;
    
public:
    SafetySystem() {
        emergency_stop_triggered = false;
        overtemp_detected = false;
        overcurrent_detected = false;
        communication_fault = false;
        last_communication_time = millis();
    }
    
    void initialize() {
        pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
        attachInterrupt(digitalPinToInterrupt(EMERGENCY_STOP_PIN), emergencyStopISR, FALLING);
        
        Serial.println("Safety system initialized");
    }
    
    bool checkSafety() {
        // Check emergency stop
        if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
            triggerEmergencyStop("Emergency stop button pressed");
            return false;
        }
        
        // Check temperature limits
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            for (int sensor = 0; sensor < NUM_SENSORS_PER_ZONE; sensor++) {
                float temp = thermal_zones[zone].temperature[sensor];
                if (temp > MAX_TEMPERATURE) {
                    triggerEmergencyStop("Overtemperature Zone " + String(zone) + " Sensor " + String(sensor));
                    return false;
                }
                if (temp < MIN_TEMPERATURE && temp > -100) { // Valid temperature range
                    triggerEmergencyStop("Undertemperature Zone " + String(zone) + " Sensor " + String(sensor));
                    return false;
                }
            }
        }
        
        // Check current limits
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            if (thermal_zones[zone].current > MAX_CURRENT) {
                triggerEmergencyStop("Overcurrent Zone " + String(zone));
                return false;
            }
        }
        
        // Check communication health
        if (millis() - last_communication_time > 30000) { // 30 second timeout
            triggerEmergencyStop("Communication timeout");
            return false;
        }
        
        return true;
    }
    
    void triggerEmergencyStop(String reason) {
        emergency_stop_triggered = true;
        emergency_stop_active = true;
        
        // Turn off all TECs immediately
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            for (int tec = 0; tec < NUM_SENSORS_PER_ZONE; tec++) {
                int pin_index = zone * NUM_SENSORS_PER_ZONE + tec;
                analogWrite(TEC_PWM_PINS[pin_index], 0);
                digitalWrite(STATUS_LED_PINS[pin_index], HIGH); // Red LED on
            }
        }
        
        // Log emergency event
        logEmergencyEvent(reason);
        
        // Send alert to cloud
        sendEmergencyAlert(reason);
        
        Serial.println("🚨 EMERGENCY STOP: " + reason);
    }
    
    void updateCommunicationTime() {
        last_communication_time = millis();
    }
    
    bool isEmergencyActive() {
        return emergency_stop_active;
    }
    
    void resetEmergencyStop() {
        if (digitalRead(EMERGENCY_STOP_PIN) == HIGH) {
            emergency_stop_triggered = false;
            emergency_stop_active = false;
            Serial.println("Emergency stop reset");
        }
    }
};

// Model Predictive Control Class
class MPCController {
private:
    float prediction_model[NUM_ZONES][PREDICTION_HORIZON];
    float control_sequence[NUM_ZONES][CONTROL_HORIZON];
    float thermal_coupling_matrix[NUM_ZONES][NUM_ZONES];
    
public:
    MPCController() {
        initializeThermalModel();
    }
    
    void initializeThermalModel() {
        // Initialize thermal coupling matrix
        for (int i = 0; i < NUM_ZONES; i++) {
            for (int j = 0; j < NUM_ZONES; j++) {
                if (i == j) {
                    thermal_coupling_matrix[i][j] = 1.0;
                } else {
                    // Adjacent zones have stronger coupling
                    float distance = abs(i - j);
                    thermal_coupling_matrix[i][j] = 0.1 / distance;
                }
            }
        }
    }
    
    void calculateControl() {
        // Predict future temperatures
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            for (int step = 0; step < PREDICTION_HORIZON; step++) {
                prediction_model[zone][step] = predictTemperature(zone, step);
            }
        }
        
        // Optimize control sequence
        optimizeControlSequence();
        
        // Apply first control action
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            applyControl(zone, control_sequence[zone][0]);
        }
    }
    
    float predictTemperature(int zone, int prediction_step) {
        float current_temp = thermal_zones[zone].temperature[0];
        float thermal_resistance = thermal_zones[zone].thermal_resistance;
        float thermal_capacitance = thermal_zones[zone].thermal_capacitance;
        
        // Calculate heat transfer between zones
        float heat_coupling = 0;
        for (int i = 0; i < NUM_ZONES; i++) {
            if (i != zone) {
                float temp_diff = thermal_zones[i].temperature[0] - current_temp;
                heat_coupling += temp_diff * thermal_coupling_matrix[zone][i];
            }
        }
        
        // First-order thermal model
        float power = thermal_zones[zone].power;
        float dT_dt = (power + heat_coupling) / thermal_capacitance;
        
        return current_temp + dT_dt * SAMPLE_INTERVAL / 1000.0 * prediction_step;
    }
    
    void optimizeControlSequence() {
        // Simplified optimization - can be enhanced with proper optimization algorithms
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            float error = thermal_zones[zone].setpoint - thermal_zones[zone].temperature[0];
            
            // Simple predictive control
            for (int step = 0; step < CONTROL_HORIZON; step++) {
                float predicted_error = thermal_zones[zone].setpoint - prediction_model[zone][step];
                control_sequence[zone][step] = constrain(predicted_error * 10.0, -255, 255);
            }
        }
    }
    
    void applyControl(int zone, float control_value) {
        // Apply control to TECs
        for (int tec = 0; tec < NUM_SENSORS_PER_ZONE; tec++) {
            int pin_index = zone * NUM_SENSORS_PER_ZONE + tec;
            
            if (control_value > 0) {
                // Heating mode
                digitalWrite(TEC_DIR_PINS[pin_index], HIGH);
                analogWrite(TEC_PWM_PINS[pin_index], min(255, (int)abs(control_value)));
            } else {
                // Cooling mode
                digitalWrite(TEC_DIR_PINS[pin_index], LOW);
                analogWrite(TEC_PWM_PINS[pin_index], min(255, (int)abs(control_value)));
            }
        }
    }
};

// Phase Change Detection Class
class PhaseChangeDetector {
private:
    float temperature_history[NUM_ZONES][100];
    int history_index[NUM_ZONES];
    
public:
    PhaseChangeDetector() {
        for (int i = 0; i < NUM_ZONES; i++) {
            history_index[i] = 0;
        }
    }
    
    void updateTemperatureHistory(int zone, float temperature) {
        temperature_history[zone][history_index[zone]] = temperature;
        history_index[zone] = (history_index[zone] + 1) % 100;
    }
    
    bool detectPhaseChange(int zone) {
        float current_temp = thermal_zones[zone].temperature[0];
        float temp_gradient = calculateTemperatureGradient(zone);
        float power = thermal_zones[zone].power;
        
        // Phase change detection: temperature plateau with power input
        if (abs(temp_gradient) < 0.1 && power > 5.0) {
            float melting_point = phase_states[zone].melting_point;
            
            if (current_temp > melting_point - 2.0 && current_temp < melting_point + 2.0) {
                if (!phase_states[zone].phase_change_detected) {
                    phase_states[zone].phase_change_detected = true;
                    logPhaseChangeEvent(zone, "MELTING_START", current_temp);
                    return true;
                }
            }
        }
        
        return false;
    }
    
    float calculateTemperatureGradient(int zone) {
        if (history_index[zone] < 10) return 0.0;
        
        float recent_temp = temperature_history[zone][(history_index[zone] - 1 + 100) % 100];
        float older_temp = temperature_history[zone][(history_index[zone] - 10 + 100) % 100];
        
        return (recent_temp - older_temp) / 10.0; // °C per sample
    }
    
    float calculateLatentHeat(int zone) {
        float heat_input = getIntegratedHeatInput(zone);
        float mass = 0.5; // kg - estimated mass
        
        return heat_input / mass; // J/kg
    }
    
    float getIntegratedHeatInput(int zone) {
        // Simplified - integrate power over phase change period
        return thermal_zones[zone].power * 60.0; // J (assuming 1 minute phase change)
    }
};

// IoT Gateway Class
class IoTGateway {
private:
    unsigned long last_publish_time;
    const unsigned long PUBLISH_INTERVAL = 30000; // 30 seconds
    
public:
    IoTGateway() {
        last_publish_time = 0;
    }
    
    void initialize() {
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid, password);
        
        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.print(".");
        }
        
        Serial.println();
        Serial.print("WiFi connected. IP address: ");
        Serial.println(WiFi.localIP());
        
        mqtt_client.setServer(mqtt_server, mqtt_port);
        mqtt_client.setCallback(mqttCallback);
        
        connectToMQTT();
    }
    
    void connectToMQTT() {
        while (!mqtt_client.connected()) {
            Serial.print("Attempting MQTT connection...");
            
            if (mqtt_client.connect("ThermalController")) {
                Serial.println("connected");
                mqtt_client.subscribe("thermal/commands");
            } else {
                Serial.print("failed, rc=");
                Serial.print(mqtt_client.state());
                Serial.println(" try again in 5 seconds");
                delay(5000);
            }
        }
    }
    
    void publishData() {
        if (millis() - last_publish_time < PUBLISH_INTERVAL) return;
        
        if (!mqtt_client.connected()) {
            connectToMQTT();
        }
        
        // Create JSON payload
        StaticJsonDocument<1024> doc;
        doc["timestamp"] = millis();
        doc["system_status"] = emergency_stop_active ? "EMERGENCY" : "NORMAL";
        doc["uptime"] = millis() - system_start_time;
        
        JsonArray zones = doc.createNestedArray("zones");
        for (int i = 0; i < NUM_ZONES; i++) {
            JsonObject zone = zones.createNestedObject();
            zone["id"] = i;
            zone["temperature"] = thermal_zones[i].temperature[0];
            zone["setpoint"] = thermal_zones[i].setpoint;
            zone["power"] = thermal_zones[i].power;
            zone["current"] = thermal_zones[i].current;
            zone["phase_change"] = phase_states[i].phase_change_detected;
            zone["phase_fraction"] = phase_states[i].phase_fraction;
        }
        
        // Publish to MQTT
        String payload;
        serializeJson(doc, payload);
        mqtt_client.publish("thermal/data", payload.c_str());
        
        last_publish_time = millis();
    }
    
    void handleCommands() {
        if (mqtt_client.connected()) {
            mqtt_client.loop();
        }
    }
    
    static void mqttCallback(char* topic, byte* payload, unsigned int length) {
        String command = "";
        for (int i = 0; i < length; i++) {
            command += (char)payload[i];
        }
        
        Serial.println("Received command: " + command);
        
        // Parse and execute commands
        StaticJsonDocument<256> doc;
        deserializeJson(doc, command);
        
        if (doc["action"] == "set_setpoint") {
            int zone = doc["zone"];
            float setpoint = doc["setpoint"];
            if (zone >= 0 && zone < NUM_ZONES) {
                thermal_zones[zone].setpoint = setpoint;
                Serial.println("Set zone " + String(zone) + " setpoint to " + String(setpoint));
            }
        }
    }
};

// Global objects
SafetySystem safety_system;
MPCController mpc_controller;
PhaseChangeDetector phase_detector;
IoTGateway iot_gateway;

// Interrupt Service Routine
void emergencyStopISR() {
    emergency_stop_active = true;
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("🌡️ MULTI-ZONE THERMAL MANAGEMENT SYSTEM STARTED!");
    Serial.println("🌡️ THERMAL SYSTEMS ENGINEER MODE - Design advanced thermal control!");
    Serial.println("Professional battery thermal management with predictive control");
    Serial.println("================================================================");
    
    // Initialize system
    system_start_time = millis();
    
    // Initialize hardware
    initializeHardware();
    
    // Initialize safety system
    safety_system.initialize();
    
    // Initialize IoT gateway
    iot_gateway.initialize();
    
    // Initialize data logging
    initializeDataLogging();
    
    // Initialize thermal zones
    initializeThermalZones();
    
    // Initialize phase change detection
    initializePhaseChangeDetection();
    
    Serial.println("🎯 System Ready for Operation");
    system_initialized = true;
}

void loop() {
    if (!system_initialized) return;
    
    // Safety check first
    if (!safety_system.checkSafety()) {
        handleEmergencyState();
        return;
    }
    
    // Sample at regular intervals
    if (millis() - last_sample_time >= SAMPLE_INTERVAL) {
        // Update sensor readings
        updateSensorReadings();
        
        // Update phase change detection
        updatePhaseChangeDetection();
        
        // Run MPC control
        mpc_controller.calculateControl();
        
        // Update status display
        updateStatusDisplay();
        
        // Log data
        logData();
        
        // Update IoT
        iot_gateway.publishData();
        iot_gateway.handleCommands();
        
        last_sample_time = millis();
    }
    
    // Handle commands
    handleSerialCommands();
    
    delay(100);
}

void initializeHardware() {
    Serial.println("🔧 Initializing Hardware...");
    
    // Initialize thermocouple interfaces
    for (int i = 0; i < TOTAL_SENSORS; i++) {
        thermocouples[i].begin(THERMOCOUPLE_CS_PINS[i]);
    }
    
    // Initialize current sensors
    for (int i = 0; i < NUM_ZONES; i++) {
        current_sensors[i].begin();
        current_sensors[i].setCalibration_32V_2A(); // 32V, 2A range
    }
    
    // Initialize PWM pins
    for (int i = 0; i < TOTAL_SENSORS; i++) {
        pinMode(TEC_PWM_PINS[i], OUTPUT);
        pinMode(TEC_DIR_PINS[i], OUTPUT);
        pinMode(STATUS_LED_PINS[i], OUTPUT);
        
        // Start with TECs off
        analogWrite(TEC_PWM_PINS[i], 0);
        digitalWrite(TEC_DIR_PINS[i], LOW);
        digitalWrite(STATUS_LED_PINS[i], LOW);
    }
    
    // Initialize SD card
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("SD card initialization failed!");
    } else {
        Serial.println("✅ SD card initialized");
    }
    
    Serial.println("✅ Hardware initialization complete");
}

void initializeThermalZones() {
    Serial.println("🔥 Initializing Thermal Zones...");
    
    for (int i = 0; i < NUM_ZONES; i++) {
        thermal_zones[i].zone_id = i;
        thermal_zones[i].setpoint = 25.0; // Default setpoint
        thermal_zones[i].control_output = 0.0;
        thermal_zones[i].current = 0.0;
        thermal_zones[i].power = 0.0;
        thermal_zones[i].thermal_resistance = 1.5; // °C/W
        thermal_zones[i].thermal_capacitance = 100.0; // J/°C
        thermal_zones[i].safety_fault = false;
        thermal_zones[i].last_update = 0;
        
        // Initialize PID controller
        thermal_zones[i].pid_controller = PID(&thermal_zones[i].pid_input, 
                                              &thermal_zones[i].pid_output, 
                                              &thermal_zones[i].pid_setpoint, 
                                              kp, ki, kd, DIRECT);
        thermal_zones[i].pid_controller.SetMode(AUTOMATIC);
        thermal_zones[i].pid_controller.SetOutputLimits(-255, 255);
        
        Serial.println("✅ Zone " + String(i) + " initialized");
    }
}

void initializePhaseChangeDetection() {
    Serial.println("🔄 Initializing Phase Change Detection...");
    
    for (int i = 0; i < NUM_ZONES; i++) {
        phase_states[i].phase_change_detected = false;
        phase_states[i].melting_point = 60.0; // Default melting point
        phase_states[i].freezing_point = 55.0; // Default freezing point
        phase_states[i].latent_heat = 200.0; // J/g
        phase_states[i].phase_fraction = 0.0; // Start solid
        phase_states[i].enthalpy = 0.0;
    }
    
    Serial.println("✅ Phase change detection initialized");
}

void initializeDataLogging() {
    log_filename = "thermal_" + String(millis()) + ".csv";
    
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        // Write header
        dataFile.println("timestamp,zone,temp1,temp2,setpoint,power,current,phase_change,phase_fraction");
        dataFile.close();
        Serial.println("✅ Data logging initialized: " + log_filename);
    }
}

void updateSensorReadings() {
    for (int zone = 0; zone < NUM_ZONES; zone++) {
        // Read thermocouples
        for (int sensor = 0; sensor < NUM_SENSORS_PER_ZONE; sensor++) {
            int sensor_index = zone * NUM_SENSORS_PER_ZONE + sensor;
            thermal_zones[zone].temperature[sensor] = thermocouples[sensor_index].readCelsius();
            
            // Check for sensor errors
            if (isnan(thermal_zones[zone].temperature[sensor])) {
                thermal_zones[zone].temperature[sensor] = -999.0; // Error value
                thermal_zones[zone].safety_fault = true;
            }
        }
        
        // Read current and calculate power
        thermal_zones[zone].current = current_sensors[zone].getCurrent_mA() / 1000.0;
        float voltage = current_sensors[zone].getBusVoltage_V();
        thermal_zones[zone].power = voltage * thermal_zones[zone].current;
        
        // Update PID inputs
        thermal_zones[zone].pid_input = thermal_zones[zone].temperature[0];
        thermal_zones[zone].pid_setpoint = thermal_zones[zone].setpoint;
        
        // Calculate PID output
        thermal_zones[zone].pid_controller.Compute();
        thermal_zones[zone].control_output = thermal_zones[zone].pid_output;
        
        thermal_zones[zone].last_update = millis();
        
        // Update phase change detector
        phase_detector.updateTemperatureHistory(zone, thermal_zones[zone].temperature[0]);
    }
}

void updatePhaseChangeDetection() {
    for (int zone = 0; zone < NUM_ZONES; zone++) {
        if (phase_detector.detectPhaseChange(zone)) {
            Serial.println("🔄 Phase change detected in zone " + String(zone));
            
            // Update phase fraction based on temperature and power
            updatePhaseFraction(zone);
        }
    }
}

void updatePhaseFraction(int zone) {
    float temp = thermal_zones[zone].temperature[0];
    float melting_point = phase_states[zone].melting_point;
    float freezing_point = phase_states[zone].freezing_point;
    
    if (temp > melting_point) {
        phase_states[zone].phase_fraction = 1.0; // Fully liquid
    } else if (temp < freezing_point) {
        phase_states[zone].phase_fraction = 0.0; // Fully solid
    } else {
        // Mixed phase - linear interpolation
        phase_states[zone].phase_fraction = (temp - freezing_point) / (melting_point - freezing_point);
    }
    
    // Update enthalpy
    float sensible_heat = thermal_zones[zone].temperature[0] * 2.0; // Assuming 2 J/g/K specific heat
    float latent_contribution = phase_states[zone].phase_fraction * phase_states[zone].latent_heat;
    phase_states[zone].enthalpy = sensible_heat + latent_contribution;
}

void updateStatusDisplay() {
    static unsigned long last_display_time = 0;
    
    if (millis() - last_display_time > 5000) { // Every 5 seconds
        Serial.println("=== THERMAL SYSTEM STATUS ===");
        Serial.print("Time: ");
        Serial.print((millis() - system_start_time) / 1000);
        Serial.print("s | Mode: ");
        Serial.print(emergency_stop_active ? "EMERGENCY" : "NORMAL");
        Serial.print(" | Total Power: ");
        
        float total_power = 0;
        for (int i = 0; i < NUM_ZONES; i++) {
            total_power += thermal_zones[i].power;
        }
        Serial.print(total_power);
        Serial.println("W");
        
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            Serial.print("Zone ");
            Serial.print(zone);
            Serial.print(": ");
            Serial.print(thermal_zones[zone].temperature[0]);
            Serial.print("°C → ");
            Serial.print(thermal_zones[zone].setpoint);
            Serial.print("°C | ");
            Serial.print(thermal_zones[zone].current);
            Serial.print("A | PID: ");
            Serial.print(thermal_zones[zone].control_output);
            Serial.print("% | Phase: ");
            Serial.print(phase_states[zone].phase_fraction * 100);
            Serial.println("%");
        }
        
        Serial.println("🌐 IoT Status: " + String(mqtt_client.connected() ? "Connected" : "Disconnected"));
        Serial.println();
        
        last_display_time = millis();
    }
}

void logData() {
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        for (int zone = 0; zone < NUM_ZONES; zone++) {
            dataFile.print(millis());
            dataFile.print(",");
            dataFile.print(zone);
            dataFile.print(",");
            dataFile.print(thermal_zones[zone].temperature[0]);
            dataFile.print(",");
            dataFile.print(thermal_zones[zone].temperature[1]);
            dataFile.print(",");
            dataFile.print(thermal_zones[zone].setpoint);
            dataFile.print(",");
            dataFile.print(thermal_zones[zone].power);
            dataFile.print(",");
            dataFile.print(thermal_zones[zone].current);
            dataFile.print(",");
            dataFile.print(phase_states[zone].phase_change_detected ? 1 : 0);
            dataFile.print(",");
            dataFile.println(phase_states[zone].phase_fraction);
        }
        dataFile.close();
    }
}

void handleEmergencyState() {
    // Flash all LEDs
    static bool led_state = false;
    static unsigned long last_flash_time = 0;
    
    if (millis() - last_flash_time > 500) {
        led_state = !led_state;
        for (int i = 0; i < TOTAL_SENSORS; i++) {
            digitalWrite(STATUS_LED_PINS[i], led_state);
        }
        last_flash_time = millis();
    }
    
    // Check for emergency reset
    if (digitalRead(EMERGENCY_STOP_PIN) == HIGH) {
        safety_system.resetEmergencyStop();
    }
}

void handleSerialCommands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command.startsWith("SET_SETPOINT")) {
            // Format: SET_SETPOINT zone temperature
            int zone = command.substring(13, 14).toInt();
            float temperature = command.substring(15).toFloat();
            
            if (zone >= 0 && zone < NUM_ZONES) {
                thermal_zones[zone].setpoint = temperature;
                Serial.println("Set zone " + String(zone) + " setpoint to " + String(temperature) + "°C");
            }
        }
        else if (command == "STATUS") {
            updateStatusDisplay();
        }
        else if (command == "RESET_EMERGENCY") {
            safety_system.resetEmergencyStop();
        }
        else if (command == "HELP") {
            Serial.println("Available commands:");
            Serial.println("SET_SETPOINT <zone> <temperature>");
            Serial.println("STATUS");
            Serial.println("RESET_EMERGENCY");
            Serial.println("HELP");
        }
    }
}

void logEmergencyEvent(String reason) {
    dataFile = SD.open("emergency_log.txt", FILE_WRITE);
    if (dataFile) {
        dataFile.print(millis());
        dataFile.print(",");
        dataFile.println(reason);
        dataFile.close();
    }
}

void logPhaseChangeEvent(int zone, String event, float temperature) {
    dataFile = SD.open("phase_change_log.txt", FILE_WRITE);
    if (dataFile) {
        dataFile.print(millis());
        dataFile.print(",");
        dataFile.print(zone);
        dataFile.print(",");
        dataFile.print(event);
        dataFile.print(",");
        dataFile.println(temperature);
        dataFile.close();
    }
}

void sendEmergencyAlert(String reason) {
    if (mqtt_client.connected()) {
        StaticJsonDocument<256> doc;
        doc["alert"] = "EMERGENCY";
        doc["reason"] = reason;
        doc["timestamp"] = millis();
        doc["zone"] = "ALL";
        
        String payload;
        serializeJson(doc, payload);
        mqtt_client.publish("thermal/alerts", payload.c_str());
    }
}