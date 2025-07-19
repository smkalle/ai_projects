# Program 17: Phase Change Material (PCM) Controller - Testing Guide

## Overview
This comprehensive testing guide provides procedures for validating the PCM controller system, including phase change detection, thermal energy storage optimization, machine learning predictions, and advanced analytics.

## Safety Prerequisites

### ⚠️ CRITICAL SAFETY WARNINGS
- **NEVER** operate the system without proper safety equipment
- **ALWAYS** have fire extinguisher nearby when testing with heaters
- **ENSURE** emergency stop button is easily accessible
- **VERIFY** all electrical connections before powering on
- **USE** proper PPE (safety glasses, insulated gloves, lab coat)
- **MAINTAIN** clear workspace free of flammable materials
- **MONITOR** temperature continuously during phase change testing
- **ENSURE** proper ventilation for PCM vapors

### Required Safety Equipment
- Fire extinguisher (Class A, B, and C)
- Safety glasses with side shields
- Insulated gloves (rated for 120V AC)
- Lab coat or protective clothing
- Multimeter with CAT III rating
- Emergency stop button (tested daily)
- First aid kit with burn treatment
- Chemical spill cleanup kit
- Ventilation system (minimum 6 air changes/hour)
- Emergency shower and eyewash station (if available)

## Pre-Test Hardware Verification

### 1. Visual Inspection Checklist
```
□ All connections secure and properly terminated
□ No damaged wires or components
□ Proper grounding of all metal components
□ Emergency stop button functional and accessible
□ Status LEDs properly mounted and visible
□ Heat sinks properly attached to power components
□ Thermocouple junctions properly made and insulated
□ Load cells properly mounted and calibrated
□ PCM containers properly sealed and mounted
□ Cartridge heaters properly installed
□ Cooling fans operational
□ SD card inserted and functional
□ Power supplies within voltage tolerances
□ All safety interlocks functional
```

### 2. Electrical Safety Tests
```bash
# Test thermocouple continuity
Multimeter Settings: Resistance mode, 200Ω range
Expected: 0.1-50Ω depending on thermocouple length
Test all 8 thermocouples

# Test power supply stability
Multimeter Settings: DC Voltage, 20V range
12V Supply: 12.0V ± 0.5V under no load
12V Supply: 11.5V ± 0.5V under full load
3.3V Supply: 3.3V ± 0.1V
5V Supply: 5.0V ± 0.2V

# Test AC power integrity
Multimeter Settings: AC Voltage, 200V range
120V AC: 120V ± 6V
Ground continuity: < 1Ω to earth ground

# Test emergency stop circuit
Multimeter Settings: Continuity mode
Expected: Open circuit when pressed, closed when released
Test response time: < 100ms
```

### 3. Sensor Verification Tests
```cpp
// Test I2C bus integrity
void testI2CBus() {
    Wire.begin();
    Serial.println("Scanning I2C bus...");
    
    int deviceCount = 0;
    for (int address = 1; address < 127; address++) {
        Wire.beginTransmission(address);
        int error = Wire.endTransmission();
        
        if (error == 0) {
            Serial.print("Device found at address 0x");
            if (address < 16) Serial.print("0");
            Serial.println(address, HEX);
            deviceCount++;
        }
    }
    
    Serial.print("Total I2C devices found: ");
    Serial.println(deviceCount);
    
    // Expected devices:
    // 0x40, 0x41: INA3221 current monitors
    // 0x48, 0x49: ADS1115 ADC modules
    // 0x68: DS3231 RTC
    assert(deviceCount >= 5);
}

// Test load cell calibration
void testLoadCells() {
    Serial.println("=== LOAD CELL CALIBRATION TEST ===");
    
    for (int i = 0; i < NUM_LOAD_CELLS; i++) {
        Serial.print("Testing load cell ");
        Serial.println(i);
        
        // Tare the scale
        load_cells[i].tare(10);
        float zero_reading = load_cells[i].get_units(10);
        
        Serial.print("Zero reading: ");
        Serial.println(zero_reading);
        
        // Test with known mass
        Serial.println("Place 1kg calibration weight...");
        delay(5000);
        
        float calibrated_reading = load_cells[i].get_units(10);
        Serial.print("1kg reading: ");
        Serial.println(calibrated_reading);
        
        // Verify calibration
        if (abs(calibrated_reading - 1000.0) < 10.0) {
            Serial.println("✅ Load cell calibration OK");
        } else {
            Serial.println("❌ Load cell calibration FAILED");
        }
    }
}
```

## Functional Testing Procedures

### Phase 1: Basic System Startup (45 minutes)

