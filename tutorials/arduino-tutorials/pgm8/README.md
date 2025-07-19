# Program 8: LCD Display

## Overview
This program demonstrates how to display text and sensor data on a 16x2 LCD display. It shows temperature readings and includes a scrolling text demonstration.

## Components Required
- Arduino board (Uno, Nano, Mega, etc.)
- 16x2 LCD display (HD44780 compatible)
- 10K ohm potentiometer (for contrast adjustment)
- Temperature sensor (LM35 or TMP36)
- Jumper wires
- Breadboard
- 220 ohm resistor (for LCD backlight, if needed)

## Circuit Diagram
```
Arduino         LCD Display
-------         -----------
5V      ------> VSS (Pin 2)
GND     ------> VDD (Pin 1)
Pin 12  ------> Enable (Pin 6)
Pin 11  ------> RS (Pin 4)
Pin 5   ------> D4 (Pin 11)
Pin 4   ------> D5 (Pin 12)
Pin 3   ------> D6 (Pin 13)
Pin 2   ------> D7 (Pin 14)
5V      ------> A (Pin 15, Backlight +)
GND     ------> K (Pin 16, Backlight -)

Potentiometer (Contrast)
------------------------
5V      ------> Pin 1
Wiper   ------> V0 (Pin 3) of LCD
GND     ------> Pin 3

Temperature Sensor (LM35)
-------------------------
5V      ------> Left pin
A0      ------> Middle pin
GND     ------> Right pin
```

## Wiring Instructions

### LCD Display Connection:
1. **Power connections:**
   - LCD VSS (Pin 2) to Arduino 5V
   - LCD VDD (Pin 1) to Arduino GND
   - LCD A (Pin 15) to Arduino 5V (backlight)
   - LCD K (Pin 16) to Arduino GND (backlight)

2. **Control connections:**
   - LCD Enable (Pin 6) to Arduino Pin 12
   - LCD RS (Pin 4) to Arduino Pin 11
   - LCD RW (Pin 5) to GND (write mode)

3. **Data connections (4-bit mode):**
   - LCD D4 (Pin 11) to Arduino Pin 5
   - LCD D5 (Pin 12) to Arduino Pin 4
   - LCD D6 (Pin 13) to Arduino Pin 3
   - LCD D7 (Pin 14) to Arduino Pin 2

### Contrast Control:
1. Connect 10K potentiometer:
   - Pin 1 to Arduino 5V
   - Pin 2 (wiper) to LCD V0 (Pin 3)
   - Pin 3 to Arduino GND

### Temperature Sensor (LM35):
1. Left pin to Arduino 5V
2. Middle pin to Arduino A0
3. Right pin to Arduino GND

## Installation and Setup

1. **Install Arduino IDE**
   - Download from: https://www.arduino.cc/en/software

2. **Connect Arduino**
   - Connect via USB cable
   - Select board: Tools → Board → Arduino Uno
   - Select port: Tools → Port → COM# (Windows) or /dev/tty.* (Mac/Linux)

3. **Library Installation**
   - The LiquidCrystal library is included with Arduino IDE
   - No additional installation required

## Running the Program

1. **Hardware Setup:**
   - Wire the circuit as described above
   - Adjust contrast potentiometer until text is clearly visible
   - Ensure all connections are secure

2. **Upload Code:**
   - Open `lcd_display.ino` in Arduino IDE
   - Click Upload button (→) or press Ctrl+U
   - Open Serial Monitor (Ctrl+Shift+M) and set baud rate to 9600

3. **Expected Behavior:**
   - LCD displays "Arduino LCD Demo" followed by "Initializing..."
   - After 2 seconds, shows current temperature and voltage
   - Every 10 seconds, demonstrates scrolling text
   - Serial Monitor shows the same data

## Understanding the Code

### Key Functions:
- `lcd.begin(16, 2)`: Initialize LCD with 16 columns, 2 rows
- `lcd.setCursor(col, row)`: Set cursor position
- `lcd.print(text)`: Display text at cursor position
- `lcd.clear()`: Clear entire display
- `lcd.createChar(num, array)`: Create custom character

### Program Flow:
1. Initialize LCD and display startup message
2. Read temperature sensor every second
3. Display temperature and voltage on LCD
4. Show scrolling text demo every 10 seconds
5. Output data to Serial Monitor

## Troubleshooting

### No display on LCD:
- Check all wiring connections
- Adjust contrast potentiometer
- Verify 5V and GND connections
- Ensure LCD is HD44780 compatible

### Garbled text:
- Check data pin connections (D4-D7)
- Verify Enable and RS pin connections
- Adjust contrast potentiometer
- Check for loose connections

