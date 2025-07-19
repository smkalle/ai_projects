# Program 24: Nano-Indentation Controller - Circuit Diagram

## Overview
This circuit diagram details the complete wiring for a precision nano-indentation system capable of sub-micronewton force control and sub-nanometer displacement measurement for mechanical property characterization at the micro and nano-scale.

## Main Components Connection

### Arduino Due (High-Performance Controller)
```
Arduino Due (84 MHz ARM Cortex-M3)
├── Digital Pins
│   ├── Pin 2  → Piezo Drive PWM Output
│   ├── Pin 3  → Piezo Driver Enable
│   ├── Pin 4  → Load Cell Clock (HX711)
│   ├── Pin 5  → Load Cell Data (HX711)
│   ├── Pin 6  → Load Cell Gain Control
│   ├── Pin 7  → Displacement Sensor CS
│   ├── Pin 8  → Displacement Sensor Reset
│   ├── Pin 9  → Displacement Sensor Ready
│   ├── Pin 10 → X-Axis Stepper Step
│   ├── Pin 11 → X-Axis Stepper Direction
│   ├── Pin 12 → Y-Axis Stepper Step
│   ├── Pin 13 → Y-Axis Stepper Direction
│   ├── Pin 14 → Z-Axis Stepper Step
│   ├── Pin 15 → Z-Axis Stepper Direction
│   ├── Pin 16 → Stepper Motors Enable
│   ├── Pin 17 → Heater Control
│   ├── Pin 18 → Cooler Control
│   ├── Pin 19 → Fan Control
│   ├── Pin 20 → Camera Trigger
│   ├── Pin 21 → LED Illumination Control
│   ├── Pin 22 → Focus Motor Step
│   ├── Pin 23 → Focus Motor Direction
│   ├── Pin 24 → Emergency Stop Input
│   ├── Pin 25 → Start Button Input
│   ├── Pin 26 → Stop Button Input
│   ├── Pin 27 → Status LED Green
│   ├── Pin 28 → Status LED Red
│   ├── Pin 29 → Status LED Blue
│   ├── Pin 30 → Vibration Monitor
│   ├── Pin 31 → Safety Interlock
│   ├── Pin 32 → Overload Protection
│   ├── Pin 33 → Position Limit Switch
│   ├── Pin 34 → Microscope Control
│   ├── Pin 35 → Vacuum Control
│   ├── Pin 36 → Pressure Control
│   ├── Pin 37 → Spare Digital I/O
│   ├── Pin 38 → Spare Digital I/O
│   ├── Pin 39 → Spare Digital I/O
│   ├── Pin 40 → Spare Digital I/O
│   ├── Pin 41 → Spare Digital I/O
│   ├── Pin 42 → Spare Digital I/O
│   ├── Pin 43 → Spare Digital I/O
│   ├── Pin 44 → Spare Digital I/O
│   ├── Pin 45 → Spare Digital I/O
│   ├── Pin 46 → Spare Digital I/O
│   ├── Pin 47 → Spare Digital I/O
│   ├── Pin 48 → Spare Digital I/O
│   ├── Pin 49 → Spare Digital I/O
│   ├── Pin 50 → MISO (SPI)
│   ├── Pin 51 → MOSI (SPI)
│   ├── Pin 52 → SCK (SPI)
│   └── Pin 53 → SD Card CS
├── Analog Pins
│   ├── Pin A0 → Piezo Position Feedback
│   ├── Pin A1 → Temperature Sensor
│   ├── Pin A2 → Humidity Sensor
│   ├── Pin A3 → Vibration Monitor
│   ├── Pin A4 → Pressure Sensor
│   ├── Pin A5 → Vacuum Sensor
│   ├── Pin A6 → Strain Gauge Amplifier
│   ├── Pin A7 → Force Sensor Backup
│   ├── Pin A8 → Displacement Backup
│   ├── Pin A9 → Current Monitor
│   ├── Pin A10 → Voltage Monitor
│   └── Pin A11 → Spare Analog Input
├── I2C Bus
│   ├── Pin 20 → SDA (Environmental sensors)
│   └── Pin 21 → SCL (Environmental sensors)
├── Serial Communication
│   ├── Pin 0  → USB Debug/Programming
│   ├── Pin 1  → USB Debug/Programming
│   ├── Pin 14 → TX3 (ESP32 Communication)
│   ├── Pin 15 → RX3 (ESP32 Communication)
│   ├── Pin 16 → TX2 (GPS Communication)
│   ├── Pin 17 → RX2 (GPS Communication)
│   ├── Pin 18 → TX1 (Microscope Communication)
│   └── Pin 19 → RX1 (Microscope Communication)
└── Power
    ├── VIN → 12V DC Input
    ├── 5V → Logic Power
    ├── 3.3V → Sensor Power
    └── GND → Common Ground
```

