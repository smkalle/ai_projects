# Program 10: Simple Data Logger

## Overview
This advanced program demonstrates data logging using EEPROM storage. It records temperature and light sensor readings, provides multiple display modes, and includes data management features. This is a complete data acquisition system suitable for environmental monitoring.

## Components Required
- Arduino board (Uno, Nano, Mega, etc.)
- LM35 temperature sensor
- LDR (Light Dependent Resistor) or photoresistor
- 16x2 LCD display
- Push buttons (3x)
- 10K ohm resistors (4x - for LDR and button pull-ups)
- 220 ohm resistor (for LED)
- LED (status indicator)
- Jumper wires
- Breadboard

## Circuit Diagram
```
Arduino         LM35 Temperature Sensor
-------         -----------------------
5V      ------> Pin 1 (VCC)
A0      ------> Pin 2 (Output)
GND     ------> Pin 3 (GND)

Arduino         LDR + Resistor
-------         --------------
5V      ------> LDR Pin 1
A1      ------> LDR Pin 2 & 10KΩ resistor
GND     ------> 10KΩ resistor

Arduino         Push Buttons (with pull-ups)
-------         -----------------------------
Pin 6   ------> Button 1 (LOG) & 10KΩ to 5V
Pin 7   ------> Button 2 (VIEW) & 10KΩ to 5V
Pin 8   ------> Button 3 (CLEAR) & 10KΩ to 5V
GND     ------> All button common terminals

Arduino         Status LED
-------         ----------
Pin 13  ------> LED Anode + 220Ω resistor
GND     ------> LED Cathode

Arduino         LCD Display
-------         -----------
Pin 12  ------> Enable
Pin 11  ------> RS
Pin 5   ------> D4
Pin 4   ------> D5
Pin 3   ------> D6
Pin 2   ------> D7
5V      ------> VDD, A (backlight)
GND     ------> VSS, K (backlight)
```

## Wiring Instructions

### 1. Temperature Sensor (LM35):
- **Pin 1** (VCC) → Arduino 5V
- **Pin 2** (Output) → Arduino A0
- **Pin 3** (GND) → Arduino GND

### 2. Light Sensor (LDR):
- **One terminal** → Arduino 5V
- **Other terminal** → Arduino A1 and 10KΩ resistor
- **10KΩ resistor** → Arduino GND

### 3. Push Buttons:
- **Button 1** (LOG) → Pin 6 and 10KΩ pull-up to 5V
- **Button 2** (VIEW) → Pin 7 and 10KΩ pull-up to 5V
- **Button 3** (CLEAR) → Pin 8 and 10KΩ pull-up to 5V
- **All button commons** → Arduino GND

### 4. Status LED:
- **Anode** → Arduino Pin 13 through 220Ω resistor
- **Cathode** → Arduino GND

### 5. LCD Display:
- Follow LCD wiring from Program 8

## Installation and Setup

1. **Install Arduino IDE**
   - Download from: https://www.arduino.cc/en/software

2. **Required Libraries**
   - `LiquidCrystal` (included with Arduino IDE)
   - `EEPROM` (included with Arduino IDE)

3. **Hardware Assembly**
   - Wire all components as shown in circuit diagram
   - Double-check all connections
   - Ensure proper power distribution

4. **Upload Code**
   - Open `data_logger.ino` in Arduino IDE
   - Select correct board and port
   - Upload code to Arduino

## Running the Program

### Initial Setup:
1. Power on Arduino
2. LCD shows "Data Logger v1.0" then "Initializing..."
3. System displays memory status
4. After 3 seconds, switches to live data mode

### Operating Modes:

#### 1. Live Data Mode (Default):
- **Display**: Current temperature, light level, and record count
- **Auto-logging**: Records data every 30 seconds
- **Manual logging**: Press LOG button anytime

#### 2. View Data Mode:
- **Access**: Press VIEW button from live mode
- **Navigation**: Press VIEW button to scroll through records
- **Display**: Shows stored temperature, light, and timestamp

