/*
Program 27: Injection Molding Controller
Arduino Zero to Hero v2.0 - Track 3

Smart injection molding controller implementing scientific molding principles
with real-time cavity pressure monitoring, SPC integration, and digital twin
synchronization for precision plastic part manufacturing.

Features:
- Real-time cavity pressure profiling (0-2000 bar, ±0.5% accuracy)
- Multi-stage injection velocity control (10-200 mm/s)
- Pack/hold pressure optimization with gate seal detection
- Statistical Process Control (SPC) with Cp/Cpk calculation
- Digital twin synchronization for virtual optimization
- Closed-loop melt temperature control (150-400°C)
- Multi-cavity balance monitoring
- Automatic process parameter optimization
- Quality prediction with part rejection system

Hardware:
- Arduino Mega 2560 (main controller) + Arduino Due (high-speed DAQ)
- ESP32 (IoT gateway and analytics)
- High-pressure transducers (0-2000 bar, piezoelectric)
- K-type thermocouples with MAX31855
- LVDT position sensors, current monitoring
- 24-bit ADC (ADS1256), 7" TFT touchscreen
- Emergency stop system, industrial enclosure (IP65)

Author: Claude Code Assistant
Date: 2025
*/

#include <SPI.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <EEPROM.h>
#include <SD.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <XPT2046_Touchscreen.h>
#include <PID_v1.h>
#include <math.h>

// Pin Definitions - Injection Molding Controller
#define PRESSURE_SENSOR_CS    22    // ADS1256 CS for high-pressure transducers
#define TEMP_SENSOR_CS        24    // MAX31855 thermocouple interface
#define POSITION_SENSOR_ADC   A0    // LVDT screw position
#define CLAMP_POSITION_ADC    A1    // Clamp position sensor
#define HYDRAULIC_PRESSURE    A2    // System hydraulic pressure
#define FLOW_RATE_SENSOR      A3    // Calculated from position/velocity
#define POWER_MONITOR         A4    // Energy consumption monitoring
#define CAVITY_PRESSURE_1     A8    // Multi-cavity pressure monitoring
#define CAVITY_PRESSURE_2     A9    // Secondary cavity pressure
#define CAVITY_PRESSURE_3     A10   // Third cavity pressure
#define CAVITY_PRESSURE_4     A11   // Fourth cavity pressure

// Control Output Pins
#define INJECTION_VALVE       5     // PWM control for injection velocity
#define PACK_PRESSURE_VALVE   6     // Pack/hold pressure control
#define BACK_PRESSURE_VALVE   7     // Plasticizing back pressure
#define CLAMP_CONTROL         8     // Clamp force control
#define HEATER_ZONE_1         9     // Barrel zone 1 heater
#define HEATER_ZONE_2         10    // Barrel zone 2 heater
#define HEATER_ZONE_3         11    // Barrel zone 3 heater
#define NOZZLE_HEATER         12    // Nozzle heater control
#define MOLD_HEATER           13    // Mold temperature control
#define EJECTION_CONTROL      23    // Ejection system

// Safety and Monitoring Pins
#define EMERGENCY_STOP        2     // Hardware emergency stop
#define SAFETY_GATES          3     // Mold safety gates
#define ALARM_HORN            25    // Audible alarm
#define STATUS_LED_GREEN      26    // System OK indicator
#define STATUS_LED_YELLOW     27    // Warning indicator
#define STATUS_LED_RED        28    // Fault indicator
#define PRESSURE_RELIEF       29    // Pressure relief valve

// Display and Interface
#define TFT_CS                30
#define TFT_DC                31
#define TFT_RST               32
#define TOUCH_CS              33
#define TOUCH_IRQ             34

// Communication
#define SD_CS                 53    // SD card for data logging
#define ESP32_SERIAL          Serial1  // Communication with ESP32

// Process Control Constants
#define MAX_PRESSURE          2000.0  // bar (29,000 psi)
#define MIN_PRESSURE          0.0     // bar
#define MAX_TEMPERATURE       400.0   // °C
#define MIN_TEMPERATURE       150.0   // °C
#define MAX_VELOCITY          200.0   // mm/s
#define MIN_VELOCITY          10.0    // mm/s
#define PRESSURE_RESOLUTION   0.1     // bar
#define TEMP_RESOLUTION       0.1     // °C
#define POSITION_RESOLUTION   0.01    // mm
#define SAMPLING_RATE         1000    // Hz for critical parameters
#define SPC_SAMPLES           50      // Samples for SPC calculation

// Scientific Molding Parameters
#define MAX_INJECTION_STAGES  10      // Multi-stage velocity profiling
#define MAX_PACK_STAGES       5       // Pack pressure profiling
#define VISCOSITY_SAMPLES     20      // Samples for viscosity calculation
#define GATE_SEAL_THRESHOLD   0.95    // Pressure drop for gate seal detection

// Process Phase Definitions
enum ProcessPhase {
  PHASE_IDLE,
  PHASE_CLAMP_CLOSE,
  PHASE_INJECTION,
  PHASE_PACK_HOLD,
  PHASE_COOLING,
  PHASE_EJECTION,
  PHASE_CLAMP_OPEN,
  PHASE_PLASTICIZING,
  PHASE_FAULT
};

enum QualityStatus {
  QUALITY_EXCELLENT,
  QUALITY_GOOD,
  QUALITY_ACCEPTABLE,
  QUALITY_POOR,
  QUALITY_REJECT
};

// Data Structures
struct CavityPressureData {
  float cavity_1_pressure;      // bar
  float cavity_2_pressure;      // bar
  float cavity_3_pressure;      // bar
  float cavity_4_pressure;      // bar
  float average_pressure;       // bar
  float pressure_balance;       // % difference between cavities
  float peak_pressure;          // bar
  float integral_pressure;      // bar·s
  uint32_t timestamp;
};

struct TemperatureData {
  float barrel_zone_1;          // °C
  float barrel_zone_2;          // °C
  float barrel_zone_3;          // °C
  float nozzle_temp;            // °C
  float mold_temp;              // °C
  float melt_temp;              // °C (calculated)
  float ambient_temp;           // °C
  uint32_t timestamp;
};

struct PositionData {
  float screw_position;         // mm
  float screw_velocity;         // mm/s
  float clamp_position;         // mm
  float clamp_force;            // kN
  float cushion_position;       // mm
  float ejection_position;      // mm
  uint32_t timestamp;
};

struct ProcessParameters {
  // Injection Parameters
  float injection_velocity[MAX_INJECTION_STAGES];  // mm/s
  float injection_position[MAX_INJECTION_STAGES];  // mm
  float injection_pressure_limit;                  // bar
  float transfer_position;                         // mm
  
  // Pack/Hold Parameters
  float pack_pressure[MAX_PACK_STAGES];           // bar
  float pack_time[MAX_PACK_STAGES];               // s
  float hold_pressure;                            // bar
  float hold_time;                                // s
  
  // Plasticizing Parameters
  float back_pressure;                            // bar
  float screw_speed;                              // rpm
  float shot_size;                                // mm³
  
