# Program 21: Fatigue Testing Machine - Testing Guide

## Overview
This guide provides comprehensive testing procedures for validating the fatigue testing machine including load control, displacement measurement, acoustic emission monitoring, and statistical analysis systems.

## Safety Precautions

### Pre-Testing Safety Checks
- [ ] Verify all electrical connections per circuit diagram
- [ ] Check emergency stop functionality
- [ ] Confirm proper grounding of all equipment
- [ ] Validate safety interlocks operation
- [ ] Inspect for proper PPE (safety glasses, gloves, lab coat)
- [ ] Verify mechanical system integrity
- [ ] Check specimen grips and alignment
- [ ] Ensure safety enclosure is properly installed

### Operating Safety Limits
- **Maximum Load**: 2000N (200kg)
- **Maximum Displacement**: ±25mm
- **Maximum Frequency**: 50Hz
- **Maximum Test Duration**: Continuous operation
- **Emergency Response**: <1 second for all safety systems

## Pre-Test Setup

### Hardware Verification
```
Hardware Checklist:
├── Arduino Mega 2560 mounted and powered
├── ESP32 DevKit analytics gateway connected
├── NEMA 23 stepper motor with TB6600 driver
├── 200kg S-type load cell calibrated
├── HX711 load cell amplifier configured
├── LVDT ±25mm with AD698 conditioner
├── 2x Acoustic emission sensors mounted
├── ADS1256 24-bit ADC for AE signals
├── 7" TFT display with touch interface
├── SD card module with 32GB card
├── Emergency stop button and safety relay
├── Door interlock switches operational
├── Linear guide rails and lead screw assembly
├── Specimen grips (wedge or pin type)
└── Safety enclosure with interlocks
```

### Software Configuration
```cpp
// Test Configuration Constants
#define MAX_LOAD 2000.0              // Maximum load in N
#define MAX_DISPLACEMENT 25.0        // Maximum displacement in mm
#define MIN_FREQUENCY 0.1            // Minimum frequency in Hz
#define MAX_FREQUENCY 50.0           // Maximum frequency in Hz
#define LOAD_CELL_SENSITIVITY 2.0    // mV/V
#define LVDT_SENSITIVITY 100.0       // mV/mm
#define AE_THRESHOLD 2.5             // AE threshold in V
#define MICROSTEPS 16                // Stepper microstepping
#define LEAD_SCREW_PITCH 5.0         // Lead screw pitch in mm
```

## Load Cell Calibration

### Calibration Procedure
```
Load Cell Calibration Steps:
1. Ensure system is at zero load
2. Tare the load cell (zero adjustment)
3. Apply known weights in increments:
   - 0kg (zero check)
   - 50kg (25% of capacity)
   - 100kg (50% of capacity)
   - 150kg (75% of capacity)
   - 200kg (100% of capacity)
4. Record readings and calculate calibration factor
5. Apply calibration factor to software
6. Verify accuracy with independent standards
7. Document calibration certificate
```

**Expected Results:**
- Accuracy: ±0.1% of full scale
- Linearity: ±0.03% of full scale
- Hysteresis: ±0.02% of full scale
- Temperature coefficient: ±0.001%/°C
- Overload capacity: 150% of rated capacity

### Load Cell Validation Test
```cpp
// Test Load Cell Accuracy
bool testLoadCellAccuracy() {
    float test_loads[] = {0, 500, 1000, 1500, 2000}; // N
    float tolerance = 2.0; // ±2N tolerance
    
    bool accuracy_ok = true;
    
    for (int i = 0; i < 5; i++) {
        // Apply test load (manually or with calibration weights)
        Serial.print("Apply load: ");
        Serial.print(test_loads[i]);
        Serial.println(" N");
        
        delay(5000); // Wait for operator to apply load
        
        // Read load cell
        float measured_load = readLoadCell();
        float error = abs(measured_load - test_loads[i]);
        
        Serial.print("Measured: ");
        Serial.print(measured_load);
        Serial.print(" N, Error: ");
        Serial.print(error);
        Serial.println(" N");
        
        if (error > tolerance) {
            accuracy_ok = false;
            Serial.println("FAIL: Load cell accuracy");
            break;
        }
    }
    
    return accuracy_ok;
}
```

## LVDT Displacement Calibration

