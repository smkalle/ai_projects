/*
 * Program 30: Digital Twin Platform - Sensor Hub Controller
 * 
 * Comprehensive sensor integration system for the digital twin platform,
 * providing real-time data collection from multiple manufacturing processes
 * including CNC machining, 3D printing, injection molding, and assembly operations.
 * 
 * Features:
 * - Multi-process sensor integration (temperature, pressure, vibration, vision)
 * - High-speed data acquisition with <100ms synchronization latency
 * - Edge computing preprocessing and feature extraction
 * - Real-time anomaly detection and alerting
 * - Bi-directional control interface with digital twin
 * - Machine learning inference at the edge
 * - Protocol conversion (Modbus, OPC-UA, MQTT)
 * - Predictive maintenance monitoring
 * - Quality prediction and process optimization
 * 
 * Hardware: Arduino Mega 2560 + Arduino Due + ESP32 + Jetson Nano
 * Protocols: Serial, SPI, I2C, Ethernet, WiFi, CAN
 */

#include <SPI.h>
#include <Wire.h>
#include <Ethernet.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SD.h>
#include <TimeLib.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>
#include <MPU6050.h>
#include <HX711.h>
#include <Stepper.h>

// Network Configuration
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED};
IPAddress ip(192, 168, 1, 177);
IPAddress server(192, 168, 1, 100);
const char* mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;

// Digital Twin Configuration
const char* DEVICE_ID = "DT_SENSOR_HUB_001";
const char* PLATFORM_VERSION = "2.0";
const int DATA_SYNC_INTERVAL = 50;    // 20Hz data sync
const int FAST_SYNC_INTERVAL = 10;    // 100Hz for critical sensors
const int PREDICTION_INTERVAL = 5000; // 5 second prediction updates

// System Objects
EthernetClient ethClient;
PubSubClient mqttClient(ethClient);
MPU6050 accelerometer;
OneWire tempWire(2);
DallasTemperature tempSensors(&tempWire);
DHT dht(22, DHT22);

// Data Structures
struct ManufacturingProcess {
    char process_id[16];
    char process_type[32];     // CNC, 3D_PRINT, INJECTION, ASSEMBLY
    bool active;
    float cycle_time;          // Current cycle time (seconds)
    float target_cycle_time;   // Target cycle time (seconds)
    float efficiency;          // Process efficiency (%)
    float quality_score;       // Real-time quality score (0-100)
    unsigned long start_time;
    unsigned long last_update;
};

struct SensorData {
    // Temperature Sensors (12 channels)
    float temperatures[12];         // °C
    float ambient_temperature;      // °C
    float ambient_humidity;         // %RH
    
    // Pressure Sensors (8 channels)
    float pressures[8];            // bar
    float vacuum_level;            // mmHg
    
    // Vibration Sensors (6 axes)
    float accelerations[6];        // g
    float angular_velocities[6];   // rad/s
    float vibration_rms;           // g RMS
    float vibration_peak;          // g peak
    
    // Force/Load Sensors (4 channels)
    float forces[4];               // N
    float torques[4];              // Nm
    
    // Energy Monitoring
    float voltage[3];              // V (3-phase)
    float current[3];              // A (3-phase)
    float power_active;            // kW
    float power_reactive;          // kVAR
    float power_factor;            // 0-1
    float energy_consumed;         // kWh
    
    // Position/Motion Sensors
    float positions[8];            // mm
    float velocities[8];           // mm/s
    float encoder_counts[8];       // counts
    
    // Flow Sensors
    float flow_rates[4];           // L/min
    float fluid_temperatures[4];   // °C
    
    // Vision/Quality Sensors
    float dimensional_accuracy;    // mm deviation
    float surface_roughness;       // Ra (μm)
    float color_consistency;       // 0-100 score
    bool defect_detected;
    
    unsigned long timestamp;
    bool data_valid;
    float data_quality;            // 0-1 (completeness/accuracy)
};

struct ProcessPrediction {
    float predicted_quality;       // 0-100
    float predicted_cycle_time;    // seconds
    float predicted_defect_rate;   // %
    float remaining_tool_life;     // hours
    float maintenance_probability; // 0-1
    float energy_forecast;         // kWh for next cycle
    float confidence_level;        // 0-1
    unsigned long prediction_time;
    bool prediction_valid;
};

struct ControlCommands {
    bool emergency_stop;
    bool process_pause;
    bool quality_hold;
    float speed_override;          // 0-150%
    float feed_override;           // 0-150%
    float temperature_setpoints[12]; // °C
    float pressure_setpoints[8];   // bar
    bool adaptive_control_enabled;
    bool predictive_mode_enabled;
    unsigned long command_timestamp;
};

struct DigitalTwinSync {
    bool sync_enabled;
    float sync_latency;            // ms
    float model_accuracy;          // 0-1
    unsigned long last_sync;
    unsigned long sync_count;
    float data_transmission_rate;  // KB/s
    bool physics_sync;
    bool ml_sync;
    bool control_sync;
};

// Global Variables
ManufacturingProcess processes[4];    // Support 4 concurrent processes
SensorData sensor_data;
ProcessPrediction predictions[4];
ControlCommands control_commands;
DigitalTwinSync dt_sync;

// Timing Variables
unsigned long last_sensor_read = 0;
unsigned long last_fast_sync = 0;
unsigned long last_prediction = 0;
unsigned long last_mqtt_publish = 0;
unsigned long last_health_check = 0;

// Configuration
const int TEMP_SENSOR_COUNT = 12;
const int PRESSURE_SENSOR_COUNT = 8;
const int VIBRATION_SENSOR_COUNT = 6;
const int FORCE_SENSOR_COUNT = 4;
const int POSITION_SENSOR_COUNT = 8;
const int FLOW_SENSOR_COUNT = 4;

// Pin Definitions
const int EMERGENCY_STOP_PIN = 2;
const int SYSTEM_READY_LED = 13;
const int DATA_ACTIVITY_LED = 12;
const int ERROR_LED = 11;
const int PROCESS_ACTIVE_LED = 10;

// ADC Configuration for High-Speed Acquisition
const int ADC_CHANNELS = 16;
const int ADC_RESOLUTION = 12;      // 12-bit ADC
const float ADC_VREF = 3.3;         // 3.3V reference
const int OVERSAMPLING_FACTOR = 16; // 16x oversampling for noise reduction

// Communication Buffers
char mqtt_buffer[4096];
char json_buffer[2048];
char command_buffer[512];

// Machine Learning Buffers
float ml_feature_buffer[100];
float ml_prediction_buffer[20];
int ml_feature_count = 0;

void setup() {
    Serial.begin(115200);
    Serial1.begin(921600);  // High-speed link to Raspberry Pi
    Serial2.begin(115200);  // Link to ESP32
    Serial3.begin(115200);  // Link to Jetson Nano
    
    Serial.println("Digital Twin Sensor Hub Starting...");
    Serial.println("Version: " + String(PLATFORM_VERSION));
    
    // Initialize I/O pins
    initializeGPIO();
    
    // Initialize sensor interfaces
    initializeSensorInterfaces();
    
    // Initialize network
    initializeNetworking();
    
    // Initialize processes
    initializeProcesses();
    
    // Initialize digital twin synchronization
    initializeDigitalTwinSync();
    
    // Perform system health check
    performSystemHealthCheck();
    
    Serial.println("Digital Twin Sensor Hub Ready!");
    Serial.println("Device ID: " + String(DEVICE_ID));
    Serial.println("Synchronization Latency Target: <100ms");
    
    // Signal system ready
    digitalWrite(SYSTEM_READY_LED, HIGH);
}