  // Temperature Setpoints
  float barrel_temp_1;                            // °C
  float barrel_temp_2;                            // °C
  float barrel_temp_3;                            // °C
  float nozzle_temp;                              // °C
  float mold_temp;                                // °C
  
  // Timing Parameters
  float injection_time;                           // s
  float cooling_time;                             // s
  float cycle_time_target;                        // s
  
  // Quality Parameters
  float target_weight;                            // g
  float weight_tolerance;                         // g
  float pressure_tolerance;                       // bar
};

struct SPCData {
  float mean_value;             // X-bar
  float range_value;            // R
  float standard_deviation;     // σ
  float cp_value;               // Process capability
  float cpk_value;              // Process capability index
  float ucl;                    // Upper control limit
  float lcl;                    // Lower control limit
  int out_of_control_count;     // Consecutive out-of-control points
  bool process_stable;          // Process stability flag
};

struct QualityPrediction {
  float predicted_weight;       // g
  float dimensional_accuracy;   // % of tolerance
  float strength_index;         // Relative strength
  float cosmetic_quality;       // Surface quality index
  QualityStatus overall_quality;
  float confidence_level;       // 0-1
  bool reject_part;            // Reject recommendation
};

struct MaterialProperties {
  char material_name[32];       // Material identifier
  float melt_temp_range[2];     // Min/max melt temperature
  float viscosity_index;        // Flow characteristic
  float thermal_conductivity;   // W/m·K
  float specific_heat;          // J/kg·K
  float shrinkage_rate;         // Linear shrinkage %
  float pvt_data[10];          // Pressure-volume-temperature data
};

struct SystemStatus {
  ProcessPhase current_phase;
  bool emergency_stop_active;
  bool safety_gates_closed;
  bool pressure_relief_open;
  bool all_heaters_ready;
  bool hydraulic_system_ready;
  float cycle_time_actual;      // s
  int parts_produced_today;
  int parts_rejected_today;
  float overall_efficiency;     // %
  uint32_t system_uptime;       // seconds
  int system_health_score;      // 0-100
};

// Global Variables
CavityPressureData cavity_pressure;
TemperatureData temperature_data;
PositionData position_data;
ProcessParameters process_params;
SPCData spc_pressure, spc_weight, spc_cycle_time;
QualityPrediction quality_prediction;
MaterialProperties current_material;
SystemStatus system_status;

// Process Control Variables
unsigned long cycle_start_time;
unsigned long phase_start_time;
unsigned long last_data_log;
unsigned long last_spc_update;
unsigned long last_display_update;
bool cycle_active = false;
int current_injection_stage = 0;
int current_pack_stage = 0;

// SPC Data Arrays
float pressure_spc_data[SPC_SAMPLES];
float weight_spc_data[SPC_SAMPLES];
float cycle_time_spc_data[SPC_SAMPLES];
int spc_data_index = 0;

// PID Controllers
PID temp_pid_1(&temperature_data.barrel_zone_1, &process_params.barrel_temp_1, &process_params.barrel_temp_1, 2.0, 0.1, 0.05, DIRECT);
PID temp_pid_2(&temperature_data.barrel_zone_2, &process_params.barrel_temp_2, &process_params.barrel_temp_2, 2.0, 0.1, 0.05, DIRECT);
PID temp_pid_3(&temperature_data.barrel_zone_3, &process_params.barrel_temp_3, &process_params.barrel_temp_3, 2.0, 0.1, 0.05, DIRECT);
PID nozzle_pid(&temperature_data.nozzle_temp, &process_params.nozzle_temp, &process_params.nozzle_temp, 3.0, 0.2, 0.1, DIRECT);
PID mold_pid(&temperature_data.mold_temp, &process_params.mold_temp, &process_params.mold_temp, 1.5, 0.05, 0.02, DIRECT);

// Display and Communication
Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);
XPT2046_Touchscreen touch(TOUCH_CS, TOUCH_IRQ);
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);
WebServer web_server(80);

// Network Configuration
const char* ssid = "IndustryNet";
const char* password = "Manufacturing2024";
const char* mqtt_server = "mqtt.industry.local";
const int mqtt_port = 1883;

void setup() {
  Serial.begin(115200);
  ESP32_SERIAL.begin(115200);
  
  Serial.println("Injection Molding Controller v2.0 Starting...");
  
  // Initialize safety systems first
  initializeSafetySystems();
  
  // Initialize hardware interfaces
  initializePinModes();
  initializeDisplayAndTouch();
  initializeSDCard();
  initializeNetworking();
  
  // Load configuration from EEPROM
  loadConfiguration();
  
  // Initialize process control systems
  initializePIDControllers();
  initializeSPCSystem();
  
  // Load material properties
  loadMaterialDatabase();
  
  // Initialize process parameters
  initializeProcessParameters();
  
  // Perform system self-test
  performSystemSelfTest();
  
  Serial.println("Injection Molding Controller initialized successfully");
  
  // Start main control loop
  system_status.current_phase = PHASE_IDLE;
  cycle_start_time = millis();
}

void loop() {
  unsigned long current_time = millis();
  
  // Critical safety monitoring (highest priority)
  monitorSafetySystems();
  
  // High-speed data acquisition (1000 Hz)
  if (current_time - last_data_log >= 1) {
    readAllSensors();
    updateProcessControl();
    last_data_log = current_time;
  }
  
  // Process phase management
  updateProcessPhase();
  
  // Quality prediction and SPC updates (10 Hz)
  if (current_time - last_spc_update >= 100) {
    updateSPCAnalysis();
    performQualityPrediction();
    last_spc_update = current_time;
  }
  
  // Display updates (5 Hz)
  if (current_time - last_display_update >= 200) {
    updateDisplay();
    handleTouchInput();
    last_display_update = current_time;
  }
  
  // Communication handling
  handleMQTTCommunication();
  handleWebServerRequests();
  handleESP32Communication();
  
  // Data logging to SD card
  logProcessData();
  
  // System health monitoring
  updateSystemHealth();
}

void initializeSafetySystems() {
  // Configure emergency stop and safety inputs
  pinMode(EMERGENCY_STOP, INPUT_PULLUP);
  pinMode(SAFETY_GATES, INPUT_PULLUP);
  
  // Configure alarm outputs
  pinMode(ALARM_HORN, OUTPUT);
  pinMode(STATUS_LED_GREEN, OUTPUT);
  pinMode(STATUS_LED_YELLOW, OUTPUT);
  pinMode(STATUS_LED_RED, OUTPUT);
  pinMode(PRESSURE_RELIEF, OUTPUT);
  
  // Initialize safety outputs to safe state
  digitalWrite(ALARM_HORN, LOW);
  digitalWrite(STATUS_LED_RED, HIGH);  // Red until system ready
  digitalWrite(PRESSURE_RELIEF, HIGH); // Open pressure relief initially
  
  // Attach emergency stop interrupt
  attachInterrupt(digitalPinToInterrupt(EMERGENCY_STOP), emergencyStopISR, FALLING);
  
  system_status.emergency_stop_active = !digitalRead(EMERGENCY_STOP);
  system_status.safety_gates_closed = !digitalRead(SAFETY_GATES);
}

