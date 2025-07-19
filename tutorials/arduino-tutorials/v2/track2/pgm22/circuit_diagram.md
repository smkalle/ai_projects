# Program 22: Environmental Test Chamber - Circuit Diagram

## Overview
This circuit diagram shows the complete wiring for a professional environmental test chamber with precise temperature, humidity, and UV exposure control for accelerated life testing (ALT), HALT, and HASS procedures.

## Main Components Connection

### Arduino Mega 2560 (Main Controller)
```
Arduino Mega 2560
├── Digital Pins
│   ├── Pin 2  → DS18B20 Temperature Sensor (OneWire)
│   ├── Pin 3  → DHT22 Humidity Sensor (Data)
│   ├── Pin 4  → Peltier Hot Side Control (PWM)
│   ├── Pin 5  → Peltier Cold Side Control (PWM)
│   ├── Pin 6  → Intake Fan Control (PWM)
│   ├── Pin 7  → Exhaust Fan Control (PWM)
│   ├── Pin 8  → Humidifier Control (PWM)
│   ├── Pin 9  → Dehumidifier Control (PWM)
│   ├── Pin 10 → UV-A LED Array Control (PWM)
│   ├── Pin 11 → UV-B LED Array Control (PWM)
│   ├── Pin 12 → Resistive Heater Control (PWM)
│   ├── Pin 13 → Cooler Control (PWM)
│   ├── Pin 14 → Water Pump Control
│   ├── Pin 15 → Drain Valve Control
│   ├── Pin 16 → Spare Output
│   ├── Pin 17 → Spare Output
│   ├── Pin 18 → Door Interlock Switch (Interrupt)
│   ├── Pin 19 → Emergency Stop Button (Interrupt)
│   ├── Pin 20 → UV Safety Interlock (Interrupt)
│   ├── Pin 21 → Over Temperature Alarm (Interrupt)
│   ├── Pin 22 → Water Level Sensor
│   ├── Pin 23 → Condensate Level Sensor
│   ├── Pin 24 → Tower Light Red
│   ├── Pin 25 → Tower Light Yellow
│   ├── Pin 26 → Tower Light Green
│   ├── Pin 27 → Alarm Buzzer
│   ├── Pin 28 → Circulation Fan 1
│   ├── Pin 29 → Circulation Fan 2
│   ├── Pin 30 → Air Filter Monitor
│   ├── Pin 31 → Pressure Relief Valve
│   ├── Pin 32 → Nitrogen Purge Valve
│   ├── Pin 33 → Sample Holder Light
│   ├── Pin 34 → Chamber Light
│   ├── Pin 35 → Spare Digital Output
│   ├── Pin 36 → Spare Digital Output
│   ├── Pin 37 → Spare Digital Output
│   ├── Pin 38 → TFT Display RS
│   ├── Pin 39 → TFT Display WR
│   ├── Pin 40 → TFT Display CS
│   ├── Pin 41 → TFT Display RST
│   ├── Pin 42 → TFT Display RD
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
│   ├── Pin A0 → UV Irradiance Sensor
│   ├── Pin A1 → Pressure Sensor
│   ├── Pin A2 → Airflow Sensor
│   ├── Pin A3 → Coolant Temperature
│   ├── Pin A4 → Spare Analog Input
│   ├── Pin A5 → Spare Analog Input
│   ├── Pin A6 → Touch Screen X
│   ├── Pin A7 → Touch Screen Y
│   ├── Pin A8 → Current Monitor 1
│   ├── Pin A9 → Current Monitor 2
│   ├── Pin A10 → Voltage Monitor
│   ├── Pin A11 → Spare Analog Input
│   ├── Pin A12 → Spare Analog Input
│   ├── Pin A13 → Spare Analog Input
│   ├── Pin A14 → Spare Analog Input
│   └── Pin A15 → Spare Analog Input
├── I2C Bus
│   ├── Pin 20 → SDA (BME680, LCD)
│   └── Pin 21 → SCL (BME680, LCD)
├── Communication
│   ├── Pin 0  → RX (USB/Debug)
│   ├── Pin 1  → TX (USB/Debug)
│   ├── Pin 14 → TX3 (ESP32 communication)
│   └── Pin 15 → RX3 (ESP32 communication)
└── Power
    ├── VIN → 12V DC Input
    ├── 5V → Logic Level Power
    ├── 3.3V → Sensor Power
    └── GND → Common Ground
```

