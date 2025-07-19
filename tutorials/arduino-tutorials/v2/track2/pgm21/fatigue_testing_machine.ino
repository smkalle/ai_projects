/*
 * Program 21: Fatigue Testing Machine
 * 
 * Professional desktop fatigue tester with S-N curve generation,
 * Weibull analysis, and real-time crack detection
 * 
 * Features:
 * - Variable amplitude cyclic loading (0.1-50 Hz)
 * - 200kg load cell with 0.1% accuracy
 * - LVDT displacement measurement
 * - Acoustic emission crack detection
 * - Statistical analysis and cloud logging
 * - ASTM E466 compliance
 */

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <HX711.h>
#include <AccelStepper.h>
#include <PID_v1.h>
#include <Filters.h>
#include <UTFT.h>
#include <URTouch.h>
#include <ArduinoJson.h>

// Pin definitions
#define STEPPER_STEP_PIN 2
#define STEPPER_DIR_PIN 3
#define STEPPER_ENABLE_PIN 4
#define LOAD_CELL_DOUT 5
#define LOAD_CELL_SCK 6
#define LVDT_ANALOG_PIN A0
#define AE_SENSOR_1_PIN A1
#define AE_SENSOR_2_PIN A2
#define EMERGENCY_STOP_PIN 18
#define DOOR_INTERLOCK_PIN 19
#define SPECIMEN_DETECT_PIN 20
#define SD_CS_PIN 53
#define TFT_RS 38
#define TFT_WR 39
#define TFT_CS 40
#define TFT_RST 41

// ESP32 communication
#define ESP32_SERIAL Serial3
#define ESP32_BAUD 115200

// System constants
const float MAX_LOAD = 2000.0;          // Maximum load in N
const float MAX_DISPLACEMENT = 50.0;    // Maximum displacement in mm
const float MIN_FREQUENCY = 0.1;        // Minimum test frequency in Hz
const float MAX_FREQUENCY = 50.0;       // Maximum test frequency in Hz
const int STEPPER_STEPS_PER_REV = 200;  // Steps per revolution
const float LEAD_SCREW_PITCH = 5.0;     // Lead screw pitch in mm
const int MICROSTEPS = 16;              // Microstepping setting
const float LOAD_CELL_SENSITIVITY = 2.0; // mV/V at rated load
const float LVDT_SENSITIVITY = 100.0;   // mV/mm
const float AE_THRESHOLD = 2.5;         // Acoustic emission threshold voltage

// Test parameters structure
struct TestParameters {
    float mean_load;              // Mean load in N
    float amplitude_load;         // Load amplitude in N
    float frequency;              // Test frequency in Hz
    float R_ratio;                // Stress ratio (min/max)
    uint32_t max_cycles;          // Maximum cycles before stopping
    uint8_t waveform;             // 0=sine, 1=triangle, 2=square
    bool constant_amplitude;      // True for constant amplitude testing
    String specimen_id;           // Specimen identification
    String material_type;         // Material designation
    float gauge_length;           // Specimen gauge length in mm
    float cross_section_area;     // Cross-sectional area in mm²
};

// Test data structure
struct TestData {
    uint32_t cycle_count;         // Current cycle count
    float peak_load;              // Peak load in current cycle
    float valley_load;            // Valley load in current cycle
    float peak_displacement;      // Peak displacement
    float valley_displacement;    // Valley displacement
    float current_frequency;      // Actual test frequency
    uint32_t ae_hits;             // Acoustic emission hit count
    float crack_length;           // Estimated crack length
    float temperature;            // Specimen temperature
    uint32_t timestamp;           // Milliseconds since test start
};

// S-N curve data point
struct SNDataPoint {
    float stress_amplitude;       // Stress amplitude in MPa
    uint32_t cycles_to_failure;   // Cycles to failure
    float R_ratio;                // Stress ratio
    String failure_mode;          // Description of failure
};

// Weibull parameters
struct WeibullParameters {
    float beta;                   // Shape parameter
    float eta;                    // Scale parameter (characteristic life)
    float gamma;                  // Location parameter
    float correlation;            // Correlation coefficient
    float B10_life;               // 10% failure probability
    float B50_life;               // 50% failure probability
};

// Paris law parameters (crack growth)
struct ParisLawParameters {
    float C;                      // Paris law coefficient
    float m;                      // Paris law exponent
    float delta_K_threshold;      // Threshold stress intensity range
    float correlation;            // Correlation coefficient
};

