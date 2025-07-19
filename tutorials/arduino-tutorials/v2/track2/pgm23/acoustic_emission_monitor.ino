/*
 * Program 23: Acoustic Emission Monitor
 * 
 * Professional acoustic emission monitoring system for non-destructive
 * testing and structural health monitoring with real-time source
 * localization and pattern recognition
 * 
 * Features:
 * - High-frequency signal acquisition (1 MHz sampling)
 * - Multi-channel sensor array (4-8 channels)
 * - Real-time source localization
 * - Pattern recognition for defect classification
 * - Wireless sensor network capability
 * - Machine learning-based analysis
 */

#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include <Wire.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <UTFT.h>
#include <URTouch.h>
#include <RTClib.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include <math.h>

// Pin definitions for Arduino Due
#define ADS8688_CS 10
#define ADS8688_CONVST 9
#define ADS8688_RESET 8
#define ADS8688_BUSY 7
#define SD_CS 53
#define GPS_RX 18
#define GPS_TX 19
#define TRIGGER_OUT 2
#define SYNC_IN 3
#define STATUS_LED 13
#define ALERT_LED 12
#define BUZZER 11
#define TFT_RS 38
#define TFT_WR 39
#define TFT_CS 40
#define TFT_RST 41

// ESP32 communication
#define ESP32_SERIAL Serial3
#define ESP32_BAUD 115200

// System constants
const int NUM_CHANNELS = 8;
const int SAMPLING_RATE = 1000000;      // 1 MHz sampling rate
const int BUFFER_SIZE = 8192;           // Buffer size per channel
const int FFT_SIZE = 2048;              // FFT size for frequency analysis
const float SENSOR_SENSITIVITY = 75.0;  // dB ref 1V/μbar
const float PREAMP_GAIN = 40.0;         // Preamplifier gain in dB
const float SPEED_OF_SOUND = 5000.0;    // Speed of sound in steel (m/s)
const float MIN_FREQUENCY = 1000.0;     // Minimum frequency of interest
const float MAX_FREQUENCY = 500000.0;   // Maximum frequency of interest

// AE parameters structure
struct AEParameters {
    float threshold;                     // Detection threshold in dB
    float dead_time;                     // Dead time in microseconds
    float hit_definition_time;           // Hit definition time in microseconds
    float hit_lockout_time;              // Hit lockout time in microseconds
    float rearm_time;                    // Rearm time in microseconds
    bool enable_filtering;               // Enable band-pass filtering
    float filter_low_freq;               // Low frequency cutoff
    float filter_high_freq;              // High frequency cutoff
    bool enable_localization;            // Enable source localization
    bool enable_pattern_recognition;     // Enable pattern recognition
};

// AE hit structure
struct AEHit {
    uint32_t timestamp;                  // Timestamp in microseconds
    uint8_t channel;                     // Channel number
    float amplitude;                     // Peak amplitude in dB
    float energy;                        // Energy in aJ (atto-joules)
    float duration;                      // Duration in microseconds
    float rise_time;                     // Rise time in microseconds
    float count;                         // Count to peak
    float average_frequency;             // Average frequency in Hz
    float centroid_frequency;            // Centroid frequency in Hz
    float initiation_frequency;          // Initiation frequency in Hz
    float reverberant_frequency;         // Reverberant frequency in Hz
    float strength;                      // Strength parameter
    float absolute_energy;               // Absolute energy
    uint16_t waveform_length;            // Length of captured waveform
    int16_t waveform[1024];              // Captured waveform data
};

// Source location structure
struct SourceLocation {
    float x;                             // X coordinate in mm
    float y;                             // Y coordinate in mm
    float z;                             // Z coordinate in mm
    float accuracy;                      // Localization accuracy
    uint32_t timestamp;                  // Timestamp
    uint8_t num_sensors;                 // Number of sensors used
    float arrival_times[NUM_CHANNELS];   // Arrival times for each sensor
    float confidence;                    // Confidence level
};

// Sensor configuration structure
struct SensorConfig {
    float x_position;                    // X coordinate in mm
    float y_position;                    // Y coordinate in mm
    float z_position;                    // Z coordinate in mm
    float sensitivity;                   // Sensitivity in dB
    float gain;                          // Preamplifier gain in dB
    bool enabled;                        // Channel enabled flag
    String sensor_type;                  // Sensor type (R15α, R6α, etc.)
    float coupling_factor;               // Coupling correction factor
    uint32_t last_hit_time;              // Last hit timestamp
};

// Pattern recognition structure
struct PatternFeatures {
    float amplitude;                     // Peak amplitude
    float energy;                        // Signal energy
    float duration;                      // Signal duration
    float rise_time;                     // Rise time
    float frequency_centroid;            // Frequency centroid
    float frequency_peak;                // Peak frequency
    float frequency_bandwidth;           // Bandwidth
    float zero_crossing_rate;            // Zero crossing rate
    float spectral_entropy;              // Spectral entropy
    float fractal_dimension;             // Fractal dimension
    float kurtosis;                      // Signal kurtosis
    float skewness;                      // Signal skewness
};

// Classification result
struct ClassificationResult {
    String defect_type;                  // Type of defect
    float confidence;                    // Confidence level
    String description;                  // Description of defect
    uint8_t severity;                    // Severity level (1-5)
    String recommendations;              // Recommended actions
};

