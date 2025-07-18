# 🌈 Program 13: Mood Ring Light Circuit Diagram

## 🎯 **COLOR SCIENTIST MISSION**
Create an intelligent color-changing system that responds to environmental conditions and user interaction!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **RGB LED (Common Cathode)** (1x)
- **TMP36 Temperature Sensor** (1x)
- **Photoresistor (LDR)** (1x)
- **Push Button** (1x) - for mode selection
- **Potentiometer (10kΩ)** (1x) - for sensitivity adjustment
- **220Ω Resistors** (3x) - for RGB LED
- **10kΩ Resistors** (2x) - for LDR and button
- **Breadboard** (1x)
- **Jumper Wires** (15x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Mood Ring System
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │  D9,D10,D11 │────────────────┤ RGB LED Control │
    │             │                │                 │
    │         A0  │────────────────┤ Temperature     │
    │         A1  │────────────────┤ Light Sensor    │
    │         A2  │────────────────┤ Sensitivity     │
    │             │                │                 │
    │         D2  │────────────────┤ Mode Button     │
    │             │                │                 │
    │         5V  │────────────────┤ Power Rails     │
    │         GND │────────────────┤ Ground Rails    │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: RGB LED Understanding**
Common cathode RGB LED with three separate color channels:

```
RGB LED Pinout (Common Cathode):
┌─────────────────────┐
│  R   G   CC   B     │
│  │   │   │    │     │
│  1   2   3    4     │
└─────────────────────┘

Pin 1: Red Anode (+)
Pin 2: Green Anode (+)
Pin 3: Common Cathode (-)
Pin 4: Blue Anode (+)
```

### **Step 2: Breadboard Layout**
```
Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← RGB LED Red
│  2  2  .  .  .  .  .  .  .  .  │ ← RGB LED Green
│  3  3  .  .  .  .  .  .  .  .  │ ← RGB LED Common Cathode
│  4  4  .  .  .  .  .  .  .  .  │ ← RGB LED Blue
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  .  .  .  .  .  .  .  .  │ ← TMP36 VCC
│  7  7  .  .  .  .  .  .  .  .  │ ← TMP36 Signal
│  8  8  .  .  .  .  .  .  .  .  │ ← TMP36 GND
│  9  9  .  .  .  .  .  .  .  .  │
│ 10 10  .  .  .  .  .  .  .  .  │ ← LDR Pin 1
│ 11 11  .  .  .  .  .  .  .  .  │ ← LDR Pin 2
│ 12 12  .  .  .  .  .  .  .  .  │ ← LDR Resistor
│ 13 13  .  .  .  .  .  .  .  .  │
│ 14 14  .  .  .  .  .  .  .  .  │ ← Button Pin 1
│ 15 15  .  .  .  .  .  .  .  .  │ ← Button Pin 2
│ 16 16  .  .  .  .  .  .  .  .  │ ← Button Resistor
│ 17 17  .  .  .  .  .  .  .  .  │
│ 18 18  .  .  .  .  .  .  .  .  │ ← Potentiometer Pin 1
│ 19 19  .  .  .  .  .  .  .  .  │ ← Potentiometer Pin 2
│ 20 20  .  .  .  .  .  .  .  .  │ ← Potentiometer Pin 3
└─────────────────────────────────┘
```

### **Step 3: Install RGB LED**
Mount RGB LED with proper orientation:

```
RGB LED Installation:
┌─────────────────────────────────┐
│  1  1  R  .  .  .  .  .  .  .  │ ← Red anode
│  2  2  G  .  .  .  .  .  .  .  │ ← Green anode
│  3  3  C  .  .  .  .  .  .  .  │ ← Common cathode
│  4  4  B  .  .  .  .  .  .  .  │ ← Blue anode
└─────────────────────────────────┘
```

### **Step 4: Install Current-Limiting Resistors**
Each RGB channel needs a 220Ω resistor:

```
Resistor Installation:
┌─────────────────────────────────┐
│  1  1  R  Rr .  .  .  .  .  .  │ ← Red + resistor
│  2  2  G  Rg .  .  .  .  .  .  │ ← Green + resistor
│  3  3  C  ●  .  .  .  .  .  .  │ ← Common cathode to GND
│  4  4  B  Rb .  .  .  .  .  .  │ ← Blue + resistor
│  5  5  .  Rr─●  .  .  .  .  .  │ ← Red resistor to D9
│  6  6  .  Rg─●  .  .  .  .  .  │ ← Green resistor to D10
│  7  7  .  Rb─●  .  .  .  .  .  │ ← Blue resistor to D11
└─────────────────────────────────┘
```

### **Step 5: Install Temperature Sensor**
TMP36 for ambient temperature sensing:

```
TMP36 Installation:
┌─────────────────────────────────┐
│  8  8  T1 .  .  .  .  .  .  .  │ ← TMP36 VCC
│  9  9  T2 .  .  .  .  .  .  .  │ ← TMP36 Signal
│ 10 10  T3 .  .  .  .  .  .  .  │ ← TMP36 GND
│ 11 11  .  ●  .  .  .  .  .  .  │ ← TMP36 VCC to 5V
│ 12 12  .  ●  .  .  .  .  .  .  │ ← TMP36 Signal to A0
│ 13 13  .  ●  .  .  .  .  .  .  │ ← TMP36 GND to GND
└─────────────────────────────────┘
```

### **Step 6: Install Light Sensor**
LDR (Light Dependent Resistor) with pull-down resistor:

```
LDR Installation:
┌─────────────────────────────────┐
│ 14 14  L1 .  .  .  .  .  .  .  │ ← LDR Pin 1
│ 15 15  L2 LR .  .  .  .  .  .  │ ← LDR Pin 2 + resistor
│ 16 16  .  LR .  .  .  .  .  .  │ ← LDR resistor to GND
│ 17 17  .  ●  .  .  .  .  .  .  │ ← LDR to 5V
│ 18 18  .  ●  .  .  .  .  .  .  │ ← LDR signal to A1
│ 19 19  .  ●  .  .  .  .  .  .  │ ← LDR resistor to GND
└─────────────────────────────────┘
```

### **Step 7: Install Mode Button**
Button for cycling through different mood modes:

```
Button Installation:
┌─────────────────────────────────┐
│ 20 20  B1 BR .  .  .  .  .  .  │ ← Button + pull-up resistor
│ 21 21  B2 ●  .  .  .  .  .  .  │ ← Button to GND
│ 22 22  .  BR─●  .  .  .  .  .  │ ← Pull-up resistor to 5V
│ 23 23  .  ●  .  .  .  .  .  .  │ ← Button signal to D2
└─────────────────────────────────┘
```

### **Step 8: Install Sensitivity Potentiometer**
Potentiometer for adjusting sensor sensitivity:

```
Potentiometer Installation:
┌─────────────────────────────────┐
│ 24 24  P1 .  .  .  .  .  .  .  │ ← Potentiometer Pin 1
│ 25 25  P2 .  .  .  .  .  .  .  │ ← Potentiometer Pin 2 (wiper)
│ 26 26  P3 .  .  .  .  .  .  .  │ ← Potentiometer Pin 3
│ 27 27  .  ●  .  .  .  .  .  .  │ ← Potentiometer to 5V
│ 28 28  .  ●  .  .  .  .  .  .  │ ← Potentiometer wiper to A2
│ 29 29  .  ●  .  .  .  .  .  .  │ ← Potentiometer to GND
└─────────────────────────────────┘
```

### **Step 9: Connect All Wires**
```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  R  Rr─●  .  .  .  .  .  │ ← Red to D9
│  2  2  G  Rg─●  .  .  .  .  .  │ ← Green to D10
│  3  3  C  ●  .  .  .  .  .  .  │ ← Common cathode to GND
│  4  4  B  Rb─●  .  .  .  .  .  │ ← Blue to D11
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  T1─●  .  .  .  .  .  .  │ ← TMP36 VCC to 5V
│  7  7  T2─●  .  .  .  .  .  .  │ ← TMP36 Signal to A0
│  8  8  T3─●  .  .  .  .  .  .  │ ← TMP36 GND to GND
│  9  9  .  .  .  .  .  .  .  .  │
│ 10 10  L1─●  .  .  .  .  .  .  │ ← LDR to 5V
│ 11 11  L2─●──LR .  .  .  .  .  │ ← LDR to A1 + resistor
│ 12 12  .  LR─●  .  .  .  .  .  │ ← LDR resistor to GND
│ 13 13  .  .  .  .  .  .  .  .  │
│ 14 14  B1─●──BR .  .  .  .  .  │ ← Button to D2 + pull-up
│ 15 15  B2─●  .  .  .  .  .  .  │ ← Button to GND
│ 16 16  .  BR─●  .  .  .  .  .  │ ← Button resistor to 5V
│ 17 17  .  .  .  .  .  .  .  .  │
│ 18 18  P1─●  .  .  .  .  .  .  │ ← Potentiometer to 5V
│ 19 19  P2─●  .  .  .  .  .  .  │ ← Potentiometer wiper to A2
│ 20 20  P3─●  .  .  .  .  .  .  │ ← Potentiometer to GND
└─────────────────────────────────┘

● = Jumper wire connections
Rr = Red LED resistor (220Ω)
Rg = Green LED resistor (220Ω)
Rb = Blue LED resistor (220Ω)
LR = LDR resistor (10kΩ)
BR = Button resistor (10kΩ)
```

### **Step 10: Wire Connections Summary**
**RGB LED Connections:**
- D9 → Red channel (through 220Ω resistor)
- D10 → Green channel (through 220Ω resistor)
- D11 → Blue channel (through 220Ω resistor)
- GND → Common cathode

**Sensor Connections:**
- A0 → TMP36 output (temperature)
- A1 → LDR junction (light level)
- A2 → Potentiometer wiper (sensitivity)

**Control Connections:**
- D2 → Mode button (with pull-up resistor)

**Power Connections:**
- 5V → TMP36 VCC, LDR, Button pull-up, Potentiometer
- GND → TMP36 GND, LDR resistor, Button, Potentiometer, RGB LED common

---

## ⚡ **Circuit Explanation**

### **How Mood Ring Light Works:**
1. **Temperature sensor** detects environmental warmth
2. **Light sensor** measures ambient lighting conditions
3. **RGB LED** displays colors based on sensor inputs
4. **Mode button** switches between different color algorithms
5. **Potentiometer** adjusts sensitivity of sensor responses

### **Color Psychology:**
```
Temperature-based colors:
Cold (< 20°C)  → Blue (calm, cool)
Cool (20-24°C) → Green (balanced, natural)
Warm (24-28°C) → Yellow (energetic, happy)
Hot (> 28°C)   → Red (passionate, intense)

Light-based colors:
Dark    → Deep colors (purple, navy)
Dim     → Warm colors (orange, gold)
Bright  → Cool colors (cyan, white)
```

### **Sensor Processing:**
```
Temperature conversion:
TMP36: 10mV per °C, 500mV at 0°C
Temperature (°C) = (voltage - 0.5) × 100

Light level conversion:
LDR: Lower resistance = more light
Light % = map(analogRead(A1), 0, 1023, 0, 100)

Color mapping:
RGB values = f(temperature, light, mode, sensitivity)
```

### **Color Algorithms:**
```
Algorithm 1: Temperature dominant
Red = map(temperature, 15, 35, 0, 255)
Green = map(temperature, 15, 35, 255, 0)
Blue = map(temperature, 15, 35, 100, 0)

Algorithm 2: Light dominant
Red = map(lightLevel, 0, 100, 255, 0)
Green = map(lightLevel, 0, 100, 0, 255)
Blue = map(lightLevel, 0, 100, 50, 150)

Algorithm 3: Combined
Red = (tempValue + lightValue) / 2
Green = abs(tempValue - lightValue)
Blue = 255 - Red
```

---

## 🎨 **Visual Connection Guide**

```
   ARDUINO UNO
   ┌─────────────┐
   │  ┌─────────┐│
   │  │  RESET  ││
   │  └─────────┘│
   │             │
   │  D2 ●────────┼─── MODE BUTTON ──────────┐
   │             │                          │
   │  D9 ●────────┼─── RGB RED ─────────────┼─┐
   │ D10 ●────────┼─── RGB GREEN ───────────┼─┼─┐
   │ D11 ●────────┼─── RGB BLUE ────────────┼─┼─┼─┐
   │             │                          │ │ │ │
   │  A0 ●────────┼─── TEMPERATURE ─────────┼─┼─┼─┼─┐
   │  A1 ●────────┼─── LIGHT SENSOR ────────┼─┼─┼─┼─┼─┐
   │  A2 ●────────┼─── SENSITIVITY ─────────┼─┼─┼─┼─┼─┼─┐
   │             │                          │ │ │ │ │ │ │
   │  5V ●────────┼─── POWER ───────────────┼─┼─┼─┼─┼─┼─┼─┐
   │ GND ●────────┼─── GROUND ──────────────┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                          │ │ │ │ │ │ │ │ │
   └─────────────┘                          │ │ │ │ │ │ │ │ │
                                            │ │ │ │ │ │ │ │ │
   MODE BUTTON                              │ │ │ │ │ │ │ │ │
   ┌─────────────┐                          │ │ │ │ │ │ │ │ │
   │    ┌───┐    │                          │ │ │ │ │ │ │ │ │
   │    │BTN│    │                          │ │ │ │ │ │ │ │ │
   │    └───┘    │                          │ │ │ │ │ │ │ │ │
   │     │ │     │                          │ │ │ │ │ │ │ │ │
   │     │ └─────┼──────────────────────────┘ │ │ │ │ │ │ │ │
   │     │       │                            │ │ │ │ │ │ │ │
   │     └───────┼────────────────────────────┘ │ │ │ │ │ │ │
   │             │                              │ │ │ │ │ │ │
   │ [10kΩ]──────┼──────────────────────────────┘ │ │ │ │ │ │
   │             │                                │ │ │ │ │ │
   └─────────────┘                                │ │ │ │ │ │
                                                  │ │ │ │ │ │
   RGB LED                                        │ │ │ │ │ │
   ┌─────────────┐                                │ │ │ │ │ │
   │    ┌───┐    │                                │ │ │ │ │ │
   │    │RGB│    │                                │ │ │ │ │ │
   │    └───┘    │                                │ │ │ │ │ │
   │  R G CC B   │                                │ │ │ │ │ │
   │  │ │ │  │   │                                │ │ │ │ │ │
   │  └─┼─┼──┼───┼────────────────────────────────┘ │ │ │ │ │
   │    │ │  │   │                                  │ │ │ │ │
   │ [220Ω]┼──┼───┼──────────────────────────────────┘ │ │ │ │
   │    │ │  │   │                                    │ │ │ │
   │    └─┼──┼───┼──────────────────────────────────────┘ │ │ │
   │      │  │   │                                      │ │ │
   │   [220Ω]┼───┼────────────────────────────────────────┘ │ │
   │      │  │   │                                        │ │
   │      └──┼───┼──────────────────────────────────────────┘ │
   │         │   │                                          │
   │      [220Ω]─┼────────────────────────────────────────────┘
   │         │   │
   │         └───┼────────────────────────────────────────────┐
   │             │                                            │
   └─────────────┘                                            │
                                                              │
   TMP36 TEMPERATURE SENSOR                                   │
   ┌─────────────┐                                            │
   │  ┌─────────┐│                                            │
   │  │ TMP36   ││                                            │
   │  └─────────┘│                                            │
   │  1  2  3    │                                            │
   │  │  │  │    │                                            │
   │  └──┼──┼────┼────────────────────────────────────────────┘
   │     │  │    │                                            │
   │     └──┼────┼──────────────────────────────────────────────┐
   │        │    │                                              │
   │        └────┼────────────────────────────────────────────────┘
   │             │                                              │
   └─────────────┘                                              │
                                                                │
   LIGHT SENSOR (LDR)                                          │
   ┌─────────────┐                                              │
   │    ┌───┐    │                                              │
   │    │LDR│    │                                              │
   │    └───┘    │                                              │
   │     │ │     │                                              │
   │     │ └─────┼──────────────────────────────────────────────┘
   │     │       │                                              │
   │     └───────┼────────────────────────────────────────────────┐
   │             │                                                │
   │ [10kΩ]──────┼──────────────────────────────────────────────────┘
   │             │                                                │
   └─────────────┘                                                │
                                                                  │
   SENSITIVITY POTENTIOMETER                                      │
   ┌─────────────┐                                                │
   │      ┌─┐    │                                                │
   │   1──┤ │─3  │                                                │
   │      │ │    │                                                │
   │      └─┘    │                                                │
   │       │     │                                                │
   │       2     │                                                │
   │       │     │                                                │
   │       └─────┼────────────────────────────────────────────────┘
   │             │                                                │
   │   1─────────┼──────────────────────────────────────────────────┐
   │             │                                                  │
   │   3─────────┼────────────────────────────────────────────────────┘
   │             │                                                  │
   └─────────────┘                                                  │
                                                                    │
   POWER DISTRIBUTION                                               │
   ┌─────────────┐                                                  │
   │  5V ●───────┼──────────────────────────────────────────────────┘
   │             │                                                  │
   │ GND ●───────┼────────────────────────────────────────────────────┐
   │             │                                                    │
   └─────────────┘                                                    │
                                                                      │
                                                                      └─────────────┐
                                                                                    │
   GROUND BUS                                                                       │
   ┌─────────────┐                                                                  │
   │ GND ●───────┼──────────────────────────────────────────────────────────────────┘
   │             │
   └─────────────┘
```

---

## 🌈 **Mood Ring Programming**

### **Main Program Structure:**
```cpp
// Pin definitions
#define RED_PIN 9
#define GREEN_PIN 10
#define BLUE_PIN 11
#define TEMP_PIN A0
#define LIGHT_PIN A1
#define SENSITIVITY_PIN A2
#define BUTTON_PIN 2

// Mode definitions
enum MoodMode {
    TEMPERATURE_MODE,
    LIGHT_MODE,
    COMBINED_MODE,
    RAINBOW_MODE,
    PULSE_MODE
};

// Global variables
MoodMode currentMode = TEMPERATURE_MODE;
float temperature = 0;
int lightLevel = 0;
int sensitivity = 50;
unsigned long lastButtonPress = 0;
unsigned long lastUpdate = 0;

// Color structure
struct Color {
    int red;
    int green;
    int blue;
};

void setup() {
    Serial.begin(9600);
    
    // Initialize pins
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    pinMode(BLUE_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    
    // Initial color
    setColor(255, 0, 255);  // Purple startup
    
    Serial.println("Mood Ring Light Ready!");
    Serial.println("Press button to change modes");
    
    delay(1000);
}

void loop() {
    // Read sensors
    readSensors();
    
    // Check for mode button press
    if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButtonPress > 500) {
        changeMode();
        lastButtonPress = millis();
    }
    
    // Update color based on current mode
    if (millis() - lastUpdate > 100) {
        updateMoodColor();
        lastUpdate = millis();
    }
    
    delay(50);
}

void readSensors() {
    // Read temperature
    int tempReading = analogRead(TEMP_PIN);
    float voltage = (tempReading * 5.0) / 1024.0;
    temperature = (voltage - 0.5) * 100;
    
    // Read light level
    int lightReading = analogRead(LIGHT_PIN);
    lightLevel = map(lightReading, 0, 1023, 0, 100);
    
    // Read sensitivity
    int sensitivityReading = analogRead(SENSITIVITY_PIN);
    sensitivity = map(sensitivityReading, 0, 1023, 10, 100);
}

void setColor(int red, int green, int blue) {
    analogWrite(RED_PIN, red);
    analogWrite(GREEN_PIN, green);
    analogWrite(BLUE_PIN, blue);
}

void changeMode() {
    currentMode = (MoodMode)((currentMode + 1) % 5);
    
    String modeNames[] = {"Temperature", "Light", "Combined", "Rainbow", "Pulse"};
    Serial.print("Mode changed to: ");
    Serial.println(modeNames[currentMode]);
    
    // Flash to indicate mode change
    setColor(255, 255, 255);
    delay(200);
    setColor(0, 0, 0);
    delay(200);
}
```

### **Mood Color Algorithms:**
```cpp
void updateMoodColor() {
    Color moodColor;
    
    switch (currentMode) {
        case TEMPERATURE_MODE:
            moodColor = getTemperatureColor();
            break;
            
        case LIGHT_MODE:
            moodColor = getLightColor();
            break;
            
        case COMBINED_MODE:
            moodColor = getCombinedColor();
            break;
            
        case RAINBOW_MODE:
            moodColor = getRainbowColor();
            break;
            
        case PULSE_MODE:
            moodColor = getPulseColor();
            break;
    }
    
    // Apply sensitivity scaling
    moodColor.red = (moodColor.red * sensitivity) / 100;
    moodColor.green = (moodColor.green * sensitivity) / 100;
    moodColor.blue = (moodColor.blue * sensitivity) / 100;
    
    setColor(moodColor.red, moodColor.green, moodColor.blue);
}

Color getTemperatureColor() {
    Color color;
    
    // Temperature-based color mapping
    if (temperature < 18) {
        // Very cold - Deep blue
        color.red = 0;
        color.green = 0;
        color.blue = 255;
    } else if (temperature < 22) {
        // Cold - Blue to cyan
        int range = map(temperature * 10, 180, 219, 0, 255);
        color.red = 0;
        color.green = range;
        color.blue = 255;
    } else if (temperature < 26) {
        // Cool - Cyan to green
        int range = map(temperature * 10, 220, 259, 0, 255);
        color.red = 0;
        color.green = 255;
        color.blue = 255 - range;
    } else if (temperature < 30) {
        // Warm - Green to yellow
        int range = map(temperature * 10, 260, 299, 0, 255);
        color.red = range;
        color.green = 255;
        color.blue = 0;
    } else if (temperature < 34) {
        // Hot - Yellow to red
        int range = map(temperature * 10, 300, 339, 0, 255);
        color.red = 255;
        color.green = 255 - range;
        color.blue = 0;
    } else {
        // Very hot - Red
        color.red = 255;
        color.green = 0;
        color.blue = 0;
    }
    
    return color;
}

Color getLightColor() {
    Color color;
    
    // Light-based color mapping
    if (lightLevel < 20) {
        // Dark - Deep purple
        color.red = 100;
        color.green = 0;
        color.blue = 150;
    } else if (lightLevel < 40) {
        // Dim - Blue to purple
        int range = map(lightLevel, 20, 39, 0, 255);
        color.red = range;
        color.green = 0;
        color.blue = 255;
    } else if (lightLevel < 60) {
        // Medium - Purple to orange
        int range = map(lightLevel, 40, 59, 0, 255);
        color.red = 255;
        color.green = range;
        color.blue = 255 - range;
    } else if (lightLevel < 80) {
        // Bright - Orange to yellow
        int range = map(lightLevel, 60, 79, 0, 255);
        color.red = 255;
        color.green = 150 + range / 2;
        color.blue = 0;
    } else {
        // Very bright - White
        color.red = 255;
        color.green = 255;
        color.blue = 255;
    }
    
    return color;
}

Color getCombinedColor() {
    Color tempColor = getTemperatureColor();
    Color lightColor = getLightColor();
    Color combined;
    
    // Blend temperature and light colors
    combined.red = (tempColor.red + lightColor.red) / 2;
    combined.green = (tempColor.green + lightColor.green) / 2;
    combined.blue = (tempColor.blue + lightColor.blue) / 2;
    
    return combined;
}

Color getRainbowColor() {
    Color color;
    static int hue = 0;
    
    // HSV to RGB conversion for rainbow effect
    float h = hue / 60.0;
    float x = 1 - abs(fmod(h, 2) - 1);
    
    if (h < 1) {
        color.red = 255; color.green = x * 255; color.blue = 0;
    } else if (h < 2) {
        color.red = x * 255; color.green = 255; color.blue = 0;
    } else if (h < 3) {
        color.red = 0; color.green = 255; color.blue = x * 255;
    } else if (h < 4) {
        color.red = 0; color.green = x * 255; color.blue = 255;
    } else if (h < 5) {
        color.red = x * 255; color.green = 0; color.blue = 255;
    } else {
        color.red = 255; color.green = 0; color.blue = x * 255;
    }
    
    hue = (hue + 1) % 360;
    return color;
}

Color getPulseColor() {
    Color color;
    static int brightness = 0;
    static int direction = 1;
    
    // Get base color from temperature
    Color baseColor = getTemperatureColor();
    
    // Apply pulsing brightness
    color.red = (baseColor.red * brightness) / 255;
    color.green = (baseColor.green * brightness) / 255;
    color.blue = (baseColor.blue * brightness) / 255;
    
    brightness += direction * 5;
    if (brightness >= 255 || brightness <= 0) {
        direction *= -1;
    }
    
    return color;
}
```

### **Advanced Features:**
```cpp
// Smooth color transitions
void smoothTransition(Color from, Color to, int duration) {
    int steps = duration / 10;
    
    for (int i = 0; i <= steps; i++) {
        int red = map(i, 0, steps, from.red, to.red);
        int green = map(i, 0, steps, from.green, to.green);
        int blue = map(i, 0, steps, from.blue, to.blue);
        
        setColor(red, green, blue);
        delay(10);
    }
}

// Mood analysis
void analyzeMood() {
    String mood = "";
    
    if (temperature < 20 && lightLevel < 30) {
        mood = "Calm/Relaxed";
    } else if (temperature > 28 && lightLevel > 70) {
        mood = "Energetic/Alert";
    } else if (temperature > 25 && lightLevel < 40) {
        mood = "Cozy/Comfortable";
    } else if (temperature < 22 && lightLevel > 60) {
        mood = "Fresh/Awake";
    } else {
        mood = "Neutral/Balanced";
    }
    
    Serial.print("Detected mood: ");
    Serial.print(mood);
    Serial.print(" (T: ");
    Serial.print(temperature);
    Serial.print("°C, L: ");
    Serial.print(lightLevel);
    Serial.println("%)");
}

// Calibration mode
void calibrateColors() {
    Serial.println("=== COLOR CALIBRATION ===");
    
    // Test all primary colors
    Serial.println("Testing Red...");
    setColor(255, 0, 0);
    delay(2000);
    
    Serial.println("Testing Green...");
    setColor(0, 255, 0);
    delay(2000);
    
    Serial.println("Testing Blue...");
    setColor(0, 0, 255);
    delay(2000);
    
    Serial.println("Testing White...");
    setColor(255, 255, 255);
    delay(2000);
    
    Serial.println("Calibration complete!");
    setColor(0, 0, 0);
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check RGB LED connections** - Verify common cathode and resistor values
2. **Test sensor readings** - Ensure TMP36 and LDR are working properly
3. **Verify button wiring** - Check pull-up resistor and connections
4. **Confirm power connections** - All components need proper power

### **Sensor Test Program:**
```cpp
void sensorTest() {
    Serial.println("=== SENSOR TEST ===");
    
    for (int i = 0; i < 10; i++) {
        // Test temperature sensor
        int tempReading = analogRead(TEMP_PIN);
        float voltage = (tempReading * 5.0) / 1024.0;
        float temp = (voltage - 0.5) * 100;
        
        // Test light sensor
        int lightReading = analogRead(LIGHT_PIN);
        int lightPercent = map(lightReading, 0, 1023, 0, 100);
        
        // Test sensitivity
        int sensReading = analogRead(SENSITIVITY_PIN);
        int sensPercent = map(sensReading, 0, 1023, 0, 100);
        
        Serial.print("Temp: ");
        Serial.print(temp);
        Serial.print("°C, Light: ");
        Serial.print(lightPercent);
        Serial.print("%, Sensitivity: ");
        Serial.print(sensPercent);
        Serial.println("%");
        
        delay(1000);
    }
    
    Serial.println("Sensor test complete!");
}
```

### **Troubleshooting:**
- **No color changes**: Check RGB LED connections and resistor values
- **Wrong temperature readings**: Verify TMP36 pinout and power
- **Light sensor not working**: Check LDR and pull-down resistor
- **Button not responding**: Confirm pull-up resistor and connections
- **Colors too dim/bright**: Adjust sensitivity potentiometer

---

## 🎪 **Advanced Mood Features**

### **Mood Patterns:**
```cpp
// Breathing effect
void breathingEffect(Color baseColor, int duration) {
    for (int brightness = 0; brightness <= 255; brightness += 5) {
        Color color;
        color.red = (baseColor.red * brightness) / 255;
        color.green = (baseColor.green * brightness) / 255;
        color.blue = (baseColor.blue * brightness) / 255;
        
        setColor(color.red, color.green, color.blue);
        delay(duration / 102);  // 51 steps up, 51 steps down
    }
    
    for (int brightness = 255; brightness >= 0; brightness -= 5) {
        Color color;
        color.red = (baseColor.red * brightness) / 255;
        color.green = (baseColor.green * brightness) / 255;
        color.blue = (baseColor.blue * brightness) / 255;
        
        setColor(color.red, color.green, color.blue);
        delay(duration / 102);
    }
}

// Mood history tracking
struct MoodReading {
    float temperature;
    int lightLevel;
    Color color;
    unsigned long timestamp;
};

MoodReading moodHistory[24];  // 24 hours of data
int historyIndex = 0;

void recordMood() {
    moodHistory[historyIndex].temperature = temperature;
    moodHistory[historyIndex].lightLevel = lightLevel;
    moodHistory[historyIndex].color = getCurrentColor();
    moodHistory[historyIndex].timestamp = millis();
    
    historyIndex = (historyIndex + 1) % 24;
}

// Mood prediction
Color predictMood() {
    // Analyze recent patterns
    float avgTemp = 0;
    int avgLight = 0;
    
    for (int i = 0; i < 24; i++) {
        avgTemp += moodHistory[i].temperature;
        avgLight += moodHistory[i].lightLevel;
    }
    
    avgTemp /= 24;
    avgLight /= 24;
    
    // Predict based on trends
    if (avgTemp > temperature + 2) {
        // Getting cooler - shift to cooler colors
        return getTemperatureColor();
    } else if (avgLight > lightLevel + 20) {
        // Getting darker - shift to warmer colors
        return getLightColor();
    } else {
        // Stable - use current algorithm
        return getCombinedColor();
    }
}
```

---

## 🎉 **Success! You've Built a Mood Ring Light!**

**Congratulations, Color Scientist!** Your intelligent mood ring light system is now operational! You've learned environmental sensing, color theory, human-computer interaction, and adaptive systems - essential skills for IoT devices, smart home systems, and interactive art installations!

### **Next Steps:**
- Add wireless connectivity for remote control
- Create smartphone app integration
- Add more environmental sensors (humidity, air quality)
- Build wearable version with smaller components

### **Real-World Applications:**
- **Smart home**: Ambient lighting systems
- **Healthcare**: Mood monitoring and therapy
- **Entertainment**: Interactive art and gaming
- **Retail**: Atmosphere control and marketing
- **Education**: Science demonstrations and learning tools

---

*Color is the language of emotion - let your environment speak! Keep building! 🚀*