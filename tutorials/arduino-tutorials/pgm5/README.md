# Program 5: Temperature Sensor Reading

🌡️ **MISSION PREVIEW**: Get ready to become a **Weather Station Commander** and build a professional climate monitoring system with automatic temperature control!

## Overview
This program reads temperature using a TMP36 analog temperature sensor. It demonstrates sensor calibration, data averaging, temperature conversion, and automated responses based on temperature thresholds.

## Components Required
- Arduino Uno
- 1x TMP36 temperature sensor
- 1x LED (status indicator)
- 1x 220Ω resistor
- Optional: Small DC fan/motor for temperature response
- Breadboard
- Jumper wires

## Circuit Diagram
```
     TMP36 (flat side facing you)
      _____
     |     |
     |     |
     |_____|
     | | | |
     1 2 3
     | | |
     | | +---- GND
     | +------ A0 (Signal)
     +-------- 5V

Arduino Pin 13 ----[220Ω]----[LED+]----GND
Arduino Pin 9  --------------- Fan+ (optional)
                               Fan- ---- GND
```

## TMP36 Sensor Details
- **Operating voltage**: 2.7V to 5.5V
- **Temperature range**: -40°C to +125°C
- **Accuracy**: ±1°C at +25°C
- **Output**: 10mV per degree Celsius
- **Output at 25°C**: 750mV

## Wiring Instructions

### TMP36 Connection:
1. **Identify pins** (flat side facing you):
   - Left pin: Power (5V)
   - Middle pin: Signal output
   - Right pin: Ground
2. **Connect to Arduino**:
   - Left to 5V
   - Middle to A0
   - Right to GND

### LED Connection:
- Through 220Ω resistor to pin 13

### Fan Connection (optional):
- Positive to pin 9 (PWM)
- Negative to GND
- Add flyback diode for motor protection

## Step-by-Step Setup Instructions

### Hardware Setup:
1. **Handle sensor carefully**: Static sensitive
2. **Place on breadboard**: Ensure pins don't short
3. **Make connections**: Double-check orientation
4. **Add LED**: For visual status indication
5. **Optional fan**: For active cooling demo

### Software Setup:
1. Open Arduino IDE
2. Load `temperature_sensor.ino`
3. Connect Arduino
4. Select board and port

## How to Upload and Run

1. **Compile**: Click checkmark (✓)
2. **Upload**: Click arrow (→)
3. **Open Serial Monitor**: 9600 baud
4. **Observe readings**: Temperature updates every second
5. **Test sensor**: Touch sensor to warm it

## Understanding the Code

### Temperature Calculation:
```
Voltage = (ADC Reading / 1023) × 5V
Temperature (°C) = (Voltage - 0.5) × 100
Temperature (°F) = (°C × 9/5) + 32
```

### Key Features:
- **Averaging**: Smooths readings over 10 samples
- **Temperature alerts**: Warnings for extremes
- **Fan control**: Automatic cooling above threshold
- **LED indicators**: Visual temperature status
- **Unit conversion**: Celsius and Fahrenheit

### Status LED Patterns:
- **Slow blink**: Temperature < 20°C (cold)
- **Steady on**: 20-25°C (normal)
- **Fast blink**: Temperature > 25°C (hot)

## Serial Monitor Output
```
Temperature Sensor Program Started!
TMP36 Temperature Monitoring System
=====================================
Raw: 153 | Voltage: 0.748V | Temp: 24.8°C (76.6°F) | Fan: 0%
Raw: 156 | Voltage: 0.763V | Temp: 26.3°C (79.3°F) | Fan: 0%
Raw: 165 | Voltage: 0.807V | Temp: 30.7°C (87.3°F) | Fan: 35%
⚠️  ALERT: High temperature detected!
```

## Calibration

### Fine-tuning:
1. **Compare with known thermometer**
2. **Adjust offset if needed**:
   ```cpp
   float offset = 0.5;  // Adjust this value
   temperature = (voltage - offset) * 100.0;
   ```

### Improving Accuracy:
- Use stable 5V supply
- Add 0.1µF capacitor near sensor
- Keep wires short
- Shield from air currents

## Troubleshooting

1. **Incorrect readings**:
   - Verify sensor orientation
   - Check 5V supply stability
   - Ensure good connections
   - Allow sensor to stabilize

