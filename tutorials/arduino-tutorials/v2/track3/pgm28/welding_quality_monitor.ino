/*
 * Program 28: Welding Quality Monitor
 * 
 * This program implements a comprehensive welding quality monitoring system that ensures
 * weld integrity through real-time parameter monitoring, defect prediction, and compliance
 * reporting. Supports MIG, TIG, and Stick welding processes.
 * 
 * Author: Arduino Zero to Hero v2.0
 * Version: 1.0
 * Date: 2024
 */

#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <ArduinoJson.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <MLX90614.h>
#include <FreqMeasure.h>

// Pin Definitions
#define CURRENT_SENSOR_PIN A0
#define VOLTAGE_SENSOR_PIN A1
#define IR_TEMP_SDA 20
#define IR_TEMP_SCL 21
#define WIRE_FEED_ENCODER_PIN 2
#define ARC_AUDIO_PIN A2
#define GAS_FLOW_SENSOR_PIN A3
#define VIBRATION_SENSOR_PIN A4
#define TORCH_ANGLE_PIN A5
#define TRAVEL_SPEED_ENCODER_PIN 3
#define EMERGENCY_STOP_PIN 4
#define PROCESS_RELAY_PIN 5
#define GAS_SOLENOID_PIN 6
#define WIRE_FEED_MOTOR_PIN 7
#define SHIELDING_MONITOR_PIN 8
#define HELMET_DISPLAY_TX 9
#define HELMET_DISPLAY_RX 10
#define STATUS_LED_RED_PIN 11
#define STATUS_LED_GREEN_PIN 12
#define STATUS_LED_BLUE_PIN 13
#define BUZZER_PIN 14
#define SD_CS_PIN 53

// System Constants
#define MAX_CURRENT 500.0       // Amperes
#define MAX_VOLTAGE 50.0        // Volts
#define MAX_WIRE_SPEED 20.0     // m/min
#define SAMPLING_RATE 10000     // Hz for electrical parameters
#define AUDIO_SAMPLING_RATE 44100 // Hz for acoustic analysis
#define DATA_LOG_INTERVAL 100   // ms
#define PREDICTION_INTERVAL 1000 // ms
#define FFT_SAMPLES 512         // For frequency analysis
#define ARC_STABILITY_WINDOW 1000 // samples

// Welding Process Types
enum WeldingProcess {
  MIG_MAG = 0,
  TIG = 1,
  STICK = 2,
  FLUX_CORED = 3
};

// Structure Definitions
struct ElectricalData {
  float current;              // Amperes
  float voltage;              // Volts
  float power;                // Watts
  float heat_input;           // kJ/mm
  float arc_stability_index;  // 0-1
  float power_factor;         // 0-1
  uint32_t timestamp;
};

struct ThermalData {
  float weld_pool_temp;       // °C
  float base_metal_temp;      // °C
  float heat_affected_zone_temp; // °C
  float cooling_rate;         // °C/s
  float interpass_temp;       // °C
  uint32_t timestamp;
};

struct MechanicalData {
  float wire_feed_speed;      // m/min
  float travel_speed;         // mm/min
  float torch_angle;          // degrees
  float contact_tip_distance; // mm
  float gas_flow_rate;        // CFH
  uint32_t timestamp;
};

struct AcousticData {
  float rms_amplitude;        // Audio RMS level
  float dominant_frequency;   // Hz
  float frequency_spectrum[256]; // FFT bins
  float spatter_index;        // 0-1
  float porosity_indicator;   // 0-1
  uint32_t timestamp;
};

struct WeldMetrics {
  float deposition_rate;      // kg/h
  float penetration_estimate; // mm
  float bead_width_estimate;  // mm
  float dilution_ratio;       // %
  float efficiency;           // %
  uint16_t pass_number;
  uint32_t arc_on_time;       // ms
  uint32_t total_weld_time;   // ms
};

struct QualityPrediction {
  float overall_quality_score; // 0-1
  float defect_probability;    // 0-1
  String defect_type;          // Primary defect risk
  float confidence_level;      // 0-1
  float tensile_strength_est;  // MPa
  float impact_toughness_est;  // J
  uint32_t prediction_time;
};

