# Program 24: Nano-Indentation Controller - Testing Guide

## Overview
This comprehensive testing guide provides detailed procedures for validating the nano-indentation system including force and displacement calibration, control system verification, material property accuracy, and environmental stability testing.

## Safety Precautions

### Pre-Testing Safety Checks
- [ ] Verify all electrical connections per circuit diagram
- [ ] Check emergency stop functionality
- [ ] Confirm proper grounding of all equipment
- [ ] Validate safety interlocks operation
- [ ] Inspect for proper PPE (safety glasses, anti-static protection)
- [ ] Verify high-voltage safety measures (150V piezo supply)
- [ ] Check mechanical safety limits and collision detection
- [ ] Ensure proper vibration isolation platform operation

### Operating Safety Limits
- **Maximum Load**: 500 mN (emergency stop at 550 mN)
- **Maximum Displacement**: 100 μm (hard stop at 110 μm)
- **Maximum Voltage**: 150V (piezo driver protection)
- **Maximum Temperature**: 80°C (system shutdown at 85°C)
- **Emergency Response**: <1 second for all safety systems

## Pre-Test Setup

### Hardware Verification
```
Hardware Checklist:
├── Arduino Due (84 MHz) mounted and powered
├── ESP32 IoT gateway connected and functional
├── Piezoelectric actuator system operational
├── Capacitive displacement sensor calibrated
├── High-resolution load cell verified
├── Precision stepper motors aligned
├── Environmental control chamber stable
├── Optical microscope system focused
├── Vibration isolation platform active
├── Emergency stop and safety interlocks
├── Power supply system (24V, ±15V, 150V) verified
└── Data acquisition and storage systems ready
```

### Software Configuration
```cpp
// Test Configuration Constants
#define FORCE_RESOLUTION 0.1          // μN
#define DISPLACEMENT_RESOLUTION 0.1   // nm
#define MAX_LOAD_TEST 500000          // μN (500 mN)
#define MAX_DISPLACEMENT_TEST 100000  // nm (100 μm)
#define TEMPERATURE_STABILITY 0.1     // °C
#define VIBRATION_LIMIT 1.0           // μm displacement
#define SAMPLING_RATE 1000            // Hz
#define CONTROL_BANDWIDTH 100         // Hz
#define POSITIONING_ACCURACY 0.5      // μm
```

## Force Measurement System Testing

### Load Cell Calibration and Verification
```
Load Cell Calibration Procedure:
1. Use certified calibration weights:
   - 0.1 mN, 0.5 mN, 1 mN, 5 mN, 10 mN, 50 mN, 100 mN, 500 mN
2. Apply weights in ascending and descending order
3. Record load cell readings at each calibration point
4. Calculate linearity, hysteresis, and repeatability
5. Verify temperature coefficient over operating range
6. Check for creep and drift over 1-hour period
7. Document calibration coefficients and uncertainty
```

**Expected Results:**
- Linearity: ±0.1% of full scale
- Hysteresis: ±0.05% of full scale
- Repeatability: ±0.02% of full scale (1σ)
- Temperature coefficient: <0.01%/°C
- Creep: <0.01% over 1 hour
- Drift: <0.005% over 8 hours

### Force Control System Test
```cpp
// Test Force Control System
bool testForceControl() {
    float test_loads[] = {1.0, 10.0, 50.0, 100.0, 500.0, 1000.0}; // μN
    float tolerance = 0.5; // μN
    
    bool control_ok = true;
    
    Serial.println("Testing force control system...");
    
    for (int i = 0; i < 6; i++) {
        // Set target force
        target_load = test_loads[i];
        
        // Enable force control
        force_control_enabled = true;
        
        // Wait for settling
        uint32_t start_time = millis();
        bool settled = false;
        
        while (millis() - start_time < 30000) { // 30 seconds timeout
            updateForceControl();
            
            // Check if force is within tolerance
            if (abs(current_load - target_load) < tolerance) {
                if (!settled) {
                    settled = true;
                    Serial.print("Force settled at: ");
                    Serial.print(current_load);
                    Serial.println(" μN");
                }
            } else {
                settled = false;
            }
            
            // Consider stable if settled for 5 seconds
            if (settled && (millis() - start_time > 5000)) {
                break;
            }
            
            delay(10);
        }
        
        // Verify final force
        float final_error = abs(current_load - target_load);
        
        Serial.print("Target: ");
        Serial.print(test_loads[i]);
        Serial.print(" μN, Actual: ");
        Serial.print(current_load);
        Serial.print(" μN, Error: ");
        Serial.print(final_error);
        Serial.println(" μN");
        
        if (final_error > tolerance) {
            control_ok = false;
            Serial.println("FAIL: Force control accuracy");
            break;
        }
        
        // Test step response
        float step_response_time = measureStepResponse(test_loads[i]);
        Serial.print("Step response time: ");
        Serial.print(step_response_time);
        Serial.println(" ms");
        
        if (step_response_time > 1000) { // 1 second max
            control_ok = false;
            Serial.println("FAIL: Force control response time");
        }
    }
    
    force_control_enabled = false;
    return control_ok;
}
```