## Temperature Control System

### Peltier Module Array (4x TEC1-12706)
```
Peltier Module Configuration
├── Module 1 (Hot Side)
│   ├── Positive → MOSFET Q1 Drain
│   ├── Negative → Common Hot Rail
│   ├── Power → 12V, 6A
│   └── Control → Pin 4 (PWM)
├── Module 2 (Cold Side)
│   ├── Positive → MOSFET Q2 Drain
│   ├── Negative → Common Cold Rail
│   ├── Power → 12V, 6A
│   └── Control → Pin 5 (PWM)
├── Module 3 (Heating Element)
│   ├── Type → Resistive heater
│   ├── Power → 24V, 100W
│   ├── Control → SSR via Pin 12
│   └── Temperature → Monitored by DS18B20
└── Module 4 (Cooling Element)
    ├── Type → Forced air cooler
    ├── Power → 12V, 50W
    ├── Control → PWM via Pin 13
    └── Airflow → Monitored by sensor
```

### Temperature Sensors
```
Temperature Sensor Array
├── DS18B20 Primary (Pin 2)
│   ├── Resolution → 12-bit (0.0625°C)
│   ├── Accuracy → ±0.5°C
│   ├── Range → -55°C to +125°C
│   ├── Location → Chamber center
│   └── Wiring → OneWire bus
├── DS18B20 Secondary (Pin 2)
│   ├── Address → 0x28123456789A
│   ├── Location → Chamber wall
│   └── Backup → Redundant measurement
├── BME680 Environmental (I2C)
│   ├── Temperature → -40°C to +85°C
│   ├── Humidity → 0-100% RH
│   ├── Pressure → 300-1100 hPa
│   ├── Gas → VOC detection
│   └── Address → 0x77
└── Thermocouple (Type K)
    ├── Range → -200°C to +1350°C
    ├── Amplifier → MAX31855
    ├── Interface → SPI
    └── Use → High temperature monitoring
```

### MOSFET Drivers for Peltier Control
```
MOSFET Driver Circuit
├── Q1 (Hot Side Control)
│   ├── MOSFET → IRF540N (100V, 33A)
│   ├── Gate → Pin 4 via 10Ω resistor
│   ├── Drain → Peltier hot side
│   ├── Source → Ground
│   ├── Gate Protection → 12V Zener
│   └── Flyback Diode → Schottky diode
├── Q2 (Cold Side Control)
│   ├── MOSFET → IRF540N (100V, 33A)
│   ├── Gate → Pin 5 via 10Ω resistor
│   ├── Drain → Peltier cold side
│   ├── Source → Ground
│   ├── Gate Protection → 12V Zener
│   └── Flyback Diode → Schottky diode
├── Heat Sinks
│   ├── MOSFETs → TO-220 heat sinks
│   ├── Peltiers → Aluminum heat sinks
│   ├── Thermal Paste → Applied to all interfaces
│   └── Cooling → Forced air circulation
└── Current Sensing
    ├── Shunt Resistor → 0.1Ω, 5W
    ├── Amplifier → INA219
    ├── Interface → I2C
    └── Monitoring → Over-current protection
```

## Humidity Control System

### DHT22 Humidity Sensor
```
DHT22 Humidity Sensor
├── Power Supply
│   ├── VCC → 3.3V
│   ├── GND → Ground
│   └── Current → 2.5mA
├── Digital Interface
│   ├── Data → Pin 3
│   ├── Pull-up → 10kΩ to VCC
│   └── Protocol → Single-wire digital
├── Specifications
│   ├── Humidity → 0-100% RH
│   ├── Accuracy → ±2% RH
│   ├── Temperature → -40°C to +80°C
│   ├── Accuracy → ±0.5°C
│   └── Resolution → 0.1% RH, 0.1°C
└── Calibration
    ├── Reference → Certified RH standards
    ├── Points → 11%, 33%, 75%, 95% RH
    └── Frequency → Monthly calibration
```