struct WeldingParameters {
  WeldingProcess process_type;
  String material_type;
  float material_thickness;    // mm
  String electrode_type;
  float electrode_diameter;    // mm
  String shielding_gas;
  float gas_flow_rate;        // CFH
  String welding_position;    // 1G, 2G, 3G, 4G, etc.
};

struct SystemStatus {
  bool current_sensor_ok;
  bool voltage_sensor_ok;
  bool ir_sensor_ok;
  bool flow_sensor_ok;
  bool audio_sensor_ok;
  bool sd_card_ok;
  bool emergency_stop_active;
  bool arc_active;
  uint8_t system_health_score;
};

// Global Variables
ElectricalData electrical_data;
ThermalData thermal_data;
MechanicalData mechanical_data;
AcousticData acoustic_data;
WeldMetrics weld_metrics;
QualityPrediction quality_prediction;
WeldingParameters weld_params;
SystemStatus system_status;

// Hardware Objects
LiquidCrystal_I2C lcd(0x27, 20, 4);
MLX90614 mlx_ir_sensor;
File data_log_file;
File wps_file; // Welding Procedure Specification

// Signal Processing Buffers
float current_buffer[ARC_STABILITY_WINDOW];
float voltage_buffer[ARC_STABILITY_WINDOW];
float audio_buffer[FFT_SAMPLES];
int buffer_index = 0;
int audio_buffer_index = 0;

// Timing Variables
unsigned long last_electrical_reading = 0;
unsigned long last_thermal_reading = 0;
unsigned long last_mechanical_reading = 0;
unsigned long last_acoustic_reading = 0;
unsigned long last_prediction_time = 0;
unsigned long last_data_log_time = 0;
unsigned long weld_start_time = 0;
unsigned long arc_start_time = 0;

// PID Controllers for Process Control
struct PIDController {
  float kp, ki, kd;
  float setpoint;
  float input;
  float output;
  float error;
  float last_error;
  float integral;
  float derivative;
  unsigned long last_time;
};

PIDController current_pid = {10.0, 2.0, 0.5, 0, 0, 0, 0, 0, 0, 0, 0};
PIDController voltage_pid = {15.0, 1.0, 0.3, 0, 0, 0, 0, 0, 0, 0, 0};
PIDController wire_feed_pid = {5.0, 1.5, 0.2, 0, 0, 0, 0, 0, 0, 0, 0};
PIDController gas_flow_pid = {8.0, 0.5, 0.1, 0, 0, 0, 0, 0, 0, 0, 0};

// Calibration Tables and Constants
float current_calibration_factor = 10.0; // A/V
float voltage_calibration_factor = 20.0; // V/V
float wire_feed_pulses_per_meter = 1000; // pulses/m
float travel_speed_pulses_per_mm = 10;   // pulses/mm
float gas_flow_calibration = 50.0;       // CFH/V

// Welding Standards and Limits
struct WeldingLimits {
  float min_current;
  float max_current;
  float min_voltage;
  float max_voltage;
  float min_travel_speed;
  float max_travel_speed;
  float min_wire_speed;
  float max_wire_speed;
  float max_interpass_temp;
  float min_preheat_temp;
};

WeldingLimits current_limits;

void setup() {
  Serial.begin(115200);
  Serial.println("Welding Quality Monitor v1.0");
  Serial.println("Initializing system...");

  // Initialize I/O pins
  initializePins();
  
  // Initialize hardware components
  initializeLCD();
  initializeCurrentSensor();
  initializeVoltageSensor();
  initializeIRSensor();
  initializeFlowSensor();
  initializeAudioSensor();
  initializeSDCard();
  
  // Initialize frequency measurement for arc analysis
  FreqMeasure.begin();
  
  // Load welding procedure specification
  loadWPS();
  
  // Perform system self-test
  performSystemSelfTest();
  
  // Display startup information
  displayStartupInfo();
  
  Serial.println("System initialization complete!");
  setStatusLED(0, 255, 0); // Green for ready
}

