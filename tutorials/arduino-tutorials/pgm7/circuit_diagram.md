# 🤖 Program 7: Servo Motor Control Circuit Diagram

## 🎯 **ROBOTICS ENGINEER MISSION**
Build precision movement systems and control mechanical devices with servo motors!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **SG90 Micro Servo Motor** (1x)
- **Potentiometer (10kΩ)** (1x) - for manual control
- **LED** (1x) - for position feedback
- **220Ω Resistor** (1x) - for LED
- **Breadboard** (1x)
- **Jumper Wires** (7x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         D9  │────────────────┤ Servo Signal    │
    │             │                │                 │
    │         A0  │────────────────┤ Potentiometer   │
    │             │                │                 │
    │        D13  │────────────────┤ Position LED    │
    │             │                │                 │
    │         5V  │────────────────┤ Servo Power     │
    │             │                │                 │
    │         GND │────────────────┤ Common Ground   │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: Servo Motor Pinout**
**SG90 Micro Servo** has 3 wires with standard colors:

```
Servo Motor Pinout:
┌─────────────────────┐
│  Brown  Red  Orange │
│    │     │     │    │
│   GND   VCC  Signal │
└─────────────────────┘

Brown/Black  = Ground (GND)
Red          = Power (5V)
Orange/White = Signal (PWM)
```

### **Step 2: Breadboard Layout**
```
Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← Servo signal wire
│  2  2  .  .  .  .  .  .  .  .  │ ← Servo power wire
│  3  3  .  .  .  .  .  .  .  .  │ ← Servo ground wire
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  .  .  .  .  .  .  .  .  │ ← Potentiometer middle pin
│  6  6  .  .  .  .  .  .  .  .  │ ← Potentiometer side pin
│  7  7  .  .  .  .  .  .  .  .  │ ← Potentiometer side pin
│  8  8  .  .  .  .  .  .  .  .  │
│  9  9  .  .  .  .  .  .  .  .  │ ← LED anode
│ 10 10  .  .  .  .  .  .  .  .  │ ← LED cathode
│ 11 11  .  .  .  .  .  .  .  .  │ ← LED resistor
└─────────────────────────────────┘
```

### **Step 3: Install Servo Motor Connections**
Connect servo wires to breadboard:

```
Servo Wire Installation:
┌─────────────────────────────────┐
│  1  1  S  .  .  .  .  .  .  .  │ ← Signal (Orange/White)
│  2  2  V  .  .  .  .  .  .  .  │ ← VCC (Red)
│  3  3  G  .  .  .  .  .  .  .  │ ← GND (Brown/Black)
└─────────────────────────────────┘
```

### **Step 4: Install Potentiometer**
Potentiometer for manual servo control:

```
Potentiometer Installation:
┌─────────────────────────────────┐
│  1  1  S  .  .  .  .  .  .  .  │ ← Servo signal
│  2  2  V  .  .  .  .  .  .  .  │ ← Servo power
│  3  3  G  .  .  .  .  .  .  .  │ ← Servo ground
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  A  .  .  .  .  .  .  .  │ ← Potentiometer wiper (middle)
│  6  6  P  .  .  .  .  .  .  .  │ ← Potentiometer side 1
│  7  7  P  .  .  .  .  .  .  .  │ ← Potentiometer side 2
└─────────────────────────────────┘
```

### **Step 5: Install Position LED**
LED shows servo position status:

```
LED Installation:
┌─────────────────────────────────┐
│  1  1  S  .  .  .  .  .  .  .  │ ← Servo signal
│  2  2  V  .  .  .  .  .  .  .  │ ← Servo power
│  3  3  G  .  .  .  .  .  .  .  │ ← Servo ground
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  A  .  .  .  .  .  .  .  │ ← Potentiometer wiper
│  6  6  P  .  .  .  .  .  .  .  │ ← Potentiometer side 1
│  7  7  P  .  .  .  .  .  .  .  │ ← Potentiometer side 2
│  8  8  .  .  .  .  .  .  .  .  │
│  9  9  +  .  .  .  .  .  .  .  │ ← LED anode (long leg)
│ 10 10  -  .  .  .  .  .  .  .  │ ← LED cathode (short leg)
│ 11 11  .  R  .  .  .  .  .  .  │ ← LED resistor
└─────────────────────────────────┘
```

### **Step 6: Connect All Wires**
```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  S──●  .  .  .  .  .  .  │ ← Servo signal to D9
│  2  2  V──●  .  .  .  .  .  .  │ ← Servo power to 5V
│  3  3  G──●  .  .  .  .  .  .  │ ← Servo ground to GND
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  A──●  .  .  .  .  .  .  │ ← Potentiometer to A0
│  6  6  P──●  .  .  .  .  .  .  │ ← Potentiometer to 5V
│  7  7  P──●  .  .  .  .  .  .  │ ← Potentiometer to GND
│  8  8  .  .  .  .  .  .  .  .  │
│  9  9  +──R──●  .  .  .  .  .  │ ← LED anode + resistor to D13
│ 10 10  -──●  .  .  .  .  .  .  │ ← LED cathode to GND
│ 11 11  .  R  .  .  .  .  .  .  │ ← Resistor connection
└─────────────────────────────────┘

● = Jumper wire connections
R = 220Ω Resistor
```

### **Step 7: Wire Connections Summary**
- **Orange wire**: Arduino D9 → Row 1, column 'c' (Servo signal)
- **Red wire**: Arduino 5V → Row 2, column 'c' (Servo power)
- **Brown wire**: Arduino GND → Row 3, column 'c' (Servo ground)
- **Yellow wire**: Arduino A0 → Row 5, column 'c' (Potentiometer wiper)
- **Red wire**: Arduino 5V → Row 6, column 'c' (Potentiometer power)
- **Black wire**: Arduino GND → Row 7, column 'c' and Row 10, column 'c' (Grounds)
- **Green wire**: Arduino D13 → Row 11, column 'c' (LED through resistor)

---

## ⚡ **Circuit Explanation**

### **How Servo Motors Work:**
1. **PWM signal** controls servo position (1-2ms pulse width)
2. **Feedback mechanism** maintains precise position
3. **Gears and motor** provide high torque, low speed
4. **Control circuit** interprets PWM and drives motor

### **PWM Control Signal:**
```
Servo Position Control:
┌─────────────────────────────────┐
│ Pulse Width  │ Servo Position   │
│─────────────────────────────────│
│    1.0ms     │ 0° (Full Left)   │
│    1.5ms     │ 90° (Center)     │
│    2.0ms     │ 180° (Full Right)│
└─────────────────────────────────┘

Signal Period: 20ms (50Hz)
```

### **Arduino Servo Library:**
```cpp
#include <Servo.h>

Servo myServo;

void setup() {
    myServo.attach(9);        // Attach servo to pin 9
    myServo.write(90);        // Move to 90 degrees
}

void loop() {
    myServo.write(0);         // Move to 0 degrees
    delay(1000);
    myServo.write(180);       // Move to 180 degrees
    delay(1000);
}
```

### **Power Requirements:**
- **Voltage**: 4.8V - 6V (5V typical)
- **Current**: 100-300mA depending on load
- **Torque**: 1.8kg/cm (SG90 specification)
- **Speed**: 0.1s/60° (at no load)

---

## 🎨 **Visual Connection Guide**

```
   ARDUINO UNO
   ┌─────────────┐
   │  ┌─────────┐│
   │  │  RESET  ││
   │  └─────────┘│
   │             │
   │  D9 ●────────┼─── ORANGE WIRE ──────┐
   │             │                      │
   │ D13 ●────────┼─── GREEN WIRE ───────┼─┐
   │             │                      │ │
   │  A0 ●────────┼─── YELLOW WIRE ──────┼─┼─┐
   │             │                      │ │ │
   │  5V ●────────┼─── RED WIRE ─────────┼─┼─┼─┐
   │             │                      │ │ │ │
   │ GND ●────────┼─── BLACK WIRE ───────┼─┼─┼─┼─┐
   │             │                      │ │ │ │ │
   └─────────────┘                      │ │ │ │ │
                                        │ │ │ │ │
   SERVO MOTOR                          │ │ │ │ │
   ┌─────────────┐                      │ │ │ │ │
   │    SG90     │                      │ │ │ │ │
   │  ┌─────────┐│                      │ │ │ │ │
   │  │ SHAFT   ││                      │ │ │ │ │
   │  └─────────┘│                      │ │ │ │ │
   │  O  R  B    │                      │ │ │ │ │
   │  │  │  │    │                      │ │ │ │ │
   │  └──┼──┼────┼──────────────────────┘ │ │ │ │
   │     │  │    │                        │ │ │ │
   │     └──┼────┼────────────────────────┘ │ │ │
   │        │    │                          │ │ │
   │        └────┼──────────────────────────┘ │ │
   │             │                            │ │
   └─────────────┘                            │ │
                                              │ │
   POTENTIOMETER                              │ │
   ┌─────────────┐                            │ │
   │      ┌─┐    │                            │ │
   │   1──┤ │─3  │                            │ │
   │      │ │    │                            │ │
   │      └─┘    │                            │ │
   │       │     │                            │ │
   │       2     │                            │ │
   │       │     │                            │ │
   │       └─────┼────────────────────────────┘ │
   │             │                              │
   │   1─────────┼──────────────────────────────┘
   │             │
   │   3─────────┼──────────────────────────────┐
   │             │                              │
   └─────────────┘                              │
                                                │
   STATUS LED                                   │
   ┌─────────────┐                              │
   │             │                              │
   │ ●───[220Ω]──┼──────────────────────────────┘
   │             │
   │ ●───[LED]───┼──────────────────────────────┐
   │             │                              │
   │ ●───────────┼──────────────────────────────┘
   │             │
   └─────────────┘
```

---

## 🎛️ **Servo Control Programming**

### **Basic Position Control:**
```cpp
#include <Servo.h>

Servo myServo;

void setup() {
    myServo.attach(9);
    Serial.begin(9600);
}

void loop() {
    // Read potentiometer value
    int potValue = analogRead(A0);
    
    // Map to servo range (0-180 degrees)
    int servoPos = map(potValue, 0, 1023, 0, 180);
    
    // Move servo to position
    myServo.write(servoPos);
    
    // Update status LED brightness based on position
    int ledBrightness = map(servoPos, 0, 180, 0, 255);
    analogWrite(13, ledBrightness);
    
    // Print position info
    Serial.print("Pot: ");
    Serial.print(potValue);
    Serial.print(" -> Servo: ");
    Serial.print(servoPos);
    Serial.println("°");
    
    delay(50);
}
```

### **Smooth Movement:**
```cpp
void smoothMove(int targetPos, int speed) {
    int currentPos = myServo.read();
    
    if (currentPos < targetPos) {
        for (int pos = currentPos; pos <= targetPos; pos++) {
            myServo.write(pos);
            delay(speed);
        }
    } else {
        for (int pos = currentPos; pos >= targetPos; pos--) {
            myServo.write(pos);
            delay(speed);
        }
    }
}
```

### **Sweep Pattern:**
```cpp
void sweepPattern() {
    // Sweep from 0 to 180 degrees
    for (int pos = 0; pos <= 180; pos++) {
        myServo.write(pos);
        delay(15);
    }
    
    // Sweep from 180 to 0 degrees
    for (int pos = 180; pos >= 0; pos--) {
        myServo.write(pos);
        delay(15);
    }
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check servo wire colors** - Orange/White to D9, Red to 5V, Brown/Black to GND
2. **Verify power connections** - Servo needs 5V, not 3.3V
3. **Confirm potentiometer wiring** - Middle pin to A0, sides to 5V and GND
4. **Test LED polarity** - Long leg to resistor, short leg to GND

### **Servo Test Sequence:**
```cpp
void testServo() {
    Serial.println("Testing servo positions...");
    
    // Test center position
    Serial.println("Moving to center (90°)");
    myServo.write(90);
    delay(1000);
    
    // Test full left
    Serial.println("Moving to left (0°)");
    myServo.write(0);
    delay(1000);
    
    // Test full right
    Serial.println("Moving to right (180°)");
    myServo.write(180);
    delay(1000);
    
    // Return to center
    Serial.println("Returning to center");
    myServo.write(90);
    delay(1000);
}
```

### **Potentiometer Test:**
```cpp
void testPotentiometer() {
    Serial.println("Testing potentiometer...");
    
    for (int i = 0; i < 10; i++) {
        int reading = analogRead(A0);
        Serial.print("Potentiometer reading: ");
        Serial.println(reading);
        delay(500);
    }
}
```

### **Troubleshooting:**
- **Servo doesn't move**: Check power and signal connections
- **Erratic movement**: Verify potentiometer wiring and readings
- **Servo jitters**: Check for loose connections or power issues
- **LED doesn't respond**: Confirm resistor value and LED polarity

### **Advanced Diagnostics:**
```cpp
void diagnostics() {
    Serial.println("=== SERVO DIAGNOSTIC ===");
    
    // Check potentiometer range
    Serial.println("Turn potentiometer fully left...");
    delay(3000);
    int minReading = analogRead(A0);
    Serial.print("Min reading: ");
    Serial.println(minReading);
    
    Serial.println("Turn potentiometer fully right...");
    delay(3000);
    int maxReading = analogRead(A0);
    Serial.print("Max reading: ");
    Serial.println(maxReading);
    
    // Test servo range
    Serial.println("Testing servo range...");
    myServo.write(0);
    delay(1000);
    myServo.write(90);
    delay(1000);
    myServo.write(180);
    delay(1000);
    
    Serial.println("Diagnostic complete!");
}
```

---

## 🎪 **Creative Servo Projects**

### **Robotic Arm Base:**
```cpp
// Simple robotic arm joint
void armControl() {
    int joystickX = analogRead(A0);
    int joystickY = analogRead(A1);
    
    int shoulderAngle = map(joystickX, 0, 1023, 0, 180);
    int elbowAngle = map(joystickY, 0, 1023, 0, 180);
    
    shoulderServo.write(shoulderAngle);
    elbowServo.write(elbowAngle);
}
```

### **Automated Pet Feeder:**
```cpp
// Timed feeding mechanism
void feedingSequence() {
    Serial.println("Feeding time!");
    
    // Open feeder door
    myServo.write(90);
    delay(2000);
    
    // Close feeder door
    myServo.write(0);
    delay(1000);
    
    Serial.println("Feeding complete!");
}
```

### **Security Camera Pan:**
```cpp
// Automatic scanning
void securityScan() {
    // Scan left to right
    for (int angle = 0; angle <= 180; angle += 5) {
        myServo.write(angle);
        delay(100);
        
        // Check for motion or trigger
        if (digitalRead(2) == HIGH) {
            Serial.println("Motion detected!");
            break;
        }
    }
    
    // Return to center
    myServo.write(90);
}
```

---

## 🎉 **Success! You've Built a Servo Control System!**

**Congratulations, Robotics Engineer!** Your servo motor control system is now operational! You've learned PWM control, precision positioning, and feedback systems - essential skills for robotics, automation, and mechanical control systems!

### **Next Steps:**
- Add multiple servos for robotic arm
- Create autonomous scanning systems
- Build remote-controlled mechanisms
- Add sensor feedback for closed-loop control

### **Advanced Features:**
```cpp
// Position memory system
struct ServoPosition {
    int angle;
    int speed;
    int delay_time;
};

ServoPosition sequence[] = {
    {0, 20, 1000},
    {90, 15, 500},
    {180, 10, 2000},
    {90, 25, 0}
};

void playSequence() {
    for (int i = 0; i < 4; i++) {
        smoothMove(sequence[i].angle, sequence[i].speed);
        delay(sequence[i].delay_time);
    }
}

// Servo calibration
void calibrateServo() {
    Serial.println("Servo calibration mode");
    Serial.println("Send angles 0-180 via Serial");
    
    while (Serial.available() > 0) {
        int angle = Serial.parseInt();
        if (angle >= 0 && angle <= 180) {
            myServo.write(angle);
            Serial.print("Moved to: ");
            Serial.println(angle);
        }
    }
}
```

### **Real-World Applications:**
- **Robotics**: Robotic arms and joints
- **Automation**: Conveyor systems and sorting
- **Aerospace**: Flight control surfaces
- **Automotive**: Mirror and seat adjustment
- **Entertainment**: Animatronics and props

---

*Precision and control are the foundations of great engineering! Keep building! 🚀*