void loop() {
    unsigned long current_time = millis();
    
    // Handle emergency stop
    if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        handleEmergencyStop();
    }
    
    // Fast sensor reading loop (100Hz for critical sensors)
    if (current_time - last_fast_sync >= FAST_SYNC_INTERVAL) {
        readCriticalSensors();
        last_fast_sync = current_time;
        digitalWrite(DATA_ACTIVITY_LED, !digitalRead(DATA_ACTIVITY_LED));
    }
    
    // Standard sensor reading loop (20Hz for all sensors)
    if (current_time - last_sensor_read >= DATA_SYNC_INTERVAL) {
        readAllSensors();
        processData();
        updateProcessStates();
        synchronizeWithDigitalTwin();
        last_sensor_read = current_time;
    }
    
    // Prediction update loop (0.2Hz)
    if (current_time - last_prediction >= PREDICTION_INTERVAL) {
        updatePredictions();
        runEdgeMLInference();
        last_prediction = current_time;
    }
    
    // MQTT communication loop (10Hz)
    if (current_time - last_mqtt_publish >= 100) {
        if (!mqttClient.connected()) {
            reconnectMQTT();
        }
        mqttClient.loop();
        publishSensorData();
        last_mqtt_publish = current_time;
    }
    
    // System health check (1Hz)
    if (current_time - last_health_check >= 1000) {
        performSystemHealthCheck();
        updateSystemStatus();
        last_health_check = current_time;
    }
    
    // Process serial commands
    processSerialCommands();
    
    // Handle bi-directional control
    processBidirectionalControl();
    
    delay(1); // Small delay for system stability
}

void initializeGPIO() {
    // Configure input pins
    pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
    
    // Configure output pins
    pinMode(SYSTEM_READY_LED, OUTPUT);
    pinMode(DATA_ACTIVITY_LED, OUTPUT);
    pinMode(ERROR_LED, OUTPUT);
    pinMode(PROCESS_ACTIVE_LED, OUTPUT);
    
    // Initialize outputs
    digitalWrite(SYSTEM_READY_LED, LOW);
    digitalWrite(DATA_ACTIVITY_LED, LOW);
    digitalWrite(ERROR_LED, LOW);
    digitalWrite(PROCESS_ACTIVE_LED, LOW);
}

void initializeSensorInterfaces() {
    Serial.println("Initializing sensor interfaces...");
    
    // Initialize I2C bus
    Wire.begin();
    Wire.setClock(400000); // 400kHz I2C
    
    // Initialize SPI bus
    SPI.begin();
    SPI.setClockDivider(SPI_CLOCK_DIV4); // 4MHz SPI
    
    // Initialize temperature sensors
    tempSensors.begin();
    tempSensors.setResolution(12); // 12-bit resolution
    Serial.print("Temperature sensors found: ");
    Serial.println(tempSensors.getDeviceCount());
    
    // Initialize DHT sensor
    dht.begin();
    
    // Initialize accelerometer
    accelerometer.initialize();
    if (accelerometer.testConnection()) {
        Serial.println("MPU6050 connected successfully");
        accelerometer.setFullScaleAccelRange(MPU6050_ACCEL_FS_8);
        accelerometer.setFullScaleGyroRange(MPU6050_GYRO_FS_1000);
        accelerometer.setDLPFMode(MPU6050_DLPF_BW_20); // 20Hz low-pass filter
    } else {
        Serial.println("MPU6050 connection failed");
    }
    
    // Initialize analog sensors
    analogReference(EXTERNAL); // Use external 3.3V reference
    
    // Initialize sensor data structure
    memset(&sensor_data, 0, sizeof(sensor_data));
    sensor_data.data_valid = false;
    sensor_data.data_quality = 0.0;
    
    Serial.println("Sensor interfaces initialized");
}

void initializeNetworking() {
    Serial.println("Initializing networking...");
    
    // Initialize Ethernet
    if (Ethernet.begin(mac) == 0) {
        Serial.println("Failed to configure Ethernet using DHCP");
        Ethernet.begin(mac, ip);
    }
    
    Serial.print("IP address: ");
    Serial.println(Ethernet.localIP());
    
    // Initialize MQTT client
    mqttClient.setServer(mqtt_server, mqtt_port);
    mqttClient.setCallback(mqttCallback);
    mqttClient.setBufferSize(4096);
    
    // Connect to MQTT broker
    reconnectMQTT();
    
    Serial.println("Networking initialized");
}

void initializeProcesses() {
    Serial.println("Initializing manufacturing processes...");
    
    // Process 1: CNC Machining
    strcpy(processes[0].process_id, "CNC_001");
    strcpy(processes[0].process_type, "CNC_MACHINING");
    processes[0].active = false;
    processes[0].target_cycle_time = 180.0; // 3 minutes
    processes[0].efficiency = 100.0;
    processes[0].quality_score = 95.0;
    
    // Process 2: 3D Printing
    strcpy(processes[1].process_id, "3DP_001");
    strcpy(processes[1].process_type, "3D_PRINTING");
    processes[1].active = false;
    processes[1].target_cycle_time = 3600.0; // 1 hour
    processes[1].efficiency = 85.0;
    processes[1].quality_score = 90.0;
    
    // Process 3: Injection Molding
    strcpy(processes[2].process_id, "INJ_001");
    strcpy(processes[2].process_type, "INJECTION_MOLDING");
    processes[2].active = false;
    processes[2].target_cycle_time = 45.0; // 45 seconds
    processes[2].efficiency = 95.0;
    processes[2].quality_score = 98.0;
    
    // Process 4: Assembly
    strcpy(processes[3].process_id, "ASM_001");
    strcpy(processes[3].process_type, "ASSEMBLY");
    processes[3].active = false;
    processes[3].target_cycle_time = 120.0; // 2 minutes
    processes[3].efficiency = 90.0;
    processes[3].quality_score = 92.0;
    
    // Initialize control commands
    memset(&control_commands, 0, sizeof(control_commands));
    control_commands.speed_override = 100.0;
    control_commands.feed_override = 100.0;
    control_commands.adaptive_control_enabled = true;
    control_commands.predictive_mode_enabled = true;
    
    Serial.println("Manufacturing processes initialized");
}

void initializeDigitalTwinSync() {
    Serial.println("Initializing digital twin synchronization...");
    
    dt_sync.sync_enabled = true;
    dt_sync.sync_latency = 0.0;
    dt_sync.model_accuracy = 0.95;
    dt_sync.last_sync = millis();
    dt_sync.sync_count = 0;
    dt_sync.data_transmission_rate = 0.0;
    dt_sync.physics_sync = true;
    dt_sync.ml_sync = true;
    dt_sync.control_sync = true;
    
    Serial.println("Digital twin synchronization initialized");
}