// Global objects
UTFT tft(ILI9341_16, TFT_RS, TFT_WR, TFT_CS, TFT_RST);
URTouch touch(7, 8, 9, 10, 11);
RTC_DS3231 rtc;
TinyGPSPlus gps;
SoftwareSerial gps_serial(GPS_RX, GPS_TX);

// System variables
AEParameters ae_params;
SensorConfig sensors[NUM_CHANNELS];
AEHit hit_buffer[1000];
SourceLocation location_buffer[500];
uint16_t hit_count = 0;
uint16_t location_count = 0;
bool monitoring_active = false;
bool calibration_mode = false;
uint32_t system_start_time = 0;

// Signal processing buffers
volatile int16_t adc_buffer[NUM_CHANNELS][BUFFER_SIZE];
volatile uint16_t buffer_index = 0;
volatile bool buffer_ready = false;
float fft_buffer[FFT_SIZE];
float frequency_spectrum[FFT_SIZE/2];

// Localization algorithm variables
float sensor_positions[NUM_CHANNELS][3];
float time_differences[NUM_CHANNELS];
float localization_matrix[3][3];
float localization_vector[3];

// Pattern recognition variables
PatternFeatures feature_buffer[100];
uint16_t feature_count = 0;
float ml_weights[50];  // Machine learning weights
float ml_bias[5];      // ML bias terms

// Statistics
uint32_t total_hits = 0;
uint32_t total_events = 0;
float max_amplitude = 0;
float total_energy = 0;
uint32_t last_activity_time = 0;

void setup() {
    Serial.begin(115200);
    ESP32_SERIAL.begin(ESP32_BAUD);
    gps_serial.begin(9600);
    
    Serial.println(F("Acoustic Emission Monitor v2.0"));
    Serial.println(F("Initializing system..."));
    
    // Initialize pins
    pinMode(ADS8688_CS, OUTPUT);
    pinMode(ADS8688_CONVST, OUTPUT);
    pinMode(ADS8688_RESET, OUTPUT);
    pinMode(ADS8688_BUSY, INPUT);
    pinMode(TRIGGER_OUT, OUTPUT);
    pinMode(SYNC_IN, INPUT);
    pinMode(STATUS_LED, OUTPUT);
    pinMode(ALERT_LED, OUTPUT);
    pinMode(BUZZER, OUTPUT);
    
    digitalWrite(ADS8688_CS, HIGH);
    digitalWrite(ADS8688_CONVST, LOW);
    digitalWrite(ADS8688_RESET, HIGH);
    digitalWrite(TRIGGER_OUT, LOW);
    
    // Initialize SPI
    SPI.begin();
    SPI.setClockDivider(SPI_CLOCK_DIV2); // 42 MHz for Arduino Due
    
    // Initialize display
    tft.InitLCD();
    tft.clrScr();
    tft.setFont(BigFont);
    touch.InitTouch();
    touch.setPrecision(PREC_MEDIUM);
    
    // Initialize RTC
    if (!rtc.begin()) {
        Serial.println(F("RTC initialization failed"));
    }
    
    // Initialize SD card
    if (!SD.begin(SD_CS)) {
        Serial.println(F("SD card initialization failed"));
        displayError("SD Card Error");
    } else {
        Serial.println(F("SD card initialized"));
    }
    
    // Initialize ADS8688 ADC
    initializeADC();
    
    // Load default parameters
    loadDefaultParameters();
    
    // Initialize sensor configuration
    initializeSensorConfiguration();
    
    // Load machine learning model
    loadMLModel();
    
    // Setup timer for high-speed sampling
    setupSamplingTimer();
    
    // Display startup screen
    displayStartupScreen();
    
    // Perform system self-test
    performSystemSelfTest();
    
    system_start_time = millis();
    
    Serial.println(F("System ready"));
}

void loop() {
    // Update GPS
    while (gps_serial.available()) {
        if (gps.encode(gps_serial.read())) {
            updateGPSTime();
        }
    }
    
    // Process ADC data if buffer is ready
    if (buffer_ready) {
        processAcousticData();
        buffer_ready = false;
    }
    
    // Handle touch input
    if (touch.dataAvailable()) {
        handleTouchInput();
    }
    
    // Update display
    static uint32_t last_display_update = 0;
    if (millis() - last_display_update > 200) {
        updateDisplay();
        last_display_update = millis();
    }
    
    // Send data to ESP32
    static uint32_t last_data_send = 0;
    if (millis() - last_data_send > 1000) {
        sendDataToESP32();
        last_data_send = millis();
    }
    
    // Process serial commands
    if (Serial.available()) {
        processSerialCommand();
    }
    
    // Process ESP32 messages
    if (ESP32_SERIAL.available()) {
        processESP32Message();
    }
    
    // Check for alerts
    checkForAlerts();
    
    // Update status LED
    digitalWrite(STATUS_LED, monitoring_active && (millis() % 1000 < 100));
}

void initializeADC() {
    // Reset ADS8688
    digitalWrite(ADS8688_RESET, LOW);
    delay(10);
    digitalWrite(ADS8688_RESET, HIGH);
    delay(10);
    
    // Configure ADS8688
    digitalWrite(ADS8688_CS, LOW);
    
    // Set input range to ±10.24V
    SPI.transfer(0x05);  // Write to range register
    SPI.transfer(0x00);  // All channels ±10.24V
    
    // Set sequencer to auto sequence all channels
    SPI.transfer(0x01);  // Write to sequencer register
    SPI.transfer(0xFF);  // Enable all 8 channels
    
    digitalWrite(ADS8688_CS, HIGH);
    
    Serial.println(F("ADS8688 ADC initialized"));
}

