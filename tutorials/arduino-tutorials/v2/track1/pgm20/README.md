# Program 20: Infrared Thermography System

🌡️ **MISSION PREVIEW**: Get ready to become a **Thermal Imaging Engineer** and design advanced infrared thermography systems with automated inspection and defect detection!

## Overview
This project creates a professional-grade infrared thermography system with thermal imaging, automated inspection, and defect detection capabilities. It builds upon all previous thermal engineering concepts while introducing advanced computer vision, image processing, and automated non-destructive testing techniques.

## 🧠 Fundamental Concepts Reinforced

### From Program 19 (Thermal Conductivity Measurement):
- **Precision temperature measurement** and calibration
- **Multi-method measurement** integration
- **Standards compliance** and quality assurance
- **Advanced data analysis** and uncertainty quantification

### From Program 18 (Heat Exchanger Monitor):
- **Real-time thermal monitoring** and analysis
- **Predictive maintenance** algorithms
- **Performance optimization** techniques
- **Industrial IoT integration**

### From Program 17 (PCM Controller):
- **Phase change detection** and thermal analysis
- **Energy storage optimization**
- **Multi-zone thermal management**
- **Advanced thermal modeling**

### From Program 16 (Multi-Zone Thermal):
- **Multi-zone temperature control**
- **Safety system integration**
- **Real-time monitoring** and control
- **Data logging** and analytics

### New Advanced Thermal Imaging Concepts:
- **Infrared thermography**: Non-contact temperature measurement and imaging
- **Thermal image processing**: Advanced algorithms for defect detection
- **Computer vision**: Automated inspection and pattern recognition
- **Radiometric analysis**: Quantitative temperature measurement from thermal images
- **Thermal signature analysis**: Identification of thermal patterns and anomalies
- **Automated inspection**: Machine learning-based defect classification
- **Multi-spectral imaging**: Integration of visible and thermal imaging
- **Thermal time series analysis**: Dynamic thermal behavior monitoring

## Components Required

### Core Electronics:
- **Arduino Mega 2560** (1x) - Main system controller
- **ESP32-CAM Development Board** (1x) - Image processing and WiFi connectivity
- **Raspberry Pi 4** (1x) - Advanced image processing and ML inference
- **MLX90640 Thermal Camera** (1x) - 32x24 thermal imaging sensor
- **FLIR Lepton 3.5 Module** (1x) - High-resolution thermal imaging (Optional)
- **OV2640 Camera Module** (1x) - Visible light imaging
- **Servo Motors** (2x) - Pan/tilt camera positioning
- **Stepper Motors** (2x) - Precision positioning system
- **Motor Driver Shields** (2x) - Motor control electronics

### Advanced Instrumentation:
- **Thermal Reference Sources** (3x) - Calibrated temperature references
- **Blackbody Calibration Source** (1x) - Radiometric calibration
- **Motorized Filter Wheel** (1x) - Multi-spectral imaging capability
- **Precision Thermistors** (4x) - Reference temperature measurement
- **Ambient Light Sensors** (2x) - Environmental monitoring
- **Humidity/Pressure Sensors** (2x) - Environmental compensation
- **Laser Distance Sensor** (1x) - Object distance measurement
- **RGB LED Array** (1x) - Illumination control

### Mechanical Components:
- **Pan/Tilt Mount** (1x) - Camera positioning system
- **Linear Actuators** (2x) - Sample positioning
- **Precision Stages** (2x) - XY positioning for samples
- **Vibration Isolation** (1x) - System stability
- **Thermal Isolation** (1x) - Temperature stability
- **Optical Bench** (1x) - Stable platform for components
- **Enclosure** (1x) - Environmental protection

### Display and Interface:
- **7" TFT Display** (1x) - Real-time image display
- **Touch Screen Interface** (1x) - User interaction
- **Status LED Arrays** (1x) - System status indication
- **Buzzer/Alarm** (1x) - Alert system
- **Membrane Keypad** (1x) - Manual controls
- **Emergency Stop Button** (1x) - Safety system

### Power and Safety:
- **24V Power Supply** (1x, 5A) - Main system power
- **12V Power Supply** (1x, 3A) - Motor and actuator power
- **5V Power Supply** (1x, 10A) - Logic and sensor power
- **UPS Battery Backup** (1x) - Power continuity
- **Isolation Transformers** (2x) - Electrical safety
- **Current Monitoring** (4x) - Power consumption monitoring
- **Thermal Fuses** (4x) - Overtemperature protection

## Circuit Diagram