## Force Measurement System

### High-Resolution Load Cell with HX711 Amplifier
```
Load Cell System
├── Load Cell (Sub-micronewton sensitivity)
│   ├── Type → Strain gauge load cell
│   ├── Capacity → 500 mN (500,000 μN)
│   ├── Sensitivity → 0.1 μN resolution
│   ├── Excitation → 5V DC
│   ├── Output → 0-10 mV full scale
│   ├── Temperature Compensation → Built-in
│   └── Mounting → Direct to indenter assembly
├── HX711 24-bit ADC
│   ├── Resolution → 24-bit (16.7 million counts)
│   ├── Sample Rate → 10-80 Hz selectable
│   ├── Gain → 32, 64, 128 selectable
│   ├── Interface → 2-wire serial
│   ├── Power → 5V DC
│   └── Noise → <1 LSB RMS
├── Signal Conditioning
│   ├── Pre-amplifier → Low-noise instrumentation amplifier
│   ├── Gain → 1000x (60 dB)
│   ├── Bandwidth → DC to 1 kHz
│   ├── Input Impedance → >10 MΩ
│   ├── CMRR → >100 dB
│   └── Drift → <1 μV/°C
├── Calibration System
│   ├── Reference Weights → 0.1, 0.5, 1, 5, 10 mN
│   ├── Piezoelectric Actuator → For dynamic calibration
│   ├── Electromagnetic Actuator → For static calibration
│   └── Laser Interferometer → For displacement calibration
└── Connections
    ├── CLK → Pin 4 (Clock signal)
    ├── DATA → Pin 5 (Data signal)
    ├── VCC → 5V regulated
    ├── GND → Analog ground
    └── RATE → Pin 6 (Sample rate control)
```

## Displacement Measurement System

### Capacitive Displacement Sensor
```
Displacement Sensor System
├── Capacitive Sensor
│   ├── Type → Differential capacitive sensor
│   ├── Range → 0-100 μm
│   ├── Resolution → 0.1 nm
│   ├── Linearity → ±0.01% of full scale
│   ├── Bandwidth → DC to 10 kHz
│   ├── Temperature Coefficient → <10 ppm/°C
│   └── Stability → <0.1 nm/hour
├── Signal Conditioning
│   ├── Carrier Frequency → 1 MHz
│   ├── Demodulator → Synchronous demodulator
│   ├── Filter → 8th order Butterworth
│   ├── Gain → Programmable 1x-1000x
│   ├── Output → ±10V full scale
│   └── Calibration → Digital calibration
├── Digital Interface
│   ├── Controller → 32-bit ARM processor
│   ├── ADC → 24-bit sigma-delta
│   ├── Interface → SPI at 10 MHz
│   ├── Update Rate → 1 kHz
│   └── Digital Filtering → 100x oversampling
├── Environmental Compensation
│   ├── Temperature → Built-in compensation
│   ├── Humidity → Sealed sensor head
│   ├── Vibration → Active isolation
│   └── Electromagnetic → Shielded electronics
└── Connections
    ├── CS → Pin 7 (Chip select)
    ├── RESET → Pin 8 (Reset signal)
    ├── READY → Pin 9 (Data ready)
    ├── SCLK → Pin 52 (SPI clock)
    ├── MOSI → Pin 51 (SPI data out)
    ├── MISO → Pin 50 (SPI data in)
    ├── VCC → 5V regulated
    └── GND → Analog ground
```

## Piezoelectric Actuator System