void readCriticalSensors() {
    // Read high-frequency critical sensors for real-time control
    
    // Vibration monitoring (for tool condition and quality)
    int16_t ax, ay, az, gx, gy, gz;
    accelerometer.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
    
    sensor_data.accelerations[0] = ax / 4096.0; // Convert to g
    sensor_data.accelerations[1] = ay / 4096.0;
    sensor_data.accelerations[2] = az / 4096.0;
    sensor_data.angular_velocities[0] = gx / 32.8; // Convert to rad/s
    sensor_data.angular_velocities[1] = gy / 32.8;
    sensor_data.angular_velocities[2] = gz / 32.8;
    
    // Calculate RMS vibration
    float sum_squares = 0;
    for (int i = 0; i < 3; i++) {
        sum_squares += sensor_data.accelerations[i] * sensor_data.accelerations[i];
    }
    sensor_data.vibration_rms = sqrt(sum_squares / 3.0);
    
    // Critical temperature monitoring
    sensor_data.temperatures[0] = analogRead(A0) * ADC_VREF / 1024.0 * 100.0; // PT100 sensor
    sensor_data.temperatures[1] = analogRead(A1) * ADC_VREF / 1024.0 * 100.0;
    
    // Critical pressure monitoring
    sensor_data.pressures[0] = (analogRead(A2) * ADC_VREF / 1024.0 - 0.5) * 25.0; // 4-20mA sensor
    sensor_data.pressures[1] = (analogRead(A3) * ADC_VREF / 1024.0 - 0.5) * 25.0;
    
    // Position feedback for motion control
    sensor_data.positions[0] = analogRead(A4) * ADC_VREF / 1024.0 * 100.0; // LVDT
    sensor_data.positions[1] = analogRead(A5) * ADC_VREF / 1024.0 * 100.0;
    
    // Update timestamp
    sensor_data.timestamp = millis();
}

void readAllSensors() {
    // Read all sensors for comprehensive data collection
    
    Serial.println("Reading all sensors...");
    
    // Temperature sensors (DS18B20 array)
    tempSensors.requestTemperatures();
    for (int i = 0; i < min(TEMP_SENSOR_COUNT, tempSensors.getDeviceCount()); i++) {
        sensor_data.temperatures[i] = tempSensors.getTempCByIndex(i);
        if (sensor_data.temperatures[i] == DEVICE_DISCONNECTED_C) {
            sensor_data.temperatures[i] = -999.0; // Error value
        }
    }
    
    // Ambient conditions
    sensor_data.ambient_temperature = dht.readTemperature();
    sensor_data.ambient_humidity = dht.readHumidity();
    
    // Pressure sensors (analog 4-20mA)
    for (int i = 0; i < PRESSURE_SENSOR_COUNT; i++) {
        float raw_voltage = analogRead(A8 + i) * ADC_VREF / 1024.0;
        sensor_data.pressures[i] = (raw_voltage - 0.5) * 25.0; // Convert 4-20mA to pressure
    }
    
    // Vacuum level
    sensor_data.vacuum_level = analogRead(A14) * ADC_VREF / 1024.0 * 760.0; // mmHg
    
    // Extended vibration analysis
    for (int i = 3; i < VIBRATION_SENSOR_COUNT; i++) {
        sensor_data.accelerations[i] = (analogRead(A15 - (i-3)) * ADC_VREF / 1024.0 - 1.65) * 6.0; // ±6g sensor
    }
    
    // Calculate vibration peak
    sensor_data.vibration_peak = 0;
    for (int i = 0; i < VIBRATION_SENSOR_COUNT; i++) {
        if (abs(sensor_data.accelerations[i]) > sensor_data.vibration_peak) {
            sensor_data.vibration_peak = abs(sensor_data.accelerations[i]);
        }
    }
    
    // Force/Load sensors (strain gauges)
    for (int i = 0; i < FORCE_SENSOR_COUNT; i++) {
        // Simulated force readings - would connect to HX711 load cell amplifiers
        sensor_data.forces[i] = random(-1000, 1000); // ±1000N range
        sensor_data.torques[i] = random(-50, 50);     // ±50Nm range
    }
    
    // Energy monitoring (simulate 3-phase power)
    for (int i = 0; i < 3; i++) {
        sensor_data.voltage[i] = 230.0 + random(-10, 10); // 230V ±10V
        sensor_data.current[i] = 10.0 + random(-2, 2);    // 10A ±2A
    }
    sensor_data.power_active = sensor_data.voltage[0] * sensor_data.current[0] * 
                               sensor_data.voltage[1] * sensor_data.current[1] * 
                               sensor_data.voltage[2] * sensor_data.current[2] / 1000.0; // kW
    sensor_data.power_factor = 0.85 + random(-5, 5) / 100.0; // 0.85 ±0.05
    sensor_data.energy_consumed += sensor_data.power_active * DATA_SYNC_INTERVAL / 3600000.0; // kWh
    
    // Position sensors (encoders and LVDTs)
    for (int i = 0; i < POSITION_SENSOR_COUNT; i++) {
        // Simulated position readings
        sensor_data.positions[i] = sin(millis() / 1000.0 + i) * 10.0; // ±10mm sinusoidal
        sensor_data.velocities[i] = cos(millis() / 1000.0 + i) * 10.0; // mm/s
        sensor_data.encoder_counts[i] += random(-5, 5); // Incremental encoder
    }
    
    // Flow sensors
    for (int i = 0; i < FLOW_SENSOR_COUNT; i++) {
        sensor_data.flow_rates[i] = 5.0 + random(-1, 1); // 5 ±1 L/min
        sensor_data.fluid_temperatures[i] = 25.0 + random(-2, 2); // 25 ±2°C
    }
    
    // Vision/Quality sensors (simulated)
    sensor_data.dimensional_accuracy = random(-50, 50) / 1000.0; // ±0.05mm
    sensor_data.surface_roughness = 1.6 + random(-20, 20) / 100.0; // 1.6 ±0.2 Ra μm
    sensor_data.color_consistency = 95 + random(-5, 5); // 95 ±5%
    sensor_data.defect_detected = (random(0, 100) < 5); // 5% defect probability
    
    // Data quality assessment
    calculateDataQuality();
    
    sensor_data.data_valid = true;
    sensor_data.timestamp = millis();
    
    Serial.println("All sensors read successfully");
}

void calculateDataQuality() {
    int valid_sensors = 0;
    int total_sensors = 0;
    
    // Check temperature sensors
    for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
        total_sensors++;
        if (sensor_data.temperatures[i] > -200 && sensor_data.temperatures[i] < 500) {
            valid_sensors++;
        }
    }
    
    // Check pressure sensors
    for (int i = 0; i < PRESSURE_SENSOR_COUNT; i++) {
        total_sensors++;
        if (sensor_data.pressures[i] >= 0 && sensor_data.pressures[i] < 1000) {
            valid_sensors++;
        }
    }
    
    // Check vibration sensors
    for (int i = 0; i < VIBRATION_SENSOR_COUNT; i++) {
        total_sensors++;
        if (abs(sensor_data.accelerations[i]) < 50) { // Reasonable acceleration limit
            valid_sensors++;
        }
    }
    
    // Check ambient sensors
    total_sensors += 2;
    if (!isnan(sensor_data.ambient_temperature) && !isnan(sensor_data.ambient_humidity)) {
        valid_sensors += 2;
    }
    
    sensor_data.data_quality = (float)valid_sensors / total_sensors;
    
    if (sensor_data.data_quality < 0.8) {
        digitalWrite(ERROR_LED, HIGH);
        Serial.println("Warning: Data quality below 80%");
    } else {
        digitalWrite(ERROR_LED, LOW);
    }
}

