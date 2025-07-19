# Program 21: Fatigue Testing Machine - Circuit Diagram

## Overview
This circuit diagram shows the complete wiring for a professional fatigue testing machine with cyclic loading control, acoustic emission monitoring, and comprehensive safety systems.

## Main Components Connection

### Arduino Mega 2560 (Main Controller)
```
Arduino Mega 2560
├── Digital Pins
│   ├── Pin 2  → Stepper Motor STEP (TB6600)
│   ├── Pin 3  → Stepper Motor DIR (TB6600)
│   ├── Pin 4  → Stepper Motor ENABLE (TB6600)
│   ├── Pin 5  → Load Cell DOUT (HX711)
│   ├── Pin 6  → Load Cell SCK (HX711)
│   ├── Pin 7  → Touch Screen YP
│   ├── Pin 8  → Touch Screen XM
│   ├── Pin 9  → Touch Screen YM
│   ├── Pin 10 → Touch Screen XP
│   ├── Pin 11 → Touch Screen IRQ
│   ├── Pin 18 → Emergency Stop Button (Interrupt)
│   ├── Pin 19 → Door Interlock Switch (Interrupt)
│   ├── Pin 20 → Specimen Detection Switch
│   ├── Pin 21 → Limit Switch Top
│   ├── Pin 22 → Limit Switch Bottom
│   ├── Pin 23 → Safety Relay Control
│   ├── Pin 24 → Tower Light Red
│   ├── Pin 25 → Tower Light Yellow
│   ├── Pin 26 → Tower Light Green
│   ├── Pin 27 → Buzzer Control
│   ├── Pin 28 → Cooling Fan Control
│   ├── Pin 29 → LED Strip Control
│   ├── Pin 30 → ADS1256 CS (24-bit ADC)
│   ├── Pin 31 → ADS1256 DRDY
│   ├── Pin 32 → ADS1256 RESET
│   ├── Pin 33 → Spare Digital Output
│   ├── Pin 34 → Spare Digital Output
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
│   ├── Pin A0 → LVDT Signal Input (Conditioned)
│   ├── Pin A1 → Acoustic Emission Sensor 1
│   ├── Pin A2 → Acoustic Emission Sensor 2
│   ├── Pin A3 → Temperature Sensor 1 (Specimen)
│   ├── Pin A4 → Temperature Sensor 2 (Environment)
│   ├── Pin A5 → Touch Screen Analog X
│   ├── Pin A6 → Touch Screen Analog Y
│   ├── Pin A7 → Vibration Sensor
│   ├── Pin A8 → Current Monitor (Motor)
│   ├── Pin A9 → Voltage Monitor (System)
│   ├── Pin A10 → Strain Gauge Bridge 1
│   ├── Pin A11 → Strain Gauge Bridge 2
│   ├── Pin A12 → Spare Analog Input
│   ├── Pin A13 → Spare Analog Input
│   ├── Pin A14 → Spare Analog Input
│   └── Pin A15 → Spare Analog Input
├── Communication
│   ├── Pin 0  → RX (USB/Debug)
│   ├── Pin 1  → TX (USB/Debug)
│   ├── Pin 14 → TX3 (ESP32 communication)
│   ├── Pin 15 → RX3 (ESP32 communication)
│   ├── Pin 16 → TX2 (PC communication)
│   └── Pin 17 → RX2 (PC communication)
└── Power
    ├── VIN → 12V DC Input
    ├── 5V → Logic Level Power
    ├── 3.3V → Sensor Power
    └── GND → Common Ground
```

## Load Measurement System

### 200kg S-Type Load Cell
```
S-Type Load Cell (200kg)
├── Excitation
│   ├── E+ → HX711 E+ (Red wire)
│   ├── E- → HX711 E- (Black wire)
│   └── Supply → 5V DC
├── Signal Output
│   ├── S+ → HX711 A+ (White wire)
│   ├── S- → HX711 A- (Green wire)
│   └── Shield → Ground
├── Specifications
│   ├── Capacity → 200kg (2000N)
│   ├── Sensitivity → 2.0 ± 0.1 mV/V
│   ├── Accuracy → 0.03% FS
│   ├── Overload → 150% FS
│   └── Temperature → -10°C to +40°C
└── Mounting
    ├── Top → Crosshead connection
    ├── Bottom → Specimen grip
    └── Alignment → Critical for accuracy
```

