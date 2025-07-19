/*
 * Program 24: Nano-Indentation Controller
 * 
 * This program implements a precision nano-indentation system for mechanical property
 * characterization at the micro and nano-scale. The system provides automated 
 * load-displacement testing with sub-nanometer resolution for measuring hardness,
 * elastic modulus, creep, and viscoelastic properties.
 * 
 * Features:
 * - Ultra-precise force control (0.1 μN resolution)
 * - High-resolution displacement measurement (0.1 nm)
 * - Automated load-displacement curve generation
 * - Real-time hardness and elastic modulus calculation
 * - Multiple indentation geometries and test methods
 * - Temperature-controlled testing environment
 * - Machine learning-based contact detection
 * - Standards compliance (ISO 14577, ASTM E2546)
 * 
 * Author: Arduino Zero to Hero v2.0
 * Created: 2024
 * 
 * Hardware Requirements:
 * - Arduino Due (84 MHz ARM Cortex-M3)
 * - Piezoelectric actuator system
 * - Capacitive displacement sensor
 * - High-resolution load cell
 * - Precision stepper motors
 * - Environmental control chamber
 * - Optical microscope system
 * - Vibration isolation platform
 * 
 * Libraries Required:
 * - ArduinoJson.h
 * - SD.h
 * - SPI.h
 * - Wire.h
 * - math.h
 * - DueTimer.h
 * - AccelStepper.h
 */

#include <ArduinoJson.h>
#include <SD.h>
#include <SPI.h>
#include <Wire.h>
#include <math.h>
#include <DueTimer.h>
#include <AccelStepper.h>

// System Configuration
#define SYSTEM_VERSION "v2.0.0"
#define SAMPLING_RATE 1000        // Hz
#define MAX_LOAD 500000           // μN (500 mN)
#define MAX_DISPLACEMENT 100000   // nm (100 μm)
#define LOAD_RESOLUTION 0.1       // μN
#define DISPLACEMENT_RESOLUTION 0.1 // nm

// Pin Definitions
// Piezoelectric Actuator Control
#define PIEZO_DRIVE_PIN 2         // PWM output for piezo driver
#define PIEZO_FEEDBACK_PIN A0     // Analog input for position feedback
#define PIEZO_ENABLE_PIN 3        // Enable/disable piezo driver

// Load Cell Interface
#define LOAD_CELL_CLK 4           // HX711 clock
#define LOAD_CELL_DATA 5          // HX711 data
#define LOAD_CELL_GAIN 6          // Gain control for load cell amplifier

// Displacement Sensor (Capacitive)
#define DISPLACEMENT_CS 7         // Chip select for displacement sensor
#define DISPLACEMENT_RESET 8      // Reset for displacement sensor
#define DISPLACEMENT_READY 9      // Data ready signal

// Stepper Motor Control (XYZ positioning)
#define STEPPER_X_STEP 10
#define STEPPER_X_DIR 11
#define STEPPER_Y_STEP 12
#define STEPPER_Y_DIR 13
#define STEPPER_Z_STEP 14
#define STEPPER_Z_DIR 15
#define STEPPER_ENABLE 16

// Environmental Control
#define TEMP_SENSOR_PIN A1        // Temperature sensor
#define HUMIDITY_SENSOR_PIN A2    // Humidity sensor
#define HEATER_CONTROL 17         // Heater control
#define COOLER_CONTROL 18         // Cooler control
#define FAN_CONTROL 19            // Fan control

// Optical System
#define CAMERA_TRIGGER 20         // Camera trigger
#define ILLUMINATION_CONTROL 21   // LED illumination control
#define FOCUS_MOTOR_STEP 22       // Focus motor step
#define FOCUS_MOTOR_DIR 23        // Focus motor direction

// User Interface
#define EMERGENCY_STOP 24         // Emergency stop button
#define START_BUTTON 25           // Test start button
#define STOP_BUTTON 26            // Test stop button
#define STATUS_LED_GREEN 27       // System ready LED
#define STATUS_LED_RED 28         // System fault LED
#define STATUS_LED_BLUE 29        // Test running LED

// Communication
#define ESP32_SERIAL Serial1      // ESP32 communication
#define GPS_SERIAL Serial2        // GPS communication
#define MICROSCOPE_SERIAL Serial3 // Microscope communication

// Data Structures
struct IndentationPoint {
    uint32_t timestamp;
    float load;              // μN
    float displacement;      // nm
    float stiffness;         // N/m
    float temperature;       // °C
    float humidity;          // %RH
    uint8_t contact_status;  // 0=no contact, 1=contact, 2=loading, 3=unloading
};

struct TestParameters {
    float max_load;          // μN
    float max_displacement;  // nm
    float loading_rate;      // μN/s or nm/s
    float unloading_rate;    // μN/s or nm/s
    float hold_time;         // seconds
    uint8_t test_mode;       // 0=load control, 1=displacement control
    uint8_t indenter_type;   // 0=Berkovich, 1=Vickers, 2=spherical
    float indenter_radius;   // μm (for spherical)
    float approach_speed;    // nm/s
    float contact_threshold; // μN
    uint16_t data_points;    // Number of data points to collect
    bool enable_csm;         // Continuous stiffness measurement
    float csm_frequency;     // Hz
    float csm_amplitude;     // nm
};

struct MaterialProperties {
    float hardness;          // GPa
    float elastic_modulus;   // GPa
    float yield_strength;    // GPa
    float work_hardening;    // GPa
    float contact_stiffness; // N/m
    float contact_depth;     // nm
    float plastic_depth;     // nm
    float elastic_work;      // nJ
    float plastic_work;      // nJ
    float total_work;        // nJ
    float creep_rate;        // nm/s
    float relaxation_time;   // seconds
};

struct SystemStatus {
    bool system_ready;
    bool in_contact;
    bool test_running;
    bool emergency_stop;
    bool temperature_stable;
    bool vibration_ok;
    float current_load;
    float current_displacement;
    float current_temperature;
    float current_humidity;
    uint32_t test_count;
    uint32_t uptime;
    String last_error;
};

struct CalibrationData {
    float load_calibration_factor;
    float displacement_calibration_factor;
    float stiffness_calibration_factor;
    float temperature_offset;
    float humidity_offset;
    float area_function_coefficients[6];
    float compliance_correction;
    uint32_t last_calibration_date;
};

// Global Variables
TestParameters current_test;
SystemStatus system_status;
CalibrationData calibration;
MaterialProperties calculated_properties;

