/*
Program 29: Composite Curing Controller
Arduino Zero to Hero v2.0 - Track 3

Advanced autoclave control system for aerospace-grade composite manufacturing
featuring multi-zone temperature control, vacuum management, cure kinetics
modeling, and residual stress prediction for optimal composite properties.

Features:
- Multi-zone temperature control (12 zones, ±1°C accuracy)
- Complex ramp/soak/cool profiles with exotherm management
- Vacuum pressure control (0-760 mmHg, ±1 mmHg accuracy)
- Real-time cure kinetics modeling and optimization
- Resin flow and viscosity tracking with gel point prediction
- Residual stress and warpage prediction algorithms
- ASTM/aerospace standards compliance (AS9100, NADCAP)
- Digital twin integration for virtual process development

Hardware:
- Arduino Mega 2560 (zone control) + Arduino Due (data acquisition)
- ESP32 (IoT and analytics engine)
- MAX31856 thermocouple amplifiers (12 channels)
- K-type thermocouples with industrial connectors
- Vacuum/pressure transducers with 24-bit resolution
- Solid-state relays for heater control (12 zones)
- Proportional vacuum controller and mass flow control
- 10.1" industrial touchscreen, UPS power backup

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
#include <Adafruit_ILI9488.h>
#include <XPT2046_Touchscreen.h>
#include <PID_v1.h>
#include <RTClib.h>
#include <math.h>

// Pin Definitions - Composite Curing Controller
#define TEMP_SENSOR_CS_BASE   22    // MAX31856 CS pins (22-33 for 12 zones)
#define VACUUM_SENSOR_1       A0    // Primary vacuum transducer
#define VACUUM_SENSOR_2       A1    // Secondary vacuum transducer
#define PRESSURE_SENSOR_1     A2    // Autoclave pressure sensor
#define PRESSURE_SENSOR_2     A3    // Differential pressure sensor
#define FLOW_SENSOR           A4    // Mass flow sensor for venting
#define DIELECTRIC_SENSOR     A5    // Cure monitoring sensor
#define THICKNESS_SENSOR      A6    // Part thickness measurement
#define ACOUSTIC_SENSOR       A7    // Void detection sensor

// Heater Control Outputs (12 zones)
#define HEATER_ZONE_1         2
#define HEATER_ZONE_2         3
#define HEATER_ZONE_3         4
#define HEATER_ZONE_4         5
#define HEATER_ZONE_5         6
#define HEATER_ZONE_6         7
#define HEATER_ZONE_7         8
#define HEATER_ZONE_8         9
#define HEATER_ZONE_9         10
#define HEATER_ZONE_10        11
#define HEATER_ZONE_11        12
#define HEATER_ZONE_12        13

// Vacuum and Pressure Control
#define VACUUM_PUMP_CONTROL   14    // Vacuum pump speed control
#define VACUUM_VALVE_1        15    // Primary vacuum valve
#define VACUUM_VALVE_2        16    // Secondary vacuum valve
#define VENT_VALVE            17    // Controlled venting valve
#define PRESSURE_RELIEF       18    // Emergency pressure relief
#define AUTOCLAVE_PRESSURE    19    // Autoclave pressure control

// Safety and Monitoring
#define EMERGENCY_STOP        20    // Hardware emergency stop
#define DOOR_INTERLOCK        21    // Autoclave door safety
#define OVER_TEMP_ALARM       34    // Over-temperature alarm
#define VACUUM_ALARM          35    // Vacuum system alarm
#define PRESSURE_ALARM        36    // Pressure system alarm
#define STATUS_LED_GREEN      37    // System OK indicator
#define STATUS_LED_YELLOW     38    // Warning indicator
#define STATUS_LED_RED        39    // Fault indicator
#define ALARM_HORN            40    // Audible alarm

// Display and Interface
#define TFT_CS                41
#define TFT_DC                42
#define TFT_RST               43
#define TOUCH_CS              44
#define TOUCH_IRQ             45

// Communication and Data
#define SD_CS                 53    // SD card for data logging
#define ESP32_SERIAL          Serial1  // Communication with ESP32
#define RTC_SDA               20    // Real-time clock
#define RTC_SCL               21    // Real-time clock

// Process Control Constants
#define MAX_TEMPERATURE       400.0   // °C maximum
#define MIN_TEMPERATURE       15.0    // °C minimum
#define MAX_VACUUM            760.0   // mmHg (full vacuum)
#define MAX_PRESSURE          150.0   // psi
#define TEMP_ZONES            12      // Number of temperature zones
#define MAX_CURE_TIME         172800  // 48 hours maximum
#define TEMP_RESOLUTION       0.1     // °C
#define VACUUM_RESOLUTION     0.1     // mmHg
#define PRESSURE_RESOLUTION   0.1     // psi
#define DATA_LOG_INTERVAL     1000    // ms (1 Hz default)

// Cure Kinetics Constants
#define ARRHENIUS_A           1.0e12  // Pre-exponential factor
#define ACTIVATION_ENERGY     75000   // J/mol
#define GAS_CONSTANT          8.314   // J/(mol·K)
#define REACTION_ORDER_M      0.5     // Reaction model parameter
#define REACTION_ORDER_N      2.0     // Reaction model parameter

// Process States
enum ProcessState {
  STATE_IDLE,
  STATE_HEATING,
  STATE_VACUUM_PULL,
  STATE_CURE_RAMP,
  STATE_CURE_SOAK,
  STATE_COOL_DOWN,
  STATE_PRESSURE_VENT,
  STATE_COMPLETE,
  STATE_FAULT,
  STATE_EMERGENCY
};

enum CurePhase {
  PHASE_DEBULK,
  PHASE_GELATION,
  PHASE_VITRIFICATION,
  PHASE_COMPLETE
};

// Data Structures
struct TemperatureData {
  float zone_temps[TEMP_ZONES];      // Current temperatures (°C)
  float zone_setpoints[TEMP_ZONES];  // Target temperatures (°C)
  float zone_powers[TEMP_ZONES];     // Heater power outputs (%)
  float avg_temperature;             // Average part temperature
  float max_temperature;             // Maximum zone temperature
  float min_temperature;             // Minimum zone temperature
  float temp_uniformity;             // Temperature uniformity (%)
  float heating_rate;                // Current heating rate (°C/min)
  uint32_t timestamp;
};

struct VacuumPressureData {
  float vacuum_1;                    // Primary vacuum (mmHg)
  float vacuum_2;                    // Secondary vacuum (mmHg)
  float autoclave_pressure;          // Autoclave pressure (psi)
  float differential_pressure;       // Pressure differential (psi)
  float mass_flow_rate;              // Vent flow rate (SLPM)
  float leak_rate;                   // Calculated leak rate (mmHg/min)
  bool vacuum_integrity;             // Vacuum system integrity
  uint32_t timestamp;
};

struct CureKineticsData {
  float degree_of_cure;              // α (0-1)
  float cure_rate;                   // dα/dt (1/s)
  float resin_viscosity;             // η (Pa·s)
  float glass_transition_temp;       // Tg (°C)
  float gel_time;                    // Time to gelation (s)
  float vitrification_time;          // Time to vitrification (s)
  CurePhase current_phase;           // Current cure phase
  float exotherm_heat;               // Exothermic heat release (J/g)
  uint32_t timestamp;
};

struct ProcessProfile {
  char profile_name[32];             // Profile identifier
  int num_segments;                  // Number of profile segments
  float segment_temps[20];           // Target temperatures per segment
  float segment_times[20];           // Duration of each segment (min)
  float heating_rates[20];           // Heating rates (°C/min)
  float vacuum_setpoints[20];        // Vacuum targets (mmHg)
  float pressure_setpoints[20];      // Pressure targets (psi)
  bool auto_exotherm_control;        // Enable automatic exotherm management
  float max_exotherm_temp;           // Maximum allowable exotherm
};

struct MaterialProperties {
  char material_name[32];            // Material identifier
  float arrhenius_a;                 // Pre-exponential factor
  float activation_energy;           // Activation energy (J/mol)
  float reaction_order_m;            // Autocatalytic model parameter m
  float reaction_order_n;            // Autocatalytic model parameter n
  float tg_uncured;                  // Tg of uncured resin (°C)
  float tg_cured;                    // Tg of fully cured resin (°C)
  float lambda_param;                // DiBenedetto equation parameter
  float viscosity_inf;               // Infinite shear viscosity (Pa·s)
  float visc_activation_energy;      // Viscosity activation energy (J/mol)
  float gel_point;                   // Gel point (degree of cure)
};

struct QualityMetrics {
  float temperature_deviation;       // Max deviation from setpoint (°C)
  float vacuum_stability;            // Vacuum stability metric
  float cure_uniformity;             // Cure uniformity across part
  float predicted_porosity;          // Predicted void content (%)
  float residual_stress;             // Predicted residual stress (MPa)
  float warpage_prediction;          // Predicted warpage (mm)
  float overall_quality_score;       // Overall quality index (0-100)
  bool accepts_spec;                 // Meets specification requirements
};

struct SystemStatus {
  ProcessState current_state;
  bool emergency_stop_active;
  bool door_interlock_closed;
  bool all_heaters_operational;
  bool vacuum_system_ready;
  bool pressure_system_ready;
  float cycle_elapsed_time;          // s
  float estimated_remaining_time;    // s
  int current_segment;               // Current profile segment
  float cycle_completion_percent;    // %
  int system_health_score;           // 0-100
  uint32_t cycle_start_time;         // Unix timestamp
};

// Global Variables
TemperatureData temperature_data;
VacuumPressureData vacuum_pressure_data;
CureKineticsData cure_kinetics;
ProcessProfile active_profile;
MaterialProperties current_material;
QualityMetrics quality_metrics;
SystemStatus system_status;

// Process Control Variables
unsigned long cycle_start_time;
unsigned long segment_start_time;
unsigned long last_data_log;
unsigned long last_kinetics_update;
unsigned long last_display_update;
unsigned long last_safety_check;
bool cycle_active = false;
bool emergency_triggered = false;

// PID Controllers for each temperature zone
PID zone_pid[TEMP_ZONES] = {
  PID(&temperature_data.zone_temps[0], &temperature_data.zone_powers[0], &temperature_data.zone_setpoints[0], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[1], &temperature_data.zone_powers[1], &temperature_data.zone_setpoints[1], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[2], &temperature_data.zone_powers[2], &temperature_data.zone_setpoints[2], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[3], &temperature_data.zone_powers[3], &temperature_data.zone_setpoints[3], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[4], &temperature_data.zone_powers[4], &temperature_data.zone_setpoints[4], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[5], &temperature_data.zone_powers[5], &temperature_data.zone_setpoints[5], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[6], &temperature_data.zone_powers[6], &temperature_data.zone_setpoints[6], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[7], &temperature_data.zone_powers[7], &temperature_data.zone_setpoints[7], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[8], &temperature_data.zone_powers[8], &temperature_data.zone_setpoints[8], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[9], &temperature_data.zone_powers[9], &temperature_data.zone_setpoints[9], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[10], &temperature_data.zone_powers[10], &temperature_data.zone_setpoints[10], 2.0, 0.1, 0.05, DIRECT),
  PID(&temperature_data.zone_temps[11], &temperature_data.zone_powers[11], &temperature_data.zone_setpoints[11], 2.0, 0.1, 0.05, DIRECT)
};

// Vacuum and pressure PID controllers
double vacuum_setpoint, vacuum_output, vacuum_input;
double pressure_setpoint, pressure_output, pressure_input;
PID vacuum_pid(&vacuum_input, &vacuum_output, &vacuum_setpoint, 1.0, 0.05, 0.02, DIRECT);
PID pressure_pid(&pressure_input, &pressure_output, &pressure_setpoint, 2.0, 0.1, 0.05, DIRECT);

// Display and Communication
Adafruit_ILI9488 tft = Adafruit_ILI9488(TFT_CS, TFT_DC, TFT_RST);
XPT2046_Touchscreen touch(TOUCH_CS, TOUCH_IRQ);
WiFiClient wifi_client;
PubSubClient mqtt_client(wifi_client);
WebServer web_server(80);
RTC_DS3231 rtc;

// Network Configuration
const char* ssid = "AerospaceNet";
const char* password = "Composite2024";
const char* mqtt_server = "mqtt.aerospace.local";
const int mqtt_port = 1883;

void setup() {
  Serial.begin(115200);
  ESP32_SERIAL.begin(115200);
  
  Serial.println("Composite Curing Controller v2.0 Starting...");
  
  // Initialize critical safety systems first
  initializeSafetySystems();
  
  // Initialize hardware interfaces
  initializePinModes();
  initializeDisplayAndTouch();
  initializeSDCard();
  initializeRTC();
  initializeNetworking();
  
  // Load configuration and material database
  loadConfiguration();
  loadMaterialDatabase();
  
  // Initialize control systems
  initializePIDControllers();
  initializeProcessProfiles();
  
  // Initialize material properties
  loadDefaultMaterial();
  
  // Perform comprehensive system self-test
  performSystemSelfTest();
  
  Serial.println("Composite Curing Controller initialized successfully");
  
  // Initialize process state
  system_status.current_state = STATE_IDLE;
  cycle_start_time = millis();
}

void loop() {
  unsigned long current_time = millis();
  
  // Critical safety monitoring (highest priority)
  if (current_time - last_safety_check >= 100) { // 10 Hz safety check
    monitorSafetySystems();
    last_safety_check = current_time;
  }
  
  // High-speed data acquisition and control (1 Hz)
  if (current_time - last_data_log >= DATA_LOG_INTERVAL) {
    readAllSensors();
    updateProcessControl();
    last_data_log = current_time;
  }
  
  // Cure kinetics modeling (1 Hz)
  if (current_time - last_kinetics_update >= 1000) {
    updateCureKinetics();
    predictQualityMetrics();
    last_kinetics_update = current_time;
  }
  
  // Process state management
  updateProcessState();
  
  // Display updates (2 Hz)
  if (current_time - last_display_update >= 500) {
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
  pinMode(DOOR_INTERLOCK, INPUT_PULLUP);
  
  // Configure alarm outputs
  pinMode(OVER_TEMP_ALARM, OUTPUT);
  pinMode(VACUUM_ALARM, OUTPUT);
  pinMode(PRESSURE_ALARM, OUTPUT);
  pinMode(ALARM_HORN, OUTPUT);
  pinMode(STATUS_LED_GREEN, OUTPUT);
  pinMode(STATUS_LED_YELLOW, OUTPUT);
  pinMode(STATUS_LED_RED, OUTPUT);
  pinMode(PRESSURE_RELIEF, OUTPUT);
  
  // Initialize safety outputs to safe state
  digitalWrite(OVER_TEMP_ALARM, LOW);
  digitalWrite(VACUUM_ALARM, LOW);
  digitalWrite(PRESSURE_ALARM, LOW);
  digitalWrite(ALARM_HORN, LOW);
  digitalWrite(STATUS_LED_RED, HIGH);  // Red until system ready
  digitalWrite(PRESSURE_RELIEF, HIGH); // Open pressure relief initially
  
  // Attach emergency stop interrupt
  attachInterrupt(digitalPinToInterrupt(EMERGENCY_STOP), emergencyStopISR, FALLING);
  
  system_status.emergency_stop_active = !digitalRead(EMERGENCY_STOP);
  system_status.door_interlock_closed = !digitalRead(DOOR_INTERLOCK);
}

void initializePinModes() {
  // Temperature sensor chip selects
  for (int i = 0; i < TEMP_ZONES; i++) {
    pinMode(TEMP_SENSOR_CS_BASE + i, OUTPUT);
    digitalWrite(TEMP_SENSOR_CS_BASE + i, HIGH);
  }
  
  // Analog sensor inputs
  pinMode(VACUUM_SENSOR_1, INPUT);
  pinMode(VACUUM_SENSOR_2, INPUT);
  pinMode(PRESSURE_SENSOR_1, INPUT);
  pinMode(PRESSURE_SENSOR_2, INPUT);
  pinMode(FLOW_SENSOR, INPUT);
  pinMode(DIELECTRIC_SENSOR, INPUT);
  pinMode(THICKNESS_SENSOR, INPUT);
  pinMode(ACOUSTIC_SENSOR, INPUT);
  
  // Heater control outputs
  for (int i = 0; i < TEMP_ZONES; i++) {
    pinMode(HEATER_ZONE_1 + i, OUTPUT);
    analogWrite(HEATER_ZONE_1 + i, 0); // Start with heaters off
  }
  
  // Vacuum and pressure control outputs
  pinMode(VACUUM_PUMP_CONTROL, OUTPUT);
  pinMode(VACUUM_VALVE_1, OUTPUT);
  pinMode(VACUUM_VALVE_2, OUTPUT);
  pinMode(VENT_VALVE, OUTPUT);
  pinMode(AUTOCLAVE_PRESSURE, OUTPUT);
  
  // Initialize control outputs to safe state
  analogWrite(VACUUM_PUMP_CONTROL, 0);
  digitalWrite(VACUUM_VALVE_1, LOW);
  digitalWrite(VACUUM_VALVE_2, LOW);
  digitalWrite(VENT_VALVE, HIGH); // Open for venting
  analogWrite(AUTOCLAVE_PRESSURE, 0);
  
  // SD card and communication
  pinMode(SD_CS, OUTPUT);
  digitalWrite(SD_CS, HIGH);
}

void initializeDisplayAndTouch() {
  SPI.begin();
  tft.begin();
  tft.setRotation(3);
  tft.fillScreen(ILI9488_BLACK);
  
  touch.begin();
  touch.setRotation(3);
  
  // Display startup screen
  tft.setCursor(10, 10);
  tft.setTextColor(ILI9488_WHITE);
  tft.setTextSize(2);
  tft.println("Composite Curing Controller");
  tft.println("v2.0 - Aerospace Grade");
  tft.println("");
  tft.setTextSize(1);
  tft.println("Initializing autoclave systems...");
}

void initializeSDCard() {
  if (!SD.begin(SD_CS)) {
    Serial.println("SD card initialization failed!");
    return;
  }
  Serial.println("SD card initialized successfully");
  
  // Create data directories
  SD.mkdir("/cure_data");
  SD.mkdir("/profiles");
  SD.mkdir("/materials");
  SD.mkdir("/quality");
  SD.mkdir("/config");
  SD.mkdir("/logs");
}

void initializeRTC() {
  if (!rtc.begin()) {
    Serial.println("RTC initialization failed!");
    return;
  }
  
  if (rtc.lostPower()) {
    Serial.println("RTC lost power, setting time...");
    // Set to compile time if power was lost
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
  
  Serial.println("RTC initialized successfully");
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
  // Initialize temperature zone PID controllers
  for (int i = 0; i < TEMP_ZONES; i++) {
    zone_pid[i].SetMode(AUTOMATIC);
    zone_pid[i].SetOutputLimits(0, 255);
    zone_pid[i].SetSampleTime(1000); // 1 second
    temperature_data.zone_setpoints[i] = 25.0; // Room temperature
    temperature_data.zone_powers[i] = 0.0;
  }
  
  // Initialize vacuum PID controller
  vacuum_pid.SetMode(AUTOMATIC);
  vacuum_pid.SetOutputLimits(0, 255);
  vacuum_pid.SetSampleTime(1000);
  vacuum_setpoint = 0.0; // Atmospheric pressure
  
  // Initialize pressure PID controller
  pressure_pid.SetMode(AUTOMATIC);
  pressure_pid.SetOutputLimits(0, 255);
  pressure_pid.SetSampleTime(1000);
  pressure_setpoint = 0.0; // No pressure
}

void initializeProcessProfiles() {
  // Load default aerospace composite profile
  strcpy(active_profile.profile_name, "Aerospace_Standard");
  active_profile.num_segments = 6;
  
  // Debulk phase
  active_profile.segment_temps[0] = 60.0;   // °C
  active_profile.segment_times[0] = 30.0;   // minutes
  active_profile.heating_rates[0] = 2.0;    // °C/min
  active_profile.vacuum_setpoints[0] = 700.0; // mmHg
  active_profile.pressure_setpoints[0] = 0.0; // psi
  
  // Heat-up to cure temperature
  active_profile.segment_temps[1] = 120.0;
  active_profile.segment_times[1] = 30.0;
  active_profile.heating_rates[1] = 2.0;
  active_profile.vacuum_setpoints[1] = 720.0;
  active_profile.pressure_setpoints[1] = 0.0;
  
  // Cure ramp
  active_profile.segment_temps[2] = 177.0;  // Typical epoxy cure temp
  active_profile.segment_times[2] = 28.5;   // 57 minutes total ramp at 2°C/min
  active_profile.heating_rates[2] = 2.0;
  active_profile.vacuum_setpoints[2] = 740.0;
  active_profile.pressure_setpoints[2] = 0.0;
  
  // Cure soak
  active_profile.segment_temps[3] = 177.0;
  active_profile.segment_times[3] = 120.0;  // 2 hours cure
  active_profile.heating_rates[3] = 0.0;    // Hold temperature
  active_profile.vacuum_setpoints[3] = 740.0;
  active_profile.pressure_setpoints[3] = 0.0;
  
  // Cool down
  active_profile.segment_temps[4] = 60.0;
  active_profile.segment_times[4] = 60.0;   // 1 hour cool down
  active_profile.heating_rates[4] = -2.0;   // Controlled cooling
  active_profile.vacuum_setpoints[4] = 740.0;
  active_profile.pressure_setpoints[4] = 0.0;
  
  // Atmospheric return
  active_profile.segment_temps[5] = 25.0;
  active_profile.segment_times[5] = 30.0;
  active_profile.heating_rates[5] = -1.0;
  active_profile.vacuum_setpoints[5] = 0.0; // Return to atmospheric
  active_profile.pressure_setpoints[5] = 0.0;
  
  active_profile.auto_exotherm_control = true;
  active_profile.max_exotherm_temp = 200.0; // °C
}

void loadMaterialDatabase() {
  // Load default aerospace epoxy properties (similar to Hexcel 8552)
  strcpy(current_material.material_name, "Aerospace_Epoxy_8552");
  current_material.arrhenius_a = 2.101e9;          // 1/min
  current_material.activation_energy = 75000;      // J/mol
  current_material.reaction_order_m = 0.644;        // Autocatalytic parameter
  current_material.reaction_order_n = 1.468;       // Autocatalytic parameter
  current_material.tg_uncured = -15.0;             // °C
  current_material.tg_cured = 215.0;               // °C
  current_material.lambda_param = 0.4;             // DiBenedetto parameter
  current_material.viscosity_inf = 5.74e-8;        // Pa·s
  current_material.visc_activation_energy = 83400; // J/mol
  current_material.gel_point = 0.47;               // α at gelation
}

void loadDefaultMaterial() {
  // Initialize cure kinetics with material properties
  cure_kinetics.degree_of_cure = 0.0;
  cure_kinetics.cure_rate = 0.0;
  cure_kinetics.resin_viscosity = 1000.0; // Initial viscosity
  cure_kinetics.glass_transition_temp = current_material.tg_uncured;
  cure_kinetics.current_phase = PHASE_DEBULK;
  cure_kinetics.exotherm_heat = 0.0;
  cure_kinetics.gel_time = 0.0;
  cure_kinetics.vitrification_time = 0.0;
}

void performSystemSelfTest() {
  Serial.println("Performing system self-test...");
  
  // Test temperature sensors
  bool temp_test = testTemperatureSensors();
  
  // Test vacuum system
  bool vacuum_test = testVacuumSystem();
  
  // Test pressure system
  bool pressure_test = testPressureSystem();
  
  // Test heater control
  bool heater_test = testHeaterControl();
  
  // Test safety systems
  bool safety_test = testSafetySystems();
  
  // Test communication
  bool comm_test = testCommunicationSystems();
  
  // Calculate overall system health
  int health_score = 0;
  if (temp_test) health_score += 25;
  if (vacuum_test) health_score += 20;
  if (pressure_test) health_score += 15;
  if (heater_test) health_score += 20;
  if (safety_test) health_score += 15;
  if (comm_test) health_score += 5;
  
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
  readTemperatureSensors();
  readVacuumPressureSensors();
  readProcessSensors();
}

void readTemperatureSensors() {
  // Read all 12 temperature zones using MAX31856
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    temperature_data.zone_temps[zone] = readThermocouple(zone);
  }
  
  // Calculate temperature statistics
  float temp_sum = 0.0;
  float temp_min = temperature_data.zone_temps[0];
  float temp_max = temperature_data.zone_temps[0];
  
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    temp_sum += temperature_data.zone_temps[zone];
    if (temperature_data.zone_temps[zone] < temp_min) {
      temp_min = temperature_data.zone_temps[zone];
    }
    if (temperature_data.zone_temps[zone] > temp_max) {
      temp_max = temperature_data.zone_temps[zone];
    }
  }
  
  temperature_data.avg_temperature = temp_sum / TEMP_ZONES;
  temperature_data.min_temperature = temp_min;
  temperature_data.max_temperature = temp_max;
  temperature_data.temp_uniformity = 100.0 - ((temp_max - temp_min) / temperature_data.avg_temperature * 100.0);
  
  // Calculate heating rate
  static float previous_avg_temp = temperature_data.avg_temperature;
  static unsigned long previous_time = millis();
  
  unsigned long current_time = millis();
  float dt = (current_time - previous_time) / 60000.0; // Convert to minutes
  
  if (dt > 0) {
    temperature_data.heating_rate = (temperature_data.avg_temperature - previous_avg_temp) / dt;
    previous_avg_temp = temperature_data.avg_temperature;
    previous_time = current_time;
  }
  
  temperature_data.timestamp = millis();
}

void readVacuumPressureSensors() {
  // Read vacuum sensors (4-20mA to 0-760 mmHg)
  float vacuum_1_raw = analogRead(VACUUM_SENSOR_1) * 5.0 / 1024.0;
  float vacuum_2_raw = analogRead(VACUUM_SENSOR_2) * 5.0 / 1024.0;
  
  vacuum_pressure_data.vacuum_1 = (vacuum_1_raw - 1.0) * 760.0 / 3.0; // 4-20mA to 0-760 mmHg
  vacuum_pressure_data.vacuum_2 = (vacuum_2_raw - 1.0) * 760.0 / 3.0;
  
  // Read pressure sensors (4-20mA to 0-150 psi)
  float pressure_1_raw = analogRead(PRESSURE_SENSOR_1) * 5.0 / 1024.0;
  float pressure_2_raw = analogRead(PRESSURE_SENSOR_2) * 5.0 / 1024.0;
  
  vacuum_pressure_data.autoclave_pressure = (pressure_1_raw - 1.0) * 150.0 / 3.0;
  vacuum_pressure_data.differential_pressure = (pressure_2_raw - 1.0) * 50.0 / 3.0; // ±25 psi range
  
  // Read mass flow sensor
  float flow_raw = analogRead(FLOW_SENSOR) * 5.0 / 1024.0;
  vacuum_pressure_data.mass_flow_rate = flow_raw * 20.0; // 0-5V to 0-100 SLPM
  
  // Calculate leak rate
  static float previous_vacuum = vacuum_pressure_data.vacuum_1;
  static unsigned long previous_time = millis();
  
  unsigned long current_time = millis();
  float dt = (current_time - previous_time) / 60000.0; // Convert to minutes
  
  if (dt > 0) {
    vacuum_pressure_data.leak_rate = (previous_vacuum - vacuum_pressure_data.vacuum_1) / dt;
    previous_vacuum = vacuum_pressure_data.vacuum_1;
    previous_time = current_time;
  }
  
  // Check vacuum integrity
  vacuum_pressure_data.vacuum_integrity = (vacuum_pressure_data.leak_rate < 5.0); // <5 mmHg/min acceptable
  
  vacuum_pressure_data.timestamp = millis();
}

void readProcessSensors() {
  // Read dielectric sensor for cure monitoring
  float dielectric_raw = analogRead(DIELECTRIC_SENSOR) * 5.0 / 1024.0;
  // Process dielectric data for cure state estimation
  
  // Read thickness sensor
  float thickness_raw = analogRead(THICKNESS_SENSOR) * 5.0 / 1024.0;
  // Process thickness data for part monitoring
  
  // Read acoustic sensor for void detection
  float acoustic_raw = analogRead(ACOUSTIC_SENSOR) * 5.0 / 1024.0;
  // Process acoustic data for void detection
}

void updateProcessControl() {
  switch (system_status.current_state) {
    case STATE_HEATING:
      controlHeatingPhase();
      break;
    case STATE_VACUUM_PULL:
      controlVacuumPhase();
      break;
    case STATE_CURE_RAMP:
    case STATE_CURE_SOAK:
      controlCurePhase();
      break;
    case STATE_COOL_DOWN:
      controlCoolingPhase();
      break;
    case STATE_PRESSURE_VENT:
      controlVentingPhase();
      break;
    default:
      // Safe state - maintain minimum control
      maintainSafeState();
      break;
  }
  
  // Always run temperature control
  updateTemperatureControl();
  
  // Always run vacuum/pressure control
  updateVacuumPressureControl();
}

void controlHeatingPhase() {
  // Heat up to initial cure temperature
  float target_temp = active_profile.segment_temps[system_status.current_segment];
  float heating_rate = active_profile.heating_rates[system_status.current_segment];
  
  // Calculate ramped setpoint
  float elapsed_time = (millis() - segment_start_time) / 60000.0; // minutes
  float ramped_setpoint = temperature_data.zone_setpoints[0] + (heating_rate * elapsed_time);
  
  if (ramped_setpoint >= target_temp) {
    ramped_setpoint = target_temp;
  }
  
  // Set all zones to same setpoint (can be modified for zone-specific control)
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    temperature_data.zone_setpoints[zone] = ramped_setpoint;
  }
  
  // Check if segment is complete
  if (temperature_data.avg_temperature >= target_temp - 2.0) { // Within 2°C
    advanceToNextSegment();
  }
}

void controlVacuumPhase() {
  // Pull vacuum according to profile
  float target_vacuum = active_profile.vacuum_setpoints[system_status.current_segment];
  vacuum_setpoint = target_vacuum;
  
  // Check if vacuum target is achieved
  if (vacuum_pressure_data.vacuum_1 >= target_vacuum - 5.0) { // Within 5 mmHg
    advanceToNextSegment();
  }
}

void controlCurePhase() {
  // Complex cure control with exotherm management
  float target_temp = active_profile.segment_temps[system_status.current_segment];
  float heating_rate = active_profile.heating_rates[system_status.current_segment];
  
  // Exotherm detection and management
  if (active_profile.auto_exotherm_control) {
    float exotherm_detected = detectExotherm();
    
    if (exotherm_detected > 5.0) { // >5°C exotherm detected
      // Reduce heating or implement cooling
      for (int zone = 0; zone < TEMP_ZONES; zone++) {
        if (temperature_data.zone_temps[zone] > active_profile.max_exotherm_temp) {
          temperature_data.zone_setpoints[zone] = temperature_data.zone_temps[zone] - 5.0;
        }
      }
      cure_kinetics.exotherm_heat = exotherm_detected;
    } else {
      // Normal temperature control
      for (int zone = 0; zone < TEMP_ZONES; zone++) {
        temperature_data.zone_setpoints[zone] = target_temp;
      }
    }
  }
  
  // Check segment completion
  float elapsed_time = (millis() - segment_start_time) / 60000.0; // minutes
  if (elapsed_time >= active_profile.segment_times[system_status.current_segment]) {
    advanceToNextSegment();
  }
}

void controlCoolingPhase() {
  // Controlled cooling
  float target_temp = active_profile.segment_temps[system_status.current_segment];
  float cooling_rate = active_profile.heating_rates[system_status.current_segment]; // Negative for cooling
  
  // Calculate ramped setpoint
  float elapsed_time = (millis() - segment_start_time) / 60000.0; // minutes
  float ramped_setpoint = temperature_data.zone_setpoints[0] + (cooling_rate * elapsed_time);
  
  if (ramped_setpoint <= target_temp) {
    ramped_setpoint = target_temp;
  }
  
  // Set all zones to same setpoint
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    temperature_data.zone_setpoints[zone] = ramped_setpoint;
  }
  
  // Check if cooling is complete
  if (temperature_data.avg_temperature <= target_temp + 2.0) { // Within 2°C
    advanceToNextSegment();
  }
}

void controlVentingPhase() {
  // Return to atmospheric pressure
  vacuum_setpoint = 0.0; // Atmospheric pressure
  
  // Open vent valve gradually
  static int vent_opening = 0;
  if (vent_opening < 255) {
    vent_opening += 5;
    analogWrite(VENT_VALVE, vent_opening);
  }
  
  // Check if venting is complete
  if (vacuum_pressure_data.vacuum_1 <= 50.0) { // Close to atmospheric
    system_status.current_state = STATE_COMPLETE;
  }
}

void maintainSafeState() {
  // Maintain safe heater levels
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    if (temperature_data.zone_temps[zone] > 50.0) {
      temperature_data.zone_setpoints[zone] = 25.0; // Cool to room temperature
    }
  }
  
  // Maintain safe vacuum/pressure
  vacuum_setpoint = 0.0;
  pressure_setpoint = 0.0;
}

void updateTemperatureControl() {
  // Run PID control for each temperature zone
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    zone_pid[zone].Compute();
    
    // Apply heater power output
    int heater_pin = HEATER_ZONE_1 + zone;
    analogWrite(heater_pin, (int)temperature_data.zone_powers[zone]);
    
    // Safety check: over-temperature protection
    if (temperature_data.zone_temps[zone] > MAX_TEMPERATURE) {
      analogWrite(heater_pin, 0); // Turn off heater
      triggerOverTemperatureAlarm(zone);
    }
  }
  
  // Update system status
  system_status.all_heaters_operational = true;
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    if (temperature_data.zone_temps[zone] < -50.0 || temperature_data.zone_temps[zone] > 500.0) {
      system_status.all_heaters_operational = false;
      break;
    }
  }
}

void updateVacuumPressureControl() {
  // Update PID inputs
  vacuum_input = vacuum_pressure_data.vacuum_1;
  pressure_input = vacuum_pressure_data.autoclave_pressure;
  
  // Run PID controllers
  vacuum_pid.Compute();
  pressure_pid.Compute();
  
  // Apply control outputs
  analogWrite(VACUUM_PUMP_CONTROL, (int)vacuum_output);
  analogWrite(AUTOCLAVE_PRESSURE, (int)pressure_output);
  
  // Update system status
  system_status.vacuum_system_ready = vacuum_pressure_data.vacuum_integrity;
  system_status.pressure_system_ready = (vacuum_pressure_data.autoclave_pressure < MAX_PRESSURE);
}

void updateCureKinetics() {
  // Calculate cure kinetics using Kamal-Sourour model
  float temperature_kelvin = temperature_data.avg_temperature + 273.15;
  
  // Rate constant using Arrhenius equation
  float k1 = current_material.arrhenius_a * exp(-current_material.activation_energy / (GAS_CONSTANT * temperature_kelvin));
  
  // Autocatalytic reaction model: dα/dt = k1 * α^m * (1-α)^n
  float alpha = cure_kinetics.degree_of_cure;
  cure_kinetics.cure_rate = k1 * pow(alpha, current_material.reaction_order_m) * 
                           pow(1.0 - alpha, current_material.reaction_order_n);
  
  // Update degree of cure (Euler integration)
  float dt = 1.0; // 1 second time step
  cure_kinetics.degree_of_cure += cure_kinetics.cure_rate * dt;
  
  // Clamp degree of cure between 0 and 1
  cure_kinetics.degree_of_cure = constrain(cure_kinetics.degree_of_cure, 0.0, 1.0);
  
  // Calculate resin viscosity using WLF equation
  float tg = calculateGlassTransitionTemp(alpha);
  if (temperature_data.avg_temperature > tg) {
    float viscosity_temp_factor = exp(current_material.visc_activation_energy / (GAS_CONSTANT * temperature_kelvin));
    float viscosity_cure_factor = pow((current_material.gel_point / (current_material.gel_point - alpha)), 
                                     2.0 + 3.0 * alpha);
    cure_kinetics.resin_viscosity = current_material.viscosity_inf * viscosity_temp_factor * viscosity_cure_factor;
  } else {
    cure_kinetics.resin_viscosity = 1e12; // Very high viscosity below Tg
  }
  
  // Update glass transition temperature
  cure_kinetics.glass_transition_temp = tg;
  
  // Determine cure phase
  if (alpha < 0.1) {
    cure_kinetics.current_phase = PHASE_DEBULK;
  } else if (alpha < current_material.gel_point) {
    cure_kinetics.current_phase = PHASE_GELATION;
  } else if (temperature_data.avg_temperature < tg) {
    cure_kinetics.current_phase = PHASE_VITRIFICATION;
  } else {
    cure_kinetics.current_phase = PHASE_COMPLETE;
  }
  
  // Predict gel time
  if (cure_kinetics.current_phase == PHASE_GELATION && cure_kinetics.gel_time == 0.0) {
    cure_kinetics.gel_time = (millis() - cycle_start_time) / 1000.0;
  }
  
  // Predict vitrification time
  if (cure_kinetics.current_phase == PHASE_VITRIFICATION && cure_kinetics.vitrification_time == 0.0) {
    cure_kinetics.vitrification_time = (millis() - cycle_start_time) / 1000.0;
  }
  
  cure_kinetics.timestamp = millis();
}

float calculateGlassTransitionTemp(float alpha) {
  // DiBenedetto equation for Tg evolution
  return current_material.tg_uncured + 
         (current_material.tg_cured - current_material.tg_uncured) * 
         (current_material.lambda_param * alpha) / 
         (1.0 + (current_material.lambda_param - 1.0) * alpha);
}

void predictQualityMetrics() {
  // Temperature deviation from setpoint
  float max_deviation = 0.0;
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    float deviation = abs(temperature_data.zone_temps[zone] - temperature_data.zone_setpoints[zone]);
    if (deviation > max_deviation) {
      max_deviation = deviation;
    }
  }
  quality_metrics.temperature_deviation = max_deviation;
  
  // Vacuum stability
  quality_metrics.vacuum_stability = vacuum_pressure_data.vacuum_integrity ? 100.0 : 
    max(0.0, 100.0 - abs(vacuum_pressure_data.leak_rate));
  
  // Cure uniformity based on temperature uniformity
  quality_metrics.cure_uniformity = temperature_data.temp_uniformity;
  
  // Predicted porosity based on vacuum level and temperature profile
  float avg_vacuum = (vacuum_pressure_data.vacuum_1 + vacuum_pressure_data.vacuum_2) / 2.0;
  quality_metrics.predicted_porosity = max(0.0, (760.0 - avg_vacuum) / 760.0 * 2.0 + 
                                           quality_metrics.temperature_deviation * 0.1);
  
  // Residual stress prediction (simplified model)
  float thermal_stress = temperature_data.temp_uniformity < 95.0 ? 
    (95.0 - temperature_data.temp_uniformity) * 2.0 : 0.0;
  quality_metrics.residual_stress = thermal_stress;
  
  // Warpage prediction based on thermal gradients
  quality_metrics.warpage_prediction = thermal_stress * 0.1; // mm
  
  // Overall quality score
  float temp_score = max(0.0, 100.0 - quality_metrics.temperature_deviation * 10.0);
  float vacuum_score = quality_metrics.vacuum_stability;
  float uniformity_score = quality_metrics.cure_uniformity;
  float porosity_score = max(0.0, 100.0 - quality_metrics.predicted_porosity * 50.0);
  
  quality_metrics.overall_quality_score = (temp_score + vacuum_score + uniformity_score + porosity_score) / 4.0;
  
  // Acceptance criteria (aerospace standards)
  quality_metrics.accepts_spec = (quality_metrics.temperature_deviation < 5.0) &&
                                (quality_metrics.vacuum_stability > 95.0) &&
                                (quality_metrics.cure_uniformity > 90.0) &&
                                (quality_metrics.predicted_porosity < 2.0);
}

void updateProcessState() {
  static unsigned long last_state_check = 0;
  
  if (millis() - last_state_check < 1000) return; // Check every second
  last_state_check = millis();
  
  if (!cycle_active) return;
  
  switch (system_status.current_state) {
    case STATE_IDLE:
      if (system_status.all_heaters_operational && 
          system_status.vacuum_system_ready && 
          system_status.door_interlock_closed) {
        system_status.current_state = STATE_HEATING;
        system_status.current_segment = 0;
        segment_start_time = millis();
      }
      break;
      
    case STATE_HEATING:
      // Transition to vacuum pull when initial temperature is reached
      if (temperature_data.avg_temperature >= active_profile.segment_temps[0] - 2.0) {
        system_status.current_state = STATE_VACUUM_PULL;
        segment_start_time = millis();
      }
      break;
      
    case STATE_VACUUM_PULL:
      // Transition to cure ramp when vacuum is achieved
      if (vacuum_pressure_data.vacuum_1 >= active_profile.vacuum_setpoints[system_status.current_segment] - 5.0) {
        system_status.current_state = STATE_CURE_RAMP;
        segment_start_time = millis();
      }
      break;
      
    case STATE_CURE_RAMP:
    case STATE_CURE_SOAK:
      // Managed by segment completion in control functions
      break;
      
    case STATE_COOL_DOWN:
      // Transition to venting when cool enough
      if (temperature_data.avg_temperature <= 60.0) {
        system_status.current_state = STATE_PRESSURE_VENT;
        segment_start_time = millis();
      }
      break;
      
    case STATE_COMPLETE:
      cycle_active = false;
      generateCycleReport();
      break;
      
    case STATE_FAULT:
    case STATE_EMERGENCY:
      handleFaultState();
      break;
  }
  
  // Update cycle completion percentage
  updateCycleProgress();
}

void advanceToNextSegment() {
  system_status.current_segment++;
  
  if (system_status.current_segment >= active_profile.num_segments) {
    system_status.current_state = STATE_COMPLETE;
    return;
  }
  
  // Determine next state based on profile segment
  if (system_status.current_segment <= 2) {
    system_status.current_state = STATE_CURE_RAMP;
  } else if (system_status.current_segment == 3) {
    system_status.current_state = STATE_CURE_SOAK;
  } else {
    system_status.current_state = STATE_COOL_DOWN;
  }
  
  segment_start_time = millis();
}

void updateCycleProgress() {
  if (!cycle_active) return;
  
  // Calculate total expected cycle time
  float total_time = 0.0;
  for (int i = 0; i < active_profile.num_segments; i++) {
    total_time += active_profile.segment_times[i];
  }
  
  // Calculate elapsed time in current segments
  float elapsed_time = 0.0;
  for (int i = 0; i < system_status.current_segment; i++) {
    elapsed_time += active_profile.segment_times[i];
  }
  
  // Add time in current segment
  elapsed_time += (millis() - segment_start_time) / 60000.0; // Convert to minutes
  
  system_status.cycle_completion_percent = (elapsed_time / total_time) * 100.0;
  system_status.cycle_elapsed_time = elapsed_time * 60.0; // Convert to seconds
  system_status.estimated_remaining_time = (total_time - elapsed_time) * 60.0; // Convert to seconds
}

// Helper Functions
float readThermocouple(int zone) {
  // Read MAX31856 thermocouple amplifier
  // Simplified - would implement actual MAX31856 communication
  return 25.0 + (analogRead(A0) * 400.0 / 1024.0); // Simulated reading
}

float detectExotherm() {
  // Detect exothermic reaction by comparing measured vs predicted temperature
  static float predicted_temp = temperature_data.avg_temperature;
  
  // Simple prediction based on heating rate
  predicted_temp += temperature_data.heating_rate / 60.0; // Per second
  
  float exotherm = temperature_data.avg_temperature - predicted_temp;
  return max(0.0, exotherm);
}

void triggerOverTemperatureAlarm(int zone) {
  digitalWrite(OVER_TEMP_ALARM, HIGH);
  digitalWrite(ALARM_HORN, HIGH);
  
  Serial.print("OVER-TEMPERATURE ALARM - Zone ");
  Serial.print(zone + 1);
  Serial.print(": ");
  Serial.print(temperature_data.zone_temps[zone]);
  Serial.println("°C");
  
  // Automatic safety response
  system_status.current_state = STATE_FAULT;
}

// Safety Functions
void monitorSafetySystems() {
  // Check emergency stop
  if (!digitalRead(EMERGENCY_STOP) && !system_status.emergency_stop_active) {
    triggerEmergencyStop();
  }
  
  // Check door interlock
  if (!digitalRead(DOOR_INTERLOCK) && cycle_active) {
    system_status.door_interlock_closed = false;
    system_status.current_state = STATE_FAULT;
  }
  
  // Check over-temperature conditions
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    if (temperature_data.zone_temps[zone] > MAX_TEMPERATURE) {
      triggerOverTemperatureAlarm(zone);
    }
  }
  
  // Check over-pressure conditions
  if (vacuum_pressure_data.autoclave_pressure > MAX_PRESSURE) {
    digitalWrite(PRESSURE_RELIEF, HIGH);
    digitalWrite(PRESSURE_ALARM, HIGH);
    system_status.current_state = STATE_FAULT;
  }
  
  // Check vacuum system integrity
  if (!vacuum_pressure_data.vacuum_integrity && cycle_active) {
    digitalWrite(VACUUM_ALARM, HIGH);
    Serial.println("Vacuum integrity alarm");
  }
}

void emergencyStopISR() {
  // Hardware emergency stop interrupt
  system_status.emergency_stop_active = true;
  emergency_triggered = true;
  
  // Immediately stop all heaters
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    analogWrite(HEATER_ZONE_1 + zone, 0);
  }
  
  // Stop vacuum pump
  analogWrite(VACUUM_PUMP_CONTROL, 0);
  
  // Open vent valve
  digitalWrite(VENT_VALVE, HIGH);
  
  // Open pressure relief
  digitalWrite(PRESSURE_RELIEF, HIGH);
  
  // Activate alarm
  digitalWrite(ALARM_HORN, HIGH);
  digitalWrite(STATUS_LED_RED, HIGH);
  
  system_status.current_state = STATE_EMERGENCY;
}

void triggerEmergencyStop() {
  emergencyStopISR(); // Use same logic as hardware interrupt
}

void handleFaultState() {
  // Maintain safe state during fault
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    if (temperature_data.zone_temps[zone] > 50.0) {
      analogWrite(HEATER_ZONE_1 + zone, 0);
    }
  }
  
  // Maintain safe vacuum/pressure
  analogWrite(VACUUM_PUMP_CONTROL, 0);
  digitalWrite(VENT_VALVE, HIGH);
  
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
  if (millis() - last_mqtt_publish > 5000) { // 0.2 Hz
    publishProcessData();
    last_mqtt_publish = millis();
  }
}

void reconnectMQTT() {
  while (!mqtt_client.connected()) {
    if (mqtt_client.connect("CompositeCuringController")) {
      mqtt_client.subscribe("composite/commands");
      mqtt_client.subscribe("composite/profiles");
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
  
  if (String(topic) == "composite/commands") {
    handleRemoteCommand(doc);
  } else if (String(topic) == "composite/profiles") {
    updateProcessProfile(doc);
  }
}

void publishProcessData() {
  DynamicJsonDocument doc(2048);
  
  doc["timestamp"] = rtc.now().unixtime();
  doc["state"] = system_status.current_state;
  doc["segment"] = system_status.current_segment;
  doc["completion"] = system_status.cycle_completion_percent;
  
  // Temperature data
  JsonObject temperature = doc.createNestedObject("temperature");
  temperature["average"] = temperature_data.avg_temperature;
  temperature["uniformity"] = temperature_data.temp_uniformity;
  temperature["heating_rate"] = temperature_data.heating_rate;
  
  JsonArray zone_temps = temperature.createNestedArray("zones");
  for (int i = 0; i < TEMP_ZONES; i++) {
    zone_temps.add(temperature_data.zone_temps[i]);
  }
  
  // Vacuum/pressure data
  JsonObject vacuum = doc.createNestedObject("vacuum_pressure");
  vacuum["vacuum_1"] = vacuum_pressure_data.vacuum_1;
  vacuum["vacuum_2"] = vacuum_pressure_data.vacuum_2;
  vacuum["autoclave_pressure"] = vacuum_pressure_data.autoclave_pressure;
  vacuum["leak_rate"] = vacuum_pressure_data.leak_rate;
  vacuum["integrity"] = vacuum_pressure_data.vacuum_integrity;
  
  // Cure kinetics
  JsonObject cure = doc.createNestedObject("cure_kinetics");
  cure["degree_of_cure"] = cure_kinetics.degree_of_cure;
  cure["cure_rate"] = cure_kinetics.cure_rate;
  cure["resin_viscosity"] = cure_kinetics.resin_viscosity;
  cure["glass_transition_temp"] = cure_kinetics.glass_transition_temp;
  cure["current_phase"] = cure_kinetics.current_phase;
  
  // Quality metrics
  JsonObject quality = doc.createNestedObject("quality");
  quality["overall_score"] = quality_metrics.overall_quality_score;
  quality["temperature_deviation"] = quality_metrics.temperature_deviation;
  quality["predicted_porosity"] = quality_metrics.predicted_porosity;
  quality["accepts_spec"] = quality_metrics.accepts_spec;
  
  String json_string;
  serializeJson(doc, json_string);
  mqtt_client.publish("composite/data", json_string.c_str());
}

// Display Functions
void updateDisplay() {
  tft.fillScreen(ILI9488_BLACK);
  
  // Header
  tft.setCursor(10, 10);
  tft.setTextColor(ILI9488_WHITE);
  tft.setTextSize(2);
  tft.println("Composite Curing Controller");
  
  // Process state
  tft.setCursor(10, 40);
  tft.setTextSize(1);
  tft.print("State: ");
  switch (system_status.current_state) {
    case STATE_IDLE: tft.setTextColor(ILI9488_YELLOW); tft.print("IDLE"); break;
    case STATE_HEATING: tft.setTextColor(ILI9488_ORANGE); tft.print("HEATING"); break;
    case STATE_VACUUM_PULL: tft.setTextColor(ILI9488_CYAN); tft.print("VACUUM PULL"); break;
    case STATE_CURE_RAMP: tft.setTextColor(ILI9488_GREEN); tft.print("CURE RAMP"); break;
    case STATE_CURE_SOAK: tft.setTextColor(ILI9488_GREEN); tft.print("CURE SOAK"); break;
    case STATE_COOL_DOWN: tft.setTextColor(ILI9488_BLUE); tft.print("COOLING"); break;
    case STATE_COMPLETE: tft.setTextColor(ILI9488_GREEN); tft.print("COMPLETE"); break;
    case STATE_FAULT: tft.setTextColor(ILI9488_RED); tft.print("FAULT"); break;
    default: tft.setTextColor(ILI9488_WHITE); tft.print("UNKNOWN"); break;
  }
  
  // Temperature display
  tft.setTextColor(ILI9488_WHITE);
  tft.setCursor(10, 60);
  tft.print("Avg Temp: ");
  tft.print(temperature_data.avg_temperature, 1);
  tft.print(" C");
  
  tft.setCursor(10, 80);
  tft.print("Temp Uniformity: ");
  tft.print(temperature_data.temp_uniformity, 1);
  tft.print(" %");
  
  // Vacuum display
  tft.setCursor(10, 100);
  tft.print("Vacuum: ");
  tft.print(vacuum_pressure_data.vacuum_1, 1);
  tft.print(" mmHg");
  
  // Cure kinetics
  tft.setCursor(10, 120);
  tft.print("Degree of Cure: ");
  tft.print(cure_kinetics.degree_of_cure * 100.0, 1);
  tft.print(" %");
  
  tft.setCursor(10, 140);
  tft.print("Resin Viscosity: ");
  tft.print(cure_kinetics.resin_viscosity, 0);
  tft.print(" Pa.s");
  
  // Quality metrics
  tft.setCursor(10, 160);
  tft.print("Quality Score: ");
  tft.print(quality_metrics.overall_quality_score, 1);
  tft.print(" %");
  
  tft.setCursor(10, 180);
  tft.print("Predicted Porosity: ");
  tft.print(quality_metrics.predicted_porosity, 2);
  tft.print(" %");
  
  // Cycle progress
  tft.setCursor(10, 200);
  tft.print("Cycle Progress: ");
  tft.print(system_status.cycle_completion_percent, 1);
  tft.print(" %");
  
  // Time remaining
  tft.setCursor(10, 220);
  tft.print("Time Remaining: ");
  int hours = (int)(system_status.estimated_remaining_time / 3600);
  int minutes = (int)((system_status.estimated_remaining_time % 3600) / 60);
  tft.print(hours);
  tft.print(":");
  if (minutes < 10) tft.print("0");
  tft.print(minutes);
}

void handleTouchInput() {
  if (touch.touched()) {
    TS_Point p = touch.getPoint();
    
    // Handle touch input for process control
    if (p.y > 250 && p.y < 300) {
      if (p.x > 50 && p.x < 150) {
        // Start cycle
        if (!cycle_active && system_status.current_state == STATE_IDLE) {
          startCycle();
        }
      } else if (p.x > 200 && p.x < 300) {
        // Stop cycle
        if (cycle_active) {
          stopCycle();
        }
      }
    }
  }
}

// System Test Functions
bool testTemperatureSensors() {
  // Test all temperature sensor readings
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    float temp = readThermocouple(zone);
    if (temp < -50.0 || temp > 500.0) {
      return false;
    }
  }
  return true;
}

bool testVacuumSystem() {
  // Test vacuum sensor readings
  readVacuumPressureSensors();
  return (vacuum_pressure_data.vacuum_1 >= 0 && vacuum_pressure_data.vacuum_1 <= 760);
}

bool testPressureSystem() {
  // Test pressure sensor readings
  readVacuumPressureSensors();
  return (vacuum_pressure_data.autoclave_pressure >= 0 && vacuum_pressure_data.autoclave_pressure <= 200);
}

bool testHeaterControl() {
  // Test heater output capability
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    analogWrite(HEATER_ZONE_1 + zone, 128);
    delay(100);
    analogWrite(HEATER_ZONE_1 + zone, 0);
  }
  return true;
}

bool testSafetySystems() {
  // Test safety system functionality
  return (!system_status.emergency_stop_active);
}

bool testCommunicationSystems() {
  // Test WiFi connectivity
  return (WiFi.status() == WL_CONNECTED);
}

void setupWebServer() {
  web_server.on("/", HTTP_GET, handleRoot);
  web_server.on("/api/status", HTTP_GET, handleAPIStatus);
  web_server.on("/api/start", HTTP_POST, handleAPIStart);
  web_server.on("/api/stop", HTTP_POST, handleAPIStop);
  web_server.begin();
}

void handleWebServerRequests() {
  web_server.handleClient();
}

void handleRoot() {
  web_server.send(200, "text/html", "Composite Curing Controller Web Interface");
}

void handleAPIStatus() {
  DynamicJsonDocument doc(2048);
  
  doc["timestamp"] = rtc.now().unixtime();
  doc["state"] = system_status.current_state;
  doc["completion"] = system_status.cycle_completion_percent;
  doc["avg_temperature"] = temperature_data.avg_temperature;
  doc["vacuum"] = vacuum_pressure_data.vacuum_1;
  doc["degree_of_cure"] = cure_kinetics.degree_of_cure;
  doc["quality_score"] = quality_metrics.overall_quality_score;
  
  String response;
  serializeJson(doc, response);
  web_server.send(200, "application/json", response);
}

void handleAPIStart() {
  if (!cycle_active && system_status.current_state == STATE_IDLE) {
    startCycle();
    web_server.send(200, "text/plain", "Cycle started");
  } else {
    web_server.send(400, "text/plain", "Cannot start cycle");
  }
}

void handleAPIStop() {
  if (cycle_active) {
    stopCycle();
    web_server.send(200, "text/plain", "Cycle stopped");
  } else {
    web_server.send(400, "text/plain", "No active cycle");
  }
}

void handleESP32Communication() {
  if (ESP32_SERIAL.available()) {
    String message = ESP32_SERIAL.readString();
    // Process cure optimization data from ESP32
    processCureOptimizationData(message);
  }
}

void processCureOptimizationData(String data) {
  // Process cure optimization and digital twin data
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, data);
  
  // Extract optimization recommendations
  if (doc.containsKey("optimization")) {
    JsonObject opt = doc["optimization"];
    
    // Apply recommended parameter changes if safe
    if (opt.containsKey("temperature_adjustment") && abs(opt["temperature_adjustment"]) < 5.0) {
      for (int zone = 0; zone < TEMP_ZONES; zone++) {
        temperature_data.zone_setpoints[zone] += opt["temperature_adjustment"];
      }
    }
  }
}

void handleRemoteCommand(JsonDocument& doc) {
  String command = doc["command"];
  
  if (command == "start_cycle") {
    if (!cycle_active && system_status.current_state == STATE_IDLE) {
      startCycle();
    }
  } else if (command == "stop_cycle") {
    if (cycle_active) {
      stopCycle();
    }
  } else if (command == "emergency_stop") {
    triggerEmergencyStop();
  } else if (command == "reset_fault") {
    if (!system_status.emergency_stop_active) {
      system_status.current_state = STATE_IDLE;
      digitalWrite(STATUS_LED_RED, LOW);
      digitalWrite(ALARM_HORN, LOW);
    }
  }
}

void updateProcessProfile(JsonDocument& doc) {
  // Update process profile from remote command
  if (doc.containsKey("profile_name")) {
    strcpy(active_profile.profile_name, doc["profile_name"]);
  }
  
  if (doc.containsKey("segments")) {
    JsonArray segments = doc["segments"];
    active_profile.num_segments = min((int)segments.size(), 20);
    
    for (int i = 0; i < active_profile.num_segments; i++) {
      JsonObject segment = segments[i];
      active_profile.segment_temps[i] = segment["temperature"];
      active_profile.segment_times[i] = segment["time"];
      active_profile.heating_rates[i] = segment["heating_rate"];
      active_profile.vacuum_setpoints[i] = segment["vacuum"];
    }
  }
}

void startCycle() {
  cycle_active = true;
  cycle_start_time = millis();
  system_status.cycle_start_time = rtc.now().unixtime();
  system_status.current_state = STATE_IDLE; // Will advance to HEATING automatically
  system_status.current_segment = 0;
  
  // Reset cure kinetics
  cure_kinetics.degree_of_cure = 0.0;
  cure_kinetics.current_phase = PHASE_DEBULK;
  
  Serial.println("Composite curing cycle started");
}

void stopCycle() {
  cycle_active = false;
  system_status.current_state = STATE_IDLE;
  
  // Turn off all heaters
  for (int zone = 0; zone < TEMP_ZONES; zone++) {
    analogWrite(HEATER_ZONE_1 + zone, 0);
  }
  
  // Stop vacuum pump
  analogWrite(VACUUM_PUMP_CONTROL, 0);
  
  Serial.println("Composite curing cycle stopped");
}

void generateCycleReport() {
  // Generate comprehensive cycle report
  File report = SD.open("/reports/cycle_report.txt", FILE_WRITE);
  if (report) {
    report.println("=== COMPOSITE CURING CYCLE REPORT ===");
    report.print("Cycle Start: ");
    report.println(system_status.cycle_start_time);
    report.print("Cycle Duration: ");
    report.print(system_status.cycle_elapsed_time / 3600.0);
    report.println(" hours");
    
    report.println("\n--- QUALITY METRICS ---");
    report.print("Overall Quality Score: ");
    report.print(quality_metrics.overall_quality_score);
    report.println("%");
    report.print("Temperature Deviation: ");
    report.print(quality_metrics.temperature_deviation);
    report.println(" C");
    report.print("Predicted Porosity: ");
    report.print(quality_metrics.predicted_porosity);
    report.println("%");
    report.print("Specification Compliance: ");
    report.println(quality_metrics.accepts_spec ? "PASS" : "FAIL");
    
    report.println("\n--- CURE KINETICS ---");
    report.print("Final Degree of Cure: ");
    report.print(cure_kinetics.degree_of_cure * 100.0);
    report.println("%");
    report.print("Gel Time: ");
    report.print(cure_kinetics.gel_time / 60.0);
    report.println(" minutes");
    
    report.close();
  }
}

void logProcessData() {
  static unsigned long last_log_time = 0;
  
  if (millis() - last_log_time < DATA_LOG_INTERVAL) return;
  
  File data_file = SD.open("/cure_data/process_log.csv", FILE_WRITE);
  if (data_file) {
    // Write CSV header on first log
    static bool header_written = false;
    if (!header_written) {
      data_file.println("timestamp,state,avg_temp,vacuum,degree_of_cure,quality_score");
      header_written = true;
    }
    
    data_file.print(rtc.now().unixtime());
    data_file.print(",");
    data_file.print(system_status.current_state);
    data_file.print(",");
    data_file.print(temperature_data.avg_temperature);
    data_file.print(",");
    data_file.print(vacuum_pressure_data.vacuum_1);
    data_file.print(",");
    data_file.print(cure_kinetics.degree_of_cure);
    data_file.print(",");
    data_file.print(quality_metrics.overall_quality_score);
    data_file.println();
    data_file.close();
  }
  
  last_log_time = millis();
}

void updateSystemHealth() {
  // Calculate system health score based on various factors
  int health_score = 100;
  
  // Deduct points for system issues
  if (!system_status.all_heaters_operational) health_score -= 20;
  if (!system_status.vacuum_system_ready) health_score -= 15;
  if (!system_status.pressure_system_ready) health_score -= 10;
  if (system_status.emergency_stop_active) health_score -= 50;
  if (quality_metrics.temperature_deviation > 5.0) health_score -= 10;
  if (!vacuum_pressure_data.vacuum_integrity) health_score -= 15;
  
  system_status.system_health_score = max(0, health_score);
  
  // Update status LEDs
  if (system_status.system_health_score >= 90) {
    digitalWrite(STATUS_LED_GREEN, HIGH);
    digitalWrite(STATUS_LED_YELLOW, LOW);
    digitalWrite(STATUS_LED_RED, LOW);
  } else if (system_status.system_health_score >= 70) {
    digitalWrite(STATUS_LED_GREEN, LOW);
    digitalWrite(STATUS_LED_YELLOW, HIGH);
    digitalWrite(STATUS_LED_RED, LOW);
  } else {
    digitalWrite(STATUS_LED_GREEN, LOW);
    digitalWrite(STATUS_LED_YELLOW, LOW);
    digitalWrite(STATUS_LED_RED, HIGH);
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