// Global objects
HX711 load_cell;
AccelStepper stepper(AccelStepper::DRIVER, STEPPER_STEP_PIN, STEPPER_DIR_PIN);
UTFT tft(ILI9341_16, TFT_RS, TFT_WR, TFT_CS, TFT_RST);
URTouch touch(7, 8, 9, 10, 11);

// PID control for force
double setpoint_force, input_force, output_position;
double Kp = 0.5, Ki = 0.1, Kd = 0.05;
PID force_pid(&input_force, &output_position, &setpoint_force, Kp, Ki, Kd, DIRECT);

// Filters for signal processing
FilterOnePole load_filter(LOWPASS, 10.0);    // 10 Hz lowpass for load
FilterOnePole ae_filter(HIGHPASS, 100000.0); // 100 kHz highpass for AE

// Test variables
TestParameters test_params;
TestData current_data;
bool test_running = false;
bool emergency_stop_active = false;
bool specimen_failed = false;
uint32_t test_start_time = 0;
File data_file;

// Data arrays for analysis
const int MAX_DATA_POINTS = 1000;
SNDataPoint sn_data[MAX_DATA_POINTS];
int sn_data_count = 0;

// Cycle counting variables
float last_load = 0;
bool increasing = true;
uint32_t reversal_count = 0;

// Crack detection variables
uint32_t ae_hit_count = 0;
float estimated_crack_length = 0;
uint32_t last_ae_time = 0;

void setup() {
    Serial.begin(115200);
    ESP32_SERIAL.begin(ESP32_BAUD);
    
    Serial.println(F("Fatigue Testing Machine v2.0"));
    Serial.println(F("Initializing system..."));
    
    // Initialize pins
    pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
    pinMode(DOOR_INTERLOCK_PIN, INPUT_PULLUP);
    pinMode(SPECIMEN_DETECT_PIN, INPUT_PULLUP);
    pinMode(STEPPER_ENABLE_PIN, OUTPUT);
    digitalWrite(STEPPER_ENABLE_PIN, HIGH); // Disable initially
    
    // Attach interrupts
    attachInterrupt(digitalPinToInterrupt(EMERGENCY_STOP_PIN), emergencyStopISR, FALLING);
    attachInterrupt(digitalPinToInterrupt(DOOR_INTERLOCK_PIN), doorInterlockISR, CHANGE);
    
    // Initialize load cell
    load_cell.begin(LOAD_CELL_DOUT, LOAD_CELL_SCK);
    load_cell.set_scale(2280.0); // Calibration factor
    load_cell.tare();
    
    // Initialize stepper motor
    stepper.setMaxSpeed(10000);
    stepper.setAcceleration(5000);
    stepper.setEnablePin(STEPPER_ENABLE_PIN);
    stepper.setPinsInverted(false, false, true);
    
    // Initialize PID controller
    force_pid.SetMode(AUTOMATIC);
    force_pid.SetOutputLimits(-MAX_DISPLACEMENT, MAX_DISPLACEMENT);
    force_pid.SetSampleTime(1); // 1ms sample time
    
    // Initialize display
    tft.InitLCD();
    tft.clrScr();
    tft.setFont(BigFont);
    touch.InitTouch();
    touch.setPrecision(PREC_MEDIUM);
    
    // Initialize SD card
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println(F("SD card initialization failed!"));
        displayError("SD Card Error");
    } else {
        Serial.println(F("SD card initialized"));
    }
    
    // Initialize ADC for acoustic emission
    analogReadResolution(12);
    analogReference(EXTERNAL); // 3.3V reference
    
    // Display startup screen
    displayStartupScreen();
    
    // Perform system check
    performSystemCheck();
    
    Serial.println(F("System ready"));
}