void processData() {
    // Apply signal processing and feature extraction
    
    // Moving average filter for temperature stability
    static float temp_buffer[TEMP_SENSOR_COUNT][10];
    static int temp_index = 0;
    
    for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
        temp_buffer[i][temp_index] = sensor_data.temperatures[i];
        
        float sum = 0;
        for (int j = 0; j < 10; j++) {
            sum += temp_buffer[i][j];
        }
        sensor_data.temperatures[i] = sum / 10.0; // 10-point moving average
    }
    temp_index = (temp_index + 1) % 10;
    
    // Vibration feature extraction for condition monitoring
    static float vibration_history[100];
    static int vib_index = 0;
    
    vibration_history[vib_index] = sensor_data.vibration_rms;
    vib_index = (vib_index + 1) % 100;
    
    // Calculate vibration trend
    float recent_avg = 0, old_avg = 0;
    for (int i = 0; i < 20; i++) {
        recent_avg += vibration_history[(vib_index - 1 - i + 100) % 100];
        old_avg += vibration_history[(vib_index - 21 - i + 100) % 100];
    }
    recent_avg /= 20.0;
    old_avg /= 20.0;
    
    float vibration_trend = (recent_avg - old_avg) / old_avg * 100.0; // % change
    
    // Anomaly detection for each process
    detectAnomalies();
    
    // Feature extraction for ML inference
    extractMLFeatures();
}

void detectAnomalies() {
    // Temperature anomaly detection
    for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
        if (sensor_data.temperatures[i] > 200.0) { // Over-temperature
            publishAlert("TEMPERATURE_HIGH", "Zone " + String(i+1) + " over-temperature: " + 
                        String(sensor_data.temperatures[i]) + "°C");
        }
        if (sensor_data.temperatures[i] < 5.0 && sensor_data.temperatures[i] > -100.0) { // Under-temperature
            publishAlert("TEMPERATURE_LOW", "Zone " + String(i+1) + " under-temperature: " + 
                        String(sensor_data.temperatures[i]) + "°C");
        }
    }
    
    // Vibration anomaly detection
    if (sensor_data.vibration_rms > 5.0) { // High vibration
        publishAlert("VIBRATION_HIGH", "Excessive vibration detected: " + 
                    String(sensor_data.vibration_rms) + "g RMS");
    }
    
    // Pressure anomaly detection
    for (int i = 0; i < PRESSURE_SENSOR_COUNT; i++) {
        if (sensor_data.pressures[i] > 100.0) { // Over-pressure
            publishAlert("PRESSURE_HIGH", "Channel " + String(i+1) + " over-pressure: " + 
                        String(sensor_data.pressures[i]) + " bar");
        }
    }
    
    // Power anomaly detection
    if (sensor_data.power_active > 50.0) { // High power consumption
        publishAlert("POWER_HIGH", "High power consumption: " + 
                    String(sensor_data.power_active) + " kW");
    }
    
    // Quality anomaly detection
    if (sensor_data.defect_detected) {
        publishAlert("QUALITY_DEFECT", "Quality defect detected - stopping process");
        control_commands.quality_hold = true;
    }
}

void extractMLFeatures() {
    // Extract features for machine learning models
    if (ml_feature_count < 100) {
        // Statistical features
        ml_feature_buffer[ml_feature_count++] = sensor_data.vibration_rms;
        ml_feature_buffer[ml_feature_count++] = sensor_data.vibration_peak;
        
        // Temperature features
        float temp_avg = 0, temp_std = 0;
        for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
            temp_avg += sensor_data.temperatures[i];
        }
        temp_avg /= TEMP_SENSOR_COUNT;
        
        for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
            temp_std += pow(sensor_data.temperatures[i] - temp_avg, 2);
        }
        temp_std = sqrt(temp_std / TEMP_SENSOR_COUNT);
        
        ml_feature_buffer[ml_feature_count++] = temp_avg;
        ml_feature_buffer[ml_feature_count++] = temp_std;
        
        // Power features
        ml_feature_buffer[ml_feature_count++] = sensor_data.power_active;
        ml_feature_buffer[ml_feature_count++] = sensor_data.power_factor;
        
        // Quality features
        ml_feature_buffer[ml_feature_count++] = sensor_data.dimensional_accuracy;
        ml_feature_buffer[ml_feature_count++] = sensor_data.surface_roughness;
    }
}

void updateProcessStates() {
    // Update each manufacturing process state
    for (int i = 0; i < 4; i++) {
        if (processes[i].active) {
            unsigned long current_time = millis();
            processes[i].cycle_time = (current_time - processes[i].start_time) / 1000.0;
            
            // Calculate efficiency
            if (processes[i].cycle_time > 0) {
                processes[i].efficiency = (processes[i].target_cycle_time / processes[i].cycle_time) * 100.0;
                processes[i].efficiency = constrain(processes[i].efficiency, 0.0, 150.0);
            }
            
            // Update quality score based on sensor data
            updateProcessQuality(i);
            
            processes[i].last_update = current_time;
            
            // Check for process completion
            if (processes[i].cycle_time >= processes[i].target_cycle_time) {
                completeProcess(i);
            }
        }
    }
    
    // Update overall process activity LED
    bool any_active = false;
    for (int i = 0; i < 4; i++) {
        if (processes[i].active) any_active = true;
    }
    digitalWrite(PROCESS_ACTIVE_LED, any_active);
}

void updateProcessQuality(int process_index) {
    float quality_score = 100.0;
    
    switch (process_index) {
        case 0: // CNC Machining
            // Quality based on vibration, dimensional accuracy, surface finish
            if (sensor_data.vibration_rms > 2.0) quality_score -= 10;
            if (abs(sensor_data.dimensional_accuracy) > 0.02) quality_score -= 15;
            if (sensor_data.surface_roughness > 2.0) quality_score -= 10;
            break;
            
        case 1: // 3D Printing
            // Quality based on temperature stability, flow consistency
            float temp_variation = 0;
            for (int i = 0; i < 4; i++) {
                temp_variation += abs(sensor_data.temperatures[i] - 200.0); // Target 200°C
            }
            temp_variation /= 4.0;
            if (temp_variation > 5.0) quality_score -= 20;
            if (sensor_data.flow_rates[0] < 4.0 || sensor_data.flow_rates[0] > 6.0) quality_score -= 15;
            break;
            
        case 2: // Injection Molding
            // Quality based on pressure profile, temperature control
            if (sensor_data.pressures[0] < 80.0 || sensor_data.pressures[0] > 120.0) quality_score -= 25;
            if (abs(sensor_data.temperatures[0] - 180.0) > 5.0) quality_score -= 15;
            break;
            
        case 3: // Assembly
            // Quality based on force/torque, position accuracy
            if (abs(sensor_data.forces[0]) > 500.0) quality_score -= 20;
            if (abs(sensor_data.positions[0]) > 0.1) quality_score -= 15;
            break;
    }
    
    // Apply defect detection penalty
    if (sensor_data.defect_detected) quality_score -= 30;
    
    processes[process_index].quality_score = constrain(quality_score, 0.0, 100.0);
}

