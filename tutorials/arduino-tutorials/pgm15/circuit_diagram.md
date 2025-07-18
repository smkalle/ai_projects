# 🔒 Program 15: Secret Knock Detector Circuit Diagram

## 🎯 **SECURITY CODE BREAKER MISSION**
Build an intelligent security system that recognizes secret knock patterns and controls access!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **Piezo Buzzer** (1x) - for knock detection and feedback
- **Servo Motor (SG90)** (1x) - for lock mechanism
- **LEDs** (3x - Red, Green, Blue) - for status indication
- **Push Button** (1x) - for programming mode
- **Potentiometer (10kΩ)** (1x) - for sensitivity adjustment
- **220Ω Resistors** (3x) - for LEDs
- **10kΩ Resistor** (1x) - for button pull-up
- **1MΩ Resistor** (1x) - for piezo sensor
- **Breadboard** (1x)
- **Jumper Wires** (12x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Security System
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         A0  │────────────────┤ Knock Sensor    │
    │         A1  │────────────────┤ Sensitivity     │
    │             │                │                 │
    │         D9  │────────────────┤ Servo Lock      │
    │             │                │                 │
    │         D2  │────────────────┤ Program Button  │
    │             │                │                 │
    │         D5  │────────────────┤ Red LED         │
    │         D6  │────────────────┤ Green LED       │
    │         D7  │────────────────┤ Blue LED        │
    │             │                │                 │
    │         D8  │────────────────┤ Feedback Buzzer │
    │             │                │                 │
    │         5V  │────────────────┤ Power Rails     │
    │         GND │────────────────┤ Ground Rails    │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: Knock Sensor Setup**
Piezo buzzer acts as both knock sensor and audio feedback:

```
Piezo Sensor Configuration:
┌─────────────┐
│    ┌───┐    │
│    │ + │    │ ← Positive to A0 (through 1MΩ resistor)
│    │ - │    │ ← Negative to GND
│    └───┘    │
└─────────────┘

The piezo element generates voltage when vibrated,
allowing it to detect knocks and taps.
```

### **Step 2: Breadboard Layout**
```
Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← Knock sensor positive
│  2  2  .  .  .  .  .  .  .  .  │ ← Knock sensor negative
│  3  3  .  .  .  .  .  .  .  .  │ ← Sensor resistor
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  .  .  .  .  .  .  .  .  │ ← Servo signal
│  6  6  .  .  .  .  .  .  .  .  │ ← Servo power
│  7  7  .  .  .  .  .  .  .  .  │ ← Servo ground
│  8  8  .  .  .  .  .  .  .  .  │
│  9  9  .  .  .  .  .  .  .  .  │ ← Red LED
│ 10 10  .  .  .  .  .  .  .  .  │ ← Green LED
│ 11 11  .  .  .  .  .  .  .  .  │ ← Blue LED
│ 12 12  .  .  .  .  .  .  .  .  │
│ 13 13  .  .  .  .  .  .  .  .  │ ← Program button
│ 14 14  .  .  .  .  .  .  .  .  │ ← Button pull-up
│ 15 15  .  .  .  .  .  .  .  .  │
│ 16 16  .  .  .  .  .  .  .  .  │ ← Feedback buzzer
│ 17 17  .  .  .  .  .  .  .  .  │
│ 18 18  .  .  .  .  .  .  .  .  │ ← Sensitivity pot
│ 19 19  .  .  .  .  .  .  .  .  │
│ 20 20  .  .  .  .  .  .  .  .  │
└─────────────────────────────────┘
```

### **Step 3: Install Knock Sensor**
Piezo element for vibration detection:

```
Knock Sensor Installation:
┌─────────────────────────────────┐
│  1  1  P+ PR .  .  .  .  .  .  │ ← Piezo positive + 1MΩ resistor
│  2  2  P- ●  .  .  .  .  .  .  │ ← Piezo negative to GND
│  3  3  .  PR─●  .  .  .  .  .  │ ← Resistor to A0
│  4  4  .  ●  .  .  .  .  .  .  │ ← Resistor to GND (bias)
└─────────────────────────────────┘
```

### **Step 4: Install Servo Lock**
SG90 servo motor for lock mechanism:

```
Servo Installation:
┌─────────────────────────────────┐
│  5  5  S  .  .  .  .  .  .  .  │ ← Servo signal (Orange)
│  6  6  V  .  .  .  .  .  .  .  │ ← Servo VCC (Red)
│  7  7  G  .  .  .  .  .  .  .  │ ← Servo GND (Brown)
│  8  8  .  ●  .  .  .  .  .  .  │ ← Signal to D9
│  9  9  .  ●  .  .  .  .  .  .  │ ← VCC to 5V
│ 10 10  .  ●  .  .  .  .  .  .  │ ← GND to Ground
└─────────────────────────────────┘
```

### **Step 5: Install Status LEDs**
Three LEDs for different system states:

```
LED Installation:
┌─────────────────────────────────┐
│ 11 11  R+ Rr .  .  .  .  .  .  │ ← Red LED + resistor
│ 12 12  R- ●  .  .  .  .  .  .  │ ← Red LED cathode to GND
│ 13 13  G+ Rg .  .  .  .  .  .  │ ← Green LED + resistor
│ 14 14  G- ●  .  .  .  .  .  .  │ ← Green LED cathode to GND
│ 15 15  B+ Rb .  .  .  .  .  .  │ ← Blue LED + resistor
│ 16 16  B- ●  .  .  .  .  .  .  │ ← Blue LED cathode to GND
│ 17 17  .  Rr─●  .  .  .  .  .  │ ← Red resistor to D5
│ 18 18  .  Rg─●  .  .  .  .  .  │ ← Green resistor to D6
│ 19 19  .  Rb─●  .  .  .  .  .  │ ← Blue resistor to D7
└─────────────────────────────────┘
```

### **Step 6: Install Program Button**
Button for entering programming mode:

```
Button Installation:
┌─────────────────────────────────┐
│ 20 20  B1 BR .  .  .  .  .  .  │ ← Button + pull-up resistor
│ 21 21  B2 ●  .  .  .  .  .  .  │ ← Button to GND
│ 22 22  .  BR─●  .  .  .  .  .  │ ← Pull-up resistor to 5V
│ 23 23  .  ●  .  .  .  .  .  .  │ ← Button signal to D2
└─────────────────────────────────┘
```

### **Step 7: Install Feedback Buzzer**
Separate buzzer for audio feedback:

```
Feedback Buzzer Installation:
┌─────────────────────────────────┐
│ 24 24  F+ .  .  .  .  .  .  .  │ ← Feedback buzzer positive
│ 25 25  F- .  .  .  .  .  .  .  │ ← Feedback buzzer negative
│ 26 26  .  ●  .  .  .  .  .  .  │ ← Buzzer positive to D8
│ 27 27  .  ●  .  .  .  .  .  .  │ ← Buzzer negative to GND
└─────────────────────────────────┘
```

### **Step 8: Install Sensitivity Control**
Potentiometer for knock sensitivity adjustment:

```
Sensitivity Potentiometer:
┌─────────────────────────────────┐
│ 28 28  S1 .  .  .  .  .  .  .  │ ← Potentiometer pin 1
│ 29 29  S2 .  .  .  .  .  .  .  │ ← Potentiometer pin 2 (wiper)
│ 30 30  S3 .  .  .  .  .  .  .  │ ← Potentiometer pin 3
│ 31 31  .  ●  .  .  .  .  .  .  │ ← Pin 1 to 5V
│ 32 32  .  ●  .  .  .  .  .  .  │ ← Wiper to A1
│ 33 33  .  ●  .  .  .  .  .  .  │ ← Pin 3 to GND
└─────────────────────────────────┘
```

### **Step 9: Connect All Wires**
```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  P+ PR─●  .  .  .  .  .  │ ← Piezo + to A0
│  2  2  P- ●  .  .  .  .  .  .  │ ← Piezo - to GND
│  3  3  .  PR─●  .  .  .  .  .  │ ← Resistor bias to GND
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  S  ●  .  .  .  .  .  .  │ ← Servo signal to D9
│  6  6  V  ●  .  .  .  .  .  .  │ ← Servo VCC to 5V
│  7  7  G  ●  .  .  .  .  .  .  │ ← Servo GND to Ground
│  8  8  .  .  .  .  .  .  .  .  │
│  9  9  R+ Rr─●  .  .  .  .  .  │ ← Red LED to D5
│ 10 10  R- ●  .  .  .  .  .  .  │ ← Red LED cathode to GND
│ 11 11  G+ Rg─●  .  .  .  .  .  │ ← Green LED to D6
│ 12 12  G- ●  .  .  .  .  .  .  │ ← Green LED cathode to GND
│ 13 13  B+ Rb─●  .  .  .  .  .  │ ← Blue LED to D7
│ 14 14  B- ●  .  .  .  .  .  .  │ ← Blue LED cathode to GND
│ 15 15  .  .  .  .  .  .  .  .  │
│ 16 16  B1─●──BR .  .  .  .  .  │ ← Button to D2 + pull-up
│ 17 17  B2─●  .  .  .  .  .  .  │ ← Button to GND
│ 18 18  .  BR─●  .  .  .  .  .  │ ← Button resistor to 5V
│ 19 19  .  .  .  .  .  .  .  .  │
│ 20 20  F+ ●  .  .  .  .  .  .  │ ← Feedback buzzer to D8
│ 21 21  F- ●  .  .  .  .  .  .  │ ← Feedback buzzer to GND
│ 22 22  .  .  .  .  .  .  .  .  │
│ 23 23  S1─●  .  .  .  .  .  .  │ ← Sensitivity pot to 5V
│ 24 24  S2─●  .  .  .  .  .  .  │ ← Sensitivity wiper to A1
│ 25 25  S3─●  .  .  .  .  .  .  │ ← Sensitivity pot to GND
└─────────────────────────────────┘

● = Jumper wire connections
PR = 1MΩ resistor for piezo sensor
Rr = 220Ω resistor for Red LED
Rg = 220Ω resistor for Green LED
Rb = 220Ω resistor for Blue LED
BR = 10kΩ pull-up resistor for button
```

### **Step 10: Wire Connections Summary**
**Knock Detection:**
- A0 → Piezo sensor positive (through 1MΩ resistor)
- GND → Piezo sensor negative
- A1 → Sensitivity potentiometer wiper

**Lock Mechanism:**
- D9 → Servo signal wire
- 5V → Servo power (red wire)
- GND → Servo ground (brown wire)

**Status Indicators:**
- D5 → Red LED (through 220Ω resistor)
- D6 → Green LED (through 220Ω resistor)
- D7 → Blue LED (through 220Ω resistor)
- GND → All LED cathodes

**Control and Feedback:**
- D2 → Program button (with pull-up resistor)
- D8 → Feedback buzzer
- GND → Button and buzzer grounds

**Power Distribution:**
- 5V → Servo, sensitivity pot, button pull-up
- GND → All negative terminals

---

## ⚡ **Circuit Explanation**

### **How Knock Detection Works:**
1. **Piezo element** generates voltage when vibrated
2. **1MΩ resistor** provides proper input impedance
3. **Arduino ADC** measures voltage spikes from knocks
4. **Pattern recognition** compares timing and intensity
5. **Servo lock** opens when correct pattern detected

### **Knock Pattern Analysis:**
```
Knock Pattern Structure:
- Timing between knocks (milliseconds)
- Intensity of each knock (voltage amplitude)
- Total number of knocks in sequence
- Rhythm and cadence recognition

Example Pattern:
KNOCK-pause-KNOCK-KNOCK-pause-KNOCK
 300ms    100ms 100ms    400ms
```

### **Piezo Sensor Characteristics:**
```
Piezo Element Properties:
- Voltage output: 0-5V (depends on impact)
- Frequency response: 1-10kHz typical
- Sensitivity: Adjustable via potentiometer
- Dual function: Sensor and sound generator

Voltage-to-Knock Mapping:
0-100 mV:   No knock (noise floor)
100-500 mV: Light knock
500-1000 mV: Medium knock
1000+ mV:   Strong knock
```

### **Security States:**
```
System States:
LOCKED:     Red LED on, servo at 0°
UNLOCKED:   Green LED on, servo at 90°
LISTENING:  Blue LED blinking
PROGRAMMING: All LEDs cycling
ACCESS_DENIED: Red LED flashing rapidly
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
   │  A0 ●────────┼─── KNOCK SENSOR ─────────┐
   │  A1 ●────────┼─── SENSITIVITY ──────────┼─┐
   │             │                          │ │
   │  D2 ●────────┼─── PROGRAM BUTTON ───────┼─┼─┐
   │             │                          │ │ │
   │  D5 ●────────┼─── RED LED ──────────────┼─┼─┼─┐
   │  D6 ●────────┼─── GREEN LED ────────────┼─┼─┼─┼─┐
   │  D7 ●────────┼─── BLUE LED ─────────────┼─┼─┼─┼─┼─┐
   │  D8 ●────────┼─── FEEDBACK BUZZER ──────┼─┼─┼─┼─┼─┼─┐
   │  D9 ●────────┼─── SERVO LOCK ───────────┼─┼─┼─┼─┼─┼─┼─┐
   │             │                          │ │ │ │ │ │ │ │
   │  5V ●────────┼─── POWER ────────────────┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ GND ●────────┼─── GROUND ───────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                          │ │ │ │ │ │ │ │ │ │
   └─────────────┘                          │ │ │ │ │ │ │ │ │ │
                                            │ │ │ │ │ │ │ │ │ │
   KNOCK SENSOR (PIEZO)                     │ │ │ │ │ │ │ │ │ │
   ┌─────────────┐                          │ │ │ │ │ │ │ │ │ │
   │    ┌───┐    │                          │ │ │ │ │ │ │ │ │ │
   │    │ + │    │                          │ │ │ │ │ │ │ │ │ │
   │    │ - │    │                          │ │ │ │ │ │ │ │ │ │
   │    └───┘    │                          │ │ │ │ │ │ │ │ │ │
   │     │ │     │                          │ │ │ │ │ │ │ │ │ │
   │     │ └─────┼──────────────────────────┘ │ │ │ │ │ │ │ │ │
   │     │       │                            │ │ │ │ │ │ │ │ │
   │ [1MΩ]───────┼────────────────────────────┘ │ │ │ │ │ │ │ │
   │     │       │                              │ │ │ │ │ │ │ │
   │     └───────┼──────────────────────────────┘ │ │ │ │ │ │ │
   │             │                                │ │ │ │ │ │ │
   └─────────────┘                                │ │ │ │ │ │ │
                                                  │ │ │ │ │ │ │
   SENSITIVITY POTENTIOMETER                      │ │ │ │ │ │ │
   ┌─────────────┐                                │ │ │ │ │ │ │
   │      ┌─┐    │                                │ │ │ │ │ │ │
   │   1──┤ │─3  │                                │ │ │ │ │ │ │
   │      │ │    │                                │ │ │ │ │ │ │
   │      └─┘    │                                │ │ │ │ │ │ │
   │       │     │                                │ │ │ │ │ │ │
   │       2     │                                │ │ │ │ │ │ │
   │       │     │                                │ │ │ │ │ │ │
   │       └─────┼────────────────────────────────┘ │ │ │ │ │ │
   │             │                                  │ │ │ │ │ │
   │   1─────────┼──────────────────────────────────┘ │ │ │ │ │
   │             │                                    │ │ │ │ │
   │   3─────────┼────────────────────────────────────┘ │ │ │ │
   │             │                                      │ │ │ │
   └─────────────┘                                      │ │ │ │
                                                        │ │ │ │
   PROGRAM BUTTON                                       │ │ │ │
   ┌─────────────┐                                      │ │ │ │
   │    ┌───┐    │                                      │ │ │ │
   │    │BTN│    │                                      │ │ │ │
   │    └───┘    │                                      │ │ │ │
   │     │ │     │                                      │ │ │ │
   │     │ └─────┼──────────────────────────────────────┘ │ │ │
   │     │       │                                        │ │ │
   │     └───────┼────────────────────────────────────────┘ │ │
   │             │                                          │ │
   │ [10kΩ]──────┼──────────────────────────────────────────┘ │
   │             │                                            │
   └─────────────┘                                            │
                                                              │
   STATUS LEDS                                                │
   ┌─────────────┐                                            │
   │             │                                            │
   │ ●─[220Ω]────┼────────────────────────────────────────────┘
   │             │                                            │
   │ ●─[RED]─────┼──────────────────────────────────────────────┐
   │             │                                              │
   │ ●─[220Ω]────┼──────────────────────────────────────────────┼─┐
   │             │                                              │ │
   │ ●─[GREEN]───┼────────────────────────────────────────────────┼─┼─┐
   │             │                                              │ │ │
   │ ●─[220Ω]────┼──────────────────────────────────────────────┼─┼─┼─┐
   │             │                                              │ │ │ │
   │ ●─[BLUE]────┼────────────────────────────────────────────────┼─┼─┼─┼─┐
   │             │                                              │ │ │ │ │
   │ ●───────────┼──────────────────────────────────────────────┼─┼─┼─┼─┼─┐
   │             │                                              │ │ │ │ │ │
   └─────────────┘                                              │ │ │ │ │ │
                                                                │ │ │ │ │ │
   FEEDBACK BUZZER                                              │ │ │ │ │ │
   ┌─────────────┐                                              │ │ │ │ │ │
   │    ┌───┐    │                                              │ │ │ │ │ │
   │    │ + │    │                                              │ │ │ │ │ │
   │    │ - │    │                                              │ │ │ │ │ │
   │    └───┘    │                                              │ │ │ │ │ │
   │     │ │     │                                              │ │ │ │ │ │
   │     │ └─────┼──────────────────────────────────────────────┘ │ │ │ │ │
   │     │       │                                                │ │ │ │ │
   │     └───────┼────────────────────────────────────────────────┘ │ │ │ │
   │             │                                                  │ │ │ │
   └─────────────┘                                                  │ │ │ │
                                                                    │ │ │ │
   SERVO LOCK                                                       │ │ │ │
   ┌─────────────┐                                                  │ │ │ │
   │    SG90     │                                                  │ │ │ │
   │  ┌─────────┐│                                                  │ │ │ │
   │  │ LOCK    ││                                                  │ │ │ │
   │  │ ARM     ││                                                  │ │ │ │
   │  └─────────┘│                                                  │ │ │ │
   │  O  R  B    │                                                  │ │ │ │
   │  │  │  │    │                                                  │ │ │ │
   │  └──┼──┼────┼──────────────────────────────────────────────────┘ │ │ │
   │     │  │    │                                                    │ │ │
   │     └──┼────┼────────────────────────────────────────────────────┘ │ │
   │        │    │                                                      │ │
   │        └────┼──────────────────────────────────────────────────────┘ │
   │             │                                                        │
   └─────────────┘                                                        │
                                                                          │
   POWER DISTRIBUTION                                                     │
   ┌─────────────┐                                                        │
   │  5V ●───────┼────────────────────────────────────────────────────────┘
   │             │                                                        │
   │ GND ●───────┼──────────────────────────────────────────────────────────┐
   │             │                                                          │
   └─────────────┘                                                          │
                                                                            │
   GROUND BUS                                                               │
   ┌─────────────┐                                                          │
   │ GND ●───────┼──────────────────────────────────────────────────────────┘
   │             │
   └─────────────┘
```

---

## 🔐 **Secret Knock Programming**

### **Main Program Structure:**
```cpp
#include <Servo.h>
#include <EEPROM.h>

// Pin definitions
#define KNOCK_SENSOR A0
#define SENSITIVITY_POT A1
#define PROGRAM_BUTTON 2
#define RED_LED 5
#define GREEN_LED 6
#define BLUE_LED 7
#define FEEDBACK_BUZZER 8
#define SERVO_LOCK 9

// Servo and timing constants
Servo lockServo;
#define LOCKED_POSITION 0
#define UNLOCKED_POSITION 90
#define MAX_KNOCKS 10
#define KNOCK_TIMEOUT 3000
#define UNLOCK_DURATION 5000

// System states
enum SystemState {
    LOCKED,
    LISTENING,
    PROGRAMMING,
    UNLOCKED,
    ACCESS_DENIED
};

// Knock pattern structure
struct KnockPattern {
    int intervals[MAX_KNOCKS];
    int knockCount;
    int tolerance;
};

// Global variables
SystemState currentState = LOCKED;
KnockPattern secretPattern;
KnockPattern attemptPattern;
int knockThreshold = 100;
unsigned long lastKnockTime = 0;
unsigned long unlockTime = 0;
bool isLocked = true;

void setup() {
    Serial.begin(9600);
    
    // Initialize pins
    pinMode(KNOCK_SENSOR, INPUT);
    pinMode(SENSITIVITY_POT, INPUT);
    pinMode(PROGRAM_BUTTON, INPUT_PULLUP);
    pinMode(RED_LED, OUTPUT);
    pinMode(GREEN_LED, OUTPUT);
    pinMode(BLUE_LED, OUTPUT);
    pinMode(FEEDBACK_BUZZER, OUTPUT);
    
    // Initialize servo
    lockServo.attach(SERVO_LOCK);
    lockServo.write(LOCKED_POSITION);
    
    // Load secret pattern from EEPROM
    loadSecretPattern();
    
    // Set initial state
    setState(LOCKED);
    
    Serial.println("Secret Knock Detector Ready");
    Serial.println("Hold program button while knocking to set new pattern");
}

void loop() {
    // Update sensitivity from potentiometer
    updateSensitivity();
    
    // Check for programming mode
    if (digitalRead(PROGRAM_BUTTON) == LOW) {
        if (currentState != PROGRAMMING) {
            setState(PROGRAMMING);
        }
        handleProgramming();
    } else {
        // Normal operation
        handleNormalOperation();
    }
    
    // Handle auto-lock
    if (currentState == UNLOCKED && millis() - unlockTime > UNLOCK_DURATION) {
        setState(LOCKED);
    }
    
    delay(50);
}

void updateSensitivity() {
    int potValue = analogRead(SENSITIVITY_POT);
    knockThreshold = map(potValue, 0, 1023, 50, 300);
}

void setState(SystemState newState) {
    currentState = newState;
    
    // Turn off all LEDs
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(BLUE_LED, LOW);
    
    switch (newState) {
        case LOCKED:
            digitalWrite(RED_LED, HIGH);
            lockServo.write(LOCKED_POSITION);
            isLocked = true;
            Serial.println("System LOCKED");
            break;
            
        case LISTENING:
            digitalWrite(BLUE_LED, HIGH);
            Serial.println("LISTENING for knock pattern");
            break;
            
        case PROGRAMMING:
            // Cycle through all LEDs
            for (int i = 0; i < 3; i++) {
                digitalWrite(RED_LED, HIGH);
                delay(100);
                digitalWrite(RED_LED, LOW);
                digitalWrite(GREEN_LED, HIGH);
                delay(100);
                digitalWrite(GREEN_LED, LOW);
                digitalWrite(BLUE_LED, HIGH);
                delay(100);
                digitalWrite(BLUE_LED, LOW);
            }
            Serial.println("PROGRAMMING mode - knock your new pattern");
            break;
            
        case UNLOCKED:
            digitalWrite(GREEN_LED, HIGH);
            lockServo.write(UNLOCKED_POSITION);
            isLocked = false;
            unlockTime = millis();
            
            // Success sound
            tone(FEEDBACK_BUZZER, 1000, 200);
            delay(250);
            tone(FEEDBACK_BUZZER, 1500, 200);
            delay(250);
            tone(FEEDBACK_BUZZER, 2000, 200);
            
            Serial.println("ACCESS GRANTED - System UNLOCKED");
            break;
            
        case ACCESS_DENIED:
            // Flash red LED
            for (int i = 0; i < 5; i++) {
                digitalWrite(RED_LED, HIGH);
                delay(100);
                digitalWrite(RED_LED, LOW);
                delay(100);
            }
            
            // Denial sound
            tone(FEEDBACK_BUZZER, 200, 500);
            delay(600);
            tone(FEEDBACK_BUZZER, 150, 500);
            
            Serial.println("ACCESS DENIED - Wrong pattern");
            setState(LOCKED);
            break;
    }
}
```

### **Knock Detection and Pattern Analysis:**
```cpp
int detectKnock() {
    int knockValue = analogRead(KNOCK_SENSOR);
    
    if (knockValue > knockThreshold) {
        // Debounce - ignore knocks too close together
        if (millis() - lastKnockTime > 100) {
            lastKnockTime = millis();
            
            // Provide audio feedback
            tone(FEEDBACK_BUZZER, 800, 50);
            
            Serial.print("Knock detected: ");
            Serial.println(knockValue);
            
            return knockValue;
        }
    }
    
    return 0;
}

void handleNormalOperation() {
    int knockValue = detectKnock();
    
    if (knockValue > 0) {
        if (currentState == LOCKED) {
            setState(LISTENING);
            startListening();
        } else if (currentState == LISTENING) {
            recordKnock();
        }
    }
    
    // Check for timeout during listening
    if (currentState == LISTENING && 
        millis() - lastKnockTime > KNOCK_TIMEOUT) {
        evaluatePattern();
    }
}

void startListening() {
    attemptPattern.knockCount = 0;
    Serial.println("Started listening for knock pattern");
}

void recordKnock() {
    unsigned long currentTime = millis();
    
    if (attemptPattern.knockCount == 0) {
        // First knock - just record it
        attemptPattern.intervals[0] = 0;
        attemptPattern.knockCount = 1;
    } else if (attemptPattern.knockCount < MAX_KNOCKS) {
        // Record interval since last knock
        int interval = currentTime - lastKnockTime;
        attemptPattern.intervals[attemptPattern.knockCount] = interval;
        attemptPattern.knockCount++;
        
        Serial.print("Recorded interval: ");
        Serial.println(interval);
    }
    
    // Update last knock time
    lastKnockTime = currentTime;
}

void evaluatePattern() {
    Serial.println("Evaluating knock pattern...");
    
    // Check if pattern matches
    if (patternsMatch(attemptPattern, secretPattern)) {
        setState(UNLOCKED);
    } else {
        setState(ACCESS_DENIED);
    }
}

bool patternsMatch(KnockPattern attempt, KnockPattern secret) {
    // Check if knock count matches
    if (attempt.knockCount != secret.knockCount) {
        Serial.println("Pattern mismatch: different knock count");
        return false;
    }
    
    // Check intervals with tolerance
    for (int i = 1; i < attempt.knockCount; i++) {
        int difference = abs(attempt.intervals[i] - secret.intervals[i]);
        int tolerance = secret.tolerance;
        
        if (difference > tolerance) {
            Serial.print("Pattern mismatch at interval ");
            Serial.print(i);
            Serial.print(": ");
            Serial.print(difference);
            Serial.print(" > ");
            Serial.println(tolerance);
            return false;
        }
    }
    
    Serial.println("Pattern matches!");
    return true;
}
```

### **Programming Mode:**
```cpp
void handleProgramming() {
    static bool programmingStarted = false;
    static unsigned long programmingStartTime = 0;
    
    if (!programmingStarted) {
        programmingStarted = true;
        programmingStartTime = millis();
        secretPattern.knockCount = 0;
        Serial.println("Programming started - knock your new pattern");
    }
    
    int knockValue = detectKnock();
    
    if (knockValue > 0) {
        recordProgrammingKnock();
    }
    
    // Check for programming timeout
    if (millis() - lastKnockTime > KNOCK_TIMEOUT && secretPattern.knockCount > 0) {
        finishProgramming();
        programmingStarted = false;
    }
    
    // Check for programming button release
    if (digitalRead(PROGRAM_BUTTON) == HIGH) {
        if (secretPattern.knockCount > 0) {
            finishProgramming();
        }
        programmingStarted = false;
    }
}

void recordProgrammingKnock() {
    unsigned long currentTime = millis();
    
    if (secretPattern.knockCount == 0) {
        // First knock
        secretPattern.intervals[0] = 0;
        secretPattern.knockCount = 1;
        Serial.println("First knock recorded");
    } else if (secretPattern.knockCount < MAX_KNOCKS) {
        // Record interval
        int interval = currentTime - lastKnockTime;
        secretPattern.intervals[secretPattern.knockCount] = interval;
        secretPattern.knockCount++;
        
        Serial.print("Programming knock ");
        Serial.print(secretPattern.knockCount);
        Serial.print(" - interval: ");
        Serial.println(interval);
    }
    
    lastKnockTime = currentTime;
}

void finishProgramming() {
    if (secretPattern.knockCount > 1) {
        // Set tolerance based on pattern complexity
        secretPattern.tolerance = calculateTolerance();
        
        // Save to EEPROM
        saveSecretPattern();
        
        // Confirmation
        Serial.println("New pattern programmed successfully!");
        
        // Success sound
        for (int i = 0; i < 3; i++) {
            tone(FEEDBACK_BUZZER, 1500, 200);
            delay(300);
        }
        
        setState(LOCKED);
    } else {
        Serial.println("Programming cancelled - need at least 2 knocks");
        setState(LOCKED);
    }
}

int calculateTolerance() {
    // Calculate tolerance based on pattern intervals
    int totalInterval = 0;
    for (int i = 1; i < secretPattern.knockCount; i++) {
        totalInterval += secretPattern.intervals[i];
    }
    
    int averageInterval = totalInterval / (secretPattern.knockCount - 1);
    int tolerance = max(100, averageInterval / 4);  // 25% tolerance
    
    Serial.print("Calculated tolerance: ");
    Serial.println(tolerance);
    
    return tolerance;
}
```

### **EEPROM Storage:**
```cpp
void saveSecretPattern() {
    int address = 0;
    
    // Save knock count
    EEPROM.write(address++, secretPattern.knockCount);
    
    // Save tolerance
    EEPROM.write(address++, secretPattern.tolerance >> 8);
    EEPROM.write(address++, secretPattern.tolerance & 0xFF);
    
    // Save intervals
    for (int i = 0; i < secretPattern.knockCount; i++) {
        EEPROM.write(address++, secretPattern.intervals[i] >> 8);
        EEPROM.write(address++, secretPattern.intervals[i] & 0xFF);
    }
    
    Serial.println("Pattern saved to EEPROM");
}

void loadSecretPattern() {
    int address = 0;
    
    // Load knock count
    secretPattern.knockCount = EEPROM.read(address++);
    
    // Validate knock count
    if (secretPattern.knockCount > MAX_KNOCKS || secretPattern.knockCount < 1) {
        // Load default pattern
        loadDefaultPattern();
        return;
    }
    
    // Load tolerance
    secretPattern.tolerance = (EEPROM.read(address++) << 8) | EEPROM.read(address++);
    
    // Load intervals
    for (int i = 0; i < secretPattern.knockCount; i++) {
        secretPattern.intervals[i] = (EEPROM.read(address++) << 8) | EEPROM.read(address++);
    }
    
    Serial.println("Pattern loaded from EEPROM");
    Serial.print("Knock count: ");
    Serial.println(secretPattern.knockCount);
}

void loadDefaultPattern() {
    // Default pattern: KNOCK-pause-KNOCK-KNOCK-pause-KNOCK
    secretPattern.knockCount = 4;
    secretPattern.intervals[0] = 0;
    secretPattern.intervals[1] = 300;  // 300ms pause
    secretPattern.intervals[2] = 150;  // 150ms pause
    secretPattern.intervals[3] = 400;  // 400ms pause
    secretPattern.tolerance = 100;
    
    Serial.println("Default pattern loaded");
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check piezo connections** - Ensure proper polarity and 1MΩ resistor
2. **Verify servo wiring** - Signal, power, and ground connections
3. **Test LED polarities** - Long legs to resistors, short legs to ground
4. **Confirm button wiring** - Pull-up resistor and connections

### **System Test Program:**
```cpp
void systemTest() {
    Serial.println("=== KNOCK DETECTOR TEST ===");
    
    // Test LEDs
    Serial.println("Testing LEDs...");
    digitalWrite(RED_LED, HIGH);
    delay(500);
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);
    delay(500);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(BLUE_LED, HIGH);
    delay(500);
    digitalWrite(BLUE_LED, LOW);
    
    // Test servo
    Serial.println("Testing servo...");
    lockServo.write(LOCKED_POSITION);
    delay(1000);
    lockServo.write(UNLOCKED_POSITION);
    delay(1000);
    lockServo.write(LOCKED_POSITION);
    
    // Test buzzer
    Serial.println("Testing buzzer...");
    tone(FEEDBACK_BUZZER, 1000, 500);
    delay(1000);
    
    // Test knock sensor
    Serial.println("Testing knock sensor (tap the piezo)...");
    for (int i = 0; i < 50; i++) {
        int knockValue = analogRead(KNOCK_SENSOR);
        if (knockValue > 50) {
            Serial.print("Knock detected: ");
            Serial.println(knockValue);
        }
        delay(100);
    }
    
    // Test sensitivity pot
    Serial.println("Testing sensitivity...");
    for (int i = 0; i < 10; i++) {
        int sensitivity = analogRead(SENSITIVITY_POT);
        Serial.print("Sensitivity: ");
        Serial.println(sensitivity);
        delay(500);
    }
    
    Serial.println("System test complete!");
}
```

### **Troubleshooting:**
- **No knock detection**: Check piezo connections and resistor value
- **Servo not moving**: Verify power supply and signal connection
- **LEDs not working**: Check resistor values and polarity
- **Button not responding**: Confirm pull-up resistor and connections
- **Sensitivity issues**: Adjust potentiometer and check A1 connection

---

## 🎪 **Advanced Security Features**

### **Multiple User Patterns:**
```cpp
// Multiple user support
#define MAX_USERS 5

