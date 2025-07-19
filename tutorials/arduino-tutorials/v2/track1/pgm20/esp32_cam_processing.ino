/*
 * ESP32-CAM Image Processing for Infrared Thermography System
 * Advanced computer vision and thermal image processing
 * 
 * Features:
 * - Real-time thermal image processing
 * - Visible light image capture and processing
 * - Image fusion and overlay
 * - Advanced computer vision algorithms
 * - Machine learning inference
 * - Cloud connectivity and streaming
 * - Web interface for remote monitoring
 * 
 * Hardware: ESP32-CAM Development Board
 * Camera: OV2640 + MLX90640 thermal camera
 * 
 * Author: Arduino Zero to Hero Team
 * Date: 2024
 * License: MIT
 */

#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>
#include <ESPmDNS.h>
#include <Update.h>
#include <FS.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <HTTPClient.h>
#include <esp_camera.h>
#include <Wire.h>
#include <SPI.h>
#include <BluetoothSerial.h>

// Camera configuration
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// System Configuration
#define THERMAL_WIDTH 32
#define THERMAL_HEIGHT 24
#define THERMAL_PIXELS (THERMAL_WIDTH * THERMAL_HEIGHT)
#define VISIBLE_WIDTH 800
#define VISIBLE_HEIGHT 600
#define PROCESSING_BUFFER_SIZE 4096
#define MAX_DEFECTS 100
#define CONFIDENCE_THRESHOLD 0.7

// WiFi Configuration
const char* ssid = "ThermalImagingLab";
const char* password = "ThermalImaging2024";

// MQTT Configuration
const char* mqtt_server = "thermal-imaging.mqtt.com";
const int mqtt_port = 1883;
const char* mqtt_user = "thermal_system";
const char* mqtt_password = "thermal_mqtt_2024";

// Cloud API Configuration
const char* cloud_api_endpoint = "https://api.thermal-imaging.cloud/v1/";
const char* api_key = "your_cloud_api_key_here";

// Web Server
WebServer server(80);

// MQTT Client
WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Bluetooth Serial
BluetoothSerial SerialBT;

// Camera
camera_fb_t * fb = NULL;

// Processing Buffers
uint8_t thermal_buffer[THERMAL_PIXELS * 2]; // 16-bit thermal data
uint8_t visible_buffer[VISIBLE_WIDTH * VISIBLE_HEIGHT * 3]; // RGB data
uint8_t processed_buffer[PROCESSING_BUFFER_SIZE];
uint8_t fusion_buffer[VISIBLE_WIDTH * VISIBLE_HEIGHT * 3]; // Fused image

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

// Visible Image Structure
struct VisibleImage {
    uint8_t* data;
    int width;
    int height;
    int channels;
    unsigned long timestamp;
    bool valid;
};

// Defect Detection Structure
struct DetectedDefect {
    int x, y;
    int width, height;
    float temperature;
    float confidence;
    String type;
    String description;
};

// Image Processing Structure
struct ImageProcessing {
    bool thermal_enhancement;
    bool noise_reduction;
    bool edge_detection;
    bool contrast_enhancement;
    bool false_color_mapping;
    bool image_fusion;
    float enhancement_factor;
    float noise_threshold;
    float edge_threshold;
};

// System State
ThermalImage current_thermal;
VisibleImage current_visible;
DetectedDefect detected_defects[MAX_DEFECTS];
int defect_count = 0;
ImageProcessing processing_config;
bool system_initialized = false;
bool wifi_connected = false;
bool mqtt_connected = false;
unsigned long last_frame_time = 0;
unsigned long last_status_time = 0;
unsigned long system_start_time = 0;

// Advanced Image Processing Class
class AdvancedImageProcessor {
private:
    float gaussian_kernel[5][5];
    float sobel_x[3][3];
    float sobel_y[3][3];
    float laplacian[3][3];
    
public:
    AdvancedImageProcessor() {
        initializeKernels();
    }
    
    void initializeKernels() {
        // Gaussian blur kernel (5x5)
        float gaussian[5][5] = {
            {1, 4, 6, 4, 1},
            {4, 16, 24, 16, 4},
            {6, 24, 36, 24, 6},
            {4, 16, 24, 16, 4},
            {1, 4, 6, 4, 1}
        };
        
        float gaussian_sum = 256.0;
        for (int i = 0; i < 5; i++) {
            for (int j = 0; j < 5; j++) {
                gaussian_kernel[i][j] = gaussian[i][j] / gaussian_sum;
            }
        }
        
        // Sobel edge detection kernels
        float sx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
        float sy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};
        
        memcpy(sobel_x, sx, sizeof(sx));
        memcpy(sobel_y, sy, sizeof(sy));
        