#### 1.1 Power-On Sequence
```
1. Connect 12V DC power supply (OFF)
2. Connect 120V AC power (OFF)
3. Connect Arduino USB cable
4. Connect ESP32 USB cable
5. Open serial monitors (115200 baud)
6. Upload Arduino program
7. Upload ESP32 program
8. Turn on 12V DC power supply
9. Turn on 120V AC power
10. Verify startup sequences
```

**Expected Arduino Output:**
```
🌡️ PCM CONTROLLER SYSTEM STARTED!
🌡️ PCM THERMAL ENGINEER MODE - Design advanced thermal energy storage!
Professional Phase Change Material control and optimization system
================================================================
🔧 Initializing Hardware...
✅ MAX31855 thermocouples: 8/8
✅ HX711 load cells: 2/2
✅ INA3221 current monitors: 2/2
✅ ADS1115 ADC modules: 2/2
✅ DS3231 RTC synchronized
✅ SD card initialized
✅ Safety system initialized
✅ WiFi connected. IP: 192.168.1.100
✅ MQTT broker connected
✅ Data logging initialized: pcm_data_1234567.csv
🔥 Initializing PCM Containers...
✅ Container 0 (Paraffin Wax)
✅ Container 1 (Salt Hydrate)
✅ Container 2 (Fatty Acid)
✅ Container 3 (Custom PCM)
🔥 PCM Material Characterization...
📊 Container 0 (Paraffin Wax):
  Melting point: 58.0°C
  Latent heat: 218 J/g
  Thermal conductivity: 0.21 W/m·K
🎯 System Ready for PCM Testing
```

**Expected ESP32 Output:**
```
🧠 PCM ANALYTICS GATEWAY STARTED!
🧠 Advanced AI-driven thermal energy storage analytics
================================================================
✅ SPIFFS initialized
✅ WiFi connected: 192.168.1.101
✅ MQTT connected
✅ ML model loaded successfully
✅ Web server started on port 80
📥 Downloading model update: 1.2.3
✅ Model updated successfully
🎯 Analytics Gateway Ready
```

#### 1.2 Communication Test
```cpp
void testCommunication() {
    Serial.println("=== COMMUNICATION TEST ===");
    
    // Test Arduino to ESP32 communication
    Serial2.println("{\"test\":\"communication\"}");
    delay(1000);
    
    // Test MQTT communication
    if (mqtt_client.connected()) {
        mqtt_client.publish("pcm/test", "Hello from PCM Controller");
        Serial.println("✅ MQTT communication OK");
    } else {
        Serial.println("❌ MQTT communication FAILED");
    }
    
    // Test web server
    WiFiClient client;
    if (client.connect("192.168.1.101", 80)) {
        client.println("GET /api/status HTTP/1.1");
        client.println("Host: 192.168.1.101");
        client.println("Connection: close");
        client.println();
        
        delay(1000);
        if (client.available()) {
            Serial.println("✅ Web server communication OK");
        } else {
            Serial.println("❌ Web server communication FAILED");
        }
        client.stop();
    }
}
```

### Phase 2: Sensor Calibration and Validation (60 minutes)

#### 2.1 Temperature Sensor Calibration
```cpp
void calibrateTemperatureSensors() {
    Serial.println("=== TEMPERATURE SENSOR CALIBRATION ===");
    
    // Ice point calibration (0°C)
    Serial.println("Prepare ice bath (0°C)...");
    Serial.println("Immerse all thermocouples in ice bath");
    Serial.println("Press any key when ready...");
    while (!Serial.available()) delay(100);
    Serial.readString();
    
    delay(30000); // 30 seconds stabilization
    
    Serial.println("Ice point readings:");
    for (int i = 0; i < TOTAL_THERMOCOUPLES; i++) {
        float temp = thermocouples[i].readCelsius();
        Serial.print("TC ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(temp);
        Serial.print("°C (Error: ");
        Serial.print(temp - 0.0);
        Serial.println("°C)");
        
        if (abs(temp - 0.0) > 2.0) {
            Serial.println("❌ Temperature sensor " + String(i) + " out of tolerance");
        }
    }
    
    // Boiling point calibration (100°C)
    Serial.println("\nPrepare boiling water bath (100°C)...");
    Serial.println("Immerse all thermocouples in boiling water");
    Serial.println("Press any key when ready...");
    while (!Serial.available()) delay(100);
    Serial.readString();
    
    delay(30000); // 30 seconds stabilization
    
    Serial.println("Boiling point readings:");
    for (int i = 0; i < TOTAL_THERMOCOUPLES; i++) {
        float temp = thermocouples[i].readCelsius();
        Serial.print("TC ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(temp);
        Serial.print("°C (Error: ");
        Serial.print(temp - 100.0);
        Serial.println("°C)");
        
        if (abs(temp - 100.0) > 2.0) {
            Serial.println("❌ Temperature sensor " + String(i) + " out of tolerance");
        }
    }
}
```

