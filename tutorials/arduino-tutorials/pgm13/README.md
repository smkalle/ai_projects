# Project 13: Mood Ring Light

🌈 **MISSION PREVIEW**: Get ready to become a **Color Scientist** and master the science of color mixing while creating dynamic lighting systems!

## Overview
This project creates an RGB LED mood light that changes color based on temperature (like mood rings) with smooth color transitions and both automatic and manual control modes. It reinforces analog input concepts while introducing color theory and RGB color mixing.

## 🧠 Fundamental Concepts Reinforced

### From Program 3 (PWM LED Fade):
- **PWM output control** with `analogWrite()` for LED brightness
- **Smooth animations** and timing control
- **Value interpolation** for seamless transitions

### From Program 4 (Potentiometer Reading):
- **Analog input reading** with `analogRead()`
- **Value mapping** with `map()` function
- **Real-time user input processing**

### From Program 5 (Temperature Sensor):
- **Temperature sensor reading** and calibration
- **Data smoothing** through averaging
- **Analog-to-digital conversion** concepts

### New Color Science Concepts:
- **RGB color mixing**: Understanding additive color theory
- **HSV color space**: Hue, saturation, and value relationships
- **Color temperature**: How temperature relates to color perception
- **Smooth color transitions**: Interpolation between colors

## Components Required
- Arduino Uno
- RGB LED (common cathode)
- Temperature sensor (LM35 or TMP36)
- 10KΩ potentiometer
- 3x 220Ω resistors (for RGB LED)
- Breadboard
- Jumper wires

## Circuit Diagram
```
Temperature Sensor (LM35):
5V ---------> LM35 Pin 1 (VCC)
A0 ---------> LM35 Pin 2 (Output)
GND --------> LM35 Pin 3 (GND)

Potentiometer:
5V ---------> Potentiometer Pin 1
A1 ---------> Potentiometer Pin 2 (Wiper)
GND --------> Potentiometer Pin 3

RGB LED (Common Cathode):
Arduino Pin 9  ----[220Ω]----[Red LED]
Arduino Pin 10 ----[220Ω]----[Green LED]
Arduino Pin 11 ----[220Ω]----[Blue LED]
GND ------------------------[LED Common Cathode]
```

## Wiring Instructions

### Temperature Sensor (LM35):
1. **Pin 1** (VCC) → Arduino 5V
2. **Pin 2** (Output) → Arduino A0
3. **Pin 3** (GND) → Arduino GND

### Potentiometer:
1. **Outer pins** → 5V and GND
2. **Middle pin** (wiper) → Arduino A1

### RGB LED:
1. **Common cathode** → Arduino GND
2. **Red anode** → 220Ω resistor → Arduino Pin 9
3. **Green anode** → 220Ω resistor → Arduino Pin 10
4. **Blue anode** → 220Ω resistor → Arduino Pin 11

## Step-by-Step Setup Instructions

### Hardware Setup:
1. **Temperature sensor**: Connect LM35 for temperature reading
2. **Potentiometer**: Wire for manual color control
3. **RGB LED**: Connect with current-limiting resistors
4. **Test connections**: Verify all connections before upload

### Software Setup:
1. Open Arduino IDE
2. Load `mood_ring_light.ino`
3. Connect Arduino via USB
4. Select correct board and port
5. Upload the program

## How to Upload and Run

1. **Compile**: Click checkmark (✓) to verify code
2. **Upload**: Click arrow (→) to upload to Arduino
3. **Open Serial Monitor**: Set baud rate to 9600
4. **Watch colors**: LED will show startup color demonstration
5. **Test temperature**: Touch sensor to see color changes

## How It Works

### Temperature Mode (Automatic):
- **Cold (< 15°C)**: Deep blue
- **Cool (15-20°C)**: Blue to cyan transition
- **Moderate (20-25°C)**: Cyan to green transition
- **Warm (25-30°C)**: Green to yellow transition
- **Hot (> 30°C)**: Yellow to red transition

### Manual Mode:
- **Potentiometer control**: Turn knob to cycle through color spectrum
- **Full color wheel**: 360 degrees of hue control
- **Automatic return**: Returns to temperature mode after inactivity