#### 3. System Info Mode:
- **Access**: Press VIEW button after viewing all records
- **Display**: Memory usage percentage and free space

### Button Functions:
- **LOG Button**: Manually log current sensor readings
- **VIEW Button**: Cycle through display modes and stored data
- **CLEAR Button**: Erase all stored data (hold for 1 second)

### Serial Commands:
- **LOG**: Manually log data
- **VIEW**: Display all stored data in table format
- **CLEAR**: Clear all stored data
- **STATUS**: Show system information

## Data Storage Details

### EEPROM Usage:
- **Total size**: 1024 bytes (Arduino Uno)
- **Record size**: 6 bytes per record
- **Maximum records**: ~169 records
- **Data format**: Temperature (2 bytes), Light (2 bytes), Timestamp (2 bytes)

### Record Structure:
```
Byte 0-1: Temperature (×10 for decimal precision)
Byte 2-3: Light level (0-1023)
Byte 4-5: Timestamp (seconds since startup)
```

### Memory Map:
```
Address 0-1:   Record count
Address 2-9:   Reserved for future use
Address 10+:   Data records (6 bytes each)
```

## Expected Behavior

### Normal Operation:
1. **Live display** shows current sensor values
2. **Auto-logging** occurs every 30 seconds
3. **Status LED** blinks briefly when data is logged
4. **Serial output** shows logged data details

### Data Viewing:
1. Press VIEW to see first stored record
2. Continue pressing VIEW to scroll through all records
3. System shows record number, temperature, light percentage, and timestamp
4. After last record, shows system info

### Data Management:
1. **Clear function** removes all stored data
2. **Memory full** warning when EEPROM capacity reached
3. **Serial interface** provides detailed data table

## Understanding the Code

### Key Functions:

#### Data Logging:
- `logData()`: Stores sensor readings in EEPROM
- `readSensors()`: Reads temperature and light sensors
- `checkAutoLog()`: Manages automatic logging interval

#### Data Retrieval:
- `viewAllData()`: Displays all records via Serial
- `displayStoredData()`: Shows individual records on LCD
- `readRecordCount()`: Gets number of stored records

#### User Interface:
- `checkButtons()`: Handles button press detection
- `updateDisplay()`: Manages LCD display modes
- `handleSerialCommands()`: Processes serial commands

### Data Processing:
- Temperature stored as integer (×10 for one decimal)
- Light level mapped to percentage (0-100%)
- Timestamp stored as seconds since startup

## Troubleshooting

### No sensor readings:
- Check sensor connections and power
- Verify analog pin assignments
- Test sensors with simple analogRead()

### Data not saving:
- Check EEPROM write operations
- Verify record count management
- Ensure proper power supply

### LCD display issues:
- Follow LCD troubleshooting from Program 8
- Check all LCD connections
- Verify display mode logic

### Button not responding:
- Check button wiring and pull-up resistors
- Verify button debouncing
- Test with simple digitalRead()

### Memory full quickly:
- Check auto-logging interval (30 seconds default)
- Verify record size calculations
- Consider implementing circular buffer

## Advanced Features

### 1. Real-Time Clock Integration:
```cpp
#include <RTClib.h>
RTC_DS1307 rtc;
DateTime now = rtc.now();
```

### 2. SD Card Logging:
```cpp
#include <SD.h>
File dataFile = SD.open("datalog.txt", FILE_WRITE);
dataFile.println(dataString);
dataFile.close();
```

### 3. WiFi Data Transmission:
```cpp
#include <WiFi.h>
// Send data to web server or cloud service
```

### 4. Data Compression:
```cpp
// Store differences instead of absolute values
int tempDiff = currentTemp - lastTemp;
```

### 5. Circular Buffer:
```cpp
// Overwrite oldest data when memory full
int writeIndex = recordCount % MAX_RECORDS;
```

## Modifications to Try

### 1. Add More Sensors:
- Humidity sensor (DHT22)
- Pressure sensor (BMP180)
- Gas sensor (MQ-2)