### HX711 Load Cell Amplifier
```
HX711 24-bit ADC
├── Power Supply
│   ├── VCC → 5V
│   ├── GND → Ground
│   └── Current → 1.5mA typical
├── Load Cell Interface
│   ├── E+ → Load cell excitation positive
│   ├── E- → Load cell excitation negative
│   ├── A+ → Load cell signal positive
│   ├── A- → Load cell signal negative
│   ├── B+ → Not used
│   └── B- → Not used
├── Digital Interface
│   ├── DOUT → Pin 5 (Arduino)
│   ├── SCK → Pin 6 (Arduino)
│   └── RATE → Ground (10Hz)
└── Configuration
    ├── Gain → 128 (Channel A)
    ├── Resolution → 24-bit
    ├── Sample Rate → 10/80 Hz
    └── Input Range → ±20mV/40mV
```

## Displacement Measurement System

### LVDT (Linear Variable Differential Transformer)
```
LVDT ±25mm
├── Primary Coil
│   ├── AC Excitation → AD698 OSC OUT
│   ├── Frequency → 2.5kHz
│   └── Amplitude → 3V RMS
├── Secondary Coils
│   ├── SEC1+ → AD698 A
│   ├── SEC1- → AD698 B
│   ├── SEC2+ → AD698 C
│   └── SEC2- → AD698 D
├── Specifications
│   ├── Range → ±25mm
│   ├── Linearity → 0.25% FS
│   ├── Sensitivity → 100mV/mm
│   └── Resolution → 0.001mm
└── Mounting
    ├── Body → Fixed to frame
    └── Core → Connected to crosshead
```

### AD698 LVDT Signal Conditioner
```
AD698 Signal Conditioner
├── Power Supply
│   ├── +VS → +15V
│   ├── -VS → -15V
│   ├── GND → Ground
│   └── Current → 12mA
├── LVDT Interface
│   ├── A, B → Primary connections
│   ├── C, D → Secondary connections
│   └── Shield → Cable shield
├── Output
│   ├── VOUT → Pin A0 (Arduino)
│   ├── Range → 0-5V
│   ├── Scaling → 100mV/mm
│   └── Filter → 100Hz lowpass
└── Configuration
    ├── R1 → 10kΩ (frequency set)
    ├── C1 → 100nF (filter)
    └── Zero Adjust → 10kΩ pot
```

## Motion Control System

### NEMA 23 Stepper Motor
```
NEMA 23 Stepper Motor
├── Specifications
│   ├── Holding Torque → 3.0 Nm
│   ├── Current → 4.2A per phase
│   ├── Resistance → 0.9Ω per phase
│   ├── Inductance → 5.0mH per phase
│   ├── Steps/Rev → 200 (1.8°)
│   └── Bipolar → 4-wire
├── Wiring
│   ├── A+ → TB6600 A+ (Red)
│   ├── A- → TB6600 A- (Green)
│   ├── B+ → TB6600 B+ (Yellow)
│   └── B- → TB6600 B- (Blue)
└── Mechanical
    ├── Lead Screw → 5mm pitch
    ├── Coupling → Flexible coupling
    └── Linear Guide → THK rails
```

### TB6600 Stepper Driver
```
TB6600 Stepper Motor Driver
├── Power Input
│   ├── VCC → 24V DC (9-42V range)
│   ├── GND → Power Ground
│   └── Current → Up to 4A
├── Motor Output
│   ├── A+ → Motor coil A positive
│   ├── A- → Motor coil A negative
│   ├── B+ → Motor coil B positive
│   └── B- → Motor coil B negative
├── Control Signals
│   ├── PUL+ → Pin 2 (Step)
│   ├── PUL- → Ground
│   ├── DIR+ → Pin 3 (Direction)
│   ├── DIR- → Ground
│   ├── ENA+ → Pin 4 (Enable)
│   └── ENA- → Ground
├── Configuration (DIP Switches)
│   ├── Current → 3.5A (SW1-3: ON,OFF,OFF)
│   ├── Microstep → 16 (SW4-6: ON,ON,OFF)
│   └── Decay → Fast decay
└── Protection
    ├── Overcurrent → Automatic
    ├── Overtemperature → Thermal shutdown
    └── Short Circuit → Protected
```

## Acoustic Emission System