void completeProcess(int process_index) {
    processes[process_index].active = false;
    
    Serial.print("Process completed: ");
    Serial.print(processes[process_index].process_type);
    Serial.print(" - Cycle time: ");
    Serial.print(processes[process_index].cycle_time);
    Serial.print("s, Quality: ");
    Serial.print(processes[process_index].quality_score);
    Serial.println("%");
    
    // Publish completion event
    DynamicJsonDocument doc(512);
    doc["event"] = "process_completed";
    doc["process_id"] = processes[process_index].process_id;
    doc["process_type"] = processes[process_index].process_type;
    doc["cycle_time"] = processes[process_index].cycle_time;
    doc["efficiency"] = processes[process_index].efficiency;
    doc["quality_score"] = processes[process_index].quality_score;
    doc["timestamp"] = millis();
    
    String payload;
    serializeJson(doc, payload);
    mqttClient.publish("digitaltwin/events/process_completed", payload.c_str());
}

void synchronizeWithDigitalTwin() {
    if (!dt_sync.sync_enabled) return;
    
    unsigned long sync_start = micros();
    
    // Send sensor data to Raspberry Pi edge server
    sendDataToEdgeServer();
    
    // Send data to ESP32 for IoT processing
    sendDataToESP32();
    
    // Send data to Jetson Nano for AI inference
    sendDataToJetsonNano();
    
    // Calculate synchronization latency
    unsigned long sync_end = micros();
    dt_sync.sync_latency = (sync_end - sync_start) / 1000.0; // Convert to milliseconds
    
    // Update sync statistics
    dt_sync.last_sync = millis();
    dt_sync.sync_count++;
    
    // Check if latency target is met
    if (dt_sync.sync_latency > 100.0) {
        Serial.println("Warning: Sync latency exceeded 100ms target: " + String(dt_sync.sync_latency) + "ms");
    }
}

void sendDataToEdgeServer() {
    // Send comprehensive data to Raspberry Pi for physics simulation
    DynamicJsonDocument doc(2048);
    
    doc["timestamp"] = sensor_data.timestamp;
    doc["device_id"] = DEVICE_ID;
    doc["data_quality"] = sensor_data.data_quality;
    
    // Temperature array
    JsonArray temps = doc.createNestedArray("temperatures");
    for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
        temps.add(sensor_data.temperatures[i]);
    }
    
    // Pressure array
    JsonArray pressures = doc.createNestedArray("pressures");
    for (int i = 0; i < PRESSURE_SENSOR_COUNT; i++) {
        pressures.add(sensor_data.pressures[i]);
    }
    
    // Vibration data
    JsonObject vibration = doc.createNestedObject("vibration");
    vibration["rms"] = sensor_data.vibration_rms;
    vibration["peak"] = sensor_data.vibration_peak;
    JsonArray accel = vibration.createNestedArray("accelerations");
    for (int i = 0; i < VIBRATION_SENSOR_COUNT; i++) {
        accel.add(sensor_data.accelerations[i]);
    }
    
    // Power data
    JsonObject power = doc.createNestedObject("power");
    power["active"] = sensor_data.power_active;
    power["factor"] = sensor_data.power_factor;
    power["energy"] = sensor_data.energy_consumed;
    
    // Process states
    JsonArray proc_array = doc.createNestedArray("processes");
    for (int i = 0; i < 4; i++) {
        JsonObject proc = proc_array.createNestedObject();
        proc["id"] = processes[i].process_id;
        proc["type"] = processes[i].process_type;
        proc["active"] = processes[i].active;
        proc["cycle_time"] = processes[i].cycle_time;
        proc["efficiency"] = processes[i].efficiency;
        proc["quality"] = processes[i].quality_score;
    }
    
    String payload;
    serializeJson(doc, payload);
    
    // Send via high-speed serial to Raspberry Pi
    Serial1.println(payload);
}

void sendDataToESP32() {
    // Send lightweight data to ESP32 for IoT connectivity
    DynamicJsonDocument doc(1024);
    
    doc["timestamp"] = sensor_data.timestamp;
    doc["temp_avg"] = (sensor_data.temperatures[0] + sensor_data.temperatures[1] + sensor_data.temperatures[2]) / 3.0;
    doc["pressure_avg"] = (sensor_data.pressures[0] + sensor_data.pressures[1]) / 2.0;
    doc["vibration"] = sensor_data.vibration_rms;
    doc["power"] = sensor_data.power_active;
    doc["quality"] = sensor_data.defect_detected ? 0 : 100;
    
    // Process summary
    int active_processes = 0;
    float avg_efficiency = 0;
    for (int i = 0; i < 4; i++) {
        if (processes[i].active) {
            active_processes++;
            avg_efficiency += processes[i].efficiency;
        }
    }
    if (active_processes > 0) avg_efficiency /= active_processes;
    
    doc["active_processes"] = active_processes;
    doc["avg_efficiency"] = avg_efficiency;
    
    String payload;
    serializeJson(doc, payload);
    
    // Send to ESP32
    Serial2.println(payload);
}

void sendDataToJetsonNano() {
    // Send ML features to Jetson Nano for AI inference
    if (ml_feature_count >= 20) { // Minimum features for inference
        DynamicJsonDocument doc(1024);
        
        doc["timestamp"] = sensor_data.timestamp;
        doc["feature_count"] = ml_feature_count;
        
        JsonArray features = doc.createNestedArray("features");
        for (int i = 0; i < min(ml_feature_count, 50); i++) {
            features.add(ml_feature_buffer[i]);
        }
        
        String payload;
        serializeJson(doc, payload);
        
        // Send to Jetson Nano
        Serial3.println(payload);
        
        // Reset feature buffer
        ml_feature_count = 0;
    }
}

void updatePredictions() {
    Serial.println("Updating predictions...");
    
    // Update predictions for each active process
    for (int i = 0; i < 4; i++) {
        if (processes[i].active) {
            updateProcessPrediction(i);
        }
    }
}