## Displacement Measurement System Testing

### Displacement Sensor Calibration
```
Displacement Sensor Calibration Procedure:
1. Use laser interferometer reference system:
   - Wavelength: 633 nm (HeNe laser)
   - Resolution: 0.01 nm
   - Accuracy: ±0.1 nm
2. Mount displacement sensor and reference in parallel
3. Apply known displacements: 0, 100, 500, 1000, 5000, 10000 nm
4. Record sensor readings and reference values
5. Calculate calibration factor and linearity
6. Verify temperature coefficient
7. Check for noise and drift
```

**Expected Results:**
- Calibration factor: Within ±0.1% of nominal
- Linearity: ±0.01% of full scale
- Resolution: 0.1 nm RMS
- Temperature coefficient: <10 ppm/°C
- Noise: <0.05 nm RMS
- Drift: <0.1 nm over 8 hours

### Displacement Control Test
```cpp
// Test Displacement Control System
bool testDisplacementControl() {
    float test_displacements[] = {10.0, 50.0, 100.0, 500.0, 1000.0, 5000.0}; // nm
    float tolerance = 0.5; // nm
    
    bool control_ok = true;
    
    Serial.println("Testing displacement control system...");
    
    for (int i = 0; i < 6; i++) {
        // Set target displacement
        target_displacement = test_displacements[i];
        
        // Enable displacement control
        displacement_control_enabled = true;
        
        // Wait for settling
        uint32_t start_time = millis();
        bool settled = false;
        
        while (millis() - start_time < 30000) { // 30 seconds timeout
            updateDisplacementControl();
            
            // Check if displacement is within tolerance
            if (abs(current_displacement - target_displacement) < tolerance) {
                if (!settled) {
                    settled = true;
                    Serial.print("Displacement settled at: ");
                    Serial.print(current_displacement);
                    Serial.println(" nm");
                }
            } else {
                settled = false;
            }
            
            // Consider stable if settled for 2 seconds
            if (settled && (millis() - start_time > 2000)) {
                break;
            }
            
            delay(10);
        }
        
        // Verify final displacement
        float final_error = abs(current_displacement - target_displacement);
        
        Serial.print("Target: ");
        Serial.print(test_displacements[i]);
        Serial.print(" nm, Actual: ");
        Serial.print(current_displacement);
        Serial.print(" nm, Error: ");
        Serial.print(final_error);
        Serial.println(" nm");
        
        if (final_error > tolerance) {
            control_ok = false;
            Serial.println("FAIL: Displacement control accuracy");
            break;
        }
    }
    
    displacement_control_enabled = false;
    return control_ok;
}
```

## Piezoelectric Actuator Testing

### Piezo System Calibration
```
Piezo Actuator Test Procedure:
1. Test voltage-displacement relationship:
   - Apply voltages: 0V, 30V, 60V, 90V, 120V, 150V
   - Measure displacement with calibrated sensor
   - Calculate sensitivity (nm/V)
2. Test hysteresis characteristics:
   - Apply full voltage cycle (0-150V-0V)
   - Measure hysteresis loop
   - Calculate hysteresis percentage
3. Test frequency response:
   - Apply sine wave at various frequencies
   - Measure amplitude and phase response
   - Determine bandwidth and resonance
4. Test linearity and repeatability:
   - Multiple voltage cycles
   - Statistical analysis of repeatability
```