### AE Sensors
```
Acoustic Emission Sensors (2x)
├── Sensor Type
│   ├── Model → R15α
│   ├── Frequency → 150-400 kHz
│   ├── Resonance → 150 kHz
│   └── Sensitivity → 75 dB ref 1V/μbar
├── Preamplifier
│   ├── Gain → 40 dB
│   ├── Power → 28V DC
│   ├── Output → 0-10V
│   └── Impedance → 50Ω
├── Connection
│   ├── Sensor 1 → Pin A1 (via divider)
│   ├── Sensor 2 → Pin A2 (via divider)
│   └── Shield → Analog ground
└── Mounting
    ├── Coupling → Ultrasonic gel
    ├── Pressure → Spring-loaded
    └── Location → Near gauge section
```

### ADS1256 24-bit ADC (For High-Speed AE)
```
ADS1256 24-bit ADC
├── Power Supply
│   ├── DVDD → 5V (Digital)
│   ├── AVDD → 5V (Analog)
│   ├── AGND → Analog Ground
│   └── DGND → Digital Ground
├── SPI Interface
│   ├── SCLK → Pin 52 (SCK)
│   ├── DIN → Pin 51 (MOSI)
│   ├── DOUT → Pin 50 (MISO)
│   ├── CS → Pin 30
│   ├── DRDY → Pin 31
│   └── RESET → Pin 32
├── Analog Inputs
│   ├── AIN0 → AE Sensor 1 (buffered)
│   ├── AIN1 → AE Sensor 2 (buffered)
│   ├── AIN2-7 → Spare inputs
│   └── AINCOM → Analog ground
└── Configuration
    ├── Data Rate → 30kSPS
    ├── PGA Gain → 1
    ├── Input Range → ±5V
    └── Reference → Internal 2.5V
```

## Display and User Interface

### 7" TFT Display (800x480)
```
7" TFT Display Module
├── Display Interface
│   ├── RS → Pin 38 (Register Select)
│   ├── WR → Pin 39 (Write)
│   ├── RD → Pin 42 (Read)
│   ├── CS → Pin 40 (Chip Select)
│   ├── RST → Pin 41 (Reset)
│   └── D0-D15 → Port A and Port C
├── Touch Interface
│   ├── YP → Pin 7
│   ├── XM → Pin 8
│   ├── YM → Pin 9
│   ├── XP → Pin 10
│   ├── IRQ → Pin 11
│   ├── X → Pin A5
│   └── Y → Pin A6
├── Power Supply
│   ├── VDD → 3.3V (Logic)
│   ├── LED+ → 12V (Backlight)
│   ├── LED- → Ground
│   └── Current → 500mA total
└── Features
    ├── Resolution → 800x480
    ├── Colors → 65K (16-bit)
    ├── Touch → 4-wire resistive
    └── Controller → SSD1963
```

## Safety Systems

### Emergency Stop Circuit
```
Emergency Stop System
├── E-Stop Button
│   ├── Type → Red mushroom, NC
│   ├── Contacts → 2 NC pairs
│   ├── Reset → Twist to release
│   └── Rating → 10A @ 250VAC
├── Safety Relay
│   ├── Coil → 24V DC
│   ├── Contacts → 4 NC, 2 NO
│   ├── Input → E-stop button
│   └── Output → Motor power
├── Control Circuit
│   ├── Pin 18 → E-stop status
│   ├── Pin 23 → Relay control
│   └── Interrupt → FALLING edge
└── Actions
    ├── Motor → Immediate stop
    ├── Data → Save current state
    └── Alert → Visual + audible
```

### Door Interlock System
```
Door Interlock
├── Magnetic Switch
│   ├── Type → NC reed switch
│   ├── Gap → 10mm maximum
│   ├── Rating → 0.5A @ 100V
│   └── LED → Status indicator
├── Connection
│   ├── Pin 19 → Switch status
│   ├── Pull-up → Internal
│   └── Interrupt → CHANGE
└── Logic
    ├── Door Open → Pause test
    ├── Door Closed → Allow resume
    └── Override → Maintenance mode
```

## Power Distribution

