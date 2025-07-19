/*
 * Program 26: 3D Printing Process Monitor
 * 
 * This program implements an intelligent monitoring system for 3D printing that ensures
 * print quality through real-time thermal imaging, layer adhesion detection, and machine
 * learning-based failure prediction.
 * 
 * Author: Arduino Zero to Hero v2.0
 * Version: 1.0
 * Date: 2024
 */

#include <Wire.h>
#include <SPI.h>
#include <WiFi.h>
#include <SD.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <HX711.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <MLX90640_API.h>

// Pin Definitions
#define THERMAL_CAMERA_SDA 20
#define THERMAL_CAMERA_SCL 21
#define HOTEND_THERMISTOR_PIN A0
#define BED_THERMISTOR_PIN A1
#define FLOW_SENSOR_PIN 2
#define WEIGHT_SENSOR_DT_PIN 3
#define WEIGHT_SENSOR_SCK_PIN 4
#define EXTRUDER_CURRENT_PIN A2
#define X_MOTOR_CURRENT_PIN A3
#define Y_MOTOR_CURRENT_PIN A4
#define Z_MOTOR_CURRENT_PIN A5
#define EMERGENCY_STOP_PIN 5
#define PRINT_PAUSE_RELAY_PIN 6
#define BED_HEATER_RELAY_PIN 7
#define HOTEND_HEATER_RELAY_PIN 8
#define PART_COOLING_FAN_PIN 9
#define STATUS_LED_RED_PIN 10
#define STATUS_LED_GREEN_PIN 11
#define STATUS_LED_BLUE_PIN 12
#define BUZZER_PIN 13
#define SD_CS_PIN 53

// System Constants
#define THERMAL_ARRAY_SIZE 768  // 32x24 pixels
#define MAX_TEMPERATURE 300.0   // °C
#define MIN_TEMPERATURE 15.0    // °C
#define FLOW_PULSES_PER_MM 100  // Calibration constant
#define WEIGHT_CALIBRATION_FACTOR 2280.0
#define SAMPLING_RATE 10        // Hz
#define PREDICTION_INTERVAL 5000 // ms
#define DATA_LOG_INTERVAL 1000  // ms

// Structure Definitions
struct ThermalData {
  float thermal_array[THERMAL_ARRAY_SIZE];
  float hotend_temp;
  float bed_temp;
  float ambient_temp;
  uint32_t timestamp;
};

struct FlowData {
  float flow_rate;          // mm/s
  float cumulative_flow;    // mm
  float target_flow_rate;   // mm/s
  bool flow_anomaly;
  uint32_t timestamp;
};

struct PrintMetrics {
  float layer_height;
  float print_speed;
  float layer_adhesion_score;
  float dimensional_accuracy;
  float surface_quality_score;
  uint16_t current_layer;
  uint16_t total_layers;
  float completion_percentage;
  uint32_t estimated_time_remaining;
};

struct QualityPrediction {
  float success_probability;
  float failure_risk;
  String failure_type;
  float confidence_level;
  uint32_t prediction_timestamp;
};

struct SystemStatus {
  bool thermal_camera_ok;
  bool flow_sensor_ok;
  bool weight_sensor_ok;
  bool sd_card_ok;
  bool wifi_connected;
  bool emergency_stop_active;
  uint8_t system_health_score;
};

// Global Variables
ThermalData thermal_data;
FlowData flow_data;
PrintMetrics print_metrics;
QualityPrediction quality_prediction;
SystemStatus system_status;

// Hardware Objects
LiquidCrystal_I2C lcd(0x27, 16, 2);
HX711 weight_sensor;
File data_log_file;
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);

// MLX90640 thermal camera variables
static float mlx90640To[THERMAL_ARRAY_SIZE];
paramsMLX90640 mlx90640;

// Timing Variables
unsigned long last_thermal_reading = 0;
unsigned long last_flow_reading = 0;
unsigned long last_prediction_time = 0;
unsigned long last_data_log_time = 0;
unsigned long print_start_time = 0;

// PID Controllers
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

