# Program 17: Phase Change Material (PCM) Controller - Circuit Diagram

## Overview
This circuit diagram shows the complete wiring for a 4-container PCM thermal energy storage system with advanced analytics, real-time phase change detection, and IoT connectivity.

## Main Components Connection

### Arduino Mega 2560 (Main Controller)
```
Arduino Mega 2560
├── Digital Pins
│   ├── Pin 2  → TEC Container 0 PWM Control
│   ├── Pin 3  → TEC Container 0 Direction Control
│   ├── Pin 4  → TEC Container 1 PWM Control
│   ├── Pin 5  → TEC Container 1 Direction Control
│   ├── Pin 6  → TEC Container 2 PWM Control
│   ├── Pin 7  → TEC Container 2 Direction Control
│   ├── Pin 8  → TEC Container 3 PWM Control
│   ├── Pin 9  → TEC Container 3 Direction Control
│   ├── Pin 10 → SSR Container 0 Heater Control
│   ├── Pin 11 → SSR Container 1 Heater Control
│   ├── Pin 12 → SSR Container 2 Heater Control
│   ├── Pin 13 → SSR Container 3 Heater Control
│   ├── Pin 14 → Fan Container 0 PWM Control
│   ├── Pin 15 → Fan Container 1 PWM Control
│   ├── Pin 16 → Fan Container 2 PWM Control
│   ├── Pin 17 → Fan Container 3 PWM Control
│   ├── Pin 18 → Load Cell 0 Data (HX711)
│   ├── Pin 19 → Load Cell 0 Clock (HX711)
│   ├── Pin 20 → Load Cell 1 Data (HX711)
│   ├── Pin 21 → Load Cell 1 Clock (HX711)
│   ├── Pin 22 → MAX31855 Container 0 Top CS
│   ├── Pin 24 → MAX31855 Container 0 Bottom CS
│   ├── Pin 26 → MAX31855 Container 1 Top CS
│   ├── Pin 28 → MAX31855 Container 1 Bottom CS
│   ├── Pin 30 → MAX31855 Container 2 Top CS
│   ├── Pin 32 → MAX31855 Container 2 Bottom CS
│   ├── Pin 34 → MAX31855 Container 3 Top CS
│   ├── Pin 36 → MAX31855 Container 3 Bottom CS
│   ├── Pin 38 → Status LED Container 0 Top
│   ├── Pin 40 → Status LED Container 0 Bottom
│   ├── Pin 42 → Status LED Container 1 Top
│   ├── Pin 44 → Status LED Container 1 Bottom
│   ├── Pin 46 → Status LED Container 2 Top
│   ├── Pin 48 → Status LED Container 2 Bottom
│   ├── Pin 50 → Status LED Container 3 Top
│   ├── Pin 52 → Status LED Container 3 Bottom
│   └── Pin 53 → SD Card CS
├── SPI Bus
│   ├── Pin 50 → MISO (MAX31855 data)
│   ├── Pin 51 → MOSI (SD Card data)
│   ├── Pin 52 → SCK (Clock)
│   └── Pin 53 → SS (Slave Select)
├── I2C Bus
│   ├── Pin 20 → SDA (INA3221, ADS1115, DS3231)
│   └── Pin 21 → SCL (INA3221, ADS1115, DS3231)
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

## PCM Container Configuration

### Container 0 (Typical for all containers)
```
PCM Container 0
├── Temperature Sensing
│   ├── MAX31855 Top Thermocouple Amplifier
│   │   ├── VCC → 3.3V
│   │   ├── GND → Ground
│   │   ├── SCK → Pin 52 (SPI Clock)
│   │   ├── CS  → Pin 22 (Chip Select)
│   │   ├── DO  → Pin 50 (MISO)
│   │   └── T+, T- → Type T Thermocouple (Top)
│   ├── MAX31855 Bottom Thermocouple Amplifier
│   │   ├── VCC → 3.3V
│   │   ├── GND → Ground
│   │   ├── SCK → Pin 52 (SPI Clock)
│   │   ├── CS  → Pin 24 (Chip Select)
│   │   ├── DO  → Pin 50 (MISO)
│   │   └── T+, T- → Type T Thermocouple (Bottom)
│   ├── Type T Thermocouple (Top)
│   │   ├── T+ → MAX31855 T+ (Top)
│   │   ├── T- → MAX31855 T- (Top)
│   │   └── Shield → Ground
│   └── Type T Thermocouple (Bottom)
│       ├── T+ → MAX31855 T+ (Bottom)
│       ├── T- → MAX31855 T- (Bottom)
│       └── Shield → Ground
├── Mass Measurement
│   ├── HX711 Load Cell Amplifier
│   │   ├── VCC → 5V
│   │   ├── GND → Ground
│   │   ├── DT → Pin 18 (Data)
│   │   ├── SCK → Pin 19 (Clock)
│   │   ├── E+ → Load Cell Red
│   │   ├── E- → Load Cell Black
│   │   ├── A+ → Load Cell White
│   │   └── A- → Load Cell Green
│   └── Load Cell (5kg capacity)
│       ├── Red → HX711 E+
│       ├── Black → HX711 E-
│       ├── White → HX711 A+
│       └── Green → HX711 A-
├── Thermal Control
│   ├── TEC1-12706 Peltier Module
│   │   ├── L298N Motor Driver
│   │   │   ├── VCC → 12V
│   │   │   ├── GND → Ground
│   │   │   ├── ENA → Pin 2 (PWM Control)
│   │   │   ├── IN1 → Pin 3 (Direction)
│   │   │   ├── IN2 → GND
│   │   │   ├── OUT1 → TEC Red Wire
│   │   │   └── OUT2 → TEC Black Wire
│   │   ├── Red Wire → L298N OUT1
│   │   ├── Black Wire → L298N OUT2
│   │   └── Thermal Interface → PCM Container
│   ├── Cartridge Heater (100W)
│   │   ├── SSR-25DA Solid State Relay
│   │   │   ├── Input+ → Pin 10 (Control)
│   │   │   ├── Input- → Ground
│   │   │   ├── Output 1 → 120V AC Live
│   │   │   └── Output 2 → Heater Terminal 1
│   │   ├── Terminal 1 → SSR Output 2
│   │   ├── Terminal 2 → 120V AC Neutral
│   │   └── Thermal Interface → PCM Container
│   └── Cooling Fan (12V)
│       ├── IRF540N MOSFET
│       │   ├── Gate → Pin 14 (PWM) via 1kΩ resistor
│       │   ├── Drain → Fan Positive
│       │   ├── Source → Ground
│       │   └── Gate Resistor → 1kΩ
│       ├── Positive → MOSFET Drain
│       ├── Negative → Ground
│       └── Airflow → PCM Container
├── Power Monitoring
│   ├── INA3221 Current Monitor (Address 0x40)
│   │   ├── VCC → 3.3V
│   │   ├── GND → Ground
│   │   ├── SDA → Pin 20 (I2C Data)
│   │   ├── SCL → Pin 21 (I2C Clock)
│   │   ├── Channel 1 VIN+ → 12V TEC Supply
│   │   ├── Channel 1 VIN- → To TEC Load
│   │   ├── Channel 2 VIN+ → 120V AC (via transformer)
│   │   ├── Channel 2 VIN- → To Heater Load
│   │   └── A0, A1 → Ground (Address 0x40)
├── Heat Flux Sensing
│   ├── ADS1115 16-bit ADC (Address 0x48)
│   │   ├── VCC → 3.3V
│   │   ├── GND → Ground
│   │   ├── SDA → Pin 20 (I2C Data)
│   │   ├── SCL → Pin 21 (I2C Clock)
│   │   ├── A0 → Heat Flux Sensor Output
│   │   ├── A1 → Auxiliary Analog Input
│   │   └── ADDR → Ground (Address 0x48)
│   └── Heat Flux Sensor (Hukseflux HFP01)
│       ├── Signal+ → ADS1115 A0
│       ├── Signal- → ADS1115 GND
│       ├── Shield → Ground
│       └── Thermal Interface → PCM Container
└── Status Indication
    ├── Status LED Top (RGB Common Cathode)
    │   ├── Red → Pin 38 via 220Ω resistor
    │   ├── Green → Pin 39 via 220Ω resistor
    │   ├── Blue → Pin 40 via 220Ω resistor
    │   └── Common → Ground
    ├── Status LED Bottom (RGB Common Cathode)
    │   ├── Red → Pin 40 via 220Ω resistor
    │   ├── Green → Pin 41 via 220Ω resistor
    │   ├── Blue → Pin 42 via 220Ω resistor
    │   └── Common → Ground
    └── Current Limiting Resistors
        └── 220Ω for each LED color