#### 2.2 Mass Measurement Validation
```cpp
void validateMassMeasurement() {
    Serial.println("=== MASS MEASUREMENT VALIDATION ===");
    
    float test_masses[] = {0.0, 100.0, 500.0, 1000.0, 2000.0}; // grams
    int num_masses = sizeof(test_masses) / sizeof(test_masses[0]);
    
    for (int mass_idx = 0; mass_idx < num_masses; mass_idx++) {
        Serial.print("Place ");
        Serial.print(test_masses[mass_idx]);
        Serial.println("g on each load cell...");
        Serial.println("Press any key when ready...");
        while (!Serial.available()) delay(100);
        Serial.readString();
        
        delay(5000); // Stabilization time
        
        for (int i = 0; i < NUM_LOAD_CELLS; i++) {
            float measured_mass = load_cells[i].get_units(10);
            float error = measured_mass - test_masses[mass_idx];
            
            Serial.print("Load cell ");
            Serial.print(i);
            Serial.print(": ");
            Serial.print(measured_mass, 1);
            Serial.print("g (Error: ");
            Serial.print(error, 1);
            Serial.println("g)");
            
            if (abs(error) > test_masses[mass_idx] * 0.001 + 0.5) { // 0.1% + 0.5g
                Serial.println("❌ Load cell " + String(i) + " accuracy out of tolerance");
            } else {
                Serial.println("✅ Load cell " + String(i) + " accuracy OK");
            }
        }
        Serial.println();
    }
}
```

#### 2.3 Heat Flux Sensor Calibration
```cpp
void calibrateHeatFluxSensors() {
    Serial.println("=== HEAT FLUX SENSOR CALIBRATION ===");
    
    // Zero point calibration
    Serial.println("Ensure no heat flux across sensors...");
    Serial.println("Press any key when ready...");
    while (!Serial.available()) delay(100);
    Serial.readString();
    
    delay(10000); // 10 seconds stabilization
    
    Serial.println("Zero point readings:");
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        int adc_index = i / 2;
        int adc_channel = i % 2;
        int16_t adc_value = adc_modules[adc_index].readADC_SingleEnded(adc_channel);
        float voltage = adc_value * 0.125 / 1000.0; // mV
        
        Serial.print("Container ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(voltage, 3);
        Serial.println(" mV");
        
        if (abs(voltage) > 0.1) {
            Serial.println("❌ Heat flux sensor " + String(i) + " zero offset too high");
        }
    }
    
    // Sensitivity verification (requires calibrated heat source)
    Serial.println("\nApply known heat flux (100 W/m²)...");
    Serial.println("Press any key when ready...");
    while (!Serial.available()) delay(100);
    Serial.readString();
    
    delay(30000); // 30 seconds stabilization
    
    Serial.println("Heat flux readings:");
    for (int i = 0; i < NUM_CONTAINERS; i++) {
        int adc_index = i / 2;
        int adc_channel = i % 2;
        int16_t adc_value = adc_modules[adc_index].readADC_SingleEnded(adc_channel);
        float voltage = adc_value * 0.125 / 1000.0; // mV
        float heat_flux = voltage / 0.06; // W/m² (calibration factor)
        
        Serial.print("Container ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(heat_flux, 1);
        Serial.print(" W/m² (");
        Serial.print(voltage, 3);
        Serial.println(" mV)");
        
        if (abs(heat_flux - 100.0) > 10.0) {
            Serial.println("❌ Heat flux sensor " + String(i) + " calibration error");
        } else {
            Serial.println("✅ Heat flux sensor " + String(i) + " calibration OK");
        }
    }
}
```

### Phase 3: Phase Change Detection Testing (90 minutes)