### Dim or no backlight:
- Check backlight connections (A and K pins)
- Add 220 ohm resistor in series with backlight if too bright
- Some LCDs have different backlight pin arrangements

### Temperature readings incorrect:
- Verify temperature sensor type (LM35 vs TMP36)
- Check sensor connections
- Adjust temperature calculation formula if needed

## LCD Pin Reference

| LCD Pin | Name     | Function                | Arduino Connection |
|---------|----------|-------------------------|-------------------|
| 1       | VSS      | Ground                  | GND               |
| 2       | VDD      | 5V Power                | 5V                |
| 3       | V0       | Contrast                | Potentiometer     |
| 4       | RS       | Register Select         | Pin 11            |
| 5       | Enable   | Enable                  | Pin 12            |
| 6       | D0       | Data 0 (not used)       | -                 |
| 7       | D1       | Data 1 (not used)       | -                 |
| 8       | D2       | Data 2 (not used)       | -                 |
| 9       | D3       | Data 3 (not used)       | -                 |
| 10      | D4       | Data 4                  | Pin 5             |
| 11      | D5       | Data 5                  | Pin 4             |
| 12      | D6       | Data 6                  | Pin 3             |
| 13      | D7       | Data 7                  | Pin 2             |
| 14      | A        | Backlight Anode         | 5V                |
| 15      | K        | Backlight Cathode       | GND               |

## Modifications to Try

1. **Menu System:**
```cpp
void displayMenu() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("1.Temp  2.Time");
  lcd.setCursor(0, 1);
  lcd.print("3.Count 4.Demo");
}
```

2. **Real-time Clock:**
```cpp
unsigned long seconds = millis() / 1000;
int hours = (seconds / 3600) % 24;
int minutes = (seconds / 60) % 60;
int secs = seconds % 60;
```

3. **Custom Characters:**
```cpp
byte degree[8] = {
  0b00110,
  0b01001,
  0b01001,
  0b00110,
  0b00000,
  0b00000,
  0b00000,
  0b00000
};
lcd.createChar(0, degree);
```

## What You'll Learn
- LCD display control
- Text positioning and formatting
- Custom character creation
- Real-time data display
- User interface design
- Multi-tasking with millis()

## Next Steps
- Create interactive menus
- Build a weather station display
- Add button navigation
- Implement data logging display
- Create animated characters

---

## 📏 MISSION THEME: DISTANCE DETECTIVE

**Impressive work, Detective!** You've built a sophisticated information display system that shows data in real-time!

### 🎯 Your Information Display Mission:
You've created a professional-grade display interface that can show multiple pieces of information simultaneously. This is the foundation for building dashboards, control panels, and monitoring systems!

### 🌟 What Makes This Special:
- **Multi-line display**: Show multiple data points at once
- **Real-time updates**: Information refreshes automatically
- **Professional formatting**: Clean, organized data presentation
- **Scrolling capabilities**: Handle long messages gracefully
- **Custom characters**: Create unique symbols and indicators
- **Contrast control**: Adjust display for perfect visibility

### 🏆 Detective Achievements to Unlock:
- **📊 Data Displayer**: Successfully show temperature and voltage readings
- **🎨 Interface Designer**: Create clean, readable displays
- **⏰ Real-time Operator**: Demonstrate live data updates
- **🎭 Character Creator**: Design and display custom characters
- **📺 Multi-tasker**: Show multiple data streams simultaneously

### 🎮 Advanced Detective Challenges:
1. **📊 Dashboard Creator**: Build a multi-sensor monitoring display
2. **🎮 Menu Master**: Create interactive navigation menus
3. **⏰ Clock Builder**: Display real-time clock with date
4. **🌡️ Weather Station**: Show temperature, humidity, and pressure
5. **🎯 Status Monitor**: Create system status indicators

### 🏭 Real-World Applications:
- **Industrial control**: Machine status and parameter displays
- **Home automation**: Smart home control panels
- **Automotive**: Dashboard information systems
- **Medical devices**: Patient monitoring displays
- **Scientific instruments**: Data collection interfaces
- **Security systems**: Status and alarm displays

### 🎨 Why This Matters:
You've mastered the fundamentals of:
- **Information architecture**: How to organize and present data
- **User experience**: Making information easy to read and understand
- **Real-time systems**: Updating displays without interruption
- **Interface design**: Creating professional-looking control panels
- **Multi-threading**: Handling multiple tasks simultaneously

**📏 Mission Complete!** You've earned the title of Distance Detective and mastered the art of professional information display systems!