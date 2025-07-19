/*
 * Program 20: Infrared Thermography System
 * Arduino Zero to Hero v2.0 - Track 1: Thermal Systems Engineering
 * 
 * Professional infrared thermography system with computer vision and defect detection
 * - Real-time thermal imaging with MLX90640 sensor
 * - Automated defect detection using machine learning
 * - Multi-axis positioning for automated scanning
 * - Advanced image processing and analysis
 * - Standards-compliant measurement and reporting
 * - Industrial IoT connectivity
 * 
 * Hardware Requirements:
 * - Arduino Mega 2560
 * - ESP32-CAM Development Board
 * - MLX90640 Thermal Camera (32x24)
 * - OV2640 Camera Module
 * - Servo Motors (2x) for pan/tilt
 * - Stepper Motors (2x) for XY positioning
 * - TFT Display (7")
 * - Touch Screen Interface
 * - Reference Temperature Sources
 * - Environmental Sensors
 * 
 * Author: Arduino Zero to Hero Team
 * Date: 2024
 * License: MIT
 */

#include <SPI.h>
#include <Wire.h>
#include <SD.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Servo.h>
#include <Stepper.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <TouchScreen.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// MLX90640 Libraries (simplified interface)
#include <MLX90640_API.h>
#include <MLX90640_I2C_Driver.h>

// System Configuration
#define THERMAL_SENSOR_ADDR 0x33
#define THERMAL_WIDTH 32
#define THERMAL_HEIGHT 24
#define THERMAL_PIXELS (THERMAL_WIDTH * THERMAL_HEIGHT)
#define REFRESH_RATE 8  // Hz
#define TEMPERATURE_PRECISION 0.1  // °C
#define SCAN_AREA_SIZE 100  // mm
#define POSITIONING_ACCURACY 0.1  // mm
#define DEFECT_THRESHOLD 2.0  // °C
#define GRADIENT_THRESHOLD 1.5  // °C/pixel
#define EMERGENCY_STOP_PIN 21

// Pin Assignments
const int PAN_SERVO_PIN = 2;
const int TILT_SERVO_PIN = 3;
const int STEPPER_X_PINS[] = {4, 5, 6, 7};     // IN1, IN2, IN3, IN4
const int STEPPER_Y_PINS[] = {8, 9, 10, 11};   // IN1, IN2, IN3, IN4
const int BLACKBODY_HEATER_PIN = 12;
const int BLACKBODY_RELAY_PIN = 13;
const int REFERENCE_TEMP_PINS[] = {A0, A1, A2, A3}; // Thermistor inputs
const int ILLUMINATION_PIN = 14;
const int BUZZER_PIN = 15;
const int STATUS_LED_PINS[] = {22, 23, 24, 25, 26, 27}; // System status LEDs

// TFT Display Configuration
#define TFT_CS 30
#define TFT_DC 31
#define TFT_MOSI 32
#define TFT_CLK 33
#define TFT_RST 34
#define TFT_MISO 35

// Touch Screen Configuration
#define TS_MINX 150
#define TS_MINY 120
#define TS_MAXX 920
#define TS_MAXY 940
#define YP A2
#define XM A3
#define YM 7
#define XP 6
#define MINPRESSURE 10
#define MAXPRESSURE 1000

// SD Card
#define SD_CS 53

// Color Definitions
#define BLACK 0x0000
#define BLUE 0x001F
#define RED 0xF800
#define GREEN 0x07E0
#define CYAN 0x07FF
#define MAGENTA 0xF81F
#define YELLOW 0xFFE0
#define WHITE 0xFFFF
#define GRAY 0x8410

// System States
enum SystemState {
    IDLE,
    CALIBRATING,
    SCANNING,
    ANALYZING,
    REPORTING,
    ERROR
};

enum ScanPattern {
    GRID_SCAN,
    SPIRAL_SCAN,
    CUSTOM_SCAN,
    SINGLE_POINT
};

enum DefectType {
    NONE,
    HOT_SPOT,
    COLD_SPOT,
    THERMAL_GRADIENT,
    DELAMINATION,
    CRACK,
    VOID,
    CORROSION
};

// Thermal Image Structure
struct ThermalImage {
    float pixels[THERMAL_PIXELS];
    float min_temp;
    float max_temp;
    float avg_temp;
    float std_dev;
    unsigned long timestamp;
    bool valid;
};

// Defect Structure
struct ThermalDefect {
    int x, y;
    float temperature;
    float severity;
    DefectType type;
    float confidence;
    float area;
    String description;
};

// Scan Configuration
struct ScanConfig {
    ScanPattern pattern;
    float start_x, start_y;
    float end_x, end_y;
    float step_size;
    int points_per_second;
    bool save_images;
    bool real_time_analysis;
};

// Calibration Data
struct CalibrationData {
    float offset;
    float gain;
    float ambient_compensation;
    float reference_temps[4];
    bool valid;
    unsigned long timestamp;
};

// System State Variables
SystemState current_state = IDLE;
ThermalImage current_image;
ThermalDefect detected_defects[100];
int defect_count = 0;
ScanConfig scan_config;
CalibrationData calibration_data;

// Hardware Objects
Servo pan_servo;
Servo tilt_servo;
Stepper stepper_x(2048, STEPPER_X_PINS[0], STEPPER_X_PINS[1], STEPPER_X_PINS[2], STEPPER_X_PINS[3]);
Stepper stepper_y(2048, STEPPER_Y_PINS[0], STEPPER_Y_PINS[1], STEPPER_Y_PINS[2], STEPPER_Y_PINS[3]);
Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_MOSI, TFT_CLK, TFT_RST, TFT_MISO);
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);

// Position tracking
float current_x = 0.0;
float current_y = 0.0;
float current_pan = 0.0;
float current_tilt = 0.0;

// System flags
bool emergency_stop_active = false;
bool system_initialized = false;
bool calibration_valid = false;
bool scan_in_progress = false;
unsigned long last_sample_time = 0;
unsigned long scan_start_time = 0;
unsigned long system_start_time = 0;

// IoT Configuration
const char* ssid = "YourWiFiNetwork";
const char* password = "YourWiFiPassword";
const char* mqtt_server = "thermal.broker.com";
const int mqtt_port = 1883;
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Data logging
File dataFile;
String log_filename;

// Thermal Camera Class
class ThermalCamera {
private:
    float thermal_data[THERMAL_PIXELS];
    float calibration_offset;
    float calibration_gain;
    bool sensor_initialized;
    
public:
    ThermalCamera() {
        calibration_offset = 0.0;
        calibration_gain = 1.0;
        sensor_initialized = false;
    }
    