**Expected Results:**
- Sensitivity: 100 ± 5 nm/V
- Hysteresis: <10% of full scale
- Linearity: ±0.5% of full scale
- Repeatability: ±0.1% of full scale
- Bandwidth: >1 kHz (-3dB)
- Resonance frequency: >20 kHz

### Piezo Control System Test
```cpp
// Test Piezo Control System
bool testPiezoControl() {
    float test_voltages[] = {10.0, 30.0, 60.0, 90.0, 120.0, 150.0}; // V
    float tolerance = 1.0; // V
    
    bool control_ok = true;
    
    Serial.println("Testing piezo control system...");
    
    for (int i = 0; i < 6; i++) {
        // Set target voltage
        setPiezoVoltage(test_voltages[i]);
        
        // Wait for settling
        delay(1000);
        
        // Measure actual voltage
        float actual_voltage = measurePiezoVoltage();
        float voltage_error = abs(actual_voltage - test_voltages[i]);
        
        Serial.print("Target: ");
        Serial.print(test_voltages[i]);
        Serial.print(" V, Actual: ");
        Serial.print(actual_voltage);
        Serial.print(" V, Error: ");
        Serial.print(voltage_error);
        Serial.println(" V");
        
        if (voltage_error > tolerance) {
            control_ok = false;
            Serial.println("FAIL: Piezo voltage accuracy");
        }
        
        // Test displacement response
        float displacement = readDisplacementSensor();
        float expected_displacement = test_voltages[i] * 100.0; // 100 nm/V
        float displacement_error = abs(displacement - expected_displacement);
        
        Serial.print("Expected displacement: ");
        Serial.print(expected_displacement);
        Serial.print(" nm, Actual: ");
        Serial.print(displacement);
        Serial.print(" nm, Error: ");
        Serial.print(displacement_error);
        Serial.println(" nm");
        
        if (displacement_error > 50.0) { // 50 nm tolerance
            control_ok = false;
            Serial.println("FAIL: Piezo displacement accuracy");
        }
    }
    
    // Return to zero
    setPiezoVoltage(0.0);
    
    return control_ok;
}
```

## Sample Positioning System Testing

### Stepper Motor Accuracy Test
```
Stepper Motor Test Procedure:
1. Test positioning accuracy:
   - Move to known positions using encoder feedback
   - Measure actual position with laser interferometer
   - Calculate positioning accuracy and repeatability
2. Test speed and acceleration:
   - Various move profiles
   - Measure settling time and overshoot
3. Test load capacity:
   - With various sample weights
   - Verify no step loss or position drift
4. Test micro-stepping performance:
   - Smoothness of motion
   - Resolution verification
```

**Expected Results:**
- Positioning accuracy: ±0.5 μm
- Repeatability: ±0.1 μm
- Resolution: 0.1 μm per step
- Maximum speed: 10 mm/s
- Settling time: <2 seconds
- No step loss under rated load

### Positioning System Test
```cpp
// Test Sample Positioning System
bool testPositioningSystem() {
    float test_positions[] = {100.0, 500.0, 1000.0, 5000.0, 10000.0}; // μm
    float tolerance = 0.5; // μm
    
    bool positioning_ok = true;
    
    Serial.println("Testing sample positioning system...");
    
    // Test X-axis
    for (int i = 0; i < 5; i++) {
        // Move to position
        moveToPosition('X', test_positions[i]);
        
        // Wait for settling
        delay(2000);
        
        // Measure actual position
        float actual_position = getCurrentPosition('X');
        float position_error = abs(actual_position - test_positions[i]);
        
        Serial.print("X Target: ");
        Serial.print(test_positions[i]);
        Serial.print(" μm, Actual: ");
        Serial.print(actual_position);
        Serial.print(" μm, Error: ");
        Serial.print(position_error);
        Serial.println(" μm");
        
        if (position_error > tolerance) {
            positioning_ok = false;
            Serial.println("FAIL: X-axis positioning accuracy");
        }
        
        // Test repeatability
        float positions[5];
        for (int j = 0; j < 5; j++) {
            moveToPosition('X', test_positions[i]);
            delay(1000);
            positions[j] = getCurrentPosition('X');
        }
        
        float repeatability = calculateStandardDeviation(positions, 5);
        Serial.print("X Repeatability: ");
        Serial.print(repeatability);
        Serial.println(" μm");
        
        if (repeatability > 0.1) {
            positioning_ok = false;
            Serial.println("FAIL: X-axis repeatability");
        }
    }
    
    // Test Y-axis (similar to X-axis)
    // Test Z-axis (similar to X-axis)
    
    // Return to home position
    moveToPosition('X', 0.0);
    moveToPosition('Y', 0.0);
    moveToPosition('Z', 0.0);
    
    return positioning_ok;
}
```