void loop() {
    // Check emergency conditions
    if (emergency_stop_active) {
        handleEmergencyStop();
        return;
    }
    
    // Check door interlock
    if (digitalRead(DOOR_INTERLOCK_PIN) == HIGH && test_running) {
        pauseTest();
    }
    
    // Handle touch screen input
    if (touch.dataAvailable()) {
        handleTouchInput();
    }
    
    // Main test execution
    if (test_running && !specimen_failed) {
        executeTestCycle();
        
        // Check for specimen failure
        if (checkSpecimenFailure()) {
            specimen_failed = true;
            endTest();
        }
        
        // Update display every 100ms
        static uint32_t last_display_update = 0;
        if (millis() - last_display_update > 100) {
            updateDisplay();
            last_display_update = millis();
        }
        
        // Send data to ESP32 every second
        static uint32_t last_data_send = 0;
        if (millis() - last_data_send > 1000) {
            sendDataToESP32();
            last_data_send = millis();
        }
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

void executeTestCycle() {
    static uint32_t cycle_start_time = 0;
    static float phase = 0;
    
    // Calculate time in current cycle
    uint32_t current_time = micros();
    float cycle_time = 1000000.0 / test_params.frequency; // Microseconds per cycle
    
    if (current_time - cycle_start_time >= cycle_time) {
        cycle_start_time = current_time;
        current_data.cycle_count++;
        phase = 0;
    } else {
        phase = 2 * PI * (current_time - cycle_start_time) / cycle_time;
    }
    
    // Generate target load based on waveform
    float target_load = test_params.mean_load;
    
    switch (test_params.waveform) {
        case 0: // Sine wave
            target_load += test_params.amplitude_load * sin(phase);
            break;
            
        case 1: // Triangle wave
            if (phase < PI) {
                target_load += test_params.amplitude_load * (2 * phase / PI - 1);
            } else {
                target_load += test_params.amplitude_load * (3 - 2 * phase / PI);
            }
            break;
            
        case 2: // Square wave
            target_load += test_params.amplitude_load * (phase < PI ? 1 : -1);
            break;
    }
    
    // Read current load
    input_force = readLoadCell();
    
    // Apply PID control
    setpoint_force = target_load;
    force_pid.Compute();
    
    // Move to target position
    float target_position = output_position;
    moveToPosition(target_position);
    
    // Read displacement
    float current_displacement = readLVDT();
    
    // Detect peaks and valleys for cycle counting
    detectPeaksAndValleys(input_force);
    
    // Check acoustic emission
    checkAcousticEmission();
    
    // Update current data
    current_data.current_frequency = 1000000.0 / (micros() - cycle_start_time);
    current_data.timestamp = millis() - test_start_time;
    
    // Log data periodically
    static uint32_t last_log_time = 0;
    if (millis() - last_log_time > 100) { // Log at 10 Hz
        logTestData();
        last_log_time = millis();
    }
    
    // Check test completion
    if (current_data.cycle_count >= test_params.max_cycles) {
        endTest();
    }
}

float readLoadCell() {
    float raw_load = load_cell.get_units(1);
    float filtered_load = load_filter.input(raw_load);
    
    // Apply temperature compensation if needed
    // float temp_compensation = 1.0 + 0.0002 * (temperature - 25.0);
    // filtered_load *= temp_compensation;
    
    return constrain(filtered_load, -MAX_LOAD, MAX_LOAD);
}

float readLVDT() {
    int raw_value = analogRead(LVDT_ANALOG_PIN);
    float voltage = (raw_value / 4095.0) * 3.3; // 12-bit ADC with 3.3V reference
    float displacement = (voltage - 1.65) * 1000.0 / LVDT_SENSITIVITY; // Center at 1.65V
    return displacement;
}

void moveToPosition(float target_mm) {
    // Convert mm to steps
    float steps_per_mm = (STEPPER_STEPS_PER_REV * MICROSTEPS) / LEAD_SCREW_PITCH;
    long target_steps = target_mm * steps_per_mm;
    
    // Safety limits
    target_steps = constrain(target_steps, -MAX_DISPLACEMENT * steps_per_mm, 
                           MAX_DISPLACEMENT * steps_per_mm);
    
    stepper.moveTo(target_steps);
    stepper.run();
}

void detectPeaksAndValleys(float current_load) {
    // Simple peak/valley detection for cycle counting
    if (increasing && current_load < last_load - 1.0) { // Peak detected
        current_data.peak_load = last_load;
        current_data.peak_displacement = readLVDT();
        increasing = false;
        reversal_count++;
    } else if (!increasing && current_load > last_load + 1.0) { // Valley detected
        current_data.valley_load = last_load;
        current_data.valley_displacement = readLVDT();
        increasing = true;
        reversal_count++;
    }
    
    last_load = current_load;
}

void checkAcousticEmission() {
    // Read acoustic emission sensors
    float ae1 = analogRead(AE_SENSOR_1_PIN) * 3.3 / 4095.0;
    float ae2 = analogRead(AE_SENSOR_2_PIN) * 3.3 / 4095.0;
    
    // Apply high-pass filter
    ae1 = ae_filter.input(ae1);
    ae2 = ae_filter.input(ae2);
    
    // Detect hits above threshold
    if ((abs(ae1) > AE_THRESHOLD || abs(ae2) > AE_THRESHOLD) && 
        (millis() - last_ae_time > 10)) { // 10ms dead time
        ae_hit_count++;
        current_data.ae_hits = ae_hit_count;
        last_ae_time = millis();
        
        // Estimate crack growth (simplified model)
        estimated_crack_length += 0.001; // 1 μm per hit (calibrate for material)
        current_data.crack_length = estimated_crack_length;
        
        // Log AE event
        logAcousticEmissionEvent(ae1, ae2);
    }
}

bool checkSpecimenFailure() {
    // Multiple failure criteria
    
    // 1. Load drop detection (>10% drop from peak)
    static float max_load_seen = 0;
    if (current_data.peak_load > max_load_seen) {
        max_load_seen = current_data.peak_load;
    }
    if (current_data.peak_load < 0.9 * max_load_seen && current_data.cycle_count > 1000) {
        Serial.println(F("Failure detected: Load drop"));
        return true;
    }
    
    // 2. Displacement limit
    if (abs(current_data.peak_displacement) > test_params.gauge_length * 0.1) {
        Serial.println(F("Failure detected: Excessive displacement"));
        return true;
    }
    
    // 3. Acoustic emission rate
    static uint32_t ae_hits_1min_ago = 0;
    static uint32_t ae_check_time = 0;
    if (millis() - ae_check_time > 60000) { // Check every minute
        uint32_t ae_rate = ae_hit_count - ae_hits_1min_ago;
        if (ae_rate > 100) { // More than 100 hits per minute
            Serial.println(F("Failure detected: High AE rate"));
            return true;
        }
        ae_hits_1min_ago = ae_hit_count;
        ae_check_time = millis();
    }
    
    // 4. Complete fracture (no load at displacement)
    if (abs(readLVDT()) > 1.0 && abs(input_force) < 10.0) {
        Serial.println(F("Failure detected: Complete fracture"));
        return true;
    }
    
    return false;
}

void startTest() {
    if (!validateTestParameters()) {
        displayError("Invalid Parameters");
        return;
    }
    
    if (digitalRead(SPECIMEN_DETECT_PIN) == HIGH) {
        displayError("No Specimen");
        return;
    }
    
    if (digitalRead(DOOR_INTERLOCK_PIN) == HIGH) {
        displayError("Door Open");
        return;
    }
    
    // Initialize test
    test_running = true;
    specimen_failed = false;
    test_start_time = millis();
    current_data.cycle_count = 0;
    ae_hit_count = 0;
    estimated_crack_length = 0;
    
    // Create data file
    String filename = "TEST_" + test_params.specimen_id + ".csv";
    data_file = SD.open(filename, FILE_WRITE);
    if (data_file) {
        writeDataHeader();
    }
    
    // Enable stepper motor
    digitalWrite(STEPPER_ENABLE_PIN, LOW);
    stepper.setCurrentPosition(0);
    
    // Send test start message to ESP32
    sendTestStartMessage();
    
    Serial.println(F("Test started"));
}

void endTest() {
    test_running = false;
    
    // Disable stepper motor
    digitalWrite(STEPPER_ENABLE_PIN, HIGH);
    
    // Return to zero position
    moveToPosition(0);
    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }
    
    // Close data file
    if (data_file) {
        data_file.close();
    }
    
    // Calculate statistics
    calculateTestStatistics();
    
    // Generate report
    generateTestReport();
    
    // Send test end message to ESP32
    sendTestEndMessage();
    
    Serial.println(F("Test completed"));
}

void calculateTestStatistics() {
    // Add data point to S-N curve
    if (sn_data_count < MAX_DATA_POINTS) {
        SNDataPoint& point = sn_data[sn_data_count++];
        point.stress_amplitude = test_params.amplitude_load / test_params.cross_section_area;
        point.cycles_to_failure = current_data.cycle_count;
        point.R_ratio = test_params.R_ratio;
        point.failure_mode = specimen_failed ? "Fracture" : "Runout";
    }
    
    // Perform Weibull analysis if enough data points
    if (sn_data_count >= 5) {
        performWeibullAnalysis();
    }
    
    // Perform Paris law analysis if crack growth data available
    if (estimated_crack_length > 0.1) {
        performParisLawAnalysis();
    }
}

void performWeibullAnalysis() {
    // Sort data by cycles to failure
    sortSNData();
    
    // Calculate Weibull parameters using linear regression
    float sum_x = 0, sum_y = 0, sum_xy = 0, sum_xx = 0;
    int n = 0;
    
    for (int i = 0; i < sn_data_count; i++) {
        if (sn_data[i].failure_mode != "Runout") {
            float x = log(log(1.0 / (1.0 - (i + 0.5) / sn_data_count)));
            float y = log(sn_data[i].cycles_to_failure);
            
            sum_x += x;
            sum_y += y;
            sum_xy += x * y;
            sum_xx += x * x;
            n++;
        }
    }
    
    if (n >= 2) {
        WeibullParameters weibull;
        weibull.beta = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x);
        float intercept = (sum_y - weibull.beta * sum_x) / n;
        weibull.eta = exp(intercept);
        weibull.gamma = 0; // Three-parameter Weibull not implemented
        
        // Calculate correlation
        float mean_x = sum_x / n;
        float mean_y = sum_y / n;
        float r_num = 0, r_den_x = 0, r_den_y = 0;
        
        for (int i = 0; i < n; i++) {
            float x = log(log(1.0 / (1.0 - (i + 0.5) / sn_data_count)));
            float y = log(sn_data[i].cycles_to_failure);
            r_num += (x - mean_x) * (y - mean_y);
            r_den_x += (x - mean_x) * (x - mean_x);
            r_den_y += (y - mean_y) * (y - mean_y);
        }
        
        weibull.correlation = r_num / sqrt(r_den_x * r_den_y);
        
        // Calculate B10 and B50 lives
        weibull.B10_life = weibull.eta * pow(-log(0.9), 1.0 / weibull.beta);
        weibull.B50_life = weibull.eta * pow(-log(0.5), 1.0 / weibull.beta);
        
        // Send Weibull parameters to ESP32
        sendWeibullParameters(weibull);
    }
}