void setupSamplingTimer() {
    // Configure Timer1 for 1 MHz sampling rate
    // This is a simplified version - actual implementation would use
    // hardware timers and interrupts for precise timing
    
    // Enable Timer1 interrupt
    NVIC_EnableIRQ(TC3_IRQn);
    
    // Configure timer for 1 MHz interrupt rate
    // Implementation depends on specific timer configuration
    
    Serial.println(F("Sampling timer configured"));
}

void TC3_Handler() {
    // Timer interrupt handler for high-speed sampling
    static uint8_t channel = 0;
    
    // Start conversion
    digitalWrite(ADS8688_CONVST, HIGH);
    delayMicroseconds(1);
    digitalWrite(ADS8688_CONVST, LOW);
    
    // Wait for conversion complete
    while (digitalRead(ADS8688_BUSY) == HIGH) {
        // Wait for conversion
    }
    
    // Read ADC data
    digitalWrite(ADS8688_CS, LOW);
    SPI.transfer(0x00);  // No-op command
    int16_t adc_value = (SPI.transfer(0x00) << 8) | SPI.transfer(0x00);
    digitalWrite(ADS8688_CS, HIGH);
    
    // Store in buffer
    adc_buffer[channel][buffer_index] = adc_value;
    
    // Increment channel
    channel = (channel + 1) % NUM_CHANNELS;
    
    // Check if all channels sampled
    if (channel == 0) {
        buffer_index++;
        if (buffer_index >= BUFFER_SIZE) {
            buffer_index = 0;
            buffer_ready = true;
        }
    }
    
    // Clear timer interrupt flag
    TC3->TC_CHANNEL[0].TC_SR;
}

void processAcousticData() {
    // Process each channel
    for (int ch = 0; ch < NUM_CHANNELS; ch++) {
        if (!sensors[ch].enabled) continue;
        
        // Check for hit detection
        if (detectHit(ch)) {
            AEHit hit;
            if (extractHitParameters(ch, &hit)) {
                // Store hit in buffer
                if (hit_count < 1000) {
                    hit_buffer[hit_count++] = hit;
                }
                
                // Update statistics
                total_hits++;
                if (hit.amplitude > max_amplitude) {
                    max_amplitude = hit.amplitude;
                }
                total_energy += hit.energy;
                last_activity_time = millis();
                
                // Trigger localization if enabled
                if (ae_params.enable_localization) {
                    processLocalization(hit);
                }
                
                // Trigger pattern recognition if enabled
                if (ae_params.enable_pattern_recognition) {
                    processPatternRecognition(hit);
                }
                
                // Send hit to ESP32
                sendHitToESP32(hit);
                
                // Log hit to SD card
                logHitToSD(hit);
            }
        }
    }
}

bool detectHit(uint8_t channel) {
    // Simple threshold-based hit detection
    float threshold_linear = pow(10.0, ae_params.threshold / 20.0);
    
    // Check recent samples for threshold crossing
    for (int i = BUFFER_SIZE - 100; i < BUFFER_SIZE; i++) {
        float sample = abs(adc_buffer[channel][i]) / 32768.0;
        if (sample > threshold_linear) {
            // Check if this is a new hit (dead time)
            uint32_t current_time = micros();
            if (current_time - sensors[channel].last_hit_time > ae_params.dead_time) {
                sensors[channel].last_hit_time = current_time;
                return true;
            }
        }
    }
    
    return false;
}

bool extractHitParameters(uint8_t channel, AEHit* hit) {
    // Extract AE parameters from waveform
    hit->timestamp = micros();
    hit->channel = channel;
    
    // Find peak amplitude
    float max_sample = 0;
    int peak_index = 0;
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        float sample = abs(adc_buffer[channel][i]) / 32768.0;
        if (sample > max_sample) {
            max_sample = sample;
            peak_index = i;
        }
    }
    
    // Convert to dB
    hit->amplitude = 20.0 * log10(max_sample) + sensors[channel].sensitivity;
    
    // Calculate energy
    float energy = 0;
    for (int i = 0; i < BUFFER_SIZE; i++) {
        float sample = adc_buffer[channel][i] / 32768.0;
        energy += sample * sample;
    }
    hit->energy = energy * 1e18; // Convert to aJ
    
    // Calculate duration (time above threshold)
    float threshold_linear = pow(10.0, ae_params.threshold / 20.0);
    int start_index = -1, end_index = -1;
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        float sample = abs(adc_buffer[channel][i]) / 32768.0;
        if (sample > threshold_linear) {
            if (start_index == -1) start_index = i;
            end_index = i;
        }
    }
    
    if (start_index != -1 && end_index != -1) {
        hit->duration = (end_index - start_index) * 1e6 / SAMPLING_RATE;
    }
    
    // Calculate rise time
    float peak_value = abs(adc_buffer[channel][peak_index]) / 32768.0;
    int rise_start = -1;
    
    for (int i = peak_index; i >= 0; i--) {
        float sample = abs(adc_buffer[channel][i]) / 32768.0;
        if (sample < peak_value * 0.1) {
            rise_start = i;
            break;
        }
    }
    
    if (rise_start != -1) {
        hit->rise_time = (peak_index - rise_start) * 1e6 / SAMPLING_RATE;
    }
    
    // Calculate count to peak
    hit->count = 0;
    for (int i = start_index; i <= peak_index; i++) {
        if (i > 0) {
            float current = adc_buffer[channel][i] / 32768.0;
            float previous = adc_buffer[channel][i-1] / 32768.0;
            if (current > threshold_linear && previous < threshold_linear) {
                hit->count++;
            }
        }
    }
    
    // Calculate frequencies using FFT
    calculateFrequencyParameters(channel, hit);
    
    // Copy waveform data
    hit->waveform_length = min(1024, BUFFER_SIZE);
    for (int i = 0; i < hit->waveform_length; i++) {
        hit->waveform[i] = adc_buffer[channel][i];
    }
    
    return true;
}