```
Infrared Thermography System Architecture

Arduino Mega 2560 (Main Controller)
├── Thermal Imaging Sensors
│   ├── MLX90640 → I2C Bus (32x24 thermal array)
│   ├── FLIR Lepton 3.5 → SPI Bus (160x120 thermal array)
│   ├── OV2640 Camera → Serial Interface (Visible light)
│   ├── Reference Thermistors → Analog Inputs (A0-A3)
│   └── Ambient Sensors → I2C Bus (Temperature, Humidity)
├── Motion Control System
│   ├── Pan Servo → PWM Pin 2
│   ├── Tilt Servo → PWM Pin 3
│   ├── X-Axis Stepper → Pins 4-7 (Dir, Step, Enable, Limit)
│   ├── Y-Axis Stepper → Pins 8-11 (Dir, Step, Enable, Limit)
│   ├── Z-Axis Linear → PWM Pin 12 (Focus control)
│   └── Filter Wheel → PWM Pin 13 (Spectral selection)
├── Calibration System
│   ├── Blackbody Source → Relay Pin 22 (On/Off control)
│   ├── Reference Heater → PWM Pin 23 (Temperature control)
│   ├── Calibration Standards → Digital Pins 24-27
│   └── Ambient Compensation → I2C Sensors
├── Safety and Monitoring
│   ├── Emergency Stop → Pin 21 (Interrupt)
│   ├── Overtemperature → Pin 20 (Interrupt)
│   ├── System Fault → Pin 19 (Interrupt)
│   ├── Power Monitoring → I2C Current Sensors
│   └── Vibration Detection → Pin 18 (Interrupt)
├── User Interface
│   ├── TFT Display → SPI Interface
│   ├── Touch Screen → SPI Interface
│   ├── Status LEDs → Digital Pins 30-37
│   ├── Keypad → Digital Pins 38-45
│   └── Buzzer → PWM Pin 46
├── Data Storage
│   ├── SD Card → SPI Interface
│   ├── EEPROM → I2C Interface
│   └── External Memory → SPI Interface
└── Communication
    ├── ESP32-CAM → Serial1 (Image processing)
    ├── Raspberry Pi → Serial2 (ML processing)
    ├── Ethernet → SPI Interface
    └── WiFi → ESP32 Module

ESP32-CAM (Image Processing Unit)
├── Camera Interface
│   ├── Thermal Image Acquisition → MLX90640/Lepton
│   ├── Visible Image Acquisition → OV2640
│   ├── Image Preprocessing → ESP32 CPU
│   └── Real-time Processing → Dual Core
├── Image Processing Algorithms
│   ├── Thermal Calibration → Radiometric conversion
│   ├── Noise Reduction → Spatial/temporal filtering
│   ├── Image Enhancement → Contrast, sharpening
│   ├── Feature Detection → Edge detection, blob analysis
│   └── Object Tracking → Motion detection
├── Communication
│   ├── WiFi Connection → Cloud services
│   ├── MQTT Publishing → Real-time data
│   ├── HTTP Server → Web interface
│   └── Serial Communication → Arduino coordination
└── Storage
    ├── Local Image Storage → SD Card
    ├── Configuration Storage → SPIFFS
    └── Temporary Processing → RAM

Raspberry Pi 4 (Advanced Processing)
├── Machine Learning Pipeline
│   ├── TensorFlow Lite → Defect detection models
│   ├── OpenCV → Computer vision processing
│   ├── Scikit-learn → Statistical analysis
│   └── PyTorch → Deep learning inference
├── Advanced Analytics
│   ├── Thermal Pattern Recognition → Anomaly detection
│   ├── Defect Classification → ML-based categorization
│   ├── Trend Analysis → Time series analysis
│   ├── Predictive Maintenance → Failure prediction
│   └── Quality Assessment → Automated scoring
├── Data Management
│   ├── Database → SQLite/PostgreSQL
│   ├── Time Series → InfluxDB
│   ├── Image Archive → File system
│   └── Report Generation → PDF/HTML
├── Network Services
│   ├── REST API → System integration
│   ├── WebSocket → Real-time updates
│   ├── MQTT Client → IoT communication
│   └── SSH/VNC → Remote access
└── Integration
    ├── Serial Communication → Arduino/ESP32
    ├── GPIO Interface → Hardware control
    ├── Camera Interface → Direct capture
    └── Network Interface → Cloud connectivity

Cloud Services Integration
├── Image Storage → AWS S3/Google Cloud
├── ML Model Training → Cloud ML platforms
├── Data Analytics → Big data processing
├── Remote Monitoring → Dashboard services
├── Alert Management → Notification systems
├── API Gateway → Service integration
├── Database Services → Cloud databases
└── Backup/Archive → Long-term storage
```

## Physical Setup