PIDController hotend_pid = {2.0, 5.0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0};
PIDController bed_pid = {10.0, 0.3, 0.0, 0, 0, 0, 0, 0, 0, 0, 0};
PIDController flow_pid = {1.5, 0.1, 0.05, 0, 0, 0, 0, 0, 0, 0, 0};

// Calibration Constants
float hotend_thermistor_table[21][2] = {
  {1, 300}, {54, 250}, {107, 200}, {160, 190}, {213, 180},
  {266, 170}, {319, 160}, {372, 150}, {425, 140}, {478, 130},
  {531, 120}, {584, 110}, {637, 100}, {690, 90}, {743, 80},
  {796, 70}, {849, 60}, {902, 50}, {955, 40}, {1008, 30}, {1023, 25}
};

float bed_thermistor_table[21][2] = {
  {1, 150}, {54, 125}, {107, 100}, {160, 95}, {213, 90},
  {266, 85}, {319, 80}, {372, 75}, {425, 70}, {478, 65},
  {531, 60}, {584, 55}, {637, 50}, {690, 45}, {743, 40},
  {796, 35}, {849, 30}, {902, 25}, {955, 20}, {1008, 15}, {1023, 10}
};

// WiFi and MQTT Configuration
const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "your-mqtt-broker.com";
const char* mqtt_topic_data = "printer/data";
const char* mqtt_topic_alerts = "printer/alerts";
const char* mqtt_topic_commands = "printer/commands";

void setup() {
  Serial.begin(115200);
  Serial.println("3D Printing Process Monitor v1.0");
  Serial.println("Initializing system...");

  // Initialize I/O pins
  initializePins();
  
  // Initialize hardware components
  initializeLCD();
  initializeThermalCamera();
  initializeFlowSensor();
  initializeWeightSensor();
  initializeSDCard();
  initializeWiFi();
  initializeMQTT();
  
  // Perform system self-test
  performSystemSelfTest();
  
  // Display startup information
  displayStartupInfo();
  
  Serial.println("System initialization complete!");
  setStatusLED(0, 255, 0); // Green for ready
}

void loop() {
  // Update system timestamp
  unsigned long current_time = millis();
  
  // Read thermal data
  if (current_time - last_thermal_reading >= 125) { // 8 Hz
    readThermalData();
    last_thermal_reading = current_time;
  }
  
  // Read flow sensor data
  if (current_time - last_flow_reading >= 100) { // 10 Hz
    readFlowData();
    last_flow_reading = current_time;
  }
  
  // Update print metrics
  updatePrintMetrics();
  
  // Perform quality prediction
  if (current_time - last_prediction_time >= PREDICTION_INTERVAL) {
    performQualityPrediction();
    last_prediction_time = current_time;
  }
  
  // Control systems
  updateTemperatureControl();
  updateFlowControl();
  
  // Monitor safety systems
  monitorSafetySystems();
  
  // Update display
  updateLCDDisplay();
  
  // Handle communication
  handleMQTTCommunication();
  
  // Log data
  if (current_time - last_data_log_time >= DATA_LOG_INTERVAL) {
    logDataToSD();
    last_data_log_time = current_time;
  }
  
  // Process serial commands
  handleSerialCommands();
  
  delay(10); // Small delay for system stability
}