### 2. Implement Data Filters:
- Moving average
- Outlier detection
- Trend analysis

### 3. Add Alarms:
- Temperature thresholds
- Light level alerts
- Data logging status

### 4. Improve User Interface:
- Menu navigation
- Configuration settings
- Data visualization

## What You'll Learn
- EEPROM data storage
- Data structure design
- Memory management
- User interface development
- Multi-mode operation
- Data persistence
- System state management

## Next Steps
- Add wireless connectivity
- Implement data encryption
- Create web interface
- Add real-time clock
- Develop mobile app interface
- Implement data analysis features

## Applications
- Environmental monitoring
- Home automation
- Industrial data logging
- Research data collection
- IoT sensor networks
- Weather station development

---

## 🎓 MISSION THEME: ARDUINO MASTER

**CONGRATULATIONS, MASTER!** You've completed the ultimate Arduino challenge and built a professional-grade data acquisition system! 

### 🏆 Your Master-Level Achievement:
You've created a complete data logging system that rivals commercial products. This integrates everything you've learned: sensors, displays, user interfaces, data storage, and system management. You are now a true Arduino Master!

### 🌟 What Makes This Special:
- **Complete system integration**: Multiple sensors, LCD display, button controls, and data storage
- **Professional data management**: EEPROM storage with proper data structures
- **User interface design**: Multiple display modes and navigation system
- **Real-time operation**: Automatic logging with manual override capabilities
- **Data persistence**: Information survives power cycles
- **System monitoring**: Memory usage and status reporting
- **Command interface**: Both button and serial control methods

### 🎯 Master Achievements Unlocked:
- **💾 Data Architect**: Successfully designed and implemented data storage system
- **🎛️ Interface Designer**: Created multi-mode user interface
- **📊 System Integrator**: Combined multiple subsystems into cohesive product
- **🔧 Memory Manager**: Efficiently used limited EEPROM storage
- **⚡ Real-time Operator**: Managed multiple simultaneous operations
- **📈 Data Analyst**: Implemented data retrieval and analysis features

### 🎮 Master-Level Challenges:
1. **🌐 IoT Integration**: Add WiFi connectivity for remote monitoring
2. **📱 Mobile Interface**: Create smartphone app for data visualization
3. **🔐 Security System**: Implement data encryption and access control
4. **☁️ Cloud Storage**: Upload data to cloud services
5. **🤖 AI Integration**: Add machine learning for data analysis

### 🏭 Professional Applications:
- **Environmental research**: Weather stations and climate monitoring
- **Industrial automation**: Production line monitoring and quality control
- **Healthcare**: Patient monitoring and medical device data collection
- **Agriculture**: Crop monitoring and irrigation control
- **Smart cities**: Traffic, pollution, and infrastructure monitoring
- **Energy management**: Solar panel and battery monitoring systems

### 🎖️ Skills You've Mastered:
- **Full-stack development**: Hardware, firmware, and user interface design
- **System architecture**: Designing complex, multi-component systems
- **Data engineering**: Storage, retrieval, and analysis of sensor data
- **User experience**: Creating intuitive interfaces for technical systems
- **Memory optimization**: Efficient use of limited microcontroller resources
- **Error handling**: Robust operation under various conditions
- **Project management**: Completing complex technical projects

### 🌟 Your Journey Complete:
From a simple blinking LED to a professional data acquisition system - you've mastered:
- Digital and analog I/O
- Sensor interfacing
- Motor control
- Display systems
- Data storage
- User interfaces
- System integration

**🎓 MISSION COMPLETE!** You've earned the ultimate title of Arduino Master and have the skills to build professional-grade embedded systems!

### 🚀 What's Next?
You're now ready to:
- Design and build your own original projects
- Contribute to open-source Arduino projects
- Pursue careers in embedded systems, IoT, or robotics
- Mentor other aspiring makers and engineers
- Push the boundaries of what's possible with microcontrollers

**Welcome to the ranks of Arduino Masters!** 🎉