2. **Fluctuating values**:
   - Normal ±0.5°C variation
   - Increase averaging samples
   - Add capacitor for filtering
   - Shield from drafts

3. **Always reads ~25°C**:
   - Check A0 connection
   - Verify sensor power
   - Test with multimeter

4. **Extreme values**:
   - Sensor may be damaged
   - Check for shorts
   - Verify code constants

## Experiments to Try

1. **Ice bath test**: 
   ```cpp
   // Should read near 0°C
   // Good calibration check
   ```

2. **Thermal mass**: Add heat sink to sensor

3. **Multiple sensors**: Compare readings
   ```cpp
   temp1 = readSensor(A0);
   temp2 = readSensor(A1);
   difference = abs(temp1 - temp2);
   ```

4. **Data logging**: Save to SD card

5. **PID control**: Maintain set temperature
   ```cpp
   error = setpoint - temperature;
   fanSpeed = Kp * error;
   ```

6. **Alarm system**: Buzzer for alerts

## Advanced Features

### Other Temperature Sensors:

**DHT22**: Digital, includes humidity
```cpp
#include <DHT.h>
DHT dht(pin, DHT22);
float humidity = dht.readHumidity();
```

**DS18B20**: Digital, 1-Wire protocol
```cpp
#include <OneWire.h>
#include <DallasTemperature.h>
```

**Thermistor**: Requires calculation
```cpp
resistance = SERIESRESISTOR / (1023/reading - 1);
temperature = resistance / THERMISTORNOMINAL;
```

## Applications
- Weather stations
- HVAC control
- Server room monitoring
- Greenhouse automation
- 3D printer bed temperature
- Food safety monitoring

## What You've Learned
- Analog sensor interfacing
- Sensor calibration techniques
- Data smoothing with averaging
- Threshold-based control
- Temperature unit conversion
- Real-world sensor applications

## Next Steps
Ready for Program 6: RGB LED Control!

---

## 🌡️ MISSION THEME: WEATHER STATION COMMANDER

**Congratulations, Commander!** You've built a sophisticated weather monitoring system that would make any meteorologist proud!

### 🎯 Your Climate Control Mission:
Transform your Arduino into a professional weather station with real-time temperature monitoring, automatic fan control, and intelligent alert systems. You're now in command of your own climate!

### 🌟 What Makes This Special:
- **Precision monitoring**: Real-time temperature readings with data averaging for accuracy
- **Smart climate control**: Automatic fan activation when temperatures rise
- **Visual status system**: LED indicators that show temperature conditions at a glance
- **Alert system**: Warnings for extreme temperatures and rapid changes
- **Dual unit display**: Both Celsius and Fahrenheit readings
- **Professional calibration**: Industry-standard TMP36 sensor with voltage calculations

### 🏆 Commander Achievements to Unlock:
- **❄️ Ice Master**: Successfully detect temperatures below 10°C
- **🔥 Heat Detector**: Trigger high temperature alerts above 35°C
- **🎯 Precision Operator**: Maintain stable readings within ±1°C
- **💨 Climate Controller**: Activate automatic cooling system
- **📊 Data Analyst**: Interpret voltage-to-temperature conversions

### 🎮 Advanced Commander Challenges:
1. **🧊 Ice Bath Test**: Verify accuracy by testing in ice water (should read ~0°C)
2. **🌡️ Calibration Expert**: Fine-tune sensor readings against a reference thermometer
3. **⚡ Rapid Response**: Detect temperature changes faster than 5°C/minute
4. **🔄 Multi-Zone Control**: Add multiple sensors for different room monitoring
5. **📈 Trend Analysis**: Track temperature patterns over time

### 🏭 Real-World Applications:
- **Home automation**: Smart thermostat control
- **Industrial monitoring**: Server room temperature management
- **Agriculture**: Greenhouse climate control
- **Food safety**: Restaurant kitchen monitoring
- **Weather research**: Personal weather station data
- **3D printing**: Heated bed temperature control

### 🎖️ Why This Matters:
You've mastered the fundamentals of sensor interfacing, data processing, and automated control systems - the core skills used in:
- Smart home systems
- Industrial automation
- Weather monitoring networks
- Environmental research
- IoT (Internet of Things) devices

**🌟 Mission Complete!** You've earned the rank of Weather Station Commander and mastered the art of precision temperature monitoring!