### Humidification System
```
Humidification System
├── Ultrasonic Humidifier
│   ├── Power → 24V, 35W
│   ├── Control → PWM via Pin 8
│   ├── Output → 350ml/hour
│   ├── Particle Size → 1-5μm
│   └── Water Quality → Distilled water
├── Water Reservoir
│   ├── Capacity → 2 liters
│   ├── Level Sensor → Float switch
│   ├── Low Level → Pin 22
│   ├── Refill → Automatic pump
│   └── Filtration → Activated carbon
├── Distribution System
│   ├── Manifold → PVC distribution
│   ├── Nozzles → 4x spray nozzles
│   ├── Circulation → Forced air mixing
│   └── Drainage → Condensate collection
└── Water Pump
    ├── Type → Diaphragm pump
    ├── Power → 12V, 1A
    ├── Control → Pin 14
    ├── Flow Rate → 2 L/min
    └── Pressure → 2 bar
```

### Dehumidification System
```
Dehumidification System
├── Peltier Dehumidifier
│   ├── Power → 12V, 60W
│   ├── Control → PWM via Pin 9
│   ├── Cooling → Cold side condensation
│   ├── Capacity → 400ml/day
│   └── Efficiency → 80% at 60% RH
├── Condensate Management
│   ├── Collection → Drain pan
│   ├── Level Sensor → Pin 23
│   ├── Drain Valve → Solenoid valve
│   ├── Control → Pin 15
│   └── Overflow → Safety drain
├── Desiccant Backup
│   ├── Material → Silica gel
│   ├── Capacity → 500g
│   ├── Regeneration → Heating element
│   └── Control → Temperature cycling
└── Air Circulation
    ├── Fan → 12V, 2A
    ├── Airflow → 50 CFM
    ├── Filter → HEPA filter
    └── Monitoring → Airflow sensor
```

## UV Exposure System

### UV LED Arrays
```
UV LED Array System
├── UV-A Array (365nm)
│   ├── LEDs → 50x high-power LEDs
│   ├── Power → 50W total
│   ├── Control → PWM via Pin 10
│   ├── Irradiance → 0-1000 W/m²
│   ├── Uniformity → ±5% across chamber
│   └── Cooling → Forced air + heat sink
├── UV-B Array (280nm)
│   ├── LEDs → 20x high-power LEDs
│   ├── Power → 20W total
│   ├── Control → PWM via Pin 11
│   ├── Irradiance → 0-400 W/m²
│   ├── Uniformity → ±10% across chamber
│   └── Cooling → Forced air + heat sink
├── Power Supply
│   ├── Voltage → 24V constant current
│   ├── Current → 2A per array
│   ├── Regulation → ±1%
│   └── Protection → Over-temperature shutdown
└── Monitoring
    ├── UV Sensor → PIN photodiode
    ├── Range → 280-400nm
    ├── Calibration → NIST traceable
    └── Feedback → Closed-loop control
```

### UV Safety System
```
UV Safety Interlocks
├── Door Interlock
│   ├── Switch → Magnetic reed switch
│   ├── Input → Pin 18
│   ├── Logic → NC contact
│   └── Action → Immediate UV shutdown
├── UV Shutter
│   ├── Type → Motorized shutter
│   ├── Control → Stepper motor
│   ├── Position → Optical encoder
│   └── Response → <1 second close
├── Warning System
│   ├── LED → UV warning light
│   ├── Sign → "UV EXPOSURE ACTIVE"
│   ├── Audible → Beeping alarm
│   └── Duration → 10 seconds before exposure
├── Personnel Protection
│   ├── Viewing Window → UV-blocking glass
│   ├── Seals → UV-proof gaskets
│   ├── Ventilation → Exhaust system
│   └── Monitoring → UV leak detection
└── Emergency Stop
    ├── Button → Big red mushroom
    ├── Input → Pin 19
    ├── Action → All systems shutdown
    └── Reset → Manual reset required
```

## Ventilation and Air Management