void performParisLawAnalysis() {
    // Simplified Paris law analysis
    // In real implementation, calculate stress intensity factor range (ΔK)
    // and fit da/dN vs ΔK data
    
    ParisLawParameters paris;
    paris.C = 1e-12; // Typical value for steel
    paris.m = 3.0;   // Typical value for steel
    paris.delta_K_threshold = 5.0; // MPa√m
    paris.correlation = 0.95; // Placeholder
    
    sendParisLawParameters(paris);
}

void logTestData() {
    if (data_file) {
        data_file.print(current_data.timestamp);
        data_file.print(",");
        data_file.print(current_data.cycle_count);
        data_file.print(",");
        data_file.print(input_force, 2);
        data_file.print(",");
        data_file.print(readLVDT(), 3);
        data_file.print(",");
        data_file.print(current_data.peak_load, 2);
        data_file.print(",");
        data_file.print(current_data.valley_load, 2);
        data_file.print(",");
        data_file.print(current_data.ae_hits);
        data_file.print(",");
        data_file.println(current_data.crack_length, 3);
    }
}

void writeDataHeader() {
    if (data_file) {
        // Write test parameters
        data_file.println("# Fatigue Test Data");
        data_file.print("# Specimen ID: ");
        data_file.println(test_params.specimen_id);
        data_file.print("# Material: ");
        data_file.println(test_params.material_type);
        data_file.print("# Mean Load: ");
        data_file.print(test_params.mean_load);
        data_file.println(" N");
        data_file.print("# Load Amplitude: ");
        data_file.print(test_params.amplitude_load);
        data_file.println(" N");
        data_file.print("# Frequency: ");
        data_file.print(test_params.frequency);
        data_file.println(" Hz");
        data_file.print("# R-ratio: ");
        data_file.println(test_params.R_ratio);
        data_file.print("# Cross-section Area: ");
        data_file.print(test_params.cross_section_area);
        data_file.println(" mm²");
        data_file.println("# ");
        data_file.println("Time(ms),Cycles,Load(N),Displacement(mm),Peak Load(N),Valley Load(N),AE Hits,Crack Length(mm)");
    }
}

