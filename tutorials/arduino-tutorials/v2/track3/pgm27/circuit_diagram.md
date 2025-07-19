# Program 27: Injection Molding Controller - Circuit Diagram

## Overview
This document provides the complete electrical circuit design for the smart injection molding controller implementing scientific molding principles with real-time cavity pressure monitoring, SPC integration, and digital twin synchronization for precision plastic part manufacturing.

## System Architecture

### Main Controller Configuration
- **Primary Controller**: Arduino Mega 2560 (main process control)
- **High-Speed DAQ**: Arduino Due (1000 Hz data acquisition)
- **IoT Gateway**: ESP32 (digital twin synchronization)
- **Operating Voltage**: 24V DC industrial power supply
- **Control Voltage**: 5V/3.3V logic levels

## Power Supply System

### Primary Power Distribution
```
AC 240V Input
    │
    ├── Circuit Breaker (20A)
    │
    ├── EMC Filter
    │
    ├── Transformer (240V → 24V, 10A)
    │
    ├── Bridge Rectifier
    │
    ├── Filter Capacitors (4700µF)
    │
    └── 24V DC Bus
         │
         ├── Buck Converter → 12V (2A) → Heater Control
         ├── Buck Converter → 5V (3A) → Arduino Logic
         ├── LDO Regulator → 3.3V (1A) → ESP32 & Sensors
         └── Isolated DC-DC → 24V (1A) → Sensor Power
```

### Emergency Power Backup
```
24V Battery Backup System:
- 24V/5Ah Sealed Lead-Acid Battery
- Battery Monitoring IC (LTC2943)
- Automatic Switchover Circuit
- Low Battery Warning System
- Emergency Data Save Capability
```

## High-Pressure Measurement System

### Cavity Pressure Sensors (4 Channels)
```
Piezoelectric Pressure Transducers:
Model: Kistler 6157BA (0-2000 bar)
Power: +24V DC, 4-20mA output
Accuracy: ±0.5% Full Scale

Channel 1 - Cavity 1:
Sensor (+) ──── ADS1256 CH0+ (Pin 1)
Sensor (-) ──── ADS1256 CH0- (Pin 2)
Shield ──────── Analog Ground

Channel 2 - Cavity 2:
Sensor (+) ──── ADS1256 CH1+ (Pin 3)
Sensor (-) ──── ADS1256 CH1- (Pin 4)
Shield ──────── Analog Ground

Channel 3 - Cavity 3:
Sensor (+) ──── ADS1256 CH2+ (Pin 5)
Sensor (-) ──── ADS1256 CH2- (Pin 6)
Shield ──────── Analog Ground

Channel 4 - Cavity 4:
Sensor (+) ──── ADS1256 CH3+ (Pin 7)
Sensor (-) ──── ADS1256 CH3- (Pin 8)
Shield ──────── Analog Ground
```

### ADS1256 24-bit ADC Configuration
```
ADS1256 Pinout:
Pin 1-8:    Differential Input Channels
Pin 9:      AGND (Analog Ground)
Pin 10:     CLK (Clock Input from Arduino Due Pin 13)
Pin 11:     DIN (Data Input from Arduino Due Pin 11)
Pin 12:     DOUT (Data Output to Arduino Due Pin 12)
Pin 13:     CS (Chip Select from Arduino Due Pin 10)
Pin 14:     DRDY (Data Ready to Arduino Due Pin 9)
Pin 15:     RESET (Reset from Arduino Due Pin 8)
Pin 16:     DVDD (+5V Digital Supply)
Pin 17:     DGND (Digital Ground)
Pin 18:     AVDD (+5V Analog Supply with filtering)
Pin 19:     VREFP (+2.5V Precision Reference)
Pin 20:     VREFN (Analog Ground)

External Reference Circuit:
REF5025 (2.5V Precision Reference)
VIN ──── REF5025 ──── VREFP
         │
         0.1µF ──── AGND
         │
         10µF ──── AGND

Anti-Aliasing Filter (per channel):
Signal ──── 100Ω ──── 100nF ──── ADC Input
                │
                1kΩ ──── AGND
```

## Temperature Measurement System