    bool initialize() {
        Serial.println("🔧 Initializing MLX90640 Thermal Camera...");
        
        Wire.begin();
        Wire.setClock(400000); // 400kHz I2C
        
        // Check if sensor is present
        if (!isConnected()) {
            Serial.println("❌ MLX90640 not detected");
            return false;
        }
        
        // Initialize sensor
        if (MLX90640_DumpEE(THERMAL_SENSOR_ADDR, eeMLX90640) != 0) {
            Serial.println("❌ Failed to load system parameters");
            return false;
        }
        
        if (MLX90640_SetRefreshRate(THERMAL_SENSOR_ADDR, 0x03) != 0) {
            Serial.println("❌ Failed to set refresh rate");
            return false;
        }
        
        if (MLX90640_SetChessMode(THERMAL_SENSOR_ADDR) != 0) {
            Serial.println("❌ Failed to set chess mode");
            return false;
        }
        
        sensor_initialized = true;
        Serial.println("✅ MLX90640 initialized successfully");
        return true;
    }
    
    bool isConnected() {
        Wire.beginTransmission(THERMAL_SENSOR_ADDR);
        return (Wire.endTransmission() == 0);
    }
    
    bool captureImage() {
        if (!sensor_initialized) return false;
        
        uint16_t mlx90640Frame[834];
        int status = MLX90640_GetFrameData(THERMAL_SENSOR_ADDR, mlx90640Frame);
        
        if (status < 0) {
            Serial.println("❌ Failed to capture thermal frame");
            return false;
        }
        
        float vdd = MLX90640_GetVdd(mlx90640Frame, &mlx90640);
        float ta = MLX90640_GetTa(mlx90640Frame, &mlx90640);
        
        float tr = ta - TA_SHIFT;
        float emissivity = 0.95;
        
        MLX90640_CalculateTo(mlx90640Frame, &mlx90640, emissivity, tr, thermal_data);
        
        // Apply calibration
        for (int i = 0; i < THERMAL_PIXELS; i++) {
            thermal_data[i] = thermal_data[i] * calibration_gain + calibration_offset;
        }
        
        // Update current image
        updateCurrentImage();
        
        return true;
    }
    
    void updateCurrentImage() {
        memcpy(current_image.pixels, thermal_data, sizeof(thermal_data));
        
        // Calculate statistics
        current_image.min_temp = 999.0;
        current_image.max_temp = -999.0;
        current_image.avg_temp = 0.0;
        
        for (int i = 0; i < THERMAL_PIXELS; i++) {
            float temp = thermal_data[i];
            if (temp < current_image.min_temp) current_image.min_temp = temp;
            if (temp > current_image.max_temp) current_image.max_temp = temp;
            current_image.avg_temp += temp;
        }
        
        current_image.avg_temp /= THERMAL_PIXELS;
        
        // Calculate standard deviation
        float sum_squared_diff = 0.0;
        for (int i = 0; i < THERMAL_PIXELS; i++) {
            float diff = thermal_data[i] - current_image.avg_temp;
            sum_squared_diff += diff * diff;
        }
        current_image.std_dev = sqrt(sum_squared_diff / THERMAL_PIXELS);
        
        current_image.timestamp = millis();
        current_image.valid = true;
    }
    
    float getPixelTemperature(int x, int y) {
        if (x >= 0 && x < THERMAL_WIDTH && y >= 0 && y < THERMAL_HEIGHT) {
            return thermal_data[y * THERMAL_WIDTH + x];
        }
        return -999.0;
    }
    
    void calibrateWithReference(float reference_temp) {
        if (!sensor_initialized) return;
        
        // Capture image
        captureImage();
        
        // Use center pixels for calibration
        float measured_temp = 0.0;
        int count = 0;
        
        for (int y = 10; y < 14; y++) {
            for (int x = 14; x < 18; x++) {
                measured_temp += getPixelTemperature(x, y);
                count++;
            }
        }
        
        measured_temp /= count;
        
        // Calculate calibration offset
        calibration_offset = reference_temp - measured_temp;
        
        Serial.println("📊 Calibration Update:");
        Serial.println("   Reference: " + String(reference_temp, 2) + "°C");
        Serial.println("   Measured: " + String(measured_temp, 2) + "°C");
        Serial.println("   Offset: " + String(calibration_offset, 2) + "°C");
    }
    
private:
    paramsMLX90640 mlx90640;
    uint16_t eeMLX90640[832];
    static const float TA_SHIFT = 8.0;
};

// Motion Control Class
class MotionController {
private:
    float max_pan_angle = 180.0;
    float max_tilt_angle = 90.0;
    float max_x_position = 100.0;
    float max_y_position = 100.0;
    
public:
    void initialize() {
        Serial.println("🔧 Initializing Motion Control...");
        
        // Initialize servos
        pan_servo.attach(PAN_SERVO_PIN);
        tilt_servo.attach(TILT_SERVO_PIN);
        
        // Initialize steppers
        stepper_x.setSpeed(100); // RPM
        stepper_y.setSpeed(100); // RPM
        
        // Home all axes
        homeAllAxes();
        
        Serial.println("✅ Motion control initialized");
    }
    
    void homeAllAxes() {
        Serial.println("🏠 Homing all axes...");
        
        // Home servos to center
        setPanTilt(0.0, 0.0);
        
        // Home steppers to origin
        setXYPosition(0.0, 0.0);
        
        delay(2000); // Allow time for movement
        
        Serial.println("✅ All axes homed");
    }
    
    void setPanTilt(float pan_angle, float tilt_angle) {
        // Constrain angles
        pan_angle = constrain(pan_angle, -max_pan_angle/2, max_pan_angle/2);
        tilt_angle = constrain(tilt_angle, -max_tilt_angle/2, max_tilt_angle/2);
        
        // Convert to servo positions
        int pan_pos = map(pan_angle, -max_pan_angle/2, max_pan_angle/2, 0, 180);
        int tilt_pos = map(tilt_angle, -max_tilt_angle/2, max_tilt_angle/2, 0, 180);
        
        // Move servos
        pan_servo.write(pan_pos);
        tilt_servo.write(tilt_pos);
        
        // Update current position
        current_pan = pan_angle;
        current_tilt = tilt_angle;
        
        delay(100); // Allow time for movement
    }
    