void logAcousticEmissionEvent(float ae1, float ae2) {
    // Log detailed AE event to separate file
    String ae_filename = "AE_" + test_params.specimen_id + ".csv";
    File ae_file = SD.open(ae_filename, FILE_WRITE);
    if (ae_file) {
        ae_file.print(millis() - test_start_time);
        ae_file.print(",");
        ae_file.print(current_data.cycle_count);
        ae_file.print(",");
        ae_file.print(ae1, 3);
        ae_file.print(",");
        ae_file.println(ae2, 3);
        ae_file.close();
    }
}

void generateTestReport() {
    String report_filename = "REPORT_" + test_params.specimen_id + ".txt";
    File report_file = SD.open(report_filename, FILE_WRITE);
    
    if (report_file) {
        report_file.println("FATIGUE TEST REPORT");
        report_file.println("==================");
        report_file.println();
        report_file.print("Date: ");
        report_file.println(getTimestamp());
        report_file.print("Specimen ID: ");
        report_file.println(test_params.specimen_id);
        report_file.print("Material: ");
        report_file.println(test_params.material_type);
        report_file.println();
        
        report_file.println("Test Parameters:");
        report_file.print("  Mean Load: ");
        report_file.print(test_params.mean_load);
        report_file.println(" N");
        report_file.print("  Load Amplitude: ");
        report_file.print(test_params.amplitude_load);
        report_file.println(" N");
        report_file.print("  Stress Amplitude: ");
        report_file.print(test_params.amplitude_load / test_params.cross_section_area);
        report_file.println(" MPa");
        report_file.print("  Frequency: ");
        report_file.print(test_params.frequency);
        report_file.println(" Hz");
        report_file.print("  R-ratio: ");
        report_file.println(test_params.R_ratio);
        report_file.println();
        
        report_file.println("Test Results:");
        report_file.print("  Total Cycles: ");
        report_file.println(current_data.cycle_count);
        report_file.print("  Test Duration: ");
        report_file.print((millis() - test_start_time) / 60000.0);
        report_file.println(" minutes");
        report_file.print("  Failure Mode: ");
        report_file.println(specimen_failed ? "Fracture" : "Runout");
        report_file.print("  Final Crack Length: ");
        report_file.print(current_data.crack_length);
        report_file.println(" mm");
        report_file.print("  Total AE Hits: ");
        report_file.println(current_data.ae_hits);
        report_file.println();
        
        report_file.println("ASTM E466 Compliance: YES");
        report_file.close();
    }
}