### High-Precision Piezoelectric Stack
```
Piezoelectric Actuator System
├── Piezo Stack Actuator
│   ├── Type → Multilayer piezoelectric stack
│   ├── Stroke → 0-15 μm
│   ├── Resolution → 0.1 nm
│   ├── Blocking Force → 1000 N
│   ├── Resonance Frequency → 20 kHz
│   ├── Hysteresis → <10% full scale
│   ├── Linearity → ±0.5% full scale
│   └── Operating Voltage → 0-150V
├── High-Voltage Amplifier
│   ├── Output Voltage → 0-150V
│   ├── Output Current → 0-100 mA
│   ├── Bandwidth → DC to 10 kHz
│   ├── Linearity → ±0.1%
│   ├── Noise → <1 mV RMS
│   ├── Stability → ±0.01% over 8 hours
│   └── Protection → Over-current, over-voltage
├── Position Feedback
│   ├── Sensor → Integrated strain gauge
│   ├── Sensitivity → 1000 μV/V/με
│   ├── Range → ±1000 με
│   ├── Bandwidth → DC to 10 kHz
│   ├── Amplifier → Instrumentation amplifier
│   └── Output → 0-10V
├── Control Interface
│   ├── Input → 0-10V from Arduino PWM
│   ├── PWM Filter → 3rd order low-pass
│   ├── Cutoff Frequency → 100 Hz
│   ├── Gain → 15x (0-10V to 0-150V)
│   └── Offset → Adjustable ±5V
└── Connections
    ├── Control Input → Pin 2 (PWM output)
    ├── Enable → Pin 3 (Enable/disable)
    ├── Position Feedback → Pin A0 (Analog input)
    ├── HV Output → Piezo stack positive
    ├── HV Ground → Piezo stack negative
    ├── Power → ±15V, +5V supplies
    └── Ground → System ground
```

## Sample Positioning System

### Precision Stepper Motor Stages
```
XYZ Positioning System
├── X-Axis Stage
│   ├── Stepper Motor → NEMA 17 with encoder
│   ├── Resolution → 0.1 μm per step
│   ├── Travel → 25 mm
│   ├── Accuracy → ±0.5 μm
│   ├── Repeatability → ±0.1 μm
│   ├── Speed → 0.1-10 mm/s
│   └── Load Capacity → 5 kg
├── Y-Axis Stage
│   ├── Same specifications as X-axis
│   ├── Perpendicular to X-axis
│   └── Orthogonal accuracy → ±5 arcseconds
├── Z-Axis Stage (Coarse positioning)
│   ├── Stepper Motor → NEMA 17 with encoder
│   ├── Resolution → 0.1 μm per step
│   ├── Travel → 12 mm
│   ├── Accuracy → ±1 μm
│   ├── Speed → 0.05-5 mm/s
│   └── Load Capacity → 2 kg
├── Stepper Motor Drivers
│   ├── Type → Microstepping drivers
│   ├── Microsteps → 256 microsteps/step
│   ├── Current → 2A per phase
│   ├── Voltage → 24V supply
│   ├── Control → Step/direction interface
│   └── Features → Current reduction, decay control
├── Encoders
│   ├── Type → Optical rotary encoders
│   ├── Resolution → 4000 PPR
│   ├── Interface → Quadrature TTL
│   ├── Accuracy → ±5 arcseconds
│   └── Max Speed → 6000 RPM
└── Connections
    ├── X-Axis Step → Pin 10
    ├── X-Axis Direction → Pin 11
    ├── Y-Axis Step → Pin 12
    ├── Y-Axis Direction → Pin 13
    ├── Z-Axis Step → Pin 14
    ├── Z-Axis Direction → Pin 15
    ├── Enable → Pin 16 (Common enable)
    ├── Power → 24V regulated
    └── Ground → System ground
```

## Optical Microscope System

