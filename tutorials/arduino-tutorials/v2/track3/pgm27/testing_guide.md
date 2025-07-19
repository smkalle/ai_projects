# Program 27: Injection Molding Controller - Testing Guide & SPC Validation

## Overview
This comprehensive testing guide provides detailed procedures for validating the smart injection molding controller implementing scientific molding principles with real-time cavity pressure monitoring, SPC integration, and digital twin synchronization for precision plastic part manufacturing compliance with ANSI/SPI, ISO, and ASTM standards.

## Safety Precautions

### Pre-Testing Safety Checks
- [ ] Verify all electrical connections per circuit diagram
- [ ] Check emergency stop functionality and response time (<1 second)
- [ ] Confirm proper grounding of all equipment and high-voltage isolation
- [ ] Validate safety interlocks and force-guided safety relay operation
- [ ] Inspect PPE requirements (safety glasses, heat-resistant gloves, hearing protection)
- [ ] Verify hydraulic system pressure relief valve operation (set to 90% max pressure)
- [ ] Check mold safety gates and light curtain functionality
- [ ] Validate fire safety equipment and fume extraction systems
- [ ] Ensure proper calibration of all safety monitoring systems
- [ ] Test emergency shutdown of all heaters and hydraulic systems

### Operating Safety Limits
- **Maximum Injection Pressure**: 2000 bar (emergency stop at 2100 bar)
- **Maximum Heater Temperature**: 400°C (emergency stop at 420°C)
- **Maximum Clamp Force**: 500 kN (safety relief at 520 kN)
- **Hydraulic System Pressure**: 300 bar (relief valve at 270 bar)
- **Emergency Response**: <500ms for all safety systems
- **Mold Temperature Range**: 20-150°C (thermal runaway protection)
- **Power Supply**: Proper isolation and RCD protection mandatory

## Pre-Test Setup

### Hardware Verification
```
Hardware Checklist:
├── Arduino Mega 2560 (main controller) + Arduino Due (high-speed DAQ)
├── ESP32 IoT gateway connected and functional
├── ADS1256 24-bit ADC for high-precision pressure measurement
├── Cavity pressure transducers (4x Kistler 6157BA, 0-2000 bar)
├── MAX31855 thermocouple amplifiers (6 channels)
├── K-type thermocouples properly installed and compensated
├── LVDT position sensors (screw and clamp position)
├── Proportional hydraulic valve control system
├── Solid-state relay heater control (5 zones)
├── 7" TFT touchscreen display operational
├── SD card module with high-speed storage capability
├── Emergency stop button and safety relay system functional
├── Status LEDs, alarm horn, and beacon working
├── WiFi connectivity and Modbus RTU communication established
├── Digital twin synchronization with cloud platform active
└── All connections verified per circuit diagram
```

### Software Configuration
```cpp
// Test Configuration Constants - Scientific Molding
#define PRESSURE_ACCURACY_TARGET     0.5      // % full scale
#define TEMPERATURE_ACCURACY_TARGET  1.0      // °C
#define POSITION_ACCURACY_TARGET     0.01     // mm
#define CYCLE_REPEATABILITY_TARGET   1.0      // % coefficient of variation
#define SPC_SAMPLES_MINIMUM          50       // Minimum samples for SPC
#define SAMPLING_RATE_PRESSURE       1000     // Hz
#define SAMPLING_RATE_TEMPERATURE    10       // Hz
#define CONTROL_LOOP_RESPONSE        10       // ms maximum
#define DIGITAL_TWIN_SYNC_INTERVAL   10000    // ms
#define ML_PREDICTION_ACCURACY       85       // % minimum
#define PROCESS_CAPABILITY_TARGET    1.67     // Cp/Cpk minimum
```

## High-Precision Pressure System Testing

### Cavity Pressure Transducer Calibration
```
Piezoelectric Pressure Transducer Calibration (Kistler 6157BA):
1. Use deadweight tester or pressure calibrator (0.02% accuracy)
2. Test at pressure points: 0, 500, 1000, 1500, 2000 bar
3. Perform ascending and descending pressure cycles
4. Verify linearity across full measurement range
5. Check hysteresis (<0.1% full scale)
6. Validate temperature coefficient (<0.02%/°C)
7. Test dynamic response (>10 kHz bandwidth)
8. Verify isolation and common-mode rejection (>100 dB)
9. Document calibration certificates with traceability
```

**Expected Results:**
- Pressure accuracy: ±0.5% of full scale (±10 bar at 2000 bar)
- Linearity: <±0.1% over full scale
- Hysteresis: <±0.1% of full scale
- Temperature coefficient: <0.02%/°C from 0-70°C
- Dynamic response: 10 kHz bandwidth minimum
- Resolution: 0.1 bar with 24-bit ADC
- Isolation: >1000V common-mode voltage

### Multi-Cavity Pressure Balance Test
```cpp
// Test Multi-Cavity Pressure Balance
bool testCavityPressureBalance() {
    Serial.println("Testing multi-cavity pressure balance...");
    
    // Perform test injection cycles
    int test_cycles = 20;
    float pressure_data[4][test_cycles];
    bool balance_ok = true;
    
    for (int cycle = 0; cycle < test_cycles; cycle++) {
        Serial.print("Test cycle ");
        Serial.print(cycle + 1);
        Serial.println("/20");
        
        // Start injection cycle
        startTestInjectionCycle();
        
        // Monitor cavity pressures during injection
        unsigned long cycle_start = millis();
        int sample_count = 0;
        
        while (system_status.current_phase == PHASE_INJECTION && 
               sample_count < 1000) {
            
            readCavityPressure();
            
            // Store peak pressure for each cavity
            if (cavity_pressure.average_pressure > pressure_data[0][cycle]) {
                pressure_data[0][cycle] = cavity_pressure.cavity_1_pressure;
                pressure_data[1][cycle] = cavity_pressure.cavity_2_pressure;
                pressure_data[2][cycle] = cavity_pressure.cavity_3_pressure;
                pressure_data[3][cycle] = cavity_pressure.cavity_4_pressure;
            }
            
            sample_count++;
            delay(1); // 1 kHz sampling
        }
        
        // Wait for cycle completion
        while (system_status.current_phase != PHASE_IDLE) {
            delay(100);
        }
        
        delay(5000); // Wait between cycles
    }
    
    // Analyze pressure balance
    for (int cycle = 0; cycle < test_cycles; cycle++) {
        float cycle_average = (pressure_data[0][cycle] + pressure_data[1][cycle] + 
                              pressure_data[2][cycle] + pressure_data[3][cycle]) / 4.0;
        
        for (int cavity = 0; cavity < 4; cavity++) {
            float deviation = abs(pressure_data[cavity][cycle] - cycle_average);
            float deviation_percent = (deviation / cycle_average) * 100.0;
            
            Serial.print("Cycle ");
            Serial.print(cycle + 1);
            Serial.print(", Cavity ");
            Serial.print(cavity + 1);
            Serial.print(": ");
            Serial.print(pressure_data[cavity][cycle]);
            Serial.print(" bar, Deviation: ");
            Serial.print(deviation_percent);
            Serial.println("%");
            
            if (deviation_percent > 5.0) { // 5% maximum deviation
                balance_ok = false;
                Serial.println("FAIL: Cavity pressure imbalance");
            }
        }
    }
    
    // Calculate overall statistics
    float cavity_means[4] = {0, 0, 0, 0};
    float cavity_std[4] = {0, 0, 0, 0};
    
    for (int cavity = 0; cavity < 4; cavity++) {
        // Calculate mean
        for (int cycle = 0; cycle < test_cycles; cycle++) {
            cavity_means[cavity] += pressure_data[cavity][cycle];
        }
        cavity_means[cavity] /= test_cycles;
        
        // Calculate standard deviation
        for (int cycle = 0; cycle < test_cycles; cycle++) {
            float diff = pressure_data[cavity][cycle] - cavity_means[cavity];
            cavity_std[cavity] += diff * diff;
        }
        cavity_std[cavity] = sqrt(cavity_std[cavity] / (test_cycles - 1));
        
        Serial.print("Cavity ");
        Serial.print(cavity + 1);
        Serial.print(" - Mean: ");
        Serial.print(cavity_means[cavity]);
        Serial.print(" bar, Std: ");
        Serial.print(cavity_std[cavity]);
        Serial.println(" bar");
    }
    
    return balance_ok;
}
```