### LVDT Calibration Procedure
```
LVDT Calibration Steps:
1. Set LVDT core to center position
2. Zero the AD698 output with trim pot
3. Move core to known positions:
   - -25mm (full negative)
   - -12.5mm (half negative)
   - 0mm (center)
   - +12.5mm (half positive)
   - +25mm (full positive)
4. Record voltages and calculate sensitivity
5. Verify linearity across full range
6. Check for null position stability
7. Document calibration coefficients
```

**Expected Results:**
- Linearity: ±0.25% of full scale
- Sensitivity: 100 ± 2 mV/mm
- Null voltage: 2.5 ± 0.1V at center
- Resolution: 0.001mm
- Temperature coefficient: ±0.01%/°C

### LVDT Validation Test
```cpp
// Test LVDT Accuracy
bool testLVDTAccuracy() {
    float test_positions[] = {-25, -12.5, 0, 12.5, 25}; // mm
    float tolerance = 0.05; // ±0.05mm tolerance
    
    bool accuracy_ok = true;
    
    for (int i = 0; i < 5; i++) {
        // Move to test position
        moveToPosition(test_positions[i]);
        
        // Wait for settling
        delay(2000);
        
        // Read LVDT
        float measured_position = readLVDT();
        float error = abs(measured_position - test_positions[i]);
        
        Serial.print("Target: ");
        Serial.print(test_positions[i]);
        Serial.print(" mm, Measured: ");
        Serial.print(measured_position);
        Serial.print(" mm, Error: ");
        Serial.print(error);
        Serial.println(" mm");
        
        if (error > tolerance) {
            accuracy_ok = false;
            Serial.println("FAIL: LVDT accuracy");
            break;
        }
    }
    
    return accuracy_ok;
}
```

## Motion Control System Testing

### Stepper Motor Calibration
```
Stepper Motor Calibration:
1. Home the system to a known position
2. Move a known distance (e.g., 10mm)
3. Measure actual movement with external gauge
4. Calculate steps per mm
5. Verify repeatability over multiple moves
6. Test acceleration and deceleration profiles
7. Check for lost steps at maximum speed
8. Validate microstepping operation
```

**Expected Results:**
- Position accuracy: ±0.01mm
- Repeatability: ±0.005mm
- Maximum speed: 10mm/s
- Acceleration: 50mm/s²
- No lost steps at rated speed
- Microstepping: 16 steps/full step

### Motion Control Test
```cpp
// Test Motion Control Accuracy
bool testMotionControlAccuracy() {
    float test_moves[] = {1.0, 5.0, 10.0, 20.0}; // mm
    float tolerance = 0.02; // ±0.02mm tolerance
    
    bool accuracy_ok = true;
    
    // Return to home position
    moveToPosition(0);
    delay(2000);
    
    for (int i = 0; i < 4; i++) {
        // Move to test position
        moveToPosition(test_moves[i]);
        
        // Wait for movement completion
        while (stepper.distanceToGo() != 0) {
            stepper.run();
        }
        
        delay(1000); // Settling time
        
        // Read actual position
        float actual_position = readLVDT();
        float error = abs(actual_position - test_moves[i]);
        
        Serial.print("Target: ");
        Serial.print(test_moves[i]);
        Serial.print(" mm, Actual: ");
        Serial.print(actual_position);
        Serial.print(" mm, Error: ");
        Serial.print(error);
        Serial.println(" mm");
        
        if (error > tolerance) {
            accuracy_ok = false;
            Serial.println("FAIL: Motion control accuracy");
            break;
        }
    }
    
    return accuracy_ok;
}
```

## Acoustic Emission System Testing

### AE Sensor Calibration
```
AE Sensor Calibration:
1. Apply coupling agent to specimen surface
2. Mount sensors with specified pressure
3. Perform pencil lead break test (PLB)
4. Record AE signals from each sensor
5. Verify sensitivity and frequency response
6. Check for electrical noise and interference
7. Validate hit detection threshold
8. Test source localization accuracy
```

**Expected Results:**
- Sensitivity: 75 ± 5 dB ref 1V/μbar
- Frequency response: 150-400 kHz
- Signal-to-noise ratio: >40 dB
- Hit detection threshold: 2.5V
- Source location accuracy: ±5mm

### AE System Validation
```cpp
// Test Acoustic Emission System
bool testAcousticEmissionSystem() {
    Serial.println("Perform pencil lead break test...");
    
    // Reset AE counters
    ae_hit_count = 0;
    uint32_t test_start_time = millis();
    
    // Wait for PLB events (operator performs)
    delay(10000);
    
    // Check if hits were detected
    if (ae_hit_count > 0) {
        Serial.print("AE hits detected: ");
        Serial.println(ae_hit_count);
        return true;
    } else {
        Serial.println("FAIL: No AE hits detected");
        return false;
    }
}
```