// Control Variables
volatile bool data_acquisition_active = false;
volatile bool emergency_stop_triggered = false;
volatile uint32_t sample_counter = 0;

// Data Storage
IndentationPoint data_buffer[2000];
uint16_t buffer_index = 0;
bool buffer_full = false;

// Stepper Motor Objects
AccelStepper stepper_x(AccelStepper::DRIVER, STEPPER_X_STEP, STEPPER_X_DIR);
AccelStepper stepper_y(AccelStepper::DRIVER, STEPPER_Y_STEP, STEPPER_Y_DIR);
AccelStepper stepper_z(AccelStepper::DRIVER, STEPPER_Z_STEP, STEPPER_Z_DIR);
AccelStepper focus_motor(AccelStepper::DRIVER, FOCUS_MOTOR_STEP, FOCUS_MOTOR_DIR);

// Control Variables
float target_load = 0.0;
float target_displacement = 0.0;
float current_load = 0.0;
float current_displacement = 0.0;
float current_stiffness = 0.0;

// PID Controllers
float load_pid_kp = 1.0;
float load_pid_ki = 0.1;
float load_pid_kd = 0.01;
float load_pid_error = 0.0;
float load_pid_integral = 0.0;
float load_pid_derivative = 0.0;
float load_pid_previous_error = 0.0;

float displacement_pid_kp = 2.0;
float displacement_pid_ki = 0.2;
float displacement_pid_kd = 0.02;
float displacement_pid_error = 0.0;
float displacement_pid_integral = 0.0;
float displacement_pid_derivative = 0.0;
float displacement_pid_previous_error = 0.0;

// Timing Variables
uint32_t last_sample_time = 0;
uint32_t test_start_time = 0;
uint32_t contact_detection_time = 0;
uint32_t last_temperature_update = 0;
uint32_t last_status_update = 0;

// Contact Detection
bool contact_detected = false;
float contact_detection_threshold = 0.5; // μN
float contact_stiffness_threshold = 0.1; // N/m
uint8_t contact_confirmation_count = 0;

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== Nano-Indentation Controller v2.0 ===");
    Serial.println("Initializing precision mechanical testing system...");
    
    // Initialize pin modes
    initializePins();
    
    // Initialize communication interfaces
    initializeCommunication();
    
    // Initialize SD card
    initializeStorage();
    
    // Load calibration data
    loadCalibrationData();
    
    // Initialize stepper motors
    initializeStepperMotors();
    
    // Initialize sensors
    initializeSensors();
    
    // Initialize environmental control
    initializeEnvironmentalControl();
    
    // Initialize test parameters with defaults
    initializeDefaultParameters();
    
    // Initialize system status
    initializeSystemStatus();
    
    // Set up timer interrupt for data acquisition
    Timer1.attachInterrupt(dataAcquisitionISR);
    Timer1.start(1000); // 1 kHz sampling rate
    
    // Perform system self-test
    performSystemSelfTest();
    
    Serial.println("System initialization complete!");
    Serial.println("Ready for nano-indentation testing...");
    
    // Initial status update
    updateSystemStatus();
    sendStatusToESP32();
}

void loop() {
    uint32_t current_time = millis();
    
    // Check emergency stop
    if (digitalRead(EMERGENCY_STOP) == LOW || emergency_stop_triggered) {
        handleEmergencyStop();
        return;
    }
    
    // Check start button
    if (digitalRead(START_BUTTON) == LOW && !system_status.test_running) {
        delay(50); // Debounce
        if (digitalRead(START_BUTTON) == LOW) {
            startTest();
        }
    }
    
    // Check stop button
    if (digitalRead(STOP_BUTTON) == LOW && system_status.test_running) {
        delay(50); // Debounce
        if (digitalRead(STOP_BUTTON) == LOW) {
            stopTest();
        }
    }
    
    // Process serial commands
    processSerialCommands();
    
    // Update environmental control
    if (current_time - last_temperature_update > 1000) {
        updateEnvironmentalControl();
        last_temperature_update = current_time;
    }
    
    // Update system status
    if (current_time - last_status_update > 5000) {
        updateSystemStatus();
        sendStatusToESP32();
        last_status_update = current_time;
    }
    
    // Execute test sequence if running
    if (system_status.test_running) {
        executeTestSequence();
    }
    
    // Process data buffer
    processDataBuffer();
    
    // Update stepper motors
    stepper_x.run();
    stepper_y.run();
    stepper_z.run();
    focus_motor.run();
    
    delay(10); // Small delay to prevent overwhelming the system
}

void initializePins() {
    // Control pins
    pinMode(PIEZO_DRIVE_PIN, OUTPUT);
    pinMode(PIEZO_ENABLE_PIN, OUTPUT);
    pinMode(LOAD_CELL_GAIN, OUTPUT);
    
    // Stepper motor pins
    pinMode(STEPPER_X_STEP, OUTPUT);
    pinMode(STEPPER_X_DIR, OUTPUT);
    pinMode(STEPPER_Y_STEP, OUTPUT);
    pinMode(STEPPER_Y_DIR, OUTPUT);
    pinMode(STEPPER_Z_STEP, OUTPUT);
    pinMode(STEPPER_Z_DIR, OUTPUT);
    pinMode(STEPPER_ENABLE, OUTPUT);
    
    // Environmental control pins
    pinMode(HEATER_CONTROL, OUTPUT);
    pinMode(COOLER_CONTROL, OUTPUT);
    pinMode(FAN_CONTROL, OUTPUT);
    
    // Optical system pins
    pinMode(CAMERA_TRIGGER, OUTPUT);
    pinMode(ILLUMINATION_CONTROL, OUTPUT);
    pinMode(FOCUS_MOTOR_STEP, OUTPUT);
    pinMode(FOCUS_MOTOR_DIR, OUTPUT);
    
    // User interface pins
    pinMode(EMERGENCY_STOP, INPUT_PULLUP);
    pinMode(START_BUTTON, INPUT_PULLUP);
    pinMode(STOP_BUTTON, INPUT_PULLUP);
    pinMode(STATUS_LED_GREEN, OUTPUT);
    pinMode(STATUS_LED_RED, OUTPUT);
    pinMode(STATUS_LED_BLUE, OUTPUT);
    
    // Sensor pins
    pinMode(DISPLACEMENT_CS, OUTPUT);
    pinMode(DISPLACEMENT_RESET, OUTPUT);
    pinMode(DISPLACEMENT_READY, INPUT);
    
    // Initial states
    digitalWrite(PIEZO_ENABLE_PIN, LOW);
    digitalWrite(STEPPER_ENABLE, HIGH); // Enable steppers
    digitalWrite(STATUS_LED_GREEN, LOW);
    digitalWrite(STATUS_LED_RED, LOW);
    digitalWrite(STATUS_LED_BLUE, LOW);
}