### Multi-Zone Thermocouple Interface
```
MAX31855 Thermocouple Amplifiers (6 channels):

Channel 1 - Barrel Zone 1 (K-Type):
MAX31855_1:
Pin 1:      GND
Pin 2:      T- (Thermocouple Negative)
Pin 3:      T+ (Thermocouple Positive)
Pin 4:      VCC (+3.3V)
Pin 5:      SCK (Arduino Mega Pin 52)
Pin 6:      CS (Arduino Mega Pin 24)
Pin 7:      SO (Arduino Mega Pin 50)
Pin 8:      NC

Channel 2 - Barrel Zone 2:
MAX31855_2:
CS ──────── Arduino Mega Pin 25
[Other pins same as Channel 1]

Channel 3 - Barrel Zone 3:
MAX31855_3:
CS ──────── Arduino Mega Pin 26
[Other pins same as Channel 1]

Channel 4 - Nozzle Temperature:
MAX31855_4:
CS ──────── Arduino Mega Pin 27
[Other pins same as Channel 1]

Channel 5 - Mold Temperature:
MAX31855_5:
CS ──────── Arduino Mega Pin 28
[Other pins same as Channel 1]

Channel 6 - Ambient Temperature:
MAX31855_6:
CS ──────── Arduino Mega Pin 29
[Other pins same as Channel 1]
```

### Cold Junction Compensation
```
Isothermal Terminal Block:
- Copper block with thermal mass
- RTD temperature sensor (PT100)
- Thermoelectric cooling capability
- Maintains ±0.1°C stability
```

## Position Measurement System

### LVDT (Linear Variable Differential Transformer)
```
Screw Position LVDT:
Model: Solartron DP/2/S (±25mm range)

Primary Excitation:
Signal Generator IC (AD9833):
Pin 1:      COMP (NC)
Pin 2:      AGND
Pin 3:      DGND
Pin 4:      CLK (Arduino Mega Pin 30)
Pin 5:      FSYNC (Arduino Mega Pin 31)
Pin 6:      SDATA (Arduino Mega Pin 32)
Pin 7:      NC
Pin 8:      VDD (+3.3V)
Pin 9:      VOUT ──── Buffer Amplifier ──── LVDT Primary
Pin 10:     NC

Secondary Processing:
LVDT Secondary 1 ──── Instrumentation Amplifier (INA114)
LVDT Secondary 2 ──── Instrumentation Amplifier (INA114)
                 │
                 Phase-Sensitive Detector
                 │
                 Low-Pass Filter
                 │
                 Arduino Mega A0 (Position Signal)

Clamp Position (Potentiometric):
10kΩ Linear Potentiometer
Wiper ──── Arduino Mega A1
Supply: +5V to GND
```

## Control Output System

### Hydraulic Valve Control
```
Proportional Valve Driver Circuit:

Injection Velocity Control:
Arduino Mega Pin 5 (PWM) ──── Low-Pass Filter ──── Voltage Amplifier ──── Valve Coil
                         │
                         100Ω ──── 10µF ──── GND
                         │
                         Op-Amp Buffer (LM358)
                         │
                         Power Amplifier (TIP31C)
                         │
                         24V Supply

Pack/Hold Pressure Control:
Arduino Mega Pin 6 (PWM) ──── [Same circuit as above] ──── Valve Coil

Back Pressure Control:
Arduino Mega Pin 7 (PWM) ──── [Same circuit as above] ──── Valve Coil

Clamp Force Control:
Arduino Mega Pin 8 (PWM) ──── [Same circuit as above] ──── Valve Coil
```

### Heater Control System
```
Solid State Relay (SSR) Control:

Barrel Zone 1 Heater:
Arduino Mega Pin 9 ──── Current Limiting Resistor (330Ω) ──── SSR Input
                   │
                   Pull-down Resistor (10kΩ) ──── GND

SSR Output ──── 240V AC Heater Element (2kW)
            │
            Current Monitoring (ACS712-30A)
            │
            Arduino Mega A4 (Power Monitor)

Barrel Zone 2 Heater:
Arduino Mega Pin 10 ──── [Same circuit] ──── 240V AC Heater (2kW)

Barrel Zone 3 Heater:
Arduino Mega Pin 11 ──── [Same circuit] ──── 240V AC Heater (2kW)

Nozzle Heater:
Arduino Mega Pin 12 ──── [Same circuit] ──── 240V AC Heater (1kW)

Mold Heater:
Arduino Mega Pin 13 ──── [Same circuit] ──── 240V AC Heater (3kW)
```

### Ejection System Control
```
Pneumatic Ejection Control:
Arduino Mega Pin 23 ──── Solenoid Valve Driver ──── 24V Solenoid
                    │
                    Flyback Diode (1N4007)
                    │
                    MOSFET Driver (IRF540)
```

## Safety and Monitoring System

### Emergency Stop Circuit
```
Hardwired Emergency Stop:
E-Stop Button (NC) ──── Safety Relay (PILZ PNOZ s3) ──── Master Contactor
                   │
                   Force-Guided Contacts
                   │
                   All Heater SSRs (Disable)
                   │
                   All Hydraulic Valves (Safe Position)
                   │
                   Arduino Mega Pin 2 (Interrupt Input)

Safety Gates Monitoring:
Safety Gate 1 (NC) ──── Safety Input Module
Safety Gate 2 (NC) ──── Arduino Mega Pin 3
                   │
                   24V Safety Circuit
```