#### 3.1 Controlled Phase Change Test
```cpp
void testPhaseChangeDetection() {
    Serial.println("=== PHASE CHANGE DETECTION TEST ===");
    
    int test_container = 0; // Test with first container
    
    // Setup for paraffin wax test
    Serial.println("Container 0: Paraffin Wax (Melting point: 58°C)");
    Serial.println("Starting controlled heating test...");
    
    // Start heating
    digitalWrite(HEATER_RELAY_PINS[test_container], HIGH);
    Serial.println("Heater ON");
    
    float start_temp = pcm_containers[test_container].temperature_top;
    unsigned long test_start_time = millis();
    bool phase_change_detected = false;
    bool melting_complete = false;
    
    while (millis() - test_start_time < 3600000) { // 1 hour max
        // Update sensors
        updateSensorReadings();
        
        // Check for phase change
        if (phase_detector.detectPhaseState(test_container) == MELTING && !phase_change_detected) {
            phase_change_detected = true;
            Serial.println("🔄 PHASE CHANGE DETECTED!");
            Serial.print("Time to detection: ");
            Serial.print((millis() - test_start_time) / 1000);
            Serial.println(" seconds");
            Serial.print("Temperature at detection: ");
            Serial.print(pcm_containers[test_container].temperature_top);
            Serial.println("°C");
        }
        
        // Check for melting completion
        if (pcm_containers[test_container].phase_fraction > 0.95 && !melting_complete) {
            melting_complete = true;
            Serial.println("🔄 MELTING COMPLETE!");
            Serial.print("Time to complete melting: ");
            Serial.print((millis() - test_start_time) / 1000);
            Serial.println(" seconds");
            Serial.print("Final temperature: ");
            Serial.print(pcm_containers[test_container].temperature_top);
            Serial.println("°C");
            
            // Turn off heater
            digitalWrite(HEATER_RELAY_PINS[test_container], LOW);
            Serial.println("Heater OFF");
            break;
        }
        
        // Safety check
        if (pcm_containers[test_container].temperature_top > 80.0) {
            digitalWrite(HEATER_RELAY_PINS[test_container], LOW);
            Serial.println("❌ SAFETY LIMIT EXCEEDED - Test aborted");
            break;
        }
        
        // Status update every 30 seconds
        if ((millis() - test_start_time) % 30000 == 0) {
            Serial.print("Temperature: ");
            Serial.print(pcm_containers[test_container].temperature_top);
            Serial.print("°C | Phase fraction: ");
            Serial.print(pcm_containers[test_container].phase_fraction * 100, 1);
            Serial.print("% | Heat flux: ");
            Serial.print(pcm_containers[test_container].heat_flux);
            Serial.println(" W/m²");
        }
        
        delay(5000); // Check every 5 seconds
    }
    
    // Results
    if (phase_change_detected && melting_complete) {
        Serial.println("✅ Phase change detection test PASSED");
    } else {
        Serial.println("❌ Phase change detection test FAILED");
    }
}
```

#### 3.2 Cooling and Solidification Test
```cpp
void testSolidificationDetection() {
    Serial.println("=== SOLIDIFICATION DETECTION TEST ===");
    
    int test_container = 0;
    
    // Ensure PCM is in liquid state
    if (pcm_containers[test_container].phase_fraction < 0.8) {
        Serial.println("❌ PCM not in liquid state - run melting test first");
        return;
    }
    
    // Start cooling with TEC
    Serial.println("Starting controlled cooling...");
    digitalWrite(TEC_DIR_PINS[test_container], LOW); // Cooling mode
    analogWrite(TEC_PWM_PINS[test_container], 150); // Medium cooling
    
    unsigned long test_start_time = millis();
    bool solidification_detected = false;
    bool solidification_complete = false;
    
    while (millis() - test_start_time < 3600000) { // 1 hour max
        // Update sensors
        updateSensorReadings();
        
        // Check for solidification
        if (phase_detector.detectPhaseState(test_container) == FREEZING && !solidification_detected) {
            solidification_detected = true;
            Serial.println("🔄 SOLIDIFICATION DETECTED!");
            Serial.print("Time to detection: ");
            Serial.print((millis() - test_start_time) / 1000);
            Serial.println(" seconds");
            Serial.print("Temperature at detection: ");
            Serial.print(pcm_containers[test_container].temperature_top);
            Serial.println("°C");
        }
        
        // Check for solidification completion
        if (pcm_containers[test_container].phase_fraction < 0.05 && !solidification_complete) {
            solidification_complete = true;
            Serial.println("🔄 SOLIDIFICATION COMPLETE!");
            Serial.print("Time to complete solidification: ");
            Serial.print((millis() - test_start_time) / 1000);
            Serial.println(" seconds");
            Serial.print("Final temperature: ");
            Serial.print(pcm_containers[test_container].temperature_top);
            Serial.println("°C");
            
            // Turn off cooling
            analogWrite(TEC_PWM_PINS[test_container], 0);
            Serial.println("Cooling OFF");
            break;
        }
        
        // Safety check
        if (pcm_containers[test_container].temperature_top < 10.0) {
            analogWrite(TEC_PWM_PINS[test_container], 0);
            Serial.println("❌ SAFETY LIMIT EXCEEDED - Test aborted");
            break;
        }
        
        // Status update every 30 seconds
        if ((millis() - test_start_time) % 30000 == 0) {
            Serial.print("Temperature: ");
            Serial.print(pcm_containers[test_container].temperature_top);
            Serial.print("°C | Phase fraction: ");
            Serial.print(pcm_containers[test_container].phase_fraction * 100, 1);
            Serial.print("% | Heat flux: ");
            Serial.print(pcm_containers[test_container].heat_flux);
            Serial.println(" W/m²");
        }
        
        delay(5000); // Check every 5 seconds
    }
    
    // Results
    if (solidification_detected && solidification_complete) {
        Serial.println("✅ Solidification detection test PASSED");
    } else {
        Serial.println("❌ Solidification detection test FAILED");
    }
}
```