### Thermal Imaging Laboratory Layout:
```
┌─────────────────────────────────────────────────────────────────────┐
│                  Thermal Imaging Laboratory                         │
│                                                                     │
│  Imaging Station:                                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Thermal Camera     Pan/Tilt Mount     Visible Camera       │   │
│  │ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │   │
│  │ │ MLX90640    │    │   Servo     │    │   OV2640    │      │   │
│  │ │ 32x24 Array │ ── │   Control   │ ── │   Module    │      │   │
│  │ │ Thermal     │    │   System    │    │   Visible   │      │   │
│  │ │ Sensor      │    │             │    │   Light     │      │   │
│  │ └─────────────┘    └─────────────┘    └─────────────┘      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Sample Positioning System:                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ X-Y Stage          Sample Holder      Z-Axis Control       │   │
│  │ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │   │
│  │ │ Stepper     │    │   Sample    │    │   Linear    │      │   │
│  │ │ Motor XY    │ ── │   Platform  │ ── │   Actuator  │      │   │
│  │ │ Precision   │    │   Heated    │    │   Focus     │      │   │
│  │ │ Stages      │    │   Stage     │    │   Control   │      │   │
│  │ └─────────────┘    └─────────────┘    └─────────────┘      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Calibration System:                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Blackbody Source   Reference Temps    Filter Wheel         │   │
│  │ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │   │
│  │ │ Calibrated  │    │ Thermistor  │    │ Spectral    │      │   │
│  │ │ Temperature │    │ References  │    │ Selection   │      │   │
│  │ │ Sources     │    │ RTD Array   │    │ Automated   │      │   │
│  │ │ Standards   │    │ Calibrated  │    │ Switching   │      │   │
│  │ └─────────────┘    └─────────────┘    └─────────────┘      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Control and Processing Center:                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│  │   Arduino   │  │   ESP32     │  │ Raspberry   │                │
│  │    Mega     │  │    CAM      │  │    Pi 4     │                │
│  │   System    │  │   Image     │  │   ML/AI     │                │
│  │   Control   │  │ Processing  │  │ Processing  │                │
│  │ Motion/Cal  │  │ Real-time   │  │ Analytics   │                │
│  └─────────────┘  └─────────────┘  └─────────────┘                │
│                                                                     │
│  User Interface:                                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Touch Display     Status LEDs      Control Panel           │   │
│  │ ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │   │
│  │ │ 7" TFT      │    │ System      │    │ Emergency   │      │   │
│  │ │ Real-time   │    │ Status      │    │ Stop        │      │   │
│  │ │ Images      │    │ Indicators  │    │ Manual      │      │   │
│  │ │ Analysis    │    │ Alarms      │    │ Controls    │      │   │
│  │ └─────────────┘    └─────────────┘    └─────────────┘      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Environmental Control:                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Temperature | Humidity | Lighting | Vibration Isolation    │   │
│  │   ±0.5°C    |  ±2% RH  | LED Array| Anti-vibration Pads   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Setup Instructions

### Phase 1: Hardware Assembly (6-8 hours)

#### 1. Thermal Camera Integration
```cpp
// MLX90640 thermal camera configuration
#define MLX90640_I2C_ADDR 0x33
#define MLX90640_RESOLUTION 32*24
#define MLX90640_REFRESH_RATE 8 // Hz

class ThermalCamera {
private:
    MLX90640_I2C_Driver i2c_driver;
    float thermal_image[MLX90640_RESOLUTION];
    float calibration_offset;
    float calibration_gain;
    
public:
    void initialize() {
        i2c_driver.begin();
        
        // Configure refresh rate
        MLX90640_SetRefreshRate(MLX90640_I2C_ADDR, MLX90640_REFRESH_RATE);
        
        // Set resolution
        MLX90640_SetResolution(MLX90640_I2C_ADDR, 0x00); // 18-bit
        
        // Calibrate camera
        performCalibration();
        
        Serial.println("✅ MLX90640 thermal camera initialized");
    }
    
    void captureImage() {
        // Capture thermal image
        MLX90640_GetFrameData(MLX90640_I2C_ADDR, thermal_image);
        
        // Apply calibration
        applyCalibratedCorrection();
        
        // Apply temperature compensation
        applyTemperatureCompensation();
    }
    
    float getPixelTemperature(int x, int y) {
        int index = y * 32 + x;
        if (index >= 0 && index < MLX90640_RESOLUTION) {
            return thermal_image[index];
        }
        return -999.0; // Invalid
    }
    
    void performCalibration() {
        // Calibrate with blackbody source
        calibrateWithBlackbody();
        
        // Compensate for ambient temperature
        compensateAmbientTemperature();
        
        // Non-uniformity correction
        performNonUniformityCorrection();
    }
};
```

#### 2. Motion Control System
```cpp
// Pan/Tilt and XY positioning system
class MotionControl {
private:
    Servo pan_servo;
    Servo tilt_servo;
    StepperMotor x_stepper;
    StepperMotor y_stepper;
    
    float current_pan, current_tilt;
    float current_x, current_y;
    float position_accuracy;
    
public:
    void initialize() {
        // Initialize servos
        pan_servo.attach(2);
        tilt_servo.attach(3);
        
        // Initialize steppers
        x_stepper.initialize(4, 5, 6, 7); // Direction, Step, Enable, Limit
        y_stepper.initialize(8, 9, 10, 11);
        
        // Home all axes
        homeAllAxes();
        
        position_accuracy = 0.1; // mm
        
        Serial.println("✅ Motion control system initialized");
    }
    