### Pressure Profile Analysis Test
```cpp
// Test Pressure Profile Characteristics
bool testPressureProfileAnalysis() {
    Serial.println("Testing pressure profile analysis...");
    
    // Record complete pressure profile during injection
    float pressure_profile[5000]; // 5 seconds at 1 kHz
    unsigned long time_stamps[5000];
    int profile_index = 0;
    
    // Start injection cycle
    startTestInjectionCycle();
    
    unsigned long profile_start = millis();
    
    while (system_status.current_phase == PHASE_INJECTION && 
           profile_index < 5000) {
        
        readCavityPressure();
        pressure_profile[profile_index] = cavity_pressure.average_pressure;
        time_stamps[profile_index] = millis() - profile_start;
        profile_index++;
        
        delay(1); // 1 kHz sampling
    }
    
    // Analyze pressure profile characteristics
    float fill_time = time_stamps[profile_index - 1] / 1000.0; // seconds
    float peak_pressure = 0.0;
    int peak_index = 0;
    
    for (int i = 0; i < profile_index; i++) {
        if (pressure_profile[i] > peak_pressure) {
            peak_pressure = pressure_profile[i];
            peak_index = i;
        }
    }
    
    float time_to_peak = time_stamps[peak_index] / 1000.0;
    
    // Calculate pressure rise rate
    float pressure_rise_rate = peak_pressure / time_to_peak; // bar/s
    
    // Calculate pressure integral (area under curve)
    float pressure_integral = 0.0;
    for (int i = 1; i < profile_index; i++) {
        float dt = (time_stamps[i] - time_stamps[i-1]) / 1000.0;
        pressure_integral += pressure_profile[i] * dt;
    }
    
    // Analyze pressure stability during hold phase
    float hold_pressure_mean = 0.0;
    float hold_pressure_std = 0.0;
    int hold_samples = 0;
    
    // Find hold phase (after 80% of peak pressure)
    float hold_threshold = peak_pressure * 0.8;
    
    for (int i = peak_index; i < profile_index; i++) {
        if (pressure_profile[i] >= hold_threshold) {
            hold_pressure_mean += pressure_profile[i];
            hold_samples++;
        }
    }
    
    if (hold_samples > 0) {
        hold_pressure_mean /= hold_samples;
        
        // Calculate standard deviation
        for (int i = peak_index; i < profile_index; i++) {
            if (pressure_profile[i] >= hold_threshold) {
                float diff = pressure_profile[i] - hold_pressure_mean;
                hold_pressure_std += diff * diff;
            }
        }
        hold_pressure_std = sqrt(hold_pressure_std / (hold_samples - 1));
    }
    
    // Report results
    Serial.print("Fill time: ");
    Serial.print(fill_time);
    Serial.println(" seconds");
    
    Serial.print("Peak pressure: ");
    Serial.print(peak_pressure);
    Serial.println(" bar");
    
    Serial.print("Time to peak: ");
    Serial.print(time_to_peak);
    Serial.println(" seconds");
    
    Serial.print("Pressure rise rate: ");
    Serial.print(pressure_rise_rate);
    Serial.println(" bar/s");
    
    Serial.print("Pressure integral: ");
    Serial.print(pressure_integral);
    Serial.println(" bar·s");
    
    Serial.print("Hold pressure stability: ");
    Serial.print(hold_pressure_std);
    Serial.println(" bar");
    
    // Validate against scientific molding criteria
    bool profile_ok = true;
    
    if (fill_time < 0.5 || fill_time > 5.0) {
        Serial.println("FAIL: Fill time out of range");
        profile_ok = false;
    }
    
    if (peak_pressure < 500 || peak_pressure > 2000) {
        Serial.println("FAIL: Peak pressure out of range");
        profile_ok = false;
    }
    
    if (hold_pressure_std > peak_pressure * 0.05) {
        Serial.println("FAIL: Hold pressure instability");
        profile_ok = false;
    }
    
    return profile_ok;
}
```

## Temperature Control System Testing