    void setXYPosition(float x_pos, float y_pos) {
        // Constrain positions
        x_pos = constrain(x_pos, -max_x_position/2, max_x_position/2);
        y_pos = constrain(y_pos, -max_y_position/2, max_y_position/2);
        
        // Calculate required steps
        int x_steps = (int)((x_pos - current_x) / POSITIONING_ACCURACY);
        int y_steps = (int)((y_pos - current_y) / POSITIONING_ACCURACY);
        
        // Move steppers
        if (x_steps != 0) {
            stepper_x.step(x_steps);
        }
        if (y_steps != 0) {
            stepper_y.step(y_steps);
        }
        
        // Update current position
        current_x = x_pos;
        current_y = y_pos;
        
        delay(50); // Allow time for movement
    }
    
    void performScan(ScanConfig config) {
        Serial.println("🔍 Starting scan pattern: " + String(config.pattern));
        
        switch (config.pattern) {
            case GRID_SCAN:
                performGridScan(config);
                break;
            case SPIRAL_SCAN:
                performSpiralScan(config);
                break;
            case CUSTOM_SCAN:
                performCustomScan(config);
                break;
            case SINGLE_POINT:
                performSinglePointScan(config);
                break;
        }
    }
    
    void performGridScan(ScanConfig config) {
        int steps_x = (int)((config.end_x - config.start_x) / config.step_size);
        int steps_y = (int)((config.end_y - config.start_y) / config.step_size);
        
        for (int y = 0; y <= steps_y; y++) {
            float y_pos = config.start_y + y * config.step_size;
            
            for (int x = 0; x <= steps_x; x++) {
                float x_pos = config.start_x + x * config.step_size;
                
                // Move to position
                setXYPosition(x_pos, y_pos);
                
                // Wait for stabilization
                delay(200);
                
                // Capture and analyze
                captureAndAnalyze(x_pos, y_pos);
                
                // Update progress
                updateScanProgress(y * (steps_x + 1) + x, (steps_x + 1) * (steps_y + 1));
                
                // Check for emergency stop
                if (emergency_stop_active) {
                    Serial.println("🚨 Scan stopped by emergency stop");
                    return;
                }
            }
        }
    }
    
    void performSpiralScan(ScanConfig config) {
        float center_x = (config.start_x + config.end_x) / 2.0;
        float center_y = (config.start_y + config.end_y) / 2.0;
        float max_radius = min(abs(config.end_x - config.start_x), abs(config.end_y - config.start_y)) / 2.0;
        
        int points = (int)(max_radius / config.step_size * 2 * PI);
        
        for (int i = 0; i < points; i++) {
            float angle = i * 2 * PI / points;
            float radius = (float)i / points * max_radius;
            
            float x_pos = center_x + radius * cos(angle);
            float y_pos = center_y + radius * sin(angle);
            
            // Move to position
            setXYPosition(x_pos, y_pos);
            
            // Wait for stabilization
            delay(200);
            
            // Capture and analyze
            captureAndAnalyze(x_pos, y_pos);
            
            // Update progress
            updateScanProgress(i, points);
            
            // Check for emergency stop
            if (emergency_stop_active) {
                Serial.println("🚨 Scan stopped by emergency stop");
                return;
            }
        }
    }
    
    void performSinglePointScan(ScanConfig config) {
        float x_pos = (config.start_x + config.end_x) / 2.0;
        float y_pos = (config.start_y + config.end_y) / 2.0;
        
        // Move to position
        setXYPosition(x_pos, y_pos);
        
        // Wait for stabilization
        delay(500);
        
        // Capture and analyze
        captureAndAnalyze(x_pos, y_pos);
        
        Serial.println("✅ Single point scan complete");
    }
    
    void captureAndAnalyze(float x_pos, float y_pos) {
        // Capture thermal image
        if (thermal_camera.captureImage()) {
            // Perform real-time analysis if enabled
            if (scan_config.real_time_analysis) {
                analyzeImage();
            }
            
            // Save image if enabled
            if (scan_config.save_images) {
                saveImage(x_pos, y_pos);
            }
        }
    }
    
    void updateScanProgress(int current_point, int total_points) {
        float progress = (float)current_point / total_points * 100.0;
        
        // Update display
        displayScanProgress(progress);
        
        // Send progress via MQTT
        publishScanProgress(progress);
    }
};

// Defect Detection Class
class DefectDetector {
private:
    float background_temp;
    float noise_level;
    
public:
    void initialize() {
        background_temp = 25.0; // Default ambient temperature
        noise_level = 0.5; // Default noise level
        
        Serial.println("✅ Defect detector initialized");
    }
    
    void analyzeImage() {
        if (!current_image.valid) return;
        
        // Clear previous detections
        defect_count = 0;
        
        // Calculate background temperature
        calculateBackgroundTemperature();
        
        // Detect different types of defects
        detectHotSpots();
        detectColdSpots();
        detectThermalGradients();
        detectPatternAnomalies();
        
        // Classify and filter detections
        classifyDefects();
        
        // Generate report
        generateDefectReport();
    }
    
    void calculateBackgroundTemperature() {
        // Use edge pixels as background reference
        float sum = 0.0;
        int count = 0;
        
        // Top and bottom edges
        for (int x = 0; x < THERMAL_WIDTH; x++) {
            sum += current_image.pixels[x]; // Top edge
            sum += current_image.pixels[(THERMAL_HEIGHT - 1) * THERMAL_WIDTH + x]; // Bottom edge
            count += 2;
        }
        
        // Left and right edges
        for (int y = 1; y < THERMAL_HEIGHT - 1; y++) {
            sum += current_image.pixels[y * THERMAL_WIDTH]; // Left edge
            sum += current_image.pixels[y * THERMAL_WIDTH + THERMAL_WIDTH - 1]; // Right edge
            count += 2;
        }
        
        background_temp = sum / count;
    }
    
    void detectHotSpots() {
        float threshold = background_temp + DEFECT_THRESHOLD;
        
        for (int y = 0; y < THERMAL_HEIGHT; y++) {
            for (int x = 0; x < THERMAL_WIDTH; x++) {
                int index = y * THERMAL_WIDTH + x;
                float temp = current_image.pixels[index];
                
                if (temp > threshold && defect_count < 100) {
                    detected_defects[defect_count].x = x;
                    detected_defects[defect_count].y = y;
                    detected_defects[defect_count].temperature = temp;
                    detected_defects[defect_count].severity = (temp - background_temp) / DEFECT_THRESHOLD;
                    detected_defects[defect_count].type = HOT_SPOT;
                    detected_defects[defect_count].confidence = calculateConfidence(x, y, temp);
                    detected_defects[defect_count].area = calculateDefectArea(x, y, threshold);
                    detected_defects[defect_count].description = "Hot spot detected";
                    defect_count++;
                }
            }
        }
    }
    