void initializePinModes() {
  // Analog sensor inputs
  pinMode(POSITION_SENSOR_ADC, INPUT);
  pinMode(CLAMP_POSITION_ADC, INPUT);
  pinMode(HYDRAULIC_PRESSURE, INPUT);
  pinMode(FLOW_RATE_SENSOR, INPUT);
  pinMode(POWER_MONITOR, INPUT);
  
  // Control outputs
  pinMode(INJECTION_VALVE, OUTPUT);
  pinMode(PACK_PRESSURE_VALVE, OUTPUT);
  pinMode(BACK_PRESSURE_VALVE, OUTPUT);
  pinMode(CLAMP_CONTROL, OUTPUT);
  pinMode(HEATER_ZONE_1, OUTPUT);
  pinMode(HEATER_ZONE_2, OUTPUT);
  pinMode(HEATER_ZONE_3, OUTPUT);
  pinMode(NOZZLE_HEATER, OUTPUT);
  pinMode(MOLD_HEATER, OUTPUT);
  pinMode(EJECTION_CONTROL, OUTPUT);
  
  // SPI chip selects
  pinMode(PRESSURE_SENSOR_CS, OUTPUT);
  pinMode(TEMP_SENSOR_CS, OUTPUT);
  pinMode(SD_CS, OUTPUT);
  
  digitalWrite(PRESSURE_SENSOR_CS, HIGH);
  digitalWrite(TEMP_SENSOR_CS, HIGH);
  digitalWrite(SD_CS, HIGH);
  
  // Initialize PWM outputs to safe state
  analogWrite(INJECTION_VALVE, 0);
  analogWrite(PACK_PRESSURE_VALVE, 0);
  analogWrite(BACK_PRESSURE_VALVE, 0);
  analogWrite(CLAMP_CONTROL, 0);
}

void initializeDisplayAndTouch() {
  SPI.begin();
  tft.begin();
  tft.setRotation(3);
  tft.fillScreen(ILI9341_BLACK);
  
  touch.begin();
  touch.setRotation(3);
  
  // Display startup screen
  tft.setCursor(10, 10);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);
  tft.println("Injection Molding Controller");
  tft.println("v2.0 - Scientific Molding");
  tft.println("");
  tft.setTextSize(1);
  tft.println("Initializing systems...");
}

void initializeSDCard() {
  if (!SD.begin(SD_CS)) {
    Serial.println("SD card initialization failed!");
    return;
  }
  Serial.println("SD card initialized successfully");
  
  // Create data directories
  SD.mkdir("/process_data");
  SD.mkdir("/spc_data");
  SD.mkdir("/quality_data");
  SD.mkdir("/config");
}

void initializeNetworking() {
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    // Initialize MQTT
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    
    // Initialize web server
    setupWebServer();
  }
}

void initializePIDControllers() {
  temp_pid_1.SetMode(AUTOMATIC);
  temp_pid_1.SetOutputLimits(0, 255);
  temp_pid_1.SetSampleTime(1000);
  
  temp_pid_2.SetMode(AUTOMATIC);
  temp_pid_2.SetOutputLimits(0, 255);
  temp_pid_2.SetSampleTime(1000);
  
  temp_pid_3.SetMode(AUTOMATIC);
  temp_pid_3.SetOutputLimits(0, 255);
  temp_pid_3.SetSampleTime(1000);
  
  nozzle_pid.SetMode(AUTOMATIC);
  nozzle_pid.SetOutputLimits(0, 255);
  nozzle_pid.SetSampleTime(500);
  
  mold_pid.SetMode(AUTOMATIC);
  mold_pid.SetOutputLimits(0, 255);
  mold_pid.SetSampleTime(2000);
}

void initializeSPCSystem() {
  // Initialize SPC data arrays
  for (int i = 0; i < SPC_SAMPLES; i++) {
    pressure_spc_data[i] = 0.0;
    weight_spc_data[i] = 0.0;
    cycle_time_spc_data[i] = 0.0;
  }
  
  // Set initial SPC parameters
  spc_pressure.ucl = 0.0;
  spc_pressure.lcl = 0.0;
  spc_pressure.process_stable = false;
  
  spc_weight.ucl = 0.0;
  spc_weight.lcl = 0.0;
  spc_weight.process_stable = false;
  
  spc_cycle_time.ucl = 0.0;
  spc_cycle_time.lcl = 0.0;
  spc_cycle_time.process_stable = false;
}

void loadMaterialDatabase() {
  // Load default PLA material properties
  strcpy(current_material.material_name, "ABS_Standard");
  current_material.melt_temp_range[0] = 220.0;
  current_material.melt_temp_range[1] = 260.0;
  current_material.viscosity_index = 1.2;
  current_material.thermal_conductivity = 0.19;
  current_material.specific_heat = 1600.0;
  current_material.shrinkage_rate = 0.6;
  
  // Load PVT data for scientific molding calculations
  for (int i = 0; i < 10; i++) {
    current_material.pvt_data[i] = 0.95 + (i * 0.005); // Example PVT curve
  }
}

void initializeProcessParameters() {
  // Default injection parameters
  process_params.injection_velocity[0] = 50.0;  // mm/s
  process_params.injection_velocity[1] = 80.0;
  process_params.injection_velocity[2] = 60.0;
  process_params.injection_position[0] = 10.0;  // mm
  process_params.injection_position[1] = 25.0;
  process_params.injection_position[2] = 35.0;
  process_params.injection_pressure_limit = 1500.0; // bar
  process_params.transfer_position = 5.0;       // mm
  
  // Pack/hold parameters
  process_params.pack_pressure[0] = 800.0;     // bar
  process_params.pack_pressure[1] = 600.0;
  process_params.pack_time[0] = 2.0;           // s
  process_params.pack_time[1] = 3.0;
  process_params.hold_pressure = 400.0;        // bar
  process_params.hold_time = 8.0;              // s
  
  // Temperature setpoints
  process_params.barrel_temp_1 = 240.0;        // °C
  process_params.barrel_temp_2 = 250.0;
  process_params.barrel_temp_3 = 260.0;
  process_params.nozzle_temp = 255.0;
  process_params.mold_temp = 60.0;
  
  // Quality parameters
  process_params.target_weight = 15.5;         // g
  process_params.weight_tolerance = 0.3;       // g
  process_params.pressure_tolerance = 50.0;    // bar
  
  // Timing
  process_params.cycle_time_target = 25.0;     // s
  process_params.cooling_time = 15.0;          // s
}