### Main Power System
```
Power Distribution
├── AC Input
│   ├── Line → 120/240VAC
│   ├── Neutral → AC return
│   ├── Ground → Safety ground
│   └── Breaker → 20A
├── 24V DC Supply
│   ├── Model → Mean Well 24V 10A
│   ├── Input → 120/240VAC
│   ├── Output → 24V @ 10A
│   └── Use → Stepper motor
├── 12V DC Supply
│   ├── Model → Mean Well 12V 5A
│   ├── Input → 120/240VAC
│   ├── Output → 12V @ 5A
│   └── Use → Arduino, display
├── ±15V DC Supply
│   ├── Model → Dual output linear
│   ├── Output → ±15V @ 1A
│   └── Use → LVDT conditioner
└── 5V DC Supply
    ├── Source → 12V buck converter
    ├── Output → 5V @ 3A
    └── Use → Sensors, logic
```

### Power Sequencing
```
Power-On Sequence
├── Step 1: AC mains → Circuit breaker ON
├── Step 2: 24V supply → Motor power ready
├── Step 3: 12V supply → Control power ready
├── Step 4: ±15V supply → Analog circuits ready
├── Step 5: 5V supply → Logic circuits ready
├── Step 6: Arduino → System initialization
├── Step 7: Motor enable → After homing
└── Step 8: Test ready → All systems go
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
│   ├── Mode → Station
│   ├── Security → WPA2
│   └── Protocol → MQTT
├── SD Card (ESP32)
│   ├── CS → GPIO5
│   ├── MOSI → GPIO23
│   ├── MISO → GPIO19
│   ├── SCK → GPIO18
│   └── Format → FAT32
└── Status LEDs
    ├── GPIO2 → WiFi status
    ├── GPIO4 → MQTT status
    └── GPIO15 → Data transfer
```

## Sensor Signal Conditioning

### Temperature Sensors
```
Temperature Measurement
├── Specimen Temperature
│   ├── Sensor → Type K thermocouple
│   ├── Amplifier → MAX31855
│   ├── Output → SPI to Arduino
│   └── Range → -200°C to +1350°C
└── Ambient Temperature
    ├── Sensor → DS18B20
    ├── Interface → OneWire
    ├── Pin → A4
    └── Accuracy → ±0.5°C
```

### Vibration Monitoring
```
Vibration Sensor
├── Type → ADXL345 Accelerometer
├── Interface → I2C
├── Address → 0x53
├── Range → ±16g
├── Output → Digital
└── Use → System health monitoring
```

## Data Logging System

### SD Card Module
```
SD Card Interface
├── Module → Standard SD breakout
├── Interface → SPI
├── Connections
│   ├── CS → Pin 53
│   ├── MOSI → Pin 51
│   ├── MISO → Pin 50
│   ├── SCK → Pin 52
│   └── VCC → 5V
├── Card Specs
│   ├── Type → SDHC
│   ├── Capacity → 32GB
│   ├── Speed → Class 10
│   └── Format → FAT32
└── File Structure
    ├── /TESTS/ → Test data files
    ├── /REPORTS/ → Generated reports
    ├── /CONFIG/ → System configuration
    └── /LOGS/ → System logs
```

## Grounding and Shielding

### Grounding Scheme
```
System Grounding
├── Safety Ground
│   ├── AC ground → Earth ground
│   ├── Chassis → Safety ground
│   └── Motor frame → Safety ground
├── Signal Ground
│   ├── Analog GND → Star point
│   ├── Digital GND → Separate plane
│   └── Connection → Single point
├── Shield Ground
│   ├── Cable shields → Analog ground
│   ├── Sensor shields → Single end
│   └── No ground loops → Critical
└── Power Ground
    ├── DC supplies → Common negative
    ├── Isolation → From signal ground
    └── Heavy gauge → For high current
```

## Installation Notes

### Wiring Guidelines
1. Keep power and signal cables separated
2. Use shielded cables for all analog signals
3. Twist pair differential signals
4. Minimize wire lengths
5. Use proper cable gauge for current

### EMI Considerations
1. Install ferrite cores on motor cables
2. Use metal enclosure for electronics
3. Proper grounding and shielding
4. Keep switching supplies away from analog
5. Filter all power inputs

### Calibration Requirements
1. Load cell calibration with certified weights
2. LVDT zero and span adjustment
3. AE sensor sensitivity check
4. Temperature sensor verification
5. System compliance validation

This comprehensive circuit diagram ensures proper implementation of the fatigue testing machine with all necessary safety, measurement, and control systems.