### Integrated Microscope with Digital Camera
```
Optical System
├── Microscope
│   ├── Type → Inverted metallurgical microscope
│   ├── Magnification → 50x-1000x
│   ├── Objectives → 5x, 10x, 20x, 50x, 100x
│   ├── Working Distance → 3-15 mm
│   ├── Resolution → 0.5 μm
│   ├── Field of View → 0.2-2 mm
│   └── Illumination → LED with intensity control
├── Digital Camera
│   ├── Sensor → 5 MP CMOS
│   ├── Pixel Size → 2.2 μm
│   ├── Frame Rate → 30 fps
│   ├── Interface → USB 3.0
│   ├── Trigger → External trigger input
│   └── Software → Real-time image processing
├── Focus Motor
│   ├── Type → Stepper motor with encoder
│   ├── Resolution → 0.1 μm per step
│   ├── Travel → 5 mm
│   ├── Speed → 0.01-1 mm/s
│   └── Accuracy → ±0.5 μm
├── Illumination Control
│   ├── LED Array → White LED array
│   ├── Power → 0-10W variable
│   ├── Control → PWM intensity control
│   ├── Uniformity → ±5% across field
│   └── Stability → ±1% over 8 hours
└── Connections
    ├── Camera Trigger → Pin 20
    ├── Illumination Control → Pin 21
    ├── Focus Step → Pin 22
    ├── Focus Direction → Pin 23
    ├── USB Camera → Computer interface
    ├── Power → 12V supply
    └── Ground → System ground
```

## Environmental Control System

### Temperature and Humidity Control
```
Environmental Control
├── Temperature Control
│   ├── Sensor → PT100 RTD
│   ├── Range → 0-100°C
│   ├── Accuracy → ±0.1°C
│   ├── Stability → ±0.05°C
│   ├── Response Time → 10 seconds
│   └── Location → Sample chamber
├── Humidity Control
│   ├── Sensor → Capacitive humidity sensor
│   ├── Range → 0-100% RH
│   ├── Accuracy → ±2% RH
│   ├── Stability → ±1% RH
│   ├── Response Time → 30 seconds
│   └── Location → Sample chamber
├── Heating System
│   ├── Heater → Ceramic heater element
│   ├── Power → 50W
│   ├── Control → PWM control
│   ├── Temperature Range → 25-80°C
│   └── Safety → Over-temperature protection
├── Cooling System
│   ├── Cooler → Peltier cooler
│   ├── Capacity → 30W at ΔT=20°C
│   ├── Control → PWM control
│   ├── Temperature Range → 10-25°C
│   └── Heat Sink → Forced air cooling
├── Air Circulation
│   ├── Fan → 12V brushless fan
│   ├── Airflow → 10 CFM
│   ├── Control → PWM speed control
│   ├── Noise → <30 dB(A)
│   └── Filter → HEPA filter
└── Connections
    ├── Temperature Sensor → Pin A1
    ├── Humidity Sensor → Pin A2
    ├── Heater Control → Pin 17
    ├── Cooler Control → Pin 18
    ├── Fan Control → Pin 19
    ├── Power → 12V supply
    └── Ground → System ground
```

## Vibration Isolation System

### Active Vibration Isolation
```
Vibration Isolation
├── Vibration Monitoring
│   ├── Accelerometer → 3-axis MEMS accelerometer
│   ├── Sensitivity → 1000 mV/g
│   ├── Frequency Range → 0.1-1000 Hz
│   ├── Noise → <10 μg/√Hz
│   ├── Dynamic Range → ±50 g
│   └── Interface → Analog output
├── Isolation Platform
│   ├── Type → Pneumatic isolation table
│   ├── Isolation → >90% at >5 Hz
│   ├── Resonance → 1-2 Hz
│   ├── Payload → 100 kg
│   ├── Control → Active feedback control
│   └── Settling Time → <30 seconds
├── Active Control
│   ├── Sensors → Piezoelectric accelerometers
│   ├── Actuators → Piezoelectric actuators
│   ├── Controller → DSP-based controller
│   ├── Bandwidth → 0.1-100 Hz
│   ├── Attenuation → >20 dB
│   └── Power → 24V supply
└── Connections
    ├── Vibration Monitor → Pin A3
    ├── Control Output → Pin 30
    ├── Power → 24V supply
    └── Ground → System ground
```

## Power Distribution System