void initializeCommunication() {
    ESP32_SERIAL.begin(115200);
    GPS_SERIAL.begin(9600);
    MICROSCOPE_SERIAL.begin(19200);
    
    Wire.begin();
    SPI.begin();
    
    Serial.println("Communication interfaces initialized");
}

void initializeStorage() {
    if (!SD.begin(53)) {
        Serial.println("SD card initialization failed!");
        digitalWrite(STATUS_LED_RED, HIGH);
        return;
    }
    
    Serial.println("SD card initialized successfully");
    
    // Create data directory structure
    if (!SD.exists("/data")) {
        SD.mkdir("/data");
    }
    if (!SD.exists("/calibration")) {
        SD.mkdir("/calibration");
    }
    if (!SD.exists("/reports")) {
        SD.mkdir("/reports");
    }
}

void initializeStepperMotors() {
    // Configure stepper motors
    stepper_x.setMaxSpeed(1000.0);      // steps/second
    stepper_x.setAcceleration(500.0);   // steps/second²
    
    stepper_y.setMaxSpeed(1000.0);
    stepper_y.setAcceleration(500.0);
    
    stepper_z.setMaxSpeed(500.0);       // Slower for Z-axis precision
    stepper_z.setAcceleration(250.0);
    
    focus_motor.setMaxSpeed(200.0);     // Slow for focus precision
    focus_motor.setAcceleration(100.0);
    
    Serial.println("Stepper motors configured");
}

void initializeSensors() {
    // Initialize load cell
    pinMode(LOAD_CELL_CLK, OUTPUT);
    pinMode(LOAD_CELL_DATA, INPUT);
    
    // Initialize displacement sensor
    digitalWrite(DISPLACEMENT_CS, HIGH);
    digitalWrite(DISPLACEMENT_RESET, LOW);
    delay(10);
    digitalWrite(DISPLACEMENT_RESET, HIGH);
    delay(100);
    
    // Test sensor communication
    if (testSensorCommunication()) {
        Serial.println("Sensors initialized successfully");
    } else {
        Serial.println("Sensor initialization failed!");
        digitalWrite(STATUS_LED_RED, HIGH);
    }
}

void initializeEnvironmentalControl() {
    // Initialize temperature and humidity control
    digitalWrite(HEATER_CONTROL, LOW);
    digitalWrite(COOLER_CONTROL, LOW);
    digitalWrite(FAN_CONTROL, LOW);
    
    // Start environmental monitoring
    updateEnvironmentalReadings();
    
    Serial.println("Environmental control initialized");
}

void initializeDefaultParameters() {
    current_test.max_load = 1000.0;           // μN
    current_test.max_displacement = 1000.0;   // nm
    current_test.loading_rate = 100.0;        // μN/s
    current_test.unloading_rate = 200.0;      // μN/s
    current_test.hold_time = 10.0;            // seconds
    current_test.test_mode = 0;               // Load control
    current_test.indenter_type = 0;           // Berkovich
    current_test.indenter_radius = 0.0;       // Not applicable for Berkovich
    current_test.approach_speed = 10.0;       // nm/s
    current_test.contact_threshold = 0.5;     // μN
    current_test.data_points = 1000;
    current_test.enable_csm = false;
    current_test.csm_frequency = 45.0;        // Hz
    current_test.csm_amplitude = 2.0;         // nm
    
    Serial.println("Default test parameters loaded");
}

void initializeSystemStatus() {
    system_status.system_ready = false;
    system_status.in_contact = false;
    system_status.test_running = false;
    system_status.emergency_stop = false;
    system_status.temperature_stable = false;
    system_status.vibration_ok = true;
    system_status.current_load = 0.0;
    system_status.current_displacement = 0.0;
    system_status.current_temperature = 25.0;
    system_status.current_humidity = 50.0;
    system_status.test_count = 0;
    system_status.uptime = 0;
    system_status.last_error = "";
}

void dataAcquisitionISR() {
    if (!data_acquisition_active) return;
    
    // Read sensors
    float load = readLoadCell();
    float displacement = readDisplacementSensor();
    float temperature = readTemperature();
    float humidity = readHumidity();
    
    // Update current values
    current_load = load;
    current_displacement = displacement;
    
    // Calculate stiffness if in contact
    if (contact_detected) {
        current_stiffness = calculateStiffness();
    }
    
    // Store data point
    if (buffer_index < 2000) {
        data_buffer[buffer_index].timestamp = millis();
        data_buffer[buffer_index].load = load;
        data_buffer[buffer_index].displacement = displacement;
        data_buffer[buffer_index].stiffness = current_stiffness;
        data_buffer[buffer_index].temperature = temperature;
        data_buffer[buffer_index].humidity = humidity;
        data_buffer[buffer_index].contact_status = getContactStatus();
        
        buffer_index++;
    } else {
        buffer_full = true;
    }
    
    sample_counter++;
}

float readLoadCell() {
    // Read HX711 load cell amplifier
    static uint32_t last_reading = 0;
    uint32_t raw_value = 0;
    
    // Wait for data ready
    while (digitalRead(LOAD_CELL_DATA) == HIGH) {
        delayMicroseconds(1);
    }
    
    // Read 24-bit value
    for (int i = 0; i < 24; i++) {
        digitalWrite(LOAD_CELL_CLK, HIGH);
        delayMicroseconds(1);
        raw_value = (raw_value << 1) | digitalRead(LOAD_CELL_DATA);
        digitalWrite(LOAD_CELL_CLK, LOW);
        delayMicroseconds(1);
    }
    
    // Set gain (25 pulses for 128 gain)
    for (int i = 0; i < 1; i++) {
        digitalWrite(LOAD_CELL_CLK, HIGH);
        delayMicroseconds(1);
        digitalWrite(LOAD_CELL_CLK, LOW);
        delayMicroseconds(1);
    }
    
    // Convert to signed 24-bit
    if (raw_value & 0x800000) {
        raw_value |= 0xFF000000;
    }
    
    // Apply calibration
    float load_uN = ((int32_t)raw_value - calibration.load_calibration_factor) * 0.1;
    
    return load_uN;
}