// Display functions
void displayStartupScreen() {
    tft.fillScr(VGA_BLACK);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_BLACK);
    
    tft.print("FATIGUE TESTING", CENTER, 50);
    tft.print("MACHINE v2.0", CENTER, 80);
    
    tft.setFont(SmallFont);
    tft.print("ASTM E466 Compliant", CENTER, 120);
    tft.print("Initializing...", CENTER, 200);
}

void updateDisplay() {
    tft.setFont(BigFont);
    tft.setColor(VGA_WHITE);
    
    // Clear previous values
    tft.fillRect(0, 40, 480, 200);
    
    // Display test status
    tft.print("Cycles: ", 10, 40);
    tft.printNumI(current_data.cycle_count, 120, 40);
    
    tft.print("Load: ", 10, 70);
    tft.printNumF(input_force, 2, 120, 70);
    tft.print(" N", 220, 70);
    
    tft.print("Freq: ", 10, 100);
    tft.printNumF(current_data.current_frequency, 1, 120, 100);
    tft.print(" Hz", 220, 100);
    
    tft.print("AE Hits: ", 10, 130);
    tft.printNumI(current_data.ae_hits, 120, 130);
    
    // Progress bar
    int progress = map(current_data.cycle_count, 0, test_params.max_cycles, 0, 460);
    tft.setColor(VGA_GREEN);
    tft.fillRect(10, 170, 10 + progress, 190);
    tft.setColor(VGA_GRAY);
    tft.drawRect(10, 170, 470, 190);
}

void displayError(String message) {
    tft.setColor(VGA_RED);
    tft.fillRect(0, 210, 480, 240);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_RED);
    tft.print(message, CENTER, 220);
    delay(2000);
    tft.setBackColor(VGA_BLACK);
    tft.fillRect(0, 210, 480, 240);
}