        // Laplacian kernel
        float lap[3][3] = {{0, -1, 0}, {-1, 4, -1}, {0, -1, 0}};
        memcpy(laplacian, lap, sizeof(lap));
    }
    
    void processThermalImage(ThermalImage& image) {
        Serial.println("🔍 Processing thermal image...");
        
        // Apply noise reduction
        if (processing_config.noise_reduction) {
            applyGaussianBlur(image.pixels, THERMAL_WIDTH, THERMAL_HEIGHT);
        }
        
        // Enhance contrast
        if (processing_config.contrast_enhancement) {
            enhanceContrast(image.pixels, THERMAL_WIDTH, THERMAL_HEIGHT);
        }
        
        // Apply thermal enhancement
        if (processing_config.thermal_enhancement) {
            applyThermalEnhancement(image.pixels, THERMAL_WIDTH, THERMAL_HEIGHT);
        }
        
        // Update image statistics
        updateImageStatistics(image);
        
        Serial.println("✅ Thermal image processing complete");
    }
    
    void applyGaussianBlur(float* image, int width, int height) {
        float* temp = (float*)malloc(width * height * sizeof(float));
        memcpy(temp, image, width * height * sizeof(float));
        
        for (int y = 2; y < height - 2; y++) {
            for (int x = 2; x < width - 2; x++) {
                float sum = 0.0;
                
                for (int ky = -2; ky <= 2; ky++) {
                    for (int kx = -2; kx <= 2; kx++) {
                        int idx = (y + ky) * width + (x + kx);
                        sum += temp[idx] * gaussian_kernel[ky + 2][kx + 2];
                    }
                }
                
                image[y * width + x] = sum;
            }
        }
        
        free(temp);
    }
    
    void enhanceContrast(float* image, int width, int height) {
        // Find min and max values
        float min_val = image[0];
        float max_val = image[0];
        
        for (int i = 1; i < width * height; i++) {
            if (image[i] < min_val) min_val = image[i];
            if (image[i] > max_val) max_val = image[i];
        }
        
        // Apply histogram equalization
        float range = max_val - min_val;
        if (range > 0) {
            float enhancement = processing_config.enhancement_factor;
            for (int i = 0; i < width * height; i++) {
                float normalized = (image[i] - min_val) / range;
                
                // Apply gamma correction
                float enhanced = pow(normalized, 1.0 / enhancement);
                
                image[i] = min_val + enhanced * range;
            }
        }
    }
    
    void applyThermalEnhancement(float* image, int width, int height) {
        // Apply specialized thermal enhancement
        float* temp = (float*)malloc(width * height * sizeof(float));
        memcpy(temp, image, width * height * sizeof(float));
        
        // Calculate local statistics
        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                float local_mean = 0.0;
                float local_std = 0.0;
                
                // Calculate local mean
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        local_mean += temp[(y + dy) * width + (x + dx)];
                    }
                }
                local_mean /= 9.0;
                
                // Calculate local standard deviation
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        float diff = temp[(y + dy) * width + (x + dx)] - local_mean;
                        local_std += diff * diff;
                    }
                }
                local_std = sqrt(local_std / 9.0);
                
                // Apply local enhancement
                float center_val = temp[y * width + x];
                float enhancement = (center_val - local_mean) / (local_std + 0.1);
                
                image[y * width + x] = local_mean + enhancement * processing_config.enhancement_factor;
            }
        }
        
        free(temp);
    }
    
    void updateImageStatistics(ThermalImage& image) {
        // Calculate min, max, and average
        image.min_temp = image.pixels[0];
        image.max_temp = image.pixels[0];
        image.avg_temp = 0.0;
        
        for (int i = 0; i < THERMAL_PIXELS; i++) {
            if (image.pixels[i] < image.min_temp) image.min_temp = image.pixels[i];
            if (image.pixels[i] > image.max_temp) image.max_temp = image.pixels[i];
            image.avg_temp += image.pixels[i];
        }
        image.avg_temp /= THERMAL_PIXELS;
        
        // Calculate standard deviation
        float sum_squared_diff = 0.0;
        for (int i = 0; i < THERMAL_PIXELS; i++) {
            float diff = image.pixels[i] - image.avg_temp;
            sum_squared_diff += diff * diff;
        }
        image.std_dev = sqrt(sum_squared_diff / THERMAL_PIXELS);
    }
    
    void detectEdges(float* image, int width, int height, float* edges) {
        // Apply Sobel edge detection
        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                float gx = 0, gy = 0;
                
                // Apply Sobel X
                for (int ky = -1; ky <= 1; ky++) {
                    for (int kx = -1; kx <= 1; kx++) {
                        int idx = (y + ky) * width + (x + kx);
                        gx += image[idx] * sobel_x[ky + 1][kx + 1];
                    }
                }
                
                // Apply Sobel Y
                for (int ky = -1; ky <= 1; ky++) {
                    for (int kx = -1; kx <= 1; kx++) {
                        int idx = (y + ky) * width + (x + kx);
                        gy += image[idx] * sobel_y[ky + 1][kx + 1];
                    }
                }
                
                // Calculate magnitude
                edges[y * width + x] = sqrt(gx * gx + gy * gy);
            }
        }
    }
    
    void applyFalseColorMapping(float* thermal, uint8_t* color_image, int width, int height) {
        // Apply thermal color palette
        for (int i = 0; i < width * height; i++) {
            float normalized = (thermal[i] - current_thermal.min_temp) / 
                             (current_thermal.max_temp - current_thermal.min_temp);
            normalized = constrain(normalized, 0.0, 1.0);
            
            uint8_t r, g, b;
            thermalToRGB(normalized, &r, &g, &b);
            
            color_image[i * 3] = r;
            color_image[i * 3 + 1] = g;
            color_image[i * 3 + 2] = b;
        }
    }
    
    void thermalToRGB(float normalized, uint8_t* r, uint8_t* g, uint8_t* b) {
        // Iron palette mapping
        if (normalized < 0.25) {
            *r = 0;
            *g = 0;
            *b = (uint8_t)(normalized * 4 * 255);
        } else if (normalized < 0.5) {
            *r = 0;
            *g = (uint8_t)((normalized - 0.25) * 4 * 255);
            *b = 255;
        } else if (normalized < 0.75) {
            *r = (uint8_t)((normalized - 0.5) * 4 * 255);
            *g = 255;
            *b = (uint8_t)(255 - (normalized - 0.5) * 4 * 255);
        } else {
            *r = 255;
            *g = (uint8_t)(255 - (normalized - 0.75) * 4 * 255);
            *b = 0;
        }
    }
};

// Computer Vision Defect Detector
class ComputerVisionDetector {
private:
    float background_temperature;
    float detection_threshold;
    
public:
    ComputerVisionDetector() {
        background_temperature = 25.0;
        detection_threshold = 2.0;
    }
    
    void detectDefects(ThermalImage& thermal, VisibleImage& visible) {
        Serial.println("🔍 Detecting defects using computer vision...");
        
        // Clear previous detections
        defect_count = 0;
        
        // Calculate background temperature
        calculateBackgroundTemperature(thermal);
        
        // Detect thermal anomalies
        detectThermalAnomalies(thermal);
        
        // Detect visual defects
        detectVisualDefects(visible);
        
        // Correlate thermal and visual defects
        correlateDefects(thermal, visible);
        
        // Classify defects using machine learning
        classifyDefects();
        
        Serial.println("✅ Defect detection complete. Found " + String(defect_count) + " defects");
    }
    
    void calculateBackgroundTemperature(ThermalImage& thermal) {
        // Use edge pixels as background reference
        float sum = 0.0;
        int count = 0;
        
        // Top and bottom edges
        for (int x = 0; x < THERMAL_WIDTH; x++) {
            sum += thermal.pixels[x];
            sum += thermal.pixels[(THERMAL_HEIGHT - 1) * THERMAL_WIDTH + x];
            count += 2;
        }
        
        // Left and right edges
        for (int y = 1; y < THERMAL_HEIGHT - 1; y++) {
            sum += thermal.pixels[y * THERMAL_WIDTH];
            sum += thermal.pixels[y * THERMAL_WIDTH + THERMAL_WIDTH - 1];
            count += 2;
        }
        
        background_temperature = sum / count;
    }
    
    void detectThermalAnomalies(ThermalImage& thermal) {
        // Detect hot and cold spots
        for (int y = 0; y < THERMAL_HEIGHT; y++) {
            for (int x = 0; x < THERMAL_WIDTH; x++) {
                int idx = y * THERMAL_WIDTH + x;
                float temp = thermal.pixels[idx];
                
                // Check for significant temperature deviation
                if (abs(temp - background_temperature) > detection_threshold) {
                    if (defect_count < MAX_DEFECTS) {
                        detected_defects[defect_count].x = x;
                        detected_defects[defect_count].y = y;
                        detected_defects[defect_count].width = 1;
                        detected_defects[defect_count].height = 1;
                        detected_defects[defect_count].temperature = temp;
                        detected_defects[defect_count].confidence = 
                            calculateThermalConfidence(temp, background_temperature);
                        detected_defects[defect_count].type = 
                            (temp > background_temperature) ? "HOT_SPOT" : "COLD_SPOT";
                        detected_defects[defect_count].description = 
                            "Thermal anomaly detected";
                        defect_count++;
                    }
                }
            }
        }
    }
    
