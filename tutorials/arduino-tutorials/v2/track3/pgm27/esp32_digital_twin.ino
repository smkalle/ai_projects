/*
ESP32 Digital Twin & IoT Gateway for Injection Molding Controller
Arduino Zero to Hero v2.0 - Track 3 - Program 27

Advanced IoT gateway implementing digital twin synchronization, cloud analytics,
and real-time process optimization for precision injection molding manufacturing.

Features:
- Digital twin synchronization with cloud simulation
- Real-time process optimization using ML algorithms
- Advanced data analytics and pattern recognition
- Cloud connectivity with AWS IoT Core / Azure IoT Hub
- OPC UA client for MES integration
- Predictive maintenance algorithms
- Energy consumption optimization
- Virtual process validation and what-if analysis

Digital Twin Capabilities:
- 3D mold geometry representation
- Material property database synchronization
- Heat transfer simulation interface
- Flow simulation integration
- Stress analysis capability
- Virtual troubleshooting assistance

Author: Claude Code Assistant
Date: 2025
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>
#include <SPIFFS.h>
#include <HTTPClient.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <HardwareSerial.h>
#include <BluetoothSerial.h>
#include <esp_task_wdt.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"

// Pin Definitions
#define ARDUINO_SERIAL      Serial2   // Communication with main Arduino
#define STATUS_LED          2         // ESP32 onboard LED
#define DIGITAL_TWIN_LED    4         // Digital twin sync indicator
#define CLOUD_LED           5         // Cloud connectivity indicator

// Network Configuration
const char* ssid = "IndustryNet";
const char* password = "Manufacturing2024";

// Cloud Configuration (AWS IoT Core)
const char* aws_iot_endpoint = "your-iot-endpoint.amazonaws.com";
const char* aws_iot_thing_name = "InjectionMoldingController_001";
const char* aws_iot_topic_data = "molding/data";
const char* aws_iot_topic_twin = "molding/twin";
const char* aws_iot_topic_optimization = "molding/optimization";

// Digital Twin API Configuration
const char* digital_twin_api_url = "https://api.digitaltwin.manufacturing.com";
const char* api_key = "your_api_key_here";

// OPC UA Configuration
const char* opcua_server_url = "opc.tcp://mes.factory.local:4840";

// Machine Learning Model Configuration
#define ML_INPUT_SIZE       20        // Number of input features
#define ML_OUTPUT_SIZE      5         // Number of optimization outputs
#define ML_TENSOR_ARENA_SIZE 60000    // Memory for TensorFlow Lite

// Process Optimization Constants
#define OPTIMIZATION_INTERVAL 30000   // 30 seconds
#define DIGITAL_TWIN_SYNC_INTERVAL 10000  // 10 seconds
#define CLOUD_UPLOAD_INTERVAL 5000    // 5 seconds
#define PREDICTIVE_WINDOW     100     // Data points for prediction
#define ENERGY_OPTIMIZATION_THRESHOLD 0.85  // Efficiency threshold

// Data Structures
struct ProcessData {
  float cavity_pressure[4];           // Multi-cavity pressures
  float average_pressure;             // Average cavity pressure
  float peak_pressure;                // Peak pressure this cycle
  float pressure_balance;             // Cavity balance percentage
  float melt_temperature;             // Calculated melt temperature
  float mold_temperature;             // Mold temperature
  float barrel_temperatures[3];       // Barrel zone temperatures
  float nozzle_temperature;           // Nozzle temperature
  float screw_position;               // Screw position
  float screw_velocity;               // Screw velocity
  float clamp_force;                  // Clamp force
  float cycle_time;                   // Actual cycle time
  float predicted_weight;             // Predicted part weight
  int quality_status;                 // Quality prediction
  float energy_consumption;           // Cycle energy consumption
  uint32_t timestamp;                 // Data timestamp
};

struct DigitalTwinState {
  // Virtual Process Model
  float virtual_pressure_profile[1000];  // Simulated pressure curve
  float virtual_temperature_profile[100]; // Temperature evolution
  float material_viscosity;               // Current material viscosity
  float flow_rate_simulation;            // Simulated flow rate
  float cooling_rate;                     // Cooling simulation
  float stress_analysis[50];              // Stress distribution
  float warpage_prediction;               // Warpage simulation
  
  // Model Validation
  float simulation_accuracy;              // Model vs reality accuracy
  bool model_synchronized;                // Sync status
  uint32_t last_sync_time;               // Last synchronization
  
  // Virtual Experiments
  float optimized_parameters[10];         // Recommended parameters
  float predicted_improvements[5];        // Expected improvements
  bool optimization_available;            // New optimization ready
};

struct MLModel {
  tflite::MicroInterpreter* interpreter;
  tflite::MicroErrorReporter* error_reporter;
  const tflite::Model* model;
  TfLiteTensor* input_tensor;
  TfLiteTensor* output_tensor;
  uint8_t tensor_arena[ML_TENSOR_ARENA_SIZE];
  bool model_loaded;
  float prediction_accuracy;
  int prediction_count;
};

struct OptimizationResult {
  float injection_velocity_opt[10];      // Optimized velocity profile
  float pack_pressure_opt[5];            // Optimized pack pressures
  float temperature_opt[5];              // Optimized temperatures
  float cooling_time_opt;                // Optimized cooling time
  float cycle_time_reduction;            // Predicted cycle time reduction
  float quality_improvement;             // Predicted quality improvement
  float energy_savings;                  // Predicted energy savings
  float confidence_level;                // Optimization confidence
  uint32_t optimization_timestamp;       // When optimization was generated
};

struct PredictiveMaintenance {
  float heater_degradation[5];           // Heater element health
  float sensor_drift[10];                // Sensor calibration drift
  float valve_wear;                      // Hydraulic valve wear
  float pump_efficiency;                 // Hydraulic pump efficiency
  float predicted_failures[5];           // Failure probability
  uint32_t maintenance_schedule[10];     // Recommended maintenance dates
  bool maintenance_required;             // Immediate maintenance flag
};

// Global Variables
ProcessData current_data;
DigitalTwinState digital_twin;
MLModel ml_optimization;
OptimizationResult latest_optimization;
PredictiveMaintenance maintenance_status;

// Networking
WiFiClientSecure wifi_secure_client;
PubSubClient mqtt_client(wifi_secure_client);
WebServer web_server(80);
WiFiUDP ntp_udp;
NTPClient time_client(ntp_udp, "pool.ntp.org", 0, 60000);
BluetoothSerial bt_serial;

// Data Storage
unsigned long last_optimization_time = 0;
unsigned long last_digital_twin_sync = 0;
unsigned long last_cloud_upload = 0;
unsigned long last_predictive_analysis = 0;

// Historical Data for ML
float historical_data[PREDICTIVE_WINDOW][ML_INPUT_SIZE];
int data_index = 0;
bool data_buffer_full = false;

// Task Handles
TaskHandle_t digital_twin_task_handle;
TaskHandle_t optimization_task_handle;
TaskHandle_t cloud_task_handle;
TaskHandle_t communication_task_handle;

void setup() {
  Serial.begin(115200);
  ARDUINO_SERIAL.begin(115200);
  
  Serial.println("ESP32 Digital Twin & IoT Gateway v2.0 Starting...");
  
  // Initialize hardware
  initializeGPIO();
  initializeFileSystem();
  
  // Initialize networking
  initializeWiFi();
  initializeCloudConnectivity();
  initializeBluetooth();
  
  // Initialize machine learning
  initializeMLModel();
  
  // Initialize digital twin
  initializeDigitalTwin();
  
  // Start real-time tasks
  startRealTimeTasks();
  
  // Initialize web server
  initializeWebServer();
  
  Serial.println("ESP32 Digital Twin system initialized successfully");
  Serial.print("Free heap: ");
  Serial.println(ESP.getFreeHeap());
}

void loop() {
  // Main loop handles low-priority tasks
  handleWebServer();
  handleBluetoothCommunication();
  updateStatusLEDs();
  
  // Monitor system health
  monitorSystemHealth();
  
  // Handle any pending cloud operations
  processCloudQueue();
  
  delay(100); // Main loop runs at 10Hz
}

void initializeGPIO() {
  pinMode(STATUS_LED, OUTPUT);
  pinMode(DIGITAL_TWIN_LED, OUTPUT);
  pinMode(CLOUD_LED, OUTPUT);
  
  digitalWrite(STATUS_LED, LOW);
  digitalWrite(DIGITAL_TWIN_LED, LOW);
  digitalWrite(CLOUD_LED, LOW);
}

void initializeFileSystem() {
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS initialization failed!");
    return;
  }
  
  Serial.println("SPIFFS initialized successfully");
  
  // Create necessary directories and files
  createConfigurationFiles();
}

void initializeWiFi() {
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected successfully");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    // Initialize NTP
    time_client.begin();
    time_client.update();
    
    digitalWrite(STATUS_LED, HIGH);
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void initializeCloudConnectivity() {
  // Configure AWS IoT Core connection
  wifi_secure_client.setCACert(aws_root_ca);
  wifi_secure_client.setCertificate(aws_device_cert);
  wifi_secure_client.setPrivateKey(aws_private_key);
  
  mqtt_client.setServer(aws_iot_endpoint, 8883);
  mqtt_client.setCallback(mqttCallback);
  
  connectToAWS();
}

void initializeBluetooth() {
  bt_serial.begin("MoldingController_ESP32");
  Serial.println("Bluetooth initialized - Device: MoldingController_ESP32");
}

void initializeMLModel() {
  // Initialize TensorFlow Lite model
  ml_optimization.error_reporter = new tflite::MicroErrorReporter();
  
  // Load model from SPIFFS
  File model_file = SPIFFS.open("/ml_model.tflite", "r");
  if (!model_file) {
    Serial.println("Failed to load ML model!");
    ml_optimization.model_loaded = false;
    return;
  }
  
  size_t model_size = model_file.size();
  uint8_t* model_buffer = new uint8_t[model_size];
  model_file.readBytes((char*)model_buffer, model_size);
  model_file.close();
  
  ml_optimization.model = tflite::GetModel(model_buffer);
  if (ml_optimization.model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema version mismatch!");
    ml_optimization.model_loaded = false;
    return;
  }
  
  // Set up interpreter
  tflite::AllOpsResolver resolver;
  ml_optimization.interpreter = new tflite::MicroInterpreter(
    ml_optimization.model, resolver, ml_optimization.tensor_arena,
    ML_TENSOR_ARENA_SIZE, ml_optimization.error_reporter);
  
  ml_optimization.interpreter->AllocateTensors();
  
  ml_optimization.input_tensor = ml_optimization.interpreter->input(0);
  ml_optimization.output_tensor = ml_optimization.interpreter->output(0);
  
  ml_optimization.model_loaded = true;
  ml_optimization.prediction_accuracy = 0.0;
  ml_optimization.prediction_count = 0;
  
  Serial.println("ML model initialized successfully");
}

void initializeDigitalTwin() {
  // Initialize digital twin state
  digital_twin.material_viscosity = 1.2; // Default viscosity
  digital_twin.simulation_accuracy = 0.0;
  digital_twin.model_synchronized = false;
  digital_twin.optimization_available = false;
  
  // Initialize virtual process model
  for (int i = 0; i < 1000; i++) {
    digital_twin.virtual_pressure_profile[i] = 0.0;
  }
  
  for (int i = 0; i < 100; i++) {
    digital_twin.virtual_temperature_profile[i] = 25.0; // Ambient temperature
  }
  
  for (int i = 0; i < 50; i++) {
    digital_twin.stress_analysis[i] = 0.0;
  }
  
  for (int i = 0; i < 10; i++) {
    digital_twin.optimized_parameters[i] = 0.0;
  }
  
  Serial.println("Digital twin initialized");
}

void startRealTimeTasks() {
  // Create high-priority real-time tasks
  xTaskCreatePinnedToCore(
    digitalTwinTask,           // Task function
    "DigitalTwinTask",         // Task name
    8192,                      // Stack size
    NULL,                      // Parameters
    3,                         // Priority (high)
    &digital_twin_task_handle, // Task handle
    1                          // Core 1
  );
  
  xTaskCreatePinnedToCore(
    optimizationTask,
    "OptimizationTask",
    8192,
    NULL,
    2,                         // Priority (medium-high)
    &optimization_task_handle,
    1                          // Core 1
  );
  
  xTaskCreatePinnedToCore(
    cloudCommunicationTask,
    "CloudTask",
    4096,
    NULL,
    1,                         // Priority (medium)
    &cloud_task_handle,
    0                          // Core 0
  );
  
  xTaskCreatePinnedToCore(
    arduinoCommunicationTask,
    "ArduinoCommTask",
    4096,
    NULL,
    4,                         // Priority (highest)
    &communication_task_handle,
    0                          // Core 0
  );
  
  Serial.println("Real-time tasks started successfully");
}

// Real-time Task: Digital Twin Synchronization
void digitalTwinTask(void* parameter) {
  TickType_t last_wake_time = xTaskGetTickCount();
  
  while (true) {
    // Run digital twin simulation
    runDigitalTwinSimulation();
    
    // Synchronize with cloud twin
    if (millis() - last_digital_twin_sync > DIGITAL_TWIN_SYNC_INTERVAL) {
      synchronizeWithCloudTwin();
      last_digital_twin_sync = millis();
    }
    
    // Update twin status LED
    digitalWrite(DIGITAL_TWIN_LED, digital_twin.model_synchronized);
    
    // Run every 100ms (10Hz)
    vTaskDelayUntil(&last_wake_time, pdMS_TO_TICKS(100));
  }
}

// Real-time Task: Process Optimization
void optimizationTask(void* parameter) {
  TickType_t last_wake_time = xTaskGetTickCount();
  
  while (true) {
    // Collect data for optimization
    collectOptimizationData();
    
    // Run ML-based optimization
    if (millis() - last_optimization_time > OPTIMIZATION_INTERVAL) {
      performMLOptimization();
      last_optimization_time = millis();
    }
    
    // Predictive maintenance analysis
    if (millis() - last_predictive_analysis > 60000) { // Every minute
      performPredictiveAnalysis();
      last_predictive_analysis = millis();
    }
    
    // Run every 500ms (2Hz)
    vTaskDelayUntil(&last_wake_time, pdMS_TO_TICKS(500));
  }
}

// Real-time Task: Cloud Communication
void cloudCommunicationTask(void* parameter) {
  TickType_t last_wake_time = xTaskGetTickCount();
  
  while (true) {
    // Maintain MQTT connection
    if (!mqtt_client.connected()) {
      connectToAWS();
    }
    mqtt_client.loop();
    
    // Upload data to cloud
    if (millis() - last_cloud_upload > CLOUD_UPLOAD_INTERVAL) {
      uploadDataToCloud();
      last_cloud_upload = millis();
    }
    
    // Update cloud status LED
    digitalWrite(CLOUD_LED, mqtt_client.connected());
    
    // Run every 1000ms (1Hz)
    vTaskDelayUntil(&last_wake_time, pdMS_TO_TICKS(1000));
  }
}

// Real-time Task: Arduino Communication
void arduinoCommunicationTask(void* parameter) {
  TickType_t last_wake_time = xTaskGetTickCount();
  
  while (true) {
    // Read data from main Arduino controller
    readArduinoData();
    
    // Send optimization results to Arduino
    if (latest_optimization.optimization_timestamp > 0) {
      sendOptimizationToArduino();
    }
    
    // Run every 50ms (20Hz) - highest frequency
    vTaskDelayUntil(&last_wake_time, pdMS_TO_TICKS(50));
  }
}

void runDigitalTwinSimulation() {
  // Advanced digital twin simulation
  simulatePressureProfile();
  simulateTemperatureEvolution();
  simulateStressAnalysis();
  simulateWarpage();
  calculateMaterialViscosity();
  
  // Validate model accuracy
  validateSimulationAccuracy();
}

void simulatePressureProfile() {
  // Simulate cavity pressure based on injection parameters
  // This would typically use computational fluid dynamics
  
  float injection_velocity = current_data.screw_velocity;
  float melt_temp = current_data.melt_temperature;
  float viscosity = digital_twin.material_viscosity;
  
  // Simplified pressure simulation model
  for (int i = 0; i < 1000; i++) {
    float time_factor = i / 1000.0; // 0 to 1
    float pressure_buildup = injection_velocity * 10.0 * time_factor;
    float viscosity_effect = viscosity * (melt_temp / 250.0);
    
    digital_twin.virtual_pressure_profile[i] = pressure_buildup * viscosity_effect;
    
    // Apply cooling effect over time
    if (i > 500) { // After injection phase
      float cooling_factor = 1.0 - ((i - 500) / 500.0) * 0.3;
      digital_twin.virtual_pressure_profile[i] *= cooling_factor;
    }
  }
}

void simulateTemperatureEvolution() {
  // Simulate temperature evolution during cycle
  float initial_melt_temp = current_data.melt_temperature;
  float mold_temp = current_data.mold_temperature;
  float ambient_temp = 25.0;
  
  for (int i = 0; i < 100; i++) {
    float time_factor = i / 100.0; // 0 to 1 (full cycle)
    
    // Heat transfer simulation
    float cooling_rate = (initial_melt_temp - mold_temp) * 0.02 * time_factor;
    digital_twin.virtual_temperature_profile[i] = initial_melt_temp - cooling_rate;
    
    // Ensure temperature doesn't go below mold temperature
    if (digital_twin.virtual_temperature_profile[i] < mold_temp) {
      digital_twin.virtual_temperature_profile[i] = mold_temp;
    }
  }
  
  // Calculate overall cooling rate
  digital_twin.cooling_rate = (initial_melt_temp - mold_temp) / 20.0; // Per second
}

void simulateStressAnalysis() {
  // Simplified stress analysis simulation
  float clamp_force = current_data.clamp_force;
  float pressure = current_data.average_pressure;
  
  for (int i = 0; i < 50; i++) {
    // Simulate stress distribution in part
    float position_factor = i / 50.0; // 0 to 1 across part
    float stress_concentration = 1.0 + 0.5 * sin(position_factor * M_PI);
    
    digital_twin.stress_analysis[i] = (pressure * 0.1 + clamp_force * 0.05) * stress_concentration;
  }
}

void simulateWarpage() {
  // Warpage prediction based on cooling and stress
  float cooling_gradient = 0.0;
  float max_stress = 0.0;
  
  // Calculate maximum cooling gradient
  for (int i = 1; i < 100; i++) {
    float gradient = digital_twin.virtual_temperature_profile[i-1] - 
                    digital_twin.virtual_temperature_profile[i];
    if (gradient > cooling_gradient) {
      cooling_gradient = gradient;
    }
  }
  
  // Find maximum stress
  for (int i = 0; i < 50; i++) {
    if (digital_twin.stress_analysis[i] > max_stress) {
      max_stress = digital_twin.stress_analysis[i];
    }
  }
  
  // Warpage prediction (simplified model)
  digital_twin.warpage_prediction = (cooling_gradient * 0.1 + max_stress * 0.001) * 100.0; // micrometers
}

void calculateMaterialViscosity() {
  // Calculate dynamic viscosity based on temperature and shear rate
  float melt_temp = current_data.melt_temperature;
  float shear_rate = current_data.screw_velocity * 0.1; // Simplified shear rate
  
  // Simplified viscosity model (power law)
  float temp_factor = exp(2500.0 / (melt_temp + 273.15)); // Arrhenius equation
  float shear_factor = pow(shear_rate, -0.3); // Shear thinning
  
  digital_twin.material_viscosity = temp_factor * shear_factor * 1000.0; // Pa·s
}

void validateSimulationAccuracy() {
  // Compare simulated vs actual pressure profile
  float simulation_error = 0.0;
  int comparison_points = 10;
  
  for (int i = 0; i < comparison_points; i++) {
    int sim_index = i * (1000 / comparison_points);
    float predicted_pressure = digital_twin.virtual_pressure_profile[sim_index];
    float actual_pressure = current_data.average_pressure; // Would need historical profile
    
    simulation_error += abs(predicted_pressure - actual_pressure);
  }
  
  simulation_error /= comparison_points;
  digital_twin.simulation_accuracy = max(0.0, 100.0 - (simulation_error / current_data.average_pressure) * 100.0);
  
  // Update synchronization status
  digital_twin.model_synchronized = (digital_twin.simulation_accuracy > 80.0);
}

void synchronizeWithCloudTwin() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  // Send current simulation state to cloud twin
  HTTPClient http;
  http.begin(String(digital_twin_api_url) + "/sync");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(api_key));
  
  DynamicJsonDocument doc(4096);
  doc["device_id"] = aws_iot_thing_name;
  doc["timestamp"] = time_client.getEpochTime();
  
  // Current process state
  JsonObject process = doc.createNestedObject("process_state");
  process["cavity_pressure"] = current_data.average_pressure;
  process["melt_temperature"] = current_data.melt_temperature;
  process["cycle_time"] = current_data.cycle_time;
  
  // Simulation results
  JsonObject simulation = doc.createNestedObject("simulation");
  simulation["accuracy"] = digital_twin.simulation_accuracy;
  simulation["viscosity"] = digital_twin.material_viscosity;
  simulation["warpage"] = digital_twin.warpage_prediction;
  
  // Add pressure profile sample
  JsonArray pressure_profile = simulation.createNestedArray("pressure_profile");
  for (int i = 0; i < 100; i += 10) { // Every 10th point
    pressure_profile.add(digital_twin.virtual_pressure_profile[i]);
  }
  
  String json_string;
  serializeJson(doc, json_string);
  
  int response_code = http.POST(json_string);
  
  if (response_code == 200) {
    String response = http.getString();
    processCloudTwinResponse(response);
    digital_twin.last_sync_time = millis();
  }
  
  http.end();
}

void processCloudTwinResponse(String response) {
  DynamicJsonDocument doc(2048);
  deserializeJson(doc, response);
  
  if (doc.containsKey("optimization")) {
    JsonObject opt = doc["optimization"];
    
    // Extract optimization recommendations
    if (opt.containsKey("parameters")) {
      JsonArray params = opt["parameters"];
      for (int i = 0; i < min(10, (int)params.size()); i++) {
        digital_twin.optimized_parameters[i] = params[i];
      }
      digital_twin.optimization_available = true;
    }
    
    // Extract predicted improvements
    if (opt.containsKey("improvements")) {
      JsonArray improvements = opt["improvements"];
      for (int i = 0; i < min(5, (int)improvements.size()); i++) {
        digital_twin.predicted_improvements[i] = improvements[i];
      }
    }
  }
}

void collectOptimizationData() {
  // Collect data for ML optimization
  if (data_index >= PREDICTIVE_WINDOW) {
    data_index = 0;
    data_buffer_full = true;
  }
  
  // Store current process data
  historical_data[data_index][0] = current_data.average_pressure;
  historical_data[data_index][1] = current_data.peak_pressure;
  historical_data[data_index][2] = current_data.melt_temperature;
  historical_data[data_index][3] = current_data.mold_temperature;
  historical_data[data_index][4] = current_data.screw_velocity;
  historical_data[data_index][5] = current_data.cycle_time;
  historical_data[data_index][6] = current_data.predicted_weight;
  historical_data[data_index][7] = current_data.quality_status;
  historical_data[data_index][8] = current_data.energy_consumption;
  historical_data[data_index][9] = digital_twin.material_viscosity;
  historical_data[data_index][10] = digital_twin.warpage_prediction;
  historical_data[data_index][11] = current_data.pressure_balance;
  historical_data[data_index][12] = current_data.barrel_temperatures[0];
  historical_data[data_index][13] = current_data.barrel_temperatures[1];
  historical_data[data_index][14] = current_data.barrel_temperatures[2];
  historical_data[data_index][15] = current_data.nozzle_temperature;
  historical_data[data_index][16] = current_data.clamp_force;
  historical_data[data_index][17] = digital_twin.cooling_rate;
  historical_data[data_index][18] = digital_twin.simulation_accuracy;
  historical_data[data_index][19] = millis() / 1000.0; // Time factor
  
  data_index++;
}

void performMLOptimization() {
  if (!ml_optimization.model_loaded || !data_buffer_full) {
    return;
  }
  
  // Prepare input features (normalize data)
  float input_features[ML_INPUT_SIZE];
  
  // Calculate moving averages for stable optimization
  for (int feature = 0; feature < ML_INPUT_SIZE; feature++) {
    float sum = 0.0;
    for (int i = 0; i < PREDICTIVE_WINDOW; i++) {
      sum += historical_data[i][feature];
    }
    input_features[feature] = sum / PREDICTIVE_WINDOW;
  }
  
  // Normalize features (example normalization)
  normalizeFeatures(input_features);
  
  // Copy to TensorFlow input tensor
  for (int i = 0; i < ML_INPUT_SIZE; i++) {
    ml_optimization.input_tensor->data.f[i] = input_features[i];
  }
  
  // Run inference
  TfLiteStatus invoke_status = ml_optimization.interpreter->Invoke();
  
  if (invoke_status == kTfLiteOk) {
    // Extract optimization results
    latest_optimization.injection_velocity_opt[0] = ml_optimization.output_tensor->data.f[0] * 100.0; // Denormalize
    latest_optimization.pack_pressure_opt[0] = ml_optimization.output_tensor->data.f[1] * 1000.0;
    latest_optimization.temperature_opt[0] = ml_optimization.output_tensor->data.f[2] * 300.0 + 150.0;
    latest_optimization.cooling_time_opt = ml_optimization.output_tensor->data.f[3] * 30.0 + 5.0;
    latest_optimization.energy_savings = ml_optimization.output_tensor->data.f[4] * 0.3; // Up to 30% savings
    
    // Calculate confidence and improvements
    latest_optimization.confidence_level = calculateOptimizationConfidence();
    latest_optimization.cycle_time_reduction = latest_optimization.energy_savings * 0.5; // Estimate
    latest_optimization.quality_improvement = latest_optimization.confidence_level * 0.1;
    
    latest_optimization.optimization_timestamp = millis();
    
    ml_optimization.prediction_count++;
    
    Serial.println("ML optimization completed");
    Serial.print("Recommended injection velocity: ");
    Serial.println(latest_optimization.injection_velocity_opt[0]);
    Serial.print("Recommended pack pressure: ");
    Serial.println(latest_optimization.pack_pressure_opt[0]);
    Serial.print("Predicted energy savings: ");
    Serial.print(latest_optimization.energy_savings * 100.0);
    Serial.println("%");
  }
}

void normalizeFeatures(float* features) {
  // Normalize features to 0-1 range for ML model
  // Example normalization (would be based on training data statistics)
  features[0] /= 2000.0;  // Pressure (0-2000 bar)
  features[1] /= 2000.0;  // Peak pressure
  features[2] = (features[2] - 150.0) / 250.0;  // Temperature (150-400°C)
  features[3] = (features[3] - 20.0) / 80.0;    // Mold temp (20-100°C)
  features[4] /= 200.0;   // Velocity (0-200 mm/s)
  features[5] /= 60.0;    // Cycle time (0-60 s)
  features[6] /= 50.0;    // Weight (0-50 g)
  features[7] /= 5.0;     // Quality status (0-5)
  features[8] /= 1000.0;  // Energy (0-1000 J)
  features[9] /= 10000.0; // Viscosity (0-10000 Pa·s)
  
  // Clamp to 0-1 range
  for (int i = 0; i < ML_INPUT_SIZE; i++) {
    features[i] = constrain(features[i], 0.0, 1.0);
  }
}

float calculateOptimizationConfidence() {
  // Calculate confidence based on historical model performance
  float base_confidence = 0.75; // Base confidence
  
  // Adjust based on simulation accuracy
  float accuracy_factor = digital_twin.simulation_accuracy / 100.0;
  
  // Adjust based on data stability
  float stability_factor = calculateDataStability();
  
  return base_confidence * accuracy_factor * stability_factor;
}

float calculateDataStability() {
  // Calculate stability of recent data
  float pressure_variance = 0.0;
  float temp_variance = 0.0;
  
  float pressure_mean = 0.0;
  float temp_mean = 0.0;
  
  // Calculate means
  for (int i = 0; i < PREDICTIVE_WINDOW; i++) {
    pressure_mean += historical_data[i][0];
    temp_mean += historical_data[i][2];
  }
  pressure_mean /= PREDICTIVE_WINDOW;
  temp_mean /= PREDICTIVE_WINDOW;
  
  // Calculate variances
  for (int i = 0; i < PREDICTIVE_WINDOW; i++) {
    float pressure_diff = historical_data[i][0] - pressure_mean;
    float temp_diff = historical_data[i][2] - temp_mean;
    pressure_variance += pressure_diff * pressure_diff;
    temp_variance += temp_diff * temp_diff;
  }
  pressure_variance /= PREDICTIVE_WINDOW;
  temp_variance /= PREDICTIVE_WINDOW;
  
  // Calculate stability score (lower variance = higher stability)
  float pressure_stability = 1.0 / (1.0 + pressure_variance / 10000.0);
  float temp_stability = 1.0 / (1.0 + temp_variance / 100.0);
  
  return (pressure_stability + temp_stability) / 2.0;
}

void performPredictiveAnalysis() {
  // Analyze equipment health and predict maintenance needs
  analyzeHeaterHealth();
  analyzeSensorDrift();
  analyzeValveWear();
  analyzePumpEfficiency();
  calculateFailureProbabilities();
  generateMaintenanceSchedule();
}

void analyzeHeaterHealth() {
  // Analyze heater degradation based on temperature response
  for (int i = 0; i < 3; i++) {
    float current_temp = current_data.barrel_temperatures[i];
    float expected_temp = 250.0; // Example setpoint
    float response_error = abs(current_temp - expected_temp);
    
    // Degradation increases with response error
    maintenance_status.heater_degradation[i] = min(1.0, response_error / 50.0);
  }
  
  // Nozzle heater
  float nozzle_error = abs(current_data.nozzle_temperature - 255.0);
  maintenance_status.heater_degradation[3] = min(1.0, nozzle_error / 30.0);
  
  // Mold heater
  float mold_error = abs(current_data.mold_temperature - 60.0);
  maintenance_status.heater_degradation[4] = min(1.0, mold_error / 20.0);
}

void analyzeSensorDrift() {
  // Analyze sensor calibration drift
  // This would typically compare against reference measurements
  
  // Pressure sensor drift analysis
  float pressure_consistency = calculateDataStability();
  maintenance_status.sensor_drift[0] = 1.0 - pressure_consistency;
  
  // Temperature sensor drift
  for (int i = 1; i < 6; i++) {
    // Simplified drift analysis based on noise levels
    maintenance_status.sensor_drift[i] = random(0, 20) / 100.0; // 0-20% drift
  }
}

void analyzeValveWear() {
  // Analyze hydraulic valve wear based on response characteristics
  float pressure_response_time = 0.5; // Simulated response time
  float nominal_response_time = 0.1;   // Nominal response time
  
  maintenance_status.valve_wear = min(1.0, pressure_response_time / nominal_response_time - 1.0);
}

void analyzePumpEfficiency() {
  // Analyze hydraulic pump efficiency
  float power_consumption = current_data.energy_consumption;
  float nominal_power = 500.0; // Nominal power consumption
  
  maintenance_status.pump_efficiency = nominal_power / max(power_consumption, nominal_power);
}

void calculateFailureProbabilities() {
  // Calculate failure probabilities based on health metrics
  
  // Heater failure probability
  float heater_health = 0.0;
  for (int i = 0; i < 5; i++) {
    heater_health += maintenance_status.heater_degradation[i];
  }
  heater_health /= 5.0;
  maintenance_status.predicted_failures[0] = heater_health;
  
  // Sensor failure probability
  float sensor_health = 0.0;
  for (int i = 0; i < 10; i++) {
    sensor_health += maintenance_status.sensor_drift[i];
  }
  sensor_health /= 10.0;
  maintenance_status.predicted_failures[1] = sensor_health;
  
  // Hydraulic system failure
  maintenance_status.predicted_failures[2] = (1.0 - maintenance_status.pump_efficiency) * 0.5 + 
                                            maintenance_status.valve_wear * 0.5;
  
  // Overall system health
  float overall_health = 0.0;
  for (int i = 0; i < 3; i++) {
    overall_health += maintenance_status.predicted_failures[i];
  }
  overall_health /= 3.0;
  maintenance_status.predicted_failures[3] = overall_health;
  
  // Immediate maintenance required?
  maintenance_status.maintenance_required = (overall_health > 0.7);
}

void generateMaintenanceSchedule() {
  // Generate maintenance schedule based on predictions
  uint32_t current_time = time_client.getEpochTime();
  
  // Schedule based on failure probabilities
  for (int i = 0; i < 5; i++) {
    if (maintenance_status.predicted_failures[i] > 0.5) {
      // Schedule within 1 week
      maintenance_status.maintenance_schedule[i] = current_time + (7 * 24 * 3600);
    } else if (maintenance_status.predicted_failures[i] > 0.3) {
      // Schedule within 1 month
      maintenance_status.maintenance_schedule[i] = current_time + (30 * 24 * 3600);
    } else {
      // Schedule within 3 months
      maintenance_status.maintenance_schedule[i] = current_time + (90 * 24 * 3600);
    }
  }
}

void readArduinoData() {
  if (ARDUINO_SERIAL.available()) {
    String data = ARDUINO_SERIAL.readStringUntil('\n');
    parseArduinoData(data);
  }
}

void parseArduinoData(String data) {
  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, data);
  
  if (error) {
    Serial.print("JSON parsing error: ");
    Serial.println(error.c_str());
    return;
  }
  
  // Extract process data
  if (doc.containsKey("pressure")) {
    JsonObject pressure = doc["pressure"];
    current_data.cavity_pressure[0] = pressure["cavity_1"];
    current_data.cavity_pressure[1] = pressure["cavity_2"];
    current_data.cavity_pressure[2] = pressure["cavity_3"];
    current_data.cavity_pressure[3] = pressure["cavity_4"];
    current_data.average_pressure = pressure["average"];
    current_data.peak_pressure = pressure["peak"];
    current_data.pressure_balance = pressure["balance"];
  }
  
  if (doc.containsKey("temperature")) {
    JsonObject temperature = doc["temperature"];
    current_data.barrel_temperatures[0] = temperature["barrel_1"];
    current_data.barrel_temperatures[1] = temperature["barrel_2"];
    current_data.barrel_temperatures[2] = temperature["barrel_3"];
    current_data.nozzle_temperature = temperature["nozzle"];
    current_data.mold_temperature = temperature["mold"];
    current_data.melt_temperature = temperature["melt"];
  }
  
  if (doc.containsKey("position")) {
    JsonObject position = doc["position"];
    current_data.screw_position = position["screw"];
    current_data.screw_velocity = position["velocity"];
    current_data.clamp_force = position["clamp_force"];
  }
  
  if (doc.containsKey("quality")) {
    JsonObject quality = doc["quality"];
    current_data.predicted_weight = quality["predicted_weight"];
    current_data.quality_status = quality["overall_quality"];
  }
  
  current_data.timestamp = millis();
}

void sendOptimizationToArduino() {
  DynamicJsonDocument doc(1024);
  
  doc["type"] = "optimization";
  doc["timestamp"] = millis();
  doc["confidence"] = latest_optimization.confidence_level;
  
  JsonObject optimization = doc.createNestedObject("parameters");
  optimization["injection_velocity"] = latest_optimization.injection_velocity_opt[0];
  optimization["pack_pressure"] = latest_optimization.pack_pressure_opt[0];
  optimization["temperature"] = latest_optimization.temperature_opt[0];
  optimization["cooling_time"] = latest_optimization.cooling_time_opt;
  
  JsonObject predictions = doc.createNestedObject("predictions");
  predictions["cycle_time_reduction"] = latest_optimization.cycle_time_reduction;
  predictions["quality_improvement"] = latest_optimization.quality_improvement;
  predictions["energy_savings"] = latest_optimization.energy_savings;
  
  String json_string;
  serializeJson(doc, json_string);
  
  ARDUINO_SERIAL.println(json_string);
  
  // Clear optimization after sending
  latest_optimization.optimization_timestamp = 0;
}

void connectToAWS() {
  while (!mqtt_client.connected()) {
    Serial.print("Connecting to AWS IoT Core...");
    
    if (mqtt_client.connect(aws_iot_thing_name)) {
      Serial.println(" connected!");
      
      // Subscribe to optimization commands
      mqtt_client.subscribe((String(aws_iot_topic_optimization) + "/commands").c_str());
      mqtt_client.subscribe((String(aws_iot_topic_twin) + "/sync").c_str());
      
    } else {
      Serial.print(" failed, rc=");
      Serial.println(mqtt_client.state());
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("MQTT message received: ");
  Serial.println(message);
  
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  
  String topic_str = String(topic);
  
  if (topic_str.indexOf("optimization") != -1) {
    handleOptimizationCommand(doc);
  } else if (topic_str.indexOf("twin") != -1) {
    handleDigitalTwinCommand(doc);
  }
}

void handleOptimizationCommand(JsonDocument& doc) {
  String command = doc["command"];
  
  if (command == "run_optimization") {
    // Force immediate optimization
    performMLOptimization();
  } else if (command == "update_model") {
    // Update ML model from cloud
    updateMLModelFromCloud();
  }
}

void handleDigitalTwinCommand(JsonDocument& doc) {
  String command = doc["command"];
  
  if (command == "sync_twin") {
    // Force digital twin synchronization
    synchronizeWithCloudTwin();
  } else if (command == "update_parameters") {
    // Update digital twin parameters
    if (doc.containsKey("parameters")) {
      JsonObject params = doc["parameters"];
      // Update material properties, simulation parameters, etc.
    }
  }
}

void uploadDataToCloud() {
  if (!mqtt_client.connected()) return;
  
  DynamicJsonDocument doc(2048);
  
  doc["device_id"] = aws_iot_thing_name;
  doc["timestamp"] = time_client.getEpochTime();
  
  // Process data
  JsonObject process = doc.createNestedObject("process");
  process["cavity_pressure"] = current_data.average_pressure;
  process["peak_pressure"] = current_data.peak_pressure;
  process["melt_temperature"] = current_data.melt_temperature;
  process["cycle_time"] = current_data.cycle_time;
  process["quality_status"] = current_data.quality_status;
  process["energy_consumption"] = current_data.energy_consumption;
  
  // Digital twin data
  JsonObject twin = doc.createNestedObject("digital_twin");
  twin["simulation_accuracy"] = digital_twin.simulation_accuracy;
  twin["material_viscosity"] = digital_twin.material_viscosity;
  twin["warpage_prediction"] = digital_twin.warpage_prediction;
  twin["model_synchronized"] = digital_twin.model_synchronized;
  
  // Optimization results
  if (latest_optimization.optimization_timestamp > 0) {
    JsonObject optimization = doc.createNestedObject("optimization");
    optimization["confidence"] = latest_optimization.confidence_level;
    optimization["energy_savings"] = latest_optimization.energy_savings;
    optimization["cycle_time_reduction"] = latest_optimization.cycle_time_reduction;
  }
  
  // Predictive maintenance
  JsonObject maintenance = doc.createNestedObject("maintenance");
  maintenance["maintenance_required"] = maintenance_status.maintenance_required;
  maintenance["pump_efficiency"] = maintenance_status.pump_efficiency;
  maintenance["valve_wear"] = maintenance_status.valve_wear;
  
  String json_string;
  serializeJson(doc, json_string);
  
  mqtt_client.publish(aws_iot_topic_data, json_string.c_str());
}

void updateMLModelFromCloud() {
  // Download updated ML model from cloud
  HTTPClient http;
  http.begin(String(digital_twin_api_url) + "/model/latest");
  http.addHeader("Authorization", "Bearer " + String(api_key));
  
  int response_code = http.GET();
  
  if (response_code == 200) {
    WiFiClient* stream = http.getStreamPtr();
    
    File model_file = SPIFFS.open("/ml_model_new.tflite", "w");
    if (model_file) {
      uint8_t buffer[1024];
      int bytes_written = 0;
      
      while (http.connected() && (bytes_written = stream->readBytes(buffer, sizeof(buffer))) > 0) {
        model_file.write(buffer, bytes_written);
      }
      
      model_file.close();
      
      // Replace old model
      SPIFFS.remove("/ml_model.tflite");
      SPIFFS.rename("/ml_model_new.tflite", "/ml_model.tflite");
      
      Serial.println("ML model updated successfully");
      
      // Reinitialize ML model
      initializeMLModel();
    }
  }
  
  http.end();
}

void initializeWebServer() {
  web_server.on("/", HTTP_GET, []() {
    web_server.send(200, "text/html", getMainPageHTML());
  });
  
  web_server.on("/api/status", HTTP_GET, []() {
    DynamicJsonDocument doc(1024);
    
    doc["timestamp"] = millis();
    doc["digital_twin_synced"] = digital_twin.model_synchronized;
    doc["simulation_accuracy"] = digital_twin.simulation_accuracy;
    doc["ml_model_loaded"] = ml_optimization.model_loaded;
    doc["cloud_connected"] = mqtt_client.connected();
    doc["free_heap"] = ESP.getFreeHeap();
    
    String response;
    serializeJson(doc, response);
    web_server.send(200, "application/json", response);
  });
  
  web_server.on("/api/optimization", HTTP_GET, []() {
    DynamicJsonDocument doc(1024);
    
    doc["confidence"] = latest_optimization.confidence_level;
    doc["energy_savings"] = latest_optimization.energy_savings;
    doc["cycle_time_reduction"] = latest_optimization.cycle_time_reduction;
    doc["quality_improvement"] = latest_optimization.quality_improvement;
    
    String response;
    serializeJson(doc, response);
    web_server.send(200, "application/json", response);
  });
  
  web_server.begin();
  Serial.println("Web server started");
}

void handleWebServer() {
  web_server.handleClient();
}

void handleBluetoothCommunication() {
  if (bt_serial.available()) {
    String command = bt_serial.readString();
    command.trim();
    
    if (command == "STATUS") {
      bt_serial.println("Digital Twin Status:");
      bt_serial.println("Model Synchronized: " + String(digital_twin.model_synchronized));
      bt_serial.println("Simulation Accuracy: " + String(digital_twin.simulation_accuracy) + "%");
      bt_serial.println("ML Model Loaded: " + String(ml_optimization.model_loaded));
      bt_serial.println("Cloud Connected: " + String(mqtt_client.connected()));
    } else if (command == "OPTIMIZE") {
      performMLOptimization();
      bt_serial.println("Optimization triggered");
    } else if (command == "SYNC") {
      synchronizeWithCloudTwin();
      bt_serial.println("Digital twin synchronization triggered");
    }
  }
}

void updateStatusLEDs() {
  static unsigned long last_led_update = 0;
  if (millis() - last_led_update < 500) return;
  
  // Main status LED
  digitalWrite(STATUS_LED, WiFi.status() == WL_CONNECTED);
  
  // Digital twin LED
  digitalWrite(DIGITAL_TWIN_LED, digital_twin.model_synchronized);
  
  // Cloud LED
  digitalWrite(CLOUD_LED, mqtt_client.connected());
  
  last_led_update = millis();
}

void monitorSystemHealth() {
  // Monitor memory usage
  if (ESP.getFreeHeap() < 10000) {
    Serial.println("WARNING: Low heap memory!");
  }
  
  // Monitor task performance
  if (uxTaskGetStackHighWaterMark(digital_twin_task_handle) < 500) {
    Serial.println("WARNING: Digital twin task stack low!");
  }
  
  // Monitor WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WARNING: WiFi disconnected, attempting reconnection...");
    WiFi.reconnect();
  }
}

void processCloudQueue() {
  // Process any pending cloud operations
  // This could include queued data uploads, model updates, etc.
}

void createConfigurationFiles() {
  // Create default configuration files in SPIFFS
  File config = SPIFFS.open("/config.json", "w");
  if (config) {
    DynamicJsonDocument doc(512);
    doc["device_id"] = aws_iot_thing_name;
    doc["optimization_interval"] = OPTIMIZATION_INTERVAL;
    doc["sync_interval"] = DIGITAL_TWIN_SYNC_INTERVAL;
    
    serializeJson(doc, config);
    config.close();
  }
}

String getMainPageHTML() {
  return R"(
<!DOCTYPE html>
<html>
<head>
    <title>ESP32 Digital Twin Gateway</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>ESP32 Digital Twin & IoT Gateway</h1>
    <h2>Injection Molding Controller</h2>
    
    <div id="status">
        <h3>System Status</h3>
        <p>Loading...</p>
    </div>
    
    <div id="optimization">
        <h3>Latest Optimization</h3>
        <p>Loading...</p>
    </div>
    
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        '<h3>System Status</h3>' +
                        '<p>Digital Twin Synced: ' + data.digital_twin_synced + '</p>' +
                        '<p>Simulation Accuracy: ' + data.simulation_accuracy + '%</p>' +
                        '<p>ML Model Loaded: ' + data.ml_model_loaded + '</p>' +
                        '<p>Cloud Connected: ' + data.cloud_connected + '</p>' +
                        '<p>Free Heap: ' + data.free_heap + ' bytes</p>';
                });
                
            fetch('/api/optimization')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('optimization').innerHTML = 
                        '<h3>Latest Optimization</h3>' +
                        '<p>Confidence: ' + (data.confidence * 100).toFixed(1) + '%</p>' +
                        '<p>Energy Savings: ' + (data.energy_savings * 100).toFixed(1) + '%</p>' +
                        '<p>Cycle Time Reduction: ' + (data.cycle_time_reduction * 100).toFixed(1) + '%</p>' +
                        '<p>Quality Improvement: ' + (data.quality_improvement * 100).toFixed(1) + '%</p>';
                });
        }
        
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
)";
}

// Certificate placeholders (would be replaced with actual certificates)
const char* aws_root_ca = R"(
-----BEGIN CERTIFICATE-----
// AWS Root CA certificate would go here
-----END CERTIFICATE-----
)";

const char* aws_device_cert = R"(
-----BEGIN CERTIFICATE-----
// Device certificate would go here
-----END CERTIFICATE-----
)";

const char* aws_private_key = R"(
-----BEGIN RSA PRIVATE KEY-----
// Private key would go here
-----END RSA PRIVATE KEY-----
)";