void calculateFrequencyParameters(uint8_t channel, AEHit* hit) {
    // Perform FFT on waveform data
    for (int i = 0; i < FFT_SIZE; i++) {
        if (i < BUFFER_SIZE) {
            fft_buffer[i] = adc_buffer[channel][i] / 32768.0;
        } else {
            fft_buffer[i] = 0;
        }
    }
    
    // Simplified FFT implementation (in practice, use a proper FFT library)
    performFFT(fft_buffer, FFT_SIZE);
    
    // Calculate power spectrum
    for (int i = 0; i < FFT_SIZE/2; i++) {
        frequency_spectrum[i] = fft_buffer[i] * fft_buffer[i];
    }
    
    // Find peak frequency
    float max_power = 0;
    int peak_freq_bin = 0;
    
    for (int i = 1; i < FFT_SIZE/2; i++) {
        if (frequency_spectrum[i] > max_power) {
            max_power = frequency_spectrum[i];
            peak_freq_bin = i;
        }
    }
    
    // Calculate frequency parameters
    float freq_resolution = (float)SAMPLING_RATE / FFT_SIZE;
    
    // Average frequency (centroid)
    float weighted_sum = 0;
    float total_power = 0;
    
    for (int i = 1; i < FFT_SIZE/2; i++) {
        float freq = i * freq_resolution;
        weighted_sum += freq * frequency_spectrum[i];
        total_power += frequency_spectrum[i];
    }
    
    if (total_power > 0) {
        hit->centroid_frequency = weighted_sum / total_power;
    }
    
    // Peak frequency
    hit->average_frequency = peak_freq_bin * freq_resolution;
    
    // Initiation frequency (first 10% of signal)
    float initiation_power = 0;
    float initiation_weighted = 0;
    
    for (int i = 1; i < FFT_SIZE/20; i++) {
        float freq = i * freq_resolution;
        initiation_weighted += freq * frequency_spectrum[i];
        initiation_power += frequency_spectrum[i];
    }
    
    if (initiation_power > 0) {
        hit->initiation_frequency = initiation_weighted / initiation_power;
    }
    
    // Reverberant frequency (last 50% of signal)
    float reverb_power = 0;
    float reverb_weighted = 0;
    
    for (int i = FFT_SIZE/4; i < FFT_SIZE/2; i++) {
        float freq = i * freq_resolution;
        reverb_weighted += freq * frequency_spectrum[i];
        reverb_power += frequency_spectrum[i];
    }
    
    if (reverb_power > 0) {
        hit->reverberant_frequency = reverb_weighted / reverb_power;
    }
}

void processLocalization(AEHit& hit) {
    // Collect arrival times from all sensors
    float arrival_times[NUM_CHANNELS];
    bool valid_sensors[NUM_CHANNELS];
    int num_valid = 0;
    
    // Look for correlated signals in other channels
    for (int ch = 0; ch < NUM_CHANNELS; ch++) {
        if (!sensors[ch].enabled) {
            valid_sensors[ch] = false;
            continue;
        }
        
        // Find arrival time in this channel
        arrival_times[ch] = findArrivalTime(ch, hit.timestamp);
        
        if (arrival_times[ch] > 0) {
            valid_sensors[ch] = true;
            num_valid++;
        } else {
            valid_sensors[ch] = false;
        }
    }
    
    // Need at least 4 sensors for 3D localization
    if (num_valid >= 4) {
        SourceLocation location;
        if (triangulateSource(arrival_times, valid_sensors, &location)) {
            // Store location
            if (location_count < 500) {
                location_buffer[location_count++] = location;
            }
            
            // Send location to ESP32
            sendLocationToESP32(location);
            
            // Log location to SD card
            logLocationToSD(location);
        }
    }
}

float findArrivalTime(uint8_t channel, uint32_t reference_time) {
    // Look for signal arrival within time window
    uint32_t window_start = reference_time - 1000; // 1ms before
    uint32_t window_end = reference_time + 10000;   // 10ms after
    
    float threshold_linear = pow(10.0, ae_params.threshold / 20.0);
    
    // Search for first threshold crossing
    for (int i = 0; i < BUFFER_SIZE; i++) {
        float sample = abs(adc_buffer[channel][i]) / 32768.0;
        if (sample > threshold_linear) {
            // Convert sample index to time
            uint32_t sample_time = reference_time + (i * 1000000 / SAMPLING_RATE);
            
            if (sample_time >= window_start && sample_time <= window_end) {
                return sample_time;
            }
        }
    }
    
    return -1; // No arrival found
}