```

## Real-Time Clock and Data Storage

### DS3231 RTC Module
```
DS3231 RTC Module
├── VCC → 3.3V
├── GND → Ground
├── SDA → Pin 20 (I2C Data)
├── SCL → Pin 21 (I2C Clock)
├── 32K → Not connected
├── SQW → Not connected
└── Battery → CR2032 (backup power)
```

### SD Card Module
```
SD Card Module
├── VCC → 5V
├── GND → Ground
├── MISO → Pin 50 (SPI MISO)
├── MOSI → Pin 51 (SPI MOSI)
├── SCK → Pin 52 (SPI Clock)
└── CS → Pin 53 (Chip Select)
```

## ESP32 Analytics Gateway

### ESP32 to Arduino Communication
```
ESP32 ↔ Arduino Serial Communication
├── ESP32 GPIO1 (TX) → Arduino Pin 19 (RX1)
├── ESP32 GPIO3 (RX) → Arduino Pin 18 (TX1)
├── ESP32 GND → Arduino GND
└── ESP32 3.3V → Arduino 3.3V
```

### ESP32 Machine Learning Processing
```
ESP32 ML Processing
├── TensorFlow Lite Model
│   ├── Phase Change Prediction
│   ├── Thermal Behavior Modeling
│   └── Optimization Algorithm
├── Edge AI Inference
│   ├── Real-time Processing
│   ├── Pattern Recognition
│   └── Anomaly Detection
└── Cloud Integration
    ├── Model Updates
    ├── Data Synchronization
    └── Remote Monitoring