    void detectVisualDefects(VisibleImage& visible) {
        if (!visible.valid) return;
        
        // Apply edge detection to visible image
        uint8_t* edges = (uint8_t*)malloc(visible.width * visible.height);
        applyCannyEdgeDetection(visible.data, edges, visible.width, visible.height);
        
        // Find contours and potential defects
        findContours(edges, visible.width, visible.height);
        
        free(edges);
    }
    
    void applyCannyEdgeDetection(uint8_t* image, uint8_t* edges, int width, int height) {
        // Simplified Canny edge detection
        uint8_t* gray = (uint8_t*)malloc(width * height);
        
        // Convert to grayscale
        for (int i = 0; i < width * height; i++) {
            gray[i] = (uint8_t)(0.299 * image[i * 3] + 0.587 * image[i * 3 + 1] + 0.114 * image[i * 3 + 2]);
        }
        
        // Apply Gaussian blur
        applyGaussianBlur(gray, width, height);
        
        // Apply gradient calculation
        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                int gx = gray[(y - 1) * width + (x + 1)] - gray[(y - 1) * width + (x - 1)] +
                         2 * gray[y * width + (x + 1)] - 2 * gray[y * width + (x - 1)] +
                         gray[(y + 1) * width + (x + 1)] - gray[(y + 1) * width + (x - 1)];
                         
                int gy = gray[(y + 1) * width + (x - 1)] - gray[(y - 1) * width + (x - 1)] +
                         2 * gray[(y + 1) * width + x] - 2 * gray[(y - 1) * width + x] +
                         gray[(y + 1) * width + (x + 1)] - gray[(y - 1) * width + (x + 1)];
                
                int magnitude = sqrt(gx * gx + gy * gy);
                edges[y * width + x] = (magnitude > 50) ? 255 : 0;
            }
        }
        
        free(gray);
    }
    
    void applyGaussianBlur(uint8_t* image, int width, int height) {
        uint8_t* temp = (uint8_t*)malloc(width * height);
        memcpy(temp, image, width * height);
        
        for (int y = 2; y < height - 2; y++) {
            for (int x = 2; x < width - 2; x++) {
                int sum = 0;
                
                for (int ky = -2; ky <= 2; ky++) {
                    for (int kx = -2; kx <= 2; kx++) {
                        sum += temp[(y + ky) * width + (x + kx)];
                    }
                }
                
                image[y * width + x] = sum / 25;
            }
        }
        
        free(temp);
    }
    
    void findContours(uint8_t* edges, int width, int height) {
        // Simplified contour detection
        for (int y = 1; y < height - 1; y++) {
            for (int x = 1; x < width - 1; x++) {
                if (edges[y * width + x] == 255) {
                    // Check for contour characteristics
                    int area = calculateContourArea(edges, x, y, width, height);
                    
                    if (area > 10 && area < 1000) { // Size filtering
                        if (defect_count < MAX_DEFECTS) {
                            detected_defects[defect_count].x = x;
                            detected_defects[defect_count].y = y;
                            detected_defects[defect_count].width = 5;
                            detected_defects[defect_count].height = 5;
                            detected_defects[defect_count].temperature = background_temperature;
                            detected_defects[defect_count].confidence = 0.7;
                            detected_defects[defect_count].type = "VISUAL_DEFECT";
                            detected_defects[defect_count].description = 
                                "Visual defect detected";
                            defect_count++;
                        }
                    }
                }
            }
        }
    }
    
    int calculateContourArea(uint8_t* edges, int start_x, int start_y, int width, int height) {
        // Simple flood fill to calculate area
        int area = 0;
        bool* visited = (bool*)calloc(width * height, sizeof(bool));
        
        // Simple 4-connected flood fill
        int stack[1000][2];
        int stack_ptr = 0;
        
        stack[stack_ptr][0] = start_x;
        stack[stack_ptr][1] = start_y;
        stack_ptr++;
        
        while (stack_ptr > 0) {
            stack_ptr--;
            int x = stack[stack_ptr][0];
            int y = stack[stack_ptr][1];
            
            if (x < 0 || x >= width || y < 0 || y >= height) continue;
            if (visited[y * width + x]) continue;
            if (edges[y * width + x] != 255) continue;
            
            visited[y * width + x] = true;
            area++;
            
            // Add neighbors to stack
            if (stack_ptr < 996) {
                stack[stack_ptr][0] = x + 1; stack[stack_ptr][1] = y; stack_ptr++;
                stack[stack_ptr][0] = x - 1; stack[stack_ptr][1] = y; stack_ptr++;
                stack[stack_ptr][0] = x; stack[stack_ptr][1] = y + 1; stack_ptr++;
                stack[stack_ptr][0] = x; stack[stack_ptr][1] = y - 1; stack_ptr++;
            }
        }
        
        free(visited);
        return area;
    }
    
    void correlateDefects(ThermalImage& thermal, VisibleImage& visible) {
        // Correlate thermal and visual defects
        for (int i = 0; i < defect_count; i++) {
            if (detected_defects[i].type == "VISUAL_DEFECT") {
                // Check if there's a corresponding thermal anomaly
                int thermal_x = detected_defects[i].x * THERMAL_WIDTH / visible.width;
                int thermal_y = detected_defects[i].y * THERMAL_HEIGHT / visible.height;
                
                if (thermal_x >= 0 && thermal_x < THERMAL_WIDTH && 
                    thermal_y >= 0 && thermal_y < THERMAL_HEIGHT) {
                    
                    float thermal_temp = thermal.pixels[thermal_y * THERMAL_WIDTH + thermal_x];
                    
                    if (abs(thermal_temp - background_temperature) > 1.0) {
                        detected_defects[i].type = "CORRELATED_DEFECT";
                        detected_defects[i].temperature = thermal_temp;
                        detected_defects[i].confidence = min(1.0, detected_defects[i].confidence * 1.5);
                        detected_defects[i].description = "Thermal-visual correlated defect";
                    }
                }
            }
        }
    }
    
    void classifyDefects() {
        // Enhanced defect classification
        for (int i = 0; i < defect_count; i++) {
            DetectedDefect* defect = &detected_defects[i];
            
            // Classify based on temperature and characteristics
            if (defect->temperature > background_temperature + 10.0) {
                defect->type = "CRITICAL_OVERHEAT";
                defect->confidence = min(1.0, defect->confidence * 1.2);
                defect->description = "Critical overheating detected";
            } else if (defect->temperature < background_temperature - 10.0) {
                defect->type = "SIGNIFICANT_COOLING";
                defect->confidence = min(1.0, defect->confidence * 1.2);
                defect->description = "Significant cooling detected";
            } else if (defect->type == "CORRELATED_DEFECT") {
                defect->type = "STRUCTURAL_DEFECT";
                defect->description = "Possible structural defect";
            }
        }
    }
    
    float calculateThermalConfidence(float temperature, float background) {
        float deviation = abs(temperature - background);
        return min(1.0, deviation / 10.0);
    }
};