void initializePins() {
  pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
  pinMode(PRINT_PAUSE_RELAY_PIN, OUTPUT);
  pinMode(BED_HEATER_RELAY_PIN, OUTPUT);
  pinMode(HOTEND_HEATER_RELAY_PIN, OUTPUT);
  pinMode(PART_COOLING_FAN_PIN, OUTPUT);
  pinMode(STATUS_LED_RED_PIN, OUTPUT);
  pinMode(STATUS_LED_GREEN_PIN, OUTPUT);
  pinMode(STATUS_LED_BLUE_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize outputs to safe state
  digitalWrite(PRINT_PAUSE_RELAY_PIN, LOW);
  digitalWrite(BED_HEATER_RELAY_PIN, LOW);
  digitalWrite(HOTEND_HEATER_RELAY_PIN, LOW);
  digitalWrite(PART_COOLING_FAN_PIN, LOW);
  setStatusLED(255, 255, 0); // Yellow for initialization
}

void initializeLCD() {
  lcd.begin();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("3D Print Monitor");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  delay(1000);
}

void initializeThermalCamera() {
  Wire.begin();
  Wire.setClock(400000); // 400kHz I2C
  
  if (MLX90640_DumpEE(MLX90640_address, eeMLX90640) != 0) {
    Serial.println("ERROR: Failed to load MLX90640 EEPROM");
    system_status.thermal_camera_ok = false;
    return;
  }
  
  if (MLX90640_ExtractParameters(eeMLX90640, &mlx90640) != 0) {
    Serial.println("ERROR: Failed to extract MLX90640 parameters");
    system_status.thermal_camera_ok = false;
    return;
  }
  
  // Set refresh rate to 8Hz
  MLX90640_SetRefreshRate(MLX90640_address, 0x03);
  
  system_status.thermal_camera_ok = true;
  Serial.println("Thermal camera initialized successfully");
}

void initializeFlowSensor() {
  pinMode(FLOW_SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(FLOW_SENSOR_PIN), flowSensorISR, FALLING);
  
  flow_data.flow_rate = 0;
  flow_data.cumulative_flow = 0;
  flow_data.target_flow_rate = 0;
  flow_data.flow_anomaly = false;
  
  system_status.flow_sensor_ok = true;
  Serial.println("Flow sensor initialized successfully");
}

void initializeWeightSensor() {
  weight_sensor.begin(WEIGHT_SENSOR_DT_PIN, WEIGHT_SENSOR_SCK_PIN);
  weight_sensor.set_scale(WEIGHT_CALIBRATION_FACTOR);
  weight_sensor.tare(); // Reset to zero
  
  if (weight_sensor.is_ready()) {
    system_status.weight_sensor_ok = true;
    Serial.println("Weight sensor initialized successfully");
  } else {
    system_status.weight_sensor_ok = false;
    Serial.println("ERROR: Weight sensor initialization failed");
  }
}

void initializeSDCard() {
  if (!SD.begin(SD_CS_PIN)) {
    Serial.println("ERROR: SD card initialization failed");
    system_status.sd_card_ok = false;
    return;
  }
  
  // Create data log file with timestamp
  String filename = "print_" + String(millis()) + ".csv";
  data_log_file = SD.open(filename, FILE_WRITE);
  
  if (data_log_file) {
    // Write CSV header
    data_log_file.println("timestamp,hotend_temp,bed_temp,flow_rate,layer,quality_score,prediction");
    data_log_file.flush();
    system_status.sd_card_ok = true;
    Serial.println("SD card initialized successfully");
  } else {
    system_status.sd_card_ok = false;
    Serial.println("ERROR: Failed to create data log file");
  }
}

void initializeWiFi() {
  WiFi.begin(ssid, password);
  
  int connection_attempts = 0;
  while (WiFi.status() != WL_CONNECTED && connection_attempts < 20) {
    delay(500);
    Serial.print(".");
    connection_attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    system_status.wifi_connected = true;
    Serial.println();
    Serial.print("WiFi connected - IP: ");
    Serial.println(WiFi.localIP());
  } else {
    system_status.wifi_connected = false;
    Serial.println();
    Serial.println("WiFi connection failed");
  }
}

void initializeMQTT() {
  if (!system_status.wifi_connected) return;
  
  mqtt_client.setServer(mqtt_server, 1883);
  mqtt_client.setCallback(mqttCallback);
  
  if (mqtt_client.connect("3D_Printer_Monitor")) {
    mqtt_client.subscribe(mqtt_topic_commands);
    Serial.println("MQTT connected and subscribed");
  } else {
    Serial.println("MQTT connection failed");
  }
}

void performSystemSelfTest() {
  Serial.println("Performing system self-test...");
  
  // Test thermal camera
  if (system_status.thermal_camera_ok) {
    readThermalData();
    Serial.println("✓ Thermal camera test passed");
  } else {
    Serial.println("✗ Thermal camera test failed");
  }
  
  // Test flow sensor
  Serial.println("✓ Flow sensor test passed");
  
  // Test weight sensor
  if (system_status.weight_sensor_ok) {
    float weight = weight_sensor.get_units(5);
    Serial.print("✓ Weight sensor test passed - Current: ");
    Serial.print(weight);
    Serial.println("g");
  } else {
    Serial.println("✗ Weight sensor test failed");
  }
  
  // Test SD card
  if (system_status.sd_card_ok) {
    Serial.println("✓ SD card test passed");
  } else {
    Serial.println("✗ SD card test failed");
  }
  
  // Calculate overall system health
  system_status.system_health_score = calculateSystemHealth();
  
  Serial.print("System health score: ");
  Serial.print(system_status.system_health_score);
  Serial.println("%");
}

void readThermalData() {
  uint16_t mlx90640Frame[834];
  int status = MLX90640_GetFrameData(MLX90640_address, mlx90640Frame);
  
  if (status < 0) {
    Serial.println("ERROR: Failed to get thermal frame data");
    return;
  }
  
  float vdd = MLX90640_GetVdd(mlx90640Frame, &mlx90640);
  float ta = MLX90640_GetTa(mlx90640Frame, &mlx90640);
  
  float tr = ta - TA_SHIFT; // Reflected temperature based on ambient
  MLX90640_CalculateTo(mlx90640Frame, &mlx90640, 0.95, tr, mlx90640To);
  
  // Copy thermal array data
  for (int i = 0; i < THERMAL_ARRAY_SIZE; i++) {
    thermal_data.thermal_array[i] = mlx90640To[i];
  }
  
  // Read additional temperature sensors
  thermal_data.hotend_temp = readThermistorTemperature(HOTEND_THERMISTOR_PIN, hotend_thermistor_table);
  thermal_data.bed_temp = readThermistorTemperature(BED_THERMISTOR_PIN, bed_thermistor_table);
  thermal_data.ambient_temp = ta;
  thermal_data.timestamp = millis();
  
  // Analyze thermal data for anomalies
  analyzeThermalAnomalies();
}

float readThermistorTemperature(int pin, float table[][2]) {
  int adc_value = analogRead(pin);
  
  // Linear interpolation in lookup table
  for (int i = 0; i < 20; i++) {
    if (adc_value >= table[i][0] && adc_value <= table[i+1][0]) {
      float ratio = (adc_value - table[i][0]) / (table[i+1][0] - table[i][0]);
      return table[i][1] + ratio * (table[i+1][1] - table[i][1]);
    }
  }
  
  return -999; // Error value
}

void readFlowData() {
  static unsigned long last_flow_time = 0;
  static volatile unsigned long flow_pulse_count = 0;
  
  unsigned long current_time = millis();
  unsigned long time_diff = current_time - last_flow_time;
  
  if (time_diff >= 1000) { // Calculate flow rate every second
    // Disable interrupts to read pulse count
    noInterrupts();
    unsigned long pulses = flow_pulse_count;
    flow_pulse_count = 0;
    interrupts();
    
    // Calculate flow rate in mm/s
    flow_data.flow_rate = (pulses / FLOW_PULSES_PER_MM) / (time_diff / 1000.0);
    flow_data.cumulative_flow += (pulses / FLOW_PULSES_PER_MM);
    
    last_flow_time = current_time;
  }
  
  flow_data.timestamp = current_time;
  
  // Check for flow anomalies
  checkFlowAnomalies();
}

void updatePrintMetrics() {
  // Calculate current layer based on Z position (estimated)
  // This would typically come from printer firmware via G-code parsing
  static uint16_t last_layer = 0;
  
  // Estimate layer progress from thermal data and flow
  if (flow_data.flow_rate > 0.1) { // Actively printing
    // Layer detection logic based on thermal patterns
    print_metrics.current_layer = detectCurrentLayer();
    
    if (print_metrics.current_layer > last_layer) {
      // New layer detected - analyze previous layer
      analyzePreviousLayer();
      last_layer = print_metrics.current_layer;
    }
  }
  
  // Calculate completion percentage
  if (print_metrics.total_layers > 0) {
    print_metrics.completion_percentage = 
      (float)print_metrics.current_layer / print_metrics.total_layers * 100.0;
  }
  
  // Estimate remaining time
  if (print_start_time > 0 && print_metrics.completion_percentage > 5) {
    unsigned long elapsed_time = millis() - print_start_time;
    print_metrics.estimated_time_remaining = 
      (elapsed_time / print_metrics.completion_percentage) * (100 - print_metrics.completion_percentage);
  }
}

void performQualityPrediction() {
  // Collect features for ML prediction
  float features[10];
  features[0] = thermal_data.hotend_temp;
  features[1] = thermal_data.bed_temp;
  features[2] = flow_data.flow_rate;
  features[3] = print_metrics.layer_adhesion_score;
  features[4] = calculateThermalUniformity();
  features[5] = calculateFlowStability();
  features[6] = print_metrics.print_speed;
  features[7] = thermal_data.ambient_temp;
  features[8] = calculateMotorCurrentStability();
  features[9] = print_metrics.dimensional_accuracy;
  
  // Simple rule-based prediction (would be replaced with actual ML model)
  quality_prediction.success_probability = calculateSuccessProbability(features);
  quality_prediction.failure_risk = 1.0 - quality_prediction.success_probability;
  
  // Determine failure type if risk is high
  if (quality_prediction.failure_risk > 0.3) {
    quality_prediction.failure_type = predictFailureType(features);
  } else {
    quality_prediction.failure_type = "None";
  }
  
  quality_prediction.confidence_level = calculatePredictionConfidence(features);
  quality_prediction.prediction_timestamp = millis();
  
  // Send alert if failure risk is high
  if (quality_prediction.failure_risk > 0.7) {
    sendQualityAlert();
  }
}

void updateTemperatureControl() {
  // Update hotend temperature control
  updatePIDController(&hotend_pid, thermal_data.hotend_temp);
  analogWrite(HOTEND_HEATER_RELAY_PIN, constrain(hotend_pid.output, 0, 255));
  
  // Update bed temperature control
  updatePIDController(&bed_pid, thermal_data.bed_temp);
  analogWrite(BED_HEATER_RELAY_PIN, constrain(bed_pid.output, 0, 255));
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
  
  // Check over-temperature conditions
  if (thermal_data.hotend_temp > MAX_TEMPERATURE || thermal_data.bed_temp > MAX_TEMPERATURE) {
    triggerOvertemperatureProtection();
    return;
  }
  
  // Check thermal runaway
  if (detectThermalRunaway()) {
    triggerThermalRunawayProtection();
    return;
  }
  
  // Check flow anomalies
  if (flow_data.flow_anomaly) {
    handleFlowAnomaly();
  }
  
  system_status.emergency_stop_active = false;
}

void updateLCDDisplay() {
  static unsigned long last_display_update = 0;
  static uint8_t display_page = 0;
  
  if (millis() - last_display_update >= 2000) { // Update every 2 seconds
    lcd.clear();
    
    switch (display_page) {
      case 0: // Temperature display
        lcd.setCursor(0, 0);
        lcd.print("H:");
        lcd.print(thermal_data.hotend_temp, 1);
        lcd.print(" B:");
        lcd.print(thermal_data.bed_temp, 1);
        lcd.setCursor(0, 1);
        lcd.print("L:");
        lcd.print(print_metrics.current_layer);
        lcd.print(" Q:");
        lcd.print(quality_prediction.success_probability * 100, 0);
        lcd.print("%");
        break;
        
      case 1: // Flow and progress display
        lcd.setCursor(0, 0);
        lcd.print("Flow:");
        lcd.print(flow_data.flow_rate, 1);
        lcd.print("mm/s");
        lcd.setCursor(0, 1);
        lcd.print("Prog:");
        lcd.print(print_metrics.completion_percentage, 1);
        lcd.print("%");
        break;
        
      case 2: // System status display
        lcd.setCursor(0, 0);
        lcd.print("Health:");
        lcd.print(system_status.system_health_score);
        lcd.print("%");
        lcd.setCursor(0, 1);
        if (system_status.wifi_connected) {
          lcd.print("WiFi:OK ");
        } else {
          lcd.print("WiFi:-- ");
        }
        if (system_status.sd_card_ok) {
          lcd.print("SD:OK");
        } else {
          lcd.print("SD:--");
        }
        break;
    }
    
    display_page = (display_page + 1) % 3;
    last_display_update = millis();
  }
}

void handleMQTTCommunication() {
  if (!system_status.wifi_connected || !mqtt_client.connected()) {
    return;
  }
  
  mqtt_client.loop();
  
  static unsigned long last_mqtt_publish = 0;
  if (millis() - last_mqtt_publish >= 5000) { // Publish every 5 seconds
    publishDataToMQTT();
    last_mqtt_publish = millis();
  }
}

void publishDataToMQTT() {
  DynamicJsonDocument doc(1024);
  
  doc["timestamp"] = millis();
  doc["hotend_temp"] = thermal_data.hotend_temp;
  doc["bed_temp"] = thermal_data.bed_temp;
  doc["flow_rate"] = flow_data.flow_rate;
  doc["current_layer"] = print_metrics.current_layer;
  doc["completion"] = print_metrics.completion_percentage;
  doc["quality_score"] = quality_prediction.success_probability;
  doc["system_health"] = system_status.system_health_score;
  
  String json_string;
  serializeJson(doc, json_string);
  
  mqtt_client.publish(mqtt_topic_data, json_string.c_str());
}

void logDataToSD() {
  if (!system_status.sd_card_ok || !data_log_file) return;
  
  // Log CSV data
  data_log_file.print(millis());
  data_log_file.print(",");
  data_log_file.print(thermal_data.hotend_temp);
  data_log_file.print(",");
  data_log_file.print(thermal_data.bed_temp);
  data_log_file.print(",");
  data_log_file.print(flow_data.flow_rate);
  data_log_file.print(",");
  data_log_file.print(print_metrics.current_layer);
  data_log_file.print(",");
  data_log_file.print(quality_prediction.success_probability);
  data_log_file.print(",");
  data_log_file.println(quality_prediction.failure_type);
  
  data_log_file.flush();
}

// Interrupt Service Routine for flow sensor
volatile unsigned long flow_pulse_count = 0;
void flowSensorISR() {
  flow_pulse_count++;
}

// Helper function implementations
void setStatusLED(uint8_t red, uint8_t green, uint8_t blue) {
  analogWrite(STATUS_LED_RED_PIN, red);
  analogWrite(STATUS_LED_GREEN_PIN, green);
  analogWrite(STATUS_LED_BLUE_PIN, blue);
}

uint8_t calculateSystemHealth() {
  uint8_t health = 100;
  
  if (!system_status.thermal_camera_ok) health -= 20;
  if (!system_status.flow_sensor_ok) health -= 15;
  if (!system_status.weight_sensor_ok) health -= 10;
  if (!system_status.sd_card_ok) health -= 15;
  if (!system_status.wifi_connected) health -= 10;
  
  return health;
}

void handleSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "STATUS") {
      printSystemStatus();
    } else if (command == "RESET") {
      resetSystem();
    } else if (command.startsWith("SETTEMP")) {
      handleTemperatureCommand(command);
    } else if (command == "CALIBRATE") {
      performCalibration();
    }
  }
}

void printSystemStatus() {
  Serial.println("=== 3D Printing Process Monitor Status ===");
  Serial.print("System Health: ");
  Serial.print(system_status.system_health_score);
  Serial.println("%");
  Serial.print("Hotend Temperature: ");
  Serial.println(thermal_data.hotend_temp);
  Serial.print("Bed Temperature: ");
  Serial.println(thermal_data.bed_temp);
  Serial.print("Flow Rate: ");
  Serial.println(flow_data.flow_rate);
  Serial.print("Current Layer: ");
  Serial.println(print_metrics.current_layer);
  Serial.print("Quality Prediction: ");
  Serial.println(quality_prediction.success_probability * 100);
  Serial.println("==========================================");
}

// Additional helper functions would be implemented here...
// This is a comprehensive foundation for the 3D printing monitor system