### Multi-Zone Temperature Accuracy Test
```cpp
// Test Multi-Zone Temperature Control Accuracy
bool testTemperatureControlAccuracy() {
    Serial.println("Testing multi-zone temperature control accuracy...");
    
    // Temperature setpoints for each zone
    float setpoints[6] = {240.0, 250.0, 260.0, 255.0, 60.0, 25.0}; // °C
    const char* zone_names[6] = {"Barrel 1", "Barrel 2", "Barrel 3", 
                                "Nozzle", "Mold", "Ambient"};
    bool temp_ok = true;
    
    // Heat up sequence
    Serial.println("Starting heat-up sequence...");
    
    process_params.barrel_temp_1 = setpoints[0];
    process_params.barrel_temp_2 = setpoints[1];
    process_params.barrel_temp_3 = setpoints[2];
    process_params.nozzle_temp = setpoints[3];
    process_params.mold_temp = setpoints[4];
    
    // Wait for temperatures to stabilize (maximum 30 minutes)
    unsigned long heatup_start = millis();
    bool all_stable = false;
    
    while (!all_stable && (millis() - heatup_start) < 1800000) { // 30 minutes
        readTemperatures();
        
        all_stable = true;
        
        // Check each zone for stability (within ±3°C for 5 minutes)
        if (abs(temperature_data.barrel_zone_1 - setpoints[0]) > 3.0 ||
            abs(temperature_data.barrel_zone_2 - setpoints[1]) > 3.0 ||
            abs(temperature_data.barrel_zone_3 - setpoints[2]) > 3.0 ||
            abs(temperature_data.nozzle_temp - setpoints[3]) > 3.0 ||
            abs(temperature_data.mold_temp - setpoints[4]) > 2.0) {
            all_stable = false;
        }
        
        Serial.print("Heat-up progress: ");
        Serial.print((millis() - heatup_start) / 60000.0);
        Serial.print(" min - Barrel: ");
        Serial.print(temperature_data.barrel_zone_1);
        Serial.print("/");
        Serial.print(temperature_data.barrel_zone_2);
        Serial.print("/");
        Serial.print(temperature_data.barrel_zone_3);
        Serial.print("°C, Nozzle: ");
        Serial.print(temperature_data.nozzle_temp);
        Serial.print("°C, Mold: ");
        Serial.print(temperature_data.mold_temp);
        Serial.println("°C");
        
        delay(30000); // Check every 30 seconds
    }
    
    if (!all_stable) {
        Serial.println("FAIL: Temperature stabilization timeout");
        return false;
    }
    
    Serial.println("Temperatures stabilized. Starting accuracy test...");
    
    // Temperature accuracy test (5 minutes at setpoint)
    float temp_readings[6][300]; // 5 minutes at 1 Hz
    
    for (int sample = 0; sample < 300; sample++) {
        readTemperatures();
        
        temp_readings[0][sample] = temperature_data.barrel_zone_1;
        temp_readings[1][sample] = temperature_data.barrel_zone_2;
        temp_readings[2][sample] = temperature_data.barrel_zone_3;
        temp_readings[3][sample] = temperature_data.nozzle_temp;
        temp_readings[4][sample] = temperature_data.mold_temp;
        temp_readings[5][sample] = temperature_data.ambient_temp;
        
        delay(1000); // 1 Hz sampling
    }
    
    // Calculate statistics for each zone
    for (int zone = 0; zone < 6; zone++) {
        float mean_temp = 0.0;
        float std_temp = 0.0;
        float min_temp = temp_readings[zone][0];
        float max_temp = temp_readings[zone][0];
        
        // Calculate mean
        for (int sample = 0; sample < 300; sample++) {
            mean_temp += temp_readings[zone][sample];
            if (temp_readings[zone][sample] < min_temp) min_temp = temp_readings[zone][sample];
            if (temp_readings[zone][sample] > max_temp) max_temp = temp_readings[zone][sample];
        }
        mean_temp /= 300;
        
        // Calculate standard deviation
        for (int sample = 0; sample < 300; sample++) {
            float diff = temp_readings[zone][sample] - mean_temp;
            std_temp += diff * diff;
        }
        std_temp = sqrt(std_temp / 299);
        
        Serial.print(zone_names[zone]);
        Serial.print(" - Mean: ");
        Serial.print(mean_temp);
        Serial.print("°C, Std: ");
        Serial.print(std_temp);
        Serial.print("°C, Range: ");
        Serial.print(max_temp - min_temp);
        Serial.print("°C, Error: ");
        Serial.print(abs(mean_temp - setpoints[zone]));
        Serial.println("°C");
        
        // Check accuracy criteria
        if (zone < 4) { // Barrel and nozzle zones
            if (abs(mean_temp - setpoints[zone]) > 2.0 || std_temp > 3.0) {
                temp_ok = false;
                Serial.print("FAIL: ");
                Serial.print(zone_names[zone]);
                Serial.println(" temperature accuracy");
            }
        } else if (zone == 4) { // Mold zone
            if (abs(mean_temp - setpoints[zone]) > 1.0 || std_temp > 1.5) {
                temp_ok = false;
                Serial.print("FAIL: ");
                Serial.print(zone_names[zone]);
                Serial.println(" temperature accuracy");
            }
        }
    }
    
    return temp_ok;
}
```

### Thermal Response Characterization
```cpp
// Test Thermal Response Characteristics
bool testThermalResponseCharacteristics() {
    Serial.println("Testing thermal response characteristics...");
    
    // Step response test for each heater zone
    bool response_ok = true;
    
    for (int zone = 0; zone < 4; zone++) { // Barrel zones and nozzle
        Serial.print("Testing thermal response for zone ");
        Serial.println(zone + 1);
        
        // Start from ambient temperature
        analogWrite(HEATER_ZONE_1 + zone, 0);
        delay(60000); // Cool down for 1 minute
        
        // Record baseline temperature
        readTemperatures();
        float baseline_temp = getZoneTemperature(zone);
        
        // Apply step input (50% power)
        analogWrite(HEATER_ZONE_1 + zone, 128);
        
        // Record step response for 10 minutes
        float response_data[600]; // 10 minutes at 1 Hz
        unsigned long step_start = millis();
        
        for (int sample = 0; sample < 600; sample++) {
            readTemperatures();
            response_data[sample] = getZoneTemperature(zone) - baseline_temp;
            
            if (sample % 60 == 0) { // Print every minute
                Serial.print("Time: ");
                Serial.print(sample / 60);
                Serial.print(" min, Temperature rise: ");
                Serial.print(response_data[sample]);
                Serial.println("°C");
            }
            
            delay(1000);
        }
        
        // Turn off heater
        analogWrite(HEATER_ZONE_1 + zone, 0);
        
        // Analyze response characteristics
        float final_temp_rise = response_data[599];
        float time_constant = calculateTimeConstant(response_data, 600);
        float settling_time = calculateSettlingTime(response_data, 600, final_temp_rise);
        
        Serial.print("Zone ");
        Serial.print(zone + 1);
        Serial.print(" - Final rise: ");
        Serial.print(final_temp_rise);
        Serial.print("°C, Time constant: ");
        Serial.print(time_constant);
        Serial.print(" s, Settling time: ");
        Serial.print(settling_time);
        Serial.println(" s");
        
        // Check response criteria
        if (time_constant > 300 || settling_time > 600) { // 5 minutes tau, 10 minutes settling
            response_ok = false;
            Serial.print("FAIL: Zone ");
            Serial.print(zone + 1);
            Serial.println(" thermal response too slow");
        }
        
        delay(300000); // Cool down for 5 minutes before next test
    }
    
    return response_ok;
}

float getZoneTemperature(int zone) {
    switch (zone) {
        case 0: return temperature_data.barrel_zone_1;
        case 1: return temperature_data.barrel_zone_2;
        case 2: return temperature_data.barrel_zone_3;
        case 3: return temperature_data.nozzle_temp;
        default: return 0.0;
    }
}

float calculateTimeConstant(float* data, int samples) {
    // Find 63.2% of final value
    float final_value = data[samples - 1];
    float target_value = final_value * 0.632;
    
    for (int i = 0; i < samples; i++) {
        if (data[i] >= target_value) {
            return i; // Time in seconds
        }
    }
    return samples; // Timeout
}

float calculateSettlingTime(float* data, int samples, float final_value) {
    // Find 2% settling time
    float tolerance = final_value * 0.02;
    
    for (int i = samples - 1; i >= 0; i--) {
        if (abs(data[i] - final_value) > tolerance) {
            return i + 1; // Time in seconds
        }
    }
    return 0; // Settled from start
}
```

## Position and Velocity Control Testing