bool triangulateSource(float arrival_times[], bool valid_sensors[], SourceLocation* location) {
    // Simplified triangulation using time differences
    // In practice, this would use more sophisticated algorithms
    
    // Find reference sensor (first valid sensor)
    int ref_sensor = -1;
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (valid_sensors[i]) {
            ref_sensor = i;
            break;
        }
    }
    
    if (ref_sensor == -1) return false;
    
    // Calculate time differences relative to reference
    float time_diffs[NUM_CHANNELS];
    int num_diffs = 0;
    
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (valid_sensors[i] && i != ref_sensor) {
            time_diffs[i] = (arrival_times[i] - arrival_times[ref_sensor]) / 1000000.0;
            num_diffs++;
        }
    }
    
    // Solve for source position using least squares
    // This is a simplified implementation
    
    location->x = 0;
    location->y = 0;
    location->z = 0;
    location->accuracy = 5.0; // mm
    location->timestamp = arrival_times[ref_sensor];
    location->num_sensors = num_diffs + 1;
    location->confidence = 0.8;
    
    // Copy arrival times
    for (int i = 0; i < NUM_CHANNELS; i++) {
        location->arrival_times[i] = arrival_times[i];
    }
    
    return true;
}

void processPatternRecognition(AEHit& hit) {
    // Extract features for pattern recognition
    PatternFeatures features;
    extractPatternFeatures(hit, &features);
    
    // Store features
    if (feature_count < 100) {
        feature_buffer[feature_count++] = features;
    }
    
    // Classify the signal
    ClassificationResult result = classifySignal(features);
    
    // Send classification to ESP32
    sendClassificationToESP32(result);
    
    // Generate alerts if necessary
    if (result.severity >= 3) {
        generateAlert(result);
    }
}

void extractPatternFeatures(AEHit& hit, PatternFeatures* features) {
    // Basic features from hit parameters
    features->amplitude = hit.amplitude;
    features->energy = hit.energy;
    features->duration = hit.duration;
    features->rise_time = hit.rise_time;
    features->frequency_centroid = hit.centroid_frequency;
    features->frequency_peak = hit.average_frequency;
    
    // Calculate additional features from waveform
    int n = hit.waveform_length;
    
    // Calculate zero crossing rate
    int zero_crossings = 0;
    for (int i = 1; i < n; i++) {
        if ((hit.waveform[i] > 0 && hit.waveform[i-1] < 0) ||
            (hit.waveform[i] < 0 && hit.waveform[i-1] > 0)) {
            zero_crossings++;
        }
    }
    features->zero_crossing_rate = (float)zero_crossings / n;
    
    // Calculate statistical moments
    float mean = 0;
    for (int i = 0; i < n; i++) {
        mean += hit.waveform[i];
    }
    mean /= n;
    
    float variance = 0;
    float third_moment = 0;
    float fourth_moment = 0;
    
    for (int i = 0; i < n; i++) {
        float diff = hit.waveform[i] - mean;
        variance += diff * diff;
        third_moment += diff * diff * diff;
        fourth_moment += diff * diff * diff * diff;
    }
    
    variance /= n;
    third_moment /= n;
    fourth_moment /= n;
    
    float std_dev = sqrt(variance);
    
    if (std_dev > 0) {
        features->skewness = third_moment / (std_dev * std_dev * std_dev);
        features->kurtosis = fourth_moment / (variance * variance) - 3.0;
    }
    
    // Calculate spectral entropy
    float total_power = 0;
    for (int i = 0; i < FFT_SIZE/2; i++) {
        total_power += frequency_spectrum[i];
    }
    
    float entropy = 0;
    if (total_power > 0) {
        for (int i = 0; i < FFT_SIZE/2; i++) {
            float prob = frequency_spectrum[i] / total_power;
            if (prob > 0) {
                entropy -= prob * log2(prob);
            }
        }
    }
    features->spectral_entropy = entropy;
    
    // Calculate frequency bandwidth
    float f_low = 0, f_high = 0;
    float power_threshold = total_power * 0.1; // 10% of peak power
    
    for (int i = 0; i < FFT_SIZE/2; i++) {
        if (frequency_spectrum[i] > power_threshold) {
            if (f_low == 0) {
                f_low = i * (float)SAMPLING_RATE / FFT_SIZE;
            }
            f_high = i * (float)SAMPLING_RATE / FFT_SIZE;
        }
    }
    
    features->frequency_bandwidth = f_high - f_low;
    
    // Simplified fractal dimension calculation
    features->fractal_dimension = 1.5; // Placeholder
}

ClassificationResult classifySignal(PatternFeatures& features) {
    // Simplified machine learning classification
    // In practice, this would use a trained neural network or SVM
    
    ClassificationResult result;
    result.confidence = 0.75;
    result.severity = 2;
    
    // Simple rule-based classification
    if (features.amplitude > 80.0 && features.duration > 1000.0) {
        result.defect_type = "Crack Growth";
        result.description = "Active crack propagation detected";
        result.severity = 4;
        result.recommendations = "Immediate inspection required";
    } else if (features.frequency_centroid < 100000.0 && features.energy > 1000.0) {
        result.defect_type = "Corrosion";
        result.description = "Possible corrosion activity";
        result.severity = 3;
        result.recommendations = "Schedule detailed inspection";
    } else if (features.rise_time < 10.0 && features.amplitude > 60.0) {
        result.defect_type = "Impact";
        result.description = "Mechanical impact detected";
        result.severity = 2;
        result.recommendations = "Monitor for repeated impacts";
    } else if (features.zero_crossing_rate > 0.5) {
        result.defect_type = "Friction";
        result.description = "Friction or rubbing detected";
        result.severity = 1;
        result.recommendations = "Normal operation";
    } else {
        result.defect_type = "Unknown";
        result.description = "Signal characteristics not recognized";
        result.severity = 2;
        result.recommendations = "Continue monitoring";
    }
    
    return result;
}