    void setPanTilt(float pan_angle, float tilt_angle) {
        // Move to specified pan/tilt position
        current_pan = constrain(pan_angle, -180, 180);
        current_tilt = constrain(tilt_angle, -90, 90);
        
        pan_servo.write(map(current_pan, -180, 180, 0, 180));
        tilt_servo.write(map(current_tilt, -90, 90, 0, 180));
        
        delay(500); // Allow time for movement
    }
    
    void setXYPosition(float x_pos, float y_pos) {
        // Move to specified XY position
        float x_steps = (x_pos - current_x) / position_accuracy;
        float y_steps = (y_pos - current_y) / position_accuracy;
        
        x_stepper.moveTo(x_steps);
        y_stepper.moveTo(y_steps);
        
        current_x = x_pos;
        current_y = y_pos;
    }
    
    void performScanPattern(ScanPattern pattern) {
        switch (pattern) {
            case GRID_SCAN:
                performGridScan();
                break;
            case SPIRAL_SCAN:
                performSpiralScan();
                break;
            case CUSTOM_SCAN:
                performCustomScan();
                break;
        }
    }
    
    void performGridScan() {
        float start_x = -50.0; // mm
        float end_x = 50.0;
        float start_y = -50.0;
        float end_y = 50.0;
        float step_size = 5.0; // mm
        
        for (float y = start_y; y <= end_y; y += step_size) {
            for (float x = start_x; x <= end_x; x += step_size) {
                setXYPosition(x, y);
                delay(200); // Allow settling
                
                // Capture image at this position
                captureImageAtPosition(x, y);
            }
        }
    }
    
    void homeAllAxes() {
        // Home all motion axes
        setPanTilt(0, 0);
        setXYPosition(0, 0);
        
        Serial.println("✅ All axes homed");
    }
};
```

#### 3. Calibration System
```cpp
// Blackbody and reference calibration system
class CalibrationSystem {
private:
    float blackbody_temperatures[5];
    float reference_temperatures[4];
    bool calibration_valid;
    
public:
    void initialize() {
        // Initialize blackbody source
        pinMode(22, OUTPUT); // Blackbody control relay
        digitalWrite(22, LOW);
        
        // Initialize reference thermistors
        for (int i = 0; i < 4; i++) {
            pinMode(A0 + i, INPUT);
        }
        
        // Set calibration temperatures
        blackbody_temperatures[0] = 0.0;   // Ice bath
        blackbody_temperatures[1] = 25.0;  // Room temperature
        blackbody_temperatures[2] = 50.0;  // Heated reference
        blackbody_temperatures[3] = 75.0;  // High temperature
        blackbody_temperatures[4] = 100.0; // Boiling water
        
        calibration_valid = false;
        
        Serial.println("✅ Calibration system initialized");
    }
    
    void performFullCalibration() {
        Serial.println("🔧 Starting full system calibration...");
        
        // Warm up blackbody source
        warmUpBlackbody();
        
        // Calibrate at each temperature point
        for (int i = 0; i < 5; i++) {
            calibrateAtTemperature(blackbody_temperatures[i]);
        }
        
        // Validate calibration
        validateCalibration();
        
        calibration_valid = true;
        
        Serial.println("✅ Full calibration complete");
    }
    
    void calibrateAtTemperature(float target_temp) {
        Serial.println("📊 Calibrating at " + String(target_temp, 1) + "°C");
        
        // Set blackbody to target temperature
        setBlackbodyTemperature(target_temp);
        
        // Wait for thermal equilibrium
        waitForThermalEquilibrium(target_temp);
        
        // Capture reference measurements
        captureReferenceData(target_temp);
        
        // Update calibration coefficients
        updateCalibrationCoefficients();
    }
    
    void setBlackbodyTemperature(float temperature) {
        // Control blackbody source temperature
        float control_value = map(temperature, 0, 100, 0, 255);
        analogWrite(23, control_value); // PWM control
        
        digitalWrite(22, HIGH); // Enable blackbody
    }
    
    void waitForThermalEquilibrium(float target_temp) {
        bool equilibrium_reached = false;
        unsigned long start_time = millis();
        
        while (!equilibrium_reached && (millis() - start_time) < 300000) { // 5 minutes max
            float current_temp = readReferenceTemperature();
            
            if (abs(current_temp - target_temp) < 0.5) {
                // Check stability for 30 seconds
                if (checkTemperatureStability(target_temp, 30000)) {
                    equilibrium_reached = true;
                }
            }
            
            delay(1000);
        }
        
        if (equilibrium_reached) {
            Serial.println("✅ Thermal equilibrium reached");
        } else {
            Serial.println("⚠️ Thermal equilibrium timeout");
        }
    }
    
    float readReferenceTemperature() {
        // Read calibrated reference thermistor
        int adc_value = analogRead(A0);
        float voltage = adc_value * 5.0 / 1023.0;
        
        // Convert to temperature (Steinhart-Hart equation)
        float resistance = 10000.0 * voltage / (5.0 - voltage);
        float temperature = 1.0 / (0.001129148 + 0.000234125 * log(resistance) + 
                                  0.0000000876741 * pow(log(resistance), 3));
        temperature -= 273.15; // Convert to Celsius
        
        return temperature;
    }
    