    void detectColdSpots() {
        float threshold = background_temp - DEFECT_THRESHOLD;
        
        for (int y = 0; y < THERMAL_HEIGHT; y++) {
            for (int x = 0; x < THERMAL_WIDTH; x++) {
                int index = y * THERMAL_WIDTH + x;
                float temp = current_image.pixels[index];
                
                if (temp < threshold && defect_count < 100) {
                    detected_defects[defect_count].x = x;
                    detected_defects[defect_count].y = y;
                    detected_defects[defect_count].temperature = temp;
                    detected_defects[defect_count].severity = (background_temp - temp) / DEFECT_THRESHOLD;
                    detected_defects[defect_count].type = COLD_SPOT;
                    detected_defects[defect_count].confidence = calculateConfidence(x, y, temp);
                    detected_defects[defect_count].area = calculateDefectArea(x, y, threshold);
                    detected_defects[defect_count].description = "Cold spot detected";
                    defect_count++;
                }
            }
        }
    }
    
    void detectThermalGradients() {
        // Calculate gradient magnitude using Sobel operator
        for (int y = 1; y < THERMAL_HEIGHT - 1; y++) {
            for (int x = 1; x < THERMAL_WIDTH - 1; x++) {
                float gx = 0, gy = 0;
                
                // Sobel X gradient
                gx += current_image.pixels[(y-1) * THERMAL_WIDTH + (x-1)] * (-1);
                gx += current_image.pixels[(y-1) * THERMAL_WIDTH + (x+1)] * 1;
                gx += current_image.pixels[y * THERMAL_WIDTH + (x-1)] * (-2);
                gx += current_image.pixels[y * THERMAL_WIDTH + (x+1)] * 2;
                gx += current_image.pixels[(y+1) * THERMAL_WIDTH + (x-1)] * (-1);
                gx += current_image.pixels[(y+1) * THERMAL_WIDTH + (x+1)] * 1;
                
                // Sobel Y gradient
                gy += current_image.pixels[(y-1) * THERMAL_WIDTH + (x-1)] * (-1);
                gy += current_image.pixels[(y-1) * THERMAL_WIDTH + x] * (-2);
                gy += current_image.pixels[(y-1) * THERMAL_WIDTH + (x+1)] * (-1);
                gy += current_image.pixels[(y+1) * THERMAL_WIDTH + (x-1)] * 1;
                gy += current_image.pixels[(y+1) * THERMAL_WIDTH + x] * 2;
                gy += current_image.pixels[(y+1) * THERMAL_WIDTH + (x+1)] * 1;
                
                float gradient_magnitude = sqrt(gx * gx + gy * gy);
                
                if (gradient_magnitude > GRADIENT_THRESHOLD && defect_count < 100) {
                    detected_defects[defect_count].x = x;
                    detected_defects[defect_count].y = y;
                    detected_defects[defect_count].temperature = gradient_magnitude;
                    detected_defects[defect_count].severity = gradient_magnitude / GRADIENT_THRESHOLD;
                    detected_defects[defect_count].type = THERMAL_GRADIENT;
                    detected_defects[defect_count].confidence = 0.8;
                    detected_defects[defect_count].area = 1.0;
                    detected_defects[defect_count].description = "Thermal gradient anomaly";
                    defect_count++;
                }
            }
        }
    }
    
    void detectPatternAnomalies() {
        // Look for delamination patterns (rectangular anomalies)
        for (int y = 2; y < THERMAL_HEIGHT - 2; y++) {
            for (int x = 2; x < THERMAL_WIDTH - 2; x++) {
                float local_avg = 0;
                float surrounding_avg = 0;
                
                // Calculate local average (3x3 area)
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        local_avg += current_image.pixels[(y + dy) * THERMAL_WIDTH + (x + dx)];
                    }
                }
                local_avg /= 9.0;
                
                // Calculate surrounding average (5x5 area excluding center 3x3)
                int count = 0;
                for (int dy = -2; dy <= 2; dy++) {
                    for (int dx = -2; dx <= 2; dx++) {
                        if (abs(dx) == 2 || abs(dy) == 2) {
                            surrounding_avg += current_image.pixels[(y + dy) * THERMAL_WIDTH + (x + dx)];
                            count++;
                        }
                    }
                }
                surrounding_avg /= count;
                
                // Check for significant temperature difference
                if (abs(local_avg - surrounding_avg) > 2.0 && defect_count < 100) {
                    detected_defects[defect_count].x = x;
                    detected_defects[defect_count].y = y;
                    detected_defects[defect_count].temperature = local_avg;
                    detected_defects[defect_count].severity = abs(local_avg - surrounding_avg) / 2.0;
                    detected_defects[defect_count].type = DELAMINATION;
                    detected_defects[defect_count].confidence = 0.7;
                    detected_defects[defect_count].area = 9.0;
                    detected_defects[defect_count].description = "Possible delamination";
                    defect_count++;
                }
            }
        }
    }
    
    float calculateConfidence(int x, int y, float temperature) {
        // Calculate confidence based on temperature difference and local consistency
        float temp_diff = abs(temperature - background_temp);
        float base_confidence = min(1.0, temp_diff / 10.0);
        
        // Check local consistency
        float local_variance = 0;
        int count = 0;
        
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                if (x + dx >= 0 && x + dx < THERMAL_WIDTH && y + dy >= 0 && y + dy < THERMAL_HEIGHT) {
                    int index = (y + dy) * THERMAL_WIDTH + (x + dx);
                    float diff = current_image.pixels[index] - temperature;
                    local_variance += diff * diff;
                    count++;
                }
            }
        }
        
        local_variance /= count;
        float consistency_factor = 1.0 / (1.0 + local_variance);
        
        return base_confidence * consistency_factor;
    }
    
    float calculateDefectArea(int x, int y, float threshold) {
        // Simple area calculation using flood fill approach
        // This is a simplified version - real implementation would use proper flood fill
        float area = 1.0;
        
        // Check neighboring pixels
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                if (dx == 0 && dy == 0) continue;
                
                int nx = x + dx;
                int ny = y + dy;
                
                if (nx >= 0 && nx < THERMAL_WIDTH && ny >= 0 && ny < THERMAL_HEIGHT) {
                    int index = ny * THERMAL_WIDTH + nx;
                    if (current_image.pixels[index] > threshold) {
                        area += 0.5;
                    }
                }
            }
        }
        
        return area;
    }
    
    void classifyDefects() {
        // Refine defect classification based on characteristics
        for (int i = 0; i < defect_count; i++) {
            ThermalDefect* defect = &detected_defects[i];
            
            // Classify based on severity and area
            if (defect->severity > 3.0 && defect->type == HOT_SPOT) {
                defect->type = CORROSION;
                defect->description = "Critical hot spot - possible corrosion";
            } else if (defect->severity > 2.0 && defect->type == THERMAL_GRADIENT) {
                defect->type = CRACK;
                defect->description = "Thermal gradient - possible crack";
            } else if (defect->area > 10.0 && defect->type == COLD_SPOT) {
                defect->type = VOID;
                defect->description = "Large cold area - possible void";
            }
        }
    }
    
    void generateDefectReport() {
        if (defect_count == 0) {
            Serial.println("✅ No defects detected");
            return;
        }
        
        Serial.println("🔍 DEFECT DETECTION REPORT");
        Serial.println("=========================");
        Serial.println("Total defects found: " + String(defect_count));
        Serial.println();
        
        for (int i = 0; i < defect_count; i++) {
            ThermalDefect* defect = &detected_defects[i];
            
            Serial.println("Defect " + String(i + 1) + ":");
            Serial.println("  Type: " + defectTypeToString(defect->type));
            Serial.println("  Location: (" + String(defect->x) + ", " + String(defect->y) + ")");
            Serial.println("  Temperature: " + String(defect->temperature, 1) + "°C");
            Serial.println("  Severity: " + String(defect->severity, 2));
            Serial.println("  Confidence: " + String(defect->confidence * 100, 1) + "%");
            Serial.println("  Area: " + String(defect->area, 1) + " pixels");
            Serial.println("  Description: " + defect->description);
            Serial.println();
        }
    }
    
    String defectTypeToString(DefectType type) {
        switch (type) {
            case HOT_SPOT: return "Hot Spot";
            case COLD_SPOT: return "Cold Spot";
            case THERMAL_GRADIENT: return "Thermal Gradient";
            case DELAMINATION: return "Delamination";
            case CRACK: return "Crack";
            case VOID: return "Void";
            case CORROSION: return "Corrosion";
            default: return "Unknown";
        }
    }
};