### Multi-Rail Power Supply
```
Power Distribution
├── Primary Power (120/240V AC)
│   ├── Input → 120/240V AC, 50/60Hz
│   ├── Protection → Circuit breaker, surge protection
│   ├── Isolation → Isolation transformer
│   └── Grounding → Safety ground
├── +24V Supply (High current)
│   ├── Type → Switching power supply
│   ├── Output → 24V DC @ 10A
│   ├── Regulation → ±1%
│   ├── Ripple → <50 mV p-p
│   ├── Efficiency → >90%
│   └── Use → Stepper motors, heaters
├── +150V Supply (Piezo driver)
│   ├── Type → High-voltage switching supply
│   ├── Output → 150V DC @ 0.5A
│   ├── Regulation → ±0.1%
│   ├── Ripple → <10 mV p-p
│   ├── Isolation → 2kV isolation
│   └── Use → Piezoelectric actuator
├── ±15V Supply (Analog)
│   ├── Type → Linear regulated supply
│   ├── Output → ±15V @ 2A
│   ├── Regulation → ±0.01%
│   ├── Noise → <100 μV RMS
│   ├── PSRR → >80 dB
│   └── Use → Analog amplifiers
├── +12V Supply (General)
│   ├── Type → Switching power supply
│   ├── Output → 12V DC @ 5A
│   ├── Regulation → ±2%
│   ├── Ripple → <100 mV p-p
│   ├── Efficiency → >85%
│   └── Use → Fans, lighting, Arduino
├── +5V Supply (Logic)
│   ├── Type → Buck converter from 12V
│   ├── Output → 5V DC @ 3A
│   ├── Regulation → ±2%
│   ├── Ripple → <50 mV p-p
│   ├── Efficiency → >90%
│   └── Use → Digital logic, sensors
├── +3.3V Supply (Low voltage)
│   ├── Type → LDO from 5V
│   ├── Output → 3.3V DC @ 1A
│   ├── Regulation → ±1%
│   ├── Noise → <20 μV RMS
│   ├── Dropout → <200 mV
│   └── Use → Microcontroller, sensors
└── Power Monitoring
    ├── Voltage Monitor → Pin A10
    ├── Current Monitor → Pin A9
    ├── Power Factor → Calculated
    ├── Energy Meter → Accumulated energy
    └── Alarms → Over/under voltage
```

## Safety and Protection Systems

### Comprehensive Safety System
```
Safety Systems
├── Emergency Stop
│   ├── Button → Red mushroom button
│   ├── Contacts → 2 NC contacts
│   ├── Response → <1 second
│   ├── Action → All motion stops
│   └── Reset → Manual reset required
├── Overload Protection
│   ├── Force Limit → 500 mN maximum
│   ├── Displacement Limit → 100 μm maximum
│   ├── Response → <10 ms
│   ├── Action → Immediate retraction
│   └── Indication → LED and alarm
├── Position Limits
│   ├── Limit Switches → Optical limit switches
│   ├── Software Limits → Programmable limits
│   ├── Hard Stops → Mechanical stops
│   ├── Response → Immediate stop
│   └── Recovery → Manual reset
├── Temperature Protection
│   ├── Sensor → PT100 RTD
│   ├── Limit → 60°C maximum
│   ├── Response → <5 seconds
│   ├── Action → Cooling activation
│   └── Shutdown → At 80°C
├── Interlocks
│   ├── Door Switches → Magnetic switches
│   ├── Cover Switches → Limit switches
│   ├── Light Curtains → Safety light curtains
│   ├── Response → <100 ms
│   └── Action → Motion disable
└── Connections
    ├── Emergency Stop → Pin 24
    ├── Overload Protection → Pin 32
    ├── Position Limits → Pin 33
    ├── Safety Interlock → Pin 31
    ├── Temperature Monitor → Pin A1
    ├── Power → 24V supply
    └── Ground → Safety ground
```

## Data Acquisition and Storage

### High-Speed Data Acquisition
```
Data Acquisition System
├── SD Card Storage
│   ├── Interface → SPI
│   ├── Capacity → 32GB SDHC
│   ├── Speed → Class 10 (10 MB/s)
│   ├── Format → FAT32
│   ├── Files → CSV, JSON, binary
│   └── Backup → Automatic backup
├── Real-Time Clock
│   ├── IC → DS3231 RTC
│   ├── Accuracy → ±2 ppm
│   ├── Battery → CR2032 backup
│   ├── Interface → I2C
│   └── Features → Temperature compensation
├── USB Interface
│   ├── Type → USB 2.0
│   ├── Speed → 480 Mbps
│   ├── Functions → Programming, data transfer
│   ├── Power → Bus powered
│   └── Drivers → Standard CDC/ACM
├── Ethernet Interface
│   ├── Speed → 100 Mbps
│   ├── Connector → RJ45
│   ├── Protocols → TCP/IP, HTTP, FTP
│   ├── Features → Web interface
│   └── Security → WPA2 encryption
└── Connections
    ├── SD Card CS → Pin 53
    ├── SPI Bus → Pins 50-52
    ├── I2C Bus → Pins 20-21
    ├── USB → Native USB port
    └── Ethernet → Via shield
```