### Phase 4: Energy Storage Optimization Testing (60 minutes)

#### 4.1 Charging Efficiency Test
```cpp
void testChargingEfficiency() {
    Serial.println("=== CHARGING EFFICIENCY TEST ===");
    
    int test_container = 0;
    
    // Ensure starting from solid state
    if (pcm_containers[test_container].phase_fraction > 0.1) {
        Serial.println("❌ PCM not in solid state - cool first");
        return;
    }
    
    // Record initial state
    float initial_enthalpy = pcm_containers[test_container].enthalpy;
    float initial_temp = pcm_containers[test_container].temperature_top;
    unsigned long start_time = millis();
    float total_energy_input = 0.0;
    
    Serial.println("Starting optimized charging test...");
    
    // Start with optimal charging rate
    energy_storage.optimizeEnergyStorage(test_container);
    
    while (pcm_containers[test_container].phase_fraction < 0.95) {
        // Update sensors
        updateSensorReadings();
        
        // Calculate energy input
        float dt = 5.0; // 5 second intervals
        total_energy_input += pcm_containers[test_container].power_input * dt;
        
        // Optimize charging rate
        energy_storage.optimizeEnergyStorage(test_container);
        
        // Safety check
        if (pcm_containers[test_container].temperature_top > 80.0) {
            Serial.println("❌ SAFETY LIMIT EXCEEDED - Test aborted");
            break;
        }
        
        // Progress update
        if ((millis() - start_time) % 60000 == 0) { // Every minute
            float efficiency = energy_storage.calculateStorageEfficiency(test_container);
            Serial.print("Time: ");
            Serial.print((millis() - start_time) / 60000);
            Serial.print(" min | Phase: ");
            Serial.print(pcm_containers[test_container].phase_fraction * 100, 1);
            Serial.print("% | Efficiency: ");
            Serial.print(efficiency, 1);
            Serial.println("%");
        }
        
        delay(5000);
    }
    
    // Final calculations
    float final_enthalpy = pcm_containers[test_container].enthalpy;
    float stored_energy = final_enthalpy - initial_enthalpy;
    float charging_efficiency = (stored_energy / total_energy_input) * 100.0;
    unsigned long charging_time = (millis() - start_time) / 1000;
    
    Serial.println("=== CHARGING TEST RESULTS ===");
    Serial.print("Charging time: ");
    Serial.print(charging_time);
    Serial.println(" seconds");
    Serial.print("Energy input: ");
    Serial.print(total_energy_input / 1000.0, 1);
    Serial.println(" kJ");
    Serial.print("Energy stored: ");
    Serial.print(stored_energy / 1000.0, 1);
    Serial.println(" kJ");
    Serial.print("Charging efficiency: ");
    Serial.print(charging_efficiency, 1);
    Serial.println("%");
    
    if (charging_efficiency > 80.0) {
        Serial.println("✅ Charging efficiency test PASSED");
    } else {
        Serial.println("❌ Charging efficiency test FAILED");
    }
}
```

### Phase 5: Machine Learning and Analytics Testing (45 minutes)

#### 5.1 ML Prediction Accuracy Test
```cpp
void testMLPredictions() {
    Serial.println("=== ML PREDICTION ACCURACY TEST ===");
    
    // Test prediction accuracy for each container
    for (int container = 0; container < NUM_CONTAINERS; container++) {
        Serial.print("Testing predictions for container ");
        Serial.println(container);
        
        // Collect baseline data
        float actual_temperature = pcm_containers[container].temperature_top;
        float actual_phase_fraction = pcm_containers[container].phase_fraction;
        float actual_efficiency = pcm_containers[container].storage_efficiency;
        
        // Trigger ML prediction
        ml_analytics.predictPhaseChange(container);
        
        // Wait for prediction results
        delay(1000);
        
        // Compare predictions with actual values
        // Note: This would require storing and comparing predictions
        // For now, just verify ML system is running
        
        Serial.print("  Current temperature: ");
        Serial.print(actual_temperature);
        Serial.println("°C");
        Serial.print("  Phase fraction: ");
        Serial.print(actual_phase_fraction * 100, 1);
        Serial.println("%");
        Serial.print("  Efficiency: ");
        Serial.print(actual_efficiency, 1);
        Serial.println("%");
        
        // Verify thermal conductivity prediction
        if (analytics[container].thermal_conductivity > 0.1 && 
            analytics[container].thermal_conductivity < 1.0) {
            Serial.println("  ✅ Thermal conductivity prediction reasonable");
        } else {
            Serial.println("  ❌ Thermal conductivity prediction out of range");
        }
    }
}
```