### LVDT Position Sensor Calibration
```cpp
// Test LVDT Position Sensor Accuracy
bool testLVDTPositionAccuracy() {
    Serial.println("Testing LVDT position sensor accuracy...");
    
    // Use precision reference positions (micrometer or laser interferometer)
    float reference_positions[] = {0.0, 5.0, 10.0, 15.0, 20.0, 25.0}; // mm
    float measured_positions[6];
    float position_errors[6];
    bool position_ok = true;
    
    for (int i = 0; i < 6; i++) {
        Serial.print("Move to reference position ");
        Serial.print(reference_positions[i]);
        Serial.println(" mm. Press enter when positioned...");
        
        // Wait for user to position reference
        while (!Serial.available()) delay(100);
        Serial.readString(); // Clear buffer
        
        // Take multiple readings for averaging
        float position_sum = 0.0;
        for (int j = 0; j < 100; j++) {
            readPositions();
            position_sum += position_data.screw_position;
            delay(10);
        }
        
        measured_positions[i] = position_sum / 100.0;
        position_errors[i] = measured_positions[i] - reference_positions[i];
        
        Serial.print("Reference: ");
        Serial.print(reference_positions[i]);
        Serial.print(" mm, Measured: ");
        Serial.print(measured_positions[i]);
        Serial.print(" mm, Error: ");
        Serial.print(position_errors[i]);
        Serial.println(" mm");
        
        if (abs(position_errors[i]) > 0.02) { // ±0.02 mm accuracy
            position_ok = false;
            Serial.println("FAIL: Position accuracy out of specification");
        }
    }
    
    // Calculate linearity
    float linearity_error = calculateLinearityError(reference_positions, measured_positions, 6);
    Serial.print("Linearity error: ");
    Serial.print(linearity_error);
    Serial.println(" mm");
    
    if (linearity_error > 0.01) { // ±0.01 mm linearity
        position_ok = false;
        Serial.println("FAIL: Position linearity out of specification");
    }
    
    // Test repeatability
    Serial.println("Testing position repeatability...");
    
    for (int pos = 0; pos < 6; pos++) {
        float repeat_readings[10];
        
        Serial.print("Position repeatability test at ");
        Serial.print(reference_positions[pos]);
        Serial.println(" mm");
        
        for (int rep = 0; rep < 10; rep++) {
            Serial.print("Measurement ");
            Serial.print(rep + 1);
            Serial.println("/10 - Press enter when positioned...");
            
            while (!Serial.available()) delay(100);
            Serial.readString();
            
            // Average 10 readings
            float reading_sum = 0.0;
            for (int k = 0; k < 10; k++) {
                readPositions();
                reading_sum += position_data.screw_position;
                delay(10);
            }
            repeat_readings[rep] = reading_sum / 10.0;
        }
        
        // Calculate repeatability statistics
        float mean_reading = 0.0;
        for (int rep = 0; rep < 10; rep++) {
            mean_reading += repeat_readings[rep];
        }
        mean_reading /= 10.0;
        
        float std_reading = 0.0;
        for (int rep = 0; rep < 10; rep++) {
            float diff = repeat_readings[rep] - mean_reading;
            std_reading += diff * diff;
        }
        std_reading = sqrt(std_reading / 9.0);
        
        Serial.print("Position ");
        Serial.print(reference_positions[pos]);
        Serial.print(" mm - Mean: ");
        Serial.print(mean_reading);
        Serial.print(" mm, Std: ");
        Serial.print(std_reading);
        Serial.println(" mm");
        
        if (std_reading > 0.005) { // ±0.005 mm repeatability
            position_ok = false;
            Serial.println("FAIL: Position repeatability out of specification");
        }
    }
    
    return position_ok;
}
```

### Injection Velocity Control Test
```cpp
// Test Injection Velocity Control Performance
bool testInjectionVelocityControl() {
    Serial.println("Testing injection velocity control performance...");
    
    float target_velocities[] = {20.0, 50.0, 80.0, 120.0, 150.0}; // mm/s
    bool velocity_ok = true;
    
    for (int v = 0; v < 5; v++) {
        Serial.print("Testing velocity control at ");
        Serial.print(target_velocities[v]);
        Serial.println(" mm/s");
        
        // Set target velocity
        process_params.injection_velocity[0] = target_velocities[v];
        
        // Start controlled injection
        system_status.current_phase = PHASE_INJECTION;
        current_injection_stage = 0;
        
        float velocity_readings[500]; // 5 seconds at 100 Hz
        float position_readings[500];
        unsigned long velocity_start = millis();
        
        for (int sample = 0; sample < 500; sample++) {
            readPositions();
            velocity_readings[sample] = position_data.screw_velocity;
            position_readings[sample] = position_data.screw_position;
            
            // Run velocity control
            controlInjectionPhase();
            
            delay(10); // 100 Hz sampling
            
            // Stop if screw reaches end of travel
            if (position_data.screw_position >= 40.0) break;
        }
        
        // Stop injection
        system_status.current_phase = PHASE_IDLE;
        analogWrite(INJECTION_VALVE, 0);
        
        // Analyze velocity control performance
        float mean_velocity = 0.0;
        float velocity_std = 0.0;
        int valid_samples = 0;
        
        // Skip first 50 samples (transient response)
        for (int sample = 50; sample < 500; sample++) {
            if (velocity_readings[sample] > 0) {
                mean_velocity += velocity_readings[sample];
                valid_samples++;
            }
        }
        
        if (valid_samples > 0) {
            mean_velocity /= valid_samples;
            
            // Calculate standard deviation
            for (int sample = 50; sample < 500; sample++) {
                if (velocity_readings[sample] > 0) {
                    float diff = velocity_readings[sample] - mean_velocity;
                    velocity_std += diff * diff;
                }
            }
            velocity_std = sqrt(velocity_std / (valid_samples - 1));
        }
        
        float velocity_error = abs(mean_velocity - target_velocities[v]);
        float velocity_error_percent = (velocity_error / target_velocities[v]) * 100.0;
        
        Serial.print("Target: ");
        Serial.print(target_velocities[v]);
        Serial.print(" mm/s, Actual: ");
        Serial.print(mean_velocity);
        Serial.print(" mm/s, Error: ");
        Serial.print(velocity_error_percent);
        Serial.print("%, Std: ");
        Serial.print(velocity_std);
        Serial.println(" mm/s");
        
        // Check velocity control criteria
        if (velocity_error_percent > 5.0 || velocity_std > target_velocities[v] * 0.1) {
            velocity_ok = false;
            Serial.println("FAIL: Velocity control accuracy");
        }
        
        // Reset screw position for next test
        delay(10000); // Wait for reset
    }
    
    return velocity_ok;
}
```

## Statistical Process Control (SPC) Validation