### Pressure Relief System
```
Automatic Pressure Relief:
Pressure Relief Valve:
Solenoid Control ──── Arduino Mega Pin 29
Pilot Valve ──── Hydraulic Pressure Relief
            │
            Set to 90% of Maximum Pressure
            │
            Manual Override Capability

Hydraulic Pressure Monitoring:
System Pressure Transducer (0-300 bar):
4-20mA Output ──── Precision Resistor (250Ω) ──── Arduino Mega A2
              │
              Isolation Amplifier (ISO124)
```

## Display and User Interface

### 7" TFT Touch Display
```
Adafruit ILI9341 TFT Display:
VCC ──── +3.3V
GND ──── Ground
CS ──── Arduino Mega Pin 30
RESET ──── Arduino Mega Pin 31
D/C ──── Arduino Mega Pin 32
MOSI ──── Arduino Mega Pin 51
SCK ──── Arduino Mega Pin 52
LED ──── +3.3V (via 100Ω resistor)
MISO ──── Arduino Mega Pin 50

XPT2046 Touch Controller:
T_IRQ ──── Arduino Mega Pin 34
T_DO ──── Arduino Mega Pin 50
T_DIN ──── Arduino Mega Pin 51
T_CS ──── Arduino Mega Pin 33
T_CLK ──── Arduino Mega Pin 52
```

### Status Indication System
```
LED Status Indicators:
System Ready (Green):
Arduino Mega Pin 26 ──── 330Ω ──── Green LED ──── GND

System Warning (Yellow):
Arduino Mega Pin 27 ──── 330Ω ──── Yellow LED ──── GND

System Fault (Red):
Arduino Mega Pin 28 ──── 330Ω ──── Red LED ──── GND

Audible Alarm:
Arduino Mega Pin 25 ──── Buzzer Driver ──── 24V Alarm Horn
                   │
                   MOSFET (IRF540)
                   │
                   Flyback Diode (1N4007)
```

## Communication Systems

### ESP32 IoT Gateway Interface
```
ESP32 DevKit V1:
GPIO 16 (RX2) ──── Arduino Mega Pin 16 (TX2)
GPIO 17 (TX2) ──── Arduino Mega Pin 17 (RX2)
GND ──── Common Ground
VIN ──── +5V Supply

ESP32 Status LEDs:
GPIO 2 ──── Status LED (Built-in)
GPIO 4 ──── Digital Twin LED
GPIO 5 ──── Cloud Connection LED
```

### Ethernet Communication
```
W5500 Ethernet Module:
VCC ──── +3.3V
GND ──── Ground
MOSI ──── Arduino Mega Pin 51
MISO ──── Arduino Mega Pin 50
SCK ──── Arduino Mega Pin 52
CS ──── Arduino Mega Pin 35
RST ──── Arduino Mega Pin 36
INT ──── Arduino Mega Pin 37
```

### Modbus RTU Interface
```
RS485 Transceiver (MAX485):
Pin 1 (RO) ──── Arduino Mega Pin 19 (RX1)
Pin 4 (DI) ──── Arduino Mega Pin 18 (TX1)
Pin 2 (RE) ──── Arduino Mega Pin 38 (Direction Control)
Pin 3 (DE) ──── Arduino Mega Pin 38 (Direction Control)
Pin 5 (GND) ──── Ground
Pin 8 (VCC) ──── +5V
Pin 6 (A) ──── RS485 A+ (to PLC)
Pin 7 (B) ──── RS485 B- (to PLC)

Termination Resistor: 120Ω between A+ and B-
```

## Data Storage System

### SD Card Module
```
SD Card Breakout:
VCC ──── +5V
GND ──── Ground
MISO ──── Arduino Mega Pin 50
MOSI ──── Arduino Mega Pin 51
SCK ──── Arduino Mega Pin 52
CS ──── Arduino Mega Pin 53

Card Detect ──── Arduino Mega Pin 39
Write Protect ──── Arduino Mega Pin 40
```

## Filtering and EMI Protection

### Power Line Filtering
```
EMC Input Filter:
L1 ──── Common Mode Choke ──── L1'
L2 ──── Common Mode Choke ──── L2'
    │                      │
    Differential Capacitor (220nF, X2)
    │                      │
    Common Mode Capacitors (2.2nF, Y2)
    │                      │
    PE ──── Earth Ground ──── PE
```