## Environmental Control Testing

### Temperature Control System Test
```
Temperature Control Test Procedure:
1. Set target temperature to 25°C
2. Monitor temperature stability over 4 hours
3. Test temperature ramp rates (heating and cooling)
4. Measure temperature uniformity across chamber
5. Test response to thermal disturbances
6. Verify over-temperature protection
```

**Expected Results:**
- Temperature stability: ±0.1°C over 4 hours
- Temperature uniformity: ±0.2°C across chamber
- Heating rate: 2°C/minute maximum
- Cooling rate: 1°C/minute maximum
- Response time: <5 minutes to 90% of step
- Over-temperature protection: <85°C

### Environmental Control Test
```cpp
// Test Environmental Control System
bool testEnvironmentalControl() {
    float target_temperatures[] = {20.0, 25.0, 30.0, 35.0, 40.0}; // °C
    float temperature_tolerance = 0.2; // °C
    
    bool control_ok = true;
    
    Serial.println("Testing environmental control system...");
    
    for (int i = 0; i < 5; i++) {
        // Set target temperature
        setTargetTemperature(target_temperatures[i]);
        
        // Wait for settling (up to 30 minutes)
        uint32_t start_time = millis();
        bool settled = false;
        
        while (millis() - start_time < 1800000) { // 30 minutes timeout
            updateEnvironmentalControl();
            
            float current_temp = readTemperature();
            
            // Check if temperature is within tolerance
            if (abs(current_temp - target_temperatures[i]) < temperature_tolerance) {
                if (!settled) {
                    settled = true;
                    Serial.print("Temperature settled at: ");
                    Serial.print(current_temp);
                    Serial.println(" °C");
                }
            } else {
                settled = false;
            }
            
            // Consider stable if settled for 5 minutes
            if (settled && (millis() - start_time > 300000)) {
                break;
            }
            
            delay(10000); // Check every 10 seconds
        }
        
        // Verify final temperature
        float final_temp = readTemperature();
        float temp_error = abs(final_temp - target_temperatures[i]);
        
        Serial.print("Target: ");
        Serial.print(target_temperatures[i]);
        Serial.print(" °C, Actual: ");
        Serial.print(final_temp);
        Serial.print(" °C, Error: ");
        Serial.print(temp_error);
        Serial.println(" °C");
        
        if (temp_error > temperature_tolerance) {
            control_ok = false;
            Serial.println("FAIL: Temperature control accuracy");
        }
        
        // Test stability over 1 hour
        if (i == 1) { // Test at 25°C
            Serial.println("Testing temperature stability...");
            
            float temp_readings[60];
            for (int j = 0; j < 60; j++) {
                temp_readings[j] = readTemperature();
                delay(60000); // 1 minute intervals
            }
            
            float stability = calculateStandardDeviation(temp_readings, 60);
            Serial.print("Temperature stability (1 hour): ");
            Serial.print(stability);
            Serial.println(" °C");
            
            if (stability > 0.1) {
                control_ok = false;
                Serial.println("FAIL: Temperature stability");
            }
        }
    }
    
    // Return to room temperature
    setTargetTemperature(25.0);
    
    return control_ok;
}
```

## Complete Indentation Test Validation

### Reference Material Testing
```
Reference Material Test Procedure:
1. Use certified reference materials:
   - Fused silica (H = 9.0 ± 0.5 GPa, E = 72 ± 2 GPa)
   - Aluminum (H = 1.5 ± 0.1 GPa, E = 70 ± 2 GPa)
   - Steel (H = 6.0 ± 0.3 GPa, E = 210 ± 5 GPa)
2. Perform multiple indentations (minimum 10 per material)
3. Calculate hardness and elastic modulus
4. Compare with certified values
5. Calculate measurement uncertainty
6. Verify repeatability and reproducibility
```