struct UserPattern {
    KnockPattern pattern;
    String userName;
    bool isActive;
    unsigned long lastUsed;
};

UserPattern users[MAX_USERS];
int currentUser = 0;

void addUser(String name, KnockPattern pattern) {
    for (int i = 0; i < MAX_USERS; i++) {
        if (!users[i].isActive) {
            users[i].pattern = pattern;
            users[i].userName = name;
            users[i].isActive = true;
            users[i].lastUsed = millis();
            
            Serial.print("Added user: ");
            Serial.println(name);
            break;
        }
    }
}

bool authenticateUser(KnockPattern attempt) {
    for (int i = 0; i < MAX_USERS; i++) {
        if (users[i].isActive && patternsMatch(attempt, users[i].pattern)) {
            Serial.print("User authenticated: ");
            Serial.println(users[i].userName);
            users[i].lastUsed = millis();
            return true;
        }
    }
    return false;
}
```

### **Security Logging:**
```cpp
// Access log system
struct AccessLog {
    unsigned long timestamp;
    bool successful;
    int attemptCount;
    String userPattern;
};

AccessLog accessHistory[20];
int logIndex = 0;

void logAccess(bool success, KnockPattern pattern) {
    accessHistory[logIndex].timestamp = millis();
    accessHistory[logIndex].successful = success;
    accessHistory[logIndex].attemptCount = pattern.knockCount;
    
    // Convert pattern to string
    String patternStr = "";
    for (int i = 0; i < pattern.knockCount; i++) {
        patternStr += String(pattern.intervals[i]);
        if (i < pattern.knockCount - 1) patternStr += ",";
    }
    accessHistory[logIndex].userPattern = patternStr;
    
    logIndex = (logIndex + 1) % 20;
}