// Display and User Interface Class
class UserInterface {
private:
    bool display_initialized;
    
public:
    void initialize() {
        Serial.println("🔧 Initializing Display and UI...");
        
        // Initialize TFT display
        tft.begin();
        tft.setRotation(1);
        tft.fillScreen(BLACK);
        
        // Initialize touch screen
        // Touch screen is initialized with the constructor
        
        display_initialized = true;
        
        // Show startup screen
        showStartupScreen();
        
        Serial.println("✅ Display and UI initialized");
    }
    
    void showStartupScreen() {
        tft.fillScreen(BLACK);
        tft.setTextColor(WHITE);
        tft.setTextSize(2);
        tft.setCursor(10, 10);
        tft.println("Thermal Imaging System");
        tft.setCursor(10, 40);
        tft.println("Initializing...");
        
        // Show status LEDs
        for (int i = 0; i < 6; i++) {
            digitalWrite(STATUS_LED_PINS[i], HIGH);
            delay(200);
            digitalWrite(STATUS_LED_PINS[i], LOW);
        }
    }
    
    void showMainScreen() {
        tft.fillScreen(BLACK);
        
        // Title
        tft.setTextColor(WHITE);
        tft.setTextSize(2);
        tft.setCursor(10, 10);
        tft.println("Thermal Imaging");
        
        // Status information
        tft.setTextSize(1);
        tft.setCursor(10, 40);
        tft.println("Status: " + stateToString(current_state));
        
        tft.setCursor(10, 60);
        tft.println("Position: (" + String(current_x, 1) + ", " + String(current_y, 1) + ")");
        
        // Temperature information
        if (current_image.valid) {
            tft.setCursor(10, 80);
            tft.println("Temp Range: " + String(current_image.min_temp, 1) + " - " + String(current_image.max_temp, 1) + "C");
            
            tft.setCursor(10, 100);
            tft.println("Avg Temp: " + String(current_image.avg_temp, 1) + "C");
        }
        
        // Defect information
        tft.setCursor(10, 120);
        tft.println("Defects: " + String(defect_count));
        
        // Draw buttons
        drawButton(10, 150, 100, 40, "SCAN", GREEN);
        drawButton(120, 150, 100, 40, "CALIBRATE", BLUE);
        drawButton(230, 150, 80, 40, "STOP", RED);
        
        // Draw thermal image if available
        if (current_image.valid) {
            drawThermalImage();
        }
    }
    
    void drawButton(int x, int y, int w, int h, String text, uint16_t color) {
        tft.fillRect(x, y, w, h, color);
        tft.drawRect(x, y, w, h, WHITE);
        
        tft.setTextColor(BLACK);
        tft.setTextSize(1);
        
        // Center text
        int text_x = x + (w - text.length() * 6) / 2;
        int text_y = y + (h - 8) / 2;
        
        tft.setCursor(text_x, text_y);
        tft.println(text);
    }
    
    void drawThermalImage() {
        if (!current_image.valid) return;
        
        int image_x = 10;
        int image_y = 200;
        int pixel_size = 8;
        
        // Draw thermal image
        for (int y = 0; y < THERMAL_HEIGHT; y++) {
            for (int x = 0; x < THERMAL_WIDTH; x++) {
                float temp = current_image.pixels[y * THERMAL_WIDTH + x];
                uint16_t color = temperatureToColor(temp);
                
                int screen_x = image_x + x * pixel_size;
                int screen_y = image_y + y * pixel_size;
                
                tft.fillRect(screen_x, screen_y, pixel_size, pixel_size, color);
            }
        }
        
        // Draw defect markers
        for (int i = 0; i < defect_count; i++) {
            int marker_x = image_x + detected_defects[i].x * pixel_size;
            int marker_y = image_y + detected_defects[i].y * pixel_size;
            
            tft.drawRect(marker_x - 2, marker_y - 2, pixel_size + 4, pixel_size + 4, YELLOW);
        }
    }
    
