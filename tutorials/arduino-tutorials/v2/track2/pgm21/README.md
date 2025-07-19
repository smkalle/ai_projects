# Program 21: Fatigue Testing Machine

## Overview
This program implements a professional desktop fatigue testing machine capable of performing cyclic loading tests on material specimens. The system generates S-N curves, performs Weibull analysis for failure prediction, and monitors crack growth in real-time, all while maintaining compliance with ASTM E466 standards.

## Features
- Variable amplitude cyclic loading (0.1-50 Hz)
- Force control up to 200kg with 0.1% accuracy
- Real-time crack detection using acoustic emission
- S-N curve generation with statistical analysis
- Weibull distribution failure analysis
- Paris law crack growth modeling
- Cloud-based data storage and analysis
- Multi-specimen sequential testing
- Emergency stop and safety interlocks
- ASTM E466 compliance

## Hardware Requirements
- Arduino Mega 2560 (main controller)
- ESP32 DevKit (analytics and IoT gateway)
- NEMA 23 stepper motor (4.2A, 3.0 Nm)
- TB6600 stepper motor driver
- 200kg load cell (S-type)
- HX711 24-bit load cell amplifier
- Linear Variable Differential Transformer (LVDT) ±25mm
- AD698 LVDT signal conditioner
- 2x Acoustic emission sensors (150-400 kHz)
- ADS1256 24-bit ADC for acoustic signals
- Emergency stop button with safety relay
- 7" TFT display with touch interface
- SD card module for data logging
- Linear guide rails and lead screw assembly
- Specimen grips (wedge or pin type)
- Safety enclosure with interlocks

## Software Features
- PID force control with adaptive tuning
- Sinusoidal, triangular, and square wave loading
- Real-time cycle counting and peak detection
- Acoustic emission hit detection and analysis
- Statistical analysis (mean, std dev, confidence intervals)
- Weibull parameter estimation (β, η)
- Paris law fitting (da/dN vs ΔK)
- Cloud synchronization via MQTT
- Web dashboard for remote monitoring
- Automated test report generation

## Applications
- Metal fatigue characterization
- Composite material testing
- Weld joint evaluation
- Component life prediction
- Quality control testing
- Research and development
- Educational demonstrations

## Getting Started
1. Review the circuit diagram for proper connections
2. Assemble the mechanical testing frame
3. Install and calibrate load cell and LVDT
4. Upload Arduino and ESP32 firmware
5. Configure network settings for IoT connectivity
6. Perform system calibration with known weights
7. Run validation tests with standard specimens
8. Begin fatigue testing following ASTM procedures

## Test Capabilities
- Maximum load: 200kg (2000N)
- Frequency range: 0.1-50 Hz
- Stroke length: ±25mm
- Load accuracy: ±0.1% of full scale
- Displacement accuracy: ±0.01mm
- Temperature range: 10-40°C
- Test duration: Continuous (>10^7 cycles)
- Data acquisition: 1000 Hz per channel

## Safety Features
- Hardware emergency stop
- Software load limits
- Displacement limits
- Door interlock sensors
- Overload protection
- Automatic test termination on failure
- Remote monitoring alerts
- Backup power for controlled shutdown

## Compliance
- ASTM E466: Constant amplitude fatigue testing
- ASTM E468: Presentation of fatigue data
- ASTM E647: Crack growth rate testing
- ASTM E739: Statistical analysis
- ISO 12106: Metallic materials fatigue testing