**Expected Results:**
- Hardness accuracy: ±5% of certified value
- Modulus accuracy: ±10% of certified value
- Repeatability: <5% coefficient of variation
- Reproducibility: <10% coefficient of variation
- Measurement uncertainty: <±10% (k=2)

### Complete Indentation Test
```cpp
// Test Complete Indentation System
bool testCompleteIndentation() {
    // Test parameters
    TestParameters test_params;
    test_params.max_load = 1000.0;      // μN
    test_params.loading_rate = 100.0;   // μN/s
    test_params.unloading_rate = 200.0; // μN/s
    test_params.hold_time = 10.0;       // seconds
    test_params.test_mode = 0;          // Load control
    test_params.indenter_type = 0;      // Berkovich
    
    bool test_ok = true;
    
    Serial.println("Testing complete indentation system...");
    
    // Perform reference material tests
    float fused_silica_hardness[10];
    float fused_silica_modulus[10];
    
    for (int i = 0; i < 10; i++) {
        Serial.print("Fused silica test ");
        Serial.print(i + 1);
        Serial.println("/10");
        
        // Perform indentation test
        MaterialProperties properties = performIndentationTest(test_params);
        
        fused_silica_hardness[i] = properties.hardness;
        fused_silica_modulus[i] = properties.elastic_modulus;
        
        Serial.print("Hardness: ");
        Serial.print(properties.hardness);
        Serial.print(" GPa, Modulus: ");
        Serial.print(properties.elastic_modulus);
        Serial.println(" GPa");
        
        // Move to new position for next test
        moveToPosition('X', getCurrentPosition('X') + 50.0);
    }
    
    // Calculate statistics
    float hardness_mean = calculateMean(fused_silica_hardness, 10);
    float hardness_std = calculateStandardDeviation(fused_silica_hardness, 10);
    float modulus_mean = calculateMean(fused_silica_modulus, 10);
    float modulus_std = calculateStandardDeviation(fused_silica_modulus, 10);
    
    Serial.print("Fused silica hardness: ");
    Serial.print(hardness_mean);
    Serial.print(" ± ");
    Serial.print(hardness_std);
    Serial.println(" GPa");
    
    Serial.print("Fused silica modulus: ");
    Serial.print(modulus_mean);
    Serial.print(" ± ");
    Serial.print(modulus_std);
    Serial.println(" GPa");
    
    // Check against certified values
    float hardness_error = abs(hardness_mean - 9.0) / 9.0 * 100.0;
    float modulus_error = abs(modulus_mean - 72.0) / 72.0 * 100.0;
    
    Serial.print("Hardness error: ");
    Serial.print(hardness_error);
    Serial.println(" %");
    
    Serial.print("Modulus error: ");
    Serial.print(modulus_error);
    Serial.println(" %");
    
    if (hardness_error > 5.0 || modulus_error > 10.0) {
        test_ok = false;
        Serial.println("FAIL: Reference material accuracy");
    }
    
    // Check repeatability
    float hardness_cv = hardness_std / hardness_mean * 100.0;
    float modulus_cv = modulus_std / modulus_mean * 100.0;
    
    Serial.print("Hardness CV: ");
    Serial.print(hardness_cv);
    Serial.println(" %");
    
    Serial.print("Modulus CV: ");
    Serial.print(modulus_cv);
    Serial.println(" %");
    
    if (hardness_cv > 5.0 || modulus_cv > 10.0) {
        test_ok = false;
        Serial.println("FAIL: Repeatability specification");
    }
    
    return test_ok;
}
```

## Data Acquisition and Analysis Testing

### Data Quality Verification
```
Data Quality Test Procedure:
1. Acquire load-displacement curves at various loads
2. Verify data integrity and completeness
3. Check for noise levels and filtering effectiveness
4. Validate timestamp accuracy and synchronization
5. Test data storage and retrieval
6. Verify calculation algorithms
```