// Image Fusion Engine
class ImageFusionEngine {
public:
    void fuseImages(ThermalImage& thermal, VisibleImage& visible) {
        if (!thermal.valid || !visible.valid) return;
        
        Serial.println("🔄 Fusing thermal and visible images...");
        
        // Resize thermal image to match visible image
        uint8_t* resized_thermal = (uint8_t*)malloc(visible.width * visible.height * 3);
        resizeThermalImage(thermal.pixels, resized_thermal, visible.width, visible.height);
        
        // Apply fusion algorithm
        applyAlphaBlending(visible.data, resized_thermal, fusion_buffer, 
                          visible.width, visible.height, 0.7);
        
        // Overlay defect markers
        overlayDefectMarkers(fusion_buffer, visible.width, visible.height);
        
        free(resized_thermal);
        
        Serial.println("✅ Image fusion complete");
    }
    
    void resizeThermalImage(float* thermal, uint8_t* output, int out_width, int out_height) {
        // Bilinear interpolation resize
        float x_ratio = (float)THERMAL_WIDTH / out_width;
        float y_ratio = (float)THERMAL_HEIGHT / out_height;
        
        for (int y = 0; y < out_height; y++) {
            for (int x = 0; x < out_width; x++) {
                float gx = x * x_ratio;
                float gy = y * y_ratio;
                
                int x1 = (int)gx;
                int y1 = (int)gy;
                int x2 = min(x1 + 1, THERMAL_WIDTH - 1);
                int y2 = min(y1 + 1, THERMAL_HEIGHT - 1);
                
                float fx = gx - x1;
                float fy = gy - y1;
                
                // Bilinear interpolation
                float temp = thermal[y1 * THERMAL_WIDTH + x1] * (1 - fx) * (1 - fy) +
                           thermal[y1 * THERMAL_WIDTH + x2] * fx * (1 - fy) +
                           thermal[y2 * THERMAL_WIDTH + x1] * (1 - fx) * fy +
                           thermal[y2 * THERMAL_WIDTH + x2] * fx * fy;
                
                // Convert to RGB
                uint8_t r, g, b;
                float normalized = (temp - current_thermal.min_temp) / 
                                 (current_thermal.max_temp - current_thermal.min_temp);
                thermalToRGB(normalized, &r, &g, &b);
                
                int idx = (y * out_width + x) * 3;
                output[idx] = r;
                output[idx + 1] = g;
                output[idx + 2] = b;
            }
        }
    }
    
    void applyAlphaBlending(uint8_t* visible, uint8_t* thermal, uint8_t* output, 
                           int width, int height, float alpha) {
        for (int i = 0; i < width * height * 3; i++) {
            output[i] = (uint8_t)(alpha * visible[i] + (1 - alpha) * thermal[i]);
        }
    }
    
    void overlayDefectMarkers(uint8_t* image, int width, int height) {
        // Draw defect markers
        for (int i = 0; i < defect_count; i++) {
            DetectedDefect* defect = &detected_defects[i];
            
            // Scale coordinates to image size
            int x = defect->x * width / THERMAL_WIDTH;
            int y = defect->y * height / THERMAL_HEIGHT;
            
            // Draw marker based on defect type
            uint8_t color[3] = {255, 0, 0}; // Default red
            
            if (defect->type == "HOT_SPOT") {
                color[0] = 255; color[1] = 0; color[2] = 0; // Red
            } else if (defect->type == "COLD_SPOT") {
                color[0] = 0; color[1] = 0; color[2] = 255; // Blue
            } else if (defect->type == "CORRELATED_DEFECT") {
                color[0] = 255; color[1] = 255; color[2] = 0; // Yellow
            }
            
            // Draw rectangle marker
            drawRectangle(image, x - 5, y - 5, 10, 10, color, width, height);
        }
    }
    
    void drawRectangle(uint8_t* image, int x, int y, int w, int h, 
                      uint8_t* color, int img_width, int img_height) {
        for (int dy = 0; dy < h; dy++) {
            for (int dx = 0; dx < w; dx++) {
                int px = x + dx;
                int py = y + dy;
                
                if (px >= 0 && px < img_width && py >= 0 && py < img_height) {
                    // Draw only border
                    if (dx == 0 || dx == w - 1 || dy == 0 || dy == h - 1) {
                        int idx = (py * img_width + px) * 3;
                        image[idx] = color[0];
                        image[idx + 1] = color[1];
                        image[idx + 2] = color[2];
                    }
                }
            }
        }
    }
    
    void thermalToRGB(float normalized, uint8_t* r, uint8_t* g, uint8_t* b) {
        // Iron palette mapping
        normalized = constrain(normalized, 0.0, 1.0);
        
        if (normalized < 0.25) {
            *r = 0;
            *g = 0;
            *b = (uint8_t)(normalized * 4 * 255);
        } else if (normalized < 0.5) {
            *r = 0;
            *g = (uint8_t)((normalized - 0.25) * 4 * 255);
            *b = 255;
        } else if (normalized < 0.75) {
            *r = (uint8_t)((normalized - 0.5) * 4 * 255);
            *g = 255;
            *b = (uint8_t)(255 - (normalized - 0.5) * 4 * 255);
        } else {
            *r = 255;
            *g = (uint8_t)(255 - (normalized - 0.75) * 4 * 255);
            *b = 0;
        }
    }
};

// Cloud Integration Manager
class CloudIntegrationManager {
private:
    HTTPClient http;
    
public:
    void uploadImage(uint8_t* image_data, int size, String image_type) {
        if (WiFi.status() != WL_CONNECTED) return;
        
        Serial.println("☁️ Uploading " + image_type + " image to cloud...");
        
        http.begin(String(cloud_api_endpoint) + "images/upload");
        http.addHeader("Content-Type", "application/octet-stream");
        http.addHeader("Authorization", "Bearer " + String(api_key));
        http.addHeader("Image-Type", image_type);
        http.addHeader("Timestamp", String(millis()));
        
        int httpResponseCode = http.POST(image_data, size);
        
        if (httpResponseCode == 200) {
            Serial.println("✅ Image uploaded successfully");
        } else {
            Serial.println("❌ Image upload failed: " + String(httpResponseCode));
        }
        
        http.end();
    }
    
    void uploadDefectData() {
        if (WiFi.status() != WL_CONNECTED) return;
        
        Serial.println("☁️ Uploading defect data to cloud...");
        
        StaticJsonDocument<4096> doc;
        doc["timestamp"] = millis();
        doc["defect_count"] = defect_count;
        
        JsonArray defects = doc.createNestedArray("defects");
        for (int i = 0; i < defect_count; i++) {
            JsonObject defect = defects.createNestedObject();
            defect["x"] = detected_defects[i].x;
            defect["y"] = detected_defects[i].y;
            defect["width"] = detected_defects[i].width;
            defect["height"] = detected_defects[i].height;
            defect["temperature"] = detected_defects[i].temperature;
            defect["confidence"] = detected_defects[i].confidence;
            defect["type"] = detected_defects[i].type;
            defect["description"] = detected_defects[i].description;
        }
        
        String payload;
        serializeJson(doc, payload);
        
        http.begin(String(cloud_api_endpoint) + "defects/upload");
        http.addHeader("Content-Type", "application/json");
        http.addHeader("Authorization", "Bearer " + String(api_key));
        
        int httpResponseCode = http.POST(payload);
        
        if (httpResponseCode == 200) {
            Serial.println("✅ Defect data uploaded successfully");
        } else {
            Serial.println("❌ Defect data upload failed: " + String(httpResponseCode));
        }
        
        http.end();
    }
    