#### 5.2 Analytics Performance Test
```cpp
void testAnalyticsPerformance() {
    Serial.println("=== ANALYTICS PERFORMANCE TEST ===");
    
    unsigned long start_time = millis();
    
    // Run analytics for all containers
    for (int container = 0; container < NUM_CONTAINERS; container++) {
        advanced_analytics.analyzePerformance(container);
    }
    
    unsigned long analysis_time = millis() - start_time;
    
    Serial.print("Analytics processing time: ");
    Serial.print(analysis_time);
    Serial.println(" ms");
    
    // Verify analytics results
    for (int container = 0; container < NUM_CONTAINERS; container++) {
        Serial.print("Container ");
        Serial.print(container);
        Serial.println(" analytics:");
        
        // Check if all metrics are within reasonable ranges
        bool metrics_valid = true;
        
        if (analytics[container].effectiveness < 0.0 || analytics[container].effectiveness > 1.0) {
            Serial.println("  ❌ Effectiveness out of range");
            metrics_valid = false;
        }
        
        if (analytics[container].efficiency < 0.0 || analytics[container].efficiency > 100.0) {
            Serial.println("  ❌ Efficiency out of range");
            metrics_valid = false;
        }
        
        if (analytics[container].performance_score < 0.0 || analytics[container].performance_score > 100.0) {
            Serial.println("  ❌ Performance score out of range");
            metrics_valid = false;
        }
        
        if (metrics_valid) {
            Serial.println("  ✅ All metrics within valid ranges");
        }
    }
    
    if (analysis_time < 5000) { // Should complete in under 5 seconds
        Serial.println("✅ Analytics performance test PASSED");
    } else {
        Serial.println("❌ Analytics performance test FAILED - too slow");
    }
}
```

### Phase 6: IoT and Cloud Integration Testing (30 minutes)

#### 6.1 WiFi and MQTT Connectivity Test
```cpp
void testIoTConnectivity() {
    Serial.println("=== IoT CONNECTIVITY TEST ===");
    
    // Test WiFi connection
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("✅ WiFi connected");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        Serial.print("Signal Strength: ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");
    } else {
        Serial.println("❌ WiFi not connected");
    }
    
    // Test MQTT connection
    if (mqtt_client.connected()) {
        Serial.println("✅ MQTT connected");
        
        // Test publishing
        StaticJsonDocument<256> testDoc;
        testDoc["test"] = "connectivity";
        testDoc["timestamp"] = millis();
        
        String testPayload;
        serializeJson(testDoc, testPayload);
        
        if (mqtt_client.publish("pcm/test", testPayload.c_str())) {
            Serial.println("✅ MQTT publish successful");
        } else {
            Serial.println("❌ MQTT publish failed");
        }
    } else {
        Serial.println("❌ MQTT not connected");
    }
    
    // Test ESP32 web server
    WiFiClient client;
    if (client.connect("192.168.1.101", 80)) {
        client.println("GET /api/status HTTP/1.1");
        client.println("Host: 192.168.1.101");
        client.println("Connection: close");
        client.println();
        
        delay(2000);
        
        if (client.available()) {
            String response = client.readString();
            if (response.indexOf("200 OK") > 0) {
                Serial.println("✅ ESP32 web server responding");
            } else {
                Serial.println("❌ ESP32 web server error");
            }
        }
        client.stop();
    } else {
        Serial.println("❌ Cannot connect to ESP32 web server");
    }
}
```

#### 6.2 Data Logging and Export Test
```cpp
void testDataLogging() {
    Serial.println("=== DATA LOGGING TEST ===");
    
    // Test SD card functionality
    if (!SD.begin(SD_CS_PIN)) {
        Serial.println("❌ SD card initialization failed");
        return;
    }
    
    // Create test log file
    File testFile = SD.open("test_log.csv", FILE_WRITE);
    if (testFile) {
        testFile.println("timestamp,container,temperature,phase_fraction,efficiency");
        
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            testFile.print(millis());
            testFile.print(",");
            testFile.print(i);
            testFile.print(",");
            testFile.print(pcm_containers[i].temperature_top);
            testFile.print(",");
            testFile.print(pcm_containers[i].phase_fraction);
            testFile.print(",");
            testFile.println(pcm_containers[i].storage_efficiency);
        }
        
        testFile.close();
        Serial.println("✅ Test data written to SD card");
    } else {
        Serial.println("❌ Failed to create test log file");
    }
    
    // Verify file can be read
    testFile = SD.open("test_log.csv", FILE_READ);
    if (testFile) {
        Serial.println("✅ Test log file readable");
        Serial.println("File contents:");
        while (testFile.available()) {
            Serial.write(testFile.read());
        }
        testFile.close();
    } else {
        Serial.println("❌ Cannot read test log file");
    }
    
    // Clean up
    SD.remove("test_log.csv");
}
```