**Expected Results:**
- Data completeness: 100% (no missing points)
- Sampling rate: 1000 Hz ± 0.1%
- Timestamp accuracy: ±1 ms
- Signal-to-noise ratio: >40 dB
- Data storage: 100% success rate
- Calculation accuracy: ±1% of theoretical

### Data Analysis Test
```cpp
// Test Data Analysis System
bool testDataAnalysis() {
    bool analysis_ok = true;
    
    Serial.println("Testing data analysis system...");
    
    // Generate synthetic load-displacement data
    float synthetic_loads[100];
    float synthetic_displacements[100];
    
    // Create ideal Berkovich indentation curve
    for (int i = 0; i < 100; i++) {
        float load = i * 10.0; // μN
        float displacement = pow(load / 1000.0, 2.0/3.0) * 100.0; // Simplified relationship
        
        synthetic_loads[i] = load;
        synthetic_displacements[i] = displacement;
    }
    
    // Test Oliver-Pharr analysis
    MaterialProperties calculated_properties = calculateOliverPharr(
        synthetic_loads, synthetic_displacements, 100);
    
    // Expected values for synthetic data
    float expected_hardness = 5.0; // GPa
    float expected_modulus = 100.0; // GPa
    
    float hardness_error = abs(calculated_properties.hardness - expected_hardness) / expected_hardness * 100.0;
    float modulus_error = abs(calculated_properties.elastic_modulus - expected_modulus) / expected_modulus * 100.0;
    
    Serial.print("Calculated hardness: ");
    Serial.print(calculated_properties.hardness);
    Serial.print(" GPa (error: ");
    Serial.print(hardness_error);
    Serial.println(" %)");
    
    Serial.print("Calculated modulus: ");
    Serial.print(calculated_properties.elastic_modulus);
    Serial.print(" GPa (error: ");
    Serial.print(modulus_error);
    Serial.println(" %)");
    
    if (hardness_error > 5.0 || modulus_error > 10.0) {
        analysis_ok = false;
        Serial.println("FAIL: Data analysis accuracy");
    }
    
    // Test contact detection algorithm
    bool contact_detected = testContactDetection(synthetic_loads, synthetic_displacements, 100);
    
    if (!contact_detected) {
        analysis_ok = false;
        Serial.println("FAIL: Contact detection");
    } else {
        Serial.println("PASS: Contact detection");
    }
    
    return analysis_ok;
}
```

## System Integration Testing

### Complete System Performance Test
```
System Integration Test Procedure:
1. Power on system and perform initialization
2. Run all individual subsystem tests
3. Perform complete indentation sequence
4. Verify all data flows and communications
5. Test fault detection and recovery
6. Validate environmental stability
7. Check safety system responses
```

**Expected Results:**
- System initialization: <30 seconds
- All subsystem tests: Pass
- Complete indentation: Successful
- Data flow: 100% integrity
- Fault detection: <1 second response
- Environmental stability: Within specifications
- Safety systems: All functional

### System Integration Test
```cpp
// Complete System Integration Test
bool performSystemIntegrationTest() {
    Serial.println("=== System Integration Test ===");
    
    bool system_ok = true;
    
    // Test all subsystems
    Serial.println("Testing subsystems...");
    system_ok &= testForceControl();
    system_ok &= testDisplacementControl();
    system_ok &= testPiezoControl();
    system_ok &= testPositioningSystem();
    system_ok &= testEnvironmentalControl();
    system_ok &= testDataAnalysis();
    
    if (!system_ok) {
        Serial.println("FAIL: Subsystem tests");
        return false;
    }
    
    // Test complete indentation sequence
    Serial.println("Testing complete indentation sequence...");
    system_ok &= testCompleteIndentation();
    
    if (!system_ok) {
        Serial.println("FAIL: Complete indentation test");
        return false;
    }
    
    // Test communication systems
    Serial.println("Testing communication systems...");
    system_ok &= testCommunicationSystems();
    
    if (!system_ok) {
        Serial.println("FAIL: Communication systems");
        return false;
    }
    
    // Test safety systems
    Serial.println("Testing safety systems...");
    system_ok &= testSafetySystems();
    
    if (!system_ok) {
        Serial.println("FAIL: Safety systems");
        return false;
    }
    
    // Test long-term stability
    Serial.println("Testing long-term stability...");
    system_ok &= testLongTermStability();
    
    if (!system_ok) {
        Serial.println("FAIL: Long-term stability");
        return false;
    }
    
    if (system_ok) {
        Serial.println("PASS: System integration test complete");
    } else {
        Serial.println("FAIL: System integration test failed");
    }
    
    return system_ok;
}
```