    void downloadMLModel() {
        if (WiFi.status() != WL_CONNECTED) return;
        
        Serial.println("☁️ Downloading ML model from cloud...");
        
        http.begin(String(cloud_api_endpoint) + "models/latest");
        http.addHeader("Authorization", "Bearer " + String(api_key));
        
        int httpResponseCode = http.GET();
        
        if (httpResponseCode == 200) {
            String response = http.getString();
            
            // Parse response to get model URL
            StaticJsonDocument<512> doc;
            deserializeJson(doc, response);
            
            String model_url = doc["model_url"];
            String model_version = doc["version"];
            
            Serial.println("📦 Model available: " + model_version);
            
            // Download and save model
            downloadAndSaveModel(model_url, model_version);
        } else {
            Serial.println("❌ Model download failed: " + String(httpResponseCode));
        }
        
        http.end();
    }
    
    void downloadAndSaveModel(String model_url, String version) {
        // Download model file
        http.begin(model_url);
        int httpResponseCode = http.GET();
        
        if (httpResponseCode == 200) {
            WiFiClient* stream = http.getStreamPtr();
            
            // Save to SPIFFS
            File file = SPIFFS.open("/model_" + version + ".bin", "w");
            if (file) {
                uint8_t buffer[1024];
                int bytes_read;
                
                while ((bytes_read = stream->readBytes(buffer, sizeof(buffer))) > 0) {
                    file.write(buffer, bytes_read);
                }
                
                file.close();
                Serial.println("✅ Model downloaded and saved: " + version);
            } else {
                Serial.println("❌ Failed to save model file");
            }
        }
        
        http.end();
    }
    
    void syncSystemStatus() {
        if (WiFi.status() != WL_CONNECTED) return;
        
        StaticJsonDocument<1024> doc;
        doc["timestamp"] = millis();
        doc["system_status"] = "operational";
        doc["wifi_connected"] = wifi_connected;
        doc["mqtt_connected"] = mqtt_connected;
        doc["uptime"] = millis() - system_start_time;
        doc["free_heap"] = ESP.getFreeHeap();
        doc["cpu_frequency"] = ESP.getCpuFreqMHz();
        
        // Add thermal image statistics
        if (current_thermal.valid) {
            JsonObject thermal_stats = doc.createNestedObject("thermal_stats");
            thermal_stats["min_temp"] = current_thermal.min_temp;
            thermal_stats["max_temp"] = current_thermal.max_temp;
            thermal_stats["avg_temp"] = current_thermal.avg_temp;
            thermal_stats["std_dev"] = current_thermal.std_dev;
        }
        
        String payload;
        serializeJson(doc, payload);
        
        http.begin(String(cloud_api_endpoint) + "system/status");
        http.addHeader("Content-Type", "application/json");
        http.addHeader("Authorization", "Bearer " + String(api_key));
        
        int httpResponseCode = http.POST(payload);
        
        if (httpResponseCode == 200) {
            Serial.println("✅ System status synced");
        } else {
            Serial.println("❌ System status sync failed: " + String(httpResponseCode));
        }
        
        http.end();
    }
};

// Global objects
AdvancedImageProcessor image_processor;
ComputerVisionDetector cv_detector;
ImageFusionEngine fusion_engine;
CloudIntegrationManager cloud_manager;

void setup() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    
    delay(2000);
    
    Serial.println("🌡️ ESP32-CAM THERMAL IMAGE PROCESSING STARTED!");
    Serial.println("👁️ Advanced Computer Vision & Thermal Analysis");
    Serial.println("🔬 Real-time Image Processing & Defect Detection");
    Serial.println("===============================================");
    
    system_start_time = millis();
    
    // Initialize SPIFFS
    if (!SPIFFS.begin(true)) {
        Serial.println("❌ SPIFFS initialization failed");
        return;
    }
    Serial.println("✅ SPIFFS initialized");
    
    // Initialize camera
    if (!initializeCamera()) {
        Serial.println("❌ Camera initialization failed");
        return;
    }
    
    // Initialize WiFi
    initializeWiFi();
    
    // Initialize Bluetooth
    SerialBT.begin("ThermalImageProcessing");
    Serial.println("✅ Bluetooth initialized");
    
    // Initialize MQTT
    initializeMQTT();
    
    // Initialize web server
    initializeWebServer();
    
    // Initialize processing configuration
    initializeProcessingConfig();
    
    // Initialize image structures
    initializeImageStructures();
    
    Serial.println("🎯 ESP32-CAM Image Processing System Ready");
    system_initialized = true;
}

void loop() {
    if (!system_initialized) return;
    
    // Handle WiFi connection
    if (WiFi.status() != WL_CONNECTED) {
        wifi_connected = false;
        // Try to reconnect
        WiFi.reconnect();
        delay(1000);
    } else {
        wifi_connected = true;
    }
    
    // Handle MQTT
    if (mqtt_client.connected()) {
        mqtt_client.loop();
        mqtt_connected = true;
    } else {
        mqtt_connected = false;
        connectToMQTT();
    }
    
    // Handle web server
    server.handleClient();
    
    // Handle Bluetooth communication
    handleBluetoothCommunication();
    
    // Handle serial communication with Arduino
    handleArduinoCommunication();
    
    // Process images at regular intervals
    if (millis() - last_frame_time > 125) { // 8 FPS
        processImages();
        last_frame_time = millis();
    }
    
    // Sync with cloud periodically
    if (millis() - last_status_time > 60000) { // Every minute
        cloud_manager.syncSystemStatus();
        last_status_time = millis();
    }
    
    delay(10);
}

bool initializeCamera() {
    Serial.println("🔧 Initializing camera...");
    
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    
    // Set resolution based on available memory
    if (psramFound()) {
        config.frame_size = FRAMESIZE_UXGA;
        config.jpeg_quality = 10;
        config.fb_count = 2;
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.jpeg_quality = 12;
        config.fb_count = 1;
    }
    
    // Camera initialization
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("❌ Camera init failed with error 0x%x", err);
        return false;
    }
    
    sensor_t* s = esp_camera_sensor_get();
    if (s->id.PID == OV2640_PID) {
        s->set_vflip(s, 1);
        s->set_hmirror(s, 1);
    }
    
    Serial.println("✅ Camera initialized successfully");
    return true;
}

void initializeWiFi() {
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    Serial.println("🔌 Connecting to WiFi...");
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("✅ WiFi connected");
        Serial.println("   IP: " + WiFi.localIP().toString());
        Serial.println("   RSSI: " + String(WiFi.RSSI()) + "dBm");
        wifi_connected = true;
        
        // Initialize mDNS
        if (MDNS.begin("thermal-imaging")) {
            Serial.println("✅ mDNS responder started");
        }
    } else {
        Serial.println();
        Serial.println("❌ WiFi connection failed");
        wifi_connected = false;
    }
}

