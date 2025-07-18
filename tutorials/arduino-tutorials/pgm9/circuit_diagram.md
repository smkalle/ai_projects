# 📡 Program 9: Ultrasonic Distance Sensor Circuit Diagram

## 🎯 **DISTANCE DETECTIVE MISSION**
Use sound waves to detect objects and measure distances like a bat or dolphin!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **HC-SR04 Ultrasonic Sensor** (1x)
- **LEDs** (3x - Green, Yellow, Red)
- **Piezo Buzzer** (1x)
- **220Ω Resistors** (3x - for LEDs)
- **Breadboard** (1x)
- **Jumper Wires** (8x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         D7  │────────────────┤ HC-SR04 Trigger │
    │         D6  │────────────────┤ HC-SR04 Echo    │
    │             │                │                 │
    │        D13  │────────────────┤ Green LED       │
    │        D12  │────────────────┤ Yellow LED      │
    │        D11  │────────────────┤ Red LED         │
    │             │                │                 │
    │        D10  │────────────────┤ Piezo Buzzer    │
    │             │                │                 │
    │         5V  │────────────────┤ Sensor Power    │
    │         GND │────────────────┤ Common Ground   │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: HC-SR04 Ultrasonic Sensor Pinout**
**HC-SR04** has 4 pins for power and communication:

```
HC-SR04 Pinout (front view):
┌─────────────────────────────────┐
│    [  ]         [  ]            │
│   Sensor      Sensor            │
│  (Trigger)    (Echo)            │
│                                 │
│ VCC  Trig  Echo  GND            │
│  │    │     │    │              │
│  1    2     3    4              │
└─────────────────────────────────┘

Pin 1 (VCC)  - Power (5V)
Pin 2 (Trig) - Trigger signal (Arduino D7)
Pin 3 (Echo) - Echo signal (Arduino D6)
Pin 4 (GND)  - Ground
```

### **Step 2: Breadboard Layout**
```
Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← HC-SR04 VCC
│  2  2  .  .  .  .  .  .  .  .  │ ← HC-SR04 Trigger
│  3  3  .  .  .  .  .  .  .  .  │ ← HC-SR04 Echo
│  4  4  .  .  .  .  .  .  .  .  │ ← HC-SR04 GND
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  .  .  .  .  .  .  .  .  │ ← Green LED (Close)
│  7  7  .  .  .  .  .  .  .  .  │ ← Green LED cathode
│  8  8  .  .  .  .  .  .  .  .  │ ← Yellow LED (Medium)
│  9  9  .  .  .  .  .  .  .  .  │ ← Yellow LED cathode
│ 10 10  .  .  .  .  .  .  .  .  │ ← Red LED (Far)
│ 11 11  .  .  .  .  .  .  .  .  │ ← Red LED cathode
│ 12 12  .  .  .  .  .  .  .  .  │ ← Buzzer positive
│ 13 13  .  .  .  .  .  .  .  .  │ ← Buzzer negative
└─────────────────────────────────┘
```

### **Step 3: Install HC-SR04 Sensor**
Mount sensor across breadboard gap or use separate area:

```
HC-SR04 Installation:
┌─────────────────────────────────┐
│  1  1  V  .  .  .  .  .  .  .  │ ← VCC (5V)
│  2  2  T  .  .  .  .  .  .  .  │ ← Trigger pin
│  3  3  E  .  .  .  .  .  .  .  │ ← Echo pin
│  4  4  G  .  .  .  .  .  .  .  │ ← Ground
└─────────────────────────────────┘
```

### **Step 4: Install Distance Indicator LEDs**
Three LEDs show distance ranges:

```
LED Installation:
┌─────────────────────────────────┐
│  1  1  V  .  .  .  .  .  .  .  │ ← HC-SR04 VCC
│  2  2  T  .  .  .  .  .  .  .  │ ← HC-SR04 Trigger
│  3  3  E  .  .  .  .  .  .  .  │ ← HC-SR04 Echo
│  4  4  G  .  .  .  .  .  .  .  │ ← HC-SR04 GND
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  G+ .  .  .  .  .  .  .  │ ← Green LED anode
│  7  7  G- .  .  .  .  .  .  .  │ ← Green LED cathode
│  8  8  Y+ .  .  .  .  .  .  .  │ ← Yellow LED anode
│  9  9  Y- .  .  .  .  .  .  .  │ ← Yellow LED cathode
│ 10 10  R+ .  .  .  .  .  .  .  │ ← Red LED anode
│ 11 11  R- .  .  .  .  .  .  .  │ ← Red LED cathode
│ 12 12  B+ .  .  .  .  .  .  .  │ ← Buzzer positive
│ 13 13  B- .  .  .  .  .  .  .  │ ← Buzzer negative
└─────────────────────────────────┘
```

### **Step 5: Install Current-Limiting Resistors**
Each LED needs a 220Ω resistor:

```
Resistor Installation:
┌─────────────────────────────────┐
│  1  1  V  .  .  .  .  .  .  .  │ ← HC-SR04 VCC
│  2  2  T  .  .  .  .  .  .  .  │ ← HC-SR04 Trigger
│  3  3  E  .  .  .  .  .  .  .  │ ← HC-SR04 Echo
│  4  4  G  .  .  .  .  .  .  .  │ ← HC-SR04 GND
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  G+ Rg .  .  .  .  .  .  │ ← Green LED + resistor
│  7  7  G- │  .  .  .  .  .  .  │ ← Green LED cathode
│  8  8  Y+ Ry .  .  .  .  .  .  │ ← Yellow LED + resistor
│  9  9  Y- │  .  .  .  .  .  .  │ ← Yellow LED cathode
│ 10 10  R+ Rr .  .  .  .  .  .  │ ← Red LED + resistor
│ 11 11  R- │  .  .  .  .  .  .  │ ← Red LED cathode
│ 12 12  B+ .  .  .  .  .  .  .  │ ← Buzzer positive
│ 13 13  B- .  .  .  .  .  .  .  │ ← Buzzer negative
│ 14 14  .  Rg .  .  .  .  .  .  │ ← Green resistor to D13
│ 15 15  .  Ry .  .  .  .  .  .  │ ← Yellow resistor to D12
│ 16 16  .  Rr .  .  .  .  .  .  │ ← Red resistor to D11
└─────────────────────────────────┘
```

### **Step 6: Connect All Wires**
```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  V──●  .  .  .  .  .  .  │ ← VCC to 5V
│  2  2  T──●  .  .  .  .  .  .  │ ← Trigger to D7
│  3  3  E──●  .  .  .  .  .  .  │ ← Echo to D6
│  4  4  G──●  .  .  .  .  .  .  │ ← Ground to GND
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  G+ Rg .  .  .  .  .  .  │ ← Green LED + resistor
│  7  7  G- ●  .  .  .  .  .  .  │ ← Green LED cathode to GND
│  8  8  Y+ Ry .  .  .  .  .  .  │ ← Yellow LED + resistor
│  9  9  Y- ●  .  .  .  .  .  .  │ ← Yellow LED cathode to GND
│ 10 10  R+ Rr .  .  .  .  .  .  │ ← Red LED + resistor
│ 11 11  R- ●  .  .  .  .  .  .  │ ← Red LED cathode to GND
│ 12 12  B+ ●  .  .  .  .  .  .  │ ← Buzzer positive to D10
│ 13 13  B- ●  .  .  .  .  .  .  │ ← Buzzer negative to GND
│ 14 14  .  Rg─●  .  .  .  .  .  │ ← Green resistor to D13
│ 15 15  .  Ry─●  .  .  .  .  .  │ ← Yellow resistor to D12
│ 16 16  .  Rr─●  .  .  .  .  .  │ ← Red resistor to D11
└─────────────────────────────────┘

● = Jumper wire connections
Rg = Green LED resistor (220Ω)
Ry = Yellow LED resistor (220Ω)
Rr = Red LED resistor (220Ω)
```

### **Step 7: Wire Connections Summary**
**Sensor Connections:**
- **Red wire**: Arduino 5V → Row 1, column 'c' (HC-SR04 VCC)
- **Orange wire**: Arduino D7 → Row 2, column 'c' (HC-SR04 Trigger)
- **Yellow wire**: Arduino D6 → Row 3, column 'c' (HC-SR04 Echo)
- **Black wire**: Arduino GND → Row 4, column 'c' (HC-SR04 GND)

**LED Connections:**
- **Green wire**: Arduino D13 → Row 14, column 'c' (Green LED through resistor)
- **Blue wire**: Arduino D12 → Row 15, column 'c' (Yellow LED through resistor)
- **Purple wire**: Arduino D11 → Row 16, column 'c' (Red LED through resistor)

**Buzzer Connection:**
- **White wire**: Arduino D10 → Row 12, column 'c' (Buzzer positive)

**Ground Connections:**
- **Black wires**: Arduino GND → Rows 7, 9, 11, 13, columns 'c' (All cathodes and buzzer negative)

---

## ⚡ **Circuit Explanation**

### **How Ultrasonic Sensors Work:**
1. **Trigger pulse** sends 8 ultrasonic sound bursts (40kHz)
2. **Sound waves** travel to object and reflect back
3. **Echo pin** receives the reflected sound
4. **Time measurement** calculates distance using speed of sound

### **Distance Calculation:**
```
Speed of Sound = 343 m/s (at 20°C)
Distance = (Time × Speed) / 2

Time in microseconds:
Distance (cm) = (pulseIn time × 0.034) / 2
Distance (inches) = (pulseIn time × 0.0133) / 2

Example:
pulseIn() = 2940 microseconds
Distance = (2940 × 0.034) / 2 = 50 cm
```

### **HC-SR04 Timing:**
```
Trigger Signal:
- Send 10μs HIGH pulse to trigger pin
- Wait for echo response

Echo Signal:
- HIGH pulse duration = travel time
- Maximum range: ~400cm
- Minimum range: ~2cm
- Update rate: 40Hz maximum
```

### **Signal Flow:**
```
Arduino → Trigger → HC-SR04 → Sound Wave → Object
   ↑                                         ↓
   ← Echo ← HC-SR04 ← Reflected Sound ←──────┘
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
   │  D6 ●────────┼─── YELLOW WIRE ─────────┐
   │  D7 ●────────┼─── ORANGE WIRE ─────────┼─┐
   │ D10 ●────────┼─── WHITE WIRE ──────────┼─┼─┐
   │ D11 ●────────┼─── PURPLE WIRE ─────────┼─┼─┼─┐
   │ D12 ●────────┼─── BLUE WIRE ───────────┼─┼─┼─┼─┐
   │ D13 ●────────┼─── GREEN WIRE ──────────┼─┼─┼─┼─┼─┐
   │             │                         │ │ │ │ │ │
   │  5V ●────────┼─── RED WIRE ───────────┼─┼─┼─┼─┼─┼─┐
   │ GND ●────────┼─── BLACK WIRE ─────────┼─┼─┼─┼─┼─┼─┼─┐
   │             │                         │ │ │ │ │ │ │ │
   └─────────────┘                         │ │ │ │ │ │ │ │
                                           │ │ │ │ │ │ │ │
   HC-SR04 ULTRASONIC SENSOR               │ │ │ │ │ │ │ │
   ┌─────────────────────────────────┐     │ │ │ │ │ │ │ │
   │    [  ]         [  ]            │     │ │ │ │ │ │ │ │
   │   Trigger      Echo             │     │ │ │ │ │ │ │ │
   │                                 │     │ │ │ │ │ │ │ │
   │ VCC  Trig  Echo  GND            │     │ │ │ │ │ │ │ │
   │  │    │     │    │              │     │ │ │ │ │ │ │ │
   │  └────┼─────┼────┼──────────────┼─────┘ │ │ │ │ │ │ │
   │       │     │    │              │       │ │ │ │ │ │ │
   │       └─────┼────┼──────────────┼───────┘ │ │ │ │ │ │
   │             │    │              │         │ │ │ │ │ │
   │             └────┼──────────────┼─────────┘ │ │ │ │ │
   │                  │              │           │ │ │ │ │
   │                  └──────────────┼───────────┘ │ │ │ │
   │                                 │             │ │ │ │
   └─────────────────────────────────┘             │ │ │ │
                                                   │ │ │ │
   DISTANCE INDICATOR LEDS                         │ │ │ │
   ┌─────────────┐                                 │ │ │ │
   │             │                                 │ │ │ │
   │ ●─[220Ω]────┼─────────────────────────────────┘ │ │ │
   │             │                                   │ │ │
   │ ●─[GREEN]───┼───────────────────────────────────┘ │ │
   │             │                                     │ │
   │ ●─[220Ω]────┼─────────────────────────────────────┘ │
   │             │                                       │
   │ ●─[YELLOW]──┼───────────────────────────────────────┘
   │             │
   │ ●─[220Ω]────┼─────────────────────────────────────┐
   │             │                                     │
   │ ●─[RED]─────┼─────────────────────────────────────┼─┐
   │             │                                     │ │
   │ ●───────────┼─────────────────────────────────────┼─┼─┐
   │             │                                     │ │ │
   └─────────────┘                                     │ │ │
                                                       │ │ │
   PIEZO BUZZER                                        │ │ │
   ┌─────────────┐                                     │ │ │
   │    ┌───┐    │                                     │ │ │
   │    │ + │    │                                     │ │ │
   │    │ - │    │                                     │ │ │
   │    └───┘    │                                     │ │ │
   │     │ │     │                                     │ │ │
   │     │ └─────┼─────────────────────────────────────┘ │ │
   │     │       │                                       │ │
   │     └───────┼───────────────────────────────────────┘ │
   │             │                                         │
   └─────────────┘                                         │
                                                           │
   GROUND BUS                                              │
   ┌─────────────┐                                         │
   │ GND ●───────┼─────────────────────────────────────────┘
   │             │
   └─────────────┘
```

---

## 🔊 **Ultrasonic Programming Guide**

### **Basic Distance Measurement:**
```cpp
// Pin definitions
#define TRIG_PIN 7
#define ECHO_PIN 6
#define GREEN_LED 13
#define YELLOW_LED 12
#define RED_LED 11
#define BUZZER 10

void setup() {
    Serial.begin(9600);
    
    // Initialize pins
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(GREEN_LED, OUTPUT);
    pinMode(YELLOW_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(BUZZER, OUTPUT);
    
    Serial.println("Ultrasonic Distance Sensor Ready");
}

void loop() {
    float distance = measureDistance();
    
    // Display distance
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    
    // Update indicators
    updateIndicators(distance);
    
    delay(100);
}

float measureDistance() {
    // Clear trigger pin
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    
    // Send 10us pulse
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    
    // Read echo time
    long duration = pulseIn(ECHO_PIN, HIGH);
    
    // Calculate distance
    float distance = (duration * 0.034) / 2;
    
    return distance;
}

void updateIndicators(float distance) {
    // Turn off all LEDs
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(YELLOW_LED, LOW);
    digitalWrite(RED_LED, LOW);
    noTone(BUZZER);
    
    if (distance <= 10) {
        // Very close - Green LED and fast beep
        digitalWrite(GREEN_LED, HIGH);
        tone(BUZZER, 2000, 100);
    } else if (distance <= 20) {
        // Medium distance - Yellow LED and medium beep
        digitalWrite(YELLOW_LED, HIGH);
        tone(BUZZER, 1000, 200);
    } else if (distance <= 30) {
        // Far distance - Red LED and slow beep
        digitalWrite(RED_LED, HIGH);
        tone(BUZZER, 500, 300);
    }
    // No indication for distances > 30cm
}
```

### **Advanced Distance Features:**
```cpp
// Smoothing filter for stable readings
float smoothDistance(float newReading) {
    static float readings[5] = {0, 0, 0, 0, 0};
    static int index = 0;
    
    readings[index] = newReading;
    index = (index + 1) % 5;
    
    float sum = 0;
    for (int i = 0; i < 5; i++) {
        sum += readings[i];
    }
    
    return sum / 5.0;
}

// Motion detection
bool detectMotion() {
    static float lastDistance = 0;
    float currentDistance = measureDistance();
    
    bool motion = abs(currentDistance - lastDistance) > 5;
    lastDistance = currentDistance;
    
    return motion;
}

// Proximity alarm
void proximityAlarm(float distance) {
    if (distance < 5) {
        // Emergency close - rapid beeping
        for (int i = 0; i < 5; i++) {
            tone(BUZZER, 3000, 50);
            delay(50);
            noTone(BUZZER);
            delay(50);
        }
    } else if (distance < 15) {
        // Warning close - slower beeping
        int beepDelay = map(distance, 5, 15, 100, 500);
        tone(BUZZER, 2000, beepDelay);
        delay(beepDelay * 2);
    }
}
```

### **Object Tracking:**
```cpp
// Track object position
void trackObject() {
    float distance = measureDistance();
    
    if (distance > 2 && distance < 400) {
        Serial.print("Object detected at: ");
        Serial.print(distance);
        Serial.println(" cm");
        
        // Visual feedback based on distance
        if (distance < 10) {
            Serial.println("Status: VERY CLOSE");
            digitalWrite(GREEN_LED, HIGH);
            digitalWrite(YELLOW_LED, LOW);
            digitalWrite(RED_LED, LOW);
        } else if (distance < 30) {
            Serial.println("Status: CLOSE");
            digitalWrite(GREEN_LED, LOW);
            digitalWrite(YELLOW_LED, HIGH);
            digitalWrite(RED_LED, LOW);
        } else {
            Serial.println("Status: FAR");
            digitalWrite(GREEN_LED, LOW);
            digitalWrite(YELLOW_LED, LOW);
            digitalWrite(RED_LED, HIGH);
        }
    } else {
        Serial.println("No object detected");
        digitalWrite(GREEN_LED, LOW);
        digitalWrite(YELLOW_LED, LOW);
        digitalWrite(RED_LED, LOW);
    }
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check HC-SR04 connections** - VCC to 5V, GND to GND, Trig to D7, Echo to D6
2. **Verify LED polarities** - Long legs to resistors, short legs to ground
3. **Test buzzer polarity** - Positive to D10, negative to ground
4. **Confirm resistor values** - 220Ω for each LED

### **Sensor Test Program:**
```cpp
void setup() {
    Serial.begin(9600);
    pinMode(7, OUTPUT);  // Trigger
    pinMode(6, INPUT);   // Echo
    Serial.println("HC-SR04 Test Starting...");
}

void loop() {
    // Test trigger signal
    digitalWrite(7, LOW);
    delayMicroseconds(2);
    digitalWrite(7, HIGH);
    delayMicroseconds(10);
    digitalWrite(7, LOW);
    
    // Read echo
    long duration = pulseIn(6, HIGH);
    float distance = (duration * 0.034) / 2;
    
    Serial.print("Duration: ");
    Serial.print(duration);
    Serial.print("μs, Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    
    delay(500);
}
```

### **Troubleshooting:**
- **No readings**: Check VCC and GND connections
- **Erratic readings**: Verify trigger and echo pin connections
- **LEDs don't work**: Check resistor values and LED polarities
- **No sound**: Verify buzzer connections and polarity

### **Calibration Test:**
```cpp
void calibrationTest() {
    Serial.println("=== ULTRASONIC CALIBRATION ===");
    
    // Test at known distances
    Serial.println("Place object at 10cm and press any key");
    while (!Serial.available()) {}
    Serial.read();
    
    float reading10cm = measureDistance();
    Serial.print("10cm reading: ");
    Serial.println(reading10cm);
    
    Serial.println("Place object at 20cm and press any key");
    while (!Serial.available()) {}
    Serial.read();
    
    float reading20cm = measureDistance();
    Serial.print("20cm reading: ");
    Serial.println(reading20cm);
    
    Serial.println("Calibration complete!");
}
```

---

## 🎪 **Creative Distance Projects**

### **Parking Sensor:**
```cpp
// Parking assistant
void parkingAssistant() {
    float distance = measureDistance();
    
    if (distance > 100) {
        Serial.println("Safe to approach");
        noTone(BUZZER);
    } else if (distance > 50) {
        Serial.println("Getting closer...");
        tone(BUZZER, 500, 500);
        delay(1000);
    } else if (distance > 20) {
        Serial.println("Slow down!");
        tone(BUZZER, 1000, 200);
        delay(500);
    } else if (distance > 10) {
        Serial.println("STOP SOON!");
        tone(BUZZER, 2000, 100);
        delay(200);
    } else {
        Serial.println("STOP NOW!");
        tone(BUZZER, 3000, 50);
        delay(100);
    }
}
```

### **Security System:**
```cpp
// Motion-activated security
void securitySystem() {
    static bool armed = true;
    static float lastDistance = 0;
    
    float currentDistance = measureDistance();
    
    if (armed && currentDistance < 50) {
        if (abs(currentDistance - lastDistance) > 10) {
            Serial.println("INTRUDER ALERT!");
            
            // Alarm sequence
            for (int i = 0; i < 10; i++) {
                digitalWrite(RED_LED, HIGH);
                tone(BUZZER, 2000, 100);
                delay(100);
                digitalWrite(RED_LED, LOW);
                noTone(BUZZER);
                delay(100);
            }
        }
    }
    
    lastDistance = currentDistance;
}
```

### **Level Indicator:**
```cpp
// Liquid level monitoring
void levelIndicator() {
    float distance = measureDistance();
    
    // Assume tank is 50cm deep
    float level = 50 - distance;
    float percentage = (level / 50.0) * 100;
    
    if (percentage < 0) percentage = 0;
    if (percentage > 100) percentage = 100;
    
    Serial.print("Level: ");
    Serial.print(percentage);
    Serial.println("%");
    
    // Visual indicators
    if (percentage > 75) {
        digitalWrite(GREEN_LED, HIGH);
        digitalWrite(YELLOW_LED, LOW);
        digitalWrite(RED_LED, LOW);
    } else if (percentage > 25) {
        digitalWrite(GREEN_LED, LOW);
        digitalWrite(YELLOW_LED, HIGH);
        digitalWrite(RED_LED, LOW);
    } else {
        digitalWrite(GREEN_LED, LOW);
        digitalWrite(YELLOW_LED, LOW);
        digitalWrite(RED_LED, HIGH);
        
        // Low level alarm
        if (percentage < 10) {
            tone(BUZZER, 1500, 1000);
        }
    }
}
```

---

## 🎉 **Success! You've Built a Distance Detection System!**

**Congratulations, Distance Detective!** Your ultrasonic sensor system is now operational! You've learned sound wave physics, pulse timing, and proximity detection - essential skills for robotics, automation, and sensing systems!

### **Next Steps:**
- Add servo motor for scanning radar
- Create obstacle avoidance robot
- Build automatic door opener
- Add data logging for traffic counting

### **Advanced Features:**
```cpp
// Multi-sensor array
class UltrasonicArray {
private:
    int trigPins[3] = {7, 9, 11};
    int echoPins[3] = {6, 8, 10};
    
public:
    float measureDistance(int sensor) {
        digitalWrite(trigPins[sensor], LOW);
        delayMicroseconds(2);
        digitalWrite(trigPins[sensor], HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPins[sensor], LOW);
        
        long duration = pulseIn(echoPins[sensor], HIGH);
        return (duration * 0.034) / 2;
    }
    
    void scanArea() {
        for (int i = 0; i < 3; i++) {
            float dist = measureDistance(i);
            Serial.print("Sensor ");
            Serial.print(i);
            Serial.print(": ");
            Serial.print(dist);
            Serial.println(" cm");
        }
    }
};

// Temperature compensation
float temperatureCompensation(float rawDistance, float temperature) {
    // Speed of sound changes with temperature
    float speedOfSound = 331.3 + (0.6 * temperature);
    float correctedDistance = rawDistance * (speedOfSound / 343.0);
    return correctedDistance;
}
```

### **Real-World Applications:**
- **Automotive**: Parking sensors and collision avoidance
- **Industrial**: Level monitoring and automation
- **Security**: Motion detection and perimeter monitoring
- **Robotics**: Navigation and obstacle avoidance
- **Medical**: Non-contact measurement systems

---

*Sound waves are your invisible measuring tape! Keep exploring! 🚀*