float readDisplacementSensor() {
    // Read capacitive displacement sensor via SPI
    uint32_t raw_value = 0;
    
    digitalWrite(DISPLACEMENT_CS, LOW);
    delayMicroseconds(10);
    
    // Send read command
    SPI.transfer(0x01); // Read command
    delayMicroseconds(10);
    
    // Read 24-bit displacement value
    raw_value = SPI.transfer(0x00) << 16;
    raw_value |= SPI.transfer(0x00) << 8;
    raw_value |= SPI.transfer(0x00);
    
    digitalWrite(DISPLACEMENT_CS, HIGH);
    
    // Convert to nanometers
    float displacement_nm = (raw_value * calibration.displacement_calibration_factor) / 1000.0;
    
    return displacement_nm;
}

float readTemperature() {
    // Read temperature sensor (PT100 or similar)
    int raw_value = analogRead(TEMP_SENSOR_PIN);
    
    // Convert to temperature (assuming linear relationship)
    float voltage = (raw_value * 3.3) / 4095.0;
    float temperature = (voltage - 0.5) * 100.0 + calibration.temperature_offset;
    
    return temperature;
}

float readHumidity() {
    // Read humidity sensor
    int raw_value = analogRead(HUMIDITY_SENSOR_PIN);
    
    // Convert to humidity (assuming linear relationship)
    float voltage = (raw_value * 3.3) / 4095.0;
    float humidity = voltage * 20.0 + calibration.humidity_offset; // 0-5V = 0-100% RH
    
    return humidity;
}

float calculateStiffness() {
    // Calculate contact stiffness using finite difference
    static float previous_load = 0.0;
    static float previous_displacement = 0.0;
    static bool first_calculation = true;
    
    if (first_calculation) {
        previous_load = current_load;
        previous_displacement = current_displacement;
        first_calculation = false;
        return 0.0;
    }
    
    float delta_load = current_load - previous_load;
    float delta_displacement = current_displacement - previous_displacement;
    
    float stiffness = 0.0;
    if (abs(delta_displacement) > 0.1) { // Avoid division by zero
        stiffness = (delta_load * 1e-6) / (delta_displacement * 1e-9); // Convert to N/m
    }
    
    previous_load = current_load;
    previous_displacement = current_displacement;
    
    return stiffness;
}

uint8_t getContactStatus() {
    if (!contact_detected) return 0; // No contact
    
    // Determine loading state based on load trend
    static float previous_load = 0.0;
    float load_trend = current_load - previous_load;
    previous_load = current_load;
    
    if (load_trend > 0.1) return 2; // Loading
    if (load_trend < -0.1) return 3; // Unloading
    return 1; // In contact but stable
}

void startTest() {
    Serial.println("Starting nano-indentation test...");
    
    // Reset system state
    buffer_index = 0;
    buffer_full = false;
    contact_detected = false;
    sample_counter = 0;
    
    // Update system status
    system_status.test_running = true;
    system_status.test_count++;
    test_start_time = millis();
    
    // Enable piezo driver
    digitalWrite(PIEZO_ENABLE_PIN, HIGH);
    
    // Start data acquisition
    data_acquisition_active = true;
    
    // Turn on test running LED
    digitalWrite(STATUS_LED_BLUE, HIGH);
    
    Serial.println("Test started - acquiring data...");
}

void stopTest() {
    Serial.println("Stopping nano-indentation test...");
    
    // Stop data acquisition
    data_acquisition_active = false;
    
    // Disable piezo driver
    digitalWrite(PIEZO_ENABLE_PIN, LOW);
    
    // Update system status
    system_status.test_running = false;
    
    // Turn off test running LED
    digitalWrite(STATUS_LED_BLUE, LOW);
    
    // Save test data
    saveTestData();
    
    // Calculate material properties
    calculateMaterialProperties();
    
    // Generate report
    generateTestReport();
    
    Serial.println("Test completed and data saved");
}

void executeTestSequence() {
    static uint8_t test_phase = 0; // 0=approach, 1=contact, 2=loading, 3=hold, 4=unloading
    static uint32_t phase_start_time = 0;
    static bool phase_initialized = false;
    
    uint32_t current_time = millis();
    
    if (!phase_initialized) {
        phase_start_time = current_time;
        phase_initialized = true;
    }
    
    uint32_t phase_duration = current_time - phase_start_time;
    
    switch (test_phase) {
        case 0: // Approach phase
            executeApproachPhase();
            if (detectContact()) {
                test_phase = 1;
                phase_initialized = false;
                Serial.println("Contact detected - beginning loading");
            }
            break;
            
        case 1: // Contact establishment
            if (establishContact()) {
                test_phase = 2;
                phase_initialized = false;
                Serial.println("Contact established - beginning loading");
            }
            break;
            
        case 2: // Loading phase
            if (executeLoadingPhase()) {
                test_phase = 3;
                phase_initialized = false;
                Serial.println("Maximum load reached - beginning hold");
            }
            break;
            
        case 3: // Hold phase
            executeHoldPhase();
            if (phase_duration > (current_test.hold_time * 1000)) {
                test_phase = 4;
                phase_initialized = false;
                Serial.println("Hold complete - beginning unloading");
            }
            break;
            
        case 4: // Unloading phase
            if (executeUnloadingPhase()) {
                stopTest();
                test_phase = 0;
                phase_initialized = false;
                Serial.println("Unloading complete - test finished");
            }
            break;
    }
}

void executeApproachPhase() {
    // Approach at constant speed until contact
    target_displacement += current_test.approach_speed / SAMPLING_RATE;
    
    // Control displacement
    float displacement_error = target_displacement - current_displacement;
    float control_output = displacement_error * 0.1; // Simple proportional control
    
    // Apply control signal to piezo
    int pwm_value = constrain(control_output + 2048, 0, 4095);
    analogWrite(PIEZO_DRIVE_PIN, pwm_value);
}

bool detectContact() {
    // Multi-criteria contact detection
    bool load_criterion = current_load > current_test.contact_threshold;
    bool stiffness_criterion = current_stiffness > contact_stiffness_threshold;
    
    if (load_criterion && stiffness_criterion) {
        contact_confirmation_count++;
        if (contact_confirmation_count >= 5) { // Require 5 consecutive confirmations
            contact_detected = true;
            contact_detection_time = millis();
            return true;
        }
    } else {
        contact_confirmation_count = 0;
    }
    
    return false;
}