### Signal Conditioning
```
Analog Signal Filtering:
Each analog input includes:
- RC Low-pass filter (fc = 1kHz)
- TVS diode protection
- Ferrite bead on signal path
- Isolated ground plane

Digital Signal Protection:
- 33Ω series resistors on all digital I/O
- 5V zener diode clamps
- ESD protection diodes
```

## PCB Layout Considerations

### Layer Stack-up (4-layer PCB)
```
Layer 1: Component placement and signal routing
Layer 2: Ground plane (analog and digital sections)
Layer 3: Power plane (+5V, +3.3V, +24V)
Layer 4: Signal routing and additional ground
```

### Grounding Strategy
```
Star Ground Configuration:
- Separate analog and digital ground planes
- Single point connection at power supply
- Guard rings around high-precision analog circuits
- Isolated ground for pressure sensor circuits
```

### Thermal Management
```
Heat Dissipation:
- Thermal vias under power components
- Copper pour for heat spreading
- Forced air cooling for high-power sections
- Temperature monitoring (LM35DZ)
```

## Component Specifications

### Critical Components List
```
Microcontrollers:
- Arduino Mega 2560 R3
- Arduino Due R3
- ESP32 DevKit V1

Precision ADC:
- ADS1256 (24-bit, 30kSPS)
- REF5025 (2.5V precision reference)

Temperature Sensors:
- MAX31855 (6x thermocouple amplifiers)
- K-type thermocouples (6x)

Pressure Sensors:
- Kistler 6157BA (4x, 0-2000 bar)
- Anti-aliasing filters

Position Sensors:
- Solartron DP/2/S LVDT
- AD9833 signal generator
- INA114 instrumentation amplifier

Power Management:
- LM2596 buck converters (3x)
- LM1117 LDO regulators (2x)
- Isolated DC-DC converter

Control Outputs:
- Solid State Relays (5x, 25A)
- MOSFET drivers (10x, IRF540)
- Current sense amplifiers (ACS712)

Safety Components:
- PILZ PNOZ s3 safety relay
- Emergency stop button
- Safety light curtains interface
```

### Electrical Specifications
```
Power Requirements:
- Input: 240V AC, 50/60 Hz, 20A
- DC Bus: 24V, 10A continuous
- Logic Power: 5V/3A, 3.3V/1A
- Peak Power: 15kW (all heaters on)

Signal Specifications:
- Pressure: 4-20mA, 0-2000 bar
- Temperature: K-type, -50 to +400°C
- Position: ±10V differential, ±25mm
- Control: 0-10V, 4-20mA outputs

Performance Specifications:
- Pressure Accuracy: ±0.5% full scale
- Temperature Accuracy: ±1°C
- Position Accuracy: ±0.01mm
- Sampling Rate: 1000 Hz (pressure)
- Response Time: <10ms (control loops)
```

## Safety Compliance

### Safety Standards
```
Compliance Requirements:
- IEC 61508 (Functional Safety)
- ISO 13849 (Safety of Machinery)
- IEC 60204-1 (Electrical Equipment)
- UL 508A (Industrial Control Panels)
- CE Marking Requirements

Safety Integrity Level:
- SIL 2 for critical safety functions
- Category 3 safety circuits
- Diagnostic coverage >90%
```

### Protection Systems
```
Electrical Protection:
- Residual Current Device (RCD)
- Miniature Circuit Breakers (MCB)
- Surge Protection Devices (SPD)
- Isolation transformers

Mechanical Protection:
- IP65 enclosure rating
- Vibration isolation mounting
- Temperature monitoring
- Overpressure protection
```

## Installation Guidelines

### Enclosure Requirements
```
Industrial Enclosure:
- Material: 316 stainless steel
- Rating: IP65/NEMA 4X
- Dimensions: 800mm x 600mm x 300mm
- Ventilation: Forced air with filters
- Cable entries: IP68 glands

Mounting Configuration:
- DIN rail mounting for modules
- Shock mounts for vibration isolation
- Thermal management system
- Emergency access procedures
```

### Wiring Specifications
```
Cable Types:
- Power: VFD cable, 600V rating
- Signals: Instrumentation cable, shielded
- Communication: Cat6 Ethernet
- Safety: TUV approved safety cable

Wire Gauges:
- 240V Power: 12 AWG (heaters)
- 24V Power: 16 AWG (control)
- Signals: 20 AWG (sensors)
- Communications: 24 AWG (data)

Labeling System:
- Unique identifier for each wire
- Function description labels
- Color coding per standards
- Cable routing documentation
```

This comprehensive circuit diagram provides the complete electrical design for a professional-grade injection molding controller suitable for industrial manufacturing environments with full safety compliance and scientific molding capabilities.