    bool checkTemperatureStability(float target_temp, unsigned long duration) {
        unsigned long start_time = millis();
        float temp_sum = 0;
        int sample_count = 0;
        
        while ((millis() - start_time) < duration) {
            float temp = readReferenceTemperature();
            temp_sum += temp;
            sample_count++;
            
            delay(1000);
        }
        
        float average_temp = temp_sum / sample_count;
        return (abs(average_temp - target_temp) < 0.2);
    }
    
    void validateCalibration() {
        Serial.println("🔍 Validating calibration...");
        
        // Test at known temperature
        float test_temp = 37.0; // Body temperature
        setBlackbodyTemperature(test_temp);
        waitForThermalEquilibrium(test_temp);
        
        // Measure with thermal camera
        float measured_temp = thermal_camera.getPixelTemperature(16, 12); // Center pixel
        float reference_temp = readReferenceTemperature();
        
        float accuracy = abs(measured_temp - reference_temp);
        
        Serial.println("📊 Calibration Validation:");
        Serial.println("   Reference: " + String(reference_temp, 2) + "°C");
        Serial.println("   Measured: " + String(measured_temp, 2) + "°C");
        Serial.println("   Accuracy: ±" + String(accuracy, 2) + "°C");
        
        if (accuracy < 1.0) {
            Serial.println("✅ Calibration validation PASSED");
        } else {
            Serial.println("❌ Calibration validation FAILED");
        }
    }
};
```

### Phase 2: Image Processing Implementation (4-6 hours)

#### 1. Thermal Image Processing
```cpp
// Advanced thermal image processing
class ThermalImageProcessor {
private:
    float processed_image[32][24];
    float gradient_image[32][24];
    float filtered_image[32][24];
    
public:
    void processImage(float* raw_image) {
        // Convert linear array to 2D
        linearTo2D(raw_image);
        
        // Apply spatial filtering
        applySpatialFiltering();
        
        // Apply temporal filtering
        applyTemporalFiltering();
        
        // Calculate temperature gradients
        calculateTemperatureGradients();
        
        // Enhance contrast
        enhanceContrast();
        
        // Apply false color mapping
        applyFalseColorMapping();
    }
    
    void linearTo2D(float* raw_image) {
        for (int y = 0; y < 24; y++) {
            for (int x = 0; x < 32; x++) {
                processed_image[x][y] = raw_image[y * 32 + x];
            }
        }
    }
    
    void applySpatialFiltering() {
        // Apply Gaussian filter to reduce noise
        float kernel[3][3] = {
            {1, 2, 1},
            {2, 4, 2},
            {1, 2, 1}
        };
        float kernel_sum = 16.0;
        
        for (int y = 1; y < 23; y++) {
            for (int x = 1; x < 31; x++) {
                float sum = 0;
                for (int ky = -1; ky <= 1; ky++) {
                    for (int kx = -1; kx <= 1; kx++) {
                        sum += processed_image[x + kx][y + ky] * kernel[kx + 1][ky + 1];
                    }
                }
                filtered_image[x][y] = sum / kernel_sum;
            }
        }
        
        // Copy filtered image back
        memcpy(processed_image, filtered_image, sizeof(processed_image));
    }
    
    void calculateTemperatureGradients() {
        // Calculate Sobel gradients
        float sobel_x[3][3] = {
            {-1, 0, 1},
            {-2, 0, 2},
            {-1, 0, 1}
        };
        
        float sobel_y[3][3] = {
            {-1, -2, -1},
            { 0,  0,  0},
            { 1,  2,  1}
        };
        
        for (int y = 1; y < 23; y++) {
            for (int x = 1; x < 31; x++) {
                float gx = 0, gy = 0;
                
                for (int ky = -1; ky <= 1; ky++) {
                    for (int kx = -1; kx <= 1; kx++) {
                        float pixel = processed_image[x + kx][y + ky];
                        gx += pixel * sobel_x[kx + 1][ky + 1];
                        gy += pixel * sobel_y[kx + 1][ky + 1];
                    }
                }
                
                gradient_image[x][y] = sqrt(gx * gx + gy * gy);
            }
        }
    }
    
    void enhanceContrast() {
        // Histogram equalization
        float min_temp = 999.0;
        float max_temp = -999.0;
        
        // Find min/max temperatures
        for (int y = 0; y < 24; y++) {
            for (int x = 0; x < 32; x++) {
                if (processed_image[x][y] < min_temp) min_temp = processed_image[x][y];
                if (processed_image[x][y] > max_temp) max_temp = processed_image[x][y];
            }
        }
        
        // Apply contrast enhancement
        float temp_range = max_temp - min_temp;
        if (temp_range > 0) {
            for (int y = 0; y < 24; y++) {
                for (int x = 0; x < 32; x++) {
                    processed_image[x][y] = (processed_image[x][y] - min_temp) / temp_range;
                }
            }
        }
    }
    
