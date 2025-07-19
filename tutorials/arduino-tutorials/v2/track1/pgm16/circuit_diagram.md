# Program 16: Multi-Zone Thermal Management System - Circuit Diagram

## Overview
This circuit diagram shows the complete wiring for a 4-zone thermal management system with predictive control, safety systems, and IoT connectivity.

## Main Components Connection

### Arduino Mega 2560 (Main Controller)
```
Arduino Mega 2560
├── Digital Pins
│   ├── Pin 2  → TEC Zone 0 PWM Control
│   ├── Pin 3  → Fan Zone 0 PWM Control
│   ├── Pin 4  → TEC Zone 1 PWM Control
│   ├── Pin 5  → Fan Zone 1 PWM Control
│   ├── Pin 6  → TEC Zone 2 PWM Control
│   ├── Pin 7  → Fan Zone 2 PWM Control
│   ├── Pin 8  → TEC Zone 3 PWM Control
│   ├── Pin 9  → Fan Zone 3 PWM Control
│   ├── Pin 10 → MAX31855 Zone 0 CS
│   ├── Pin 11 → MAX31855 Zone 1 CS
│   ├── Pin 12 → MAX31855 Zone 2 CS
│   ├── Pin 13 → MAX31855 Zone 3 CS
│   ├── Pin 20 → Overtemp Alarm (Interrupt)
│   ├── Pin 21 → Emergency Stop (Interrupt)
│   ├── Pin 22 → Status LED Zone 0
│   ├── Pin 24 → Status LED Zone 1
│   ├── Pin 26 → Status LED Zone 2
│   ├── Pin 28 → Status LED Zone 3
│   └── Pin 53 → SD Card CS
├── SPI Bus
│   ├── Pin 50 → MISO (MAX31855 data)
│   ├── Pin 51 → MOSI (SD Card data)
│   ├── Pin 52 → SCK (Clock)
│   └── Pin 53 → SS (Slave Select)
├── I2C Bus
│   ├── Pin 20 → SDA (INA219 sensors)
│   └── Pin 21 → SCL (INA219 sensors)
├── Serial Communication
│   ├── Pin 0  → RX (USB/Debug)
│   ├── Pin 1  → TX (USB/Debug)
│   ├── Pin 18 → TX1 (ESP32 communication)
│   └── Pin 19 → RX1 (ESP32 communication)
└── Power
    ├── VIN → 12V DC Input
    ├── 5V → Logic Level Power
    ├── 3.3V → Sensor Power
    └── GND → Common Ground
```

## Zone Hardware Configuration

### Zone 0 (Typical for all zones)
```
Zone 0 Hardware
├── Temperature Sensing
│   ├── MAX31855 Thermocouple Amplifier
│   │   ├── VCC → 3.3V
│   │   ├── GND → Ground
│   │   ├── SCK → Pin 52 (SPI Clock)
│   │   ├── CS  → Pin 10 (Chip Select)
│   │   ├── DO  → Pin 50 (MISO)
│   │   └── T+, T- → Type K Thermocouple
│   └── Type K Thermocouple
│       ├── T+ → MAX31855 T+
│       ├── T- → MAX31855 T-
│       └── Shield → Ground (if shielded)
├── Power Control
│   ├── L298N Motor Driver
│   │   ├── VCC → 12V
│   │   ├── GND → Ground
│   │   ├── ENA → Pin 2 (PWM Control)
│   │   ├── IN1 → 5V (Direction)
│   │   ├── IN2 → GND (Direction)
│   │   ├── OUT1 → TEC1-12706 Red (+)
│   │   └── OUT2 → TEC1-12706 Black (-)
│   └── TEC1-12706 Peltier Module
│       ├── Red Wire → L298N OUT1
│       ├── Black Wire → L298N OUT2
│       └── Thermal Connection → Heat Block
├── Current Monitoring
│   ├── INA219 Current Sensor (Address 0x40)
│   │   ├── VCC → 3.3V
│   │   ├── GND → Ground
│   │   ├── SDA → Pin 20 (I2C Data)
│   │   ├── SCL → Pin 21 (I2C Clock)
│   │   ├── VIN+ → 12V Supply
│   │   ├── VIN- → To TEC Load
│   │   └── A0, A1 → Ground (Address 0x40)
├── Cooling System
│   ├── Cooling Fan (12V)
│   │   ├── Red → MOSFET Drain
│   │   ├── Black → Ground
│   │   └── PWM Control → Pin 3 via MOSFET
│   └── MOSFET (IRF540N)
│       ├── Gate → Pin 3 (PWM)
│       ├── Drain → Fan Red
│       ├── Source → Ground
│       └── Gate Resistor → 1kΩ
└── Status Indication
    ├── Status LED (RGB Common Cathode)
    │   ├── Red → Pin 22 via 220Ω resistor
    │   ├── Green → Pin 23 via 220Ω resistor
    │   ├── Blue → Pin 24 via 220Ω resistor
    │   └── Common → Ground
    └── Current Limiting Resistors
        └── 220Ω for each LED color
```