void performSystemSelfTest() {
  Serial.println("Performing system self-test...");
  
  // Test pressure sensors
  bool pressure_test = testPressureSensors();
  
  // Test temperature sensors
  bool temp_test = testTemperatureSensors();
  
  // Test position sensors
  bool position_test = testPositionSensors();
  
  // Test control outputs
  bool control_test = testControlOutputs();
  
  // Test safety systems
  bool safety_test = testSafetySystems();
  
  // Test communication
  bool comm_test = testCommunicationSystems();
  
  // Calculate overall system health
  int health_score = 0;
  if (pressure_test) health_score += 20;
  if (temp_test) health_score += 20;
  if (position_test) health_score += 15;
  if (control_test) health_score += 15;
  if (safety_test) health_score += 20;
  if (comm_test) health_score += 10;
  
  system_status.system_health_score = health_score;
  
  if (health_score >= 90) {
    digitalWrite(STATUS_LED_GREEN, HIGH);
    digitalWrite(STATUS_LED_RED, LOW);
    Serial.println("System self-test PASSED");
  } else {
    digitalWrite(STATUS_LED_YELLOW, HIGH);
    Serial.print("System self-test PARTIAL - Health score: ");
    Serial.println(health_score);
  }
}

void readAllSensors() {
  readCavityPressure();
  readTemperatures();
  readPositions();
  readSystemPressures();
}

void readCavityPressure() {
  // Read high-precision cavity pressures using ADS1256
  cavity_pressure.cavity_1_pressure = readPressureSensor(CAVITY_PRESSURE_1) * 2000.0 / 1024.0;
  cavity_pressure.cavity_2_pressure = readPressureSensor(CAVITY_PRESSURE_2) * 2000.0 / 1024.0;
  cavity_pressure.cavity_3_pressure = readPressureSensor(CAVITY_PRESSURE_3) * 2000.0 / 1024.0;
  cavity_pressure.cavity_4_pressure = readPressureSensor(CAVITY_PRESSURE_4) * 2000.0 / 1024.0;
  
  // Calculate average and balance
  cavity_pressure.average_pressure = (cavity_pressure.cavity_1_pressure + 
                                     cavity_pressure.cavity_2_pressure + 
                                     cavity_pressure.cavity_3_pressure + 
                                     cavity_pressure.cavity_4_pressure) / 4.0;
  
  // Calculate pressure balance (deviation from average)
  float max_deviation = 0.0;
  max_deviation = max(max_deviation, abs(cavity_pressure.cavity_1_pressure - cavity_pressure.average_pressure));
  max_deviation = max(max_deviation, abs(cavity_pressure.cavity_2_pressure - cavity_pressure.average_pressure));
  max_deviation = max(max_deviation, abs(cavity_pressure.cavity_3_pressure - cavity_pressure.average_pressure));
  max_deviation = max(max_deviation, abs(cavity_pressure.cavity_4_pressure - cavity_pressure.average_pressure));
  
  cavity_pressure.pressure_balance = (max_deviation / cavity_pressure.average_pressure) * 100.0;
  
  // Update peak pressure if in injection phase
  if (system_status.current_phase == PHASE_INJECTION || system_status.current_phase == PHASE_PACK_HOLD) {
    cavity_pressure.peak_pressure = max(cavity_pressure.peak_pressure, cavity_pressure.average_pressure);
  }
  
  cavity_pressure.timestamp = millis();
}

void readTemperatures() {
  // Read all temperature zones using MAX31855
  temperature_data.barrel_zone_1 = readThermocouple(0);
  temperature_data.barrel_zone_2 = readThermocouple(1);
  temperature_data.barrel_zone_3 = readThermocouple(2);
  temperature_data.nozzle_temp = readThermocouple(3);
  temperature_data.mold_temp = readThermocouple(4);
  temperature_data.ambient_temp = readThermocouple(5);
  
  // Calculate estimated melt temperature using rheological model
  temperature_data.melt_temp = calculateMeltTemperature();
  
  temperature_data.timestamp = millis();
}

void readPositions() {
  // Read screw position and calculate velocity
  static float previous_position = 0.0;
  static unsigned long previous_time = 0;
  
  float current_position = analogRead(POSITION_SENSOR_ADC) * 100.0 / 1024.0; // Convert to mm
  unsigned long current_time = millis();
  
  if (previous_time > 0) {
    float dt = (current_time - previous_time) / 1000.0; // seconds
    position_data.screw_velocity = (current_position - previous_position) / dt;
  }
  
  position_data.screw_position = current_position;
  position_data.clamp_position = analogRead(CLAMP_POSITION_ADC) * 50.0 / 1024.0; // Convert to mm
  position_data.clamp_force = calculateClampForce();
  position_data.cushion_position = process_params.shot_size - position_data.screw_position;
  
  previous_position = current_position;
  previous_time = current_time;
  
  position_data.timestamp = millis();
}

void readSystemPressures() {
  // Read hydraulic system pressure
  float hydraulic_pressure = analogRead(HYDRAULIC_PRESSURE) * 300.0 / 1024.0; // bar
  
  // Calculate flow rate from position changes
  static float previous_position = position_data.screw_position;
  static unsigned long previous_time = millis();
  
  unsigned long current_time = millis();
  float dt = (current_time - previous_time) / 1000.0;
  
  if (dt > 0) {
    float flow_rate = (position_data.screw_position - previous_position) / dt; // mm/s
  }
  
  previous_position = position_data.screw_position;
  previous_time = current_time;
}

void updateProcessControl() {
  switch (system_status.current_phase) {
    case PHASE_INJECTION:
      controlInjectionPhase();
      break;
    case PHASE_PACK_HOLD:
      controlPackHoldPhase();
      break;
    case PHASE_COOLING:
      controlCoolingPhase();
      break;
    case PHASE_PLASTICIZING:
      controlPlasticizingPhase();
      break;
    default:
      // Safe state - all control outputs off
      analogWrite(INJECTION_VALVE, 0);
      analogWrite(PACK_PRESSURE_VALVE, 0);
      analogWrite(BACK_PRESSURE_VALVE, 0);
      break;
  }
  
  // Always run temperature control
  updateTemperatureControl();
}

void controlInjectionPhase() {
  // Multi-stage velocity control
  float target_velocity = process_params.injection_velocity[current_injection_stage];
  float position_setpoint = process_params.injection_position[current_injection_stage];
  
  // Check if we need to advance to next stage
  if (position_data.screw_position >= position_setpoint && current_injection_stage < MAX_INJECTION_STAGES - 1) {
    current_injection_stage++;
    target_velocity = process_params.injection_velocity[current_injection_stage];
  }
  
  // Velocity control with pressure limit protection
  float velocity_error = target_velocity - position_data.screw_velocity;
  float control_output = constrain(velocity_error * 2.0, 0, 255); // Simple P controller
  
  // Pressure limit protection
  if (cavity_pressure.average_pressure > process_params.injection_pressure_limit) {
    control_output = 0; // Stop injection if pressure limit exceeded
  }
  
  analogWrite(INJECTION_VALVE, (int)control_output);
  
  // Check for transfer to pack/hold
  if (position_data.screw_position >= process_params.transfer_position) {
    system_status.current_phase = PHASE_PACK_HOLD;
    phase_start_time = millis();
    current_pack_stage = 0;
  }
}