```

## Safety Systems

### Emergency Stop Circuit
```
Emergency Stop System
├── Emergency Stop Button (NC)
│   ├── Terminal 1 → 5V
│   ├── Terminal 2 → Pin 21 (Interrupt)
│   └── Pull-up resistor → 10kΩ to 5V
├── Overtemperature Protection
│   ├── Temperature Switch (NC at 120°C)
│   ├── Terminal 1 → 5V
│   ├── Terminal 2 → Pin 20 (Interrupt)
│   └── Pull-up resistor → 10kΩ to 5V
├── Overpressure Protection
│   ├── Pressure Switch (NC at 2 bar)
│   ├── Terminal 1 → 5V
│   ├── Terminal 2 → Pin 19 (Interrupt)
│   └── Pull-up resistor → 10kΩ to 5V
└── Master Power Contactor
    ├── Coil → Pin 30 via relay driver
    ├── NO Contact → Main Power
    └── Emergency Override → Hardware bypass
```

## Power Distribution

### Main Power Supply
```
Power Distribution
├── 12V 15A Power Supply
│   ├── 12V+ → Master Power Contactor
│   ├── 12V- → Common Ground
│   └── Protection → 15A Circuit Breaker
├── 120V AC Power (for heaters)
│   ├── Hot → SSR Input
│   ├── Neutral → Common Neutral
│   └── Protection → 15A GFCI Breaker
├── 5V Logic Power
│   ├── Arduino Mega VIN → 12V
│   ├── Internal 5V Regulator
│   └── Current Limit → 2A
└── 3.3V Sensor Power
    ├── Arduino Mega 3.3V
    ├── MAX31855 Power (8x)
    ├── INA3221 Power (2x)
    ├── ADS1115 Power (2x)
    └── DS3231 Power
```

## Advanced Sensor Integration

### Heat Flux Measurement
```
Heat Flux Sensor Array
├── Container 0 Sensor (HFP01)
│   ├── Signal → ADS1115 #0 Channel 0
│   ├── Calibration → 60.0 µV/(W/m²)
│   └── Range → ±2000 W/m²
├── Container 1 Sensor (HFP01)
│   ├── Signal → ADS1115 #0 Channel 1
│   ├── Calibration → 60.0 µV/(W/m²)
│   └── Range → ±2000 W/m²
├── Container 2 Sensor (HFP01)
│   ├── Signal → ADS1115 #1 Channel 0
│   ├── Calibration → 60.0 µV/(W/m²)
│   └── Range → ±2000 W/m²
└── Container 3 Sensor (HFP01)
    ├── Signal → ADS1115 #1 Channel 1
    ├── Calibration → 60.0 µV/(W/m²)
    └── Range → ±2000 W/m²