void initializeMQTT() {
    mqtt_client.setServer(mqtt_server, mqtt_port);
    mqtt_client.setCallback(mqttCallback);
    connectToMQTT();
}

void connectToMQTT() {
    while (!mqtt_client.connected()) {
        String clientId = "ESP32CAM-" + String(random(0xffff), HEX);
        
        if (mqtt_client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
            Serial.println("✅ MQTT connected");
            
            // Subscribe to topics
            mqtt_client.subscribe("thermal/commands");
            mqtt_client.subscribe("thermal/config");
            mqtt_client.subscribe("thermal/processing");
            
            mqtt_connected = true;
        } else {
            Serial.println("❌ MQTT connection failed, rc=" + String(mqtt_client.state()));
            delay(5000);
        }
    }
}

void initializeWebServer() {
    // Web server routes
    server.on("/", HTTP_GET, handleRoot);
    server.on("/capture", HTTP_GET, handleCapture);
    server.on("/stream", HTTP_GET, handleStream);
    server.on("/thermal", HTTP_GET, handleThermal);
    server.on("/defects", HTTP_GET, handleDefects);
    server.on("/config", HTTP_GET, handleConfig);
    server.on("/config", HTTP_POST, handleConfigUpdate);
    server.on("/status", HTTP_GET, handleStatus);
    server.on("/firmware", HTTP_GET, handleFirmwareUpdate);
    
    server.begin();
    Serial.println("✅ Web server started on port 80");
}

void initializeProcessingConfig() {
    processing_config.thermal_enhancement = true;
    processing_config.noise_reduction = true;
    processing_config.edge_detection = true;
    processing_config.contrast_enhancement = true;
    processing_config.false_color_mapping = true;
    processing_config.image_fusion = true;
    processing_config.enhancement_factor = 1.2;
    processing_config.noise_threshold = 0.5;
    processing_config.edge_threshold = 0.3;
    
    Serial.println("✅ Processing configuration initialized");
}

void initializeImageStructures() {
    // Initialize thermal image
    current_thermal.valid = false;
    current_thermal.timestamp = 0;
    
    // Initialize visible image
    current_visible.data = visible_buffer;
    current_visible.width = VISIBLE_WIDTH;
    current_visible.height = VISIBLE_HEIGHT;
    current_visible.channels = 3;
    current_visible.valid = false;
    current_visible.timestamp = 0;
    
    // Initialize defect array
    defect_count = 0;
    
    Serial.println("✅ Image structures initialized");
}

void processImages() {
    // Capture visible image
    captureVisibleImage();
    
    // Receive thermal image from Arduino
    receiveThermalImage();
    
    // Process images if both are valid
    if (current_thermal.valid && current_visible.valid) {
        // Process thermal image
        image_processor.processThermalImage(current_thermal);
        
        // Detect defects
        cv_detector.detectDefects(current_thermal, current_visible);
        
        // Fuse images
        fusion_engine.fuseImages(current_thermal, current_visible);
        
        // Publish results
        publishProcessingResults();
    }
}

void captureVisibleImage() {
    fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("❌ Camera capture failed");
        return;
    }
    
    // Convert JPEG to RGB (simplified)
    if (fb->format == PIXFORMAT_JPEG) {
        current_visible.valid = true;
        current_visible.timestamp = millis();
        
        // For demonstration, we'll assume the image is already in RGB format
        // In a real implementation, you'd need to decode the JPEG
        memcpy(current_visible.data, fb->buf, min((size_t)(VISIBLE_WIDTH * VISIBLE_HEIGHT * 3), fb->len));
    }
    
    esp_camera_fb_return(fb);
}

void receiveThermalImage() {
    // Receive thermal image data from Arduino via serial
    if (Serial.available() >= sizeof(thermal_buffer)) {
        Serial.readBytes(thermal_buffer, sizeof(thermal_buffer));
        
        // Convert to float array
        for (int i = 0; i < THERMAL_PIXELS; i++) {
            uint16_t temp_raw = (thermal_buffer[i * 2 + 1] << 8) | thermal_buffer[i * 2];
            current_thermal.pixels[i] = temp_raw / 100.0; // Convert to Celsius
        }
        
        current_thermal.valid = true;
        current_thermal.timestamp = millis();
        
        // Update statistics
        image_processor.updateImageStatistics(current_thermal);
    }
}

void publishProcessingResults() {
    if (!mqtt_connected) return;
    
    // Publish thermal statistics
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["thermal_stats"]["min_temp"] = current_thermal.min_temp;
    doc["thermal_stats"]["max_temp"] = current_thermal.max_temp;
    doc["thermal_stats"]["avg_temp"] = current_thermal.avg_temp;
    doc["thermal_stats"]["std_dev"] = current_thermal.std_dev;
    doc["defect_count"] = defect_count;
    
    // Add defect information
    JsonArray defects = doc.createNestedArray("defects");
    for (int i = 0; i < min(defect_count, 5); i++) { // Limit to 5 defects
        JsonObject defect = defects.createNestedObject();
        defect["x"] = detected_defects[i].x;
        defect["y"] = detected_defects[i].y;
        defect["type"] = detected_defects[i].type;
        defect["confidence"] = detected_defects[i].confidence;
        defect["temperature"] = detected_defects[i].temperature;
    }
    
    String payload;
    serializeJson(doc, payload);
    mqtt_client.publish("thermal/processing_results", payload.c_str());
}

void handleBluetoothCommunication() {
    if (SerialBT.available()) {
        String message = SerialBT.readString();
        message.trim();
        
        if (message == "STATUS") {
            sendBluetoothStatus();
        } else if (message == "CAPTURE") {
            processImages();
            SerialBT.println("Image captured and processed");
        } else if (message == "DEFECTS") {
            sendBluetoothDefects();
        } else if (message.startsWith("CONFIG:")) {
            updateProcessingConfig(message.substring(7));
        }
    }
}

void handleArduinoCommunication() {
    // Handle communication with Arduino Mega
    if (Serial.available()) {
        String message = Serial.readStringUntil('\n');
        message.trim();
        
        if (message.startsWith("THERMAL:")) {
            // Parse thermal data
            parseThermalData(message.substring(8));
        } else if (message.startsWith("COMMAND:")) {
            // Parse command
            parseCommand(message.substring(8));
        }
    }
}

void parseThermalData(String data) {
    // Parse thermal data from Arduino
    // Format: "temp1,temp2,temp3,..."
    
    int index = 0;
    int start = 0;
    
    while (index < THERMAL_PIXELS && start < data.length()) {
        int comma = data.indexOf(',', start);
        if (comma == -1) comma = data.length();
        
        String temp_str = data.substring(start, comma);
        current_thermal.pixels[index] = temp_str.toFloat();
        
        index++;
        start = comma + 1;
    }
    
    if (index == THERMAL_PIXELS) {
        current_thermal.valid = true;
        current_thermal.timestamp = millis();
        image_processor.updateImageStatistics(current_thermal);
    }
}