void loop() {
  unsigned long current_time = millis();
  
  // High-speed electrical parameter sampling
  if (current_time - last_electrical_reading >= 0.1) { // 10 kHz
    readElectricalData();
    last_electrical_reading = current_time;
  }
  
  // Thermal data reading
  if (current_time - last_thermal_reading >= 100) { // 10 Hz
    readThermalData();
    last_thermal_reading = current_time;
  }
  
  // Mechanical parameter reading
  if (current_time - last_mechanical_reading >= 50) { // 20 Hz
    readMechanicalData();
    last_mechanical_reading = current_time;
  }
  
  // Acoustic analysis
  if (current_time - last_acoustic_reading >= 23) { // ~44 Hz for audio
    readAcousticData();
    last_acoustic_reading = current_time;
  }
  
  // Update weld metrics
  updateWeldMetrics();
  
  // Perform quality prediction and defect detection
  if (current_time - last_prediction_time >= PREDICTION_INTERVAL) {
    performQualityPrediction();
    checkWeldingStandards();
    last_prediction_time = current_time;
  }
  
  // Process control systems
  updateProcessControl();
  
  // Monitor safety systems
  monitorSafetySystems();
  
  // Update displays
  updateLCDDisplay();
  updateHelmetDisplay();
  
  // Handle communication
  handleSerialCommunication();
  
  // Log data
  if (current_time - last_data_log_time >= DATA_LOG_INTERVAL) {
    logDataToSD();
    last_data_log_time = current_time;
  }
  
  delay(1); // Small delay for system stability
}

void initializePins() {
  pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
  pinMode(PROCESS_RELAY_PIN, OUTPUT);
  pinMode(GAS_SOLENOID_PIN, OUTPUT);
  pinMode(WIRE_FEED_MOTOR_PIN, OUTPUT);
  pinMode(SHIELDING_MONITOR_PIN, INPUT);
  pinMode(STATUS_LED_RED_PIN, OUTPUT);
  pinMode(STATUS_LED_GREEN_PIN, OUTPUT);
  pinMode(STATUS_LED_BLUE_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(WIRE_FEED_ENCODER_PIN, INPUT_PULLUP);
  pinMode(TRAVEL_SPEED_ENCODER_PIN, INPUT_PULLUP);
  
  // Initialize outputs to safe state
  digitalWrite(PROCESS_RELAY_PIN, LOW);
  digitalWrite(GAS_SOLENOID_PIN, LOW);
  digitalWrite(WIRE_FEED_MOTOR_PIN, LOW);
  
  // Setup interrupts for encoders
  attachInterrupt(digitalPinToInterrupt(WIRE_FEED_ENCODER_PIN), wireFeedISR, RISING);
  attachInterrupt(digitalPinToInterrupt(TRAVEL_SPEED_ENCODER_PIN), travelSpeedISR, RISING);
  
  setStatusLED(255, 255, 0); // Yellow for initialization
}

void initializeLCD() {
  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Welding Monitor v1.0");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  lcd.setCursor(0, 2);
  lcd.print("Please wait...");
  delay(2000);
}

void initializeCurrentSensor() {
  // Configure ADC for high-speed current measurement
  analogReference(EXTERNAL); // Use external 5V reference
  
  // Test current sensor
  float test_current = readCurrentSensor();
  if (test_current >= 0 && test_current <= MAX_CURRENT) {
    system_status.current_sensor_ok = true;
    Serial.println("Current sensor initialized successfully");
  } else {
    system_status.current_sensor_ok = false;
    Serial.println("ERROR: Current sensor initialization failed");
  }
}

void initializeVoltageSensor() {
  // Test voltage sensor with divider circuit
  float test_voltage = readVoltageSensor();
  if (test_voltage >= 0 && test_voltage <= MAX_VOLTAGE) {
    system_status.voltage_sensor_ok = true;
    Serial.println("Voltage sensor initialized successfully");
  } else {
    system_status.voltage_sensor_ok = false;
    Serial.println("ERROR: Voltage sensor initialization failed");
  }
}

void initializeIRSensor() {
  Wire.begin();
  mlx_ir_sensor.begin();
  
  // Test IR sensor communication
  if (mlx_ir_sensor.begin()) {
    system_status.ir_sensor_ok = true;
    Serial.println("IR temperature sensor initialized successfully");
  } else {
    system_status.ir_sensor_ok = false;
    Serial.println("ERROR: IR sensor initialization failed");
  }
}

void initializeFlowSensor() {
  // Initialize gas flow sensor
  pinMode(GAS_FLOW_SENSOR_PIN, INPUT);
  
  // Test flow sensor
  float test_flow = readGasFlowSensor();
  if (test_flow >= 0 && test_flow <= 100) {
    system_status.flow_sensor_ok = true;
    Serial.println("Gas flow sensor initialized successfully");
  } else {
    system_status.flow_sensor_ok = false;
    Serial.println("ERROR: Gas flow sensor initialization failed");
  }
}

void initializeAudioSensor() {
  // Configure audio input for acoustic analysis
  pinMode(ARC_AUDIO_PIN, INPUT);
  
  // Initialize audio processing buffers
  for (int i = 0; i < FFT_SAMPLES; i++) {
    audio_buffer[i] = 0;
  }
  
  system_status.audio_sensor_ok = true;
  Serial.println("Audio sensor initialized successfully");
}

void initializeSDCard() {
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("ERROR: SD card initialization failed");
    system_status.sd_card_ok = false;
    return;
  }
  
  // Create data log file with timestamp
  String filename = "weld_" + String(millis()) + ".csv";
  data_log_file = SD.open(filename, FILE_WRITE);
  
  if (data_log_file) {
    // Write CSV header
    data_log_file.println("timestamp,current,voltage,power,heat_input,wire_speed,travel_speed,weld_temp,quality_score,defect_type");
    data_log_file.flush();
    system_status.sd_card_ok = true;
    Serial.println("SD card initialized successfully");
  } else {
    system_status.sd_card_ok = false;
    Serial.println("ERROR: Failed to create data log file");
  }
}