### Fan System
```
Air Circulation System
├── Intake Fan (Pin 6)
│   ├── Type → 12V brushless fan
│   ├── Power → 12V, 1A
│   ├── Airflow → 50 CFM
│   ├── Control → PWM speed control
│   └── Filter → HEPA filter
├── Exhaust Fan (Pin 7)
│   ├── Type → 12V brushless fan
│   ├── Power → 12V, 1A
│   ├── Airflow → 60 CFM
│   ├── Control → PWM speed control
│   └── Filter → Activated carbon
├── Circulation Fans (Pins 28, 29)
│   ├── Type → Internal mixing fans
│   ├── Power → 12V, 0.5A each
│   ├── Airflow → 25 CFM each
│   ├── Position → Chamber corners
│   └── Purpose → Uniform mixing
└── Pressure Management
    ├── Pressure Sensor → Pin A1
    ├── Range → -1000 to +1000 Pa
    ├── Control → Fan speed adjustment
    └── Safety → Pressure relief valve
```

### Air Quality Monitoring
```
Air Quality System
├── Airflow Sensor (Pin A2)
│   ├── Type → Thermal mass flow sensor
│   ├── Range → 0-100 CFM
│   ├── Accuracy → ±2% of reading
│   └── Output → 4-20mA
├── Pressure Sensor (Pin A1)
│   ├── Type → Differential pressure
│   ├── Range → ±2000 Pa
│   ├── Accuracy → ±0.1% FS
│   └── Interface → Analog 0-5V
├── Gas Detection
│   ├── Sensor → BME680 (VOC)
│   ├── Range → 0-500 IAQ index
│   ├── Response → Real-time
│   └── Alarm → High gas levels
└── Filter Monitoring
    ├── Differential Pressure → Across filters
    ├── Replacement → Based on pressure drop
    ├── Indicator → Visual and digital
    └── Logging → Filter life tracking
```

## Environmental Monitoring

### BME680 Environmental Sensor
```
BME680 Sensor Module
├── Power Supply
│   ├── VCC → 3.3V
│   ├── GND → Ground
│   └── Current → 3.7mA
├── I2C Interface
│   ├── SDA → Pin 20
│   ├── SCL → Pin 21
│   ├── Address → 0x77
│   └── Clock → 400kHz
├── Measurements
│   ├── Temperature → -40°C to +85°C
│   ├── Humidity → 0-100% RH
│   ├── Pressure → 300-1100 hPa
│   ├── Gas → VOC detection
│   └── Altitude → Calculated
├── Accuracy
│   ├── Temperature → ±1°C
│   ├── Humidity → ±3% RH
│   ├── Pressure → ±1 hPa
│   └── Gas → Qualitative
└── Calibration
    ├── Factory → Pre-calibrated
    ├── Field → User calibration
    └── Frequency → Annual
```

### UV Irradiance Sensor
```
UV Irradiance Measurement
├── Photodiode Sensor
│   ├── Type → PIN photodiode
│   ├── Spectral Range → 280-400nm
│   ├── Peak Response → 365nm
│   ├── Active Area → 7.5mm²
│   └── Responsivity → 0.2 A/W
├── Signal Conditioning
│   ├── Transimpedance → 10MΩ feedback
│   ├── Amplifier → Low-noise op-amp
│   ├── Filter → 1Hz lowpass
│   └── Output → 0-5V
├── Calibration
│   ├── Reference → NIST traceable
│   ├── Standard → UV-A lamp
│   ├── Points → 0, 250, 500, 750, 1000 W/m²
│   └── Frequency → Semi-annual
└── Temperature Compensation
    ├── Coefficient → -0.1%/°C
    ├── Sensor → Integrated thermistor
    └── Correction → Automatic
```

## Data Logging and Display