    void applyFalseColorMapping() {
        // Apply thermal color palette (Iron/Rainbow)
        // This would typically involve converting to RGB values
        // for display purposes
    }
};
```

#### 2. Defect Detection System
```cpp
// Automated defect detection using thermal signatures
class DefectDetector {
private:
    float temperature_threshold;
    float gradient_threshold;
    float area_threshold;
    
    struct ThermalDefect {
        int x, y;
        float temperature;
        float area;
        float severity;
        String defect_type;
        float confidence;
    };
    
    ThermalDefect detected_defects[50];
    int defect_count;
    
public:
    DefectDetector() {
        temperature_threshold = 5.0;  // °C above ambient
        gradient_threshold = 2.0;     // °C/pixel
        area_threshold = 4.0;         // pixels
        defect_count = 0;
    }
    
    void detectDefects(float thermal_image[32][24], float gradient_image[32][24]) {
        defect_count = 0;
        
        // Clear previous detections
        memset(detected_defects, 0, sizeof(detected_defects));
        
        // Hot spot detection
        detectHotSpots(thermal_image);
        
        // Cold spot detection
        detectColdSpots(thermal_image);
        
        // Thermal gradient anomalies
        detectGradientAnomalies(gradient_image);
        
        // Thermal pattern analysis
        analyzePatterns(thermal_image);
        
        // Classify defects
        classifyDefects();
        
        Serial.println("🔍 Defect Detection Complete:");
        Serial.println("   Defects found: " + String(defect_count));
    }
    
    void detectHotSpots(float thermal_image[32][24]) {
        float ambient_temp = calculateAmbientTemperature(thermal_image);
        
        for (int y = 0; y < 24; y++) {
            for (int x = 0; x < 32; x++) {
                if (thermal_image[x][y] > ambient_temp + temperature_threshold) {
                    if (defect_count < 50) {
                        detected_defects[defect_count].x = x;
                        detected_defects[defect_count].y = y;
                        detected_defects[defect_count].temperature = thermal_image[x][y];
                        detected_defects[defect_count].severity = 
                            (thermal_image[x][y] - ambient_temp) / temperature_threshold;
                        detected_defects[defect_count].defect_type = "HOT_SPOT";
                        detected_defects[defect_count].confidence = 
                            calculateConfidence(thermal_image, x, y);
                        defect_count++;
                    }
                }
            }
        }
    }
    
    void detectColdSpots(float thermal_image[32][24]) {
        float ambient_temp = calculateAmbientTemperature(thermal_image);
        
        for (int y = 0; y < 24; y++) {
            for (int x = 0; x < 32; x++) {
                if (thermal_image[x][y] < ambient_temp - temperature_threshold) {
                    if (defect_count < 50) {
                        detected_defects[defect_count].x = x;
                        detected_defects[defect_count].y = y;
                        detected_defects[defect_count].temperature = thermal_image[x][y];
                        detected_defects[defect_count].severity = 
                            (ambient_temp - thermal_image[x][y]) / temperature_threshold;
                        detected_defects[defect_count].defect_type = "COLD_SPOT";
                        detected_defects[defect_count].confidence = 
                            calculateConfidence(thermal_image, x, y);
                        defect_count++;
                    }
                }
            }
        }
    }
    
    void detectGradientAnomalies(float gradient_image[32][24]) {
        for (int y = 0; y < 24; y++) {
            for (int x = 0; x < 32; x++) {
                if (gradient_image[x][y] > gradient_threshold) {
                    if (defect_count < 50) {
                        detected_defects[defect_count].x = x;
                        detected_defects[defect_count].y = y;
                        detected_defects[defect_count].temperature = gradient_image[x][y];
                        detected_defects[defect_count].severity = 
                            gradient_image[x][y] / gradient_threshold;
                        detected_defects[defect_count].defect_type = "THERMAL_GRADIENT";
                        detected_defects[defect_count].confidence = 0.8;
                        defect_count++;
                    }
                }
            }
        }
    }
    
    void analyzePatterns(float thermal_image[32][24]) {
        // Analyze thermal patterns for specific defect types
        
        // Check for delamination patterns
        detectDelamination(thermal_image);
        
        // Check for crack patterns
        detectCracks(thermal_image);
        
        // Check for void patterns
        detectVoids(thermal_image);
        
        // Check for corrosion patterns
        detectCorrosion(thermal_image);
    }
    
