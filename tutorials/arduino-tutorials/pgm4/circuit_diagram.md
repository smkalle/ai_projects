# 🎛️ Program 4: Potentiometer Reading Circuit Diagram

## 🎯 **DIMMER SWITCH ENGINEER MISSION**
Create a smooth dimmer control system with analog input!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **LED** (1x - any color)
- **Potentiometer** (1x - 10kΩ)
- **220Ω Resistor** (1x)
- **Breadboard** (1x)
- **Jumper Wires** (5x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         D9~ │────────────────┤ LED PWM Control │
    │             │                │   [220Ω]        │
    │             │                │     │           │
    │             │                │   [LED]         │
    │             │                │     │           │
    │         GND │────┬───────────┤ Common Ground   │
    │             │    │           │                 │
    │         5V  │────┼───────────┤ Potentiometer   │
    │             │    │           │   [POT]         │
    │         A0  │────┼───────────┤     │           │
    │             │    └───────────┤     │           │
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
│  1  1  .  .  .  .  .  .  .  .  │ ← LED Circuit
│  2  2  .  .  .  .  .  .  .  .  │
│  3  3  .  .  .  .  .  .  .  .  │
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  .  .  .  .  .  .  .  .  │ ← Potentiometer
│  6  6  .  .  .  .  .  .  .  .  │
│  7  7  .  .  .  .  .  .  .  .  │
└─────────────────────────────────┘
```

### **Step 2: Install LED Circuit**
- **LED long leg** → Row 1, column 'a'
- **LED short leg** → Row 2, column 'a'
- **220Ω resistor** → Row 1, column 'b' to Row 3, column 'b'

```
LED Circuit:
┌─────────────────────────────────┐
│  1  1  +  R  .  .  .  .  .  .  │ ← LED anode + resistor
│  2  2  -  │  .  .  .  .  .  .  │ ← LED cathode
│  3  3  .  R  .  .  .  .  .  .  │ ← Resistor end
└─────────────────────────────────┘
```

### **Step 3: Install Potentiometer**
Potentiometer has 3 pins:
- **Pin 1** (Left) → Row 5, column 'a'
- **Pin 2** (Center/Wiper) → Row 6, column 'a'
- **Pin 3** (Right) → Row 7, column 'a'

```
Potentiometer Layout:
┌─────────────────────────────────┐
│  5  5  1  .  .  .  .  .  .  .  │ ← Pot pin 1 (5V)
│  6  6  2  .  .  .  .  .  .  .  │ ← Pot pin 2 (Wiper/Signal)
│  7  7  3  .  .  .  .  .  .  .  │ ← Pot pin 3 (GND)
└─────────────────────────────────┘

Potentiometer Symbol:
   Pin 1 ──┬─────────────┬── Pin 3
          │             │
          │    5V      GND
          │             │
          └──── Pin 2 ────┘ (Wiper - variable voltage)
```

### **Step 4: Connect Jumper Wires**
- **Red wire 1**: Arduino D9 → Row 3, column 'c' (LED control)
- **Black wire 1**: Arduino GND → Row 2, column 'c' (LED ground)
- **Red wire 2**: Arduino 5V → Row 5, column 'b' (Pot power)
- **Yellow wire**: Arduino A0 → Row 6, column 'b' (Pot signal)
- **Black wire 2**: Arduino GND → Row 7, column 'b' (Pot ground)

```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  +  R──.  .  .  .  .  .  │ LED anode + resistor
│  2  2  -  │  ●  .  .  .  .  .  │ LED cathode + GND
│  3  3  .  R──●  .  .  .  .  .  │ Resistor + D9 (PWM)
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  P──●  .  .  .  .  .  .  │ Pot pin 1 + 5V
│  6  6  P──●  .  .  .  .  .  .  │ Pot pin 2 + A0
│  7  7  P──●  .  .  .  .  .  .  │ Pot pin 3 + GND
└─────────────────────────────────┘

● = Jumper wire connection
R = Resistor
+ = LED long leg (anode)
- = LED short leg (cathode)
P = Potentiometer pins
```

---

## ⚡ **How Potentiometer Works**

### **Voltage Divider Principle:**
```
5V ──────┬─────────────┬─── GND
         │             │
         │    R1      R2
         │             │
         └─── OUTPUT ───┘
              (Wiper)

OUTPUT = 5V × (R2 / (R1 + R2))
```

### **Potentiometer Positions:**
```
Fully Counter-Clockwise:    Center Position:         Fully Clockwise:
5V ──────┬─────────────┬─── GND     5V ──────┬─────────────┬─── GND     5V ──────┬─────────────┬─── GND
         │             │                     │             │                     │             │
         │     0Ω    10kΩ                    │    5kΩ    5kΩ                    │   10kΩ     0Ω
         │             │                     │             │                     │             │
         └─── 0V ──────┘                     └─── 2.5V ────┘                     └─── 5V ──────┘

analogRead() = 0               analogRead() = 512            analogRead() = 1023
analogWrite() = 0              analogWrite() = 127           analogWrite() = 255
LED = OFF                      LED = HALF BRIGHT             LED = FULL BRIGHT
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
   │  5V ●────────┼─── RED WIRE ──────┐
   │             │                   │
   │  A0 ●────────┼─── YELLOW WIRE ───┼─┐
   │             │                   │ │
   │  D9~●────────┼─── ORANGE WIRE ───┼─┼─┐
   │             │                   │ │ │
   │ GND ●────────┼─── BLACK WIRE ────┼─┼─┼─┐
   │             │                   │ │ │ │
   └─────────────┘                   │ │ │ │
                                     │ │ │ │
   POTENTIOMETER                     │ │ │ │
   ┌─────────────┐                   │ │ │ │
   │      ●      │ ← Wiper (A0)      │ │ │ │
   │             │                   │ │ │ │
   │  ●       ●  │ ← 5V & GND        │ │ │ │
   └─────────────┘                   │ │ │ │
                                     │ │ │ │
   BREADBOARD                        │ │ │ │
   ┌─────────────┐                   │ │ │ │
   │             │                   │ │ │ │
   │ ●───[220Ω]──┼───────────────────┘ │ │ │
   │             │                     │ │ │
   │ ●───[LED]───┼─────────────────────┘ │ │
   │             │                       │ │
   │ ●───[POT]───┼───────────────────────┘ │
   │             │                         │
   │ ●───[POT]───┼─────────────────────────┘
   │             │                         
   │ ●───[POT]───┼─────────────────────────┘
   │             │
   └─────────────┘
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check potentiometer wiring** (5V, signal, GND)
2. **Verify LED polarity** (long leg to resistor)
3. **Confirm PWM pin** (D9 has ~ symbol)
4. **Test pot rotation** (should turn smoothly)

### **After Upload:**
- **Turn pot left**: LED dims or turns off
- **Turn pot right**: LED brightens
- **Smooth response**: No flickering or jumping
- **Full range**: From completely off to full bright

### **Troubleshooting:**
- **LED doesn't change**: Check A0 and potentiometer wiring
- **LED always on/off**: Check PWM pin and LED circuit
- **Backwards control**: Swap pot 5V and GND connections
- **Jumpy response**: Check for loose connections

---

## 📊 **Analog Input Explained**

### **ADC (Analog-to-Digital Converter):**
```
Analog Input Range:    Digital Output Range:
0V ────────────────→   0 (analogRead)
1V ────────────────→   204
2V ────────────────→   409
3V ────────────────→   614
4V ────────────────→   819
5V ────────────────→   1023

10-bit ADC = 2^10 = 1024 possible values (0-1023)
```

### **Mapping Values:**
```
Input Range:     Output Range:
0 - 1023    →    0 - 255

Code: 
int sensorValue = analogRead(A0);        // 0-1023
int brightness = map(sensorValue, 0, 1023, 0, 255);  // 0-255
analogWrite(9, brightness);              // PWM output
```

---

## 🎛️ **Potentiometer Types**

### **Linear Potentiometer:**
```
Resistance changes linearly with position
0° ────────────────────── 270°
0Ω                       10kΩ
```

### **Logarithmic Potentiometer:**
```
Resistance changes logarithmically (audio taper)
0° ────────────────────── 270°
0Ω                       10kΩ
   └─ More change at low end
```

### **Physical Identification:**
```
Potentiometer Markings:
A10K = 10kΩ Linear
B10K = 10kΩ Logarithmic
```

---

## 🎉 **Success! You've Built an Analog Control System!**

**Congratulations, Dimmer Switch Engineer!** Your analog control system responds smoothly to user input. You've learned analog input, voltage dividers, and real-time control - essential skills for creating responsive interfaces!

### **Next Steps:**
- Try different potentiometer values (1kΩ, 100kΩ)
- Control multiple LEDs with one potentiometer
- Add serial output to see actual values
- Create non-linear response curves

### **Code Examples to Try:**
```cpp
// Reverse control
int brightness = map(sensorValue, 0, 1023, 255, 0);

// Non-linear response
int brightness = (sensorValue * sensorValue) / 4095;

// Threshold control
int brightness = (sensorValue > 512) ? 255 : 0;
```

---

*Control is in your hands... Keep building! 🚀*