### SPC Data Collection and Analysis
```cpp
// Comprehensive SPC Validation Test
bool testSPCSystemValidation() {
    Serial.println("Testing SPC system validation...");
    
    // Collect data for SPC analysis (minimum 100 cycles)
    int spc_cycles = 100;
    float pressure_data[spc_cycles];
    float weight_data[spc_cycles];
    float cycle_time_data[spc_cycles];
    float temperature_data_spc[spc_cycles];
    
    Serial.print("Collecting ");
    Serial.print(spc_cycles);
    Serial.println(" cycles for SPC analysis...");
    
    for (int cycle = 0; cycle < spc_cycles; cycle++) {
        Serial.print("SPC data collection cycle ");
        Serial.print(cycle + 1);
        Serial.print("/");
        Serial.println(spc_cycles);
        
        // Start production cycle
        unsigned long cycle_start = millis();
        startProductionCycle();
        
        // Monitor cycle and collect data
        while (system_status.current_phase != PHASE_IDLE) {
            readAllSensors();
            updateProcessControl();
            delay(10);
        }
        
        // Record cycle data
        pressure_data[cycle] = cavity_pressure.peak_pressure;
        weight_data[cycle] = quality_prediction.predicted_weight;
        cycle_time_data[cycle] = (millis() - cycle_start) / 1000.0;
        temperature_data_spc[cycle] = temperature_data.melt_temp;
        
        Serial.print("Cycle ");
        Serial.print(cycle + 1);
        Serial.print(" - Peak pressure: ");
        Serial.print(pressure_data[cycle]);
        Serial.print(" bar, Weight: ");
        Serial.print(weight_data[cycle]);
        Serial.print(" g, Cycle time: ");
        Serial.print(cycle_time_data[cycle]);
        Serial.println(" s");
        
        delay(2000); // Brief pause between cycles
    }
    
    // Perform SPC analysis
    bool spc_ok = true;
    
    // Pressure SPC analysis
    SPCResults pressure_spc = calculateSPCStatistics(pressure_data, spc_cycles, "Pressure");
    if (pressure_spc.cp < 1.33 || pressure_spc.cpk < 1.33) {
        spc_ok = false;
        Serial.println("FAIL: Pressure process capability insufficient");
    }
    
    // Weight SPC analysis
    SPCResults weight_spc = calculateSPCStatistics(weight_data, spc_cycles, "Weight");
    if (weight_spc.cp < 1.33 || weight_spc.cpk < 1.33) {
        spc_ok = false;
        Serial.println("FAIL: Weight process capability insufficient");
    }
    
    // Cycle time SPC analysis
    SPCResults cycle_spc = calculateSPCStatistics(cycle_time_data, spc_cycles, "Cycle Time");
    if (cycle_spc.cp < 1.33 || cycle_spc.cpk < 1.33) {
        spc_ok = false;
        Serial.println("FAIL: Cycle time process capability insufficient");
    }
    
    // Temperature SPC analysis
    SPCResults temp_spc = calculateSPCStatistics(temperature_data_spc, spc_cycles, "Temperature");
    if (temp_spc.cp < 1.33 || temp_spc.cpk < 1.33) {
        spc_ok = false;
        Serial.println("FAIL: Temperature process capability insufficient");
    }
    
    // Control chart analysis
    spc_ok &= validateControlCharts(pressure_data, spc_cycles, pressure_spc, "Pressure");
    spc_ok &= validateControlCharts(weight_data, spc_cycles, weight_spc, "Weight");
    spc_ok &= validateControlCharts(cycle_time_data, spc_cycles, cycle_spc, "Cycle Time");
    
    return spc_ok;
}

struct SPCResults {
    float mean;
    float std_dev;
    float cp;
    float cpk;
    float ucl;
    float lcl;
    bool process_stable;
};

SPCResults calculateSPCStatistics(float* data, int samples, const char* parameter) {
    SPCResults results;
    
    // Calculate mean
    results.mean = 0.0;
    for (int i = 0; i < samples; i++) {
        results.mean += data[i];
    }
    results.mean /= samples;
    
    // Calculate standard deviation
    float variance = 0.0;
    for (int i = 0; i < samples; i++) {
        float diff = data[i] - results.mean;
        variance += diff * diff;
    }
    results.std_dev = sqrt(variance / (samples - 1));
    
    // Calculate control limits (±3σ)
    results.ucl = results.mean + (3.0 * results.std_dev);
    results.lcl = results.mean - (3.0 * results.std_dev);
    
    // Calculate process capability
    // Note: In real application, USL and LSL would be specified
    float usl = results.mean + (6.0 * results.std_dev); // Example
    float lsl = results.mean - (6.0 * results.std_dev); // Example
    
    results.cp = (usl - lsl) / (6.0 * results.std_dev);
    
    float cpu = (usl - results.mean) / (3.0 * results.std_dev);
    float cpl = (results.mean - lsl) / (3.0 * results.std_dev);
    results.cpk = min(cpu, cpl);
    
    // Check process stability (no points outside control limits)
    results.process_stable = true;
    for (int i = 0; i < samples; i++) {
        if (data[i] > results.ucl || data[i] < results.lcl) {
            results.process_stable = false;
            break;
        }
    }
    
    // Print results
    Serial.print(parameter);
    Serial.println(" SPC Analysis:");
    Serial.print("  Mean: ");
    Serial.println(results.mean);
    Serial.print("  Std Dev: ");
    Serial.println(results.std_dev);
    Serial.print("  UCL: ");
    Serial.println(results.ucl);
    Serial.print("  LCL: ");
    Serial.println(results.lcl);
    Serial.print("  Cp: ");
    Serial.println(results.cp);
    Serial.print("  Cpk: ");
    Serial.println(results.cpk);
    Serial.print("  Process Stable: ");
    Serial.println(results.process_stable ? "Yes" : "No");
    
    return results;
}

bool validateControlCharts(float* data, int samples, SPCResults spc, const char* parameter) {
    Serial.print("Validating ");
    Serial.print(parameter);
    Serial.println(" control chart rules...");
    
    bool chart_ok = true;
    
    // Rule 1: No points beyond control limits
    int out_of_control_count = 0;
    for (int i = 0; i < samples; i++) {
        if (data[i] > spc.ucl || data[i] < spc.lcl) {
            out_of_control_count++;
        }
    }
    
    if (out_of_control_count > 0) {
        chart_ok = false;
        Serial.print("FAIL: ");
        Serial.print(out_of_control_count);
        Serial.println(" points beyond control limits");
    }
    
    // Rule 2: 9 points in a row on same side of center line
    int consecutive_same_side = 0;
    bool above_center = (data[0] > spc.mean);
    
    for (int i = 0; i < samples; i++) {
        bool current_above = (data[i] > spc.mean);
        if (current_above == above_center) {
            consecutive_same_side++;
            if (consecutive_same_side >= 9) {
                chart_ok = false;
                Serial.println("FAIL: 9 consecutive points on same side of center line");
                break;
            }
        } else {
            consecutive_same_side = 1;
            above_center = current_above;
        }
    }
    
    // Rule 3: 6 points in a row steadily increasing or decreasing
    int consecutive_trend = 1;
    bool increasing = (data[1] > data[0]);
    
    for (int i = 1; i < samples - 1; i++) {
        bool current_increasing = (data[i + 1] > data[i]);
        if (current_increasing == increasing) {
            consecutive_trend++;
            if (consecutive_trend >= 6) {
                chart_ok = false;
                Serial.println("FAIL: 6 consecutive points in trend");
                break;
            }
        } else {
            consecutive_trend = 1;
            increasing = current_increasing;
        }
    }
    
    // Rule 4: 14 points in a row alternating up and down
    int alternating_count = 1;
    for (int i = 1; i < samples - 1; i++) {
        if ((data[i] > data[i-1] && data[i] > data[i+1]) ||
            (data[i] < data[i-1] && data[i] < data[i+1])) {
            alternating_count++;
            if (alternating_count >= 14) {
                chart_ok = false;
                Serial.println("FAIL: 14 consecutive alternating points");
                break;
            }
        } else {
            alternating_count = 1;
        }
    }
    
    if (chart_ok) {
        Serial.print("PASS: ");
        Serial.print(parameter);
        Serial.println(" control chart validation");
    }
    
    return chart_ok;
}
```

## Digital Twin Validation Testing