### SD Card Module
```
SD Card Data Logger
├── Interface → SPI
├── Connections
│   ├── CS → Pin 53
│   ├── MOSI → Pin 51
│   ├── MISO → Pin 50
│   ├── SCK → Pin 52
│   └── VCC → 5V
├── Card Specifications
│   ├── Type → SDHC
│   ├── Capacity → 32GB
│   ├── Speed → Class 10
│   └── Format → FAT32
├── File Structure
│   ├── /DATA/ → Environmental data
│   ├── /PROFILES/ → Test profiles
│   ├── /REPORTS/ → Test reports
│   └── /CONFIG/ → System configuration
└── Data Format
    ├── Timestamp → ISO 8601
    ├── Delimiter → Comma separated
    ├── Precision → 2 decimal places
    └── Backup → Automatic
```

### 7" TFT Display
```
TFT Display System
├── Display Module
│   ├── Size → 7 inches
│   ├── Resolution → 800x480
│   ├── Controller → SSD1963
│   ├── Colors → 65K (16-bit)
│   └── Backlight → LED
├── Interface
│   ├── Data → 16-bit parallel
│   ├── Control → Pins 38-42
│   ├── Touch → Resistive 4-wire
│   └── Power → 5V, 500mA
├── Touch Screen
│   ├── Type → Resistive
│   ├── Pressure → 80g activation
│   ├── Accuracy → ±2mm
│   └── Calibration → 5-point
└── Graphics
    ├── Fonts → Multiple sizes
    ├── Colors → Full palette
    ├── Graphs → Real-time plots
    └── Images → Bitmap support
```

## ESP32 IoT Gateway

### ESP32 DevKit Connection
```
ESP32 DevKit V1
├── Power
│   ├── VIN → 5V
│   ├── GND → Ground
│   └── EN → Pull-up to 3.3V
├── Serial Communication
│   ├── TX2 (GPIO17) → Pin 14 (Arduino RX3)
│   ├── RX2 (GPIO16) → Pin 15 (Arduino TX3)
│   └── Baud Rate → 115200
├── WiFi Configuration
│   ├── Mode → Station + AP
│   ├── Security → WPA2-PSK
│   ├── Protocols → HTTP, MQTT, WebSocket
│   └── Range → 100m typical
├── Additional I/O
│   ├── GPIO2 → Status LED
│   ├── GPIO4 → Relay control
│   ├── GPIO5 → Spare output
│   └── ADC → Analog monitoring
└── Programming
    ├── USB → CP2102 USB-to-serial
    ├── Flash → 4MB
    ├── RAM → 520KB
    └── OTA → Over-the-air updates
```

## Power Distribution System

### Main Power System
```
Power Distribution
├── AC Input
│   ├── Voltage → 120/240VAC
│   ├── Frequency → 50/60Hz
│   ├── Breaker → 20A
│   └── Ground → Earth ground
├── 24V DC Supply
│   ├── Model → Mean Well 24V 15A
│   ├── Input → 120/240VAC
│   ├── Output → 24V @ 15A
│   ├── Regulation → ±1%
│   └── Use → Heaters, UV LEDs
├── 12V DC Supply
│   ├── Model → Mean Well 12V 10A
│   ├── Input → 120/240VAC
│   ├── Output → 12V @ 10A
│   ├── Regulation → ±1%
│   └── Use → Fans, Peltiers, Arduino
├── 5V DC Supply
│   ├── Source → 12V buck converter
│   ├── Output → 5V @ 5A
│   ├── Regulation → ±2%
│   └── Use → Logic, sensors
└── 3.3V DC Supply
    ├── Source → 5V linear regulator
    ├── Output → 3.3V @ 2A
    ├── Regulation → ±1%
    └── Use → Sensors, ESP32
```

### Power Management
```
Power Control System
├── Main Contactor
│   ├── Coil → 24V DC
│   ├── Contacts → 3-pole, 20A
│   ├── Control → Emergency stop
│   └── Auxiliary → Status feedback
├── Solid State Relays
│   ├── SSR1 → Heater control (25A)
│   ├── SSR2 → UV LED control (10A)
│   ├── SSR3 → Pump control (5A)
│   └── SSR4 → Spare (5A)
├── Circuit Protection
│   ├── Main Breaker → 20A
│   ├── Sub-breakers → 5A each circuit
│   ├── Fuses → Fast-blow for electronics
│   └── Surge Protection → MOV devices
└── Monitoring
    ├── Voltage → Pin A10
    ├── Current → Pins A8, A9
    ├── Power Factor → Calculated
    └── Energy → Accumulated
```