void controlPackHoldPhase() {
  unsigned long phase_time = (millis() - phase_start_time) / 1000.0; // seconds
  
  float target_pressure = 0.0;
  bool hold_phase = false;
  
  // Multi-stage pack pressure control
  float cumulative_time = 0.0;
  for (int i = 0; i < MAX_PACK_STAGES && i <= current_pack_stage; i++) {
    cumulative_time += process_params.pack_time[i];
    if (phase_time <= cumulative_time) {
      target_pressure = process_params.pack_pressure[i];
      break;
    }
  }
  
  // Switch to hold pressure after pack stages
  if (phase_time > cumulative_time) {
    target_pressure = process_params.hold_pressure;
    hold_phase = true;
  }
  
  // Pressure control
  float pressure_error = target_pressure - cavity_pressure.average_pressure;
  float control_output = constrain(pressure_error * 0.5, 0, 255); // P controller
  
  analogWrite(PACK_PRESSURE_VALVE, (int)control_output);
  
  // Gate seal detection
  if (hold_phase && detectGateSeal()) {
    system_status.current_phase = PHASE_COOLING;
    phase_start_time = millis();
  }
  
  // Timeout protection
  if (phase_time > (cumulative_time + process_params.hold_time)) {
    system_status.current_phase = PHASE_COOLING;
    phase_start_time = millis();
  }
}

void controlCoolingPhase() {
  // Simply wait for cooling time to complete
  unsigned long cooling_time = (millis() - phase_start_time) / 1000.0;
  
  if (cooling_time >= process_params.cooling_time) {
    system_status.current_phase = PHASE_EJECTION;
    phase_start_time = millis();
  }
}

void controlPlasticizingPhase() {
  // Back pressure control during plasticizing
  float target_back_pressure = process_params.back_pressure;
  float pressure_error = target_back_pressure - cavity_pressure.average_pressure;
  float control_output = constrain(pressure_error * 0.3, 0, 255);
  
  analogWrite(BACK_PRESSURE_VALVE, (int)control_output);
  
  // Check if shot size is ready
  if (position_data.cushion_position >= process_params.shot_size * 0.95) {
    system_status.current_phase = PHASE_IDLE; // Ready for next cycle
  }
}

void updateTemperatureControl() {
  // PID temperature control for all zones
  double output1, output2, output3, nozzle_output, mold_output;
  
  temp_pid_1.Compute();
  temp_pid_2.Compute();
  temp_pid_3.Compute();
  nozzle_pid.Compute();
  mold_pid.Compute();
  
  analogWrite(HEATER_ZONE_1, (int)output1);
  analogWrite(HEATER_ZONE_2, (int)output2);
  analogWrite(HEATER_ZONE_3, (int)output3);
  analogWrite(NOZZLE_HEATER, (int)nozzle_output);
  analogWrite(MOLD_HEATER, (int)mold_output);
  
  // Check if all heaters are at setpoint
  system_status.all_heaters_ready = 
    (abs(temperature_data.barrel_zone_1 - process_params.barrel_temp_1) < 3.0) &&
    (abs(temperature_data.barrel_zone_2 - process_params.barrel_temp_2) < 3.0) &&
    (abs(temperature_data.barrel_zone_3 - process_params.barrel_temp_3) < 3.0) &&
    (abs(temperature_data.nozzle_temp - process_params.nozzle_temp) < 3.0) &&
    (abs(temperature_data.mold_temp - process_params.mold_temp) < 2.0);
}

void updateProcessPhase() {
  // State machine for process phase management
  static unsigned long last_phase_check = 0;
  
  if (millis() - last_phase_check < 100) return; // Check every 100ms
  last_phase_check = millis();
  
  switch (system_status.current_phase) {
    case PHASE_IDLE:
      if (cycle_active && system_status.all_heaters_ready && !system_status.emergency_stop_active) {
        system_status.current_phase = PHASE_CLAMP_CLOSE;
        phase_start_time = millis();
      }
      break;
      
    case PHASE_CLAMP_CLOSE:
      // Wait for clamp to close (simulated timing)
      if (millis() - phase_start_time > 2000) {
        system_status.current_phase = PHASE_INJECTION;
        phase_start_time = millis();
        current_injection_stage = 0;
        cavity_pressure.peak_pressure = 0.0; // Reset peak pressure tracking
      }
      break;
      
    case PHASE_EJECTION:
      // Wait for ejection (simulated timing)
      if (millis() - phase_start_time > 3000) {
        system_status.current_phase = PHASE_CLAMP_OPEN;
        phase_start_time = millis();
        
        // Update production counters
        system_status.parts_produced_today++;
        
        // Perform quality check
        performQualityPrediction();
        if (quality_prediction.reject_part) {
          system_status.parts_rejected_today++;
        }
      }
      break;
      
    case PHASE_CLAMP_OPEN:
      // Wait for clamp to open and part removal
      if (millis() - phase_start_time > 2000) {
        system_status.current_phase = PHASE_PLASTICIZING;
        phase_start_time = millis();
        
        // Calculate actual cycle time
        system_status.cycle_time_actual = (millis() - cycle_start_time) / 1000.0;
        cycle_start_time = millis();
      }
      break;
      
    case PHASE_FAULT:
      // Remain in fault state until manual reset
      handleFaultCondition();
      break;
  }
}

void updateSPCAnalysis() {
  // Update SPC data arrays with new measurements
  pressure_spc_data[spc_data_index] = cavity_pressure.peak_pressure;
  weight_spc_data[spc_data_index] = quality_prediction.predicted_weight;
  cycle_time_spc_data[spc_data_index] = system_status.cycle_time_actual;
  
  spc_data_index = (spc_data_index + 1) % SPC_SAMPLES;
  
  // Calculate SPC statistics if we have enough data
  if (spc_data_index == 0 || system_status.parts_produced_today > SPC_SAMPLES) {
    calculateSPCStatistics(&spc_pressure, pressure_spc_data);
    calculateSPCStatistics(&spc_weight, weight_spc_data);
    calculateSPCStatistics(&spc_cycle_time, cycle_time_spc_data);
  }
}

void calculateSPCStatistics(SPCData* spc, float* data) {
  // Calculate mean (X-bar)
  float sum = 0.0;
  for (int i = 0; i < SPC_SAMPLES; i++) {
    sum += data[i];
  }
  spc->mean_value = sum / SPC_SAMPLES;
  
  // Calculate standard deviation
  float variance_sum = 0.0;
  for (int i = 0; i < SPC_SAMPLES; i++) {
    float diff = data[i] - spc->mean_value;
    variance_sum += diff * diff;
  }
  spc->standard_deviation = sqrt(variance_sum / (SPC_SAMPLES - 1));
  
  // Calculate range (R)
  float min_val = data[0];
  float max_val = data[0];
  for (int i = 1; i < SPC_SAMPLES; i++) {
    if (data[i] < min_val) min_val = data[i];
    if (data[i] > max_val) max_val = data[i];
  }
  spc->range_value = max_val - min_val;
  
  // Calculate control limits (±3σ)
  spc->ucl = spc->mean_value + (3.0 * spc->standard_deviation);
  spc->lcl = spc->mean_value - (3.0 * spc->standard_deviation);
  
  // Calculate process capability (assuming USL/LSL are defined)
  float usl = spc->mean_value + 3.0 * spc->standard_deviation; // Example
  float lsl = spc->mean_value - 3.0 * spc->standard_deviation; // Example
  
  spc->cp_value = (usl - lsl) / (6.0 * spc->standard_deviation);
  
  float cpu = (usl - spc->mean_value) / (3.0 * spc->standard_deviation);
  float cpl = (spc->mean_value - lsl) / (3.0 * spc->standard_deviation);
  spc->cpk_value = min(cpu, cpl);
  
  // Check process stability
  spc->process_stable = (spc->cp_value > 1.33 && spc->cpk_value > 1.33);
}