void readElectricalData() {
  // Read current and voltage at high speed
  electrical_data.current = readCurrentSensor();
  electrical_data.voltage = readVoltageSensor();
  electrical_data.power = electrical_data.current * electrical_data.voltage;
  electrical_data.timestamp = millis();
  
  // Add to circular buffers for stability analysis
  current_buffer[buffer_index] = electrical_data.current;
  voltage_buffer[buffer_index] = electrical_data.voltage;
  buffer_index = (buffer_index + 1) % ARC_STABILITY_WINDOW;
  
  // Calculate arc stability index
  if (buffer_index == 0) { // Buffer is full
    electrical_data.arc_stability_index = calculateArcStability();
  }
  
  // Calculate power factor (for AC welding)
  electrical_data.power_factor = calculatePowerFactor();
  
  // Calculate heat input
  electrical_data.heat_input = calculateHeatInput();
  
  // Detect arc state
  system_status.arc_active = (electrical_data.current > 5.0 && electrical_data.voltage > 8.0);
  
  if (system_status.arc_active && arc_start_time == 0) {
    arc_start_time = millis();
  } else if (!system_status.arc_active && arc_start_time > 0) {
    weld_metrics.arc_on_time += (millis() - arc_start_time);
    arc_start_time = 0;
  }
}

float readCurrentSensor() {
  int adc_value = analogRead(CURRENT_SENSOR_PIN);
  float voltage = (adc_value / 1023.0) * 5.0;
  
  // Convert to current using Hall effect sensor (ACS712)
  // Vout = 2.5V + (Sensitivity * Current)
  // For ACS712-30A: Sensitivity = 66mV/A
  float current = (voltage - 2.5) / 0.066;
  
  return abs(current); // Return absolute value
}

float readVoltageSensor() {
  int adc_value = analogRead(VOLTAGE_SENSOR_PIN);
  float divided_voltage = (adc_value / 1023.0) * 5.0;
  
  // Convert from divided voltage to actual voltage
  // Voltage divider: R1=100kΩ, R2=10kΩ (11:1 ratio)
  float actual_voltage = divided_voltage * 11.0;
  
  return actual_voltage;
}

void readThermalData() {
  // Read weld pool temperature using IR sensor
  thermal_data.weld_pool_temp = mlx_ir_sensor.readObjectTempC();
  thermal_data.base_metal_temp = mlx_ir_sensor.readAmbientTempC();
  
  // Estimate heat affected zone temperature
  thermal_data.heat_affected_zone_temp = estimateHAZTemperature();
  
  // Calculate cooling rate
  static float last_weld_temp = 0;
  static unsigned long last_temp_time = 0;
  
  if (last_temp_time > 0) {
    float temp_diff = thermal_data.weld_pool_temp - last_weld_temp;
    float time_diff = (millis() - last_temp_time) / 1000.0; // seconds
    thermal_data.cooling_rate = temp_diff / time_diff;
  }
  
  last_weld_temp = thermal_data.weld_pool_temp;
  last_temp_time = millis();
  
  thermal_data.timestamp = millis();
}