## Safety Systems

### Emergency Stop Circuit
```
Emergency Stop System
├── E-Stop Button
│   ├── Type → Red mushroom, NC
│   ├── Contacts → 2 NC pairs
│   ├── Rating → 10A @ 250VAC
│   └── Reset → Twist to release
├── Safety Relay
│   ├── Model → Pilz PNOZ
│   ├── Inputs → E-stop, door, guards
│   ├── Outputs → Contactor control
│   └── Monitoring → Self-monitoring
├── Interlocks
│   ├── Door → Magnetic switch
│   ├── UV Cover → Limit switch
│   ├── Guards → Multiple switches
│   └── Manual Reset → Required
└── Actions
    ├── Power → Immediate disconnection
    ├── UV → Immediate shutdown
    ├── Alarms → Visual and audible
    └── Logging → Event recording
```

### Over-Temperature Protection
```
Thermal Protection
├── Hardware Thermostats
│   ├── Type → Bimetallic NC
│   ├── Setting → 90°C
│   ├── Location → Chamber ceiling
│   └── Reset → Manual reset
├── Software Monitoring
│   ├── Sensors → Multiple DS18B20
│   ├── Limits → 85°C alarm
│   ├── Response → Cooling activation
│   └── Shutdown → At 88°C
├── Thermal Fuses
│   ├── Rating → 95°C
│   ├── Location → Heater circuits
│   ├── Type → One-time
│   └── Replacement → User serviceable
└── Cooling System
    ├── Fans → Maximum speed
    ├── Cooling → Peltier cooling
    ├── Venting → Exhaust activation
    └── Monitoring → Continuous
```

## Grounding and EMI Protection

### Grounding System
```
Grounding Architecture
├── Safety Ground
│   ├── Earth → Building ground
│   ├── Chassis → All metal parts
│   ├── Enclosure → Conductive paint
│   └── Continuity → <0.1Ω
├── Signal Ground
│   ├── Analog → Separate ground plane
│   ├── Digital → Digital ground plane
│   ├── Isolation → Opto-isolators
│   └── Connection → Star point
├── Power Ground
│   ├── AC → Equipment ground
│   ├── DC → Common negative
│   ├── Switching → Separate ground
│   └── Filtering → Common mode filters
└── Shield Ground
    ├── Cables → 360° termination
    ├── Sensors → Single-end grounding
    └── Enclosure → RF shielding
```

### EMI Mitigation
```
EMI Protection
├── Shielded Cables
│   ├── Power → Armored cables
│   ├── Signals → Twisted pair
│   ├── Sensors → Shielded cables
│   └── Termination → Proper grounding
├── Filtering
│   ├── AC Line → EMI filters
│   ├── DC Power → LC filters
│   ├── Switching → Snubber circuits
│   └── Digital → Ferrite cores
├── Isolation
│   ├── Optocouplers → Digital signals
│   ├── Transformers → AC power
│   ├── Differential → Analog signals
│   └── Barriers → Safety barriers
└── Enclosure
    ├── Material → Conductive aluminum
    ├── Gaskets → Conductive gaskets
    ├── Penetrations → Filtered entries
    └── Ventilation → EMI louvers
```

## Installation and Testing

### Installation Guidelines
1. Mount all components securely
2. Use proper cable management
3. Verify all connections before power-up
4. Test safety systems first
5. Calibrate all sensors
6. Validate control loops
7. Perform complete system test

### Testing Procedures
1. Visual inspection of all connections
2. Continuity testing of safety circuits
3. Insulation resistance testing
4. Functional testing of all systems
5. Calibration verification
6. Performance validation
7. Safety system testing

### Maintenance Requirements
1. Monthly sensor calibration
2. Quarterly filter replacement
3. Semi-annual safety testing
4. Annual complete calibration
5. Component replacement schedule
6. Preventive maintenance log

This comprehensive circuit diagram ensures proper implementation of the environmental test chamber with all necessary environmental control, safety, and monitoring systems.