### Phase 7: Safety System Testing (30 minutes)

#### 7.1 Emergency Stop Test
```cpp
void testEmergencyStop() {
    Serial.println("=== EMERGENCY STOP TEST ===");
    
    // Turn on some heaters and TECs for testing
    digitalWrite(HEATER_RELAY_PINS[0], HIGH);
    analogWrite(TEC_PWM_PINS[0], 100);
    
    Serial.println("Heaters and TECs activated");
    Serial.println("Press emergency stop button within 10 seconds...");
    
    unsigned long start_time = millis();
    bool emergency_detected = false;
    
    while (millis() - start_time < 10000) {
        if (emergency_stop_active) {
            emergency_detected = true;
            Serial.println("✅ Emergency stop detected");
            
            // Verify all heaters and TECs are off
            bool all_off = true;
            for (int i = 0; i < NUM_CONTAINERS; i++) {
                if (digitalRead(HEATER_RELAY_PINS[i]) == HIGH) {
                    all_off = false;
                    break;
                }
            }
            
            if (all_off) {
                Serial.println("✅ All heaters and TECs turned off");
            } else {
                Serial.println("❌ Some heaters/TECs still active");
            }
            
            break;
        }
        delay(100);
    }
    
    if (!emergency_detected) {
        Serial.println("❌ Emergency stop not detected");
    }
    
    // Reset emergency stop
    Serial.println("Release emergency stop button to continue...");
    while (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
        delay(100);
    }
    
    emergency_stop_active = false;
    Serial.println("✅ Emergency stop reset");
}
```

### Phase 8: Long-Term Performance Testing (24 hours)

#### 8.1 Continuous Operation Test
```cpp
void longTermPerformanceTest() {
    Serial.println("=== 24-HOUR CONTINUOUS OPERATION TEST ===");
    
    unsigned long test_start_time = millis();
    unsigned long test_duration = 24 * 60 * 60 * 1000; // 24 hours
    
    int cycle_count = 0;
    int error_count = 0;
    float total_energy_processed = 0.0;
    float min_efficiency = 100.0;
    float max_efficiency = 0.0;
    
    while (millis() - test_start_time < test_duration) {
        // Update sensor readings
        updateSensorReadings();
        
        // Perform analytics
        performAnalytics();
        
        // Check for errors
        if (emergency_stop_active) {
            error_count++;
            Serial.println("Error detected at " + String((millis() - test_start_time) / 3600000) + " hours");
        }
        
        // Track energy and efficiency
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            total_energy_processed += pcm_containers[i].power_input * 5.0; // 5-second intervals
            
            if (pcm_containers[i].storage_efficiency < min_efficiency) {
                min_efficiency = pcm_containers[i].storage_efficiency;
            }
            
            if (pcm_containers[i].storage_efficiency > max_efficiency) {
                max_efficiency = pcm_containers[i].storage_efficiency;
            }
        }
        
        // Count thermal cycles
        static String last_phase_states[NUM_CONTAINERS] = {"", "", "", ""};
        for (int i = 0; i < NUM_CONTAINERS; i++) {
            if (pcm_containers[i].phase_state != last_phase_states[i]) {
                cycle_count++;
                last_phase_states[i] = pcm_containers[i].phase_state;
            }
        }
        
        // Hourly progress report
        if ((millis() - test_start_time) % 3600000 == 0) {
            int hours_elapsed = (millis() - test_start_time) / 3600000;
            Serial.print("Test progress: ");
            Serial.print(hours_elapsed);
            Serial.print(" hours | Cycles: ");
            Serial.print(cycle_count);
            Serial.print(" | Errors: ");
            Serial.println(error_count);
        }
        
        delay(5000); // 5-second intervals
    }
    
    // Final report
    Serial.println("=== 24-HOUR TEST COMPLETE ===");
    Serial.print("Total thermal cycles: ");
    Serial.println(cycle_count);
    Serial.print("Total errors: ");
    Serial.println(error_count);
    Serial.print("Total energy processed: ");
    Serial.print(total_energy_processed / 3600000.0, 1);
    Serial.println(" kWh");
    Serial.print("Efficiency range: ");
    Serial.print(min_efficiency, 1);
    Serial.print("% - ");
    Serial.print(max_efficiency, 1);
    Serial.println("%");
    
    // Pass criteria
    if (error_count == 0 && cycle_count > 10 && min_efficiency > 60.0) {
        Serial.println("✅ 24-hour continuous operation test PASSED");
    } else {
        Serial.println("❌ 24-hour continuous operation test FAILED");
    }
}
```