void updateProcessPrediction(int process_index) {
    // Simple predictive models - in production, these would be ML models
    
    predictions[process_index].confidence_level = 0.85;
    predictions[process_index].prediction_time = millis();
    predictions[process_index].prediction_valid = true;
    
    switch (process_index) {
        case 0: // CNC Machining
            // Quality prediction based on vibration and temperature
            predictions[process_index].predicted_quality = 100.0 - (sensor_data.vibration_rms * 5.0);
            if (sensor_data.temperatures[0] > 150.0) {
                predictions[process_index].predicted_quality -= 10.0;
            }
            
            // Tool life based on vibration trend
            predictions[process_index].remaining_tool_life = 100.0 - (sensor_data.vibration_rms * 10.0);
            
            // Cycle time prediction
            predictions[process_index].predicted_cycle_time = processes[process_index].target_cycle_time * 
                                                             (100.0 / control_commands.speed_override);
            break;
            
        case 1: // 3D Printing
            // Quality prediction based on temperature stability
            float temp_variation = 0;
            for (int i = 0; i < 4; i++) {
                temp_variation += abs(sensor_data.temperatures[i] - 200.0);
            }
            predictions[process_index].predicted_quality = 100.0 - (temp_variation * 2.0);
            
            // Print time prediction
            predictions[process_index].predicted_cycle_time = processes[process_index].target_cycle_time * 
                                                             (100.0 / control_commands.feed_override);
            break;
            
        case 2: // Injection Molding
            // Quality prediction based on pressure profile
            predictions[process_index].predicted_quality = 100.0;
            if (sensor_data.pressures[0] < 85.0 || sensor_data.pressures[0] > 115.0) {
                predictions[process_index].predicted_quality -= 20.0;
            }
            
            // Defect rate prediction
            predictions[process_index].predicted_defect_rate = (sensor_data.vibration_rms > 1.5) ? 5.0 : 1.0;
            
            break;
            
        case 3: // Assembly
            // Quality prediction based on force feedback
            predictions[process_index].predicted_quality = 100.0;
            if (abs(sensor_data.forces[0]) > 400.0) {
                predictions[process_index].predicted_quality -= 15.0;
            }
            break;
    }
    
    // Constrain predictions
    predictions[process_index].predicted_quality = constrain(predictions[process_index].predicted_quality, 0.0, 100.0);
    predictions[process_index].remaining_tool_life = constrain(predictions[process_index].remaining_tool_life, 0.0, 1000.0);
    predictions[process_index].predicted_cycle_time = constrain(predictions[process_index].predicted_cycle_time, 10.0, 7200.0);
    
    // Maintenance probability based on multiple factors
    float maintenance_score = 0;
    if (sensor_data.vibration_rms > 3.0) maintenance_score += 0.3;
    if (sensor_data.power_active > 40.0) maintenance_score += 0.2;
    if (predictions[process_index].remaining_tool_life < 50.0) maintenance_score += 0.4;
    predictions[process_index].maintenance_probability = constrain(maintenance_score, 0.0, 1.0);
    
    // Energy forecast for next cycle
    predictions[process_index].energy_forecast = sensor_data.power_active * 
                                               (predictions[process_index].predicted_cycle_time / 3600.0);
}

void runEdgeMLInference() {
    // Run machine learning inference at the edge for low-latency predictions
    if (ml_feature_count >= 10) {
        Serial.println("Running edge ML inference...");
        
        // Simple anomaly detection model (would be replaced with trained model)
        float anomaly_score = 0;
        
        // Check for vibration anomalies
        if (sensor_data.vibration_rms > 4.0) anomaly_score += 0.4;
        if (sensor_data.vibration_peak > 8.0) anomaly_score += 0.3;
        
        // Check for temperature anomalies
        float temp_std = 0;
        float temp_avg = 0;
        for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
            temp_avg += sensor_data.temperatures[i];
        }
        temp_avg /= TEMP_SENSOR_COUNT;
        
        for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
            temp_std += pow(sensor_data.temperatures[i] - temp_avg, 2);
        }
        temp_std = sqrt(temp_std / TEMP_SENSOR_COUNT);
        
        if (temp_std > 10.0) anomaly_score += 0.2;
        
        // Check for power anomalies
        if (sensor_data.power_active > 45.0) anomaly_score += 0.1;
        
        // Generate alert if anomaly detected
        if (anomaly_score > 0.5) {
            publishAlert("ANOMALY_DETECTED", "Edge ML detected anomaly - score: " + String(anomaly_score));
        }
        
        // Quality prediction model (simplified)
        float predicted_quality = 100.0 - (anomaly_score * 50.0);
        predicted_quality = constrain(predicted_quality, 0.0, 100.0);
        
        // Store prediction
        for (int i = 0; i < 4; i++) {
            if (processes[i].active) {
                predictions[i].predicted_quality = predicted_quality;
                predictions[i].confidence_level = 1.0 - anomaly_score;
            }
        }
    }
}

void publishSensorData() {
    // Publish sensor data to MQTT broker
    DynamicJsonDocument doc(2048);
    
    doc["timestamp"] = sensor_data.timestamp;
    doc["device_id"] = DEVICE_ID;
    doc["data_quality"] = sensor_data.data_quality;
    doc["sync_latency"] = dt_sync.sync_latency;
    
    // Key sensor values
    doc["temp_avg"] = (sensor_data.temperatures[0] + sensor_data.temperatures[1]) / 2.0;
    doc["pressure_main"] = sensor_data.pressures[0];
    doc["vibration_rms"] = sensor_data.vibration_rms;
    doc["power_active"] = sensor_data.power_active;
    doc["ambient_temp"] = sensor_data.ambient_temperature;
    doc["ambient_humidity"] = sensor_data.ambient_humidity;
    
    // Process states
    JsonArray processes_array = doc.createNestedArray("processes");
    for (int i = 0; i < 4; i++) {
        JsonObject proc = processes_array.createNestedObject();
        proc["id"] = processes[i].process_id;
        proc["active"] = processes[i].active;
        proc["efficiency"] = processes[i].efficiency;
        proc["quality"] = processes[i].quality_score;
    }
    
    // Predictions
    JsonArray predictions_array = doc.createNestedArray("predictions");
    for (int i = 0; i < 4; i++) {
        if (predictions[i].prediction_valid) {
            JsonObject pred = predictions_array.createNestedObject();
            pred["process"] = i;
            pred["quality"] = predictions[i].predicted_quality;
            pred["cycle_time"] = predictions[i].predicted_cycle_time;
            pred["maintenance_prob"] = predictions[i].maintenance_probability;
            pred["confidence"] = predictions[i].confidence_level;
        }
    }
    
    String payload;
    serializeJson(doc, payload);
    
    // Publish to different topics
    mqttClient.publish("digitaltwin/sensors/realtime", payload.c_str());
    mqttClient.publish("digitaltwin/sync/status", String(dt_sync.sync_latency).c_str());
    
    // Calculate transmission rate
    dt_sync.data_transmission_rate = payload.length() * 10.0 / 1024.0; // KB/s at 10Hz
}

void publishAlert(String alert_type, String message) {
    DynamicJsonDocument doc(512);
    doc["timestamp"] = millis();
    doc["device_id"] = DEVICE_ID;
    doc["alert_type"] = alert_type;
    doc["message"] = message;
    doc["severity"] = (alert_type.indexOf("HIGH") >= 0 || alert_type.indexOf("ANOMALY") >= 0) ? "CRITICAL" : "WARNING";
    
    String payload;
    serializeJson(doc, payload);
    
    mqttClient.publish("digitaltwin/alerts", payload.c_str());
    
    Serial.println("ALERT: " + alert_type + " - " + message);
}

void processSerialCommands() {
    // Process commands from connected devices
    
    // Commands from Raspberry Pi
    if (Serial1.available()) {
        String command = Serial1.readStringUntil('\n');
        processRaspberryPiCommand(command);
    }
    
    // Commands from ESP32
    if (Serial2.available()) {
        String command = Serial2.readStringUntil('\n');
        processESP32Command(command);
    }
    
    // Commands from Jetson Nano
    if (Serial3.available()) {
        String command = Serial3.readStringUntil('\n');
        processJetsonCommand(command);
    }
}