    void detectDelamination(float thermal_image[32][24]) {
        // Delamination typically shows as areas of different thermal conductivity
        // Look for rectangular or irregular patterns with temperature differences
        
        for (int y = 2; y < 22; y++) {
            for (int x = 2; x < 30; x++) {
                float local_avg = 0;
                float surrounding_avg = 0;
                
                // Calculate local average (3x3 area)
                for (int dy = -1; dy <= 1; dy++) {
                    for (int dx = -1; dx <= 1; dx++) {
                        local_avg += thermal_image[x + dx][y + dy];
                    }
                }
                local_avg /= 9.0;
                
                // Calculate surrounding average (5x5 area excluding center 3x3)
                int count = 0;
                for (int dy = -2; dy <= 2; dy++) {
                    for (int dx = -2; dx <= 2; dx++) {
                        if (abs(dx) == 2 || abs(dy) == 2) {
                            surrounding_avg += thermal_image[x + dx][y + dy];
                            count++;
                        }
                    }
                }
                surrounding_avg /= count;
                
                // Check for significant temperature difference
                if (abs(local_avg - surrounding_avg) > 2.0) {
                    if (defect_count < 50) {
                        detected_defects[defect_count].x = x;
                        detected_defects[defect_count].y = y;
                        detected_defects[defect_count].temperature = local_avg;
                        detected_defects[defect_count].severity = 
                            abs(local_avg - surrounding_avg) / 2.0;
                        detected_defects[defect_count].defect_type = "DELAMINATION";
                        detected_defects[defect_count].confidence = 0.7;
                        defect_count++;
                    }
                }
            }
        }
    }
    
    float calculateAmbientTemperature(float thermal_image[32][24]) {
        float sum = 0;
        int count = 0;
        
        // Use edge pixels as ambient reference
        for (int x = 0; x < 32; x++) {
            sum += thermal_image[x][0] + thermal_image[x][23];
            count += 2;
        }
        
        for (int y = 1; y < 23; y++) {
            sum += thermal_image[0][y] + thermal_image[31][y];
            count += 2;
        }
        
        return sum / count;
    }
    