void readMechanicalData() {
  // Wire feed speed calculation from encoder
  static volatile unsigned long wire_feed_pulses = 0;
  static unsigned long last_wire_time = 0;
  
  if (millis() - last_wire_time >= 1000) { // Calculate every second
    mechanical_data.wire_feed_speed = (wire_feed_pulses / wire_feed_pulses_per_meter) * 60.0; // m/min
    wire_feed_pulses = 0;
    last_wire_time = millis();
  }
  
  // Travel speed calculation from encoder
  static volatile unsigned long travel_pulses = 0;
  static unsigned long last_travel_time = 0;
  
  if (millis() - last_travel_time >= 1000) { // Calculate every second
    mechanical_data.travel_speed = (travel_pulses / travel_speed_pulses_per_mm) * 60.0; // mm/min
    travel_pulses = 0;
    last_travel_time = millis();
  }
  
  // Read torch angle from accelerometer/inclinometer
  mechanical_data.torch_angle = readTorchAngle();
  
  // Estimate contact tip to work distance
  mechanical_data.contact_tip_distance = estimateContactTipDistance();
  
  // Read gas flow rate
  mechanical_data.gas_flow_rate = readGasFlowSensor();
  
  mechanical_data.timestamp = millis();
}

float readGasFlowSensor() {
  int adc_value = analogRead(GAS_FLOW_SENSOR_PIN);
  float voltage = (adc_value / 1023.0) * 5.0;
  
  // Convert voltage to flow rate (CFH)
  // Linear sensor: 0-5V = 0-50 CFH
  float flow_rate = voltage * 10.0;
  
  return flow_rate;
}

float readTorchAngle() {
  int adc_value = analogRead(TORCH_ANGLE_PIN);
  float voltage = (adc_value / 1023.0) * 5.0;
  
  // Convert to angle (assuming accelerometer output)
  // 2.5V = 0°, 1V/g sensitivity
  float angle = (voltage - 2.5) * 90.0; // Approximate angle in degrees
  
  return angle;
}

void readAcousticData() {
  // Read audio sample
  int audio_sample = analogRead(ARC_AUDIO_PIN);
  float audio_voltage = (audio_sample / 1023.0) * 5.0;
  
  // Add to audio buffer
  audio_buffer[audio_buffer_index] = audio_voltage - 2.5; // Remove DC bias
  audio_buffer_index = (audio_buffer_index + 1) % FFT_SAMPLES;
  
  // When buffer is full, perform FFT analysis
  if (audio_buffer_index == 0) {
    performAcousticAnalysis();
  }
  
  acoustic_data.timestamp = millis();
}

void performAcousticAnalysis() {
  // Calculate RMS amplitude
  float sum_squares = 0;
  for (int i = 0; i < FFT_SAMPLES; i++) {
    sum_squares += audio_buffer[i] * audio_buffer[i];
  }
  acoustic_data.rms_amplitude = sqrt(sum_squares / FFT_SAMPLES);
  
  // Simple frequency analysis (would use FFT library in practice)
  acoustic_data.dominant_frequency = findDominantFrequency();
  
  // Calculate spatter index based on high-frequency content
  acoustic_data.spatter_index = calculateSpatterIndex();
  
  // Calculate porosity indicator based on frequency patterns
  acoustic_data.porosity_indicator = calculatePorosityIndicator();
}

float calculateArcStability() {
  // Calculate coefficient of variation for current
  float current_mean = 0;
  float current_var = 0;
  
  for (int i = 0; i < ARC_STABILITY_WINDOW; i++) {
    current_mean += current_buffer[i];
  }
  current_mean /= ARC_STABILITY_WINDOW;
  
  for (int i = 0; i < ARC_STABILITY_WINDOW; i++) {
    float diff = current_buffer[i] - current_mean;
    current_var += diff * diff;
  }
  current_var /= ARC_STABILITY_WINDOW;
  
  float current_std = sqrt(current_var);
  float cv = current_std / current_mean;
  
  // Convert to stability index (lower CV = higher stability)
  return constrain(1.0 - cv, 0.0, 1.0);
}

float calculateHeatInput() {
  // Heat Input (kJ/mm) = (Voltage × Current × 60) / (1000 × Travel Speed)
  if (mechanical_data.travel_speed > 0) {
    return (electrical_data.voltage * electrical_data.current * 60.0) / 
           (1000.0 * mechanical_data.travel_speed);
  }
  return 0;
}