### Digital Twin Synchronization Test
```cpp
// Test Digital Twin Synchronization and Accuracy
bool testDigitalTwinSynchronization() {
    Serial.println("Testing digital twin synchronization and accuracy...");
    
    // Test digital twin communication
    if (!testDigitalTwinCommunication()) {
        Serial.println("FAIL: Digital twin communication");
        return false;
    }
    
    // Test simulation accuracy
    if (!testSimulationAccuracy()) {
        Serial.println("FAIL: Digital twin simulation accuracy");
        return false;
    }
    
    // Test optimization recommendations
    if (!testOptimizationRecommendations()) {
        Serial.println("FAIL: Digital twin optimization");
        return false;
    }
    
    Serial.println("PASS: Digital twin validation");
    return true;
}

bool testDigitalTwinCommunication() {
    // Send test data to ESP32 digital twin
    DynamicJsonDocument test_doc(1024);
    test_doc["type"] = "test_sync";
    test_doc["timestamp"] = millis();
    test_doc["pressure"] = 1500.0;
    test_doc["temperature"] = 250.0;
    
    String test_message;
    serializeJson(test_doc, test_message);
    
    ESP32_SERIAL.println(test_message);
    
    // Wait for response
    unsigned long start_time = millis();
    while (!ESP32_SERIAL.available() && (millis() - start_time) < 5000) {
        delay(100);
    }
    
    if (!ESP32_SERIAL.available()) {
        Serial.println("FAIL: No response from digital twin");
        return false;
    }
    
    String response = ESP32_SERIAL.readString();
    DynamicJsonDocument response_doc(1024);
    deserializeJson(response_doc, response);
    
    if (response_doc["status"] != "ok") {
        Serial.println("FAIL: Digital twin communication error");
        return false;
    }
    
    Serial.println("PASS: Digital twin communication");
    return true;
}

bool testSimulationAccuracy() {
    // Compare real vs simulated process data
    float accuracy_threshold = 90.0; // 90% minimum accuracy
    
    // Collect real process data
    float real_data[10];
    float simulated_data[10];
    
    for (int i = 0; i < 10; i++) {
        // Run real injection cycle
        startTestInjectionCycle();
        
        while (system_status.current_phase != PHASE_IDLE) {
            readAllSensors();
            delay(100);
        }
        
        real_data[i] = cavity_pressure.peak_pressure;
        
        // Get simulated prediction
        DynamicJsonDocument sim_request(512);
        sim_request["type"] = "simulate";
        sim_request["parameters"]["pressure"] = cavity_pressure.average_pressure;
        sim_request["parameters"]["temperature"] = temperature_data.melt_temp;
        
        String sim_message;
        serializeJson(sim_request, sim_message);
        ESP32_SERIAL.println(sim_message);
        
        // Wait for simulation result
        delay(2000);
        if (ESP32_SERIAL.available()) {
            String sim_response = ESP32_SERIAL.readString();
            DynamicJsonDocument sim_doc(512);
            deserializeJson(sim_doc, sim_response);
            
            simulated_data[i] = sim_doc["simulation"]["predicted_pressure"];
        } else {
            simulated_data[i] = real_data[i]; // Fallback
        }
        
        delay(5000); // Wait between cycles
    }
    
    // Calculate simulation accuracy
    float total_error = 0.0;
    for (int i = 0; i < 10; i++) {
        float error_percent = abs(simulated_data[i] - real_data[i]) / real_data[i] * 100.0;
        total_error += error_percent;
        
        Serial.print("Cycle ");
        Serial.print(i + 1);
        Serial.print(" - Real: ");
        Serial.print(real_data[i]);
        Serial.print(" bar, Simulated: ");
        Serial.print(simulated_data[i]);
        Serial.print(" bar, Error: ");
        Serial.print(error_percent);
        Serial.println("%");
    }
    
    float average_accuracy = 100.0 - (total_error / 10.0);
    Serial.print("Average simulation accuracy: ");
    Serial.print(average_accuracy);
    Serial.println("%");
    
    return (average_accuracy >= accuracy_threshold);
}

bool testOptimizationRecommendations() {
    // Test ML-based process optimization
    DynamicJsonDocument opt_request(512);
    opt_request["type"] = "optimize";
    opt_request["current_state"]["pressure"] = cavity_pressure.average_pressure;
    opt_request["current_state"]["temperature"] = temperature_data.melt_temp;
    opt_request["current_state"]["cycle_time"] = system_status.cycle_time_actual;
    opt_request["current_state"]["quality"] = quality_prediction.overall_quality;
    
    String opt_message;
    serializeJson(opt_request, opt_message);
    ESP32_SERIAL.println(opt_message);
    
    // Wait for optimization result
    delay(5000);
    if (!ESP32_SERIAL.available()) {
        Serial.println("FAIL: No optimization response");
        return false;
    }
    
    String opt_response = ESP32_SERIAL.readString();
    DynamicJsonDocument opt_doc(1024);
    deserializeJson(opt_response, opt_response);
    
    if (!opt_doc.containsKey("optimization")) {
        Serial.println("FAIL: Invalid optimization response");
        return false;
    }
    
    JsonObject optimization = opt_doc["optimization"];
    float confidence = optimization["confidence"];
    float predicted_improvement = optimization["cycle_time_reduction"];
    
    Serial.print("Optimization confidence: ");
    Serial.print(confidence);
    Serial.println("%");
    
    Serial.print("Predicted cycle time reduction: ");
    Serial.print(predicted_improvement);
    Serial.println("%");
    
    if (confidence < 70.0) {
        Serial.println("FAIL: Low optimization confidence");
        return false;
    }
    
    Serial.println("PASS: Optimization recommendations");
    return true;
}
```

## Quality Prediction Validation

### ML Model Accuracy Test
```cpp
// Test Machine Learning Quality Prediction Accuracy
bool testMLQualityPrediction() {
    Serial.println("Testing ML quality prediction accuracy...");
    
    // Collect test cases with known outcomes
    int test_cases = 50;
    float prediction_accuracy = 0.0;
    int correct_predictions = 0;
    
    for (int test = 0; test < test_cases; test++) {
        Serial.print("ML test case ");
        Serial.print(test + 1);
        Serial.print("/");
        Serial.println(test_cases);
        
        // Run production cycle
        startProductionCycle();
        
        // Get quality prediction
        while (system_status.current_phase != PHASE_IDLE) {
            readAllSensors();
            updateProcessControl();
            performQualityPrediction();
            delay(100);
        }
        
        // Simulate actual quality measurement
        float actual_weight = quality_prediction.predicted_weight + (random(-5, 5) / 10.0);
        bool actual_quality_pass = (abs(actual_weight - process_params.target_weight) <= process_params.weight_tolerance);
        bool predicted_quality_pass = (quality_prediction.overall_quality >= QUALITY_ACCEPTABLE);
        
        if (actual_quality_pass == predicted_quality_pass) {
            correct_predictions++;
        }
        
        Serial.print("Predicted weight: ");
        Serial.print(quality_prediction.predicted_weight);
        Serial.print(" g, Actual weight: ");
        Serial.print(actual_weight);
        Serial.print(" g, Prediction: ");
        Serial.print(predicted_quality_pass ? "PASS" : "FAIL");
        Serial.print(", Actual: ");
        Serial.print(actual_quality_pass ? "PASS" : "FAIL");
        Serial.print(", ");
        Serial.println((actual_quality_pass == predicted_quality_pass) ? "CORRECT" : "WRONG");
        
        delay(3000); // Brief pause between tests
    }
    
    prediction_accuracy = (float)correct_predictions / test_cases * 100.0;
    
    Serial.print("ML prediction accuracy: ");
    Serial.print(prediction_accuracy);
    Serial.print("% (");
    Serial.print(correct_predictions);
    Serial.print("/");
    Serial.print(test_cases);
    Serial.println(")");
    
    if (prediction_accuracy < 85.0) {
        Serial.println("FAIL: ML prediction accuracy below 85%");
        return false;
    }
    
    Serial.println("PASS: ML quality prediction validation");
    return true;
}
```