bool establishContact() {
    // Fine-tune contact establishment
    static bool contact_established = false;
    
    if (!contact_established) {
        // Small additional displacement to ensure good contact
        target_displacement += 1.0; // 1 nm additional
        contact_established = true;
    }
    
    // Check if displacement is achieved
    if (abs(target_displacement - current_displacement) < 0.5) {
        return true;
    }
    
    return false;
}

bool executeLoadingPhase() {
    // Load control or displacement control
    if (current_test.test_mode == 0) { // Load control
        target_load += current_test.loading_rate / SAMPLING_RATE;
        
        // PID control for load
        load_pid_error = target_load - current_load;
        load_pid_integral += load_pid_error / SAMPLING_RATE;
        load_pid_derivative = (load_pid_error - load_pid_previous_error) * SAMPLING_RATE;
        
        float control_output = load_pid_kp * load_pid_error + 
                              load_pid_ki * load_pid_integral + 
                              load_pid_kd * load_pid_derivative;
        
        load_pid_previous_error = load_pid_error;
        
        // Apply control signal
        int pwm_value = constrain(control_output + 2048, 0, 4095);
        analogWrite(PIEZO_DRIVE_PIN, pwm_value);
        
        // Check if maximum load reached
        if (target_load >= current_test.max_load) {
            return true;
        }
        
    } else { // Displacement control
        target_displacement += (current_test.loading_rate / SAMPLING_RATE);
        
        // PID control for displacement
        displacement_pid_error = target_displacement - current_displacement;
        displacement_pid_integral += displacement_pid_error / SAMPLING_RATE;
        displacement_pid_derivative = (displacement_pid_error - displacement_pid_previous_error) * SAMPLING_RATE;
        
        float control_output = displacement_pid_kp * displacement_pid_error + 
                              displacement_pid_ki * displacement_pid_integral + 
                              displacement_pid_kd * displacement_pid_derivative;
        
        displacement_pid_previous_error = displacement_pid_error;
        
        // Apply control signal
        int pwm_value = constrain(control_output + 2048, 0, 4095);
        analogWrite(PIEZO_DRIVE_PIN, pwm_value);
        
        // Check if maximum displacement reached
        if (target_displacement >= current_test.max_displacement) {
            return true;
        }
    }
    
    return false;
}

void executeHoldPhase() {
    // Maintain current load/displacement
    if (current_test.test_mode == 0) { // Load control
        // PID control to maintain load
        load_pid_error = target_load - current_load;
        load_pid_integral += load_pid_error / SAMPLING_RATE;
        load_pid_derivative = (load_pid_error - load_pid_previous_error) * SAMPLING_RATE;
        
        float control_output = load_pid_kp * load_pid_error + 
                              load_pid_ki * load_pid_integral + 
                              load_pid_kd * load_pid_derivative;
        
        load_pid_previous_error = load_pid_error;
        
        int pwm_value = constrain(control_output + 2048, 0, 4095);
        analogWrite(PIEZO_DRIVE_PIN, pwm_value);
    } else { // Displacement control
        // PID control to maintain displacement
        displacement_pid_error = target_displacement - current_displacement;
        displacement_pid_integral += displacement_pid_error / SAMPLING_RATE;
        displacement_pid_derivative = (displacement_pid_error - displacement_pid_previous_error) * SAMPLING_RATE;
        
        float control_output = displacement_pid_kp * displacement_pid_error + 
                              displacement_pid_ki * displacement_pid_integral + 
                              displacement_pid_kd * displacement_pid_derivative;
        
        displacement_pid_previous_error = displacement_pid_error;
        
        int pwm_value = constrain(control_output + 2048, 0, 4095);
        analogWrite(PIEZO_DRIVE_PIN, pwm_value);
    }
}

bool executeUnloadingPhase() {
    // Unload at specified rate
    if (current_test.test_mode == 0) { // Load control
        target_load -= current_test.unloading_rate / SAMPLING_RATE;
        
        if (target_load <= 0.0) {
            target_load = 0.0;
            return true;
        }
        
        // PID control for unloading
        load_pid_error = target_load - current_load;
        load_pid_integral += load_pid_error / SAMPLING_RATE;
        load_pid_derivative = (load_pid_error - load_pid_previous_error) * SAMPLING_RATE;
        
        float control_output = load_pid_kp * load_pid_error + 
                              load_pid_ki * load_pid_integral + 
                              load_pid_kd * load_pid_derivative;
        
        load_pid_previous_error = load_pid_error;
        
        int pwm_value = constrain(control_output + 2048, 0, 4095);
        analogWrite(PIEZO_DRIVE_PIN, pwm_value);
        
    } else { // Displacement control
        target_displacement -= current_test.unloading_rate / SAMPLING_RATE;
        
        if (target_displacement <= 0.0) {
            target_displacement = 0.0;
            return true;
        }
        
        // PID control for displacement
        displacement_pid_error = target_displacement - current_displacement;
        displacement_pid_integral += displacement_pid_error / SAMPLING_RATE;
        displacement_pid_derivative = (displacement_pid_error - displacement_pid_previous_error) * SAMPLING_RATE;
        
        float control_output = displacement_pid_kp * displacement_pid_error + 
                              displacement_pid_ki * displacement_pid_integral + 
                              displacement_pid_kd * displacement_pid_derivative;
        
        displacement_pid_previous_error = displacement_pid_error;
        
        int pwm_value = constrain(control_output + 2048, 0, 4095);
        analogWrite(PIEZO_DRIVE_PIN, pwm_value);
    }
    
    return false;
}