## Understanding the Code

### Key Programming Concepts:

#### RGB Color Control:
```cpp
analogWrite(RED_PIN, redValue);
analogWrite(GREEN_PIN, greenValue);
analogWrite(BLUE_PIN, blueValue);
```
**Why important**: Controls individual color components

#### Temperature to Color Mapping:
```cpp
if (temperature < TEMP_COLD) {
  targetRed = 0;
  targetGreen = 0;
  targetBlue = 255;  // Pure blue
}
```
**Why important**: Maps physical measurements to visual representation

#### Smooth Color Transitions:
```cpp
redValue += (targetRed - redValue) * TRANSITION_SPEED;
```
**Why important**: Creates smooth, professional-looking color changes

#### HSV to RGB Conversion:
```cpp
void hsvToRgb(float h, float s, float v, float* r, float* g, float* b)
```
**Why important**: Converts between different color representation systems

## Serial Monitor Output
```
🌈 MOOD RING LIGHT STARTED!
🌈 COLOR SCIENTIST MODE - Master the science of color mixing!
Temperature-based color changing system
=========================================
🎭 Welcome to Mood Ring Light!
🌈 Color demonstration...
🔴 Red
🟢 Green
🔵 Blue
⚪ White
🌈 Rainbow transition...
🎨 Ready for mood detection!
🌡️ Auto mode: Colors change with temperature
🌡️ Temp: 23.4°C | 🎨 Mode: AUTO | 🌈 RGB: (128, 255, 64) | 🟢 GREEN
```

## Understanding Color Theory

### RGB Color Mixing:
- **Additive color**: Red + Green + Blue = White
- **Primary colors**: Red, Green, Blue
- **Secondary colors**: Cyan, Magenta, Yellow

### HSV Color Space:
- **Hue**: Color position on color wheel (0-360°)
- **Saturation**: Color intensity (0-100%)
- **Value**: Color brightness (0-100%)

### Color Temperature:
- **Cool colors**: Blue, cyan (associated with cold)
- **Warm colors**: Red, yellow (associated with heat)
- **Neutral colors**: Green (moderate temperature)

## Troubleshooting

### RGB LED not lighting:
- Check LED type (common cathode vs anode)
- Verify resistor connections
- Test individual color channels

### Temperature not affecting color:
- Check temperature sensor wiring
- Verify sensor type (LM35 vs TMP36)
- Test sensor with known temperature

### Colors not smooth:
- Check PWM pin connections (9, 10, 11)
- Verify transition speed setting
- Ensure stable power supply

### Potentiometer not working:
- Check wiper connection to A1
- Verify power connections
- Test with multimeter

## Experiments to Try

### 1. Different Color Ranges:
```cpp
const float TEMP_COLD = 10.0;   // Adjust temperature ranges
const float TEMP_HOT = 35.0;
```

### 2. Brightness Control:
```cpp
int brightness = map(analogRead(A2), 0, 1023, 0, 255);
```

### 3. Color Patterns:
```cpp
void breathingEffect() {
  static int breathValue = 0;
  static int breathDirection = 1;
  breathValue += breathDirection * 2;
  if (breathValue >= 255 || breathValue <= 0) {
    breathDirection *= -1;
  }
  brightness = breathValue;
}
```

### 4. Multiple Temperature Sensors:
```cpp
float avgTemp = (readTemp(A0) + readTemp(A2)) / 2.0;
```

### 5. Color Memory:
```cpp
void saveColor() {
  EEPROM.write(0, redValue);
  EEPROM.write(1, greenValue);
  EEPROM.write(2, blueValue);
}
```

## What You'll Learn

### Color Science:
- **Color theory**: Understanding how colors mix and interact
- **Color spaces**: RGB, HSV, and color temperature concepts
- **Visual perception**: How humans perceive color and temperature
- **Color psychology**: Emotional associations with colors

### Programming Skills:
- **Multi-mode systems**: Switching between automatic and manual control
- **Smooth interpolation**: Creating seamless transitions
- **Color space conversion**: Mathematical color transformations
- **Real-time processing**: Responding to multiple inputs simultaneously