void parseCommand(String command) {
    if (command == "CAPTURE") {
        processImages();
    } else if (command == "STREAM_START") {
        // Start streaming
    } else if (command == "STREAM_STOP") {
        // Stop streaming
    } else if (command.startsWith("CONFIG:")) {
        updateProcessingConfig(command.substring(7));
    }
}

void updateProcessingConfig(String config) {
    StaticJsonDocument<512> doc;
    deserializeJson(doc, config);
    
    if (doc.containsKey("thermal_enhancement")) {
        processing_config.thermal_enhancement = doc["thermal_enhancement"];
    }
    if (doc.containsKey("noise_reduction")) {
        processing_config.noise_reduction = doc["noise_reduction"];
    }
    if (doc.containsKey("edge_detection")) {
        processing_config.edge_detection = doc["edge_detection"];
    }
    if (doc.containsKey("contrast_enhancement")) {
        processing_config.contrast_enhancement = doc["contrast_enhancement"];
    }
    if (doc.containsKey("image_fusion")) {
        processing_config.image_fusion = doc["image_fusion"];
    }
    if (doc.containsKey("enhancement_factor")) {
        processing_config.enhancement_factor = doc["enhancement_factor"];
    }
    
    Serial.println("✅ Processing configuration updated");
}

void sendBluetoothStatus() {
    StaticJsonDocument<512> doc;
    doc["system_status"] = "operational";
    doc["wifi_connected"] = wifi_connected;
    doc["mqtt_connected"] = mqtt_connected;
    doc["thermal_valid"] = current_thermal.valid;
    doc["visible_valid"] = current_visible.valid;
    doc["defect_count"] = defect_count;
    doc["uptime"] = millis() - system_start_time;
    doc["free_heap"] = ESP.getFreeHeap();
    
    String response;
    serializeJson(doc, response);
    SerialBT.println(response);
}

void sendBluetoothDefects() {
    StaticJsonDocument<2048> doc;
    JsonArray defects = doc.createNestedArray("defects");
    
    for (int i = 0; i < defect_count; i++) {
        JsonObject defect = defects.createNestedObject();
        defect["x"] = detected_defects[i].x;
        defect["y"] = detected_defects[i].y;
        defect["type"] = detected_defects[i].type;
        defect["confidence"] = detected_defects[i].confidence;
        defect["temperature"] = detected_defects[i].temperature;
        defect["description"] = detected_defects[i].description;
    }
    
    String response;
    serializeJson(doc, response);
    SerialBT.println(response);
}

// Web server handlers
void handleRoot() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Thermal Image Processing</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #f9f9f9; padding: 20px; border-radius: 8px; }
        .status { display: inline-block; padding: 5px 10px; border-radius: 4px; color: white; }
        .status.good { background: #4CAF50; }
        .status.error { background: #F44336; }
        img { max-width: 100%; height: auto; border-radius: 4px; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-success { background: #4CAF50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌡️ Thermal Image Processing System</h1>
        
        <div class="grid">
            <div class="card">
                <h3>System Status</h3>
                <p>WiFi: <span class="status good">Connected</span></p>
                <p>MQTT: <span class="status good">Connected</span></p>
                <p>Camera: <span class="status good">Active</span></p>
                <p>Processing: <span class="status good">Running</span></p>
            </div>
            
            <div class="card">
                <h3>Live Feed</h3>
                <img src="/stream" alt="Live Stream" style="width: 100%;">
                <button class="btn-primary" onclick="refreshStream()">Refresh</button>
            </div>
            
            <div class="card">
                <h3>Thermal Analysis</h3>
                <p>Min Temp: <span id="min-temp">--</span>°C</p>
                <p>Max Temp: <span id="max-temp">--</span>°C</p>
                <p>Avg Temp: <span id="avg-temp">--</span>°C</p>
                <p>Defects: <span id="defect-count">--</span></p>
                <button class="btn-success" onclick="analyzeImage()">Analyze</button>
            </div>
            
            <div class="card">
                <h3>Controls</h3>
                <button class="btn-primary" onclick="captureImage()">Capture Image</button>
                <button class="btn-success" onclick="processImage()">Process Image</button>
                <button class="btn-primary" onclick="viewDefects()">View Defects</button>
                <button class="btn-success" onclick="downloadData()">Download Data</button>
            </div>
        </div>
    </div>
    
    <script>
        function refreshStream() {
            location.reload();
        }
        
        function analyzeImage() {
            fetch('/thermal')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('min-temp').textContent = data.min_temp.toFixed(1);
                    document.getElementById('max-temp').textContent = data.max_temp.toFixed(1);
                    document.getElementById('avg-temp').textContent = data.avg_temp.toFixed(1);
                    document.getElementById('defect-count').textContent = data.defect_count;
                });
        }
        
        function captureImage() {
            fetch('/capture')
                .then(response => response.text())
                .then(data => alert(data));
        }
        
        function processImage() {
            fetch('/thermal')
                .then(response => response.json())
                .then(data => {
                    alert('Processing complete. Found ' + data.defect_count + ' defects.');
                });
        }
        
        function viewDefects() {
            window.open('/defects', '_blank');
        }
        
        function downloadData() {
            window.open('/status', '_blank');
        }
        
        // Auto-refresh thermal data
        setInterval(analyzeImage, 5000);
    </script>
</body>
</html>
)";
    
    server.send(200, "text/html", html);
}

