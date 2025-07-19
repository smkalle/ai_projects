# 🌡️ Program 5: Temperature Sensor Circuit Diagram

## 🎯 **WEATHER STATION COMMANDER MISSION**
Build your own weather monitoring station to track temperature changes!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **TMP36 Temperature Sensor** (1x) *or LM35*
- **LED** (1x - any color for status)
- **220Ω Resistor** (1x - for LED)
- **Breadboard** (1x)
- **Jumper Wires** (4x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         A0  │────────────────┤ TMP36 Signal    │
    │             │                │                 │
    │         D13 │────────────────┤ Status LED      │
    │             │                │                 │
    │         5V  │────────────────┤ TMP36 Power     │
    │             │                │                 │
    │         GND │────────────────┤ Common Ground   │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: Breadboard Layout**
```
Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← TMP36 Pin 1 (VCC)
│  2  2  .  .  .  .  .  .  .  .  │ ← TMP36 Pin 2 (Signal)
│  3  3  .  .  .  .  .  .  .  .  │ ← TMP36 Pin 3 (GND)
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  .  .  .  .  .  .  .  .  │ ← LED Anode
│  6  6  .  .  .  .  .  .  .  .  │ ← LED Cathode
└─────────────────────────────────┘
```

### **Step 2: Install TMP36 Temperature Sensor**
**IMPORTANT**: TMP36 has a specific pinout - be careful!

```
TMP36 Pinout (flat side facing you):
┌─────────────┐
│  1   2   3  │
│ VCC OUT GND │
└─────────────┘

Installation:
┌─────────────────────────────────┐
│  1  1  V  .  .  .  .  .  .  .  │ ← Pin 1 (VCC) to power
│  2  2  S  .  .  .  .  .  .  .  │ ← Pin 2 (Signal) to A0
│  3  3  G  .  .  .  .  .  .  .  │ ← Pin 3 (GND) to ground
└─────────────────────────────────┘
```

### **Step 3: Install Status LED**
- **Long leg (anode)** goes to Row 5, column 'a'
- **Short leg (cathode)** goes to Row 6, column 'a'

```
LED Installation:
┌─────────────────────────────────┐
│  1  1  V  .  .  .  .  .  .  .  │ ← TMP36 VCC
│  2  2  S  .  .  .  .  .  .  .  │ ← TMP36 Signal
│  3  3  G  .  .  .  .  .  .  .  │ ← TMP36 GND
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  +  .  .  .  .  .  .  .  │ ← LED long leg (anode)
│  6  6  -  .  .  .  .  .  .  .  │ ← LED short leg (cathode)
└─────────────────────────────────┘
```

### **Step 4: Install LED Resistor**
- **One end** goes to Row 5, column 'b' (same row as LED anode)
- **Other end** goes to Row 7, column 'b'

```
Resistor Installation:
┌─────────────────────────────────┐
│  1  1  V  .  .  .  .  .  .  .  │ ← TMP36 VCC
│  2  2  S  .  .  .  .  .  .  .  │ ← TMP36 Signal
│  3  3  G  .  .  .  .  .  .  .  │ ← TMP36 GND
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  +  R  .  .  .  .  .  .  │ ← LED + resistor
│  6  6  -  │  .  .  .  .  .  .  │ ← LED cathode
│  7  7  .  R  .  .  .  .  .  .  │ ← Resistor to D13
└─────────────────────────────────┘
```

### **Step 5: Connect All Wires**
- **Red wire**: Arduino 5V → Row 1, column 'c' (TMP36 VCC)
- **Blue wire**: Arduino A0 → Row 2, column 'c' (TMP36 Signal)
- **Green wire**: Arduino D13 → Row 7, column 'c' (LED through resistor)
- **Black wire**: Arduino GND → Row 3, column 'c' and Row 6, column 'c'

```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  V──●  .  .  .  .  .  .  │ ← 5V power wire
│  2  2  S──●  .  .  .  .  .  .  │ ← A0 signal wire
│  3  3  G──●  .  .  .  .  .  .  │ ← Ground wire
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  +──R──.  .  .  .  .  .  │ ← LED + resistor
│  6  6  -──●  .  .  .  .  .  .  │ ← LED cathode + ground
│  7  7  .  R──●  .  .  .  .  .  │ ← Resistor + D13 wire
└─────────────────────────────────┘

● = Jumper wire connection
R = 220Ω Resistor
V = TMP36 VCC pin
S = TMP36 Signal pin
G = TMP36 GND pin
+ = LED long leg (anode)
- = LED short leg (cathode)
```

---

## ⚡ **Circuit Explanation**

### **How It Works:**
1. **TMP36 sensor** converts temperature to voltage (10mV per °C)
2. **Arduino A0** reads the analog voltage signal
3. **Code converts** voltage back to temperature in Celsius/Fahrenheit
4. **Status LED** shows when readings are being taken

### **Temperature Formula:**
```
TMP36 Output: 10mV per °C, 500mV at 0°C

Temperature (°C) = (voltage - 0.5) × 100
Temperature (°F) = (Temperature_C × 9/5) + 32

Example:
750mV = (0.75 - 0.5) × 100 = 25°C = 77°F
```

### **Voltage-to-Temperature Conversion:**
```
Voltage Reading → ADC Value → Temperature
     ↓              ↓            ↓
   750mV         153/1024     25°C
   (0.75V)      (5V scale)    (77°F)
```

### **Safety Notes:**
- **TMP36 pinout** is critical - wrong connections can damage sensor
- **Operating range**: -40°C to +125°C (-40°F to +257°F)
- **Supply voltage**: 2.7V to 5.5V (perfect for Arduino)

---

## 🎨 **Visual Connection Guide**

```
   ARDUINO UNO
   ┌─────────────┐
   │  ┌─────────┐│
   │  │  RESET  ││
   │  └─────────┘│
   │             │
   │ A0  ●────────┼─── BLUE WIRE ──────┐
   │             │                    │
   │ D13 ●────────┼─── GREEN WIRE ─────┼─┐
   │             │                    │ │
   │ 5V  ●────────┼─── RED WIRE ───────┼─┼─┐
   │             │                    │ │ │
   │ GND ●────────┼─── BLACK WIRE ─────┼─┼─┼─┐
   │             │                    │ │ │ │
   └─────────────┘                    │ │ │ │
                                      │ │ │ │
   BREADBOARD - TMP36 SENSOR          │ │ │ │
   ┌─────────────┐                    │ │ │ │
   │             │                    │ │ │ │
   │ ●─[TMP36]─● │────────────────────┘ │ │ │
   │  1  2  3    │                      │ │ │
   │ VCC OUT GND │                      │ │ │
   └─────────────┘                      │ │ │
                                        │ │ │
   STATUS LED WITH RESISTOR             │ │ │
   ┌─────────────┐                      │ │ │
   │             │                      │ │ │
   │ ●───[220Ω]──┼──────────────────────┘ │ │
   │             │                        │ │
   │ ●───[LED]───┼────────────────────────┘ │
   │             │                          │
   │ ●───────────┼──────────────────────────┘
   │             │
   └─────────────┘
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check TMP36 pinout** - flat side facing you: VCC, OUT, GND
2. **Verify power connections** - 5V to pin 1, GND to pin 3
3. **Confirm signal wire** - pin 2 to A0
4. **Test LED polarity** - long leg to resistor

### **Temperature Calibration:**
```cpp
// Test with known temperatures
float testTemp = 25.0;  // Room temperature
float voltage = (testTemp + 50) / 100.0;
int adcValue = voltage * 1024 / 5.0;
Serial.print("Expected ADC: ");
Serial.println(adcValue);
```

### **Serial Monitor Output:**
```
Temperature Sensor Test
Raw ADC: 153
Voltage: 0.75V
Temperature: 25.0°C (77.0°F)
Status: Normal
```

### **Troubleshooting:**
- **No readings**: Check TMP36 pinout and power
- **Wrong values**: Verify voltage calculation formula
- **Erratic readings**: Check for loose connections
- **LED not working**: Check resistor and LED polarity

### **Common Issues:**
```
Problem: Negative temperatures indoors
Solution: Check TMP36 pinout (VCC and GND may be swapped)

Problem: Very high temperatures (>80°C)
Solution: Verify A0 connection and TMP36 orientation

Problem: Readings jump around
Solution: Add 0.1µF capacitor across VCC and GND
```

---

## 🌡️ **Weather Station Features**

### **Temperature Monitoring:**
```cpp
// Temperature thresholds
#define COLD_TEMP   15.0    // Below 15°C
#define NORMAL_TEMP 25.0    // 15-25°C
#define HOT_TEMP    30.0    // Above 30°C

// LED status indicators
if (temperature < COLD_TEMP) {
    // Slow blink - Cold
    digitalWrite(13, HIGH);
    delay(1000);
    digitalWrite(13, LOW);
    delay(1000);
} else if (temperature > HOT_TEMP) {
    // Fast blink - Hot
    digitalWrite(13, HIGH);
    delay(200);
    digitalWrite(13, LOW);
    delay(200);
} else {
    // Steady on - Normal
    digitalWrite(13, HIGH);
}
```

### **Data Logging:**
```cpp
// Log temperature every minute
unsigned long lastReading = 0;
const unsigned long interval = 60000; // 1 minute

if (millis() - lastReading > interval) {
    float temp = readTemperature();
    logTemperature(temp);
    lastReading = millis();
}
```

### **Temperature Alerts:**
```cpp
// Alert system
void checkTemperatureAlerts(float temp) {
    if (temp > 35.0) {
        Serial.println("ALERT: High temperature detected!");
        // Flash LED rapidly
        for (int i = 0; i < 10; i++) {
            digitalWrite(13, HIGH);
            delay(100);
            digitalWrite(13, LOW);
            delay(100);
        }
    }
}
```

---

## 🎉 **Success! You've Built a Weather Station!**

**Congratulations, Weather Station Commander!** Your temperature monitoring system is now operational! You've learned analog sensor interfacing, voltage-to-temperature conversion, and real-time data monitoring - essential skills for environmental sensing and data acquisition!

### **Next Steps:**
- Add more sensors (humidity, pressure)
- Create temperature logging system
- Build temperature-controlled fan
- Add wireless data transmission

### **Advanced Features:**
```cpp
// Temperature trend analysis
float temperatureHistory[10];
int historyIndex = 0;

// Calculate temperature trend
float calculateTrend() {
    float sum = 0;
    for (int i = 1; i < 10; i++) {
        sum += (temperatureHistory[i] - temperatureHistory[i-1]);
    }
    return sum / 9.0;  // Average change per reading
}

// Predict temperature
float predictTemperature(float trend, int minutesAhead) {
    return temperatureHistory[historyIndex] + (trend * minutesAhead);
}
```

### **Real-World Applications:**
- **Home automation**: Climate control systems
- **Agriculture**: Greenhouse monitoring
- **Industrial**: Process temperature control
- **Weather stations**: Environmental monitoring
- **Food safety**: Cold chain monitoring

---

*Stay curious about the world around you! Keep building! 🚀*