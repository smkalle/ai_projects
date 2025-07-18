# 🕵️ Program 2: Button Input Circuit Diagram

## 🎯 **SECRET AGENT MISSION**
Create a covert communication system with button-controlled signals!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **LED** (1x - any color)
- **Push Button** (1x)
- **220Ω Resistor** (1x - for LED)
- **Breadboard** (1x)
- **Jumper Wires** (4x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         D13 │────────────────┤ LED Circuit     │
    │             │                │   [220Ω]        │
    │             │                │     │           │
    │             │                │   [LED]         │
    │             │                │     │           │
    │         GND │────┬───────────┤ LED Ground      │
    │             │    │           │                 │
    │          D2 │────┼───────────┤ Button Input    │
    │             │    │           │     │           │
    │             │    └───────────┤ Button Ground   │
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
│  5  5  .  .  .  .  .  .  .  .  │ ← Button Circuit
│  6  6  .  .  .  .  .  .  .  .  │
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

### **Step 3: Install Push Button**
- **Button pin 1** → Row 5, column 'a'
- **Button pin 2** → Row 5, column 'c'
- **Button pin 3** → Row 6, column 'a'
- **Button pin 4** → Row 6, column 'c'

```
Button Layout:
┌─────────────────────────────────┐
│  5  5  1─────3  .  .  .  .  .  │ ← Button pins 1&3
│  6  6  2─────4  .  .  .  .  .  │ ← Button pins 2&4
└─────────────────────────────────┘

Button Internal Connection:
   1 ─────── 3
   │         │
   │ SWITCH  │
   │         │
   2 ─────── 4
```

### **Step 4: Connect Jumper Wires**
- **Red wire**: Arduino D13 → Row 3, column 'c' (to resistor)
- **Black wire 1**: Arduino GND → Row 2, column 'c' (to LED cathode)
- **Yellow wire**: Arduino D2 → Row 5, column 'b' (to button)
- **Black wire 2**: Arduino GND → Row 6, column 'b' (to button)

```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  +  R──.  .  .  .  .  .  │ LED anode + resistor
│  2  2  -  │  ●  .  .  .  .  .  │ LED cathode + GND
│  3  3  .  R──●  .  .  .  .  .  │ Resistor + D13
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  B──●──B  .  .  .  .  .  │ Button + D2
│  6  6  B──●──B  .  .  .  .  .  │ Button + GND
└─────────────────────────────────┘

● = Jumper wire connection
R = Resistor
+ = LED long leg (anode)
- = LED short leg (cathode)
B = Button pins
```

---

## ⚡ **Circuit Explanation**

### **How It Works:**

#### **LED Circuit:**
1. **Arduino D13** controls LED on/off
2. **Resistor** protects LED from too much current
3. **Ground** completes the circuit

#### **Button Circuit:**
1. **Button** creates/breaks connection when pressed
2. **Internal pull-up** resistor keeps input HIGH when button not pressed
3. **Pressing button** connects input to ground (LOW)

### **Signal Flow:**
```
Button NOT Pressed:
D2 Input ← Internal Pull-up ← 5V (HIGH)

Button Pressed:
D2 Input ← Button ← Ground (LOW)
```

### **Program Logic:**
```
if (button == LOW) {
    // Button is pressed
    LED ON
} else {
    // Button not pressed
    LED OFF
}
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
   │ D13 ●────────┼─── RED WIRE ──────┐
   │             │                   │
   │  D2 ●────────┼─── YELLOW WIRE ───┼─┐
   │             │                   │ │
   │ GND ●────────┼─── BLACK WIRE ────┼─┼─┐
   │             │                   │ │ │
   └─────────────┘                   │ │ │
                                     │ │ │
   BREADBOARD                        │ │ │
   ┌─────────────┐                   │ │ │
   │             │                   │ │ │
   │ ●───[220Ω]──┼───────────────────┘ │ │
   │             │                     │ │
   │ ●───[LED]───┼─────────────────────┘ │
   │             │                       │
   │ ●───[BTN]───┼───────────────────────┘
   │             │                       
   │ ●───[BTN]───┼───────────────────────┘
   │             │
   └─────────────┘
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check LED polarity** (long leg to resistor)
2. **Verify button orientation** (check pin positions)
3. **Confirm all connections** match diagram
4. **Test button** mechanically (should click)

### **After Upload:**
- **LED OFF** when button not pressed
- **LED ON** when button pressed
- **Immediate response** to button press/release
- **No flickering** or erratic behavior

### **Troubleshooting:**
- **LED always on**: Check button wiring
- **LED always off**: Check LED polarity or D13 connection
- **LED flickers**: Button may be bouncing (normal)
- **No response**: Check D2 connection or button orientation

---

## 🎛️ **Button Wiring Explained**

### **Why We Use INPUT_PULLUP:**
```
Without Pull-up:           With Pull-up:
┌─────────┐               ┌─────────┐
│   D2    │               │   D2    │
│         │               │    ↑    │
│   ???   │               │   10kΩ  │
│         │               │    ↑    │
│  [BTN]  │               │  [BTN]  │
│    │    │               │    │    │
│   GND   │               │   GND   │
└─────────┘               └─────────┘
 Floating input            Stable input
```

### **Button States:**
- **Not Pressed**: INPUT_PULLUP pulls D2 to HIGH (5V)
- **Pressed**: Button connects D2 to GND (LOW)

---

## 🎉 **Success! You've Built an Interactive System!**

**Congratulations, Secret Agent!** Your communication system is operational. You've learned digital input, pull-up resistors, and user interaction - essential skills for creating responsive systems!

### **Next Steps:**
- Try different button types (momentary, toggle)
- Add multiple buttons for different functions
- Create morse code patterns
- Use button to control different outputs

---

*Your mission continues... Keep building! 🚀*