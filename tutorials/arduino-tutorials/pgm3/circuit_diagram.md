# 💡 Program 3: PWM LED Fade Circuit Diagram

## 🎯 **LIGHT SHOW DESIGNER MISSION**
Create smooth, professional lighting effects with PWM control!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **LED** (1x - any color)
- **220Ω Resistor** (1x)
- **Breadboard** (1x)
- **Jumper Wires** (2x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────┐
    │             │                │             │
    │         D9~ │────────────────┤ PWM Signal  │
    │             │                │             │
    │             │                │   [220Ω]    │ ← Current limiting
    │             │                │     │       │
    │             │                │   [LED]     │ ← LED (Long leg to resistor)
    │             │                │     │       │
    │         GND │────────────────┤ Ground      │
    │             │                │             │
    └─────────────┘                └─────────────┘

    ~ = PWM capable pin (important!)
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
│  5  5  .  .  .  .  .  .  .  .  │
└─────────────────────────────────┘
```

### **Step 2: Install LED**
- **LED long leg (anode)** → Row 1, column 'a'
- **LED short leg (cathode)** → Row 2, column 'a'

```
LED Installation:
┌─────────────────────────────────┐
│  1  1  +  .  .  .  .  .  .  .  │ ← LED anode (long leg)
│  2  2  -  .  .  .  .  .  .  .  │ ← LED cathode (short leg)
└─────────────────────────────────┘
```

### **Step 3: Install Resistor**
- **Resistor end 1** → Row 1, column 'b' (same row as LED anode)
- **Resistor end 2** → Row 3, column 'b'

```
Resistor Installation:
┌─────────────────────────────────┐
│  1  1  +  R  .  .  .  .  .  .  │ ← LED anode + resistor
│  2  2  -  │  .  .  .  .  .  .  │ ← LED cathode
│  3  3  .  R  .  .  .  .  .  .  │ ← Resistor end
└─────────────────────────────────┘
```

### **Step 4: Connect Jumper Wires**
- **Red wire**: Arduino D9 → Row 3, column 'c' (to resistor)
- **Black wire**: Arduino GND → Row 2, column 'c' (to LED cathode)

```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  +  R──.  .  .  .  .  .  │ LED anode + resistor
│  2  2  -  │  ●  .  .  .  .  .  │ LED cathode + GND
│  3  3  .  R──●  .  .  .  .  .  │ Resistor + D9 (PWM)
└─────────────────────────────────┘

● = Jumper wire connection
R = Resistor
+ = LED long leg (anode)
- = LED short leg (cathode)
```

---

## ⚡ **PWM Explanation**

### **What is PWM?**
PWM (Pulse Width Modulation) rapidly switches the output ON and OFF to simulate different voltage levels:

```
100% Brightness (analogWrite(255)):
D9: ████████████████████████████████ (Always ON)

75% Brightness (analogWrite(191)):
D9: ██████████████████████▄▄▄▄▄▄▄▄▄▄ (75% ON, 25% OFF)

50% Brightness (analogWrite(127)):
D9: ████████████████▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ (50% ON, 50% OFF)

25% Brightness (analogWrite(63)):
D9: ████████▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ (25% ON, 75% OFF)

0% Brightness (analogWrite(0)):
D9: ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄ (Always OFF)
```

### **PWM Pins on Arduino Uno:**
```
Arduino Uno PWM Pins (marked with ~):
┌─────────────────────────────────┐
│  D3~  D5~  D6~  D9~  D10~  D11~ │
└─────────────────────────────────┘
⚠️  Only these pins can use analogWrite()!
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
   │  D9~●────────┼─── RED WIRE ───┐
   │             │                │
   │ GND ●────────┼─── BLACK WIRE ─┼─┐
   │             │                │ │
   └─────────────┘                │ │
                                  │ │
   BREADBOARD                     │ │
   ┌─────────────┐                │ │
   │             │                │ │
   │ ●───[220Ω]──┼────────────────┘ │
   │             │                  │
   │ ●───[LED]───┼──────────────────┘
   │             │
   └─────────────┘
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Verify PWM pin** - Must use D3, D5, D6, D9, D10, or D11
2. **Check LED polarity** (long leg to resistor)
3. **Confirm resistor** is in the circuit
4. **Test connections** with multimeter if available

### **After Upload:**
- **LED fades in and out** smoothly
- **No flickering** at low brightness
- **Smooth transitions** between brightness levels
- **No overheating** of components

### **Troubleshooting:**
- **LED doesn't fade**: Check if using PWM pin (marked with ~)
- **LED blinks instead of fading**: Wrong pin or bad connection
- **No light**: Check LED polarity or connections
- **Dim overall**: Check resistor value or power supply

---

## 🌟 **PWM Waveform Visualization**

### **How PWM Creates Different Brightness:**
```
High Brightness (analogWrite(200)):
┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐
│ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
│ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
└─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
80% ON time = Bright LED

Medium Brightness (analogWrite(127)):
┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐   ┌─┐
│ │   │ │   │ │   │ │   │ │   │ │
│ │   │ │   │ │   │ │   │ │   │ │
└─┘   └─┘   └─┘   └─┘   └─┘   └─┘
50% ON time = Medium LED

Low Brightness (analogWrite(50)):
┌┐     ┌┐     ┌┐     ┌┐     ┌┐     ┌┐
││     ││     ││     ││     ││     ││
││     ││     ││     ││     ││     ││
└┘     └┘     └┘     └┘     └┘     └┘
20% ON time = Dim LED
```

---

## 🎭 **Fade Patterns You Can Create**

### **Linear Fade:**
```
Brightness
    ↑
255 │    ╱╲    ╱╲    ╱╲
    │   ╱  ╲  ╱  ╲  ╱  ╲
    │  ╱    ╲╱    ╲╱    ╲
  0 │─╱──────────────────────→ Time
```

### **Sine Wave Fade:**
```
Brightness
    ↑
255 │   ╭─╮   ╭─╮   ╭─╮
    │  ╱   ╲ ╱   ╲ ╱   ╲
    │ ╱     ╲╱     ╲╱     ╲
  0 │╱───────────────────────→ Time
```

### **Pulse Pattern:**
```
Brightness
    ↑
255 │ ██  ██  ██  ██  ██  ██
    │ ██  ██  ██  ██  ██  ██
    │ ██  ██  ██  ██  ██  ██
  0 │────────────────────────→ Time
```

---

## 🎉 **Success! You've Mastered PWM Control!**

**Congratulations, Light Show Designer!** Your LED now smoothly fades like professional lighting systems. You've learned PWM, analog output, and smooth animations - core skills for creating impressive visual effects!

### **Next Steps:**
- Try different fade patterns (sine wave, pulse)
- Control multiple LEDs with different fade speeds
- Add button control to change fade patterns
- Create RGB color fading effects

### **Code Examples to Try:**
```cpp
// Breathing effect
for (int i = 0; i < 256; i++) {
    analogWrite(9, i);
    delay(10);
}

// Heartbeat pattern
analogWrite(9, 255); delay(100);
analogWrite(9, 0);   delay(100);
analogWrite(9, 255); delay(100);
analogWrite(9, 0);   delay(500);
```

---

*The show must go on... Keep creating! 🚀*