### Electronics Skills:
- **RGB LED control**: Managing multiple PWM channels
- **Sensor integration**: Combining temperature and user input
- **Analog input processing**: Reading and filtering sensor data

## Applications in Real World

### Entertainment and Art:
- **Stage lighting**: Dynamic color control for performances
- **Art installations**: Interactive color displays
- **Gaming**: Mood lighting that responds to game events

### User Interface Design:
- **Status indicators**: Color-coded system feedback
- **Accessibility**: Visual indicators for hearing-impaired users
- **Smart home**: Ambient lighting that reflects conditions

### Scientific Instruments:
- **Temperature visualization**: Color-coded temperature displays
- **Data representation**: Using color to represent measurements
- **Process monitoring**: Visual feedback for industrial systems

---

## 🌈 MISSION THEME: COLOR SCIENTIST

**Fantastic work, Scientist!** You've just mastered the science of color mixing and created a sophisticated lighting system that responds to the environment!

### 🎯 Your Color Science Mission:
You've built an intelligent lighting system that demonstrates the relationship between temperature and color perception while mastering the technical aspects of RGB color mixing and smooth transitions. This is the foundation of all dynamic lighting systems!

### 🌟 What Makes This Special:
- **Temperature-responsive**: Automatically adjusts colors based on environmental conditions
- **Smooth transitions**: Professional-quality color changes with no abrupt jumps
- **Dual-mode operation**: Both automatic and manual control systems
- **Color theory application**: Demonstrates RGB mixing and HSV color space
- **Real-time processing**: Immediate response to temperature and user input
- **Scientific accuracy**: Uses actual temperature ranges and color theory principles

### 🏆 Scientist Achievements to Unlock:
- **🌡️ Temperature Reader**: Successfully correlate temperature with color changes
- **🎨 Color Mixer**: Demonstrate understanding of RGB color combinations
- **🔄 Mode Master**: Switch between automatic and manual control modes
- **🌈 Spectrum Controller**: Navigate the full color wheel with potentiometer
- **⚡ Transition Expert**: Create smooth, professional color changes

### 🎮 Advanced Scientist Challenges:
1. **🌅 Sunrise Simulator**: Create automatic daily color cycles
2. **🎵 Music Visualizer**: Make colors respond to sound input
3. **🌡️ Multi-Zone**: Control multiple RGB lights for room-wide effects
4. **📊 Data Visualizer**: Use colors to represent different data types
5. **🎨 Color Mixer**: Create custom color palettes and save them

### 🏭 Real-World Applications:
- **Entertainment industry**: Stage and architectural lighting
- **User interface design**: Status indicators and feedback systems
- **Scientific visualization**: Data representation through color
- **Smart home technology**: Ambient lighting and mood control
- **Therapeutic applications**: Color therapy and mood enhancement
- **Industrial monitoring**: Visual status indicators for equipment

### 🔬 Scientific Skills You've Mastered:
- **Color theory**: Understanding RGB, HSV, and color temperature
- **Sensor integration**: Combining multiple input sources
- **Data interpolation**: Creating smooth transitions between values
- **Real-time processing**: Immediate response to environmental changes
- **User interface design**: Creating intuitive control systems
- **Mathematical modeling**: Converting between different measurement systems

### 🌟 Why This Matters:
You've learned the fundamental concepts behind:
- Professional lighting systems (theaters, concerts, architecture)
- User interface design (status indicators, feedback systems)
- Scientific visualization (data representation, process monitoring)
- Smart home technology (responsive lighting, mood control)
- Art and entertainment (interactive installations, gaming)

**🌈 Mission Complete!** You've earned the title of Color Scientist and understand how to create responsive, intelligent lighting systems that combine science with art!

### 🚀 What's Next for Color Scientists:
- Study advanced color theory and color psychology
- Learn about LED strip programming and addressable LEDs
- Explore computer graphics and digital art creation
- Understand lighting design for photography and film
- Develop skills in data visualization and infographics
- Create interactive art installations and exhibits

You're now ready to work with professional lighting systems and create stunning visual experiences!