void updateWeldMetrics() {
  // Calculate deposition rate (simplified)
  if (mechanical_data.wire_feed_speed > 0) {
    float wire_area = PI * pow(weld_params.electrode_diameter / 2000.0, 2); // m²
    float wire_density = 7850.0; // kg/m³ for steel
    weld_metrics.deposition_rate = mechanical_data.wire_feed_speed * wire_area * wire_density * 60.0; // kg/h
  }
  
  // Estimate penetration based on heat input and travel speed
  weld_metrics.penetration_estimate = estimatePenetration();
  
  // Estimate bead width
  weld_metrics.bead_width_estimate = estimateBeadWidth();
  
  // Calculate welding efficiency
  weld_metrics.efficiency = calculateWeldingEfficiency();
  
  // Update total weld time
  if (system_status.arc_active) {
    weld_metrics.total_weld_time = millis() - weld_start_time;
  }
}

void performQualityPrediction() {
  // Collect features for quality prediction
  float features[15];
  features[0] = electrical_data.current / MAX_CURRENT;
  features[1] = electrical_data.voltage / MAX_VOLTAGE;
  features[2] = electrical_data.heat_input / 5.0; // Normalize to typical range
  features[3] = electrical_data.arc_stability_index;
  features[4] = mechanical_data.wire_feed_speed / MAX_WIRE_SPEED;
  features[5] = mechanical_data.travel_speed / 1000.0; // mm/min to normalized
  features[6] = mechanical_data.gas_flow_rate / 50.0; // CFH normalized
  features[7] = thermal_data.weld_pool_temp / 2000.0; // °C normalized
  features[8] = thermal_data.cooling_rate / 100.0; // °C/s normalized
  features[9] = acoustic_data.rms_amplitude;
  features[10] = acoustic_data.spatter_index;
  features[11] = acoustic_data.porosity_indicator;
  features[12] = abs(mechanical_data.torch_angle) / 45.0; // Angle normalized
  features[13] = weld_metrics.deposition_rate / 10.0; // kg/h normalized
  features[14] = weld_metrics.efficiency;
  
  // Simple rule-based quality prediction (would use ML model in practice)
  quality_prediction.overall_quality_score = calculateQualityScore(features);
  quality_prediction.defect_probability = 1.0 - quality_prediction.overall_quality_score;
  
  // Predict dominant defect type
  quality_prediction.defect_type = predictDefectType(features);
  
  // Calculate confidence based on feature consistency
  quality_prediction.confidence_level = calculatePredictionConfidence(features);
  
  // Estimate mechanical properties
  quality_prediction.tensile_strength_est = estimateTensileStrength(features);
  quality_prediction.impact_toughness_est = estimateImpactToughness(features);
  
  quality_prediction.prediction_time = millis();
  
  // Generate alerts if quality is poor
  if (quality_prediction.overall_quality_score < 0.7) {
    generateQualityAlert();
  }
}

float calculateQualityScore(float* features) {
  float score = 1.0;
  
  // Penalize for poor arc stability
  if (features[3] < 0.8) score *= 0.9;
  
  // Penalize for excessive heat input
  if (features[2] > 0.8) score *= 0.8;
  
  // Penalize for poor gas coverage
  if (features[6] < 0.3 || features[6] > 0.9) score *= 0.85;
  
  // Penalize for high spatter
  if (features[10] > 0.5) score *= 0.9;
  
  // Penalize for porosity indicators
  if (features[11] > 0.3) score *= 0.8;
  
  // Penalize for extreme torch angles
  if (features[12] > 0.7) score *= 0.9;
  
  return constrain(score, 0.0, 1.0);
}

String predictDefectType(float* features) {
  // Rule-based defect prediction
  if (features[11] > 0.4) return "Porosity";
  if (features[10] > 0.6) return "Excessive_Spatter";
  if (features[2] > 0.9) return "Burn_Through";
  if (features[2] < 0.2) return "Lack_of_Penetration";
  if (features[3] < 0.6) return "Poor_Arc_Stability";
  if (features[6] < 0.2) return "Poor_Gas_Coverage";
  if (features[12] > 0.8) return "Poor_Torch_Angle";
  
  return "None";
}