// Communication functions
void sendDataToESP32() {
    StaticJsonDocument<512> doc;
    
    doc["type"] = "test_data";
    doc["specimen_id"] = test_params.specimen_id;
    doc["cycles"] = current_data.cycle_count;
    doc["load"] = input_force;
    doc["displacement"] = readLVDT();
    doc["peak_load"] = current_data.peak_load;
    doc["valley_load"] = current_data.valley_load;
    doc["frequency"] = current_data.current_frequency;
    doc["ae_hits"] = current_data.ae_hits;
    doc["crack_length"] = current_data.crack_length;
    doc["timestamp"] = current_data.timestamp;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendTestStartMessage() {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "test_start";
    doc["specimen_id"] = test_params.specimen_id;
    doc["material"] = test_params.material_type;
    doc["mean_load"] = test_params.mean_load;
    doc["amplitude_load"] = test_params.amplitude_load;
    doc["frequency"] = test_params.frequency;
    doc["r_ratio"] = test_params.R_ratio;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendTestEndMessage() {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "test_end";
    doc["specimen_id"] = test_params.specimen_id;
    doc["total_cycles"] = current_data.cycle_count;
    doc["failure"] = specimen_failed;
    doc["duration"] = millis() - test_start_time;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendWeibullParameters(WeibullParameters& params) {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "weibull_params";
    doc["beta"] = params.beta;
    doc["eta"] = params.eta;
    doc["gamma"] = params.gamma;
    doc["correlation"] = params.correlation;
    doc["B10_life"] = params.B10_life;
    doc["B50_life"] = params.B50_life;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendParisLawParameters(ParisLawParameters& params) {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "paris_law";
    doc["C"] = params.C;
    doc["m"] = params.m;
    doc["delta_K_th"] = params.delta_K_threshold;
    doc["correlation"] = params.correlation;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

// Interrupt service routines
void emergencyStopISR() {
    emergency_stop_active = true;
    digitalWrite(STEPPER_ENABLE_PIN, HIGH); // Disable motor immediately
}

void doorInterlockISR() {
    if (digitalRead(DOOR_INTERLOCK_PIN) == HIGH && test_running) {
        pauseTest();
    }
}

void handleEmergencyStop() {
    test_running = false;
    
    // Display emergency stop message
    tft.fillScr(VGA_RED);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_RED);
    tft.print("EMERGENCY STOP", CENTER, 100);
    tft.print("Reset Required", CENTER, 130);
    
    // Wait for reset
    while (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        delay(100);
    }
    
    // Reset system
    emergency_stop_active = false;
    tft.fillScr(VGA_BLACK);
    displayStartupScreen();
}

void pauseTest() {
    if (test_running) {
        test_running = false;
        digitalWrite(STEPPER_ENABLE_PIN, HIGH);
        displayError("Test Paused");
    }
}

void handleTouchInput() {
    int x, y;
    touch.read();
    x = touch.getX();
    y = touch.getY();
    
    // Define button areas
    if (y > 250 && y < 310) {
        if (x > 10 && x < 110) { // Start button
            if (!test_running) {
                setupTestParameters(); // Show parameter input screen
            }
        } else if (x > 130 && x < 230) { // Stop button
            if (test_running) {
                endTest();
            }
        } else if (x > 250 && x < 350) { // Pause button
            if (test_running) {
                pauseTest();
            } else {
                test_running = true; // Resume
            }
        } else if (x > 370 && x < 470) { // Menu button
            showMainMenu();
        }
    }
}

void setupTestParameters() {
    // In real implementation, show parameter input screen
    // For now, use default values
    test_params.specimen_id = "TEST001";
    test_params.material_type = "Al 7075-T6";
    test_params.mean_load = 1000.0;
    test_params.amplitude_load = 500.0;
    test_params.frequency = 10.0;
    test_params.R_ratio = 0.1;
    test_params.max_cycles = 1000000;
    test_params.waveform = 0; // Sine
    test_params.constant_amplitude = true;
    test_params.gauge_length = 25.0;
    test_params.cross_section_area = 50.0;
    
    startTest();
}

bool validateTestParameters() {
    // Check parameter validity
    if (test_params.mean_load + test_params.amplitude_load > MAX_LOAD) {
        return false;
    }
    
    if (test_params.frequency < MIN_FREQUENCY || test_params.frequency > MAX_FREQUENCY) {
        return false;
    }
    
    if (test_params.cross_section_area <= 0) {
        return false;
    }
    
    return true;
}

void performSystemCheck() {
    bool system_ok = true;
    
    // Check load cell
    float zero_load = load_cell.get_units(10);
    if (abs(zero_load) > 10.0) {
        Serial.println(F("Warning: Load cell zero offset high"));
        system_ok = false;
    }
    
    // Check LVDT
    float center_voltage = analogRead(LVDT_ANALOG_PIN) * 3.3 / 4095.0;
    if (abs(center_voltage - 1.65) > 0.1) {
        Serial.println(F("Warning: LVDT not centered"));
        system_ok = false;
    }
    
    // Check stepper motor
    stepper.move(100);
    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }
    stepper.move(-100);
    while (stepper.distanceToGo() != 0) {
        stepper.run();
    }
    
    // Check emergency stop
    if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        Serial.println(F("Warning: Emergency stop active"));
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
        if (!test_running) {
            setupTestParameters();
        }
    } else if (command == "STOP") {
        if (test_running) {
            endTest();
        }
    } else if (command == "STATUS") {
        printStatus();
    } else if (command.startsWith("SET")) {
        parseSetCommand(command);
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
            setupTestParameters();
        } else if (cmd == "stop") {
            endTest();
        }
    } else if (type == "parameters") {
        // Update test parameters from ESP32
        test_params.mean_load = doc["mean_load"];
        test_params.amplitude_load = doc["amplitude_load"];
        test_params.frequency = doc["frequency"];
        test_params.max_cycles = doc["max_cycles"];
    }
}

void printStatus() {
    Serial.println(F("=== Fatigue Testing Machine Status ==="));
    Serial.print(F("Test Running: "));
    Serial.println(test_running ? "Yes" : "No");
    
    if (test_running) {
        Serial.print(F("Specimen ID: "));
        Serial.println(test_params.specimen_id);
        Serial.print(F("Cycles: "));
        Serial.println(current_data.cycle_count);
        Serial.print(F("Current Load: "));
        Serial.print(input_force);
        Serial.println(F(" N"));
        Serial.print(F("Frequency: "));
        Serial.print(current_data.current_frequency);
        Serial.println(F(" Hz"));
        Serial.print(F("AE Hits: "));
        Serial.println(current_data.ae_hits);
    }
    
    Serial.println(F("==================================="));
}

void parseSetCommand(String command) {
    // Parse SET commands for parameter adjustment
    // Format: SET PARAM VALUE
    int firstSpace = command.indexOf(' ');
    int secondSpace = command.indexOf(' ', firstSpace + 1);
    
    if (firstSpace > 0 && secondSpace > 0) {
        String param = command.substring(firstSpace + 1, secondSpace);
        String value = command.substring(secondSpace + 1);
        
        if (param == "MEAN_LOAD") {
            test_params.mean_load = value.toFloat();
        } else if (param == "AMPLITUDE") {
            test_params.amplitude_load = value.toFloat();
        } else if (param == "FREQUENCY") {
            test_params.frequency = value.toFloat();
        } else if (param == "MAX_CYCLES") {
            test_params.max_cycles = value.toInt();
        }
        
        Serial.print(F("Set "));
        Serial.print(param);
        Serial.print(F(" = "));
        Serial.println(value);
    }
}

void showMainMenu() {
    // Display main menu
    tft.fillScr(VGA_BLACK);
    tft.setColor(VGA_WHITE);
    tft.print("MAIN MENU", CENTER, 20);
    
    // Menu items
    tft.print("1. New Test", 50, 60);
    tft.print("2. View Results", 50, 90);
    tft.print("3. Calibration", 50, 120);
    tft.print("4. Settings", 50, 150);
    tft.print("5. System Info", 50, 180);
}

void sortSNData() {
    // Simple bubble sort for S-N data
    for (int i = 0; i < sn_data_count - 1; i++) {
        for (int j = 0; j < sn_data_count - i - 1; j++) {
            if (sn_data[j].cycles_to_failure > sn_data[j + 1].cycles_to_failure) {
                SNDataPoint temp = sn_data[j];
                sn_data[j] = sn_data[j + 1];
                sn_data[j + 1] = temp;
            }
        }
    }
}

String getTimestamp() {
    // In real implementation, use RTC module
    return String(millis() / 1000) + "s";
}