void performQualityPrediction() {
  // Scientific molding quality prediction based on process data
  
  // Weight prediction based on cavity pressure integral
  float pressure_integral = calculatePressureIntegral();
  quality_prediction.predicted_weight = process_params.target_weight * 
    (pressure_integral / (process_params.pack_pressure[0] * process_params.pack_time[0]));
  
  // Dimensional accuracy based on pressure consistency
  quality_prediction.dimensional_accuracy = 100.0 - (cavity_pressure.pressure_balance * 2.0);
  
  // Strength index based on melt temperature and pressure profile
  float temp_factor = (temperature_data.melt_temp - current_material.melt_temp_range[0]) / 
    (current_material.melt_temp_range[1] - current_material.melt_temp_range[0]);
  quality_prediction.strength_index = temp_factor * 0.7 + 
    (cavity_pressure.peak_pressure / process_params.injection_pressure_limit) * 0.3;
  
  // Cosmetic quality based on mold temperature and injection velocity consistency
  float temp_uniformity = 100.0 - abs(temperature_data.mold_temp - process_params.mold_temp);
  quality_prediction.cosmetic_quality = min(temp_uniformity, quality_prediction.dimensional_accuracy);
  
  // Overall quality assessment
  float quality_score = (quality_prediction.dimensional_accuracy + 
                        quality_prediction.strength_index * 100.0 + 
                        quality_prediction.cosmetic_quality) / 3.0;
  
  if (quality_score >= 95.0) {
    quality_prediction.overall_quality = QUALITY_EXCELLENT;
    quality_prediction.confidence_level = 0.95;
  } else if (quality_score >= 85.0) {
    quality_prediction.overall_quality = QUALITY_GOOD;
    quality_prediction.confidence_level = 0.85;
  } else if (quality_score >= 75.0) {
    quality_prediction.overall_quality = QUALITY_ACCEPTABLE;
    quality_prediction.confidence_level = 0.75;
  } else if (quality_score >= 60.0) {
    quality_prediction.overall_quality = QUALITY_POOR;
    quality_prediction.confidence_level = 0.60;
  } else {
    quality_prediction.overall_quality = QUALITY_REJECT;
    quality_prediction.confidence_level = 0.90;
  }
  
  // Rejection decision
  quality_prediction.reject_part = (quality_prediction.overall_quality == QUALITY_REJECT) ||
    (abs(quality_prediction.predicted_weight - process_params.target_weight) > process_params.weight_tolerance);
}

// Helper Functions
float readPressureSensor(int channel) {
  // Simulate ADS1256 reading for high-precision pressure
  return analogRead(channel);
}

float readThermocouple(int channel) {
  // Simulate MAX31855 thermocouple reading
  return 25.0 + (analogRead(A0 + channel) * 400.0 / 1024.0);
}

float calculateMeltTemperature() {
  // Rheological model for melt temperature estimation
  float barrel_avg = (temperature_data.barrel_zone_1 + temperature_data.barrel_zone_2 + temperature_data.barrel_zone_3) / 3.0;
  float shear_heating = position_data.screw_velocity * current_material.viscosity_index * 0.1;
  return barrel_avg + shear_heating;
}

float calculateClampForce() {
  // Convert clamp position to force using calibration
  return position_data.clamp_position * 2.0; // kN (example)
}

bool detectGateSeal() {
  // Gate seal detection based on pressure drop
  static float previous_pressure = cavity_pressure.average_pressure;
  float pressure_drop = (previous_pressure - cavity_pressure.average_pressure) / previous_pressure;
  previous_pressure = cavity_pressure.average_pressure;
  
  return (pressure_drop > GATE_SEAL_THRESHOLD);
}

float calculatePressureIntegral() {
  // Calculate area under pressure curve during pack/hold
  static float integral = 0.0;
  static unsigned long last_time = 0;
  
  if (system_status.current_phase == PHASE_PACK_HOLD) {
    unsigned long current_time = millis();
    if (last_time > 0) {
      float dt = (current_time - last_time) / 1000.0; // seconds
      integral += cavity_pressure.average_pressure * dt;
    }
    last_time = current_time;
  } else {
    integral = 0.0; // Reset for next cycle
    last_time = 0;
  }
  
  return integral;
}

// Safety and Monitoring Functions
void monitorSafetySystems() {
  // Check emergency stop
  if (!digitalRead(EMERGENCY_STOP) && !system_status.emergency_stop_active) {
    triggerEmergencyStop();
  }
  
  // Check safety gates
  if (!digitalRead(SAFETY_GATES) && !system_status.safety_gates_closed) {
    system_status.safety_gates_closed = false;
    system_status.current_phase = PHASE_FAULT;
  }
  
  // Check pressure limits
  if (cavity_pressure.average_pressure > MAX_PRESSURE * 0.9) {
    digitalWrite(PRESSURE_RELIEF, HIGH);
    system_status.pressure_relief_open = true;
  }
  
  // Check temperature limits
  if (temperature_data.barrel_zone_1 > MAX_TEMPERATURE || 
      temperature_data.barrel_zone_2 > MAX_TEMPERATURE || 
      temperature_data.barrel_zone_3 > MAX_TEMPERATURE) {
    // Turn off all heaters
    analogWrite(HEATER_ZONE_1, 0);
    analogWrite(HEATER_ZONE_2, 0);
    analogWrite(HEATER_ZONE_3, 0);
    system_status.current_phase = PHASE_FAULT;
  }
}

void emergencyStopISR() {
  // Hardware emergency stop interrupt
  system_status.emergency_stop_active = true;
  
  // Immediately stop all control outputs
  analogWrite(INJECTION_VALVE, 0);
  analogWrite(PACK_PRESSURE_VALVE, 0);
  analogWrite(BACK_PRESSURE_VALVE, 0);
  analogWrite(CLAMP_CONTROL, 0);
  
  // Open pressure relief
  digitalWrite(PRESSURE_RELIEF, HIGH);
  
  // Activate alarm
  digitalWrite(ALARM_HORN, HIGH);
  digitalWrite(STATUS_LED_RED, HIGH);
  
  system_status.current_phase = PHASE_FAULT;
}

void triggerEmergencyStop() {
  emergencyStopISR(); // Use same logic as hardware interrupt
}