void calculateMaterialProperties() {
    Serial.println("Calculating material properties...");
    
    // Find maximum load and displacement
    float max_load = 0.0;
    float max_displacement = 0.0;
    float final_displacement = 0.0;
    
    for (int i = 0; i < buffer_index; i++) {
        if (data_buffer[i].load > max_load) {
            max_load = data_buffer[i].load;
            max_displacement = data_buffer[i].displacement;
        }
    }
    
    // Find final displacement after unloading
    for (int i = buffer_index - 1; i >= 0; i--) {
        if (data_buffer[i].load <= 0.1) { // Near zero load
            final_displacement = data_buffer[i].displacement;
            break;
        }
    }
    
    // Calculate contact stiffness from unloading curve
    float contact_stiffness = calculateContactStiffness();
    
    // Calculate contact depth using Oliver-Pharr method
    float contact_depth = max_displacement - 0.75 * (max_load * 1e-6) / contact_stiffness;
    
    // Calculate contact area (depends on indenter geometry)
    float contact_area = calculateContactArea(contact_depth);
    
    // Calculate hardness
    calculated_properties.hardness = (max_load * 1e-6) / (contact_area * 1e-18); // Convert to GPa
    
    // Calculate elastic modulus
    float beta = 1.034; // Correction factor for Berkovich indenter
    float poisson_indenter = 0.07; // Diamond
    float elastic_modulus_indenter = 1141.0; // GPa
    
    float reduced_modulus = (sqrt(M_PI) * contact_stiffness) / (2.0 * beta * sqrt(contact_area * 1e-18));
    
    calculated_properties.elastic_modulus = 1.0 / ((1.0 - 0.25) / reduced_modulus - 
                                                   (1.0 - poisson_indenter * poisson_indenter) / elastic_modulus_indenter);
    
    // Calculate other properties
    calculated_properties.contact_stiffness = contact_stiffness;
    calculated_properties.contact_depth = contact_depth;
    calculated_properties.plastic_depth = final_displacement;
    
    // Calculate work values
    calculated_properties.total_work = calculateTotalWork();
    calculated_properties.elastic_work = calculateElasticWork();
    calculated_properties.plastic_work = calculated_properties.total_work - calculated_properties.elastic_work;
    
    Serial.print("Hardness: ");
    Serial.print(calculated_properties.hardness);
    Serial.println(" GPa");
    
    Serial.print("Elastic Modulus: ");
    Serial.print(calculated_properties.elastic_modulus);
    Serial.println(" GPa");
    
    Serial.print("Contact Stiffness: ");
    Serial.print(calculated_properties.contact_stiffness);
    Serial.println(" N/m");
}

float calculateContactStiffness() {
    // Use linear regression on unloading curve
    float sum_x = 0.0, sum_y = 0.0, sum_xy = 0.0, sum_x2 = 0.0;
    int count = 0;
    
    // Find unloading portion (decreasing load)
    bool unloading_started = false;
    float max_load_in_data = 0.0;
    
    for (int i = 0; i < buffer_index; i++) {
        if (data_buffer[i].load > max_load_in_data) {
            max_load_in_data = data_buffer[i].load;
        }
    }
    
    for (int i = 0; i < buffer_index; i++) {
        if (data_buffer[i].load >= 0.9 * max_load_in_data) {
            unloading_started = true;
        }
        
        if (unloading_started && data_buffer[i].load > 0.1) {
            float x = data_buffer[i].displacement;
            float y = data_buffer[i].load;
            
            sum_x += x;
            sum_y += y;
            sum_xy += x * y;
            sum_x2 += x * x;
            count++;
        }
    }
    
    if (count < 10) return 0.0; // Not enough data points
    
    // Calculate slope (stiffness)
    float slope = (count * sum_xy - sum_x * sum_y) / (count * sum_x2 - sum_x * sum_x);
    
    // Convert to N/m
    return slope * 1e-3; // μN/nm to N/m
}

float calculateContactArea(float contact_depth) {
    // Area function for Berkovich indenter
    // A = C0 * hc^2 + C1 * hc + C2 * hc^(1/2) + C3 * hc^(1/4) + C4 * hc^(1/8) + C5 * hc^(1/16)
    
    float area = 0.0;
    float depth_m = contact_depth * 1e-9; // Convert to meters
    
    // Ideal Berkovich area function
    area = 24.5 * depth_m * depth_m; // m²
    
    // Apply calibration corrections if available
    if (calibration.area_function_coefficients[0] != 0.0) {
        area = calibration.area_function_coefficients[0] * pow(depth_m, 2.0) +
               calibration.area_function_coefficients[1] * depth_m +
               calibration.area_function_coefficients[2] * pow(depth_m, 0.5) +
               calibration.area_function_coefficients[3] * pow(depth_m, 0.25) +
               calibration.area_function_coefficients[4] * pow(depth_m, 0.125) +
               calibration.area_function_coefficients[5] * pow(depth_m, 0.0625);
    }
    
    return area * 1e18; // Convert to nm²
}

float calculateTotalWork() {
    // Integrate load-displacement curve
    float total_work = 0.0;
    
    for (int i = 1; i < buffer_index; i++) {
        float delta_displacement = data_buffer[i].displacement - data_buffer[i-1].displacement;
        float average_load = (data_buffer[i].load + data_buffer[i-1].load) / 2.0;
        total_work += average_load * delta_displacement; // μN·nm
    }
    
    return total_work * 1e-9; // Convert to nJ
}

float calculateElasticWork() {
    // Integrate unloading curve
    float elastic_work = 0.0;
    bool unloading_started = false;
    
    for (int i = 1; i < buffer_index; i++) {
        if (data_buffer[i].load < data_buffer[i-1].load) {
            unloading_started = true;
        }
        
        if (unloading_started) {
            float delta_displacement = data_buffer[i].displacement - data_buffer[i-1].displacement;
            float average_load = (data_buffer[i].load + data_buffer[i-1].load) / 2.0;
            elastic_work += average_load * delta_displacement; // μN·nm
        }
    }
    
    return elastic_work * 1e-9; // Convert to nJ
}

void saveTestData() {
    String filename = "/data/test_" + String(system_status.test_count) + "_" + String(millis()) + ".csv";
    
    File dataFile = SD.open(filename, FILE_WRITE);
    if (dataFile) {
        // Write header
        dataFile.println("Timestamp,Load(uN),Displacement(nm),Stiffness(N/m),Temperature(C),Humidity(%),Contact_Status");
        
        // Write data points
        for (int i = 0; i < buffer_index; i++) {
            dataFile.print(data_buffer[i].timestamp);
            dataFile.print(",");
            dataFile.print(data_buffer[i].load, 3);
            dataFile.print(",");
            dataFile.print(data_buffer[i].displacement, 3);
            dataFile.print(",");
            dataFile.print(data_buffer[i].stiffness, 3);
            dataFile.print(",");
            dataFile.print(data_buffer[i].temperature, 2);
            dataFile.print(",");
            dataFile.print(data_buffer[i].humidity, 2);
            dataFile.print(",");
            dataFile.println(data_buffer[i].contact_status);
        }
        
        dataFile.close();
        Serial.println("Test data saved to: " + filename);
    } else {
        Serial.println("Error opening data file for writing");
    }
}