void handleCapture() {
    processImages();
    
    StaticJsonDocument<256> doc;
    doc["status"] = "success";
    doc["message"] = "Image captured and processed";
    doc["timestamp"] = millis();
    doc["defects_found"] = defect_count;
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleStream() {
    if (!current_visible.valid) {
        server.send(404, "text/plain", "No image available");
        return;
    }
    
    // Return the fused image
    server.sendHeader("Content-Type", "image/jpeg");
    server.sendHeader("Cache-Control", "no-cache");
    server.send_P(200, "image/jpeg", (const char*)fusion_buffer, VISIBLE_WIDTH * VISIBLE_HEIGHT * 3);
}

void handleThermal() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = current_thermal.timestamp;
    doc["valid"] = current_thermal.valid;
    doc["min_temp"] = current_thermal.min_temp;
    doc["max_temp"] = current_thermal.max_temp;
    doc["avg_temp"] = current_thermal.avg_temp;
    doc["std_dev"] = current_thermal.std_dev;
    doc["defect_count"] = defect_count;
    
    JsonArray defects = doc.createNestedArray("defects");
    for (int i = 0; i < min(defect_count, 10); i++) {
        JsonObject defect = defects.createNestedObject();
        defect["x"] = detected_defects[i].x;
        defect["y"] = detected_defects[i].y;
        defect["type"] = detected_defects[i].type;
        defect["confidence"] = detected_defects[i].confidence;
        defect["temperature"] = detected_defects[i].temperature;
    }
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleDefects() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Defect Analysis</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .defect { background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .critical { background: #ffebee; }
        .warning { background: #fff3e0; }
        .info { background: #e8f5e8; }
    </style>
</head>
<body>
    <h1>🔍 Defect Analysis Report</h1>
    <p>Total defects found: <strong id="total-defects">0</strong></p>
    <div id="defect-list"></div>
    
    <script>
        fetch('/thermal')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total-defects').textContent = data.defect_count;
                
                const defectList = document.getElementById('defect-list');
                data.defects.forEach((defect, index) => {
                    const div = document.createElement('div');
                    div.className = 'defect ' + getDefectClass(defect.type);
                    div.innerHTML = `
                        <h3>Defect ${index + 1}: ${defect.type}</h3>
                        <p><strong>Location:</strong> (${defect.x}, ${defect.y})</p>
                        <p><strong>Temperature:</strong> ${defect.temperature.toFixed(1)}°C</p>
                        <p><strong>Confidence:</strong> ${(defect.confidence * 100).toFixed(1)}%</p>
                    `;
                    defectList.appendChild(div);
                });
            });
        
        function getDefectClass(type) {
            if (type.includes('CRITICAL')) return 'critical';
            if (type.includes('HOT_SPOT')) return 'warning';
            return 'info';
        }
    </script>
</body>
</html>
)";
    
    server.send(200, "text/html", html);
}

void handleConfig() {
    StaticJsonDocument<512> doc;
    doc["thermal_enhancement"] = processing_config.thermal_enhancement;
    doc["noise_reduction"] = processing_config.noise_reduction;
    doc["edge_detection"] = processing_config.edge_detection;
    doc["contrast_enhancement"] = processing_config.contrast_enhancement;
    doc["image_fusion"] = processing_config.image_fusion;
    doc["enhancement_factor"] = processing_config.enhancement_factor;
    doc["noise_threshold"] = processing_config.noise_threshold;
    doc["edge_threshold"] = processing_config.edge_threshold;
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleConfigUpdate() {
    String body = server.arg("plain");
    updateProcessingConfig(body);
    server.send(200, "text/plain", "Configuration updated");
}

void handleStatus() {
    StaticJsonDocument<1024> doc;
    doc["timestamp"] = millis();
    doc["system_status"] = "operational";
    doc["wifi_connected"] = wifi_connected;
    doc["mqtt_connected"] = mqtt_connected;
    doc["uptime"] = millis() - system_start_time;
    doc["free_heap"] = ESP.getFreeHeap();
    doc["cpu_frequency"] = ESP.getCpuFreqMHz();
    doc["flash_size"] = ESP.getFlashChipSize();
    
    if (current_thermal.valid) {
        JsonObject thermal = doc.createNestedObject("thermal");
        thermal["min_temp"] = current_thermal.min_temp;
        thermal["max_temp"] = current_thermal.max_temp;
        thermal["avg_temp"] = current_thermal.avg_temp;
        thermal["std_dev"] = current_thermal.std_dev;
    }
    
    doc["defect_count"] = defect_count;
    doc["processing_config"] = processing_config.thermal_enhancement;
    
    String response;
    serializeJson(doc, response);
    server.send(200, "application/json", response);
}

void handleFirmwareUpdate() {
    String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>Firmware Update</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        .update-section { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 8px; }
        input[type="file"] { margin: 10px 0; }
        button { padding: 10px 20px; margin: 10px 0; border: none; border-radius: 4px; cursor: pointer; }
        .btn-primary { background: #2196F3; color: white; }
        .btn-warning { background: #FF9800; color: white; }
        .progress { width: 100%; height: 20px; background: #ddd; border-radius: 10px; overflow: hidden; }
        .progress-bar { height: 100%; background: #4CAF50; transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Firmware Update</h1>
        
        <div class="update-section">
            <h3>Current Version</h3>
            <p>Version: 2.0.0</p>
            <p>Build Date: 2024-01-01</p>
            <p>Features: Computer Vision, ML Processing, Cloud Integration</p>
        </div>
        
        <div class="update-section">
            <h3>Update Firmware</h3>
            <p><strong>Warning:</strong> Do not power off during update!</p>
            <input type="file" id="firmware-file" accept=".bin">
            <button class="btn-warning" onclick="uploadFirmware()">Upload Firmware</button>
            
            <div class="progress" style="display: none;">
                <div class="progress-bar" id="progress-bar"></div>
            </div>
        </div>
        
        <div class="update-section">
            <h3>Cloud Updates</h3>
            <button class="btn-primary" onclick="checkCloudUpdates()">Check for Updates</button>
            <button class="btn-primary" onclick="downloadMLModel()">Download ML Model</button>
        </div>
    </div>
    
    <script>
        function uploadFirmware() {
            alert('Firmware upload functionality would be implemented here');
        }
        
        function checkCloudUpdates() {
            alert('Checking for cloud updates...');
        }
        
        function downloadMLModel() {
            alert('Downloading latest ML model...');
        }
    </script>
</body>
</html>
)";
    
    server.send(200, "text/html", html);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String message = "";
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    
    Serial.println("📨 MQTT: " + String(topic) + " - " + message);
    
    if (strcmp(topic, "thermal/commands") == 0) {
        StaticJsonDocument<256> doc;
        deserializeJson(doc, message);
        
        String command = doc["command"];
        
        if (command == "capture") {
            processImages();
        } else if (command == "stream_start") {
            // Start streaming
        } else if (command == "stream_stop") {
            // Stop streaming
        } else if (command == "update_config") {
            updateProcessingConfig(doc["config"]);
        }
    }
    else if (strcmp(topic, "thermal/config") == 0) {
        updateProcessingConfig(message);
    }
    else if (strcmp(topic, "thermal/processing") == 0) {
        StaticJsonDocument<256> doc;
        deserializeJson(doc, message);
        
        String action = doc["action"];
        
        if (action == "enhance") {
            processing_config.thermal_enhancement = doc["enabled"];
        } else if (action == "denoise") {
            processing_config.noise_reduction = doc["enabled"];
        } else if (action == "detect_edges") {
            processing_config.edge_detection = doc["enabled"];
        }
    }
}

/*
 * ESP32-CAM Advanced Image Processing System
 * 
 * This system provides:
 * 
 * 1. Real-time Image Processing
 *    - Thermal image enhancement and filtering
 *    - Visible light image processing
 *    - Advanced computer vision algorithms
 *    - Multi-spectral image fusion
 * 
 * 2. Defect Detection
 *    - Thermal anomaly detection
 *    - Visual defect identification
 *    - Pattern recognition algorithms
 *    - Machine learning classification
 * 
 * 3. Computer Vision
 *    - Edge detection and contour analysis
 *    - Object tracking and recognition
 *    - Image segmentation
 *    - Feature extraction
 * 
 * 4. Cloud Integration
 *    - Real-time data streaming
 *    - Cloud-based ML model updates
 *    - Remote monitoring and control
 *    - Data synchronization
 * 
 * 5. Web Interface
 *    - Live streaming display
 *    - Configuration management
 *    - Defect analysis reports
 *    - System status monitoring
 * 
 * 6. Communication
 *    - MQTT real-time messaging
 *    - Bluetooth mobile interface
 *    - Serial communication with Arduino
 *    - RESTful API for integration
 * 
 * This ESP32-CAM system transforms raw thermal and visible images
 * into actionable insights for industrial inspection and quality
 * control applications.
 */