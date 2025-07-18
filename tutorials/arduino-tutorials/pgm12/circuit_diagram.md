# 🎲 Program 12: Digital Dice Circuit Diagram

## 🎯 **PROBABILITY ENGINEER MISSION**
Build an electronic dice system that explores probability, statistics, and random number generation!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **7-Segment Display** (1x)
- **LEDs** (6x - for dice pattern display)
- **Push Button** (1x) - for rolling
- **Piezo Buzzer** (1x) - for sound effects
- **220Ω Resistors** (7x - for LEDs and segments)
- **10kΩ Resistor** (1x) - for button pull-up
- **Breadboard** (2x or 1 large)
- **Jumper Wires** (20x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Digital Dice Display
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │  D2-D8      │────────────────┤ 7-Segment       │
    │             │                │                 │
    │  D9-D13     │────────────────┤ LED Pattern     │
    │             │                │                 │
    │         A0  │────────────────┤ Random Seed     │
    │             │                │                 │
    │         A1  │────────────────┤ Roll Button     │
    │             │                │                 │
    │         A2  │────────────────┤ Buzzer          │
    │             │                │                 │
    │         5V  │────────────────┤ Power Rails     │
    │         GND │────────────────┤ Ground Rails    │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: 7-Segment Display Understanding**
Common cathode 7-segment display shows numbers 1-6:

```
7-Segment Display Pinout:
    a
   ---
f |   | b
   -g-
e |   | c
   ---
    d

Pin Layout (Common Cathode):
┌─────────────┐
│  a b c d e f g dp cc│
│  1 2 3 4 5 6 7 8  9 │
└─────────────┘

Pin 1 (a)  - Top segment
Pin 2 (b)  - Top right segment
Pin 3 (c)  - Bottom right segment
Pin 4 (d)  - Bottom segment
Pin 5 (e)  - Bottom left segment
Pin 6 (f)  - Top left segment
Pin 7 (g)  - Middle segment
Pin 8 (dp) - Decimal point (not used)
Pin 9 (cc) - Common cathode (to GND)
```

### **Step 2: Breadboard Layout**
```
Main Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← 7-Segment a
│  2  2  .  .  .  .  .  .  .  .  │ ← 7-Segment b
│  3  3  .  .  .  .  .  .  .  .  │ ← 7-Segment c
│  4  4  .  .  .  .  .  .  .  .  │ ← 7-Segment d
│  5  5  .  .  .  .  .  .  .  .  │ ← 7-Segment e
│  6  6  .  .  .  .  .  .  .  .  │ ← 7-Segment f
│  7  7  .  .  .  .  .  .  .  .  │ ← 7-Segment g
│  8  8  .  .  .  .  .  .  .  .  │ ← 7-Segment common cathode
│  9  9  .  .  .  .  .  .  .  .  │
│ 10 10  .  .  .  .  .  .  .  .  │ ← LED Pattern 1
│ 11 11  .  .  .  .  .  .  .  .  │ ← LED Pattern 2
│ 12 12  .  .  .  .  .  .  .  .  │ ← LED Pattern 3
│ 13 13  .  .  .  .  .  .  .  .  │ ← LED Pattern 4
│ 14 14  .  .  .  .  .  .  .  .  │ ← LED Pattern 5
│ 15 15  .  .  .  .  .  .  .  .  │ ← LED Pattern 6
│ 16 16  .  .  .  .  .  .  .  .  │
│ 17 17  .  .  .  .  .  .  .  .  │ ← Roll Button
│ 18 18  .  .  .  .  .  .  .  .  │ ← Button Pull-up
│ 19 19  .  .  .  .  .  .  .  .  │
│ 20 20  .  .  .  .  .  .  .  .  │ ← Buzzer
└─────────────────────────────────┘
```

### **Step 3: Install 7-Segment Display**
Mount display to show dice numbers:

```
7-Segment Installation:
┌─────────────────────────────────┐
│  1  1  a  .  .  .  .  .  .  .  │ ← Segment a
│  2  2  b  .  .  .  .  .  .  .  │ ← Segment b
│  3  3  c  .  .  .  .  .  .  .  │ ← Segment c
│  4  4  d  .  .  .  .  .  .  .  │ ← Segment d
│  5  5  e  .  .  .  .  .  .  .  │ ← Segment e
│  6  6  f  .  .  .  .  .  .  .  │ ← Segment f
│  7  7  g  .  .  .  .  .  .  .  │ ← Segment g
│  8  8  cc .  .  .  .  .  .  .  │ ← Common cathode
└─────────────────────────────────┘
```

### **Step 4: Install Current-Limiting Resistors**
Each segment needs a 220Ω resistor:

```
Resistor Installation:
┌─────────────────────────────────┐
│  1  1  a  Ra .  .  .  .  .  .  │ ← Segment a + resistor
│  2  2  b  Rb .  .  .  .  .  .  │ ← Segment b + resistor
│  3  3  c  Rc .  .  .  .  .  .  │ ← Segment c + resistor
│  4  4  d  Rd .  .  .  .  .  .  │ ← Segment d + resistor
│  5  5  e  Re .  .  .  .  .  .  │ ← Segment e + resistor
│  6  6  f  Rf .  .  .  .  .  .  │ ← Segment f + resistor
│  7  7  g  Rg .  .  .  .  .  .  │ ← Segment g + resistor
│  8  8  cc ●  .  .  .  .  .  .  │ ← Common cathode to GND
│  9  9  .  Ra .  .  .  .  .  .  │ ← Resistor to D2
│ 10 10  .  Rb .  .  .  .  .  .  │ ← Resistor to D3
│ 11 11  .  Rc .  .  .  .  .  .  │ ← Resistor to D4
│ 12 12  .  Rd .  .  .  .  .  .  │ ← Resistor to D5
│ 13 13  .  Re .  .  .  .  .  .  │ ← Resistor to D6
│ 14 14  .  Rf .  .  .  .  .  .  │ ← Resistor to D7
│ 15 15  .  Rg .  .  .  .  .  .  │ ← Resistor to D8
└─────────────────────────────────┘
```

### **Step 5: Install Dice Pattern LEDs**
6 LEDs arranged in dice pattern:

```
Dice Pattern LEDs:
┌─────────────────────────────────┐
│ 16 16  L1 R1 .  .  .  .  .  .  │ ← LED 1 + resistor
│ 17 17  L2 R2 .  .  .  .  .  .  │ ← LED 2 + resistor
│ 18 18  L3 R3 .  .  .  .  .  .  │ ← LED 3 + resistor
│ 19 19  L4 R4 .  .  .  .  .  .  │ ← LED 4 + resistor
│ 20 20  L5 R5 .  .  .  .  .  .  │ ← LED 5 + resistor
│ 21 21  L6 R6 .  .  .  .  .  .  │ ← LED 6 + resistor
│ 22 22  .  R1─●  .  .  .  .  .  │ ← Resistor to D9
│ 23 23  .  R2─●  .  .  .  .  .  │ ← Resistor to D10
│ 24 24  .  R3─●  .  .  .  .  .  │ ← Resistor to D11
│ 25 25  .  R4─●  .  .  .  .  .  │ ← Resistor to D12
│ 26 26  .  R5─●  .  .  .  .  .  │ ← Resistor to D13
│ 27 27  .  R6─●  .  .  .  .  .  │ ← Resistor to A0
└─────────────────────────────────┘
```

### **Step 6: Install Roll Button**
Button triggers dice roll:

```
Button Installation:
┌─────────────────────────────────┐
│ 28 28  B1 BR .  .  .  .  .  .  │ ← Button + pull-up resistor
│ 29 29  B2 ●  .  .  .  .  .  .  │ ← Button to GND
│ 30 30  .  BR─●  .  .  .  .  .  │ ← Pull-up resistor to 5V
│ 31 31  .  ●  .  .  .  .  .  .  │ ← Button signal to A1
└─────────────────────────────────┘
```

### **Step 7: Install Buzzer**
Piezo buzzer for sound effects:

```
Buzzer Installation:
┌─────────────────────────────────┐
│ 32 32  Z+ .  .  .  .  .  .  .  │ ← Buzzer positive
│ 33 33  Z- .  .  .  .  .  .  .  │ ← Buzzer negative
│ 34 34  .  ●  .  .  .  .  .  .  │ ← Buzzer positive to A2
│ 35 35  .  ●  .  .  .  .  .  .  │ ← Buzzer negative to GND
└─────────────────────────────────┘
```

### **Step 8: Connect All Wires**
```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  a  Ra─●  .  .  .  .  .  │ ← Segment a to D2
│  2  2  b  Rb─●  .  .  .  .  .  │ ← Segment b to D3
│  3  3  c  Rc─●  .  .  .  .  .  │ ← Segment c to D4
│  4  4  d  Rd─●  .  .  .  .  .  │ ← Segment d to D5
│  5  5  e  Re─●  .  .  .  .  .  │ ← Segment e to D6
│  6  6  f  Rf─●  .  .  .  .  .  │ ← Segment f to D7
│  7  7  g  Rg─●  .  .  .  .  .  │ ← Segment g to D8
│  8  8  cc─●  .  .  .  .  .  .  │ ← Common cathode to GND
│  9  9  .  .  .  .  .  .  .  .  │
│ 10 10  L1─R1─●  .  .  .  .  .  │ ← LED 1 to D9
│ 11 11  L2─R2─●  .  .  .  .  .  │ ← LED 2 to D10
│ 12 12  L3─R3─●  .  .  .  .  .  │ ← LED 3 to D11
│ 13 13  L4─R4─●  .  .  .  .  .  │ ← LED 4 to D12
│ 14 14  L5─R5─●  .  .  .  .  .  │ ← LED 5 to D13
│ 15 15  L6─R6─●  .  .  .  .  .  │ ← LED 6 to A0
│ 16 16  .  .  .  .  .  .  .  .  │
│ 17 17  B1─BR─●  .  .  .  .  .  │ ← Button to A1 + pull-up
│ 18 18  B2─●  .  .  .  .  .  .  │ ← Button to GND
│ 19 19  .  .  .  .  .  .  .  .  │
│ 20 20  Z+─●  .  .  .  .  .  .  │ ← Buzzer to A2
│ 21 21  Z-─●  .  .  .  .  .  .  │ ← Buzzer to GND
└─────────────────────────────────┘

● = Jumper wire connections
Ra-Rg = 220Ω resistors for 7-segment
R1-R6 = 220Ω resistors for LEDs
BR = 10kΩ pull-up resistor for button
```

### **Step 9: Wire Connections Summary**
**7-Segment Display:**
- D2 → Segment a (through 220Ω resistor)
- D3 → Segment b (through 220Ω resistor)
- D4 → Segment c (through 220Ω resistor)
- D5 → Segment d (through 220Ω resistor)
- D6 → Segment e (through 220Ω resistor)
- D7 → Segment f (through 220Ω resistor)
- D8 → Segment g (through 220Ω resistor)
- GND → Common cathode

**Dice Pattern LEDs:**
- D9 → LED 1 (through 220Ω resistor)
- D10 → LED 2 (through 220Ω resistor)
- D11 → LED 3 (through 220Ω resistor)
- D12 → LED 4 (through 220Ω resistor)
- D13 → LED 5 (through 220Ω resistor)
- A0 → LED 6 (through 220Ω resistor)
- GND → All LED cathodes

**Control Components:**
- A1 → Roll Button (with 10kΩ pull-up to 5V)
- A2 → Buzzer positive
- GND → Button other terminal, buzzer negative

---

## ⚡ **Circuit Explanation**

### **How Digital Dice Work:**
1. **Random number generation** creates values 1-6
2. **7-segment display** shows the number
3. **LED pattern** mimics traditional dice dots
4. **Button press** triggers new roll
5. **Buzzer** provides audio feedback

### **Number Display Patterns:**
```
7-Segment Patterns for Dice:
Number 1: segments b,c          (  |  )
Number 2: segments a,b,g,e,d    (━━┓
                                  ━━┛)
Number 3: segments a,b,g,c,d    (━━┓
                                  ━━┛)
Number 4: segments f,g,b,c      (┃━┓
                                   ┃)
Number 5: segments a,f,g,c,d    (━━┓
                                  ━━┛)
Number 6: segments a,f,g,e,d,c  (━━┓
                                  ━━┛)
```

### **LED Dice Patterns:**
```
LED Arrangement (like real dice):
┌─────────┐
│ 1     2 │  ← LEDs 1,2 (top row)
│    3    │  ← LED 3 (middle)
│ 4     5 │  ← LEDs 4,5 (bottom row)
│    6    │  ← LED 6 (center bottom)
└─────────┘

Dice Patterns:
1: LED 3 only          (   ●   )
2: LEDs 1,5           (●     ●)
3: LEDs 1,3,5         (●  ●  ●)
4: LEDs 1,2,4,5       (●●   ●●)
5: LEDs 1,2,3,4,5     (●●●●●  )
6: LEDs 1,2,4,5,6     (●● ●●●)
```

### **Random Number Generation:**
```
Arduino randomSeed() and random():
- randomSeed(analogRead(A3)) for true randomness
- random(1,7) generates numbers 1-6
- millis() can also seed for better randomness
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
   │  D2 ●────────┼─── 7-SEG a ──────────┐
   │  D3 ●────────┼─── 7-SEG b ──────────┼─┐
   │  D4 ●────────┼─── 7-SEG c ──────────┼─┼─┐
   │  D5 ●────────┼─── 7-SEG d ──────────┼─┼─┼─┐
   │  D6 ●────────┼─── 7-SEG e ──────────┼─┼─┼─┼─┐
   │  D7 ●────────┼─── 7-SEG f ──────────┼─┼─┼─┼─┼─┐
   │  D8 ●────────┼─── 7-SEG g ──────────┼─┼─┼─┼─┼─┼─┐
   │             │                      │ │ │ │ │ │ │
   │  D9 ●────────┼─── LED 1 ───────────┼─┼─┼─┼─┼─┼─┼─┐
   │ D10 ●────────┼─── LED 2 ───────────┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D11 ●────────┼─── LED 3 ───────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D12 ●────────┼─── LED 4 ───────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ D13 ●────────┼─── LED 5 ───────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                      │ │ │ │ │ │ │ │ │ │ │ │
   │  A0 ●────────┼─── LED 6 ───────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │  A1 ●────────┼─── BUTTON ──────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │  A2 ●────────┼─── BUZZER ──────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  5V ●────────┼─── POWER ───────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │ GND ●────────┼─── GROUND ──────────┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐
   │             │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   └─────────────┘                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
                                        │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   7-SEGMENT DISPLAY                    │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   ┌─────────────┐                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │      a      │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │   ┌─────┐   │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │ f │  g  │ b │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │   ├─────┤   │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │ e │     │ c │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │   └─────┘   │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │      d      │                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   └─────────────┘                      │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │a b c d e f g cc│                   │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │● ● ● ● ● ● ● ● │                   │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │└─┼─┼─┼─┼─┼─┼─┼─┼─┐                 │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  │ │ │ │ │ │ │ │ │                 │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │  └─┼─┼─┼─┼─┼─┼─┼─┼─┼───────────────┘ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │    │ │ │ │ │ │ │ │ │                 │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │ [220Ω]─┼─┼─┼─┼─┼─┼─┼─┼─┼─────────────┘ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │    │ │ │ │ │ │ │ │ │                   │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │    └─┼─┼─┼─┼─┼─┼─┼─┼─┼───────────────────┘ │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │      │ │ │ │ │ │ │ │ │                     │ │ │ │ │ │ │ │ │ │ │ │ │ │
   │   [220Ω]─┼─┼─┼─┼─┼─┼─┼─┼─────────────────────┘ │ │ │ │ │ │ │ │ │ │ │ │ │
   │      │ │ │ │ │ │ │ │ │                       │ │ │ │ │ │ │ │ │ │ │ │ │
   │      └─┼─┼─┼─┼─┼─┼─┼─┼─┼───────────────────────┘ │ │ │ │ │ │ │ │ │ │ │ │
   │        │ │ │ │ │ │ │ │ │                         │ │ │ │ │ │ │ │ │ │ │ │
   │     [220Ω]─┼─┼─┼─┼─┼─┼─┼─┼─────────────────────────┘ │ │ │ │ │ │ │ │ │ │ │
   │        │ │ │ │ │ │ │ │ │                           │ │ │ │ │ │ │ │ │ │ │
   │        └─┼─┼─┼─┼─┼─┼─┼─┼─┼───────────────────────────┘ │ │ │ │ │ │ │ │ │ │
   │          │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │ │ │ │
   │       [220Ω]─┼─┼─┼─┼─┼─┼─┼─┼─────────────────────────────┘ │ │ │ │ │ │ │ │ │
   │          │ │ │ │ │ │ │ │ │                               │ │ │ │ │ │ │ │ │
   │          └─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐                             │ │ │ │ │ │ │ │ │
   │            │ │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │ │ │
   │         [220Ω]─┼─┼─┼─┼─┼─┼─┼─┼─┼─────────────────────────────┘ │ │ │ │ │ │ │ │
   │            │ │ │ │ │ │ │ │ │ │                               │ │ │ │ │ │ │ │
   │            └─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐                             │ │ │ │ │ │ │ │
   │              │ │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │ │
   │           [220Ω]─┼─┼─┼─┼─┼─┼─┼─┼─┼─────────────────────────────┘ │ │ │ │ │ │ │
   │              │ │ │ │ │ │ │ │ │ │                               │ │ │ │ │ │ │
   │              └─┼─┼─┼─┼─┼─┼─┼─┼─┼─┐                             │ │ │ │ │ │ │
   │                │ │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   └────────────────┘ │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
                      │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   DICE PATTERN LEDS  │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   ┌─────────────┐    │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │ ●       ●   │    │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │      ●      │    │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │ ●       ●   │    │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │      ●      │    │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   └─────────────┘    │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │1 2 3 4 5 6 │     │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │● ● ● ● ● ● │     │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │└─┼─┼─┼─┼─┼─┼─┐   │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │  │ │ │ │ │ │ │   │ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │  └─┼─┼─┼─┼─┼─┼─┼─┘ │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │    │ │ │ │ │ │ │   │ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │ [220Ω]─┼─┼─┼─┼─┼─┼─┼─┘ │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │    │ │ │ │ │ │ │     │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │    └─┼─┼─┼─┼─┼─┼─┐   │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │      │ │ │ │ │ │ │   │ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │   [220Ω]─┼─┼─┼─┼─┼─┼─┼─┘ │ │ │ │ │ │                             │ │ │ │ │ │ │
   │      │ │ │ │ │ │ │     │ │ │ │ │ │                             │ │ │ │ │ │ │
   │      └─┼─┼─┼─┼─┼─┼─┐   │ │ │ │ │ │                             │ │ │ │ │ │ │
   │        │ │ │ │ │ │ │   │ │ │ │ │ │                             │ │ │ │ │ │ │
   │     [220Ω]─┼─┼─┼─┼─┼─┼─┼─┘ │ │ │ │ │                             │ │ │ │ │ │ │
   │        │ │ │ │ │ │ │     │ │ │ │ │                             │ │ │ │ │ │ │
   │        └─┼─┼─┼─┼─┼─┼─┐   │ │ │ │ │                             │ │ │ │ │ │ │
   │          │ │ │ │ │ │ │   │ │ │ │ │                             │ │ │ │ │ │ │
   │       [220Ω]─┼─┼─┼─┼─┼─┼─┼─┘ │ │ │ │                             │ │ │ │ │ │ │
   │          │ │ │ │ │ │ │     │ │ │ │                             │ │ │ │ │ │ │
   │          └─┼─┼─┼─┼─┼─┼─┐   │ │ │ │                             │ │ │ │ │ │ │
   │            │ │ │ │ │ │ │   │ │ │ │                             │ │ │ │ │ │ │
   │         [220Ω]─┼─┼─┼─┼─┼─┼─┼─┘ │ │ │                             │ │ │ │ │ │ │
   │            │ │ │ │ │ │ │     │ │ │                             │ │ │ │ │ │ │
   │            └─┼─┼─┼─┼─┼─┼─┐   │ │ │                             │ │ │ │ │ │ │
   │              │ │ │ │ │ │ │   │ │ │                             │ │ │ │ │ │ │
   │           [220Ω]─┼─┼─┼─┼─┼─┼─┼─┘ │ │                             │ │ │ │ │ │ │
   │              │ │ │ │ │ │ │     │ │                             │ │ │ │ │ │ │
   │              └─┼─┼─┼─┼─┼─┼─┐   │ │                             │ │ │ │ │ │ │
   │                │ │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   └────────────────┘ │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
                      │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   ROLL BUTTON        │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   ┌─────────────┐    │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │    ┌───┐    │    │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │    │BTN│    │    │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │    └───┘    │    │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │     │ │     │    │ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │     │ └─────┼────┘ │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │     │       │      │ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │     └───────┼──────┘ │ │ │ │   │ │                             │ │ │ │ │ │ │
   │             │        │ │ │ │   │ │                             │ │ │ │ │ │ │
   │ [10kΩ]──────┼────────┘ │ │ │   │ │                             │ │ │ │ │ │ │
   │             │          │ │ │   │ │                             │ │ │ │ │ │ │
   └─────────────┘          │ │ │   │ │                             │ │ │ │ │ │ │
                            │ │ │   │ │                             │ │ │ │ │ │ │
   PIEZO BUZZER             │ │ │   │ │                             │ │ │ │ │ │ │
   ┌─────────────┐          │ │ │   │ │                             │ │ │ │ │ │ │
   │    ┌───┐    │          │ │ │   │ │                             │ │ │ │ │ │ │
   │    │ + │    │          │ │ │   │ │                             │ │ │ │ │ │ │
   │    │ - │    │          │ │ │   │ │                             │ │ │ │ │ │ │
   │    └───┘    │          │ │ │   │ │                             │ │ │ │ │ │ │
   │     │ │     │          │ │ │   │ │                             │ │ │ │ │ │ │
   │     │ └─────┼──────────┘ │ │   │ │                             │ │ │ │ │ │ │
   │     │       │            │ │   │ │                             │ │ │ │ │ │ │
   │     └───────┼────────────┘ │   │ │                             │ │ │ │ │ │ │
   │             │              │   │ │                             │ │ │ │ │ │ │
   └─────────────┘              │   │ │                             │ │ │ │ │ │ │
                                │   │ │                             │ │ │ │ │ │ │
   POWER DISTRIBUTION           │   │ │                             │ │ │ │ │ │ │
   ┌─────────────┐              │   │ │                             │ │ │ │ │ │ │
   │  5V ●───────┼──────────────┘   │ │                             │ │ │ │ │ │ │
   │             │                  │ │                             │ │ │ │ │ │ │
   │ GND ●───────┼──────────────────┘ │                             │ │ │ │ │ │ │
   │             │                    │                             │ │ │ │ │ │ │
   └─────────────┘                    │                             │ │ │ │ │ │ │
                                      │                             │ │ │ │ │ │ │
                                      └─────────────────────────────┘ │ │ │ │ │ │
                                                                      │ │ │ │ │ │
                                                                      └─┘ │ │ │ │
                                                                         │ │ │ │
                                                                         └─┘ │ │
                                                                            │ │
                                                                            └─┘
```

---

## 🎲 **Digital Dice Programming**

### **Main Program Structure:**
```cpp
// Pin definitions
#define BUTTON_PIN A1
#define BUZZER_PIN A2

// 7-segment display pins
int segmentPins[] = {2, 3, 4, 5, 6, 7, 8};  // a, b, c, d, e, f, g

// LED pattern pins
int ledPins[] = {9, 10, 11, 12, 13, A0};  // 6 LEDs for dice pattern

// 7-segment patterns for numbers 1-6
byte numberPatterns[][7] = {
    {0, 1, 1, 0, 0, 0, 0},  // 1: b, c
    {1, 1, 0, 1, 1, 0, 1},  // 2: a, b, g, e, d
    {1, 1, 1, 1, 0, 0, 1},  // 3: a, b, g, c, d
    {0, 1, 1, 0, 0, 1, 1},  // 4: f, g, b, c
    {1, 0, 1, 1, 0, 1, 1},  // 5: a, f, g, c, d
    {1, 0, 1, 1, 1, 1, 1}   // 6: a, f, g, e, d, c
};

// LED patterns for dice (1-6)
byte dicePatterns[][6] = {
    {0, 0, 1, 0, 0, 0},  // 1: center only
    {1, 0, 0, 0, 1, 0},  // 2: opposite corners
    {1, 0, 1, 0, 1, 0},  // 3: diagonal
    {1, 1, 0, 1, 1, 0},  // 4: four corners
    {1, 1, 1, 1, 1, 0},  // 5: four corners + center
    {1, 1, 0, 1, 1, 1}   // 6: all except center
};

// Global variables
int currentNumber = 1;
bool isRolling = false;
unsigned long rollStartTime = 0;
int rollCounter = 0;

// Statistics
int rollHistory[100];
int rollCount = 0;
int rollStats[7] = {0, 0, 0, 0, 0, 0, 0};  // Index 0 unused, 1-6 for counts

void setup() {
    Serial.begin(9600);
    
    // Initialize pins
    for (int i = 0; i < 7; i++) {
        pinMode(segmentPins[i], OUTPUT);
    }
    
    for (int i = 0; i < 6; i++) {
        pinMode(ledPins[i], OUTPUT);
    }
    
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(BUZZER_PIN, OUTPUT);
    
    // Seed random number generator
    randomSeed(analogRead(A3));
    
    // Initial display
    displayNumber(currentNumber);
    
    Serial.println("Digital Dice Ready!");
    Serial.println("Press button to roll");
}

void loop() {
    // Check for button press
    if (digitalRead(BUTTON_PIN) == LOW && !isRolling) {
        startRoll();
    }
    
    // Handle rolling animation
    if (isRolling) {
        handleRolling();
    }
    
    delay(50);
}
```

### **Display Functions:**
```cpp
void displayNumber(int number) {
    // Clear all segments
    for (int i = 0; i < 7; i++) {
        digitalWrite(segmentPins[i], LOW);
    }
    
    // Light up segments for this number
    for (int i = 0; i < 7; i++) {
        digitalWrite(segmentPins[i], numberPatterns[number-1][i]);
    }
    
    // Clear all LEDs
    for (int i = 0; i < 6; i++) {
        digitalWrite(ledPins[i], LOW);
    }
    
    // Light up LEDs for dice pattern
    for (int i = 0; i < 6; i++) {
        digitalWrite(ledPins[i], dicePatterns[number-1][i]);
    }
}

void startRoll() {
    isRolling = true;
    rollStartTime = millis();
    rollCounter = 0;
    
    // Play roll sound
    tone(BUZZER_PIN, 1000, 100);
    
    Serial.println("Rolling...");
}

void handleRolling() {
    unsigned long elapsed = millis() - rollStartTime;
    
    if (elapsed < 2000) {  // Roll for 2 seconds
        // Change number rapidly during roll
        if (elapsed % 100 == 0) {
            currentNumber = random(1, 7);
            displayNumber(currentNumber);
            rollCounter++;
            
            // Play rolling sound
            if (rollCounter % 5 == 0) {
                tone(BUZZER_PIN, 800 + random(0, 400), 50);
            }
        }
    } else {
        // Roll finished
        finishRoll();
    }
}

void finishRoll() {
    isRolling = false;
    
    // Generate final number
    currentNumber = random(1, 7);
    displayNumber(currentNumber);
    
    // Record statistics
    rollHistory[rollCount % 100] = currentNumber;
    rollStats[currentNumber]++;
    rollCount++;
    
    // Play finish sound
    tone(BUZZER_PIN, 1500, 200);
    delay(300);
    tone(BUZZER_PIN, 2000, 300);
    
    Serial.print("Rolled: ");
    Serial.println(currentNumber);
    
    // Display statistics
    displayStatistics();
}
```

### **Statistics Functions:**
```cpp
void displayStatistics() {
    Serial.println("\n=== ROLL STATISTICS ===");
    Serial.print("Total rolls: ");
    Serial.println(rollCount);
    
    for (int i = 1; i <= 6; i++) {
        Serial.print("Number ");
        Serial.print(i);
        Serial.print(": ");
        Serial.print(rollStats[i]);
        Serial.print(" times (");
        Serial.print((rollStats[i] * 100.0) / rollCount);
        Serial.println("%)");
    }
    
    // Calculate most and least rolled numbers
    int mostRolled = 1, leastRolled = 1;
    for (int i = 2; i <= 6; i++) {
        if (rollStats[i] > rollStats[mostRolled]) mostRolled = i;
        if (rollStats[i] < rollStats[leastRolled]) leastRolled = i;
    }
    
    Serial.print("Most rolled: ");
    Serial.println(mostRolled);
    Serial.print("Least rolled: ");
    Serial.println(leastRolled);
    
    // Check for unusual patterns
    checkPatterns();
    
    Serial.println("=====================\n");
}

void checkPatterns() {
    if (rollCount >= 10) {
        // Check recent rolls for patterns
        int recentRolls[10];
        for (int i = 0; i < 10; i++) {
            recentRolls[i] = rollHistory[(rollCount - 10 + i) % 100];
        }
        
        // Check for streaks
        int maxStreak = 1;
        int currentStreak = 1;
        for (int i = 1; i < 10; i++) {
            if (recentRolls[i] == recentRolls[i-1]) {
                currentStreak++;
                maxStreak = max(maxStreak, currentStreak);
            } else {
                currentStreak = 1;
            }
        }
        
        if (maxStreak >= 3) {
            Serial.print("Streak detected: ");
            Serial.print(maxStreak);
            Serial.println(" in a row!");
        }
        
        // Check for balanced distribution
        bool balanced = true;
        for (int i = 1; i <= 6; i++) {
            float expected = rollCount / 6.0;
            float actual = rollStats[i];
            if (abs(actual - expected) > expected * 0.5) {
                balanced = false;
                break;
            }
        }
        
        if (balanced) {
            Serial.println("Distribution is balanced!");
        } else {
            Serial.println("Distribution is uneven.");
        }
    }
}
```

### **Special Effects:**
```cpp
void celebrateRoll(int number) {
    // Special effects for certain numbers
    switch (number) {
        case 1:
            // Single blink
            displayNumber(0);
            delay(200);
            displayNumber(1);
            break;
            
        case 6:
            // Jackpot animation
            for (int i = 0; i < 3; i++) {
                displayNumber(0);
                delay(100);
                displayNumber(6);
                delay(100);
            }
            
            // Special sound
            for (int freq = 1000; freq <= 2000; freq += 100) {
                tone(BUZZER_PIN, freq, 50);
                delay(50);
            }
            break;
            
        default:
            // Normal display
            displayNumber(number);
            break;
    }
}

void testSequence() {
    Serial.println("Testing display sequence...");
    
    for (int i = 1; i <= 6; i++) {
        Serial.print("Displaying ");
        Serial.println(i);
        displayNumber(i);
        tone(BUZZER_PIN, 1000 + (i * 200), 300);
        delay(1000);
    }
    
    Serial.println("Test complete!");
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check all connections** - This is a complex circuit with many components
2. **Verify 7-segment display** - Common cathode to ground, segments through resistors
3. **Test LED polarities** - Long legs to resistors, short legs to ground
4. **Confirm button wiring** - Pull-up resistor and proper connections

### **Component Test Program:**
```cpp
void componentTest() {
    Serial.println("=== COMPONENT TEST ===");
    
    // Test 7-segment display
    Serial.println("Testing 7-segment display...");
    for (int i = 1; i <= 6; i++) {
        Serial.print("Number ");
        Serial.println(i);
        displayNumber(i);
        delay(1000);
    }
    
    // Test individual LEDs
    Serial.println("Testing LEDs individually...");
    for (int i = 0; i < 6; i++) {
        Serial.print("LED ");
        Serial.println(i + 1);
        
        // Turn off all LEDs
        for (int j = 0; j < 6; j++) {
            digitalWrite(ledPins[j], LOW);
        }
        
        // Turn on current LED
        digitalWrite(ledPins[i], HIGH);
        delay(500);
    }
    
    // Test button
    Serial.println("Testing button (press now)...");
    unsigned long testStart = millis();
    while (millis() - testStart < 5000) {
        if (digitalRead(BUTTON_PIN) == LOW) {
            Serial.println("Button pressed!");
            tone(BUZZER_PIN, 1500, 200);
            break;
        }
    }
    
    // Test buzzer
    Serial.println("Testing buzzer...");
    for (int freq = 500; freq <= 2000; freq += 100) {
        tone(BUZZER_PIN, freq, 100);
        delay(100);
    }
    
    Serial.println("Component test complete!");
}
```

### **Troubleshooting:**
- **7-segment doesn't work**: Check common cathode connection and resistor values
- **LEDs don't light**: Verify polarity and resistor connections
- **Button doesn't respond**: Check pull-up resistor and wiring
- **No sound**: Verify buzzer polarity and connections
- **Random numbers not random**: Check random seed source

---

## 🎪 **Advanced Dice Features**

### **Probability Analysis:**
```cpp
void probabilityAnalysis() {
    Serial.println("\n=== PROBABILITY ANALYSIS ===");
    
    if (rollCount < 36) {
        Serial.println("Need at least 36 rolls for analysis");
        return;
    }
    
    // Expected vs actual frequencies
    float expected = rollCount / 6.0;
    float chiSquare = 0;
    
    for (int i = 1; i <= 6; i++) {
        float observed = rollStats[i];
        float deviation = observed - expected;
        chiSquare += (deviation * deviation) / expected;
        
        Serial.print("Number ");
        Serial.print(i);
        Serial.print(": Expected ");
        Serial.print(expected, 1);
        Serial.print(", Observed ");
        Serial.print(observed);
        Serial.print(", Deviation ");
        Serial.println(deviation, 1);
    }
    
    Serial.print("Chi-square value: ");
    Serial.println(chiSquare, 3);
    
    // Interpret results
    if (chiSquare < 11.07) {
        Serial.println("Distribution appears random (p > 0.05)");
    } else {
        Serial.println("Distribution may not be random (p < 0.05)");
    }
    
    Serial.println("==========================\n");
}
```

### **Game Modes:**
```cpp
// Multiple game modes
enum GameMode {
    STANDARD,
    SPEED_ROLL,
    LUCKY_SEVEN,
    PROBABILITY_DEMO
};

GameMode currentMode = STANDARD;

void handleGameModes() {
    switch (currentMode) {
        case SPEED_ROLL:
            speedRollMode();
            break;
            
        case LUCKY_SEVEN:
            luckySeven();
            break;
            
        case PROBABILITY_DEMO:
            probabilityDemo();
            break;
            
        default:
            // Standard mode handled in main loop
            break;
    }
}

void speedRollMode() {
    // Rapid rolling with shorter animation
    if (isRolling) {
        unsigned long elapsed = millis() - rollStartTime;
        
        if (elapsed < 500) {  // Faster roll
            if (elapsed % 50 == 0) {
                currentNumber = random(1, 7);
                displayNumber(currentNumber);
                tone(BUZZER_PIN, 1000 + random(0, 500), 25);
            }
        } else {
            finishRoll();
        }
    }
}

void luckySeven() {
    // Roll two dice, show sum
    int die1 = random(1, 7);
    int die2 = random(1, 7);
    int sum = die1 + die2;
    
    Serial.print("Die 1: ");
    Serial.print(die1);
    Serial.print(", Die 2: ");
    Serial.print(die2);
    Serial.print(", Sum: ");
    Serial.println(sum);
    
    if (sum == 7) {
        Serial.println("LUCKY SEVEN!");
        // Special celebration
        for (int i = 0; i < 5; i++) {
            tone(BUZZER_PIN, 2000, 100);
            delay(150);
        }
    }
}
```

---

## 🎉 **Success! You've Built a Digital Dice!**

**Congratulations, Probability Engineer!** Your digital dice system is now operational! You've learned random number generation, statistical analysis, probability theory, and electronic display systems - essential skills for game development, data analysis, and statistical modeling!

### **Next Steps:**
- Add multiple dice for complex games
- Create wireless connectivity for remote rolling
- Build tournament modes with scoring
- Add historical data analysis features

### **Real-World Applications:**
- **Game development**: Random number generation and probability systems
- **Statistics education**: Hands-on probability experiments
- **Quality control**: Random sampling systems
- **Simulation**: Monte Carlo methods and modeling
- **Security**: Random number generation for cryptography

---

*Probability is the mathematics of uncertainty - embrace the randomness! Keep building! 🚀*