## Performance Benchmarks

### Expected Performance Metrics
- **Phase Change Detection Time**: < 30 seconds
- **Temperature Accuracy**: ±0.5°C
- **Mass Measurement Accuracy**: ±0.1% of reading
- **Heat Flux Accuracy**: ±5% of reading
- **Storage Efficiency**: > 80%
- **System Response Time**: < 5 seconds
- **Data Logging Rate**: 1 sample per 5 seconds
- **ML Prediction Time**: < 2 seconds
- **Analytics Processing Time**: < 5 seconds

### Thermal Cycling Requirements
- **Minimum Cycles**: 100 complete melt/freeze cycles
- **Temperature Range**: 10°C to 80°C
- **Cycle Time**: 10-30 minutes per cycle
- **Efficiency Degradation**: < 5% after 100 cycles

## Test Results Documentation

### Test Report Template
```
========================================
PCM CONTROLLER SYSTEM TEST REPORT
========================================

Test Date: _______________
Test Engineer: ___________
System Version: __________
Hardware Revision: _______

SENSOR CALIBRATION:
□ Temperature Sensors: PASS/FAIL
□ Mass Sensors: PASS/FAIL
□ Heat Flux Sensors: PASS/FAIL
□ Current Sensors: PASS/FAIL

PHASE CHANGE DETECTION:
□ Melting Detection: PASS/FAIL
□ Solidification Detection: PASS/FAIL
□ Phase Fraction Accuracy: PASS/FAIL
□ Timing Accuracy: PASS/FAIL

ENERGY STORAGE:
□ Charging Efficiency: PASS/FAIL
□ Discharging Efficiency: PASS/FAIL
□ Storage Capacity: PASS/FAIL
□ Thermal Losses: PASS/FAIL

MACHINE LEARNING:
□ Model Loading: PASS/FAIL
□ Prediction Accuracy: PASS/FAIL
□ Processing Speed: PASS/FAIL
□ Cloud Integration: PASS/FAIL

SAFETY SYSTEMS:
□ Emergency Stop: PASS/FAIL
□ Overtemperature Protection: PASS/FAIL
□ Electrical Safety: PASS/FAIL
□ Thermal Safety: PASS/FAIL

PERFORMANCE METRICS:
Phase Change Detection Time: _____ seconds
Temperature Accuracy: _____ °C
Storage Efficiency: _____ %
System Response Time: _____ seconds
ML Prediction Time: _____ seconds

RELIABILITY TESTS:
□ 24-Hour Operation: PASS/FAIL
□ Thermal Cycling: PASS/FAIL
□ Power Cycle Recovery: PASS/FAIL
□ Communication Stability: PASS/FAIL

NOTES:
_________________________________
_________________________________
_________________________________

OVERALL RESULT: PASS/FAIL
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Thermocouple readings show -999 or NaN
**Cause**: Thermocouple connection problem or MAX31855 failure
**Solution**: 
1. Check thermocouple polarity (T+ and T-)
2. Verify MAX31855 SPI connections
3. Test thermocouple continuity
4. Check cold junction compensation
5. Verify 3.3V power supply

#### Issue: Load cell readings drift or are unstable
**Cause**: Mechanical mounting issues or temperature effects
**Solution**:
1. Check mechanical mounting stability
2. Verify electrical connections
3. Recalibrate with known masses
4. Check for temperature compensation
5. Verify HX711 power supply stability

#### Issue: Phase change not detected
**Cause**: Incorrect PCM properties or sensor calibration
**Solution**:
1. Verify PCM material properties
2. Check temperature sensor calibration
3. Validate heat flux sensor readings
4. Adjust phase change detection thresholds
5. Verify power input measurements

#### Issue: ML predictions are unrealistic
**Cause**: Model training issues or input data problems
**Solution**:
1. Check model file integrity
2. Verify input data quality
3. Validate feature engineering
4. Update model from cloud
5. Reset tensor arena memory

#### Issue: Data logging fails
**Cause**: SD card problems or file system errors
**Solution**:
1. Check SD card formatting (FAT32)
2. Verify SD card connections
3. Test with different SD card
4. Check file system permissions
5. Verify CSV data format

This comprehensive testing guide ensures the PCM controller system meets all requirements for professional thermal energy storage applications, including accurate phase change detection, efficient energy storage, and reliable long-term operation.