## Force Control System Testing

### PID Controller Tuning
```
PID Tuning Procedure:
1. Set initial gains (Kp=0.5, Ki=0.1, Kd=0.05)
2. Apply step input and observe response
3. Adjust proportional gain for stability
4. Add integral action to eliminate steady-state error
5. Add derivative action to reduce overshoot
6. Test with different load levels
7. Verify stability margins
8. Document final gains
```

**Expected Results:**
- Settling time: <2 seconds
- Overshoot: <5%
- Steady-state error: <1%
- Stability margin: >6 dB
- Load disturbance rejection: >90%

### Force Control Test
```cpp
// Test Force Control System
bool testForceControlSystem() {
    float test_forces[] = {100, 500, 1000, 1500}; // N
    float tolerance = 10.0; // ±10N tolerance
    
    bool control_ok = true;
    
    for (int i = 0; i < 4; i++) {
        // Set target force
        setpoint_force = test_forces[i];
        
        // Enable PID controller
        force_pid.SetMode(AUTOMATIC);
        
        // Wait for settling
        uint32_t start_time = millis();
        while (millis() - start_time < 5000) {
            input_force = readLoadCell();
            force_pid.Compute();
            moveToPosition(output_position);
            stepper.run();
            delay(1);
        }
        
        // Check final error
        float final_error = abs(input_force - setpoint_force);
        
        Serial.print("Target: ");
        Serial.print(test_forces[i]);
        Serial.print(" N, Actual: ");
        Serial.print(input_force);
        Serial.print(" N, Error: ");
        Serial.print(final_error);
        Serial.println(" N");
        
        if (final_error > tolerance) {
            control_ok = false;
            Serial.println("FAIL: Force control accuracy");
            break;
        }
    }
    
    return control_ok;
}
```

## Fatigue Testing Validation

### Short-Term Fatigue Test
```
Short-Term Test Procedure:
1. Install test specimen in grips
2. Set test parameters:
   - Mean load: 1000N
   - Amplitude: 500N
   - Frequency: 10Hz
   - R-ratio: 0.1
3. Start test and monitor for 1000 cycles
4. Check load control stability
5. Monitor AE activity
6. Verify data logging
7. Analyze cycle counting
```

**Expected Results:**
- Load control stability: ±2%
- Frequency stability: ±0.1 Hz
- Data logging rate: 100% success
- Cycle counting accuracy: ±1 cycle
- AE hit detection: Functional

### Fatigue Test Validation
```cpp
// Perform Short Fatigue Test
bool performShortFatigueTest() {
    // Set test parameters
    test_params.mean_load = 1000.0;
    test_params.amplitude_load = 500.0;
    test_params.frequency = 10.0;
    test_params.R_ratio = 0.1;
    test_params.max_cycles = 1000;
    test_params.waveform = 0; // Sine wave
    
    // Start test
    startTest();
    
    // Monitor test progress
    uint32_t start_time = millis();
    uint32_t expected_duration = 1000000 / test_params.frequency; // microseconds
    
    while (test_running && current_data.cycle_count < test_params.max_cycles) {
        executeTestCycle();
        
        // Check for reasonable test duration
        if (millis() - start_time > expected_duration * 1.2) {
            Serial.println("FAIL: Test running too slow");
            endTest();
            return false;
        }
    }
    
    // Verify test completion
    if (current_data.cycle_count >= test_params.max_cycles) {
        Serial.println("PASS: Short fatigue test completed");
        endTest();
        return true;
    } else {
        Serial.println("FAIL: Test terminated early");
        endTest();
        return false;
    }
}
```

## Statistical Analysis Testing

### S-N Curve Generation Test
```
S-N Curve Test:
1. Run multiple specimens at different stress levels
2. Record cycles to failure for each specimen
3. Plot stress amplitude vs cycles to failure
4. Fit power law curve (S = A * N^-b)
5. Calculate correlation coefficient
6. Validate fatigue limit
7. Generate confidence intervals
```

**Expected Results:**
- Minimum 5 data points
- Correlation coefficient: >0.95
- Fatigue limit: Material dependent
- Confidence intervals: 95%