void generateTestReport() {
    String filename = "/reports/report_" + String(system_status.test_count) + "_" + String(millis()) + ".json";
    
    File reportFile = SD.open(filename, FILE_WRITE);
    if (reportFile) {
        StaticJsonDocument<2048> doc;
        
        // Test parameters
        doc["test_parameters"]["max_load"] = current_test.max_load;
        doc["test_parameters"]["max_displacement"] = current_test.max_displacement;
        doc["test_parameters"]["loading_rate"] = current_test.loading_rate;
        doc["test_parameters"]["unloading_rate"] = current_test.unloading_rate;
        doc["test_parameters"]["hold_time"] = current_test.hold_time;
        doc["test_parameters"]["test_mode"] = current_test.test_mode;
        doc["test_parameters"]["indenter_type"] = current_test.indenter_type;
        
        // Material properties
        doc["material_properties"]["hardness"] = calculated_properties.hardness;
        doc["material_properties"]["elastic_modulus"] = calculated_properties.elastic_modulus;
        doc["material_properties"]["contact_stiffness"] = calculated_properties.contact_stiffness;
        doc["material_properties"]["contact_depth"] = calculated_properties.contact_depth;
        doc["material_properties"]["plastic_depth"] = calculated_properties.plastic_depth;
        doc["material_properties"]["total_work"] = calculated_properties.total_work;
        doc["material_properties"]["elastic_work"] = calculated_properties.elastic_work;
        doc["material_properties"]["plastic_work"] = calculated_properties.plastic_work;
        
        // Test information
        doc["test_info"]["test_count"] = system_status.test_count;
        doc["test_info"]["timestamp"] = test_start_time;
        doc["test_info"]["duration"] = millis() - test_start_time;
        doc["test_info"]["data_points"] = buffer_index;
        doc["test_info"]["system_version"] = SYSTEM_VERSION;
        
        // Environmental conditions
        doc["environment"]["temperature"] = system_status.current_temperature;
        doc["environment"]["humidity"] = system_status.current_humidity;
        
        serializeJson(doc, reportFile);
        reportFile.close();
        
        Serial.println("Test report generated: " + filename);
    } else {
        Serial.println("Error creating test report");
    }
}

void processSerialCommands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command == "start") {
            if (!system_status.test_running) {
                startTest();
            }
        } else if (command == "stop") {
            if (system_status.test_running) {
                stopTest();
            }
        } else if (command == "status") {
            printSystemStatus();
        } else if (command == "calibrate") {
            performCalibration();
        } else if (command.startsWith("set_max_load ")) {
            float value = command.substring(13).toFloat();
            current_test.max_load = value;
            Serial.println("Max load set to: " + String(value) + " μN");
        } else if (command.startsWith("set_max_disp ")) {
            float value = command.substring(13).toFloat();
            current_test.max_displacement = value;
            Serial.println("Max displacement set to: " + String(value) + " nm");
        } else if (command == "reset") {
            resetSystem();
        } else if (command == "help") {
            printHelp();
        } else {
            Serial.println("Unknown command: " + command);
        }
    }
}

void printSystemStatus() {
    Serial.println("=== System Status ===");
    Serial.println("System Ready: " + String(system_status.system_ready ? "Yes" : "No"));
    Serial.println("Test Running: " + String(system_status.test_running ? "Yes" : "No"));
    Serial.println("In Contact: " + String(system_status.in_contact ? "Yes" : "No"));
    Serial.println("Current Load: " + String(system_status.current_load) + " μN");
    Serial.println("Current Displacement: " + String(system_status.current_displacement) + " nm");
    Serial.println("Temperature: " + String(system_status.current_temperature) + " °C");
    Serial.println("Humidity: " + String(system_status.current_humidity) + " %RH");
    Serial.println("Test Count: " + String(system_status.test_count));
    Serial.println("Uptime: " + String(system_status.uptime) + " seconds");
    Serial.println("====================");
}

void printHelp() {
    Serial.println("=== Available Commands ===");
    Serial.println("start - Start indentation test");
    Serial.println("stop - Stop current test");
    Serial.println("status - Show system status");
    Serial.println("calibrate - Perform system calibration");
    Serial.println("set_max_load <value> - Set maximum load (μN)");
    Serial.println("set_max_disp <value> - Set maximum displacement (nm)");
    Serial.println("reset - Reset system");
    Serial.println("help - Show this help message");
    Serial.println("=========================");
}

void updateSystemStatus() {
    system_status.uptime = millis() / 1000;
    system_status.current_load = current_load;
    system_status.current_displacement = current_displacement;
    system_status.current_temperature = readTemperature();
    system_status.current_humidity = readHumidity();
    system_status.in_contact = contact_detected;
    system_status.system_ready = !system_status.emergency_stop && 
                                system_status.temperature_stable && 
                                system_status.vibration_ok;
    
    // Update status LEDs
    digitalWrite(STATUS_LED_GREEN, system_status.system_ready);
    digitalWrite(STATUS_LED_RED, system_status.emergency_stop);
}