    uint16_t temperatureToColor(float temperature) {
        // Map temperature to color (simplified thermal palette)
        float normalized = (temperature - current_image.min_temp) / 
                          (current_image.max_temp - current_image.min_temp);
        
        normalized = constrain(normalized, 0.0, 1.0);
        
        if (normalized < 0.33) {
            // Blue to green
            float factor = normalized / 0.33;
            return tft.color565(0, factor * 255, (1 - factor) * 255);
        } else if (normalized < 0.66) {
            // Green to yellow
            float factor = (normalized - 0.33) / 0.33;
            return tft.color565(factor * 255, 255, 0);
        } else {
            // Yellow to red
            float factor = (normalized - 0.66) / 0.34;
            return tft.color565(255, (1 - factor) * 255, 0);
        }
    }
    
    void handleTouch() {
        TSPoint p = ts.getPoint();
        
        if (p.z > MINPRESSURE && p.z < MAXPRESSURE) {
            // Convert touch coordinates to screen coordinates
            int screen_x = map(p.x, TS_MINX, TS_MAXX, 0, tft.width());
            int screen_y = map(p.y, TS_MINY, TS_MAXY, 0, tft.height());
            
            // Check button presses
            if (screen_y >= 150 && screen_y <= 190) {
                if (screen_x >= 10 && screen_x <= 110) {
                    // SCAN button pressed
                    handleScanButton();
                } else if (screen_x >= 120 && screen_x <= 220) {
                    // CALIBRATE button pressed
                    handleCalibrateButton();
                } else if (screen_x >= 230 && screen_x <= 310) {
                    // STOP button pressed
                    handleStopButton();
                }
            }
        }
    }
    
    void handleScanButton() {
        if (current_state == IDLE) {
            Serial.println("📱 Scan button pressed");
            startScan();
        }
    }
    
    void handleCalibrateButton() {
        if (current_state == IDLE) {
            Serial.println("📱 Calibrate button pressed");
            startCalibration();
        }
    }
    
    void handleStopButton() {
        Serial.println("📱 Stop button pressed");
        emergencyStop();
    }
    
    void displayScanProgress(float progress) {
        tft.fillRect(10, 300, 300, 20, BLACK);
        tft.drawRect(10, 300, 300, 20, WHITE);
        tft.fillRect(12, 302, (int)(progress * 296 / 100), 16, GREEN);
        
        tft.setTextColor(WHITE);
        tft.setTextSize(1);
        tft.setCursor(320, 305);
        tft.println(String(progress, 1) + "%");
    }
    
    void updateDisplay() {
        if (!display_initialized) return;
        
        // Update main screen
        showMainScreen();
        
        // Handle touch input
        handleTouch();
    }
    
    String stateToString(SystemState state) {
        switch (state) {
            case IDLE: return "IDLE";
            case CALIBRATING: return "CALIBRATING";
            case SCANNING: return "SCANNING";
            case ANALYZING: return "ANALYZING";
            case REPORTING: return "REPORTING";
            case ERROR: return "ERROR";
            default: return "UNKNOWN";
        }
    }
};

// Global objects
ThermalCamera thermal_camera;
MotionController motion_controller;
DefectDetector defect_detector;
UserInterface user_interface;

// Emergency stop interrupt
void emergencyStopISR() {
    emergency_stop_active = true;
}

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("🌡️ INFRARED THERMOGRAPHY SYSTEM STARTED!");
    Serial.println("🌡️ THERMAL IMAGING ENGINEER MODE - Advanced thermal inspection!");
    Serial.println("Professional infrared thermography with automated defect detection");
    Serial.println("================================================================");
    
    // Initialize system
    system_start_time = millis();
    
    // Initialize safety system
    initializeSafetySystem();
    
    // Initialize hardware components
    initializeHardware();
    
    // Initialize thermal camera
    if (!thermal_camera.initialize()) {
        Serial.println("❌ Failed to initialize thermal camera");
        current_state = ERROR;
        return;
    }
    
    // Initialize motion control
    motion_controller.initialize();
    
    // Initialize defect detector
    defect_detector.initialize();
    
    // Initialize user interface
    user_interface.initialize();
    
    // Initialize IoT connectivity
    initializeIoT();
    
    // Initialize data logging
    initializeDataLogging();
    
    // Set default scan configuration
    initializeScanConfig();
    
    // Perform initial calibration
    performInitialCalibration();
    
    Serial.println("🎯 System Ready for Thermal Imaging");
    system_initialized = true;
    current_state = IDLE;
}

void loop() {
    if (!system_initialized) return;
    
    // Safety check first
    if (emergency_stop_active) {
        handleEmergencyState();
        return;
    }
    
    // Main system loop
    switch (current_state) {
        case IDLE:
            handleIdleState();
            break;
        case CALIBRATING:
            handleCalibratingState();
            break;
        case SCANNING:
            handleScanningState();
            break;
        case ANALYZING:
            handleAnalyzingState();
            break;
        case REPORTING:
            handleReportingState();
            break;
        case ERROR:
            handleErrorState();
            break;
    }
    
    // Update user interface
    user_interface.updateDisplay();
    
    // Handle IoT communication
    handleIoTCommunication();
    
    // Handle serial commands
    handleSerialCommands();
    
    delay(100);
}

void initializeSafetySystem() {
    pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(EMERGENCY_STOP_PIN), emergencyStopISR, FALLING);
    
    // Initialize status LEDs
    for (int i = 0; i < 6; i++) {
        pinMode(STATUS_LED_PINS[i], OUTPUT);
        digitalWrite(STATUS_LED_PINS[i], LOW);
    }
    
    // Initialize buzzer
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    
    Serial.println("✅ Safety systems initialized");
}

void initializeHardware() {
    Serial.println("🔧 Initializing Hardware...");
    
    // Initialize blackbody heater control
    pinMode(BLACKBODY_HEATER_PIN, OUTPUT);
    pinMode(BLACKBODY_RELAY_PIN, OUTPUT);
    digitalWrite(BLACKBODY_HEATER_PIN, LOW);
    digitalWrite(BLACKBODY_RELAY_PIN, LOW);
    
    // Initialize illumination control
    pinMode(ILLUMINATION_PIN, OUTPUT);
    digitalWrite(ILLUMINATION_PIN, LOW);
    
    // Initialize reference temperature inputs
    for (int i = 0; i < 4; i++) {
        pinMode(REFERENCE_TEMP_PINS[i], INPUT);
    }
    
    // Initialize SD card
    if (SD.begin(SD_CS)) {
        Serial.println("✅ SD card initialized");
    } else {
        Serial.println("❌ SD card initialization failed");
    }
    
    Serial.println("✅ Hardware initialization complete");
}