## Safety Systems

### Emergency Stop Circuit
```
Emergency Stop System
├── Emergency Stop Button (NC)
│   ├── Terminal 1 → 5V
│   ├── Terminal 2 → Pin 21 (Interrupt)
│   └── Pull-up resistor → 10kΩ to 5V
├── Overtemperature Alarm
│   ├── Temperature Switch (NC at 85°C)
│   ├── Terminal 1 → 5V
│   ├── Terminal 2 → Pin 20 (Interrupt)
│   └── Pull-up resistor → 10kΩ to 5V
└── Master Power Relay
    ├── Coil → Pin 30 via relay driver
    ├── NO Contact → Main 12V Power
    └── Emergency Override → Hardware bypass
```

### Power Distribution
```
Power Distribution
├── 12V 10A Power Supply
│   ├── 12V+ → Master Power Relay
│   ├── 12V- → Common Ground
│   └── Protection → 10A Fuse
├── 5V Logic Power
│   ├── Arduino Mega VIN → 12V
│   ├── Internal 5V Regulator
│   └── Current Limit → 1A
└── 3.3V Sensor Power
    ├── Arduino Mega 3.3V
    ├── MAX31855 Power
    └── INA219 Power
```

## ESP32 IoT Gateway Connection

### ESP32 to Arduino Communication
```
ESP32 ↔ Arduino Serial Communication
├── ESP32 GPIO1 (TX) → Arduino Pin 19 (RX1)
├── ESP32 GPIO3 (RX) → Arduino Pin 18 (TX1)
├── ESP32 GND → Arduino GND
└── ESP32 3.3V → Arduino 3.3V
```

### ESP32 WiFi and Cloud Connection
```
ESP32 Connectivity
├── WiFi Module (Built-in)
│   ├── SSID Configuration
│   ├── Password Authentication
│   └── Network Connection
├── MQTT Client
│   ├── Broker Connection
│   ├── Topic Subscriptions
│   └── Data Publishing
└── Cloud Services
    ├── InfluxDB Time-series Data
    ├── Grafana Dashboard
    └── Alert Management
```

## Wiring Specifications

### Wire Gauge Requirements
- **Power Wires (12V)**: 14 AWG minimum
- **TEC Connections**: 12 AWG (high current)
- **Control Signals**: 22 AWG
- **I2C/SPI**: 24 AWG with twisted pair
- **Thermocouples**: Thermocouple grade wire

### Connector Types
- **Power**: Terminal blocks (5.08mm pitch)
- **Sensors**: JST-XH connectors
- **Control**: Dupont connectors
- **Safety**: Screw terminals

### Grounding Strategy
- **Single Point Ground**: All grounds connect at power supply
- **Analog Ground**: Separate for sensitive measurements
- **Digital Ground**: Common with power ground
- **Shield Ground**: Connected to chassis ground

## PCB Layout Considerations

### High-Current Traces
- **TEC Power**: 2oz copper, 3mm minimum width
- **12V Distribution**: 1oz copper, 2mm minimum width
- **Ground Plane**: Solid copper pour

### Thermal Management
- **Power Components**: Thermal vias
- **Heat Sinks**: L298N drivers
- **Component Placement**: Keep heat sources separate

### EMC Considerations
- **Decoupling Capacitors**: 100nF ceramic near each IC
- **Power Filtering**: 1000µF electrolytic on 12V
- **Signal Integrity**: Ground planes and proper routing

## Testing and Verification

### Initial Testing Sequence
1. **Power-on Test**: Verify all voltages
2. **Communication Test**: I2C and SPI devices
3. **Sensor Test**: Temperature readings
4. **Control Test**: PWM outputs
5. **Safety Test**: Emergency stop function

### Calibration Procedure
1. **Temperature Calibration**: Ice bath and boiling water
2. **Current Calibration**: Known resistive loads
3. **Power Calibration**: Precision power meter
4. **Timing Calibration**: Oscilloscope verification

### Safety Verification
1. **Emergency Stop**: Manual activation test
2. **Overtemperature**: Controlled temperature increase
3. **Overcurrent**: Current limit verification
4. **Communication Timeout**: Disconnect test

## Troubleshooting Guide

### Common Issues
1. **No Temperature Reading**: Check thermocouple polarity
2. **No TEC Control**: Verify L298N connections
3. **Current Sensor Error**: Check I2C addresses
4. **WiFi Connection**: Verify credentials and signal

### Debug Tools
- **Multimeter**: Voltage and continuity checks
- **Oscilloscope**: Signal integrity verification
- **Thermal Camera**: Heat distribution analysis
- **Current Clamp**: Power consumption measurement