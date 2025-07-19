/*
 * ESP32 Signal Processor and IoT Gateway for Welding Quality Monitor
 * 
 * This code runs on ESP32 to handle advanced signal processing, FFT analysis,
 * machine learning inference, and IoT connectivity for the welding monitoring system.
 * 
 * Features:
 * - High-speed signal processing and FFT analysis
 * - TensorFlow Lite inference for weld quality prediction
 * - Advanced acoustic analysis for defect detection
 * - Real-time web dashboard and API
 * - MQTT communication with cloud services
 * - OTA updates and remote configuration
 * 
 * Author: Arduino Zero to Hero v2.0
 * Version: 1.0
 * Date: 2024
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <SPIFFS.h>
#include <Update.h>
#include <ESPAsyncWebServer.h>
#include <AsyncTCP.h>
#include <TensorFlowLite_ESP32.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_error_reporter.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>
#include <tensorflow/lite/version.h>
#include <arduinoFFT.h>
#include <driver/adc.h>
#include <driver/i2s.h>

// Pin Definitions
#define UART_RX_PIN 16
#define UART_TX_PIN 17
#define AUDIO_INPUT_PIN 35
#define CURRENT_ADC_PIN 34
#define VOLTAGE_ADC_PIN 36
#define STATUS_LED_PIN 2
#define BUZZER_PIN 4
#define USER_BUTTON_PIN 0

// Signal Processing Constants
#define FFT_SAMPLES 1024
#define SAMPLING_FREQUENCY 44100
#define ELECTRICAL_SAMPLING_FREQ 10000
#define BUFFER_SIZE 4096
#define SPECTROGRAM_BANDS 64

// Network Configuration
const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "your-mqtt-broker.com";
const int mqtt_port = 1883;

// Web Server and Communication
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");
WiFiClient espClient;
PubSubClient mqtt(espClient);

// TensorFlow Lite Variables
constexpr int kTensorArenaSize = 80 * 1024;
uint8_t tensor_arena[kTensorArenaSize];
tflite::MicroErrorReporter micro_error_reporter;
tflite::AllOpsResolver resolver;
const tflite::Model* weld_quality_model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* input_tensor = nullptr;
TfLiteTensor* output_tensor = nullptr;

// FFT Variables
arduinoFFT FFT = arduinoFFT();
double vReal[FFT_SAMPLES];
double vImag[FFT_SAMPLES];
float spectrogram[SPECTROGRAM_BANDS];
float frequency_bins[FFT_SAMPLES/2];

// Data Structures
struct ElectricalData {
  float current;
  float voltage;
  float power;
  float rms_current;
  float rms_voltage;
  float power_factor;
  float thd_current;      // Total Harmonic Distortion
  float thd_voltage;
  float frequency;
  uint32_t timestamp;
};

struct AcousticData {
  float rms_level;
  float peak_frequency;
  float spectral_centroid;
  float spectral_rolloff;
  float zero_crossing_rate;
  float mfcc[13];         // Mel-frequency cepstral coefficients
  float spatter_index;
  float porosity_index;
  float crack_indicator;
  uint32_t timestamp;
};

struct WeldSignature {
  float arc_signature[256];      // Arc electrical signature
  float acoustic_signature[256]; // Acoustic fingerprint
  float quality_features[32];    // Extracted quality features
  String process_type;           // MIG, TIG, Stick, etc.
  float confidence;
  uint32_t analysis_time;
};

struct QualityPrediction {
  float overall_quality;
  float tensile_strength;
  float penetration_depth;
  float bead_width;
  String defect_type;
  float defect_probability;
  float confidence;
  uint32_t prediction_time;
};

struct SystemMetrics {
  float cpu_usage;
  float memory_usage;
  float signal_quality;
  uint32_t processed_samples;
  uint32_t fft_calculations;
  uint32_t ml_predictions;
  float prediction_accuracy;
};

// Global Variables
ElectricalData electrical_data;
AcousticData acoustic_data;
WeldSignature weld_signature;
QualityPrediction quality_prediction;
SystemMetrics system_metrics;

// Signal Processing Buffers
float audio_buffer[BUFFER_SIZE];
float current_buffer[BUFFER_SIZE];
float voltage_buffer[BUFFER_SIZE];
int audio_buffer_index = 0;
int electrical_buffer_index = 0;

// Timing Variables
unsigned long last_fft_time = 0;
unsigned long last_ml_prediction = 0;
unsigned long last_data_transmission = 0;
unsigned long last_metrics_update = 0;

// Machine Learning Models
bool ml_model_loaded = false;
float feature_scaler_mean[32];
float feature_scaler_std[32];

// Communication Buffers
const int PREDICTION_HISTORY_SIZE = 100;
QualityPrediction prediction_history[PREDICTION_HISTORY_SIZE];
int prediction_history_index = 0;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, UART_RX_PIN, UART_TX_PIN);
  
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(USER_BUTTON_PIN, INPUT_PULLUP);
  
  Serial.println("ESP32 Welding Signal Processor v1.0");
  Serial.println("Initializing...");
  
  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS initialization failed");
    return;
  }
  
  // Initialize ADC for high-speed sampling
  initializeADC();
  
  // Initialize I2S for audio processing
  initializeI2S();
  
  // Initialize WiFi
  initializeWiFi();
  
  // Initialize MQTT
  initializeMQTT();
  
  // Initialize web server
  initializeWebServer();
  
  // Load ML models
  loadMLModels();
  
  // Initialize signal processing
  initializeSignalProcessing();
  
  // Initialize system metrics
  initializeMetrics();
  
  Serial.println("ESP32 initialization complete!");
  digitalWrite(STATUS_LED_PIN, HIGH);
}

void loop() {
  unsigned long current_time = millis();
  
  // Handle WiFi reconnection
  if (WiFi.status() != WL_CONNECTED) {
    reconnectWiFi();
  }
  
  // Handle MQTT
  if (!mqtt.connected()) {
    reconnectMQTT();
  }
  mqtt.loop();
  
  // Process incoming data from Arduino
  processArduinoData();
  
  // High-speed signal processing
  processElectricalSignals();
  processAcousticSignals();
  
  // Perform FFT analysis
  if (current_time - last_fft_time >= 23) { // ~44 Hz for audio FFT
    performFFTAnalysis();
    last_fft_time = current_time;
  }
  
  // Machine learning inference
  if (current_time - last_ml_prediction >= 1000 && ml_model_loaded) {
    performMLInference();
    last_ml_prediction = current_time;
  }
  
  // Update system metrics
  if (current_time - last_metrics_update >= 5000) {
    updateSystemMetrics();
    last_metrics_update = current_time;
  }
  
  // Transmit data
  if (current_time - last_data_transmission >= 500) {
    transmitData();
    last_data_transmission = current_time;
  }
  
  // Handle user input
  handleUserButton();
  
  // Cleanup WebSocket connections
  ws.cleanupClients();
  
  delay(1);
}

void initializeADC() {
  // Configure ADC for high-speed electrical signal sampling
  adc1_config_width(ADC_WIDTH_BIT_12);
  adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11); // GPIO34 - Current
  adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_11); // GPIO36 - Voltage
  
  Serial.println("ADC initialized for high-speed sampling");
}

void initializeI2S() {
  // Configure I2S for high-quality audio capture
  i2s_config_t i2s_config = {
    .mode = i2s_mode_t(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN),
    .sample_rate = SAMPLING_FREQUENCY,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S_MSB,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_adc_mode(ADC_UNIT_1, ADC1_CHANNEL_7); // GPIO35 - Audio
  i2s_adc_enable(I2S_NUM_0);
  
  Serial.println("I2S initialized for audio processing");
}

void initializeWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to WiFi");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 50) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.print("WiFi connected! IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("WiFi connection failed!");
  }
}

void initializeMQTT() {
  mqtt.setServer(mqtt_server, mqtt_port);
  mqtt.setCallback(mqttCallback);
  
  if (mqtt.connect("ESP32_WeldMonitor")) {
    Serial.println("MQTT connected");
    mqtt.subscribe("weld/commands");
    mqtt.subscribe("weld/config");
    mqtt.subscribe("weld/models");
  } else {
    Serial.println("MQTT connection failed");
  }
}

void initializeWebServer() {
  // WebSocket handler
  ws.onEvent(onWebSocketEvent);
  server.addHandler(&ws);
  
  // Serve static files
  server.serveStatic("/", SPIFFS, "/").setDefaultFile("index.html");
  
  // REST API endpoints
  server.on("/api/status", HTTP_GET, [](AsyncWebServerRequest *request) {
    DynamicJsonDocument doc(4096);
    
    doc["electrical"]["current"] = electrical_data.current;
    doc["electrical"]["voltage"] = electrical_data.voltage;
    doc["electrical"]["power"] = electrical_data.power;
    doc["electrical"]["power_factor"] = electrical_data.power_factor;
    doc["electrical"]["thd_current"] = electrical_data.thd_current;
    
    doc["acoustic"]["rms_level"] = acoustic_data.rms_level;
    doc["acoustic"]["peak_frequency"] = acoustic_data.peak_frequency;
    doc["acoustic"]["spatter_index"] = acoustic_data.spatter_index;
    doc["acoustic"]["porosity_index"] = acoustic_data.porosity_index;
    
    doc["quality"]["overall_score"] = quality_prediction.overall_quality;
    doc["quality"]["defect_type"] = quality_prediction.defect_type;
    doc["quality"]["defect_probability"] = quality_prediction.defect_probability;
    doc["quality"]["confidence"] = quality_prediction.confidence;
    
    doc["system"]["cpu_usage"] = system_metrics.cpu_usage;
    doc["system"]["memory_usage"] = system_metrics.memory_usage;
    doc["system"]["signal_quality"] = system_metrics.signal_quality;
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  server.on("/api/spectrum", HTTP_GET, [](AsyncWebServerRequest *request) {
    DynamicJsonDocument doc(8192);
    JsonArray spectrum = doc.createNestedArray("frequency_spectrum");
    
    for (int i = 0; i < SPECTROGRAM_BANDS; i++) {
      spectrum.add(spectrogram[i]);
    }
    
    doc["sample_rate"] = SAMPLING_FREQUENCY;
    doc["fft_size"] = FFT_SAMPLES;
    doc["timestamp"] = millis();
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  server.on("/api/weld_signature", HTTP_GET, [](AsyncWebServerRequest *request) {
    DynamicJsonDocument doc(8192);
    
    JsonArray arc_sig = doc.createNestedArray("arc_signature");
    for (int i = 0; i < 256; i++) {
      arc_sig.add(weld_signature.arc_signature[i]);
    }
    
    JsonArray acoustic_sig = doc.createNestedArray("acoustic_signature");
    for (int i = 0; i < 256; i++) {
      acoustic_sig.add(weld_signature.acoustic_signature[i]);
    }
    
    doc["process_type"] = weld_signature.process_type;
    doc["confidence"] = weld_signature.confidence;
    doc["analysis_time"] = weld_signature.analysis_time;
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  server.on("/api/prediction_history", HTTP_GET, [](AsyncWebServerRequest *request) {
    DynamicJsonDocument doc(8192);
    JsonArray predictions = doc.createNestedArray("predictions");
    
    for (int i = 0; i < PREDICTION_HISTORY_SIZE; i++) {
      int index = (prediction_history_index + i) % PREDICTION_HISTORY_SIZE;
      if (prediction_history[index].prediction_time > 0) {
        JsonObject pred = predictions.createNestedObject();
        pred["timestamp"] = prediction_history[index].prediction_time;
        pred["quality"] = prediction_history[index].overall_quality;
        pred["defect_type"] = prediction_history[index].defect_type;
        pred["defect_probability"] = prediction_history[index].defect_probability;
        pred["confidence"] = prediction_history[index].confidence;
      }
    }
    
    String response;
    serializeJson(doc, response);
    request->send(200, "application/json", response);
  });
  
  // Configuration endpoints
  server.on("/api/config", HTTP_POST, [](AsyncWebServerRequest *request) {
    // Handle configuration updates
    request->send(200, "application/json", "{\"status\":\"success\"}");
  });
  
  server.begin();
  Serial.println("Web server started");
}

void loadMLModels() {
  // Load TensorFlow Lite model for weld quality prediction
  File model_file = SPIFFS.open("/weld_quality_model.tflite", "r");
  if (!model_file) {
    Serial.println("Failed to open ML model file");
    return;
  }
  
  size_t model_size = model_file.size();
  uint8_t* model_data = (uint8_t*)malloc(model_size);
  model_file.readBytes((char*)model_data, model_size);
  model_file.close();
  
  // Load the model
  weld_quality_model = tflite::GetModel(model_data);
  if (weld_quality_model->version() != TFLITE_SCHEMA_VERSION) {
    Serial.println("Model schema version mismatch");
    free(model_data);
    return;
  }
  
  // Create interpreter
  static tflite::MicroInterpreter static_interpreter(
    weld_quality_model, resolver, tensor_arena, kTensorArenaSize, &micro_error_reporter);
  interpreter = &static_interpreter;
  
  // Allocate tensors
  TfLiteStatus allocate_status = interpreter->AllocateTensors();
  if (allocate_status != kTfLiteOk) {
    Serial.println("Failed to allocate tensors");
    free(model_data);
    return;
  }
  
  // Get input and output tensors
  input_tensor = interpreter->input(0);
  output_tensor = interpreter->output(0);
  
  // Load feature scaling parameters
  loadFeatureScaling();
  
  ml_model_loaded = true;
  Serial.println("ML model loaded successfully");
  Serial.printf("Model input shape: [%d, %d]\n", input_tensor->dims->data[0], input_tensor->dims->data[1]);
  Serial.printf("Model output shape: [%d, %d]\n", output_tensor->dims->data[0], output_tensor->dims->data[1]);
}

void initializeSignalProcessing() {
  // Initialize FFT imaginary parts to zero
  for (int i = 0; i < FFT_SAMPLES; i++) {
    vImag[i] = 0.0;
  }
  
  // Initialize buffers
  for (int i = 0; i < BUFFER_SIZE; i++) {
    audio_buffer[i] = 0.0;
    current_buffer[i] = 0.0;
    voltage_buffer[i] = 0.0;
  }
  
  Serial.println("Signal processing initialized");
}

void processElectricalSignals() {
  // Read current and voltage at high speed
  uint16_t current_raw = adc1_get_raw(ADC1_CHANNEL_6);
  uint16_t voltage_raw = adc1_get_raw(ADC1_CHANNEL_0);
  
  // Convert to actual values
  float current = (current_raw / 4095.0) * 3.3 * 151.515; // Scale for current sensor
  float voltage = (voltage_raw / 4095.0) * 3.3 * 20.0;    // Scale for voltage divider
  
  // Add to buffers
  current_buffer[electrical_buffer_index] = current;
  voltage_buffer[electrical_buffer_index] = voltage;
  electrical_buffer_index = (electrical_buffer_index + 1) % BUFFER_SIZE;
  
  // Update electrical data structure
  electrical_data.current = current;
  electrical_data.voltage = voltage;
  electrical_data.power = current * voltage;
  electrical_data.timestamp = millis();
  
  // Calculate RMS values when buffer is full
  if (electrical_buffer_index == 0) {
    calculateElectricalMetrics();
  }
  
  system_metrics.processed_samples++;
}

void processAcousticSignals() {
  // Read audio data via I2S
  size_t bytes_read;
  uint16_t audio_samples[64];
  
  i2s_read(I2S_NUM_0, audio_samples, sizeof(audio_samples), &bytes_read, portMAX_DELAY);
  
  // Process audio samples
  for (int i = 0; i < bytes_read / sizeof(uint16_t); i++) {
    float audio_value = (audio_samples[i] / 32768.0) - 1.0; // Normalize to -1 to 1
    
    audio_buffer[audio_buffer_index] = audio_value;
    audio_buffer_index = (audio_buffer_index + 1) % BUFFER_SIZE;
    
    // Calculate basic metrics
    if (audio_buffer_index % 100 == 0) {
      calculateAcousticMetrics();
    }
  }
}

void performFFTAnalysis() {
  // Copy audio buffer to FFT arrays
  for (int i = 0; i < FFT_SAMPLES; i++) {
    int buffer_idx = (audio_buffer_index - FFT_SAMPLES + i + BUFFER_SIZE) % BUFFER_SIZE;
    vReal[i] = audio_buffer[buffer_idx];
    vImag[i] = 0.0;
  }
  
  // Perform FFT
  FFT.Windowing(vReal, FFT_SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  FFT.Compute(vReal, vImag, FFT_SAMPLES, FFT_FORWARD);
  FFT.ComplexToMagnitude(vReal, vImag, FFT_SAMPLES);
  
  // Calculate spectrogram bands
  calculateSpectrogram();
  
  // Extract acoustic features
  extractAcousticFeatures();
  
  // Update system metrics
  system_metrics.fft_calculations++;
}

void calculateElectricalMetrics() {
  // Calculate RMS current
  float current_sum_sq = 0;
  for (int i = 0; i < BUFFER_SIZE; i++) {
    current_sum_sq += current_buffer[i] * current_buffer[i];
  }
  electrical_data.rms_current = sqrt(current_sum_sq / BUFFER_SIZE);
  
  // Calculate RMS voltage
  float voltage_sum_sq = 0;
  for (int i = 0; i < BUFFER_SIZE; i++) {
    voltage_sum_sq += voltage_buffer[i] * voltage_buffer[i];
  }
  electrical_data.rms_voltage = sqrt(voltage_sum_sq / BUFFER_SIZE);
  
  // Calculate power factor
  electrical_data.power_factor = calculatePowerFactor();
  
  // Calculate Total Harmonic Distortion
  electrical_data.thd_current = calculateTHD(current_buffer);
  electrical_data.thd_voltage = calculateTHD(voltage_buffer);
  
  // Detect fundamental frequency
  electrical_data.frequency = detectFundamentalFrequency(current_buffer);
}

void calculateAcousticMetrics() {
  // Calculate RMS level
  float sum_sq = 0;
  int start_idx = (audio_buffer_index - 1000 + BUFFER_SIZE) % BUFFER_SIZE;
  
  for (int i = 0; i < 1000; i++) {
    int idx = (start_idx + i) % BUFFER_SIZE;
    sum_sq += audio_buffer[idx] * audio_buffer[idx];
  }
  acoustic_data.rms_level = sqrt(sum_sq / 1000.0);
  
  // Calculate zero crossing rate
  acoustic_data.zero_crossing_rate = calculateZeroCrossingRate();
  
  acoustic_data.timestamp = millis();
}

void calculateSpectrogram() {
  // Convert FFT results to frequency bands
  int samples_per_band = (FFT_SAMPLES / 2) / SPECTROGRAM_BANDS;
  
  for (int band = 0; band < SPECTROGRAM_BANDS; band++) {
    float band_sum = 0;
    for (int i = 0; i < samples_per_band; i++) {
      int fft_index = band * samples_per_band + i;
      band_sum += vReal[fft_index];
    }
    spectrogram[band] = band_sum / samples_per_band;
  }
  
  // Find peak frequency
  float max_magnitude = 0;
  int peak_bin = 0;
  for (int i = 1; i < FFT_SAMPLES / 2; i++) {
    if (vReal[i] > max_magnitude) {
      max_magnitude = vReal[i];
      peak_bin = i;
    }
  }
  acoustic_data.peak_frequency = (peak_bin * SAMPLING_FREQUENCY) / FFT_SAMPLES;
}

void extractAcousticFeatures() {
  // Calculate spectral centroid
  float weighted_sum = 0;
  float magnitude_sum = 0;
  
  for (int i = 1; i < FFT_SAMPLES / 2; i++) {
    float frequency = (i * SAMPLING_FREQUENCY) / FFT_SAMPLES;
    weighted_sum += frequency * vReal[i];
    magnitude_sum += vReal[i];
  }
  
  acoustic_data.spectral_centroid = magnitude_sum > 0 ? weighted_sum / magnitude_sum : 0;
  
  // Calculate spectral rolloff (85% of energy)
  float total_energy = magnitude_sum;
  float cumulative_energy = 0;
  acoustic_data.spectral_rolloff = 0;
  
  for (int i = 1; i < FFT_SAMPLES / 2; i++) {
    cumulative_energy += vReal[i];
    if (cumulative_energy >= 0.85 * total_energy) {
      acoustic_data.spectral_rolloff = (i * SAMPLING_FREQUENCY) / FFT_SAMPLES;
      break;
    }
  }
  
  // Calculate MFCC features (simplified)
  calculateMFCC();
  
  // Calculate welding-specific indices
  acoustic_data.spatter_index = calculateSpatterIndex();
  acoustic_data.porosity_index = calculatePorosityIndex();
  acoustic_data.crack_indicator = calculateCrackIndicator();
}

void calculateMFCC() {
  // Simplified MFCC calculation for welding analysis
  // In practice, this would use mel-scale filterbanks
  
  for (int i = 0; i < 13; i++) {
    acoustic_data.mfcc[i] = 0;
    
    // Simple frequency band energy calculation
    int start_bin = i * (FFT_SAMPLES / 26);
    int end_bin = (i + 1) * (FFT_SAMPLES / 26);
    
    for (int j = start_bin; j < end_bin && j < FFT_SAMPLES / 2; j++) {
      acoustic_data.mfcc[i] += vReal[j];
    }
    
    acoustic_data.mfcc[i] = log(acoustic_data.mfcc[i] + 1e-10); // Log energy
  }
}

float calculateSpatterIndex() {
  // Spatter typically shows up in high-frequency components
  float high_freq_energy = 0;
  float total_energy = 0;
  
  for (int i = 1; i < FFT_SAMPLES / 2; i++) {
    float frequency = (i * SAMPLING_FREQUENCY) / FFT_SAMPLES;
    total_energy += vReal[i];
    
    if (frequency > 5000) { // High frequencies above 5kHz
      high_freq_energy += vReal[i];
    }
  }
  
  return total_energy > 0 ? high_freq_energy / total_energy : 0;
}

float calculatePorosityIndex() {
  // Porosity often manifests as mid-frequency irregularities
  float mid_freq_variance = 0;
  float mid_freq_count = 0;
  
  for (int i = 1; i < FFT_SAMPLES / 2; i++) {
    float frequency = (i * SAMPLING_FREQUENCY) / FFT_SAMPLES;
    
    if (frequency > 1000 && frequency < 5000) { // Mid frequencies
      mid_freq_variance += vReal[i] * vReal[i];
      mid_freq_count++;
    }
  }
  
  return mid_freq_count > 0 ? sqrt(mid_freq_variance / mid_freq_count) : 0;
}

float calculateCrackIndicator() {
  // Crack formation creates specific acoustic signatures
  float crack_signature = 0;
  
  // Look for sudden amplitude changes in specific frequency ranges
  for (int i = 2; i < FFT_SAMPLES / 2 - 1; i++) {
    float frequency = (i * SAMPLING_FREQUENCY) / FFT_SAMPLES;
    
    if (frequency > 2000 && frequency < 8000) {
      float gradient = abs(vReal[i+1] - vReal[i-1]);
      crack_signature += gradient;
    }
  }
  
  return crack_signature;
}

void performMLInference() {
  if (!ml_model_loaded || input_tensor == nullptr || output_tensor == nullptr) {
    return;
  }
  
  // Prepare input features
  float features[32];
  extractQualityFeatures(features);
  
  // Normalize features
  for (int i = 0; i < 32; i++) {
    features[i] = (features[i] - feature_scaler_mean[i]) / feature_scaler_std[i];
    input_tensor->data.f[i] = features[i];
  }
  
  // Run inference
  TfLiteStatus invoke_status = interpreter->Invoke();
  if (invoke_status != kTfLiteOk) {
    Serial.println("ML inference failed");
    return;
  }
  
  // Extract results
  quality_prediction.overall_quality = output_tensor->data.f[0];
  quality_prediction.tensile_strength = output_tensor->data.f[1] * 800.0; // Denormalize
  quality_prediction.penetration_depth = output_tensor->data.f[2] * 10.0; // mm
  quality_prediction.bead_width = output_tensor->data.f[3] * 15.0; // mm
  quality_prediction.defect_probability = 1.0 - quality_prediction.overall_quality;
  
  // Determine defect type
  quality_prediction.defect_type = classifyDefectType(features);
  
  // Calculate confidence
  quality_prediction.confidence = calculatePredictionConfidence(features);
  quality_prediction.prediction_time = millis();
  
  // Store in history
  prediction_history[prediction_history_index] = quality_prediction;
  prediction_history_index = (prediction_history_index + 1) % PREDICTION_HISTORY_SIZE;
  
  // Update metrics
  system_metrics.ml_predictions++;
  
  // Send alert if quality is poor
  if (quality_prediction.overall_quality < 0.6) {
    sendQualityAlert();
  }
  
  Serial.printf("ML Prediction: Quality=%.2f, Defect=%.2f, Type=%s\n",
    quality_prediction.overall_quality,
    quality_prediction.defect_probability,
    quality_prediction.defect_type.c_str());
}

void extractQualityFeatures(float* features) {
  // Electrical features
  features[0] = electrical_data.current / 500.0;           // Normalized current
  features[1] = electrical_data.voltage / 50.0;           // Normalized voltage
  features[2] = electrical_data.power / 25000.0;          // Normalized power
  features[3] = electrical_data.rms_current / 500.0;      // RMS current
  features[4] = electrical_data.rms_voltage / 50.0;       // RMS voltage
  features[5] = electrical_data.power_factor;             // Power factor
  features[6] = electrical_data.thd_current;              // Current THD
  features[7] = electrical_data.thd_voltage;              // Voltage THD
  features[8] = electrical_data.frequency / 100.0;        // Frequency
  
  // Acoustic features
  features[9] = acoustic_data.rms_level;                  // Audio RMS
  features[10] = acoustic_data.peak_frequency / 22050.0;  // Peak frequency
  features[11] = acoustic_data.spectral_centroid / 22050.0; // Spectral centroid
  features[12] = acoustic_data.spectral_rolloff / 22050.0;  // Spectral rolloff
  features[13] = acoustic_data.zero_crossing_rate;        // ZCR
  features[14] = acoustic_data.spatter_index;             // Spatter index
  features[15] = acoustic_data.porosity_index;            // Porosity index
  features[16] = acoustic_data.crack_indicator / 1000.0;  // Crack indicator
  
  // MFCC features (first 12)
  for (int i = 0; i < 12; i++) {
    features[17 + i] = acoustic_data.mfcc[i];
  }
  
  // Spectrogram energy in key bands
  features[29] = spectrogram[8];   // Low frequency energy
  features[30] = spectrogram[32];  // Mid frequency energy
  features[31] = spectrogram[56];  // High frequency energy
}

String classifyDefectType(float* features) {
  // Rule-based defect classification
  if (features[15] > 0.5) return "Porosity";
  if (features[14] > 0.6) return "Excessive_Spatter";
  if (features[16] > 0.4) return "Crack_Formation";
  if (features[2] > 0.9) return "Burn_Through";
  if (features[2] < 0.1) return "Lack_of_Penetration";
  if (features[5] < 0.7) return "Poor_Arc_Stability";
  if (features[6] > 0.2) return "Arc_Instability";
  
  return "None";
}

void processArduinoData() {
  if (Serial2.available()) {
    String data = Serial2.readStringUntil('\n');
    data.trim();
    
    if (data.startsWith("{") && data.endsWith("}")) {
      // Parse JSON data from Arduino
      DynamicJsonDocument doc(2048);
      DeserializationError error = deserializeJson(doc, data);
      
      if (!error) {
        // Update local data structures with Arduino data
        // This would include mechanical parameters, thermal data, etc.
        handleArduinoData(doc);
      }
    }
  }
}

void transmitData() {
  // Send data to WebSocket clients
  sendDataToWebSocketClients();
  
  // Send data via MQTT
  if (mqtt.connected()) {
    sendMQTTData();
  }
}

void sendDataToWebSocketClients() {
  DynamicJsonDocument doc(4096);
  
  doc["type"] = "realtime_data";
  doc["timestamp"] = millis();
  
  doc["electrical"]["current"] = electrical_data.current;
  doc["electrical"]["voltage"] = electrical_data.voltage;
  doc["electrical"]["power"] = electrical_data.power;
  doc["electrical"]["power_factor"] = electrical_data.power_factor;
  
  doc["acoustic"]["rms_level"] = acoustic_data.rms_level;
  doc["acoustic"]["peak_frequency"] = acoustic_data.peak_frequency;
  doc["acoustic"]["spatter_index"] = acoustic_data.spatter_index;
  
  doc["quality"]["score"] = quality_prediction.overall_quality;
  doc["quality"]["defect_type"] = quality_prediction.defect_type;
  doc["quality"]["confidence"] = quality_prediction.confidence;
  
  String message;
  serializeJson(doc, message);
  ws.textAll(message);
}

void sendQualityAlert() {
  // Send MQTT alert
  DynamicJsonDocument alert_doc(1024);
  alert_doc["timestamp"] = millis();
  alert_doc["type"] = "weld_quality_alert";
  alert_doc["quality_score"] = quality_prediction.overall_quality;
  alert_doc["defect_type"] = quality_prediction.defect_type;
  alert_doc["defect_probability"] = quality_prediction.defect_probability;
  alert_doc["confidence"] = quality_prediction.confidence;
  
  String alert_message;
  serializeJson(alert_doc, alert_message);
  mqtt.publish("weld/alerts", alert_message.c_str());
  
  // Send WebSocket alert
  DynamicJsonDocument ws_doc(1024);
  ws_doc["type"] = "alert";
  ws_doc["severity"] = "high";
  ws_doc["message"] = "Poor weld quality detected: " + quality_prediction.defect_type;
  ws_doc["data"] = alert_doc;
  
  String ws_message;
  serializeJson(ws_doc, ws_message);
  ws.textAll(ws_message);
  
  // Sound buzzer
  soundAlert();
}

void updateSystemMetrics() {
  system_metrics.uptime = millis();
  system_metrics.memory_usage = (float)(ESP.getFreeHeap()) / ESP.getHeapSize() * 100.0;
  system_metrics.signal_quality = calculateSignalQuality();
  
  // Calculate prediction accuracy (simplified)
  if (system_metrics.ml_predictions > 0) {
    system_metrics.prediction_accuracy = 0.85; // Would be calculated from validation data
  }
}

// Communication callbacks and utility functions
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.println("MQTT message received: " + message);
  
  if (String(topic) == "weld/commands") {
    handleMQTTCommand(message);
  } else if (String(topic) == "weld/config") {
    handleMQTTConfig(message);
  }
}

void onWebSocketEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, 
                     AwsEventType type, void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", 
                    client->id(), client->remoteIP().toString().c_str());
      break;
      
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
      
    case WS_EVT_DATA:
      handleWebSocketData(client, data, len);
      break;
      
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

// Additional utility functions would be implemented here...
// This provides a comprehensive foundation for the welding signal processing system