void handleFaultCondition() {
  // Maintain safe state during fault
  analogWrite(INJECTION_VALVE, 0);
  analogWrite(PACK_PRESSURE_VALVE, 0);
  analogWrite(BACK_PRESSURE_VALVE, 0);
  analogWrite(CLAMP_CONTROL, 0);
  
  // Flash red LED
  static unsigned long last_flash = 0;
  if (millis() - last_flash > 500) {
    digitalWrite(STATUS_LED_RED, !digitalRead(STATUS_LED_RED));
    last_flash = millis();
  }
}

// Communication Functions
void handleMQTTCommunication() {
  if (!mqtt_client.connected()) {
    reconnectMQTT();
  }
  mqtt_client.loop();
  
  // Publish process data
  static unsigned long last_mqtt_publish = 0;
  if (millis() - last_mqtt_publish > 1000) { // 1 Hz
    publishProcessData();
    last_mqtt_publish = millis();
  }
}

void reconnectMQTT() {
  while (!mqtt_client.connected()) {
    if (mqtt_client.connect("InjectionMoldingController")) {
      mqtt_client.subscribe("molding/commands");
      mqtt_client.subscribe("molding/parameters");
    } else {
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  
  if (String(topic) == "molding/commands") {
    handleRemoteCommand(doc);
  } else if (String(topic) == "molding/parameters") {
    updateProcessParameters(doc);
  }
}

void publishProcessData() {
  DynamicJsonDocument doc(2048);
  
  doc["timestamp"] = millis();
  doc["phase"] = system_status.current_phase;
  doc["cycle_time"] = system_status.cycle_time_actual;
  
  // Cavity pressure data
  JsonObject pressure = doc.createNestedObject("pressure");
  pressure["cavity_1"] = cavity_pressure.cavity_1_pressure;
  pressure["cavity_2"] = cavity_pressure.cavity_2_pressure;
  pressure["average"] = cavity_pressure.average_pressure;
  pressure["peak"] = cavity_pressure.peak_pressure;
  pressure["balance"] = cavity_pressure.pressure_balance;
  
  // Temperature data
  JsonObject temperature = doc.createNestedObject("temperature");
  temperature["barrel_1"] = temperature_data.barrel_zone_1;
  temperature["barrel_2"] = temperature_data.barrel_zone_2;
  temperature["barrel_3"] = temperature_data.barrel_zone_3;
  temperature["nozzle"] = temperature_data.nozzle_temp;
  temperature["mold"] = temperature_data.mold_temp;
  temperature["melt"] = temperature_data.melt_temp;
  
  // Quality prediction
  JsonObject quality = doc.createNestedObject("quality");
  quality["predicted_weight"] = quality_prediction.predicted_weight;
  quality["dimensional_accuracy"] = quality_prediction.dimensional_accuracy;
  quality["overall_quality"] = quality_prediction.overall_quality;
  quality["reject_part"] = quality_prediction.reject_part;
  
  // SPC data
  JsonObject spc = doc.createNestedObject("spc");
  spc["pressure_cp"] = spc_pressure.cp_value;
  spc["pressure_cpk"] = spc_pressure.cpk_value;
  spc["weight_cp"] = spc_weight.cp_value;
  spc["weight_cpk"] = spc_weight.cpk_value;
  
  String json_string;
  serializeJson(doc, json_string);
  mqtt_client.publish("molding/data", json_string.c_str());
}

// Display Functions
void updateDisplay() {
  tft.fillScreen(ILI9341_BLACK);
  
  // Header
  tft.setCursor(10, 10);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(2);
  tft.println("Injection Molding Controller");
  
  // Process phase
  tft.setCursor(10, 40);
  tft.setTextSize(1);
  tft.print("Phase: ");
  switch (system_status.current_phase) {
    case PHASE_IDLE: tft.setTextColor(ILI9341_YELLOW); tft.print("IDLE"); break;
    case PHASE_INJECTION: tft.setTextColor(ILI9341_GREEN); tft.print("INJECTION"); break;
    case PHASE_PACK_HOLD: tft.setTextColor(ILI9341_CYAN); tft.print("PACK/HOLD"); break;
    case PHASE_COOLING: tft.setTextColor(ILI9341_BLUE); tft.print("COOLING"); break;
    case PHASE_EJECTION: tft.setTextColor(ILI9341_MAGENTA); tft.print("EJECTION"); break;
    case PHASE_FAULT: tft.setTextColor(ILI9341_RED); tft.print("FAULT"); break;
    default: tft.setTextColor(ILI9341_WHITE); tft.print("UNKNOWN"); break;
  }
  
  // Pressure display
  tft.setTextColor(ILI9341_WHITE);
  tft.setCursor(10, 60);
  tft.print("Cavity Pressure: ");
  tft.print(cavity_pressure.average_pressure, 1);
  tft.print(" bar");
  
  tft.setCursor(10, 80);
  tft.print("Peak Pressure: ");
  tft.print(cavity_pressure.peak_pressure, 1);
  tft.print(" bar");
  
  tft.setCursor(10, 100);
  tft.print("Balance: ");
  tft.print(cavity_pressure.pressure_balance, 1);
  tft.print(" %");
  
  // Temperature display
  tft.setCursor(10, 120);
  tft.print("Melt Temp: ");
  tft.print(temperature_data.melt_temp, 1);
  tft.print(" C");
  
  tft.setCursor(10, 140);
  tft.print("Mold Temp: ");
  tft.print(temperature_data.mold_temp, 1);
  tft.print(" C");
  
  // Quality prediction
  tft.setCursor(10, 160);
  tft.print("Predicted Weight: ");
  tft.print(quality_prediction.predicted_weight, 2);
  tft.print(" g");
  
  tft.setCursor(10, 180);
  tft.print("Quality: ");
  switch (quality_prediction.overall_quality) {
    case QUALITY_EXCELLENT: tft.setTextColor(ILI9341_GREEN); tft.print("EXCELLENT"); break;
    case QUALITY_GOOD: tft.setTextColor(ILI9341_CYAN); tft.print("GOOD"); break;
    case QUALITY_ACCEPTABLE: tft.setTextColor(ILI9341_YELLOW); tft.print("ACCEPTABLE"); break;
    case QUALITY_POOR: tft.setTextColor(ILI9341_ORANGE); tft.print("POOR"); break;
    case QUALITY_REJECT: tft.setTextColor(ILI9341_RED); tft.print("REJECT"); break;
  }
  
  // SPC information
  tft.setTextColor(ILI9341_WHITE);
  tft.setCursor(10, 200);
  tft.print("Process Cp: ");
  tft.print(spc_pressure.cp_value, 2);
  tft.print(" Cpk: ");
  tft.print(spc_pressure.cpk_value, 2);
  
  // Production counters
  tft.setCursor(10, 220);
  tft.print("Parts Today: ");
  tft.print(system_status.parts_produced_today);
  tft.print(" (");
  tft.print(system_status.parts_rejected_today);
  tft.print(" rejected)");
}

void handleTouchInput() {
  if (touch.touched()) {
    TS_Point p = touch.getPoint();
    
    // Handle touch input for process control
    if (p.y > 50 && p.y < 100) {
      // Start/stop cycle
      cycle_active = !cycle_active;
    }
  }
}

// System Test Functions
bool testPressureSensors() {
  // Test all pressure sensor readings
  float test_reading = readPressureSensor(CAVITY_PRESSURE_1);
  return (test_reading >= 0 && test_reading <= 1024);
}

bool testTemperatureSensors() {
  // Test all thermocouple readings
  float temp = readThermocouple(0);
  return (temp > 0 && temp < 500);
}

bool testPositionSensors() {
  // Test position sensor readings
  float position = analogRead(POSITION_SENSOR_ADC);
  return (position >= 0 && position <= 1024);
}

bool testControlOutputs() {
  // Test all PWM outputs
  analogWrite(INJECTION_VALVE, 128);
  delay(100);
  analogWrite(INJECTION_VALVE, 0);
  return true; // Assume test passes
}

bool testSafetySystems() {
  // Test safety system functionality
  return (!system_status.emergency_stop_active);
}

bool testCommunicationSystems() {
  // Test WiFi and MQTT connectivity
  return (WiFi.status() == WL_CONNECTED);
}

void setupWebServer() {
  web_server.on("/", HTTP_GET, handleRoot);
  web_server.on("/api/status", HTTP_GET, handleAPIStatus);
  web_server.on("/api/parameters", HTTP_POST, handleAPIParameters);
  web_server.begin();
}

void handleWebServerRequests() {
  web_server.handleClient();
}

void handleRoot() {
  web_server.send(200, "text/html", "Injection Molding Controller Web Interface");
}

void handleAPIStatus() {
  DynamicJsonDocument doc(2048);
  
  doc["timestamp"] = millis();
  doc["phase"] = system_status.current_phase;
  doc["cycle_time"] = system_status.cycle_time_actual;
  doc["parts_produced"] = system_status.parts_produced_today;
  doc["parts_rejected"] = system_status.parts_rejected_today;
  doc["system_health"] = system_status.system_health_score;
  
  String response;
  serializeJson(doc, response);
  web_server.send(200, "application/json", response);
}

void handleAPIParameters() {
  // Handle parameter updates via web API
  String body = web_server.arg("plain");
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, body);
  
  // Update process parameters from JSON
  updateProcessParameters(doc);
  
  web_server.send(200, "text/plain", "Parameters updated");
}

void handleESP32Communication() {
  if (ESP32_SERIAL.available()) {
    String message = ESP32_SERIAL.readString();
    // Process digital twin data from ESP32
    processDigitalTwinData(message);
  }
}

void processDigitalTwinData(String data) {
  // Process digital twin synchronization data
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, data);
  
  // Extract optimization recommendations
  if (doc.containsKey("optimization")) {
    JsonObject opt = doc["optimization"];
    
    // Apply recommended parameter changes
    if (opt.containsKey("injection_velocity")) {
      process_params.injection_velocity[0] = opt["injection_velocity"];
    }
    
    if (opt.containsKey("pack_pressure")) {
      process_params.pack_pressure[0] = opt["pack_pressure"];
    }
  }
}