### Weibull Analysis Test
```cpp
// Test Weibull Analysis
bool testWeibullAnalysis() {
    // Generate test data (simulated failures)
    float failure_data[] = {1000, 1500, 2000, 2500, 3000, 3500, 4000};
    sn_data_count = 7;
    
    for (int i = 0; i < sn_data_count; i++) {
        sn_data[i].cycles_to_failure = failure_data[i];
        sn_data[i].stress_amplitude = 300.0; // MPa
        sn_data[i].failure_mode = "Fracture";
    }
    
    // Perform Weibull analysis
    performWeibullAnalysis();
    
    // Check if parameters are reasonable
    float beta = preferences.getFloat("weibull_beta", 0);
    float eta = preferences.getFloat("weibull_eta", 0);
    
    if (beta > 0.5 && beta < 5.0 && eta > 1000) {
        Serial.println("PASS: Weibull analysis");
        return true;
    } else {
        Serial.println("FAIL: Weibull analysis");
        return false;
    }
}
```

## Data Logging and Communication Testing

### Data Logging Test
```
Data Logging Test:
1. Create test data file on SD card
2. Log data at 10Hz rate for 10 minutes
3. Verify file integrity and completeness
4. Check timestamp accuracy
5. Validate data format and structure
6. Test file rotation and backup
7. Verify data recovery procedures
```

**Expected Results:**
- Data logging rate: 100% success
- File integrity: No corruption
- Timestamp accuracy: ±1 second
- Data completeness: >99.9%
- File format: CSV with headers

### Communication Test
```cpp
// Test Communication Systems
bool testCommunicationSystems() {
    bool comm_ok = true;
    
    // Test Serial communication
    ArduinoSerial.println("TEST_COMM");
    delay(100);
    if (ArduinoSerial.available()) {
        String response = ArduinoSerial.readString();
        if (response.indexOf("ACK") >= 0) {
            Serial.println("PASS: Serial communication");
        } else {
            Serial.println("FAIL: Serial communication");
            comm_ok = false;
        }
    }
    
    // Test WiFi connectivity
    if (WiFi.isConnected()) {
        Serial.println("PASS: WiFi connection");
    } else {
        Serial.println("FAIL: WiFi connection");
        comm_ok = false;
    }
    
    // Test MQTT connectivity
    if (mqtt_client.connected()) {
        Serial.println("PASS: MQTT connection");
    } else {
        Serial.println("FAIL: MQTT connection");
        comm_ok = false;
    }
    
    // Test SD card access
    if (SD.exists("/test.txt")) {
        Serial.println("PASS: SD card access");
    } else {
        Serial.println("FAIL: SD card access");
        comm_ok = false;
    }
    
    return comm_ok;
}
```

## Safety System Testing

### Emergency Stop Test
```
Emergency Stop Test:
1. Start fatigue test at low load
2. Activate emergency stop button
3. Verify immediate motor stop
4. Check system shutdown sequence
5. Test reset and restart procedure
6. Verify data preservation
7. Check alarm activation
```

**Expected Results:**
- Response time: <1 second
- Motor stop: Immediate
- Data preservation: 100%
- Alarm activation: Audible and visual
- Reset procedure: Manual reset required

### Safety Interlock Test
```cpp
// Test Safety Interlocks
bool testSafetyInterlocks() {
    bool safety_ok = true;
    
    // Test emergency stop
    Serial.println("Testing emergency stop...");
    digitalWrite(EMERGENCY_STOP_PIN, LOW);
    delay(100);
    
    if (emergency_stop_active) {
        Serial.println("PASS: Emergency stop");
    } else {
        Serial.println("FAIL: Emergency stop");
        safety_ok = false;
    }
    
    // Reset emergency stop
    digitalWrite(EMERGENCY_STOP_PIN, HIGH);
    emergency_stop_active = false;
    
    // Test door interlock
    Serial.println("Testing door interlock...");
    digitalWrite(DOOR_INTERLOCK_PIN, HIGH);
    delay(100);
    
    if (!test_running) {
        Serial.println("PASS: Door interlock");
    } else {
        Serial.println("FAIL: Door interlock");
        safety_ok = false;
    }
    
    // Reset door interlock
    digitalWrite(DOOR_INTERLOCK_PIN, LOW);
    
    return safety_ok;
}
```

## System Integration Testing

### Complete System Test
```
Integration Test Procedure:
1. Power on system and perform initialization
2. Load test specimen
3. Configure test parameters
4. Start fatigue test
5. Monitor all subsystems during test
6. Verify data collection and analysis
7. Complete test and generate report
8. Validate all safety systems
```