```

### Precision Mass Measurement
```
Load Cell Configuration
├── Container 0 & 1 Load Cell
│   ├── Capacity → 5kg
│   ├── Sensitivity → 2mV/V
│   ├── Accuracy → ±0.02% FS
│   └── Resolution → 0.5g
├── Container 2 & 3 Load Cell
│   ├── Capacity → 5kg
│   ├── Sensitivity → 2mV/V
│   ├── Accuracy → ±0.02% FS
│   └── Resolution → 0.5g
└── Calibration Standards
    ├── Reference Masses → 100g, 500g, 1kg, 2kg
    ├── Calibration Frequency → Weekly
    └── Temperature Compensation → Automatic
```

## Wiring Specifications

### Wire Gauge Requirements
- **High Power (120V AC)**: 12 AWG THHN
- **Medium Power (12V DC)**: 14 AWG stranded
- **TEC Connections**: 12 AWG (high current)
- **Control Signals**: 22 AWG stranded
- **I2C/SPI**: 24 AWG twisted pair
- **Thermocouples**: Type T thermocouple extension wire
- **Load Cells**: 4-wire shielded cable
- **Heat Flux Sensors**: Coaxial cable (RG-58)

### Connector Types
- **AC Power**: NEMA 5-15 plugs and receptacles
- **DC Power**: Terminal blocks (5.08mm pitch)
- **Sensors**: Waterproof M12 connectors
- **Control**: Military-spec D-sub connectors
- **Safety**: Lockout/tagout compatible

### Grounding and EMI
- **Single Point Ground**: All grounds at power supply
- **Isolated Grounds**: Separate for precision measurements
- **Shielding**: All sensor cables properly shielded
- **Ferrite Cores**: On all switching power lines
- **EMI Filters**: On AC power inputs

## PCB Layout Considerations

### High-Current Traces
- **TEC Power**: 4oz copper, 5mm minimum width
- **Heater Control**: 2oz copper, 3mm minimum width
- **12V Distribution**: 2oz copper, 3mm minimum width
- **Ground Planes**: Solid copper pour with thermal vias

### Thermal Management
- **Power Components**: Thermal vias and heat sinks
- **Critical ICs**: Temperature monitoring
- **Component Spacing**: Adequate thermal isolation
- **Airflow**: Forced convection cooling

### Signal Integrity
- **Differential Pairs**: Matched impedance
- **Clock Routing**: Minimum crosstalk
- **Power Decoupling**: 100nF ceramic + 10µF tantalum
- **Ground Planes**: Continuous reference planes

## Testing and Calibration

### Initial System Test
1. **Power-on Test**: All voltage rails
2. **Communication Test**: I2C and SPI devices
3. **Sensor Test**: All temperature and mass readings
4. **Control Test**: TEC and heater operation
5. **Safety Test**: Emergency stop and interlocks

### Calibration Procedures
1. **Temperature Calibration**
   - Ice point: 0°C ± 0.1°C
   - Boiling point: 100°C ± 0.1°C
   - Melting point standards: Various PCM materials

2. **Mass Calibration**
   - Zero point: Unloaded containers
   - Span calibration: Certified reference masses
   - Linearity check: Multiple points

3. **Heat Flux Calibration**
   - Reference heat flux generator
   - Multiple flux levels
   - Temperature compensation

4. **Power Calibration**
   - Precision power analyzer
   - Multiple power levels
   - AC and DC measurements

### Performance Verification
1. **Phase Change Detection**: Known PCM materials
2. **Energy Storage Efficiency**: Calorimetry validation
3. **Response Time**: Step response tests
4. **Stability**: Long-term monitoring
5. **Repeatability**: Multiple test cycles

## Troubleshooting Guide

### Common Issues
1. **Thermocouple Errors**: Check connections and cold junction compensation
2. **Load Cell Drift**: Verify mechanical mounting and temperature stability
3. **Heat Flux Noise**: Check shielding and grounding
4. **Communication Failures**: Verify I2C addresses and bus integrity
5. **Power Supply Issues**: Check voltage regulation and current capacity

### Diagnostic Tools
- **Multimeter**: Basic electrical measurements
- **Oscilloscope**: Signal integrity analysis
- **Thermal Camera**: Temperature distribution
- **Power Analyzer**: Precision power measurements
- **Calorimeter**: Energy measurement validation

This comprehensive circuit diagram ensures precise PCM characterization, real-time phase change detection, and advanced thermal energy storage optimization capabilities.