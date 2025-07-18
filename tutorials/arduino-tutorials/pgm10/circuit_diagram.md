# 💾 Program 10: Data Logger Circuit Diagram

## 🎯 **DATA SCIENTIST MISSION**
Build a comprehensive environmental monitoring system that stores data over time!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **16x2 LCD Display** (1x)
- **TMP36 Temperature Sensor** (1x)
- **Photoresistor (LDR)** (1x)
- **Potentiometer (10kΩ)** (1x) - for LCD contrast
- **10kΩ Resistor** (1x) - for photoresistor
- **Push Button** (1x) - for mode selection
- **10kΩ Resistor** (1x) - for button pull-up
- **LED** (1x) - for status indication
- **220Ω Resistor** (1x) - for LED
- **Breadboard** (2x or 1 large)
- **Jumper Wires** (20x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Multi-Sensor Array
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │  D2-D5,D11  │────────────────┤ LCD Display     │
    │         D12 │────────────────┤ LCD Enable      │
    │             │                │                 │
    │         A0  │────────────────┤ Temperature     │
    │         A1  │────────────────┤ Light Sensor    │
    │         A2  │────────────────┤ LCD Contrast    │
    │             │                │                 │
    │         D7  │────────────────┤ Mode Button     │
    │        D13  │────────────────┤ Status LED      │
    │             │                │                 │
    │         5V  │────────────────┤ Power Rails     │
    │         GND │────────────────┤ Ground Rails    │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: Breadboard Layout Planning**
This is a complex circuit - plan your layout carefully:

```
Main Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← LCD Pin 1 (VSS)
│  2  2  .  .  .  .  .  .  .  .  │ ← LCD Pin 2 (VDD)
│  3  3  .  .  .  .  .  .  .  .  │ ← LCD Pin 3 (V0)
│  4  4  .  .  .  .  .  .  .  .  │ ← LCD Pin 4 (RS)
│  5  5  .  .  .  .  .  .  .  .  │ ← LCD Pin 5 (EN)
│  6  6  .  .  .  .  .  .  .  .  │ ← LCD Pin 6 (D0) - not used
│  7  7  .  .  .  .  .  .  .  .  │ ← LCD Pin 7 (D1) - not used
│  8  8  .  .  .  .  .  .  .  .  │ ← LCD Pin 8 (D2) - not used
│  9  9  .  .  .  .  .  .  .  .  │ ← LCD Pin 9 (D3) - not used
│ 10 10  .  .  .  .  .  .  .  .  │ ← LCD Pin 10 (D4)
│ 11 11  .  .  .  .  .  .  .  .  │ ← LCD Pin 11 (D5)
│ 12 12  .  .  .  .  .  .  .  .  │ ← LCD Pin 12 (D6)
│ 13 13  .  .  .  .  .  .  .  .  │ ← LCD Pin 13 (D7)
│ 14 14  .  .  .  .  .  .  .  .  │ ← LCD Pin 14 (A)
│ 15 15  .  .  .  .  .  .  .  .  │ ← LCD Pin 15 (K)
└─────────────────────────────────┘

Sensor Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│ 16 16  .  .  .  .  .  .  .  .  │ ← TMP36 Pin 1 (VCC)
│ 17 17  .  .  .  .  .  .  .  .  │ ← TMP36 Pin 2 (OUT)
│ 18 18  .  .  .  .  .  .  .  .  │ ← TMP36 Pin 3 (GND)
│ 19 19  .  .  .  .  .  .  .  .  │
│ 20 20  .  .  .  .  .  .  .  .  │ ← LDR Pin 1
│ 21 21  .  .  .  .  .  .  .  .  │ ← LDR Pin 2
│ 22 22  .  .  .  .  .  .  .  .  │ ← LDR Resistor
│ 23 23  .  .  .  .  .  .  .  .  │
│ 24 24  .  .  .  .  .  .  .  .  │ ← Button Pin 1
│ 25 25  .  .  .  .  .  .  .  .  │ ← Button Pin 2
│ 26 26  .  .  .  .  .  .  .  .  │ ← Button Resistor
│ 27 27  .  .  .  .  .  .  .  .  │
│ 28 28  .  .  .  .  .  .  .  .  │ ← Status LED Anode
│ 29 29  .  .  .  .  .  .  .  .  │ ← Status LED Cathode
│ 30 30  .  .  .  .  .  .  .  .  │ ← LED Resistor
└─────────────────────────────────┘
```

### **Step 2: Install LCD Display**
Connect 16x2 LCD with standard HD44780 controller:

```
LCD Installation:
┌─────────────────────────────────┐
│  1  1  G  .  .  .  .  .  .  .  │ ← VSS (Ground)
│  2  2  V  .  .  .  .  .  .  .  │ ← VDD (5V)
│  3  3  C  .  .  .  .  .  .  .  │ ← V0 (Contrast)
│  4  4  R  .  .  .  .  .  .  .  │ ← RS (Register Select)
│  5  5  E  .  .  .  .  .  .  .  │ ← EN (Enable)
│  6  6  .  .  .  .  .  .  .  .  │ ← D0 (not used)
│  7  7  .  .  .  .  .  .  .  .  │ ← D1 (not used)
│  8  8  .  .  .  .  .  .  .  .  │ ← D2 (not used)
│  9  9  .  .  .  .  .  .  .  .  │ ← D3 (not used)
│ 10 10  4  .  .  .  .  .  .  .  │ ← D4 (Data)
│ 11 11  5  .  .  .  .  .  .  .  │ ← D5 (Data)
│ 12 12  6  .  .  .  .  .  .  .  │ ← D6 (Data)
│ 13 13  7  .  .  .  .  .  .  .  │ ← D7 (Data)
│ 14 14  A  .  .  .  .  .  .  .  │ ← A (Backlight +)
│ 15 15  K  .  .  .  .  .  .  .  │ ← K (Backlight -)
└─────────────────────────────────┘
```

### **Step 3: Install Temperature Sensor**
TMP36 provides ambient temperature readings:

```
TMP36 Installation:
┌─────────────────────────────────┐
│ 16 16  T1 .  .  .  .  .  .  .  │ ← TMP36 Pin 1 (VCC)
│ 17 17  T2 .  .  .  .  .  .  .  │ ← TMP36 Pin 2 (OUT)
│ 18 18  T3 .  .  .  .  .  .  .  │ ← TMP36 Pin 3 (GND)
└─────────────────────────────────┘
```

### **Step 4: Install Light Sensor**
LDR (Light Dependent Resistor) with pull-down resistor:

```
LDR Installation:
┌─────────────────────────────────┐
│ 20 20  L1 .  .  .  .  .  .  .  │ ← LDR Pin 1 (to 5V)
│ 21 21  L2 .  .  .  .  .  .  .  │ ← LDR Pin 2 (to A1)
│ 22 22  LR .  .  .  .  .  .  .  │ ← LDR Resistor (10kΩ)
└─────────────────────────────────┘
```

### **Step 5: Install Mode Button**
Push button for cycling through display modes:

```
Button Installation:
┌─────────────────────────────────┐
│ 24 24  B1 .  .  .  .  .  .  .  │ ← Button Pin 1 (to D7)
│ 25 25  B2 .  .  .  .  .  .  .  │ ← Button Pin 2 (to GND)
│ 26 26  BR .  .  .  .  .  .  .  │ ← Button Resistor (10kΩ)
└─────────────────────────────────┘
```

### **Step 6: Install Status LED**
LED indicates data logging status:

```
Status LED Installation:
┌─────────────────────────────────┐
│ 28 28  S+ .  .  .  .  .  .  .  │ ← LED Anode (long leg)
│ 29 29  S- .  .  .  .  .  .  .  │ ← LED Cathode (short leg)
│ 30 30  SR .  .  .  .  .  .  .  │ ← LED Resistor (220Ω)
└─────────────────────────────────┘
```

### **Step 7: Install Contrast Potentiometer**
10kΩ potentiometer for LCD contrast adjustment:

```
Potentiometer Installation:
┌─────────────────────────────────┐
│ 31 31  P1 .  .  .  .  .  .  .  │ ← Potentiometer Pin 1 (5V)
│ 32 32  P2 .  .  .  .  .  .  .  │ ← Potentiometer Pin 2 (Wiper)
│ 33 33  P3 .  .  .  .  .  .  .  │ ← Potentiometer Pin 3 (GND)
└─────────────────────────────────┘
```

### **Step 8: Connect All Wires**
```
Final Circuit Connections:
┌─────────────────────────────────┐
│  1  1  G──●  .  .  .  .  .  .  │ ← LCD VSS to GND
│  2  2  V──●  .  .  .  .  .  .  │ ← LCD VDD to 5V
│  3  3  C──●  .  .  .  .  .  .  │ ← LCD V0 to Pot wiper
│  4  4  R──●  .  .  .  .  .  .  │ ← LCD RS to D2
│  5  5  E──●  .  .  .  .  .  .  │ ← LCD EN to D12
│  6  6  .  .  .  .  .  .  .  .  │ ← LCD D0 (not used)
│  7  7  .  .  .  .  .  .  .  .  │ ← LCD D1 (not used)
│  8  8  .  .  .  .  .  .  .  .  │ ← LCD D2 (not used)
│  9  9  .  .  .  .  .  .  .  .  │ ← LCD D3 (not used)
│ 10 10  4──●  .  .  .  .  .  .  │ ← LCD D4 to D3
│ 11 11  5──●  .  .  .  .  .  .  │ ← LCD D5 to D4
│ 12 12  6──●  .  .  .  .  .  .  │ ← LCD D6 to D5
│ 13 13  7──●  .  .  .  .  .  .  │ ← LCD D7 to D11
│ 14 14  A──●  .  .  .  .  .  .  │ ← LCD A to 5V
│ 15 15  K──●  .  .  .  .  .  .  │ ← LCD K to GND
│ 16 16  T1─●  .  .  .  .  .  .  │ ← TMP36 VCC to 5V
│ 17 17  T2─●  .  .  .  .  .  .  │ ← TMP36 OUT to A0
│ 18 18  T3─●  .  .  .  .  .  .  │ ← TMP36 GND to GND
│ 19 19  .  .  .  .  .  .  .  .  │
│ 20 20  L1─●  .  .  .  .  .  .  │ ← LDR to 5V
│ 21 21  L2─●──LR .  .  .  .  .  │ ← LDR to A1 + resistor
│ 22 22  LR─●  .  .  .  .  .  .  │ ← LDR resistor to GND
│ 23 23  .  .  .  .  .  .  .  .  │
│ 24 24  B1─●──BR .  .  .  .  .  │ ← Button to D7 + resistor
│ 25 25  B2─●  .  .  .  .  .  .  │ ← Button to GND
│ 26 26  BR─●  .  .  .  .  .  .  │ ← Button resistor to 5V
│ 27 27  .  .  .  .  .  .  .  .  │
│ 28 28  S+─●──SR .  .  .  .  .  │ ← LED anode + resistor
│ 29 29  S-─●  .  .  .  .  .  .  │ ← LED cathode to GND
│ 30 30  SR─●  .  .  .  .  .  .  │ ← LED resistor to D13
│ 31 31  P1─●  .  .  .  .  .  .  │ ← Potentiometer to 5V
│ 32 32  P2─●  .  .  .  .  .  .  │ ← Potentiometer wiper to V0
│ 33 33  P3─●  .  .  .  .  .  .  │ ← Potentiometer to GND
└─────────────────────────────────┘

● = Jumper wire connections
LR = LDR resistor (10kΩ)
BR = Button resistor (10kΩ)
SR = LED resistor (220Ω)
```

### **Step 9: Wire Connections Summary**
**LCD Connections:**
- D2 → LCD RS (Register Select)
- D3 → LCD D4 (Data bit 4)
- D4 → LCD D5 (Data bit 5)
- D5 → LCD D6 (Data bit 6)
- D11 → LCD D7 (Data bit 7)
- D12 → LCD EN (Enable)

**Sensor Connections:**
- A0 → TMP36 Output (Temperature)
- A1 → LDR Junction (Light level)
- A2 → Potentiometer Wiper (Contrast) [Optional]

**Control Connections:**
- D7 → Mode Button (with pull-up resistor)
- D13 → Status LED (with current-limiting resistor)

**Power Connections:**
- 5V → LCD VDD, TMP36 VCC, LDR, Button pull-up, Potentiometer, LCD backlight
- GND → LCD VSS, TMP36 GND, LDR resistor, Button, LED cathode, Potentiometer, LCD backlight

---

## ⚡ **Circuit Explanation**

### **How Data Logging Works:**
1. **Sensors collect data** continuously (temperature, light)
2. **Arduino processes** and stores readings in memory
3. **LCD displays** current values and statistics
4. **Button cycles** through different display modes
5. **Status LED** indicates active logging

### **Data Storage Strategy:**
```
Arduino Memory Usage:
- SRAM: 2KB (for variables and program stack)
- EEPROM: 1KB (for permanent data storage)
- Flash: 32KB (for program code)

Data Storage Options:
1. Array in SRAM (temporary, lost on reset)
2. EEPROM (permanent, 100,000 write cycles)
3. SD card (external, unlimited storage)
```

### **Sensor Reading Process:**
```
Data Collection Cycle:
1. Read temperature from TMP36 (A0)
2. Read light level from LDR (A1)
3. Convert ADC values to real units
4. Calculate statistics (min, max, average)
5. Store in memory if changed significantly
6. Update display with current mode
7. Wait for next reading interval
```

### **Display Modes:**
```
Mode 1: Current Values
T: 23.5°C  L: 65%
Status: Logging

Mode 2: Statistics
Max: 25.1°C  78%
Min: 21.3°C  45%

Mode 3: Data Points
Entry 1: 23.5°C
Entry 2: 24.1°C

Mode 4: System Info
Uptime: 2h 15m
Samples: 542
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
   │  A0 ●────────┼─── TEMP SENSOR ──────────┐
   │  A1 ●────────┼─── LIGHT SENSOR ─────────┼─┐
   │  A2 ●────────┼─── CONTRAST POT ─────────┼─┼─┐
   │             │                          │ │ │
   │  D2 ●────────┼─── LCD RS ──────────────┼─┼─┼─┐
   │  D3 ●────────┼─── LCD D4 ──────────────┼─┼─┼─┼─┐
   │  D4 ●────────┼─── LCD D5 ──────────────┼─┼─┼─┼─┼─┐
   │  D5 ●────────┼─── LCD D6 ──────────────┼─┼─┼─┼─┼─┼─┐
   │  D7 ●────────┼─── MODE BUTTON ─────────┼─┼─┼─┼─┼─┼─┼─┐
   │ D11 ●────────┼─── LCD D7 ──────────────┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D12 ●────────┼─── LCD EN ──────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D13 ●────────┼─── STATUS LED ──────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                          │ │ │ │ │ │ │ │ │ │ │
   │  5V ●────────┼─── POWER BUS ───────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ GND ●────────┼─── GROUND BUS ──────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                          │ │ │ │ │ │ │ │ │ │ │ │ │
   └─────────────┘                          │ │ │ │ │ │ │ │ │ │ │ │ │
                                            │ │ │ │ │ │ │ │ │ │ │ │ │
   16x2 LCD DISPLAY                         │ │ │ │ │ │ │ │ │ │ │ │ │
   ┌─────────────────────────────────┐      │ │ │ │ │ │ │ │ │ │ │ │ │
   │  T:23.5°C  L:65%  │             │      │ │ │ │ │ │ │ │ │ │ │ │ │
   │  Status: Logging  │             │      │ │ │ │ │ │ │ │ │ │ │ │ │
   └─────────────────────────────────┘      │ │ │ │ │ │ │ │ │ │ │ │ │
   │1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16│ │ │ │ │ │ │ │ │ │ │ │ │
   │● ● ● ● ● ● ● ● ● ●  ●  ●  ●  ●  ●  ●│ │ │ │ │ │ │ │ │ │ │ │ │
   │└─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──┼──┼──┘ │ │ │ │ │ │ │ │ │ │ │ │
   │  │ │ │ │ │ │ │ │ │  │  │  │  │  │    │ │ │ │ │ │ │ │ │ │ │ │
   │  └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──┼──┼──┘ │ │ │ │ │ │ │ │ │ │ │
   │    │ │ │ │ │ │ │ │ │  │  │  │  │  │    │ │ │ │ │ │ │ │ │ │ │
   │    └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──┼────┘ │ │ │ │ │ │ │ │ │ │
   │      │ │ │ │ │ │ │ │ │  │  │  │  │      │ │ │ │ │ │ │ │ │ │
   │      └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──────┘ │ │ │ │ │ │ │ │ │
   │        │ │ │ │ │ │ │ │ │  │  │  │        │ │ │ │ │ │ │ │ │
   │        └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼────────┘ │ │ │ │ │ │ │ │
   │          │ │ │ │ │ │ │ │ │  │  │          │ │ │ │ │ │ │ │
   │          └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │ │ │
   │            │ │ │ │ │ │ │ │ │  │            │ │ │ │ │ │ │
   │            └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │ │
   │              │ │ │ │ │ │ │ │ │  │            │ │ │ │ │ │
   │              └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │
   │                │ │ │ │ │ │ │ │ │  │            │ │ │ │ │
   └────────────────┘ │ │ │ │ │ │ │ │ │            │ │ │ │ │
                      │ │ │ │ │ │ │ │ │            │ │ │ │ │
   TMP36 TEMP SENSOR  │ │ │ │ │ │ │ │ │            │ │ │ │ │
   ┌─────────────┐    │ │ │ │ │ │ │ │ │            │ │ │ │ │
   │  ┌─────────┐│    │ │ │ │ │ │ │ │ │            │ │ │ │ │
   │  │ TMP36   ││    │ │ │ │ │ │ │ │ │            │ │ │ │ │
   │  └─────────┘│    │ │ │ │ │ │ │ │ │            │ │ │ │ │
   │  1  2  3    │    │ │ │ │ │ │ │ │ │            │ │ │ │ │
   │  │  │  │    │    │ │ │ │ │ │ │ │ │            │ │ │ │ │
   │  └──┼──┼────┼────┘ │ │ │ │ │ │ │ │            │ │ │ │ │
   │     │  │    │      │ │ │ │ │ │ │ │            │ │ │ │ │
   │     └──┼────┼──────┘ │ │ │ │ │ │ │            │ │ │ │ │
   │        │    │        │ │ │ │ │ │ │            │ │ │ │ │
   │        └────┼────────┘ │ │ │ │ │ │            │ │ │ │ │
   │             │          │ │ │ │ │ │            │ │ │ │ │
   └─────────────┘          │ │ │ │ │ │            │ │ │ │ │
                            │ │ │ │ │ │            │ │ │ │ │
   LIGHT SENSOR (LDR)       │ │ │ │ │ │            │ │ │ │ │
   ┌─────────────┐          │ │ │ │ │ │            │ │ │ │ │
   │    ┌───┐    │          │ │ │ │ │ │            │ │ │ │ │
   │    │LDR│    │          │ │ │ │ │ │            │ │ │ │ │
   │    └───┘    │          │ │ │ │ │ │            │ │ │ │ │
   │     │ │     │          │ │ │ │ │ │            │ │ │ │ │
   │     │ └─────┼──────────┘ │ │ │ │ │            │ │ │ │ │
   │     │       │            │ │ │ │ │            │ │ │ │ │
   │     └───────┼────────────┘ │ │ │ │            │ │ │ │ │
   │             │              │ │ │ │            │ │ │ │ │
   │ [10kΩ]──────┼──────────────┘ │ │ │            │ │ │ │ │
   │             │                │ │ │            │ │ │ │ │
   └─────────────┘                │ │ │            │ │ │ │ │
                                  │ │ │            │ │ │ │ │
   CONTRAST POTENTIOMETER         │ │ │            │ │ │ │ │
   ┌─────────────┐                │ │ │            │ │ │ │ │
   │      ┌─┐    │                │ │ │            │ │ │ │ │
   │   1──┤ │─3  │                │ │ │            │ │ │ │ │
   │      │ │    │                │ │ │            │ │ │ │ │
   │      └─┘    │                │ │ │            │ │ │ │ │
   │       │     │                │ │ │            │ │ │ │ │
   │       2     │                │ │ │            │ │ │ │ │
   │       │     │                │ │ │            │ │ │ │ │
   │       └─────┼────────────────┘ │ │            │ │ │ │ │
   │             │                  │ │            │ │ │ │ │
   │   1─────────┼──────────────────┘ │            │ │ │ │ │
   │             │                    │            │ │ │ │ │
   │   3─────────┼────────────────────┘            │ │ │ │ │
   │             │                                 │ │ │ │ │
   └─────────────┘                                 │ │ │ │ │
                                                   │ │ │ │ │
   MODE BUTTON                                     │ │ │ │ │
   ┌─────────────┐                                 │ │ │ │ │
   │    ┌───┐    │                                 │ │ │ │ │
   │    │BTN│    │                                 │ │ │ │ │
   │    └───┘    │                                 │ │ │ │ │
   │     │ │     │                                 │ │ │ │ │
   │     │ └─────┼─────────────────────────────────┘ │ │ │ │
   │     │       │                                   │ │ │ │
   │     └───────┼───────────────────────────────────┘ │ │ │
   │             │                                     │ │ │
   │ [10kΩ]──────┼─────────────────────────────────────┘ │ │
   │             │                                       │ │
   └─────────────┘                                       │ │
                                                         │ │
   STATUS LED                                            │ │
   ┌─────────────┐                                       │ │
   │             │                                       │ │
   │ ●─[220Ω]────┼───────────────────────────────────────┘ │
   │             │                                         │
   │ ●─[LED]─────┼─────────────────────────────────────────┘
   │             │
   └─────────────┘
```

---

## 📊 **Data Logger Programming**

### **Main Program Structure:**
```cpp
#include <LiquidCrystal.h>
#include <EEPROM.h>

// Pin definitions
#define TEMP_PIN A0
#define LIGHT_PIN A1
#define BUTTON_PIN 7
#define LED_PIN 13

// LCD initialization
LiquidCrystal lcd(2, 12, 3, 4, 5, 11);

// Data structures
struct SensorData {
    float temperature;
    int lightLevel;
    unsigned long timestamp;
};

// Global variables
SensorData currentData;
SensorData dataLog[100];  // Store 100 readings
int dataIndex = 0;
int displayMode = 0;
unsigned long lastReading = 0;
unsigned long lastButton = 0;

void setup() {
    Serial.begin(9600);
    lcd.begin(16, 2);
    
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    
    // Initialize display
    lcd.print("Data Logger");
    lcd.setCursor(0, 1);
    lcd.print("Starting...");
    delay(2000);
    
    // Load saved data from EEPROM
    loadDataFromEEPROM();
    
    lcd.clear();
    Serial.println("Data Logger Ready");
}

void loop() {
    // Read sensors every 5 seconds
    if (millis() - lastReading > 5000) {
        readSensors();
        storeData();
        lastReading = millis();
        
        // Blink LED to show activity
        digitalWrite(LED_PIN, HIGH);
        delay(100);
        digitalWrite(LED_PIN, LOW);
    }
    
    // Check for button press
    if (digitalRead(BUTTON_PIN) == LOW && millis() - lastButton > 500) {
        displayMode = (displayMode + 1) % 4;
        lastButton = millis();
    }
    
    // Update display
    updateDisplay();
    
    delay(100);
}
```

### **Sensor Reading Functions:**
```cpp
void readSensors() {
    // Read temperature from TMP36
    int tempReading = analogRead(TEMP_PIN);
    float voltage = (tempReading * 5.0) / 1024.0;
    currentData.temperature = (voltage - 0.5) * 100;
    
    // Read light level from LDR
    int lightReading = analogRead(LIGHT_PIN);
    currentData.lightLevel = map(lightReading, 0, 1023, 0, 100);
    
    // Store timestamp
    currentData.timestamp = millis();
    
    // Debug output
    Serial.print("Temperature: ");
    Serial.print(currentData.temperature);
    Serial.print("°C, Light: ");
    Serial.print(currentData.lightLevel);
    Serial.println("%");
}

void storeData() {
    // Store current reading in circular buffer
    dataLog[dataIndex] = currentData;
    dataIndex = (dataIndex + 1) % 100;
    
    // Save to EEPROM every 10 readings
    static int saveCounter = 0;
    if (++saveCounter >= 10) {
        saveDataToEEPROM();
        saveCounter = 0;
    }
}

void updateDisplay() {
    lcd.clear();
    
    switch (displayMode) {
        case 0:
            displayCurrent();
            break;
        case 1:
            displayStatistics();
            break;
        case 2:
            displayHistory();
            break;
        case 3:
            displaySystemInfo();
            break;
    }
}
```

### **Display Mode Functions:**
```cpp
void displayCurrent() {
    lcd.setCursor(0, 0);
    lcd.print("T:");
    lcd.print(currentData.temperature, 1);
    lcd.print("C L:");
    lcd.print(currentData.lightLevel);
    lcd.print("%");
    
    lcd.setCursor(0, 1);
    lcd.print("Status: Logging");
}

void displayStatistics() {
    float maxTemp = -999, minTemp = 999;
    int maxLight = 0, minLight = 100;
    
    // Calculate statistics
    for (int i = 0; i < 100; i++) {
        if (dataLog[i].temperature > maxTemp) maxTemp = dataLog[i].temperature;
        if (dataLog[i].temperature < minTemp) minTemp = dataLog[i].temperature;
        if (dataLog[i].lightLevel > maxLight) maxLight = dataLog[i].lightLevel;
        if (dataLog[i].lightLevel < minLight) minLight = dataLog[i].lightLevel;
    }
    
    lcd.setCursor(0, 0);
    lcd.print("Max:");
    lcd.print(maxTemp, 1);
    lcd.print("C ");
    lcd.print(maxLight);
    lcd.print("%");
    
    lcd.setCursor(0, 1);
    lcd.print("Min:");
    lcd.print(minTemp, 1);
    lcd.print("C ");
    lcd.print(minLight);
    lcd.print("%");
}

void displayHistory() {
    static int historyIndex = 0;
    
    lcd.setCursor(0, 0);
    lcd.print("Entry ");
    lcd.print(historyIndex + 1);
    lcd.print(":");
    
    lcd.setCursor(0, 1);
    if (historyIndex < 100) {
        lcd.print(dataLog[historyIndex].temperature, 1);
        lcd.print("C ");
        lcd.print(dataLog[historyIndex].lightLevel);
        lcd.print("%");
    } else {
        lcd.print("No data");
    }
    
    // Auto-advance through history
    static unsigned long lastAdvance = 0;
    if (millis() - lastAdvance > 2000) {
        historyIndex = (historyIndex + 1) % 100;
        lastAdvance = millis();
    }
}

void displaySystemInfo() {
    lcd.setCursor(0, 0);
    lcd.print("Uptime: ");
    unsigned long seconds = millis() / 1000;
    unsigned long minutes = seconds / 60;
    unsigned long hours = minutes / 60;
    
    lcd.print(hours);
    lcd.print("h ");
    lcd.print(minutes % 60);
    lcd.print("m");
    
    lcd.setCursor(0, 1);
    lcd.print("Samples: ");
    lcd.print(dataIndex);
}
```

### **EEPROM Data Storage:**
```cpp
void saveDataToEEPROM() {
    // Save current data to EEPROM
    int address = 0;
    
    // Save data index
    EEPROM.write(address++, dataIndex);
    
    // Save recent data (last 10 entries)
    for (int i = 0; i < 10; i++) {
        int idx = (dataIndex - 10 + i + 100) % 100;
        
        // Save temperature (as integer * 10)
        int tempInt = (int)(dataLog[idx].temperature * 10);
        EEPROM.write(address++, tempInt >> 8);
        EEPROM.write(address++, tempInt & 0xFF);
        
        // Save light level
        EEPROM.write(address++, dataLog[idx].lightLevel);
    }
}

void loadDataFromEEPROM() {
    int address = 0;
    
    // Load data index
    dataIndex = EEPROM.read(address++);
    
    // Load recent data
    for (int i = 0; i < 10; i++) {
        int idx = (dataIndex - 10 + i + 100) % 100;
        
        // Load temperature
        int tempHigh = EEPROM.read(address++);
        int tempLow = EEPROM.read(address++);
        int tempInt = (tempHigh << 8) | tempLow;
        dataLog[idx].temperature = tempInt / 10.0;
        
        // Load light level
        dataLog[idx].lightLevel = EEPROM.read(address++);
    }
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check all connections** - This is a complex circuit with many wires
2. **Verify sensor polarities** - TMP36 pinout is critical
3. **Test LCD contrast** - Adjust potentiometer for readable display
4. **Confirm button pull-up** - Should read HIGH when not pressed

### **System Test Program:**
```cpp
void systemTest() {
    Serial.println("=== DATA LOGGER SYSTEM TEST ===");
    
    // Test LCD
    lcd.clear();
    lcd.print("LCD Test");
    lcd.setCursor(0, 1);
    lcd.print("Display OK");
    delay(2000);
    
    // Test temperature sensor
    Serial.println("Testing temperature sensor...");
    for (int i = 0; i < 5; i++) {
        int reading = analogRead(TEMP_PIN);
        float voltage = (reading * 5.0) / 1024.0;
        float temp = (voltage - 0.5) * 100;
        
        Serial.print("TMP36 - ADC: ");
        Serial.print(reading);
        Serial.print(", Voltage: ");
        Serial.print(voltage);
        Serial.print("V, Temp: ");
        Serial.print(temp);
        Serial.println("°C");
        
        delay(1000);
    }
    
    // Test light sensor
    Serial.println("Testing light sensor...");
    for (int i = 0; i < 5; i++) {
        int reading = analogRead(LIGHT_PIN);
        int percentage = map(reading, 0, 1023, 0, 100);
        
        Serial.print("LDR - ADC: ");
        Serial.print(reading);
        Serial.print(", Light: ");
        Serial.print(percentage);
        Serial.println("%");
        
        delay(1000);
    }
    
    // Test button
    Serial.println("Testing button (press now)...");
    unsigned long testStart = millis();
    while (millis() - testStart < 5000) {
        if (digitalRead(BUTTON_PIN) == LOW) {
            Serial.println("Button pressed!");
            digitalWrite(LED_PIN, HIGH);
            delay(500);
            digitalWrite(LED_PIN, LOW);
            break;
        }
    }
    
    Serial.println("System test complete!");
}
```

### **Troubleshooting:**
- **No LCD display**: Check power, contrast, and data connections
- **Wrong temperature readings**: Verify TMP36 pinout and voltage
- **Light sensor not working**: Check LDR and pull-down resistor
- **Button not responding**: Confirm pull-up resistor and connections
- **Data not saving**: Check EEPROM functions and power stability

---

## 🎪 **Advanced Data Logger Features**

### **Data Analysis:**
```cpp
// Calculate trends
float calculateTrend(int sensorType, int samples) {
    if (samples > 100) samples = 100;
    
    float sum = 0;
    for (int i = 1; i < samples; i++) {
        int idx1 = (dataIndex - i + 100) % 100;
        int idx2 = (dataIndex - i - 1 + 100) % 100;
        
        if (sensorType == 0) {  // Temperature
            sum += dataLog[idx1].temperature - dataLog[idx2].temperature;
        } else {  // Light
            sum += dataLog[idx1].lightLevel - dataLog[idx2].lightLevel;
        }
    }
    
    return sum / (samples - 1);
}

// Alarm system
void checkAlarms() {
    // High temperature alarm
    if (currentData.temperature > 30.0) {
        lcd.setCursor(0, 1);
        lcd.print("TEMP ALARM!");
        
        // Flash LED
        for (int i = 0; i < 5; i++) {
            digitalWrite(LED_PIN, HIGH);
            delay(100);
            digitalWrite(LED_PIN, LOW);
            delay(100);
        }
    }
    
    // Low light alarm
    if (currentData.lightLevel < 10) {
        lcd.setCursor(0, 1);
        lcd.print("LOW LIGHT!");
    }
}
```

### **Data Export:**
```cpp
// Export data via Serial
void exportData() {
    Serial.println("=== DATA EXPORT ===");
    Serial.println("Index,Temperature,Light,Timestamp");
    
    for (int i = 0; i < 100; i++) {
        if (dataLog[i].timestamp > 0) {
            Serial.print(i);
            Serial.print(",");
            Serial.print(dataLog[i].temperature);
            Serial.print(",");
            Serial.print(dataLog[i].lightLevel);
            Serial.print(",");
            Serial.println(dataLog[i].timestamp);
        }
    }
    
    Serial.println("=== END EXPORT ===");
}
```

---

## 🎉 **Success! You've Built a Data Logger!**

**Congratulations, Data Scientist!** Your environmental monitoring system is now operational! You've learned data acquisition, storage, statistical analysis, and user interface design - essential skills for scientific instruments, industrial monitoring, and research applications!

### **Next Steps:**
- Add SD card storage for unlimited data
- Include wireless data transmission
- Add more sensors (humidity, pressure, etc.)
- Create web interface for remote monitoring

### **Real-World Applications:**
- **Environmental monitoring**: Weather stations and air quality
- **Industrial**: Process control and quality assurance
- **Research**: Scientific data collection and analysis
- **Agriculture**: Greenhouse monitoring and automation
- **Home automation**: Smart home environmental control

---

*Data is the foundation of understanding - collect it wisely! Keep building! 🚀*