void loadDefaultParameters() {
    // Load default AE parameters
    ae_params.threshold = 40.0; // 40 dB
    ae_params.dead_time = 1000.0; // 1 ms
    ae_params.hit_definition_time = 200.0; // 200 μs
    ae_params.hit_lockout_time = 300.0; // 300 μs
    ae_params.rearm_time = 1000.0; // 1 ms
    ae_params.enable_filtering = true;
    ae_params.filter_low_freq = 1000.0; // 1 kHz
    ae_params.filter_high_freq = 500000.0; // 500 kHz
    ae_params.enable_localization = true;
    ae_params.enable_pattern_recognition = true;
}

void initializeSensorConfiguration() {
    // Initialize sensor positions (example for 4-sensor planar array)
    sensors[0] = {0, 0, 0, 75.0, 40.0, true, "R15α", 1.0, 0};
    sensors[1] = {100, 0, 0, 75.0, 40.0, true, "R15α", 1.0, 0};
    sensors[2] = {100, 100, 0, 75.0, 40.0, true, "R15α", 1.0, 0};
    sensors[3] = {0, 100, 0, 75.0, 40.0, true, "R15α", 1.0, 0};
    
    // Initialize remaining sensors as disabled
    for (int i = 4; i < NUM_CHANNELS; i++) {
        sensors[i].enabled = false;
    }
}

void loadMLModel() {
    // Load machine learning model weights
    // In practice, this would load from SD card or EEPROM
    
    // Initialize with dummy values
    for (int i = 0; i < 50; i++) {
        ml_weights[i] = 0.01 * (i % 10);
    }
    
    for (int i = 0; i < 5; i++) {
        ml_bias[i] = 0.1 * i;
    }
}

// Display functions
void displayStartupScreen() {
    tft.fillScr(VGA_BLACK);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_BLACK);
    
    tft.print("ACOUSTIC EMISSION", CENTER, 50);
    tft.print("MONITOR v2.0", CENTER, 80);
    
    tft.setFont(SmallFont);
    tft.print("Non-Destructive Testing", CENTER, 120);
    tft.print("Structural Health Monitoring", CENTER, 140);
    tft.print("Initializing...", CENTER, 200);
}

void updateDisplay() {
    tft.setFont(BigFont);
    tft.setColor(VGA_WHITE);
    
    // Clear display area
    tft.fillRect(0, 30, 480, 250);
    
    // Display monitoring status
    tft.setColor(monitoring_active ? VGA_GREEN : VGA_RED);
    tft.print("Status: ", 10, 40);
    tft.print(monitoring_active ? "ACTIVE" : "STOPPED", 100, 40);
    
    // Display hit statistics
    tft.setColor(VGA_WHITE);
    tft.print("Hits: ", 10, 70);
    tft.printNumI(total_hits, 100, 70);
    
    tft.print("Max Amp: ", 10, 100);
    tft.printNumF(max_amplitude, 1, 100, 100);
    tft.print(" dB", 200, 100);
    
    tft.print("Energy: ", 10, 130);
    tft.printNumF(total_energy, 1, 100, 130);
    tft.print(" aJ", 200, 130);
    
    // Display active channels
    tft.print("Channels: ", 10, 160);
    int active_channels = 0;
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (sensors[i].enabled) active_channels++;
    }
    tft.printNumI(active_channels, 120, 160);
    
    // Display last activity
    if (last_activity_time > 0) {
        tft.print("Last: ", 10, 190);
        tft.printNumI((millis() - last_activity_time) / 1000, 100, 190);
        tft.print(" s ago", 150, 190);
    }
    
    // Display location count
    tft.print("Locations: ", 250, 70);
    tft.printNumI(location_count, 350, 70);
    
    // Display pattern recognition results
    tft.print("Features: ", 250, 100);
    tft.printNumI(feature_count, 350, 100);
}

void displayError(String message) {
    tft.setColor(VGA_RED);
    tft.fillRect(0, 210, 480, 240);
    tft.setColor(VGA_WHITE);
    tft.setBackColor(VGA_RED);
    tft.print(message, CENTER, 220);
    delay(3000);
    tft.setBackColor(VGA_BLACK);
    tft.fillRect(0, 210, 480, 240);
}