void processRaspberryPiCommand(String command) {
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, command);
    
    if (!error) {
        String cmd_type = doc["command"];
        
        if (cmd_type == "update_model") {
            // Update physics model parameters
            float model_accuracy = doc["accuracy"];
            dt_sync.model_accuracy = model_accuracy;
            Serial.println("Physics model updated - accuracy: " + String(model_accuracy));
            
        } else if (cmd_type == "control_update") {
            // Receive optimized control parameters
            if (doc.containsKey("speed_override")) {
                control_commands.speed_override = doc["speed_override"];
            }
            if (doc.containsKey("feed_override")) {
                control_commands.feed_override = doc["feed_override"];
            }
            Serial.println("Control parameters updated from physics simulation");
            
        } else if (cmd_type == "process_start") {
            // Start a manufacturing process
            String process_type = doc["process_type"];
            startProcess(process_type);
            
        } else if (cmd_type == "emergency_stop") {
            // Emergency stop from digital twin
            handleEmergencyStop();
        }
    }
}

void processESP32Command(String command) {
    DynamicJsonDocument doc(512);
    DeserializationError error = deserializeJson(doc, command);
    
    if (!error) {
        String cmd_type = doc["command"];
        
        if (cmd_type == "cloud_status") {
            // Cloud connectivity status
            bool cloud_connected = doc["connected"];
            dt_sync.sync_enabled = cloud_connected;
            
        } else if (cmd_type == "prediction_result") {
            // Prediction results from cloud ML
            int process_id = doc["process_id"];
            float predicted_quality = doc["quality"];
            float confidence = doc["confidence"];
            
            if (process_id >= 0 && process_id < 4) {
                predictions[process_id].predicted_quality = predicted_quality;
                predictions[process_id].confidence_level = confidence;
            }
        }
    }
}

void processJetsonCommand(String command) {
    DynamicJsonDocument doc(512);
    DeserializationError error = deserializeJson(doc, command);
    
    if (!error) {
        String cmd_type = doc["command"];
        
        if (cmd_type == "ai_inference_result") {
            // AI inference results
            float anomaly_score = doc["anomaly_score"];
            float quality_prediction = doc["quality_prediction"];
            float maintenance_prediction = doc["maintenance_prediction"];
            
            // Update predictions for active processes
            for (int i = 0; i < 4; i++) {
                if (processes[i].active) {
                    predictions[i].predicted_quality = quality_prediction;
                    predictions[i].maintenance_probability = maintenance_prediction;
                }
            }
            
            // Check for anomalies
            if (anomaly_score > 0.7) {
                publishAlert("AI_ANOMALY", "AI detected high anomaly score: " + String(anomaly_score));
            }
            
        } else if (cmd_type == "optimization_result") {
            // Process optimization results
            JsonArray params = doc["optimized_parameters"];
            if (params.size() >= 2) {
                control_commands.speed_override = params[0];
                control_commands.feed_override = params[1];
                Serial.println("Process parameters optimized by AI");
            }
        }
    }
}

void startProcess(String process_type) {
    // Find available process slot
    int slot = -1;
    for (int i = 0; i < 4; i++) {
        if (!processes[i].active && strcmp(processes[i].process_type, process_type.c_str()) == 0) {
            slot = i;
            break;
        }
    }
    
    if (slot >= 0) {
        processes[slot].active = true;
        processes[slot].start_time = millis();
        processes[slot].cycle_time = 0.0;
        processes[slot].efficiency = 100.0;
        processes[slot].quality_score = 100.0;
        
        Serial.println("Started process: " + process_type + " in slot " + String(slot));
        
        // Publish process start event
        DynamicJsonDocument doc(512);
        doc["event"] = "process_started";
        doc["process_id"] = processes[slot].process_id;
        doc["process_type"] = process_type;
        doc["timestamp"] = millis();
        
        String payload;
        serializeJson(doc, payload);
        mqttClient.publish("digitaltwin/events/process_started", payload.c_str());
    } else {
        Serial.println("No available slot for process: " + process_type);
    }
}

void processBidirectionalControl() {
    // Implement bi-directional control between physical and digital systems
    
    // Apply speed/feed overrides from digital twin optimization
    applyControlOverrides();
    
    // Send physical system feedback to digital twin
    sendPhysicalFeedback();
    
    // Handle predictive control actions
    handlePredictiveControl();
}

void applyControlOverrides() {
    // Apply control overrides from digital twin
    static float last_speed_override = 100.0;
    static float last_feed_override = 100.0;
    
    if (abs(control_commands.speed_override - last_speed_override) > 5.0) {
        // Speed override changed significantly
        Serial.println("Applying speed override: " + String(control_commands.speed_override) + "%");
        // In real implementation, this would control actual servo drives
        last_speed_override = control_commands.speed_override;
    }
    
    if (abs(control_commands.feed_override - last_feed_override) > 5.0) {
        // Feed override changed significantly
        Serial.println("Applying feed override: " + String(control_commands.feed_override) + "%");
        // In real implementation, this would control feed rates
        last_feed_override = control_commands.feed_override;
    }
    
    // Handle emergency conditions
    if (control_commands.emergency_stop) {
        handleEmergencyStop();
        control_commands.emergency_stop = false;
    }
    
    if (control_commands.quality_hold) {
        // Pause process for quality issue
        Serial.println("Quality hold activated - pausing processes");
        for (int i = 0; i < 4; i++) {
            if (processes[i].active) {
                // Pause process (in real implementation, stop feeds/spindles)
            }
        }
        control_commands.quality_hold = false;
    }
}

void sendPhysicalFeedback() {
    // Send physical system performance back to digital twin for model calibration
    DynamicJsonDocument doc(1024);
    
    doc["timestamp"] = millis();
    doc["feedback_type"] = "physical_performance";
    
    // Actual vs predicted performance
    for (int i = 0; i < 4; i++) {
        if (processes[i].active && predictions[i].prediction_valid) {
            JsonObject feedback = doc.createNestedObject("process_" + String(i));
            feedback["actual_quality"] = processes[i].quality_score;
            feedback["predicted_quality"] = predictions[i].predicted_quality;
            feedback["actual_cycle_time"] = processes[i].cycle_time;
            feedback["predicted_cycle_time"] = predictions[i].predicted_cycle_time;
            feedback["prediction_error"] = abs(processes[i].quality_score - predictions[i].predicted_quality);
        }
    }
    
    // Energy consumption feedback
    doc["actual_power"] = sensor_data.power_active;
    doc["energy_consumed"] = sensor_data.energy_consumed;
    
    String payload;
    serializeJson(doc, payload);
    
    // Send to Raspberry Pi for model calibration
    Serial1.println(payload);
}

void handlePredictiveControl() {
    // Implement predictive control based on digital twin predictions
    
    for (int i = 0; i < 4; i++) {
        if (processes[i].active && predictions[i].prediction_valid) {
            
            // Predictive quality control
            if (predictions[i].predicted_quality < 80.0 && predictions[i].confidence_level > 0.7) {
                Serial.println("Predictive quality alert for process " + String(i) + 
                             " - predicted quality: " + String(predictions[i].predicted_quality) + "%");
                
                // Adjust parameters to improve quality
                if (i == 0) { // CNC process
                    control_commands.speed_override = max(50.0, control_commands.speed_override - 10.0);
                } else if (i == 1) { // 3D printing
                    control_commands.feed_override = max(50.0, control_commands.feed_override - 5.0);
                }
            }
            
            // Predictive maintenance
            if (predictions[i].maintenance_probability > 0.8) {
                publishAlert("PREDICTIVE_MAINTENANCE", 
                           "Process " + String(i) + " requires maintenance - probability: " + 
                           String(predictions[i].maintenance_probability * 100) + "%");
                
                // Schedule maintenance after current cycle
                // In real implementation, this would interface with CMMS
            }
            
            // Energy optimization
            if (predictions[i].energy_forecast > 50.0) { // High energy consumption predicted
                Serial.println("High energy consumption predicted for process " + String(i) + 
                             " - optimizing parameters");
                
                // Reduce energy consumption by slightly reducing speeds
                control_commands.speed_override = max(80.0, control_commands.speed_override - 5.0);
            }
        }
    }
}