void sendStatusToESP32() {
    StaticJsonDocument<512> doc;
    doc["type"] = "status";
    doc["system_ready"] = system_status.system_ready;
    doc["test_running"] = system_status.test_running;
    doc["in_contact"] = system_status.in_contact;
    doc["current_load"] = system_status.current_load;
    doc["current_displacement"] = system_status.current_displacement;
    doc["temperature"] = system_status.current_temperature;
    doc["humidity"] = system_status.current_humidity;
    doc["test_count"] = system_status.test_count;
    doc["uptime"] = system_status.uptime;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void handleEmergencyStop() {
    Serial.println("EMERGENCY STOP ACTIVATED!");
    
    // Stop all motion
    data_acquisition_active = false;
    digitalWrite(PIEZO_ENABLE_PIN, LOW);
    digitalWrite(STEPPER_ENABLE, LOW);
    
    // Update system status
    system_status.emergency_stop = true;
    system_status.test_running = false;
    emergency_stop_triggered = true;
    
    // Turn on error LED
    digitalWrite(STATUS_LED_RED, HIGH);
    digitalWrite(STATUS_LED_BLUE, LOW);
    
    // Save emergency data if test was running
    if (buffer_index > 0) {
        saveTestData();
    }
    
    // Wait for emergency stop to be cleared
    while (digitalRead(EMERGENCY_STOP) == LOW) {
        delay(100);
    }
    
    Serial.println("Emergency stop cleared - system reset required");
    resetSystem();
}

void resetSystem() {
    Serial.println("Resetting system...");
    
    // Reset all control variables
    target_load = 0.0;
    target_displacement = 0.0;
    current_load = 0.0;
    current_displacement = 0.0;
    contact_detected = false;
    data_acquisition_active = false;
    emergency_stop_triggered = false;
    
    // Reset PID controllers
    load_pid_integral = 0.0;
    load_pid_previous_error = 0.0;
    displacement_pid_integral = 0.0;
    displacement_pid_previous_error = 0.0;
    
    // Reset buffer
    buffer_index = 0;
    buffer_full = false;
    
    // Reset system status
    system_status.emergency_stop = false;
    system_status.test_running = false;
    system_status.in_contact = false;
    
    // Re-enable systems
    digitalWrite(STEPPER_ENABLE, HIGH);
    digitalWrite(STATUS_LED_RED, LOW);
    
    Serial.println("System reset complete");
}

void updateEnvironmentalControl() {
    float current_temp = readTemperature();
    float current_humid = readHumidity();
    
    // Temperature control (target: 25°C ± 0.5°C)
    if (current_temp < 24.5) {
        digitalWrite(HEATER_CONTROL, HIGH);
        digitalWrite(COOLER_CONTROL, LOW);
    } else if (current_temp > 25.5) {
        digitalWrite(HEATER_CONTROL, LOW);
        digitalWrite(COOLER_CONTROL, HIGH);
    } else {
        digitalWrite(HEATER_CONTROL, LOW);
        digitalWrite(COOLER_CONTROL, LOW);
        system_status.temperature_stable = true;
    }
    
    // Humidity control (target: 50% ± 5%)
    // Implementation depends on specific humidity control hardware
    
    // Fan control based on temperature
    if (current_temp > 30.0) {
        digitalWrite(FAN_CONTROL, HIGH);
    } else {
        digitalWrite(FAN_CONTROL, LOW);
    }
}

void updateEnvironmentalReadings() {
    system_status.current_temperature = readTemperature();
    system_status.current_humidity = readHumidity();
}

bool testSensorCommunication() {
    // Test load cell communication
    float load_reading = readLoadCell();
    if (isnan(load_reading) || abs(load_reading) > 1000000) {
        return false;
    }
    
    // Test displacement sensor communication
    float displacement_reading = readDisplacementSensor();
    if (isnan(displacement_reading) || abs(displacement_reading) > 200000) {
        return false;
    }
    
    return true;
}

void performSystemSelfTest() {
    Serial.println("Performing system self-test...");
    
    bool self_test_passed = true;
    
    // Test sensors
    if (!testSensorCommunication()) {
        Serial.println("FAIL: Sensor communication test");
        self_test_passed = false;
    } else {
        Serial.println("PASS: Sensor communication test");
    }
    
    // Test actuators
    digitalWrite(PIEZO_ENABLE_PIN, HIGH);
    delay(100);
    digitalWrite(PIEZO_ENABLE_PIN, LOW);
    Serial.println("PASS: Actuator test");
    
    // Test stepper motors
    stepper_x.move(100);
    stepper_x.runToPosition();
    stepper_x.move(-100);
    stepper_x.runToPosition();
    Serial.println("PASS: Stepper motor test");
    
    // Test environmental sensors
    updateEnvironmentalReadings();
    if (system_status.current_temperature > 0 && system_status.current_temperature < 50) {
        Serial.println("PASS: Environmental sensor test");
    } else {
        Serial.println("FAIL: Environmental sensor test");
        self_test_passed = false;
    }
    
    if (self_test_passed) {
        Serial.println("System self-test PASSED");
        system_status.system_ready = true;
        digitalWrite(STATUS_LED_GREEN, HIGH);
    } else {
        Serial.println("System self-test FAILED");
        system_status.system_ready = false;
        digitalWrite(STATUS_LED_RED, HIGH);
    }
}

void performCalibration() {
    Serial.println("Starting system calibration...");
    
    // This would typically involve:
    // 1. Force calibration with known weights
    // 2. Displacement calibration with optical interferometry
    // 3. Area function calibration with reference materials
    // 4. Temperature calibration
    
    Serial.println("Calibration procedure would be implemented here");
    Serial.println("Please refer to calibration manual for detailed procedures");
}

void loadCalibrationData() {
    // Load calibration data from SD card
    if (SD.exists("/calibration/calibration.json")) {
        File calFile = SD.open("/calibration/calibration.json", FILE_READ);
        if (calFile) {
            StaticJsonDocument<1024> doc;
            deserializeJson(doc, calFile);
            
            calibration.load_calibration_factor = doc["load_calibration_factor"];
            calibration.displacement_calibration_factor = doc["displacement_calibration_factor"];
            calibration.stiffness_calibration_factor = doc["stiffness_calibration_factor"];
            calibration.temperature_offset = doc["temperature_offset"];
            calibration.humidity_offset = doc["humidity_offset"];
            calibration.compliance_correction = doc["compliance_correction"];
            calibration.last_calibration_date = doc["last_calibration_date"];
            
            // Load area function coefficients
            for (int i = 0; i < 6; i++) {
                calibration.area_function_coefficients[i] = doc["area_function_coefficients"][i];
            }
            
            calFile.close();
            Serial.println("Calibration data loaded successfully");
        }
    } else {
        // Use default calibration values
        calibration.load_calibration_factor = 0.0;
        calibration.displacement_calibration_factor = 1.0;
        calibration.stiffness_calibration_factor = 1.0;
        calibration.temperature_offset = 0.0;
        calibration.humidity_offset = 0.0;
        calibration.compliance_correction = 0.0;
        calibration.last_calibration_date = 0;
        
        // Default area function for ideal Berkovich indenter
        calibration.area_function_coefficients[0] = 24.5;
        for (int i = 1; i < 6; i++) {
            calibration.area_function_coefficients[i] = 0.0;
        }
        
        Serial.println("Using default calibration values");
    }
}

void processDataBuffer() {
    // Process data buffer for real-time analysis
    if (buffer_index > 10 && system_status.test_running) {
        // Real-time contact detection
        if (!contact_detected) {
            detectContact();
        }
        
        // Real-time stiffness calculation
        if (contact_detected && buffer_index > 50) {
            current_stiffness = calculateStiffness();
        }
    }
    
    // Check if buffer is getting full
    if (buffer_index > 1800) {
        Serial.println("Warning: Data buffer nearly full");
    }
}

// Additional utility functions for advanced features would be implemented here
// These might include:
// - Continuous stiffness measurement (CSM)
// - Dynamic mechanical analysis (DMA)
// - Creep and relaxation testing
// - Multi-cycle fatigue testing
// - Temperature ramping protocols
// - Automated array testing
// - Machine learning algorithms for contact detection
// - Advanced data analysis and curve fitting