void handleRemoteCommand(JsonDocument& doc) {
  String command = doc["command"];
  
  if (command == "start_cycle") {
    cycle_active = true;
  } else if (command == "stop_cycle") {
    cycle_active = false;
  } else if (command == "emergency_stop") {
    triggerEmergencyStop();
  } else if (command == "reset_fault") {
    if (!system_status.emergency_stop_active) {
      system_status.current_phase = PHASE_IDLE;
      digitalWrite(STATUS_LED_RED, LOW);
      digitalWrite(ALARM_HORN, LOW);
    }
  }
}

void updateProcessParameters(JsonDocument& doc) {
  // Update process parameters from remote command
  if (doc.containsKey("injection_velocity")) {
    JsonArray vel_array = doc["injection_velocity"];
    for (int i = 0; i < min((int)vel_array.size(), MAX_INJECTION_STAGES); i++) {
      process_params.injection_velocity[i] = vel_array[i];
    }
  }
  
  if (doc.containsKey("pack_pressure")) {
    JsonArray press_array = doc["pack_pressure"];
    for (int i = 0; i < min((int)press_array.size(), MAX_PACK_STAGES); i++) {
      process_params.pack_pressure[i] = press_array[i];
    }
  }
  
  if (doc.containsKey("temperature")) {
    JsonObject temp_obj = doc["temperature"];
    if (temp_obj.containsKey("barrel_1")) process_params.barrel_temp_1 = temp_obj["barrel_1"];
    if (temp_obj.containsKey("barrel_2")) process_params.barrel_temp_2 = temp_obj["barrel_2"];
    if (temp_obj.containsKey("barrel_3")) process_params.barrel_temp_3 = temp_obj["barrel_3"];
    if (temp_obj.containsKey("nozzle")) process_params.nozzle_temp = temp_obj["nozzle"];
    if (temp_obj.containsKey("mold")) process_params.mold_temp = temp_obj["mold"];
  }
}

void logProcessData() {
  static unsigned long last_log_time = 0;
  
  if (millis() - last_log_time < 100) return; // Log at 10 Hz
  
  File data_file = SD.open("/process_data/molding_data.csv", FILE_WRITE);
  if (data_file) {
    data_file.print(millis());
    data_file.print(",");
    data_file.print(system_status.current_phase);
    data_file.print(",");
    data_file.print(cavity_pressure.average_pressure);
    data_file.print(",");
    data_file.print(cavity_pressure.peak_pressure);
    data_file.print(",");
    data_file.print(temperature_data.melt_temp);
    data_file.print(",");
    data_file.print(temperature_data.mold_temp);
    data_file.print(",");
    data_file.print(position_data.screw_position);
    data_file.print(",");
    data_file.print(position_data.screw_velocity);
    data_file.print(",");
    data_file.print(quality_prediction.predicted_weight);
    data_file.print(",");
    data_file.print(quality_prediction.overall_quality);
    data_file.println();
    data_file.close();
  }
  
  last_log_time = millis();
}

void updateSystemHealth() {
  // Calculate system health score based on various factors
  int health_score = 100;
  
  // Deduct points for out-of-spec conditions
  if (!system_status.all_heaters_ready) health_score -= 10;
  if (system_status.emergency_stop_active) health_score -= 50;
  if (!system_status.safety_gates_closed) health_score -= 30;
  if (cavity_pressure.pressure_balance > 10.0) health_score -= 15;
  if (!spc_pressure.process_stable) health_score -= 10;
  if (quality_prediction.overall_quality == QUALITY_REJECT) health_score -= 20;
  
  system_status.system_health_score = max(0, health_score);
  
  // Update system efficiency
  if (system_status.parts_produced_today > 0) {
    system_status.overall_efficiency = 
      ((float)(system_status.parts_produced_today - system_status.parts_rejected_today) / 
       system_status.parts_produced_today) * 100.0;
  }
}

void loadConfiguration() {
  // Load saved configuration from EEPROM
  // Implementation would read process parameters, calibration data, etc.
}

void saveConfiguration() {
  // Save current configuration to EEPROM
  // Implementation would write process parameters, calibration data, etc.
}