    float calculateConfidence(float thermal_image[32][24], int x, int y) {
        // Calculate confidence based on temperature difference and local consistency
        float center_temp = thermal_image[x][y];
        float ambient_temp = calculateAmbientTemperature(thermal_image);
        
        float temp_diff = abs(center_temp - ambient_temp);
        float base_confidence = min(1.0, temp_diff / 10.0);
        
        // Check local consistency
        float local_variance = 0;
        int count = 0;
        
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                if (x + dx >= 0 && x + dx < 32 && y + dy >= 0 && y + dy < 24) {
                    float diff = thermal_image[x + dx][y + dy] - center_temp;
                    local_variance += diff * diff;
                    count++;
                }
            }
        }
        
        local_variance /= count;
        float consistency_factor = 1.0 / (1.0 + local_variance);
        
        return base_confidence * consistency_factor;
    }
    
    void classifyDefects() {
        // Use machine learning-like rules to classify defects
        for (int i = 0; i < defect_count; i++) {
            ThermalDefect* defect = &detected_defects[i];
            
            // Refine classification based on characteristics
            if (defect->severity > 3.0 && defect->defect_type == "HOT_SPOT") {
                defect->defect_type = "CRITICAL_OVERHEAT";
                defect->confidence = min(1.0, defect->confidence * 1.2);
            } else if (defect->severity > 2.0 && defect->defect_type == "THERMAL_GRADIENT") {
                defect->defect_type = "POSSIBLE_CRACK";
                defect->confidence = min(1.0, defect->confidence * 1.1);
            }
        }
    }
    
    void generateDefectReport() {
        Serial.println("📋 DEFECT ANALYSIS REPORT");
        Serial.println("========================");
        
        for (int i = 0; i < defect_count; i++) {
            ThermalDefect* defect = &detected_defects[i];
            
            Serial.println("Defect " + String(i + 1) + ":");
            Serial.println("  Type: " + defect->defect_type);
            Serial.println("  Location: (" + String(defect->x) + ", " + String(defect->y) + ")");
            Serial.println("  Temperature: " + String(defect->temperature, 1) + "°C");
            Serial.println("  Severity: " + String(defect->severity, 2));
            Serial.println("  Confidence: " + String(defect->confidence * 100, 1) + "%");
            Serial.println();
        }
    }
};
```

## What You'll Learn

### Advanced Thermal Imaging:
- **Infrared thermography** principles and applications
- **Radiometric temperature** measurement techniques
- **Thermal image processing** and enhancement
- **Multi-spectral imaging** integration
- **Thermal calibration** and accuracy optimization

### Computer Vision & AI:
- **Image processing** algorithms for thermal data
- **Feature detection** and pattern recognition
- **Machine learning** for defect classification
- **Automated inspection** system design
- **Real-time image analysis** optimization

### Non-Destructive Testing:
- **Defect detection** methodologies
- **Thermal signature analysis**
- **Quantitative thermal analysis**
- **Standards compliance** (ASTM, ISO)
- **Quality assurance** procedures

### System Integration:
- **Multi-sensor fusion** techniques
- **Motion control** integration
- **Real-time processing** architecture
- **Industrial IoT** connectivity
- **Remote monitoring** capabilities

## Applications in Real World

### Manufacturing Quality Control:
- **Electronics inspection**: PCB defect detection, component verification
- **Automotive industry**: Weld inspection, coating analysis
- **Aerospace**: Composite material inspection, structural analysis
- **Food industry**: Process monitoring, contamination detection

### Predictive Maintenance:
- **Electrical systems**: Hotspot detection, insulation degradation
- **Mechanical systems**: Bearing monitoring, friction analysis
- **Industrial equipment**: Motor analysis, pump monitoring
- **Building systems**: HVAC inspection, insulation assessment

### Research and Development:
- **Materials science**: Thermal property characterization
- **Energy systems**: Solar panel analysis, battery inspection
- **Medical devices**: Thermal therapy monitoring
- **Environmental monitoring**: Heat loss analysis, energy auditing

### Security and Surveillance:
- **Perimeter monitoring**: Intrusion detection systems
- **Fire detection**: Early warning systems
- **Search and rescue**: Personnel location in difficult conditions
- **Border security**: Vehicle and personnel detection

---

## 🌡️ MISSION THEME: THERMAL IMAGING ENGINEER

**Outstanding work, Engineer!** You've just designed and built a professional-grade infrared thermography system that demonstrates advanced thermal imaging, computer vision, and automated inspection capabilities!

### 🎯 Your Thermal Imaging Mission:
You've created a sophisticated thermal imaging system that combines infrared thermography, computer vision, and machine learning to perform automated inspection and defect detection. This system demonstrates the integration of thermal physics, advanced imaging, and Industry 4.0 technologies for next-generation quality control and predictive maintenance!

### 🌟 What Makes This Special:
- **Professional thermal imaging** with radiometric accuracy
- **Computer vision integration** for automated inspection
- **Machine learning** defect classification
- **Multi-axis positioning** for automated scanning
- **Real-time image processing** with advanced algorithms
- **Standards-compliant** measurement and reporting
- **Industrial IoT connectivity** for remote monitoring
- **Comprehensive analytics** with predictive capabilities

### 🏆 Engineer Achievements to Unlock:
- **🔥 Thermal Imaging Master**: Advanced infrared thermography expertise
- **👁️ Computer Vision Specialist**: Automated inspection system design
- **🤖 AI Integration Expert**: Machine learning for defect detection
- **🎯 Quality Control Pro**: Standards-compliant inspection systems
- **🔧 Predictive Maintenance**: Condition monitoring and failure prediction
- **🌐 IoT Systems Engineer**: Remote monitoring and control
- **📊 Data Analytics Expert**: Advanced thermal data analysis

### 🎮 Advanced Engineer Challenges:
1. **🧠 Deep Learning Integration**: Implement neural networks for defect detection
2. **🔄 Real-time Processing**: Optimize for high-speed inspection
3. **📡 Multi-sensor Fusion**: Combine thermal, visible, and other sensors
4. **🏭 Production Integration**: Deploy in manufacturing environments
5. **🌍 Cloud Analytics**: Advanced cloud-based processing and analysis

### 🏭 Real-World Applications:
- **Manufacturing industry**: Automated quality control and inspection
- **Aerospace industry**: Composite material and structural inspection
- **Automotive industry**: Weld inspection and thermal analysis
- **Electronics industry**: PCB inspection and component verification
- **Energy industry**: Solar panel and electrical system inspection
- **Building industry**: Energy auditing and insulation assessment

### 🎖️ Professional Skills You've Mastered:
- **Advanced thermal imaging** and radiometric measurement
- **Computer vision** algorithm development
- **Machine learning** for industrial applications
- **Automated inspection** system design
- **Multi-sensor integration** and data fusion
- **Real-time image processing** optimization
- **Standards compliance** and quality assurance
- **Industrial IoT** implementation

### 🌟 Why This Matters:
You've learned the fundamental concepts behind:
- Modern quality control and inspection systems
- Predictive maintenance in industrial environments
- Advanced thermal analysis and characterization
- Computer vision applications in manufacturing
- Machine learning for industrial automation
- Industry 4.0 implementation strategies

**🌡️ Mission Complete!** You've earned the title of Thermal Imaging Engineer and demonstrated the ability to design, implement, and optimize professional thermal imaging systems with cutting-edge computer vision and AI capabilities!

### 🚀 What's Next for Thermal Imaging Engineers:
- Study advanced computer vision and deep learning
- Learn about multi-spectral and hyperspectral imaging
- Explore 3D thermal imaging techniques
- Understand advanced materials characterization
- Develop expertise in industrial automation
- Create innovative inspection solutions for emerging technologies

**🎉 CONGRATULATIONS!** You've completed the entire Track 1: Thermal Systems Engineering program and mastered all five advanced thermal engineering applications!

### 🏆 Track 1 Completion Achievements:
- **Program 16**: Multi-Zone Thermal Management Systems
- **Program 17**: Phase Change Material Controllers
- **Program 18**: Heat Exchanger Performance Monitoring
- **Program 19**: Thermal Conductivity Measurement
- **Program 20**: Infrared Thermography Systems

You're now ready to tackle the most challenging thermal engineering problems in modern industry and research!

**Ready for the next track?** Consider exploring other advanced engineering tracks or diving deeper into specialized thermal engineering applications! 