void checkWeldingStandards() {
  // Check against AWS/ISO standards
  bool standards_ok = true;
  String violations = "";
  
  // Check current limits
  if (electrical_data.current < current_limits.min_current || 
      electrical_data.current > current_limits.max_current) {
    standards_ok = false;
    violations += "Current out of range; ";
  }
  
  // Check voltage limits
  if (electrical_data.voltage < current_limits.min_voltage || 
      electrical_data.voltage > current_limits.max_voltage) {
    standards_ok = false;
    violations += "Voltage out of range; ";
  }
  
  // Check travel speed
  if (mechanical_data.travel_speed < current_limits.min_travel_speed || 
      mechanical_data.travel_speed > current_limits.max_travel_speed) {
    standards_ok = false;
    violations += "Travel speed out of range; ";
  }
  
  // Check interpass temperature
  if (thermal_data.base_metal_temp > current_limits.max_interpass_temp) {
    standards_ok = false;
    violations += "Interpass temperature exceeded; ";
  }
  
  if (!standards_ok) {
    Serial.print("STANDARDS VIOLATION: ");
    Serial.println(violations);
    generateComplianceAlert(violations);
  }
}

void updateProcessControl() {
  // Only control if in automatic mode and arc is active
  if (!system_status.arc_active) return;
  
  // Current control
  updatePIDController(&current_pid, electrical_data.current);
  
  // Voltage control (if available)
  updatePIDController(&voltage_pid, electrical_data.voltage);
  
  // Wire feed speed control
  updatePIDController(&wire_feed_pid, mechanical_data.wire_feed_speed);
  analogWrite(WIRE_FEED_MOTOR_PIN, constrain(wire_feed_pid.output, 0, 255));
  
  // Gas flow control
  updatePIDController(&gas_flow_pid, mechanical_data.gas_flow_rate);
}

void updatePIDController(PIDController* pid, float input) {
  unsigned long now = millis();
  unsigned long time_change = now - pid->last_time;
  
  if (time_change >= 100) { // Update every 100ms
    pid->input = input;
    pid->error = pid->setpoint - pid->input;
    
    pid->integral += pid->error * time_change;
    pid->derivative = (pid->error - pid->last_error) / time_change;
    
    pid->output = pid->kp * pid->error + 
                  pid->ki * pid->integral + 
                  pid->kd * pid->derivative;
    
    // Clamp output
    pid->output = constrain(pid->output, -255, 255);
    
    pid->last_error = pid->error;
    pid->last_time = now;
  }
}

void monitorSafetySystems() {
  // Check emergency stop
  if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
    triggerEmergencyStop();
    return;
  }
  
  // Check overcurrent condition
  if (electrical_data.current > MAX_CURRENT * 1.1) {
    triggerOvercurrentProtection();
    return;
  }
  
  // Check overvoltage condition
  if (electrical_data.voltage > MAX_VOLTAGE * 1.1) {
    triggerOvervoltageProtection();
    return;
  }
  
  // Check gas flow
  if (system_status.arc_active && mechanical_data.gas_flow_rate < 5.0) {
    handleLowGasFlow();
  }
  
  // Check excessive heat input
  if (electrical_data.heat_input > 10.0) { // kJ/mm
    handleExcessiveHeatInput();
  }
  
  system_status.emergency_stop_active = false;
}