void printAccessLog() {
    Serial.println("=== ACCESS LOG ===");
    for (int i = 0; i < 20; i++) {
        if (accessHistory[i].timestamp > 0) {
            Serial.print("Time: ");
            Serial.print(accessHistory[i].timestamp);
            Serial.print(", Success: ");
            Serial.print(accessHistory[i].successful ? "YES" : "NO");
            Serial.print(", Pattern: ");
            Serial.println(accessHistory[i].userPattern);
        }
    }
}
```

### **Tamper Detection:**
```cpp
// Anti-tamper features
int failedAttempts = 0;
unsigned long lockoutTime = 0;
bool isLockedOut = false;

void handleFailedAttempt() {
    failedAttempts++;
    
    if (failedAttempts >= 3) {
        // Lockout for 5 minutes
        isLockedOut = true;
        lockoutTime = millis();
        
        Serial.println("SECURITY ALERT: Too many failed attempts");
        Serial.println("System locked for 5 minutes");
        
        // Alert sound
        for (int i = 0; i < 10; i++) {
            tone(FEEDBACK_BUZZER, 3000, 200);
            delay(300);
        }
    }
}

void checkLockout() {
    if (isLockedOut && millis() - lockoutTime > 300000) {  // 5 minutes
        isLockedOut = false;
        failedAttempts = 0;
        Serial.println("Lockout period ended");
    }
}
```

---

## 🎉 **Success! You've Built a Secret Knock Detector!**

**Congratulations, Security Code Breaker!** Your intelligent security system is now operational! You've learned pattern recognition, signal processing, access control, and security systems - essential skills for cybersecurity, authentication systems, and smart home security!

### **Next Steps:**
- Add wireless connectivity for remote alerts
- Integrate with smartphone app for management
- Add camera module for visual verification
- Create master override codes for emergencies

### **Real-World Applications:**
- **Home security**: Smart door locks and access control
- **Commercial**: Office building security systems
- **Automotive**: Vehicle security and access
- **Personal**: Phone unlock patterns and biometrics
- **Industrial**: Secure equipment access control

---

*Security through obscurity and intelligence - keep protecting! 🚀*