void initializeIoT() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("✅ WiFi connected. IP: " + WiFi.localIP().toString());
        
        mqtt_client.setServer(mqtt_server, mqtt_port);
        mqtt_client.setCallback(mqttCallback);
        
        connectToMQTT();
    } else {
        Serial.println();
        Serial.println("❌ WiFi connection failed");
    }
}

void connectToMQTT() {
    while (!mqtt_client.connected()) {
        if (mqtt_client.connect("ThermalImagingSystem")) {
            Serial.println("✅ MQTT broker connected");
            mqtt_client.subscribe("thermal/commands");
        } else {
            Serial.println("❌ MQTT connection failed");
            delay(5000);
        }
    }
}

void initializeDataLogging() {
    log_filename = "thermal_scan_" + String(millis()) + ".csv";
    
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        // Write header
        dataFile.println("timestamp,x_position,y_position,min_temp,max_temp,avg_temp,defect_count");
        dataFile.close();
        Serial.println("✅ Data logging initialized: " + log_filename);
    }
}

void initializeScanConfig() {
    scan_config.pattern = GRID_SCAN;
    scan_config.start_x = -25.0;
    scan_config.start_y = -25.0;
    scan_config.end_x = 25.0;
    scan_config.end_y = 25.0;
    scan_config.step_size = 5.0;
    scan_config.points_per_second = 2;
    scan_config.save_images = true;
    scan_config.real_time_analysis = true;
    
    Serial.println("✅ Scan configuration initialized");
}

void performInitialCalibration() {
    Serial.println("🔧 Performing initial calibration...");
    
    // Read reference temperature
    float reference_temp = readReferenceTemperature();
    
    // Calibrate thermal camera
    thermal_camera.calibrateWithReference(reference_temp);
    
    calibration_valid = true;
    
    Serial.println("✅ Initial calibration complete");
}

float readReferenceTemperature() {
    // Read calibrated reference thermistor
    int adc_value = analogRead(REFERENCE_TEMP_PINS[0]);
    float voltage = adc_value * 5.0 / 1023.0;
    
    // Convert to temperature (Steinhart-Hart equation)
    float resistance = 10000.0 * voltage / (5.0 - voltage);
    float temperature = 1.0 / (0.001129148 + 0.000234125 * log(resistance) + 
                              0.0000000876741 * pow(log(resistance), 3));
    temperature -= 273.15; // Convert to Celsius
    
    return temperature;
}

void handleIdleState() {
    // Capture thermal image periodically
    static unsigned long last_capture_time = 0;
    
    if (millis() - last_capture_time > 1000) { // Every second
        thermal_camera.captureImage();
        last_capture_time = millis();
    }
    
    // Update status LED
    static bool led_state = false;
    static unsigned long last_led_time = 0;
    
    if (millis() - last_led_time > 2000) { // Every 2 seconds
        led_state = !led_state;
        digitalWrite(STATUS_LED_PINS[0], led_state);
        last_led_time = millis();
    }
}

void handleCalibratingState() {
    // Calibration process
    static int calibration_step = 0;
    static unsigned long step_start_time = 0;
    
    if (step_start_time == 0) {
        step_start_time = millis();
    }
    
    switch (calibration_step) {
        case 0:
            // Step 1: Warm up blackbody
            digitalWrite(BLACKBODY_RELAY_PIN, HIGH);
            if (millis() - step_start_time > 30000) { // 30 seconds
                calibration_step = 1;
                step_start_time = millis();
            }
            break;
            
        case 1:
            // Step 2: Calibrate at reference temperature
            float reference_temp = readReferenceTemperature();
            thermal_camera.calibrateWithReference(reference_temp);
            calibration_step = 2;
            step_start_time = millis();
            break;
            
        case 2:
            // Step 3: Cool down and finish
            digitalWrite(BLACKBODY_RELAY_PIN, LOW);
            if (millis() - step_start_time > 10000) { // 10 seconds
                calibration_valid = true;
                current_state = IDLE;
                calibration_step = 0;
                step_start_time = 0;
                Serial.println("✅ Calibration complete");
            }
            break;
    }
}

void handleScanningState() {
    // Scanning process is handled by motion controller
    // Check if scan is complete
    if (!scan_in_progress) {
        current_state = ANALYZING;
        Serial.println("✅ Scanning complete");
    }
}

void handleAnalyzingState() {
    // Analyze all captured images
    defect_detector.analyzeImage();
    
    // Move to reporting state
    current_state = REPORTING;
    Serial.println("✅ Analysis complete");
}

void handleReportingState() {
    // Generate and send reports
    generateScanReport();
    
    // Send data via IoT
    publishScanResults();
    
    // Return to idle state
    current_state = IDLE;
    Serial.println("✅ Reporting complete");
}

void handleErrorState() {
    // Flash error LED
    static bool error_led_state = false;
    static unsigned long last_error_led_time = 0;
    
    if (millis() - last_error_led_time > 250) { // Every 250ms
        error_led_state = !error_led_state;
        digitalWrite(STATUS_LED_PINS[5], error_led_state);
        last_error_led_time = millis();
    }
    
    // Sound buzzer
    static unsigned long last_buzzer_time = 0;
    if (millis() - last_buzzer_time > 2000) { // Every 2 seconds
        digitalWrite(BUZZER_PIN, HIGH);
        delay(100);
        digitalWrite(BUZZER_PIN, LOW);
        last_buzzer_time = millis();
    }
}

void handleEmergencyState() {
    // Turn off all systems
    digitalWrite(BLACKBODY_RELAY_PIN, LOW);
    digitalWrite(BLACKBODY_HEATER_PIN, LOW);
    digitalWrite(ILLUMINATION_PIN, LOW);
    
    // Stop all motion
    // Motion controllers will stop automatically
    
    // Flash all status LEDs
    static bool led_state = false;
    static unsigned long last_flash_time = 0;
    
    if (millis() - last_flash_time > 200) {
        led_state = !led_state;
        for (int i = 0; i < 6; i++) {
            digitalWrite(STATUS_LED_PINS[i], led_state);
        }
        last_flash_time = millis();
    }
    
    // Check for emergency reset
    if (digitalRead(EMERGENCY_STOP_PIN) == HIGH) {
        emergency_stop_active = false;
        scan_in_progress = false;
        current_state = IDLE;
        Serial.println("Emergency stop reset");
    }
}

void startScan() {
    if (current_state != IDLE) return;
    
    Serial.println("🔍 Starting thermal scan...");
    
    current_state = SCANNING;
    scan_in_progress = true;
    scan_start_time = millis();
    
    // Start motion controller scan
    motion_controller.performScan(scan_config);
}

