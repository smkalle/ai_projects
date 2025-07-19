# 🐕 Program 14: Pet Feeder Timer Circuit Diagram

## 🎯 **PET CARE ENGINEER MISSION**
Build an automated pet feeding system that schedules meals, controls portions, and monitors feeding patterns!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **Servo Motor (SG90)** (1x) - for food dispensing
- **16x2 LCD Display** (1x) - for time and status
- **DS1307 RTC Module** (1x) - for accurate timekeeping
- **Push Buttons** (3x) - for menu navigation
- **Piezo Buzzer** (1x) - for feeding alerts
- **LED** (1x) - for status indication
- **10kΩ Resistors** (3x) - for button pull-ups
- **10kΩ Potentiometer** (1x) - for LCD contrast
- **220Ω Resistor** (1x) - for LED
- **Breadboard** (2x or 1 large)
- **Jumper Wires** (25x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Pet Feeder System
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │  D2-D5,D11  │────────────────┤ LCD Display     │
    │         D12 │────────────────┤ LCD Enable      │
    │             │                │                 │
    │         D9  │────────────────┤ Servo Motor     │
    │             │                │                 │
    │         D6  │────────────────┤ Menu Button     │
    │         D7  │────────────────┤ Select Button   │
    │         D8  │────────────────┤ Back Button     │
    │             │                │                 │
    │        D10  │────────────────┤ Buzzer          │
    │        D13  │────────────────┤ Status LED      │
    │             │                │                 │
    │    SDA/SCL  │────────────────┤ RTC Module      │
    │             │                │                 │
    │         5V  │────────────────┤ Power Rails     │
    │         GND │────────────────┤ Ground Rails    │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: LCD Display Setup**
16x2 LCD for displaying time, feeding schedule, and status:

```
LCD Pinout (Standard HD44780):
┌─────────────────────────────────┐
│ 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 │
│VSS VDD V0 RS EN D0 D1 D2 D3 D4 D5 D6 D7 A  K  │
└─────────────────────────────────┘

Connected pins:
1  (VSS) - Ground
2  (VDD) - Power (+5V)
3  (V0)  - Contrast (potentiometer)
4  (RS)  - Register Select (Arduino D2)
5  (EN)  - Enable (Arduino D12)
10 (D4)  - Data bit 4 (Arduino D3)
11 (D5)  - Data bit 5 (Arduino D4)
12 (D6)  - Data bit 6 (Arduino D5)
13 (D7)  - Data bit 7 (Arduino D11)
14 (A)   - Backlight Anode (+5V)
15 (K)   - Backlight Cathode (Ground)
```

### **Step 2: Breadboard Layout**
```
Main Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← LCD VSS
│  2  2  .  .  .  .  .  .  .  .  │ ← LCD VDD
│  3  3  .  .  .  .  .  .  .  .  │ ← LCD V0
│  4  4  .  .  .  .  .  .  .  .  │ ← LCD RS
│  5  5  .  .  .  .  .  .  .  .  │ ← LCD EN
│  6  6  .  .  .  .  .  .  .  .  │ ← LCD D4
│  7  7  .  .  .  .  .  .  .  .  │ ← LCD D5
│  8  8  .  .  .  .  .  .  .  .  │ ← LCD D6
│  9  9  .  .  .  .  .  .  .  .  │ ← LCD D7
│ 10 10  .  .  .  .  .  .  .  .  │ ← LCD A
│ 11 11  .  .  .  .  .  .  .  .  │ ← LCD K
│ 12 12  .  .  .  .  .  .  .  .  │
│ 13 13  .  .  .  .  .  .  .  .  │ ← Servo Signal
│ 14 14  .  .  .  .  .  .  .  .  │ ← Servo Power
│ 15 15  .  .  .  .  .  .  .  .  │ ← Servo Ground
└─────────────────────────────────┘

Secondary Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│ 16 16  .  .  .  .  .  .  .  .  │ ← RTC VCC
│ 17 17  .  .  .  .  .  .  .  .  │ ← RTC GND
│ 18 18  .  .  .  .  .  .  .  .  │ ← RTC SDA
│ 19 19  .  .  .  .  .  .  .  .  │ ← RTC SCL
│ 20 20  .  .  .  .  .  .  .  .  │
│ 21 21  .  .  .  .  .  .  .  .  │ ← Menu Button
│ 22 22  .  .  .  .  .  .  .  .  │ ← Select Button
│ 23 23  .  .  .  .  .  .  .  .  │ ← Back Button
│ 24 24  .  .  .  .  .  .  .  .  │
│ 25 25  .  .  .  .  .  .  .  .  │ ← Buzzer
│ 26 26  .  .  .  .  .  .  .  .  │ ← Status LED
│ 27 27  .  .  .  .  .  .  .  .  │
│ 28 28  .  .  .  .  .  .  .  .  │ ← Contrast Pot
│ 29 29  .  .  .  .  .  .  .  .  │
│ 30 30  .  .  .  .  .  .  .  .  │
└─────────────────────────────────┘
```

### **Step 3: Install LCD Display**
```
LCD Installation:
┌─────────────────────────────────┐
│  1  1  G  .  .  .  .  .  .  .  │ ← VSS to GND
│  2  2  V  .  .  .  .  .  .  .  │ ← VDD to 5V
│  3  3  C  .  .  .  .  .  .  .  │ ← V0 to contrast pot
│  4  4  R  .  .  .  .  .  .  .  │ ← RS to D2
│  5  5  E  .  .  .  .  .  .  .  │ ← EN to D12
│  6  6  D4 .  .  .  .  .  .  .  │ ← D4 to D3
│  7  7  D5 .  .  .  .  .  .  .  │ ← D5 to D4
│  8  8  D6 .  .  .  .  .  .  .  │ ← D6 to D5
│  9  9  D7 .  .  .  .  .  .  .  │ ← D7 to D11
│ 10 10  A  .  .  .  .  .  .  .  │ ← Backlight to 5V
│ 11 11  K  .  .  .  .  .  .  .  │ ← Backlight to GND
└─────────────────────────────────┘
```

### **Step 4: Install Servo Motor**
SG90 servo for food dispensing mechanism:

```
Servo Installation:
┌─────────────────────────────────┐
│ 13 13  S  .  .  .  .  .  .  .  │ ← Servo Signal (Orange)
│ 14 14  V  .  .  .  .  .  .  .  │ ← Servo VCC (Red)
│ 15 15  G  .  .  .  .  .  .  .  │ ← Servo GND (Brown)
│ 16 16  .  ●  .  .  .  .  .  .  │ ← Signal to D9
│ 17 17  .  ●  .  .  .  .  .  .  │ ← VCC to 5V
│ 18 18  .  ●  .  .  .  .  .  .  │ ← GND to Ground
└─────────────────────────────────┘
```

### **Step 5: Install RTC Module**
DS1307 Real-Time Clock for accurate timekeeping:

```
RTC Installation:
┌─────────────────────────────────┐
│ 19 19  RV .  .  .  .  .  .  .  │ ← RTC VCC
│ 20 20  RG .  .  .  .  .  .  .  │ ← RTC GND
│ 21 21  RS .  .  .  .  .  .  .  │ ← RTC SDA
│ 22 22  RC .  .  .  .  .  .  .  │ ← RTC SCL
│ 23 23  .  ●  .  .  .  .  .  .  │ ← VCC to 5V
│ 24 24  .  ●  .  .  .  .  .  .  │ ← GND to Ground
│ 25 25  .  ●  .  .  .  .  .  .  │ ← SDA to A4
│ 26 26  .  ●  .  .  .  .  .  .  │ ← SCL to A5
└─────────────────────────────────┘
```

### **Step 6: Install Control Buttons**
Three buttons for menu navigation:

```
Button Installation:
┌─────────────────────────────────┐
│ 27 27  M1 MR .  .  .  .  .  .  │ ← Menu Button + resistor
│ 28 28  M2 ●  .  .  .  .  .  .  │ ← Menu Button to GND
│ 29 29  S1 SR .  .  .  .  .  .  │ ← Select Button + resistor
│ 30 30  S2 ●  .  .  .  .  .  .  │ ← Select Button to GND
│ 31 31  B1 BR .  .  .  .  .  .  │ ← Back Button + resistor
│ 32 32  B2 ●  .  .  .  .  .  .  │ ← Back Button to GND
│ 33 33  .  MR─●  .  .  .  .  .  │ ← Menu resistor to 5V
│ 34 34  .  SR─●  .  .  .  .  .  │ ← Select resistor to 5V
│ 35 35  .  BR─●  .  .  .  .  .  │ ← Back resistor to 5V
│ 36 36  .  ●  .  .  .  .  .  .  │ ← Menu Button to D6
│ 37 37  .  ●  .  .  .  .  .  .  │ ← Select Button to D7
│ 38 38  .  ●  .  .  .  .  .  .  │ ← Back Button to D8
└─────────────────────────────────┘
```

### **Step 7: Install Buzzer and Status LED**
Audio alerts and visual status indication:

```
Buzzer and LED Installation:
┌─────────────────────────────────┐
│ 39 39  Z+ .  .  .  .  .  .  .  │ ← Buzzer positive
│ 40 40  Z- .  .  .  .  .  .  .  │ ← Buzzer negative
│ 41 41  L+ LR .  .  .  .  .  .  │ ← LED anode + resistor
│ 42 42  L- .  .  .  .  .  .  .  │ ← LED cathode
│ 43 43  .  ●  .  .  .  .  .  .  │ ← Buzzer positive to D10
│ 44 44  .  ●  .  .  .  .  .  .  │ ← Buzzer negative to GND
│ 45 45  .  LR─●  .  .  .  .  .  │ ← LED resistor to D13
│ 46 46  .  ●  .  .  .  .  .  .  │ ← LED cathode to GND
└─────────────────────────────────┘
```

### **Step 8: Install Contrast Potentiometer**
10kΩ potentiometer for LCD contrast adjustment:

```
Potentiometer Installation:
┌─────────────────────────────────┐
│ 47 47  P1 .  .  .  .  .  .  .  │ ← Potentiometer pin 1
│ 48 48  P2 .  .  .  .  .  .  .  │ ← Potentiometer pin 2 (wiper)
│ 49 49  P3 .  .  .  .  .  .  .  │ ← Potentiometer pin 3
│ 50 50  .  ●  .  .  .  .  .  .  │ ← Pin 1 to 5V
│ 51 51  .  ●  .  .  .  .  .  .  │ ← Wiper to LCD V0
│ 52 52  .  ●  .  .  .  .  .  .  │ ← Pin 3 to GND
└─────────────────────────────────┘
```

### **Step 9: Connect All Wires**
```
Final Circuit Summary:
┌─────────────────────────────────┐
│ LCD Display:                    │
│ - VSS to GND                    │
│ - VDD to 5V                     │
│ - V0 to Potentiometer wiper     │
│ - RS to D2                      │
│ - EN to D12                     │
│ - D4 to D3                      │
│ - D5 to D4                      │
│ - D6 to D5                      │
│ - D7 to D11                     │
│ - A to 5V                       │
│ - K to GND                      │
│                                 │
│ Servo Motor:                    │
│ - Signal to D9                  │
│ - VCC to 5V                     │
│ - GND to Ground                 │
│                                 │
│ RTC Module:                     │
│ - VCC to 5V                     │
│ - GND to Ground                 │
│ - SDA to A4                     │
│ - SCL to A5                     │
│                                 │
│ Control Buttons:                │
│ - Menu Button to D6 (pull-up)   │
│ - Select Button to D7 (pull-up) │
│ - Back Button to D8 (pull-up)   │
│                                 │
│ Audio/Visual:                   │
│ - Buzzer to D10                 │
│ - Status LED to D13             │
│                                 │
│ Power Distribution:             │
│ - 5V to all VCC pins            │
│ - GND to all ground pins        │
└─────────────────────────────────┘
```

---

## ⚡ **Circuit Explanation**

### **How Pet Feeder Works:**
1. **RTC module** maintains accurate time even when powered off
2. **LCD display** shows current time and feeding schedule
3. **Servo motor** controls food dispensing mechanism
4. **Buttons** allow setting feeding times and portions
5. **Buzzer** alerts when feeding time arrives
6. **Status LED** indicates system status

### **Real-Time Clock (DS1307):**
```
RTC Features:
- Battery backup for timekeeping
- I2C communication (SDA/SCL)
- Accurate timekeeping ±1 minute/month
- Automatic leap year compensation
- 56-byte battery-backed RAM
```

### **Servo Control for Food Dispensing:**
```
Servo Positions:
0°   - Closed (no food)
90°  - Small portion
180° - Large portion

Dispensing Sequence:
1. Move to portion position
2. Wait for food to fall
3. Return to closed position
4. Log feeding event
```

### **I2C Communication:**
```
I2C Pins:
- SDA (Serial Data) - A4 on Arduino Uno
- SCL (Serial Clock) - A5 on Arduino Uno
- Pull-up resistors usually built into modules
- Multiple devices can share same I2C bus
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
   │  D2 ●────────┼─── LCD RS ──────────────┐
   │  D3 ●────────┼─── LCD D4 ──────────────┼─┐
   │  D4 ●────────┼─── LCD D5 ──────────────┼─┼─┐
   │  D5 ●────────┼─── LCD D6 ──────────────┼─┼─┼─┐
   │  D6 ●────────┼─── MENU BUTTON ─────────┼─┼─┼─┼─┐
   │  D7 ●────────┼─── SELECT BUTTON ───────┼─┼─┼─┼─┼─┐
   │  D8 ●────────┼─── BACK BUTTON ─────────┼─┼─┼─┼─┼─┼─┐
   │  D9 ●────────┼─── SERVO SIGNAL ────────┼─┼─┼─┼─┼─┼─┼─┐
   │ D10 ●────────┼─── BUZZER ──────────────┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D11 ●────────┼─── LCD D7 ──────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D12 ●────────┼─── LCD EN ──────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D13 ●────────┼─── STATUS LED ──────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                         │ │ │ │ │ │ │ │ │ │ │ │
   │  A4 ●────────┼─── RTC SDA ────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │  A5 ●────────┼─── RTC SCL ────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                         │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  5V ●────────┼─── POWER ──────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ GND ●────────┼─── GROUND ─────────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                         │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   └─────────────┘                         │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
                                           │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   16x2 LCD DISPLAY                        │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   ┌─────────────────────────────────┐     │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  12:30 PM Feed Time │           │     │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  Next: 6:00 PM     │           │     │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   └─────────────────────────────────┘     │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16│ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │● ● ● ● ● ● ● ● ● ●  ●  ●  ●  ●  ●  ●│ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │└─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──┼──┼──┘ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  │ │ │ │ │ │ │ │ │  │  │  │  │  │    │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──┼──┼──┘ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │    │ │ │ │ │ │ │ │ │  │  │  │  │  │    │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │    └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──┼────┘ │ │ │ │ │ │ │ │ │ │ │ │ │
   │      │ │ │ │ │ │ │ │ │  │  │  │  │      │ │ │ │ │ │ │ │ │ │ │ │ │
   │      └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼──┼──────┘ │ │ │ │ │ │ │ │ │ │ │ │
   │        │ │ │ │ │ │ │ │ │  │  │  │        │ │ │ │ │ │ │ │ │ │ │ │
   │        └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──┼────────┘ │ │ │ │ │ │ │ │ │ │ │
   │          │ │ │ │ │ │ │ │ │  │  │          │ │ │ │ │ │ │ │ │ │ │
   │          └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │ │ │ │ │ │
   │            │ │ │ │ │ │ │ │ │  │            │ │ │ │ │ │ │ │ │ │
   │            └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │ │ │ │ │
   │              │ │ │ │ │ │ │ │ │  │            │ │ │ │ │ │ │ │ │
   │              └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │ │ │ │
   │                │ │ │ │ │ │ │ │ │  │            │ │ │ │ │ │ │ │
   │                └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │ │ │
   │                  │ │ │ │ │ │ │ │ │  │            │ │ │ │ │ │ │
   │                  └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │ │
   │                    │ │ │ │ │ │ │ │ │  │            │ │ │ │ │ │
   │                    └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │ │
   │                      │ │ │ │ │ │ │ │ │  │            │ │ │ │ │
   │                      └─┼─┼─┼─┼─┼─┼─┼─┼─┼──┼──────────┘ │ │ │ │
   │                        │ │ │ │ │ │ │ │ │  │            │ │ │ │
   └────────────────────────┘ │ │ │ │ │ │ │ │ │            │ │ │ │
                              │ │ │ │ │ │ │ │ │            │ │ │ │
   SERVO MOTOR                │ │ │ │ │ │ │ │ │            │ │ │ │
   ┌─────────────┐            │ │ │ │ │ │ │ │ │            │ │ │ │
   │    SG90     │            │ │ │ │ │ │ │ │ │            │ │ │ │
   │  ┌─────────┐│            │ │ │ │ │ │ │ │ │            │ │ │ │
   │  │ SHAFT   ││            │ │ │ │ │ │ │ │ │            │ │ │ │
   │  └─────────┘│            │ │ │ │ │ │ │ │ │            │ │ │ │
   │  O  R  B    │            │ │ │ │ │ │ │ │ │            │ │ │ │
   │  │  │  │    │            │ │ │ │ │ │ │ │ │            │ │ │ │
   │  └──┼──┼────┼────────────┘ │ │ │ │ │ │ │ │            │ │ │ │
   │     │  │    │              │ │ │ │ │ │ │ │            │ │ │ │
   │     └──┼────┼──────────────┘ │ │ │ │ │ │ │            │ │ │ │
   │        │    │                │ │ │ │ │ │ │            │ │ │ │
   │        └────┼────────────────┘ │ │ │ │ │ │            │ │ │ │
   │             │                  │ │ │ │ │ │            │ │ │ │
   └─────────────┘                  │ │ │ │ │ │            │ │ │ │
                                    │ │ │ │ │ │            │ │ │ │
   DS1307 RTC MODULE                │ │ │ │ │ │            │ │ │ │
   ┌─────────────┐                  │ │ │ │ │ │            │ │ │ │
   │  ┌─────────┐│                  │ │ │ │ │ │            │ │ │ │
   │  │ DS1307  ││                  │ │ │ │ │ │            │ │ │ │
   │  │ [BATT]  ││                  │ │ │ │ │ │            │ │ │ │
   │  └─────────┘│                  │ │ │ │ │ │            │ │ │ │
   │VCC GND SDA SCL│                │ │ │ │ │ │            │ │ │ │
   │ ●   ●   ●   ●│                │ │ │ │ │ │            │ │ │ │
   │ └───┼───┼───┼─┼────────────────┘ │ │ │ │ │            │ │ │ │
   │     │   │   │ │                  │ │ │ │ │            │ │ │ │
   │     └───┼───┼─┼──────────────────┘ │ │ │ │            │ │ │ │
   │         │   │ │                    │ │ │ │            │ │ │ │
   │         └───┼─┼────────────────────┘ │ │ │            │ │ │ │
   │             │ │                      │ │ │            │ │ │ │
   │             └─┼──────────────────────┘ │ │            │ │ │ │
   │               │                        │ │            │ │ │ │
   └───────────────┘                        │ │            │ │ │ │
                                            │ │            │ │ │ │
   CONTROL BUTTONS                          │ │            │ │ │ │
   ┌─────────────┐                          │ │            │ │ │ │
   │  ┌─────────┐│                          │ │            │ │ │ │
   │  │  MENU   ││                          │ │            │ │ │ │
   │  └─────────┘│                          │ │            │ │ │ │
   │      │      │                          │ │            │ │ │ │
   │      └──────┼──────────────────────────┘ │            │ │ │ │
   │             │                            │            │ │ │ │
   │  ┌─────────┐│                            │            │ │ │ │
   │  │ SELECT  ││                            │            │ │ │ │
   │  └─────────┘│                            │            │ │ │ │
   │      │      │                            │            │ │ │ │
   │      └──────┼────────────────────────────┘            │ │ │ │
   │             │                                         │ │ │ │
   │  ┌─────────┐│                                         │ │ │ │
   │  │  BACK   ││                                         │ │ │ │
   │  └─────────┘│                                         │ │ │ │
   │      │      │                                         │ │ │ │
   │      └──────┼─────────────────────────────────────────┘ │ │ │
   │             │                                           │ │ │
   │ [10kΩ]──────┼───────────────────────────────────────────┘ │ │
   │ [10kΩ]──────┼─────────────────────────────────────────────┘ │
   │ [10kΩ]──────┼───────────────────────────────────────────────┘
   │             │
   └─────────────┘
```

---

## 🕐 **Pet Feeder Programming**

### **Main Program Structure:**
```cpp
#include <LiquidCrystal.h>
#include <Wire.h>
#include <RTClib.h>
#include <Servo.h>
#include <EEPROM.h>

// Pin definitions
#define SERVO_PIN 9
#define BUZZER_PIN 10
#define LED_PIN 13
#define MENU_BUTTON 6
#define SELECT_BUTTON 7
#define BACK_BUTTON 8

// LCD initialization
LiquidCrystal lcd(2, 12, 3, 4, 5, 11);

// RTC and Servo initialization
RTC_DS1307 rtc;
Servo feedServo;

// Menu system
enum MenuState {
    MAIN_SCREEN,
    SCHEDULE_MENU,
    PORTION_MENU,
    HISTORY_MENU,
    SETTINGS_MENU
};

// Feeding schedule structure
struct FeedingTime {
    int hour;
    int minute;
    int portion;  // 1=small, 2=medium, 3=large
    bool enabled;
};

// Global variables
MenuState currentMenu = MAIN_SCREEN;
FeedingTime schedule[6];  // Up to 6 feeding times
int scheduleCount = 0;
int selectedItem = 0;
bool feedingInProgress = false;
unsigned long lastButtonPress = 0;

// Feeding history
struct FeedingRecord {
    DateTime timestamp;
    int portion;
    bool successful;
};

FeedingRecord feedingHistory[50];
int historyIndex = 0;

void setup() {
    Serial.begin(9600);
    
    // Initialize components
    lcd.begin(16, 2);
    feedServo.attach(SERVO_PIN);
    
    // Initialize RTC
    if (!rtc.begin()) {
        Serial.println("RTC not found");
        while (1);
    }
    
    if (!rtc.isrunning()) {
        Serial.println("RTC not running, setting time");
        rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    }
    
    // Initialize pins
    pinMode(MENU_BUTTON, INPUT_PULLUP);
    pinMode(SELECT_BUTTON, INPUT_PULLUP);
    pinMode(BACK_BUTTON, INPUT_PULLUP);
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
    
    // Set servo to closed position
    feedServo.write(0);
    
    // Load schedule from EEPROM
    loadSchedule();
    
    // Welcome message
    lcd.clear();
    lcd.print("Pet Feeder");
    lcd.setCursor(0, 1);
    lcd.print("Starting...");
    delay(2000);
    
    Serial.println("Pet Feeder Ready!");
}

void loop() {
    // Check for feeding times
    checkFeedingTime();
    
    // Handle button presses
    handleButtons();
    
    // Update display
    updateDisplay();
    
    // Check for feeding completion
    if (feedingInProgress) {
        handleFeeding();
    }
    
    delay(100);
}
```

### **Time and Scheduling Functions:**
```cpp
void checkFeedingTime() {
    DateTime now = rtc.now();
    
    for (int i = 0; i < scheduleCount; i++) {
        if (schedule[i].enabled && 
            schedule[i].hour == now.hour() && 
            schedule[i].minute == now.minute() &&
            now.second() == 0) {  // Only trigger once per minute
            
            startFeeding(schedule[i].portion);
            break;
        }
    }
}

void startFeeding(int portion) {
    feedingInProgress = true;
    digitalWrite(LED_PIN, HIGH);
    
    // Alert sound
    for (int i = 0; i < 3; i++) {
        tone(BUZZER_PIN, 1000, 200);
        delay(300);
    }
    
    // Display feeding message
    lcd.clear();
    lcd.print("Feeding Time!");
    lcd.setCursor(0, 1);
    lcd.print("Portion: ");
    
    switch (portion) {
        case 1: lcd.print("Small"); break;
        case 2: lcd.print("Medium"); break;
        case 3: lcd.print("Large"); break;
    }
    
    // Operate servo
    dispensePortion(portion);
    
    // Log feeding
    logFeeding(portion, true);
    
    Serial.print("Fed pet at ");
    Serial.print(rtc.now().hour());
    Serial.print(":");
    Serial.print(rtc.now().minute());
    Serial.print(" - Portion: ");
    Serial.println(portion);
    
    feedingInProgress = false;
    digitalWrite(LED_PIN, LOW);
}

void dispensePortion(int portion) {
    int angle = 0;
    int dispenseDuration = 0;
    
    switch (portion) {
        case 1: angle = 45; dispenseDuration = 1000; break;  // Small
        case 2: angle = 90; dispenseDuration = 2000; break;  // Medium
        case 3: angle = 135; dispenseDuration = 3000; break; // Large
    }
    
    // Open dispenser
    feedServo.write(angle);
    delay(dispenseDuration);
    
    // Close dispenser
    feedServo.write(0);
    delay(500);
}

void logFeeding(int portion, bool successful) {
    feedingHistory[historyIndex].timestamp = rtc.now();
    feedingHistory[historyIndex].portion = portion;
    feedingHistory[historyIndex].successful = successful;
    
    historyIndex = (historyIndex + 1) % 50;
    
    // Save to EEPROM
    saveFeedingHistory();
}
```

### **Menu System:**
```cpp
void handleButtons() {
    if (digitalRead(MENU_BUTTON) == LOW && millis() - lastButtonPress > 300) {
        navigateMenu();
        lastButtonPress = millis();
    }
    
    if (digitalRead(SELECT_BUTTON) == LOW && millis() - lastButtonPress > 300) {
        selectMenuItem();
        lastButtonPress = millis();
    }
    
    if (digitalRead(BACK_BUTTON) == LOW && millis() - lastButtonPress > 300) {
        backButton();
        lastButtonPress = millis();
    }
}

void navigateMenu() {
    switch (currentMenu) {
        case MAIN_SCREEN:
            currentMenu = SCHEDULE_MENU;
            selectedItem = 0;
            break;
            
        case SCHEDULE_MENU:
            selectedItem = (selectedItem + 1) % (scheduleCount + 1);
            break;
            
        case PORTION_MENU:
            selectedItem = (selectedItem + 1) % 3;
            break;
            
        case HISTORY_MENU:
            selectedItem = (selectedItem + 1) % min(historyIndex, 10);
            break;
            
        case SETTINGS_MENU:
            selectedItem = (selectedItem + 1) % 3;
            break;
    }
}

void selectMenuItem() {
    switch (currentMenu) {
        case MAIN_SCREEN:
            // Manual feeding
            manualFeed();
            break;
            
        case SCHEDULE_MENU:
            if (selectedItem == scheduleCount) {
                // Add new feeding time
                addFeedingTime();
            } else {
                // Edit existing feeding time
                editFeedingTime(selectedItem);
            }
            break;
            
        case PORTION_MENU:
            // Set portion size
            setPortionSize(selectedItem + 1);
            break;
            
        case HISTORY_MENU:
            // Show feeding details
            showFeedingDetails(selectedItem);
            break;
            
        case SETTINGS_MENU:
            handleSettings(selectedItem);
            break;
    }
}

void updateDisplay() {
    lcd.clear();
    
    switch (currentMenu) {
        case MAIN_SCREEN:
            displayMainScreen();
            break;
            
        case SCHEDULE_MENU:
            displayScheduleMenu();
            break;
            
        case PORTION_MENU:
            displayPortionMenu();
            break;
            
        case HISTORY_MENU:
            displayHistoryMenu();
            break;
            
        case SETTINGS_MENU:
            displaySettingsMenu();
            break;
    }
}

void displayMainScreen() {
    DateTime now = rtc.now();
    
    // Display current time
    lcd.setCursor(0, 0);
    if (now.hour() < 10) lcd.print("0");
    lcd.print(now.hour());
    lcd.print(":");
    if (now.minute() < 10) lcd.print("0");
    lcd.print(now.minute());
    lcd.print(":");
    if (now.second() < 10) lcd.print("0");
    lcd.print(now.second());
    
    // Display next feeding time
    lcd.setCursor(0, 1);
    lcd.print("Next: ");
    
    DateTime nextFeed = getNextFeedingTime();
    if (nextFeed.hour() != 255) {
        if (nextFeed.hour() < 10) lcd.print("0");
        lcd.print(nextFeed.hour());
        lcd.print(":");
        if (nextFeed.minute() < 10) lcd.print("0");
        lcd.print(nextFeed.minute());
    } else {
        lcd.print("None");
    }
}

DateTime getNextFeedingTime() {
    DateTime now = rtc.now();
    DateTime next = DateTime(2099, 1, 1, 0, 0, 0);  // Far future
    
    for (int i = 0; i < scheduleCount; i++) {
        if (schedule[i].enabled) {
            DateTime feedTime = DateTime(now.year(), now.month(), now.day(), 
                                       schedule[i].hour, schedule[i].minute, 0);
            
            // If feeding time has passed today, check tomorrow
            if (feedTime < now) {
                feedTime = DateTime(now.year(), now.month(), now.day() + 1, 
                                  schedule[i].hour, schedule[i].minute, 0);
            }
            
            if (feedTime < next) {
                next = feedTime;
            }
        }
    }
    
    return next;
}
```

### **Schedule Management:**
```cpp
void addFeedingTime() {
    if (scheduleCount < 6) {
        schedule[scheduleCount].hour = 12;
        schedule[scheduleCount].minute = 0;
        schedule[scheduleCount].portion = 2;
        schedule[scheduleCount].enabled = true;
        scheduleCount++;
        
        saveSchedule();
        
        lcd.clear();
        lcd.print("Feeding Added");
        delay(1000);
    } else {
        lcd.clear();
        lcd.print("Max 6 Feedings");
        delay(1000);
    }
}

void editFeedingTime(int index) {
    // Simple time editing (increment by 30 minutes)
    schedule[index].minute += 30;
    if (schedule[index].minute >= 60) {
        schedule[index].minute = 0;
        schedule[index].hour++;
        if (schedule[index].hour >= 24) {
            schedule[index].hour = 0;
        }
    }
    
    saveSchedule();
    
    lcd.clear();
    lcd.print("Time Updated");
    delay(1000);
}

void manualFeed() {
    lcd.clear();
    lcd.print("Manual Feed");
    lcd.setCursor(0, 1);
    lcd.print("Dispensing...");
    
    startFeeding(2);  // Medium portion
    
    delay(1000);
}

void saveSchedule() {
    for (int i = 0; i < 6; i++) {
        EEPROM.write(i * 4, schedule[i].hour);
        EEPROM.write(i * 4 + 1, schedule[i].minute);
        EEPROM.write(i * 4 + 2, schedule[i].portion);
        EEPROM.write(i * 4 + 3, schedule[i].enabled ? 1 : 0);
    }
    EEPROM.write(24, scheduleCount);
}

void loadSchedule() {
    scheduleCount = EEPROM.read(24);
    if (scheduleCount > 6) scheduleCount = 0;
    
    for (int i = 0; i < scheduleCount; i++) {
        schedule[i].hour = EEPROM.read(i * 4);
        schedule[i].minute = EEPROM.read(i * 4 + 1);
        schedule[i].portion = EEPROM.read(i * 4 + 2);
        schedule[i].enabled = EEPROM.read(i * 4 + 3) == 1;
    }
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check all connections** - This is a complex circuit with many components
2. **Verify RTC module** - Ensure I2C connections (SDA/SCL) are correct
3. **Test servo motor** - Check power and signal connections
4. **Confirm LCD display** - Verify all data and control connections

### **Component Test Program:**
```cpp
void componentTest() {
    Serial.println("=== PET FEEDER COMPONENT TEST ===");
    
    // Test LCD
    lcd.clear();
    lcd.print("LCD Test");
    delay(1000);
    
    // Test RTC
    DateTime now = rtc.now();
    Serial.print("RTC Time: ");
    Serial.print(now.hour());
    Serial.print(":");
    Serial.print(now.minute());
    Serial.print(":");
    Serial.println(now.second());
    
    // Test servo
    Serial.println("Testing servo...");
    feedServo.write(0);
    delay(1000);
    feedServo.write(90);
    delay(1000);
    feedServo.write(0);
    delay(1000);
    
    // Test buttons
    Serial.println("Testing buttons (press each)...");
    while (true) {
        if (digitalRead(MENU_BUTTON) == LOW) {
            Serial.println("Menu button pressed");
            break;
        }
        if (digitalRead(SELECT_BUTTON) == LOW) {
            Serial.println("Select button pressed");
            break;
        }
        if (digitalRead(BACK_BUTTON) == LOW) {
            Serial.println("Back button pressed");
            break;
        }
    }
    
    // Test buzzer
    Serial.println("Testing buzzer...");
    tone(BUZZER_PIN, 1000, 500);
    delay(1000);
    
    // Test LED
    Serial.println("Testing LED...");
    digitalWrite(LED_PIN, HIGH);
    delay(1000);
    digitalWrite(LED_PIN, LOW);
    
    Serial.println("Component test complete!");
}
```

### **Troubleshooting:**
- **LCD not working**: Check power, contrast, and data connections
- **RTC not keeping time**: Verify I2C connections and battery
- **Servo not moving**: Check power supply and signal connection
- **Buttons not responding**: Confirm pull-up resistors and connections
- **No sound**: Verify buzzer polarity and connection

---

## 🎪 **Advanced Pet Feeder Features**

### **Smart Feeding Algorithm:**
```cpp
// Adaptive feeding based on consumption patterns
struct FeedingStats {
    int totalFeedings;
    int missedFeedings;
    float averageConsumption;
    unsigned long lastActivity;
};

FeedingStats petStats;

void adaptiveFeedingCheck() {
    // Check if pet ate previous meal (sensor or manual confirmation)
    if (checkFoodBowl()) {
        petStats.totalFeedings++;
        petStats.averageConsumption = calculateConsumption();
        petStats.lastActivity = millis();
    } else {
        petStats.missedFeedings++;
        
        // Reduce portion size if consistently not eating
        if (petStats.missedFeedings > 3) {
            adjustPortionSizes(0.8);  // Reduce by 20%
        }
    }
}

// Weight-based portion control
void adjustPortionSizes(float factor) {
    for (int i = 0; i < scheduleCount; i++) {
        if (schedule[i].portion > 1 && factor < 1.0) {
            schedule[i].portion = max(1, (int)(schedule[i].portion * factor));
        }
    }
    saveSchedule();
}
```

### **Remote Monitoring:**
```cpp
// WiFi connectivity for remote monitoring
void sendFeedingNotification() {
    String message = "Pet fed at ";
    DateTime now = rtc.now();
    message += now.hour();
    message += ":";
    message += now.minute();
    message += " - Portion: ";
    message += getCurrentPortion();
    
    // Send to phone app or web service
    Serial.println(message);
    
    // Could integrate with ESP8266 for WiFi
    // or Bluetooth module for local communication
}

// Emergency feeding override
void emergencyFeed() {
    lcd.clear();
    lcd.print("Emergency Feed");
    lcd.setCursor(0, 1);
    lcd.print("Override Active");
    
    // Play urgent sound
    for (int i = 0; i < 5; i++) {
        tone(BUZZER_PIN, 2000, 100);
        delay(150);
    }
    
    startFeeding(1);  // Small emergency portion
}
```

---

## 🎉 **Success! You've Built a Pet Feeder Timer!**

**Congratulations, Pet Care Engineer!** Your automated pet feeding system is now operational! You've learned real-time systems, scheduling algorithms, servo control, and user interface design - essential skills for home automation, IoT devices, and care systems!

### **Next Steps:**
- Add food level sensors for automatic refilling alerts
- Integrate camera for pet monitoring
- Add WiFi connectivity for remote control
- Include multiple pet support with RFID identification

### **Real-World Applications:**
- **Home automation**: Automated care systems
- **Healthcare**: Medication dispensing systems
- **Agriculture**: Automated feeding for livestock
- **Industrial**: Scheduled material dispensing
- **Elder care**: Automated reminder and dispensing systems

---

*Caring for our companions through technology - keep innovating! 🚀*