## Communication Interfaces

### Multi-Protocol Communication
```
Communication System
├── ESP32 IoT Gateway
│   ├── Interface → Serial UART
│   ├── Baud Rate → 115200 bps
│   ├── Protocol → JSON messages
│   ├── Functions → WiFi, Bluetooth, cloud
│   └── Features → OTA updates
├── GPS Module
│   ├── Interface → Serial UART
│   ├── Baud Rate → 9600 bps
│   ├── Protocol → NMEA 0183
│   ├── Accuracy → 2.5m CEP
│   └── Features → Time synchronization
├── Microscope Interface
│   ├── Interface → Serial UART
│   ├── Baud Rate → 19200 bps
│   ├── Protocol → Proprietary
│   ├── Functions → Focus, illumination
│   └── Features → Image capture
├── USB Debug Interface
│   ├── Interface → Native USB
│   ├── Speed → 12 Mbps
│   ├── Functions → Programming, debug
│   ├── Drivers → Standard CDC
│   └── Features → Real-time monitoring
└── Connections
    ├── ESP32 → Pins 14-15 (Serial1)
    ├── GPS → Pins 16-17 (Serial2)
    ├── Microscope → Pins 18-19 (Serial3)
    └── USB → Native USB connector
```

## Grounding and EMI Protection

### Comprehensive Grounding System
```
Grounding Architecture
├── Safety Ground
│   ├── Connection → Earth ground rod
│   ├── Resistance → <1 Ω
│   ├── Bonding → All metal parts
│   ├── Continuity → Verified annually
│   └── Isolation → Signal isolation
├── Analog Ground
│   ├── Plane → Separate ground plane
│   ├── Connection → Star point connection
│   ├── Isolation → Opto-isolators
│   ├── Noise → <1 μV RMS
│   └── Stability → <1 μV drift
├── Digital Ground
│   ├── Plane → Digital ground plane
│   ├── Separation → From analog ground
│   ├── Connection → Single point
│   ├── Switching → Isolated switching
│   └── Filtering → Ferrite beads
├── Power Ground
│   ├── Connection → Power supply ground
│   ├── Distribution → Wide traces
│   ├── Filtering → Bypass capacitors
│   ├── Regulation → Voltage regulation
│   └── Protection → Surge protection
└── Shield Ground
    ├── Cables → Cable shields
    ├── Enclosures → Conductive enclosures
    ├── Penetrations → Filtered penetrations
    └── Termination → 360° termination
```

## Installation and Testing

### Installation Requirements
1. **Environmental Conditions**
   - Temperature: 20°C ±2°C
   - Humidity: 45-55% RH
   - Vibration: <1 μm displacement
   - Electromagnetic interference: <1 V/m

2. **Power Requirements**
   - AC Input: 120/240V ±10%
   - Frequency: 50/60Hz ±1%
   - Power: 500W maximum
   - Ground: <1Ω earth ground

3. **Space Requirements**
   - Footprint: 1m × 1m minimum
   - Height: 1.5m minimum
   - Access: 0.5m clearance all sides
   - Ventilation: 100 CFM minimum

### Testing and Calibration
1. **System Testing**
   - Power-on self-test
   - Sensor calibration
   - Actuator calibration
   - Safety system testing
   - Performance verification

2. **Calibration Standards**
   - Force: NIST traceable weights
   - Displacement: Laser interferometer
   - Temperature: Certified RTD
   - Humidity: Saturated salt solutions

3. **Performance Verification**
   - Force accuracy: ±0.5% of reading
   - Displacement accuracy: ±0.1% of reading
   - Temperature stability: ±0.1°C
   - Vibration isolation: >90% above 5 Hz

This comprehensive circuit diagram ensures proper implementation of the nano-indentation system with professional-grade precision, safety, and reliability for advanced materials characterization.