## Performance Validation

### Accuracy Requirements
- [ ] Force measurement: ±0.1 μN or ±0.1% of reading
- [ ] Displacement measurement: ±0.1 nm or ±0.1% of reading
- [ ] Hardness accuracy: ±5% of certified value
- [ ] Modulus accuracy: ±10% of certified value
- [ ] Temperature control: ±0.1°C
- [ ] Positioning accuracy: ±0.5 μm

### Repeatability Requirements
- [ ] Force repeatability: ±0.05 μN (1σ)
- [ ] Displacement repeatability: ±0.05 nm (1σ)
- [ ] Hardness repeatability: <5% coefficient of variation
- [ ] Modulus repeatability: <10% coefficient of variation
- [ ] Temperature repeatability: ±0.05°C (1σ)
- [ ] Positioning repeatability: ±0.1 μm (1σ)

### Stability Requirements
- [ ] Force stability: ±0.1 μN over 1 hour
- [ ] Displacement stability: ±0.1 nm over 1 hour
- [ ] Temperature stability: ±0.1°C over 8 hours
- [ ] System drift: <0.1% per day
- [ ] Calibration stability: <0.5% per month

## Standards Compliance Testing

### ISO 14577 Compliance
- [ ] Indenter geometry: Berkovich pyramid, 65.03° angle
- [ ] Load application: Controlled rate, smooth loading
- [ ] Displacement measurement: Continuous monitoring
- [ ] Data analysis: Oliver-Pharr method
- [ ] Calibration: Area function determination
- [ ] Uncertainty analysis: Complete evaluation

### ASTM E2546 Compliance
- [ ] Test procedure: Standardized methodology
- [ ] Calibration requirements: Traceable standards
- [ ] Data reporting: Complete documentation
- [ ] Quality control: Reference materials
- [ ] Operator training: Certified procedures

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: Force control instability
**Solution**: Check PID parameters, verify load cell calibration, inspect electrical connections

**Issue**: Displacement measurement drift
**Solution**: Check sensor calibration, verify temperature stability, inspect mechanical mounting

**Issue**: Poor hardness repeatability
**Solution**: Verify indenter condition, check surface preparation, validate test parameters

**Issue**: Contact detection problems
**Solution**: Adjust detection threshold, verify sensor noise levels, check approach speed

**Issue**: Temperature control oscillations
**Solution**: Tune PID parameters, check thermal mass, verify sensor placement

**Issue**: Positioning accuracy errors
**Solution**: Recalibrate stepper motors, check mechanical backlash, verify encoder operation

## Maintenance Schedule

### Daily Maintenance
- [ ] Check system status and error logs
- [ ] Verify temperature and humidity readings
- [ ] Inspect indenter condition
- [ ] Check safety system operation

### Weekly Maintenance
- [ ] Verify force and displacement calibration
- [ ] Clean optical surfaces
- [ ] Check positioning accuracy
- [ ] Test emergency stop system

### Monthly Maintenance
- [ ] Complete system calibration
- [ ] Inspect mechanical components
- [ ] Update software if needed
- [ ] Perform reference material tests

### Annual Maintenance
- [ ] Complete recalibration with traceable standards
- [ ] Replace wear components
- [ ] Comprehensive safety testing
- [ ] Documentation and records update

## Quality Assurance

### Measurement Uncertainty Analysis
- [ ] Identify all uncertainty sources
- [ ] Quantify individual uncertainty components
- [ ] Combine uncertainties using GUM methodology
- [ ] Calculate expanded uncertainty (k=2)
- [ ] Document uncertainty budget

### Proficiency Testing
- [ ] Participate in interlaboratory comparisons
- [ ] Test certified reference materials
- [ ] Document measurement results
- [ ] Investigate any discrepancies
- [ ] Maintain measurement traceability

This comprehensive testing guide ensures thorough validation of the nano-indentation system, providing confidence in measurement accuracy and reliability for critical materials characterization applications.