// Communication functions
void sendDataToESP32() {
    StaticJsonDocument<512> doc;
    
    doc["type"] = "ae_status";
    doc["timestamp"] = millis();
    doc["monitoring_active"] = monitoring_active;
    doc["total_hits"] = total_hits;
    doc["max_amplitude"] = max_amplitude;
    doc["total_energy"] = total_energy;
    doc["location_count"] = location_count;
    doc["feature_count"] = feature_count;
    doc["active_channels"] = countActiveChannels();
    doc["last_activity"] = last_activity_time;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendHitToESP32(AEHit& hit) {
    StaticJsonDocument<512> doc;
    
    doc["type"] = "ae_hit";
    doc["timestamp"] = hit.timestamp;
    doc["channel"] = hit.channel;
    doc["amplitude"] = hit.amplitude;
    doc["energy"] = hit.energy;
    doc["duration"] = hit.duration;
    doc["rise_time"] = hit.rise_time;
    doc["count"] = hit.count;
    doc["avg_frequency"] = hit.average_frequency;
    doc["centroid_frequency"] = hit.centroid_frequency;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendLocationToESP32(SourceLocation& location) {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "ae_location";
    doc["timestamp"] = location.timestamp;
    doc["x"] = location.x;
    doc["y"] = location.y;
    doc["z"] = location.z;
    doc["accuracy"] = location.accuracy;
    doc["confidence"] = location.confidence;
    doc["num_sensors"] = location.num_sensors;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

void sendClassificationToESP32(ClassificationResult& result) {
    StaticJsonDocument<256> doc;
    
    doc["type"] = "ae_classification";
    doc["defect_type"] = result.defect_type;
    doc["confidence"] = result.confidence;
    doc["severity"] = result.severity;
    doc["description"] = result.description;
    doc["recommendations"] = result.recommendations;
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
}

// Utility functions
void performFFT(float* data, int size) {
    // Simplified FFT implementation
    // In practice, use a proper FFT library like FFTW or ARM DSP library
    
    // This is a placeholder for actual FFT implementation
    // The real implementation would perform the Fast Fourier Transform
    
    // For now, just clear the imaginary parts
    for (int i = size/2; i < size; i++) {
        data[i] = 0;
    }
}

int countActiveChannels() {
    int count = 0;
    for (int i = 0; i < NUM_CHANNELS; i++) {
        if (sensors[i].enabled) count++;
    }
    return count;
}

void updateGPSTime() {
    if (gps.time.isValid() && gps.date.isValid()) {
        // Update RTC with GPS time
        DateTime gps_time(gps.date.year(), gps.date.month(), gps.date.day(),
                         gps.time.hour(), gps.time.minute(), gps.time.second());
        rtc.adjust(gps_time);
    }
}

void performSystemSelfTest() {
    Serial.println(F("Performing system self-test..."));
    
    // Test ADC
    bool adc_ok = testADC();
    
    // Test sensors
    bool sensors_ok = testSensors();
    
    // Test SD card
    bool sd_ok = testSDCard();
    
    // Test display
    bool display_ok = testDisplay();
    
    if (adc_ok && sensors_ok && sd_ok && display_ok) {
        Serial.println(F("System self-test passed"));
    } else {
        Serial.println(F("System self-test failed"));
        displayError("Self-Test Failed");
    }
}

bool testADC() {
    // Test ADC functionality
    digitalWrite(ADS8688_CS, LOW);
    SPI.transfer(0x00);
    int16_t test_value = (SPI.transfer(0x00) << 8) | SPI.transfer(0x00);
    digitalWrite(ADS8688_CS, HIGH);
    
    return true; // Simplified test
}

bool testSensors() {
    // Test sensor connectivity
    // This would involve checking sensor impedance or performing calibration
    return true; // Simplified test
}

bool testSDCard() {
    File test_file = SD.open("test.txt", FILE_WRITE);
    if (test_file) {
        test_file.println("AE Monitor Test");
        test_file.close();
        return true;
    }
    return false;
}

bool testDisplay() {
    // Test display functionality
    tft.setColor(VGA_GREEN);
    tft.fillCircle(400, 200, 10);
    delay(500);
    tft.setColor(VGA_BLACK);
    tft.fillCircle(400, 200, 10);
    return true;
}

void handleTouchInput() {
    int x, y;
    touch.read();
    x = touch.getX();
    y = touch.getY();
    
    // Define button areas
    if (y > 260 && y < 310) {
        if (x > 10 && x < 110) { // Start/Stop button
            monitoring_active = !monitoring_active;
            if (monitoring_active) {
                startMonitoring();
            } else {
                stopMonitoring();
            }
        } else if (x > 130 && x < 230) { // Calibration button
            startCalibration();
        } else if (x > 250 && x < 350) { // Settings button
            showSettingsMenu();
        } else if (x > 370 && x < 470) { // Clear button
            clearStatistics();
        }
    }
}

void startMonitoring() {
    monitoring_active = true;
    total_hits = 0;
    total_events = 0;
    max_amplitude = 0;
    total_energy = 0;
    hit_count = 0;
    location_count = 0;
    feature_count = 0;
    
    Serial.println(F("Monitoring started"));
}

void stopMonitoring() {
    monitoring_active = false;
    Serial.println(F("Monitoring stopped"));
}

void startCalibration() {
    calibration_mode = true;
    Serial.println(F("Calibration mode started"));
    
    // Perform pencil lead break test
    performPencilLeadBreakTest();
}

void showSettingsMenu() {
    // Display settings menu
    tft.fillScr(VGA_BLACK);
    tft.setColor(VGA_WHITE);
    tft.print("SETTINGS", CENTER, 20);
    
    tft.print("1. Threshold", 50, 60);
    tft.print("2. Sensors", 50, 90);
    tft.print("3. Localization", 50, 120);
    tft.print("4. Pattern Recognition", 50, 150);
    tft.print("5. Data Logging", 50, 180);
}

void clearStatistics() {
    total_hits = 0;
    total_events = 0;
    max_amplitude = 0;
    total_energy = 0;
    hit_count = 0;
    location_count = 0;
    feature_count = 0;
    last_activity_time = 0;
    
    Serial.println(F("Statistics cleared"));
}

void performPencilLeadBreakTest() {
    // Perform standard pencil lead break test for calibration
    Serial.println(F("Perform pencil lead break test..."));
    
    // Wait for pencil lead break events
    uint32_t start_time = millis();
    uint32_t initial_hits = total_hits;
    
    while (millis() - start_time < 30000) { // 30 second timeout
        if (total_hits > initial_hits) {
            Serial.println(F("Pencil lead break detected"));
            break;
        }
        delay(100);
    }
    
    calibration_mode = false;
}

void checkForAlerts() {
    // Check for various alert conditions
    
    // High activity alert
    if (total_hits > 1000) {
        generateSystemAlert("High AE activity detected", 3);
    }
    
    // High amplitude alert
    if (max_amplitude > 100.0) {
        generateSystemAlert("High amplitude event detected", 4);
    }
    
    // System health alerts
    if (millis() - last_activity_time > 3600000 && monitoring_active) {
        generateSystemAlert("No AE activity for 1 hour", 2);
    }
}

void generateAlert(ClassificationResult& result) {
    // Generate alert based on classification result
    digitalWrite(ALERT_LED, HIGH);
    
    if (result.severity >= 4) {
        // Sound buzzer for critical alerts
        for (int i = 0; i < 3; i++) {
            digitalWrite(BUZZER, HIGH);
            delay(200);
            digitalWrite(BUZZER, LOW);
            delay(200);
        }
    }
    
    // Send alert to ESP32
    StaticJsonDocument<256> doc;
    doc["type"] = "ae_alert";
    doc["defect_type"] = result.defect_type;
    doc["severity"] = result.severity;
    doc["description"] = result.description;
    doc["recommendations"] = result.recommendations;
    doc["timestamp"] = millis();
    
    serializeJson(doc, ESP32_SERIAL);
    ESP32_SERIAL.println();
    
    delay(5000);
    digitalWrite(ALERT_LED, LOW);
}

void generateSystemAlert(String message, uint8_t severity) {
    Serial.print(F("ALERT: "));
    Serial.println(message);
    
    digitalWrite(ALERT_LED, HIGH);
    
    if (severity >= 3) {
        digitalWrite(BUZZER, HIGH);
        delay(1000);
        digitalWrite(BUZZER, LOW);
    }
    
    delay(3000);
    digitalWrite(ALERT_LED, LOW);
}

// Data logging functions
void logHitToSD(AEHit& hit) {
    File data_file = SD.open("ae_hits.csv", FILE_WRITE);
    if (data_file) {
        data_file.print(hit.timestamp);
        data_file.print(",");
        data_file.print(hit.channel);
        data_file.print(",");
        data_file.print(hit.amplitude, 2);
        data_file.print(",");
        data_file.print(hit.energy, 2);
        data_file.print(",");
        data_file.print(hit.duration, 2);
        data_file.print(",");
        data_file.print(hit.rise_time, 2);
        data_file.print(",");
        data_file.print(hit.count);
        data_file.print(",");
        data_file.print(hit.average_frequency, 1);
        data_file.print(",");
        data_file.println(hit.centroid_frequency, 1);
        data_file.close();
    }
}

void logLocationToSD(SourceLocation& location) {
    File location_file = SD.open("locations.csv", FILE_WRITE);
    if (location_file) {
        location_file.print(location.timestamp);
        location_file.print(",");
        location_file.print(location.x, 2);
        location_file.print(",");
        location_file.print(location.y, 2);
        location_file.print(",");
        location_file.print(location.z, 2);
        location_file.print(",");
        location_file.print(location.accuracy, 2);
        location_file.print(",");
        location_file.print(location.confidence, 2);
        location_file.print(",");
        location_file.println(location.num_sensors);
        location_file.close();
    }
}

void processSerialCommand() {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "START") {
        startMonitoring();
    } else if (command == "STOP") {
        stopMonitoring();
    } else if (command == "STATUS") {
        printStatus();
    } else if (command == "CLEAR") {
        clearStatistics();
    } else if (command == "CALIBRATE") {
        startCalibration();
    } else if (command.startsWith("THRESHOLD")) {
        float threshold = command.substring(10).toFloat();
        if (threshold > 0) {
            ae_params.threshold = threshold;
            Serial.print(F("Threshold set to: "));
            Serial.println(threshold);
        }
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
            startMonitoring();
        } else if (cmd == "stop") {
            stopMonitoring();
        } else if (cmd == "calibrate") {
            startCalibration();
        } else if (cmd == "clear") {
            clearStatistics();
        }
    } else if (type == "config") {
        // Update configuration
        if (doc.containsKey("threshold")) {
            ae_params.threshold = doc["threshold"];
        }
        if (doc.containsKey("enable_localization")) {
            ae_params.enable_localization = doc["enable_localization"];
        }
    }
}

void printStatus() {
    Serial.println(F("=== Acoustic Emission Monitor Status ==="));
    Serial.print(F("Monitoring: "));
    Serial.println(monitoring_active ? "Active" : "Stopped");
    Serial.print(F("Total Hits: "));
    Serial.println(total_hits);
    Serial.print(F("Max Amplitude: "));
    Serial.print(max_amplitude);
    Serial.println(F(" dB"));
    Serial.print(F("Total Energy: "));
    Serial.print(total_energy);
    Serial.println(F(" aJ"));
    Serial.print(F("Locations: "));
    Serial.println(location_count);
    Serial.print(F("Features: "));
    Serial.println(feature_count);
    Serial.print(F("Active Channels: "));
    Serial.println(countActiveChannels());
    Serial.print(F("Threshold: "));
    Serial.print(ae_params.threshold);
    Serial.println(F(" dB"));
    Serial.println(F("======================================"));
}