**Expected Results:**
- System initialization: <30 seconds
- Test setup: <5 minutes
- Data collection: 100% success
- Analysis: Real-time updates
- Report generation: Automatic
- Safety systems: 100% functional

### System Integration Test
```cpp
// Complete System Integration Test
bool performSystemIntegrationTest() {
    Serial.println("Starting system integration test...");
    
    // Initialize all subsystems
    bool init_ok = true;
    init_ok &= testLoadCellAccuracy();
    init_ok &= testLVDTAccuracy();
    init_ok &= testMotionControlAccuracy();
    init_ok &= testForceControlSystem();
    init_ok &= testAcousticEmissionSystem();
    init_ok &= testCommunicationSystems();
    init_ok &= testSafetyInterlocks();
    
    if (!init_ok) {
        Serial.println("FAIL: Subsystem initialization");
        return false;
    }
    
    // Run short fatigue test
    bool fatigue_ok = performShortFatigueTest();
    
    if (!fatigue_ok) {
        Serial.println("FAIL: Fatigue test");
        return false;
    }
    
    // Test data analysis
    bool analysis_ok = testWeibullAnalysis();
    
    if (!analysis_ok) {
        Serial.println("FAIL: Statistical analysis");
        return false;
    }
    
    Serial.println("PASS: System integration test");
    return true;
}
```

## Performance Validation

### Accuracy Requirements
- [ ] Load measurement: ±0.1% of full scale
- [ ] Displacement measurement: ±0.01mm
- [ ] Frequency control: ±0.1 Hz
- [ ] Cycle counting: ±1 cycle
- [ ] AE detection: 100% of PLB events
- [ ] Data logging: >99.9% success rate

### Repeatability Requirements
- [ ] Load control: ±2% variation
- [ ] Position control: ±0.005mm
- [ ] Frequency stability: ±0.1%
- [ ] Test duration: ±1% of calculated time
- [ ] Statistical analysis: Consistent results

### Performance Metrics
- [ ] System startup time: <30 seconds
- [ ] Test setup time: <5 minutes
- [ ] Data acquisition rate: 100 Hz
- [ ] Analysis update rate: 1 Hz
- [ ] Report generation time: <1 minute
- [ ] Safety response time: <1 second

## Compliance Verification

### ASTM E466 Compliance
- [ ] Load control: ±2% of mean load
- [ ] Frequency control: ±1% of set frequency
- [ ] Waveform quality: <5% harmonic distortion
- [ ] Cycle counting: Rainflow or equivalent
- [ ] Data recording: All required parameters
- [ ] Calibration: Traceable standards

### ISO 12106 Compliance
- [ ] Test piece preparation: Per standard
- [ ] Test conditions: Controlled environment
- [ ] Loading procedure: Gradual application
- [ ] Data analysis: Statistical methods
- [ ] Reporting: Complete documentation

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: Load cell readings unstable
**Solution**: Check electrical connections, verify grounding, calibrate with known weights

**Issue**: LVDT output nonlinear
**Solution**: Check core alignment, verify excitation voltage, adjust null position

**Issue**: Stepper motor losing steps
**Solution**: Reduce acceleration, check motor current, verify mechanical binding

**Issue**: PID controller oscillating
**Solution**: Reduce gains, check for mechanical play, verify sensor response

**Issue**: AE sensors not detecting
**Solution**: Check coupling, verify sensor connection, adjust threshold

**Issue**: Data logging failures
**Solution**: Check SD card, verify file system, test write permissions

**Issue**: Communication errors
**Solution**: Check cable connections, verify baud rates, test signal integrity

**Issue**: Safety systems not responding
**Solution**: Check emergency stop wiring, verify interlock switches, test relay operation

## Maintenance Schedule

### Daily Maintenance
- [ ] Check system status indicators
- [ ] Verify emergency stop operation
- [ ] Check specimen grip alignment
- [ ] Monitor data logging status

### Weekly Maintenance
- [ ] Calibrate load cell zero
- [ ] Check LVDT center position
- [ ] Verify motion control accuracy
- [ ] Test communication systems

### Monthly Maintenance
- [ ] Full system calibration
- [ ] Mechanical inspection
- [ ] Software backup
- [ ] Safety system test

### Annual Maintenance
- [ ] Complete recalibration
- [ ] Mechanical component replacement
- [ ] Software updates
- [ ] Compliance verification

This comprehensive testing guide ensures proper validation of all fatigue testing machine systems, providing confidence in test results and compliance with industry standards.