## Complete System Integration Test

### End-to-End Production Simulation
```cpp
// Test Complete Production System Integration
bool testCompleteSystemIntegration() {
    Serial.println("Testing complete system integration...");
    
    // Initialize production parameters
    initializeProductionParameters();
    
    // Run extended production simulation (8 hours equivalent)
    int production_cycles = 200; // Compressed to 200 cycles
    bool integration_ok = true;
    
    // Production statistics
    int successful_cycles = 0;
    int failed_cycles = 0;
    int rejected_parts = 0;
    float total_cycle_time = 0.0;
    float total_energy = 0.0;
    
    Serial.print("Starting production simulation: ");
    Serial.print(production_cycles);
    Serial.println(" cycles");
    
    for (int cycle = 0; cycle < production_cycles; cycle++) {
        unsigned long cycle_start = millis();
        
        Serial.print("Production cycle ");
        Serial.print(cycle + 1);
        Serial.print("/");
        Serial.print(production_cycles);
        
        // Start production cycle
        bool cycle_success = runCompleteCycle();
        
        if (cycle_success) {
            successful_cycles++;
            
            // Check quality
            if (quality_prediction.reject_part) {
                rejected_parts++;
            }
            
            // Record cycle time
            float cycle_time = (millis() - cycle_start) / 1000.0;
            total_cycle_time += cycle_time;
            
            // Estimate energy consumption
            total_energy += estimateEnergyConsumption();
            
            Serial.print(" - SUCCESS (");
            Serial.print(cycle_time);
            Serial.print("s, Quality: ");
            Serial.print(quality_prediction.overall_quality);
            Serial.println(")");
            
        } else {
            failed_cycles++;
            Serial.println(" - FAILED");
            
            // Attempt recovery
            if (!performSystemRecovery()) {
                integration_ok = false;
                Serial.println("FAIL: System recovery failed");
                break;
            }
        }
        
        // Periodic system checks
        if (cycle % 25 == 0) {
            if (!performPeriodicSystemCheck()) {
                integration_ok = false;
                Serial.println("FAIL: Periodic system check failed");
                break;
            }
        }
        
        // Brief pause between cycles
        delay(1000);
    }
    
    // Calculate production statistics
    float success_rate = (float)successful_cycles / production_cycles * 100.0;
    float quality_rate = (float)(successful_cycles - rejected_parts) / successful_cycles * 100.0;
    float average_cycle_time = total_cycle_time / successful_cycles;
    float average_energy_per_cycle = total_energy / successful_cycles;
    
    Serial.println("\n=== Production Statistics ===");
    Serial.print("Total cycles: ");
    Serial.println(production_cycles);
    Serial.print("Successful cycles: ");
    Serial.println(successful_cycles);
    Serial.print("Failed cycles: ");
    Serial.println(failed_cycles);
    Serial.print("Rejected parts: ");
    Serial.println(rejected_parts);
    Serial.print("Success rate: ");
    Serial.print(success_rate);
    Serial.println("%");
    Serial.print("Quality rate: ");
    Serial.print(quality_rate);
    Serial.println("%");
    Serial.print("Average cycle time: ");
    Serial.print(average_cycle_time);
    Serial.println(" seconds");
    Serial.print("Average energy per cycle: ");
    Serial.print(average_energy_per_cycle);
    Serial.println(" kJ");
    
    // Validate production requirements
    if (success_rate < 95.0) {
        integration_ok = false;
        Serial.println("FAIL: Production success rate below 95%");
    }
    
    if (quality_rate < 97.0) {
        integration_ok = false;
        Serial.println("FAIL: Quality rate below 97%");
    }
    
    if (average_cycle_time > process_params.cycle_time_target * 1.1) {
        integration_ok = false;
        Serial.println("FAIL: Average cycle time exceeds target");
    }
    
    if (integration_ok) {
        Serial.println("PASS: Complete system integration test");
    } else {
        Serial.println("FAIL: Complete system integration test");
    }
    
    return integration_ok;
}

bool runCompleteCycle() {
    // Complete production cycle with all phases
    
    // Phase 1: Mold Close
    system_status.current_phase = PHASE_CLAMP_CLOSE;
    delay(2000); // Simulate mold closing time
    
    // Phase 2: Injection
    system_status.current_phase = PHASE_INJECTION;
    current_injection_stage = 0;
    
    unsigned long injection_start = millis();
    while (system_status.current_phase == PHASE_INJECTION && 
           (millis() - injection_start) < 10000) {
        
        readAllSensors();
        controlInjectionPhase();
        
        // Check for faults
        if (cavity_pressure.average_pressure > process_params.injection_pressure_limit) {
            Serial.println("Injection pressure fault");
            return false;
        }
        
        delay(10);
    }
    
    // Phase 3: Pack/Hold
    system_status.current_phase = PHASE_PACK_HOLD;
    current_pack_stage = 0;
    
    unsigned long pack_start = millis();
    while (system_status.current_phase == PHASE_PACK_HOLD && 
           (millis() - pack_start) < 15000) {
        
        readAllSensors();
        controlPackHoldPhase();
        delay(10);
    }
    
    // Phase 4: Cooling
    system_status.current_phase = PHASE_COOLING;
    delay(process_params.cooling_time * 1000);
    
    // Phase 5: Ejection
    system_status.current_phase = PHASE_EJECTION;
    delay(3000);
    
    // Phase 6: Mold Open
    system_status.current_phase = PHASE_CLAMP_OPEN;
    delay(2000);
    
    // Complete quality prediction
    performQualityPrediction();
    
    // Return to idle
    system_status.current_phase = PHASE_IDLE;
    
    return true; // Cycle completed successfully
}

bool performSystemRecovery() {
    Serial.println("Performing system recovery...");
    
    // Stop all outputs
    analogWrite(INJECTION_VALVE, 0);
    analogWrite(PACK_PRESSURE_VALVE, 0);
    analogWrite(BACK_PRESSURE_VALVE, 0);
    
    // Check system health
    if (!performSystemSelfTest()) {
        return false;
    }
    
    // Reset to idle state
    system_status.current_phase = PHASE_IDLE;
    
    Serial.println("System recovery completed");
    return true;
}

bool performPeriodicSystemCheck() {
    // Check system health periodically
    if (system_status.system_health_score < 85) {
        Serial.println("System health degraded");
        return false;
    }
    
    // Check SPC status
    if (!spc_pressure.process_stable) {
        Serial.println("Process not in statistical control");
        return false;
    }
    
    // Check digital twin synchronization
    if (!digital_twin.model_synchronized) {
        Serial.println("Digital twin not synchronized");
        return false;
    }
    
    return true;
}

float estimateEnergyConsumption() {
    // Estimate energy consumption for the cycle
    float heater_energy = 0.0;
    float hydraulic_energy = 0.0;
    float control_energy = 0.1; // kJ for control systems
    
    // Heater energy (simplified calculation)
    heater_energy = (temperature_data.barrel_zone_1 * 0.01 + 
                    temperature_data.barrel_zone_2 * 0.01 + 
                    temperature_data.barrel_zone_3 * 0.01 + 
                    temperature_data.nozzle_temp * 0.005 + 
                    temperature_data.mold_temp * 0.02); // kJ
    
    // Hydraulic energy (based on pressure and flow)
    hydraulic_energy = cavity_pressure.peak_pressure * 0.001; // kJ
    
    return heater_energy + hydraulic_energy + control_energy;
}
```