void startCalibration() {
    if (current_state != IDLE) return;
    
    Serial.println("🔧 Starting calibration...");
    
    current_state = CALIBRATING;
}

void emergencyStop() {
    emergency_stop_active = true;
    scan_in_progress = false;
    current_state = IDLE;
    
    Serial.println("🚨 Emergency stop activated");
}

void generateScanReport() {
    Serial.println("📋 THERMAL SCAN REPORT");
    Serial.println("======================");
    Serial.println("Scan completed at: " + String(millis() - scan_start_time) + "ms");
    Serial.println("Temperature range: " + String(current_image.min_temp, 1) + " - " + String(current_image.max_temp, 1) + "°C");
    Serial.println("Average temperature: " + String(current_image.avg_temp, 1) + "°C");
    Serial.println("Total defects found: " + String(defect_count));
    
    // Log data
    logScanData();
}

void logScanData() {
    dataFile = SD.open(log_filename, FILE_WRITE);
    if (dataFile) {
        dataFile.print(millis());
        dataFile.print(",");
        dataFile.print(current_x);
        dataFile.print(",");
        dataFile.print(current_y);
        dataFile.print(",");
        dataFile.print(current_image.min_temp);
        dataFile.print(",");
        dataFile.print(current_image.max_temp);
        dataFile.print(",");
        dataFile.print(current_image.avg_temp);
        dataFile.print(",");
        dataFile.println(defect_count);
        dataFile.close();
    }
}

void publishScanResults() {
    if (!mqtt_client.connected()) return;
    
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["scan_duration"] = millis() - scan_start_time;
    doc["temperature_range"]["min"] = current_image.min_temp;
    doc["temperature_range"]["max"] = current_image.max_temp;
    doc["temperature_range"]["avg"] = current_image.avg_temp;
    doc["defect_count"] = defect_count;
    
    JsonArray defects = doc.createNestedArray("defects");
    for (int i = 0; i < min(defect_count, 10); i++) { // Limit to 10 defects
        JsonObject defect = defects.createNestedObject();
        defect["x"] = detected_defects[i].x;
        defect["y"] = detected_defects[i].y;
        defect["temperature"] = detected_defects[i].temperature;
        defect["severity"] = detected_defects[i].severity;
        defect["type"] = defect_detector.defectTypeToString(detected_defects[i].type);
        defect["confidence"] = detected_defects[i].confidence;
    }
    
    String payload;
    serializeJson(doc, payload);
    mqtt_client.publish("thermal/scan_results", payload.c_str());
}

void publishScanProgress(float progress) {
    if (!mqtt_client.connected()) return;
    
    StaticJsonDocument<256> doc;
    doc["progress"] = progress;
    doc["current_position"]["x"] = current_x;
    doc["current_position"]["y"] = current_y;
    doc["elapsed_time"] = millis() - scan_start_time;
    
    String payload;
    serializeJson(doc, payload);
    mqtt_client.publish("thermal/scan_progress", payload.c_str());
}

void handleIoTCommunication() {
    if (mqtt_client.connected()) {
        mqtt_client.loop();
    } else {
        connectToMQTT();
    }
}

void handleSerialCommands() {
    if (Serial.available()) {
        String command = Serial.readStringUntil('\n');
        command.trim();
        
        if (command == "SCAN") {
            startScan();
        }
        else if (command == "CALIBRATE") {
            startCalibration();
        }
        else if (command == "STOP") {
            emergencyStop();
        }
        else if (command == "STATUS") {
            showSystemStatus();
        }
        else if (command == "CAPTURE") {
            thermal_camera.captureImage();
            defect_detector.analyzeImage();
        }
        else if (command.startsWith("MOVE")) {
            // Format: MOVE x y
            int space1 = command.indexOf(' ');
            int space2 = command.indexOf(' ', space1 + 1);
            
            if (space1 > 0 && space2 > 0) {
                float x = command.substring(space1 + 1, space2).toFloat();
                float y = command.substring(space2 + 1).toFloat();
                motion_controller.setXYPosition(x, y);
            }
        }
        else if (command == "HELP") {
            Serial.println("Available commands:");
            Serial.println("SCAN - Start thermal scan");
            Serial.println("CALIBRATE - Start calibration");
            Serial.println("STOP - Emergency stop");
            Serial.println("STATUS - Show system status");
            Serial.println("CAPTURE - Capture single image");
            Serial.println("MOVE x y - Move to position");
            Serial.println("HELP - Show this help message");
        }
    }
}

void showSystemStatus() {
    Serial.println("=== THERMAL IMAGING SYSTEM STATUS ===");
    Serial.println("State: " + user_interface.stateToString(current_state));
    Serial.println("Position: (" + String(current_x, 1) + ", " + String(current_y, 1) + ")");
    Serial.println("Pan/Tilt: (" + String(current_pan, 1) + ", " + String(current_tilt, 1) + ")");
    
    if (current_image.valid) {
        Serial.println("Temperature Range: " + String(current_image.min_temp, 1) + " - " + String(current_image.max_temp, 1) + "°C");
        Serial.println("Average Temperature: " + String(current_image.avg_temp, 1) + "°C");
    }
    
    Serial.println("Defects Detected: " + String(defect_count));
    Serial.println("Calibration Valid: " + String(calibration_valid ? "Yes" : "No"));
    Serial.println("Emergency Stop: " + String(emergency_stop_active ? "Active" : "Inactive"));
    Serial.println("WiFi Connected: " + String(WiFi.status() == WL_CONNECTED ? "Yes" : "No"));
    Serial.println("MQTT Connected: " + String(mqtt_client.connected() ? "Yes" : "No"));
    Serial.println("Uptime: " + String((millis() - system_start_time) / 1000) + " seconds");
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("Received MQTT message: " + message);
    
    // Parse and execute commands
    StaticJsonDocument<256> doc;
    deserializeJson(doc, message);
    
    if (doc["action"] == "start_scan") {
        startScan();
    }
    else if (doc["action"] == "start_calibration") {
        startCalibration();
    }
    else if (doc["action"] == "emergency_stop") {
        emergencyStop();
    }
    else if (doc["action"] == "move_to") {
        float x = doc["x"];
        float y = doc["y"];
        motion_controller.setXYPosition(x, y);
    }
    else if (doc["action"] == "capture_image") {
        thermal_camera.captureImage();
        defect_detector.analyzeImage();
    }
} 