void handleEmergencyStop() {
    Serial.println("EMERGENCY STOP ACTIVATED");
    
    // Stop all processes immediately
    for (int i = 0; i < 4; i++) {
        processes[i].active = false;
    }
    
    // Turn off all outputs (in real implementation)
    digitalWrite(PROCESS_ACTIVE_LED, LOW);
    digitalWrite(ERROR_LED, HIGH);
    
    // Publish emergency stop event
    publishAlert("EMERGENCY_STOP", "Emergency stop activated - all processes stopped");
    
    // Reset control commands
    control_commands.speed_override = 0.0;
    control_commands.feed_override = 0.0;
    control_commands.emergency_stop = false;
    
    // Wait for manual reset
    while (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        delay(100);
        digitalWrite(ERROR_LED, !digitalRead(ERROR_LED)); // Blink error LED
    }
    
    // Reset system
    Serial.println("Emergency stop cleared - system ready");
    digitalWrite(ERROR_LED, LOW);
    control_commands.speed_override = 100.0;
    control_commands.feed_override = 100.0;
}

void performSystemHealthCheck() {
    static int health_check_count = 0;
    health_check_count++;
    
    // Check sensor health
    int healthy_sensors = 0;
    int total_sensors = TEMP_SENSOR_COUNT + PRESSURE_SENSOR_COUNT + VIBRATION_SENSOR_COUNT + 2; // +2 for ambient
    
    // Temperature sensors
    for (int i = 0; i < TEMP_SENSOR_COUNT; i++) {
        if (sensor_data.temperatures[i] > -200 && sensor_data.temperatures[i] < 500) {
            healthy_sensors++;
        }
    }
    
    // Pressure sensors
    for (int i = 0; i < PRESSURE_SENSOR_COUNT; i++) {
        if (sensor_data.pressures[i] >= 0 && sensor_data.pressures[i] < 1000) {
            healthy_sensors++;
        }
    }
    
    // Vibration sensors
    for (int i = 0; i < VIBRATION_SENSOR_COUNT; i++) {
        if (abs(sensor_data.accelerations[i]) < 50) {
            healthy_sensors++;
        }
    }
    
    // Ambient sensors
    if (!isnan(sensor_data.ambient_temperature)) healthy_sensors++;
    if (!isnan(sensor_data.ambient_humidity)) healthy_sensors++;
    
    float sensor_health = (float)healthy_sensors / total_sensors * 100.0;
    
    // Check communication health
    bool comm_health = mqttClient.connected() && 
                      (millis() - dt_sync.last_sync < 5000);
    
    // Check sync performance
    bool sync_performance = dt_sync.sync_latency < 100.0;
    
    // Overall system health
    float system_health = sensor_health * 0.5 + 
                         (comm_health ? 25.0 : 0.0) + 
                         (sync_performance ? 25.0 : 0.0);
    
    // Report health every 10 checks (10 seconds)
    if (health_check_count % 10 == 0) {
        Serial.print("System Health: ");
        Serial.print(system_health);
        Serial.print("% - Sensors: ");
        Serial.print(sensor_health);
        Serial.print("%, Comm: ");
        Serial.print(comm_health ? "OK" : "FAIL");
        Serial.print(", Sync: ");
        Serial.print(sync_performance ? "OK" : "SLOW");
        Serial.print(" (");
        Serial.print(dt_sync.sync_latency);
        Serial.println("ms)");
        
        // Publish health status
        DynamicJsonDocument doc(512);
        doc["timestamp"] = millis();
        doc["device_id"] = DEVICE_ID;
        doc["system_health"] = system_health;
        doc["sensor_health"] = sensor_health;
        doc["communication_health"] = comm_health;
        doc["sync_latency"] = dt_sync.sync_latency;
        doc["uptime"] = millis() / 1000;
        
        String payload;
        serializeJson(doc, payload);
        mqttClient.publish("digitaltwin/health", payload.c_str());
    }
    
    // Alert if health is poor
    if (system_health < 70.0) {
        publishAlert("SYSTEM_HEALTH", "System health degraded: " + String(system_health) + "%");
    }
}

void updateSystemStatus() {
    // Update system status LEDs
    
    // Data activity LED (toggles during data acquisition)
    // Already handled in main loop
    
    // System ready LED
    bool system_ready = sensor_data.data_quality > 0.8 && 
                       mqttClient.connected() && 
                       dt_sync.sync_latency < 100.0;
    digitalWrite(SYSTEM_READY_LED, system_ready);
    
    // Error LED
    bool system_error = sensor_data.data_quality < 0.5 || 
                       !mqttClient.connected() || 
                       dt_sync.sync_latency > 200.0;
    digitalWrite(ERROR_LED, system_error);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // Handle incoming MQTT commands
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';
    
    Serial.print("MQTT message received on topic: ");
    Serial.print(topic);
    Serial.print(" - ");
    Serial.println(message);
    
    DynamicJsonDocument doc(1024);
    DeserializationError error = deserializeJson(doc, message);
    
    if (!error) {
        String topic_str = String(topic);
        
        if (topic_str.endsWith("/command")) {
            String command = doc["command"];
            
            if (command == "start_process") {
                String process_type = doc["process_type"];
                startProcess(process_type);
                
            } else if (command == "stop_process") {
                String process_id = doc["process_id"];
                // Find and stop process
                for (int i = 0; i < 4; i++) {
                    if (strcmp(processes[i].process_id, process_id.c_str()) == 0) {
                        processes[i].active = false;
                        Serial.println("Stopped process: " + process_id);
                        break;
                    }
                }
                
            } else if (command == "emergency_stop") {
                handleEmergencyStop();
                
            } else if (command == "set_overrides") {
                if (doc.containsKey("speed")) control_commands.speed_override = doc["speed"];
                if (doc.containsKey("feed")) control_commands.feed_override = doc["feed"];
                
            } else if (command == "enable_predictive") {
                control_commands.predictive_mode_enabled = doc["enabled"];
                
            } else if (command == "calibrate_sensors") {
                // Trigger sensor calibration
                Serial.println("Sensor calibration requested");
                // In real implementation, run calibration routines
            }
        }
    }
}

void reconnectMQTT() {
    while (!mqttClient.connected()) {
        Serial.print("Attempting MQTT connection...");
        
        if (mqttClient.connect(DEVICE_ID)) {
            Serial.println("connected");
            
            // Subscribe to command topics
            mqttClient.subscribe("digitaltwin/command");
            mqttClient.subscribe("digitaltwin/sensors/command");
            mqttClient.subscribe("digitaltwin/processes/command");
            
            // Publish connection status
            publishAlert("SYSTEM_ONLINE", "Digital Twin Sensor Hub connected");
            
        } else {
            Serial.print("failed, rc=");
            Serial.print(mqttClient.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}