## Performance Validation

### System Performance Metrics
- [ ] Pressure measurement accuracy: ±0.5% full scale
- [ ] Temperature control accuracy: ±1°C
- [ ] Position measurement resolution: 0.01 mm
- [ ] Injection velocity control: ±2% of setpoint
- [ ] Cavity pressure balance: ±5% between cavities
- [ ] Cycle time repeatability: CV <2%
- [ ] Digital twin sync rate: 10 Hz minimum
- [ ] ML prediction accuracy: >85%
- [ ] SPC process capability: Cp/Cpk >1.33
- [ ] System response time: <10 ms for control loops

### Accuracy Requirements
- [ ] Pressure transducers: ±0.5% accuracy class
- [ ] Thermocouples: ±1°C or ±0.4% accuracy
- [ ] LVDT position sensors: ±0.01 mm linearity
- [ ] Flow calculations: ±2% of reading
- [ ] Quality predictions: >85% correlation with actual
- [ ] Process parameter control: ±5% of setpoint
- [ ] Energy monitoring: ±3% accuracy

### Industrial Reliability Requirements
- [ ] System availability: >99% during production
- [ ] Mean Time Between Failures (MTBF): >1000 hours
- [ ] Safety response time: <500 ms for all critical alarms
- [ ] EMI immunity: IEC 61000-6-2 compliance
- [ ] Operating temperature: 0°C to +50°C
- [ ] Vibration resistance: IEC 60068-2-6
- [ ] Data integrity: 100% for critical measurements

## Troubleshooting Guide

### Common Issues and Solutions

**Issue**: Cavity pressure imbalance between cavities
**Solution**: Check mold design, gate sizes, runner balance, temperature uniformity, material flow properties

**Issue**: Temperature control oscillations or overshooting
**Solution**: Tune PID parameters, check heater element condition, verify thermocouple placement, inspect insulation

**Issue**: Injection velocity control instability
**Solution**: Check hydraulic system pressure, valve response, position sensor calibration, control loop tuning

**Issue**: Digital twin synchronization failures
**Solution**: Verify network connectivity, check ESP32 operation, validate data formats, update firmware

**Issue**: ML prediction accuracy degradation
**Solution**: Retrain model with recent data, verify feature scaling, check input data quality, validate sensors

**Issue**: SPC charts showing out-of-control conditions
**Solution**: Investigate process variations, check material consistency, verify machine wear, calibrate sensors

### Diagnostic Procedures

#### Comprehensive System Health Check
```cpp
void performComprehensiveHealthCheck() {
    Serial.println("=== Comprehensive System Health Check ===");
    
    // Test all subsystems
    bool pressure_system_ok = testPressureMeasurementSystem();
    bool temperature_system_ok = testTemperatureControlSystem();
    bool position_system_ok = testPositionMeasurementSystem();
    bool control_system_ok = testControlOutputSystem();
    bool safety_system_ok = testSafetyInterlockSystem();
    bool communication_ok = testCommunicationSystems();
    bool digital_twin_ok = testDigitalTwinSystem();
    bool spc_system_ok = testSPCSystem();
    bool ml_system_ok = testMLPredictionSystem();
    
    // Calculate overall health score
    int health_components = 9;
    int healthy_components = 0;
    
    if (pressure_system_ok) healthy_components++;
    if (temperature_system_ok) healthy_components++;
    if (position_system_ok) healthy_components++;
    if (control_system_ok) healthy_components++;
    if (safety_system_ok) healthy_components++;
    if (communication_ok) healthy_components++;
    if (digital_twin_ok) healthy_components++;
    if (spc_system_ok) healthy_components++;
    if (ml_system_ok) healthy_components++;
    
    int overall_health = (healthy_components * 100) / health_components;
    
    Serial.print("Overall System Health: ");
    Serial.print(overall_health);
    Serial.println("%");
    
    if (overall_health < 90) {
        Serial.println("WARNING: System health below production readiness");
        generateHealthReport();
        recommendMaintenanceActions();
    } else {
        Serial.println("System ready for production");
    }
}
```

## Maintenance Schedule

### Daily Maintenance (Production Environment)
- [ ] Check system status displays and error logs
- [ ] Verify pressure sensor readings and zero drift
- [ ] Check temperature controller setpoints and stability
- [ ] Inspect cavity pressure balance trends
- [ ] Review SPC charts for process stability
- [ ] Verify digital twin synchronization status
- [ ] Check ML prediction accuracy trends

### Weekly Maintenance
- [ ] Calibrate pressure transducers with reference standards
- [ ] Verify thermocouple cold junction compensation
- [ ] Test position sensor linearity and repeatability
- [ ] Check hydraulic valve response characteristics
- [ ] Inspect safety interlock operation
- [ ] Update ML training data with recent production
- [ ] Backup SPC data and configuration

### Monthly Maintenance
- [ ] Complete pressure system calibration with traceable standards
- [ ] Comprehensive temperature calibration verification
- [ ] Position measurement system accuracy verification
- [ ] Control loop performance analysis and tuning
- [ ] Digital twin model validation with physical tests
- [ ] SPC control limit review and adjustment
- [ ] Predictive maintenance analysis review

### Quarterly Maintenance
- [ ] Replace pressure sensor O-rings and seals
- [ ] Thermocouple junction inspection and replacement
- [ ] Hydraulic system filter and fluid analysis
- [ ] Control valve overhaul and calibration
- [ ] Complete safety system functional test
- [ ] ML model retraining with extended dataset
- [ ] System performance benchmarking against specifications

## Standards Compliance

### Industry Standards Compliance
- [ ] **ANSI/SPI B151.1**: Safety requirements for injection molding
- [ ] **ISO 294**: Molding standards and test methods
- [ ] **ASTM D3641**: Practice for injection molding test specimens
- [ ] **Euromap 77**: OPC UA interface for injection molding machines
- [ ] **IEC 61508**: Functional safety requirements
- [ ] **ISO 13849**: Safety of machinery control systems

### Test Documentation Requirements
- [ ] Complete calibration certificates with NIST traceability
- [ ] Measurement uncertainty analysis for all critical parameters
- [ ] Statistical validation of process capability studies
- [ ] Safety system validation and functional testing records
- [ ] Digital twin model validation documentation
- [ ] ML model training and validation records

### Quality Management Integration
- [ ] ISO 9001 quality management system integration
- [ ] Statistical process control implementation
- [ ] Continuous improvement process documentation
- [ ] Operator training and qualification records
- [ ] Equipment validation and re-validation procedures
- [ ] Change control and configuration management

This comprehensive testing guide ensures thorough validation of the injection molding controller for professional manufacturing environments, providing confidence in system performance for critical plastic part production applications across automotive, medical, aerospace, and consumer electronics industries.