void updateLCDDisplay() {
  static unsigned long last_display_update = 0;
  static uint8_t display_page = 0;
  
  if (millis() - last_display_update >= 1000) { // Update every second
    lcd.clear();
    
    switch (display_page) {
      case 0: // Electrical parameters
        lcd.setCursor(0, 0);
        lcd.print("Current: ");
        lcd.print(electrical_data.current, 1);
        lcd.print("A");
        
        lcd.setCursor(0, 1);
        lcd.print("Voltage: ");
        lcd.print(electrical_data.voltage, 1);
        lcd.print("V");
        
        lcd.setCursor(0, 2);
        lcd.print("Power: ");
        lcd.print(electrical_data.power, 1);
        lcd.print("W");
        
        lcd.setCursor(0, 3);
        lcd.print("Arc Stability: ");
        lcd.print(electrical_data.arc_stability_index * 100, 0);
        lcd.print("%");
        break;
        
      case 1: // Thermal and mechanical
        lcd.setCursor(0, 0);
        lcd.print("Weld Temp: ");
        lcd.print(thermal_data.weld_pool_temp, 0);
        lcd.print("C");
        
        lcd.setCursor(0, 1);
        lcd.print("Wire Speed: ");
        lcd.print(mechanical_data.wire_feed_speed, 1);
        lcd.print("m/min");
        
        lcd.setCursor(0, 2);
        lcd.print("Travel: ");
        lcd.print(mechanical_data.travel_speed, 0);
        lcd.print("mm/min");
        
        lcd.setCursor(0, 3);
        lcd.print("Gas Flow: ");
        lcd.print(mechanical_data.gas_flow_rate, 1);
        lcd.print("CFH");
        break;
        
      case 2: // Quality prediction
        lcd.setCursor(0, 0);
        lcd.print("Quality Score: ");
        lcd.print(quality_prediction.overall_quality_score * 100, 0);
        lcd.print("%");
        
        lcd.setCursor(0, 1);
        lcd.print("Defect Risk: ");
        lcd.print(quality_prediction.defect_probability * 100, 0);
        lcd.print("%");
        
        lcd.setCursor(0, 2);
        lcd.print("Defect Type:");
        
        lcd.setCursor(0, 3);
        lcd.print(quality_prediction.defect_type);
        break;
        
      case 3: // System status
        lcd.setCursor(0, 0);
        lcd.print("System Health: ");
        lcd.print(system_status.system_health_score);
        lcd.print("%");
        
        lcd.setCursor(0, 1);
        lcd.print("Arc: ");
        lcd.print(system_status.arc_active ? "ON" : "OFF");
        lcd.print(" Time: ");
        lcd.print(weld_metrics.arc_on_time / 1000);
        lcd.print("s");
        
        lcd.setCursor(0, 2);
        lcd.print("Heat Input: ");
        lcd.print(electrical_data.heat_input, 2);
        lcd.print("kJ/mm");
        
        lcd.setCursor(0, 3);
        lcd.print("Deposition: ");
        lcd.print(weld_metrics.deposition_rate, 1);
        lcd.print("kg/h");
        break;
    }
    
    display_page = (display_page + 1) % 4;
    last_display_update = millis();
  }
}

void logDataToSD() {
  if (!system_status.sd_card_ok || !data_log_file) return;
  
  // Log comprehensive weld data
  data_log_file.print(millis());
  data_log_file.print(",");
  data_log_file.print(electrical_data.current);
  data_log_file.print(",");
  data_log_file.print(electrical_data.voltage);
  data_log_file.print(",");
  data_log_file.print(electrical_data.power);
  data_log_file.print(",");
  data_log_file.print(electrical_data.heat_input);
  data_log_file.print(",");
  data_log_file.print(mechanical_data.wire_feed_speed);
  data_log_file.print(",");
  data_log_file.print(mechanical_data.travel_speed);
  data_log_file.print(",");
  data_log_file.print(thermal_data.weld_pool_temp);
  data_log_file.print(",");
  data_log_file.print(quality_prediction.overall_quality_score);
  data_log_file.print(",");
  data_log_file.println(quality_prediction.defect_type);
  
  data_log_file.flush();
}

// Interrupt Service Routines
volatile unsigned long wire_feed_pulse_count = 0;
volatile unsigned long travel_pulse_count = 0;

void wireFeedISR() {
  wire_feed_pulse_count++;
}

void travelSpeedISR() {
  travel_pulse_count++;
}

// Helper functions
void setStatusLED(uint8_t red, uint8_t green, uint8_t blue) {
  analogWrite(STATUS_LED_RED_PIN, red);
  analogWrite(STATUS_LED_GREEN_PIN, green);
  analogWrite(STATUS_LED_BLUE_PIN, blue);
}

void generateQualityAlert() {
  // Sound alarm pattern
  for (int i = 0; i < 3; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    delay(200);
  }
  
  // Set LED to warning color
  setStatusLED(255, 165, 0); // Orange
  
  // Send alert message
  Serial.print("QUALITY ALERT: Score=");
  Serial.print(quality_prediction.overall_quality_score * 100);
  Serial.print("%, Defect=");
  Serial.println(quality_prediction.defect_type);
}

// Additional helper functions would be implemented here...
// This provides a comprehensive foundation for the welding quality monitoring system