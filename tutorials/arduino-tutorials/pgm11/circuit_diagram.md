# 🎯 Program 11: Simon Says Game Circuit Diagram

## 🎯 **GAME DEVELOPER MISSION**
Create an interactive memory game with LEDs and buttons!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **LEDs** (4x - Red, Green, Blue, Yellow)
- **Push Buttons** (4x)
- **Piezo Buzzer** (1x)
- **220Ω Resistors** (4x - for LEDs)
- **Breadboard** (1x)
- **Jumper Wires** (13x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         D2  │────────────────┤ Red LED         │
    │         D3  │────────────────┤ Green LED       │
    │         D4  │────────────────┤ Blue LED        │
    │         D5  │────────────────┤ Yellow LED      │
    │             │                │                 │
    │         D6  │────────────────┤ Red Button      │
    │         D7  │────────────────┤ Green Button    │
    │         D8  │────────────────┤ Blue Button     │
    │         D9  │────────────────┤ Yellow Button   │
    │             │                │                 │
    │        D10  │────────────────┤ Buzzer          │
    │             │                │                 │
    │         GND │────────────────┤ Common Ground   │
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
│  1  1  .  .  .  .  .  .  .  .  │ ← Red LED
│  2  2  .  .  .  .  .  .  .  .  │
│  3  3  .  .  .  .  .  .  .  .  │ ← Green LED
│  4  4  .  .  .  .  .  .  .  .  │
│  5  5  .  .  .  .  .  .  .  .  │ ← Blue LED
│  6  6  .  .  .  .  .  .  .  .  │
│  7  7  .  .  .  .  .  .  .  .  │ ← Yellow LED
│  8  8  .  .  .  .  .  .  .  .  │
│  9  9  .  .  .  .  .  .  .  .  │ ← Red Button
│ 10 10  .  .  .  .  .  .  .  .  │
│ 11 11  .  .  .  .  .  .  .  .  │ ← Green Button
│ 12 12  .  .  .  .  .  .  .  .  │
│ 13 13  .  .  .  .  .  .  .  .  │ ← Blue Button
│ 14 14  .  .  .  .  .  .  .  .  │
│ 15 15  .  .  .  .  .  .  .  .  │ ← Yellow Button
│ 16 16  .  .  .  .  .  .  .  .  │
│ 17 17  .  .  .  .  .  .  .  .  │ ← Buzzer
│ 18 18  .  .  .  .  .  .  .  .  │
└─────────────────────────────────┘
```

### **Step 2: Install LEDs**
Each LED needs:
- **Long leg (anode)** → Signal row
- **Short leg (cathode)** → Ground row

```
LED Installation:
┌─────────────────────────────────┐
│  1  1  R+  .  .  .  .  .  .  .  │ ← Red LED anode
│  2  2  R-  .  .  .  .  .  .  .  │ ← Red LED cathode
│  3  3  G+  .  .  .  .  .  .  .  │ ← Green LED anode
│  4  4  G-  .  .  .  .  .  .  .  │ ← Green LED cathode
│  5  5  B+  .  .  .  .  .  .  .  │ ← Blue LED anode
│  6  6  B-  .  .  .  .  .  .  .  │ ← Blue LED cathode
│  7  7  Y+  .  .  .  .  .  .  .  │ ← Yellow LED anode
│  8  8  Y-  .  .  .  .  .  .  .  │ ← Yellow LED cathode
└─────────────────────────────────┘
```

### **Step 3: Install Resistors**
Connect 220Ω resistors between LED anodes and signal wires:

```
Resistor Installation:
┌─────────────────────────────────┐
│  1  1  R+  Rr .  .  .  .  .  .  │ ← Red LED + resistor
│  2  2  R-  │  .  .  .  .  .  .  │ ← Red LED cathode
│  3  3  G+  Rg .  .  .  .  .  .  │ ← Green LED + resistor
│  4  4  G-  │  .  .  .  .  .  .  │ ← Green LED cathode
│  5  5  B+  Rb .  .  .  .  .  .  │ ← Blue LED + resistor
│  6  6  B-  │  .  .  .  .  .  .  │ ← Blue LED cathode
│  7  7  Y+  Ry .  .  .  .  .  .  │ ← Yellow LED + resistor
│  8  8  Y-  │  .  .  .  .  .  .  │ ← Yellow LED cathode
└─────────────────────────────────┘
```

### **Step 4: Install Buttons**
Each button connects signal to ground when pressed:

```
Button Installation:
┌─────────────────────────────────┐
│  9  9  Br1─────Br2 .  .  .  .  │ ← Red Button
│ 10 10  .   .   .   .  .  .  .  │
│ 11 11  Bg1─────Bg2 .  .  .  .  │ ← Green Button
│ 12 12  .   .   .   .  .  .  .  │
│ 13 13  Bb1─────Bb2 .  .  .  .  │ ← Blue Button
│ 14 14  .   .   .   .  .  .  .  │
│ 15 15  By1─────By2 .  .  .  .  │ ← Yellow Button
│ 16 16  .   .   .   .  .  .  .  │
└─────────────────────────────────┘
```

### **Step 5: Install Buzzer**
```
Buzzer Installation:
┌─────────────────────────────────┐
│ 17 17  Bz+ .   .   .  .  .  .  │ ← Buzzer positive
│ 18 18  Bz- .   .   .  .  .  .  │ ← Buzzer negative
└─────────────────────────────────┘
```

### **Step 6: Connect All Wires**
```
Final Circuit Connections:
┌─────────────────────────────────┐
│  1  1  R+  Rr──●  .  .  .  .  .  │ ← Red LED (D2)
│  2  2  R-  │   ●  .  .  .  .  .  │ ← Ground bus
│  3  3  G+  Rg──●  .  .  .  .  .  │ ← Green LED (D3)
│  4  4  G-  │   ●  .  .  .  .  .  │ ← Ground bus
│  5  5  B+  Rb──●  .  .  .  .  .  │ ← Blue LED (D4)
│  6  6  B-  │   ●  .  .  .  .  .  │ ← Ground bus
│  7  7  Y+  Ry──●  .  .  .  .  .  │ ← Yellow LED (D5)
│  8  8  Y-  │   ●  .  .  .  .  .  │ ← Ground bus
│  9  9  Br1─●───Br2 .  .  .  .  .  │ ← Red Button (D6)
│ 10 10  .   ●   .   .  .  .  .  .  │ ← Ground bus
│ 11 11  Bg1─●───Bg2 .  .  .  .  .  │ ← Green Button (D7)
│ 12 12  .   ●   .   .  .  .  .  .  │ ← Ground bus
│ 13 13  Bb1─●───Bb2 .  .  .  .  .  │ ← Blue Button (D8)
│ 14 14  .   ●   .   .  .  .  .  .  │ ← Ground bus
│ 15 15  By1─●───By2 .  .  .  .  .  │ ← Yellow Button (D9)
│ 16 16  .   ●   .   .  .  .  .  .  │ ← Ground bus
│ 17 17  Bz+ ●   .   .  .  .  .  .  │ ← Buzzer (D10)
│ 18 18  Bz- ●   .   .  .  .  .  .  │ ← Ground bus
└─────────────────────────────────┘

● = Jumper wire connections
```

---

## 🎨 **Visual Game Layout**

### **Physical Game Arrangement:**
```
    ┌─────────────────────────────┐
    │        SIMON SAYS           │
    │                             │
    │  ┌─────┐      ┌─────┐       │
    │  │ RED │      │GREEN│       │
    │  │ LED │      │ LED │       │
    │  └─────┘      └─────┘       │
    │  [RED ]      [GREEN]       │
    │  [BTN ]      [ BTN ]       │
    │                             │
    │  ┌─────┐      ┌─────┐       │
    │  │BLUE │      │YELLOW│      │
    │  │ LED │      │ LED │       │
    │  └─────┘      └─────┘       │
    │  [BLUE]      [YELLOW]      │
    │  [BTN ]      [ BTN ]       │
    │                             │
    │        ♪ BUZZER ♪           │
    └─────────────────────────────┘
```

### **Connection Summary:**
```
Component        Arduino Pin    Purpose
─────────────────────────────────────────
Red LED          D2            Pattern display
Green LED        D3            Pattern display
Blue LED         D4            Pattern display
Yellow LED       D5            Pattern display
Red Button       D6            Player input
Green Button     D7            Player input
Blue Button      D8            Player input
Yellow Button    D9            Player input
Buzzer           D10           Audio feedback
```

---

## 🎮 **Game Flow Logic**

### **Game States:**
```
WAITING → SHOW_PATTERN → PLAYER_TURN → CHECK_INPUT
   ↑                                        ↓
   └─────────── GAME_OVER ←─────────────────┘
```

### **Pattern Storage:**
```
int gamePattern[100];  // Store up to 100 moves
int currentLevel = 1;  // Current difficulty level

Level 1: [RED]
Level 2: [RED, GREEN]
Level 3: [RED, GREEN, BLUE]
Level 4: [RED, GREEN, BLUE, YELLOW]
...and so on
```

### **Input Validation:**
```
For each level:
1. Show pattern (light up LEDs in sequence)
2. Wait for player input
3. Check if input matches pattern
4. If correct: advance to next level
5. If wrong: game over, restart
```

---

## 🎵 **Audio Feedback**

### **Different Tones for Each Color:**
```cpp
// Frequency assignments
#define NOTE_RED    262   // C4
#define NOTE_GREEN  294   // D4
#define NOTE_BLUE   330   // E4
#define NOTE_YELLOW 349   // F4
#define NOTE_WRONG  100   // Low buzz for errors
#define NOTE_WIN    523   // C5 for success

// Play tone function
void playTone(int frequency, int duration) {
    tone(10, frequency, duration);
    delay(duration);
    noTone(10);
}
```

### **Game Audio Patterns:**
```
Pattern Display:    RED-GREEN-BLUE-YELLOW
Audio Sequence:     C4 - D4 - E4 - F4

Correct Input:      Same tone as button
Wrong Input:        Low buzz (100Hz)
Game Win:           Rising tone sequence
Game Over:          Descending tone sequence
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check all LED polarities** (long leg to resistor)
2. **Verify button connections** (one pin to Arduino, one to ground)
3. **Test buzzer polarity** (positive to D10, negative to ground)
4. **Confirm power connections** (all grounds connected)

### **LED Test Sequence:**
```cpp
// Test each LED individually
digitalWrite(2, HIGH); delay(500); digitalWrite(2, LOW);  // Red
digitalWrite(3, HIGH); delay(500); digitalWrite(3, LOW);  // Green
digitalWrite(4, HIGH); delay(500); digitalWrite(4, LOW);  // Blue
digitalWrite(5, HIGH); delay(500); digitalWrite(5, LOW);  // Yellow
```

### **Button Test:**
```cpp
// Test each button
Serial.println(digitalRead(6));  // Red button
Serial.println(digitalRead(7));  // Green button
Serial.println(digitalRead(8));  // Blue button
Serial.println(digitalRead(9));  // Yellow button
```

### **Troubleshooting:**
- **LED doesn't light**: Check polarity and resistor
- **Button doesn't respond**: Check wiring and INPUT_PULLUP
- **No sound**: Check buzzer polarity and connection
- **Erratic behavior**: Check for loose connections

---

## 🎉 **Success! You've Built an Interactive Game!**

**Congratulations, Game Developer!** You've created a fully functional Simon Says game with multiple inputs and outputs. You've learned complex state management, pattern storage, and real-time user interaction - essential skills for game development and interactive systems!

### **Next Steps:**
- Add difficulty levels (speed variation)
- Create different game modes
- Add score tracking with EEPROM
- Implement multiplayer features

### **Code Enhancements:**
```cpp
// Variable speed based on level
int playbackSpeed = max(200, 800 - (level * 50));

// Score tracking
int highScore = EEPROM.read(0);
if (score > highScore) {
    EEPROM.write(0, score);
}

// Multiple game modes
enum GameMode { CLASSIC, SPEED, REVERSE, MEMORY };
```

---

*Game on! Keep coding! 🚀*