# Project 12: Digital Dice

🎲 **MISSION PREVIEW**: Get ready to become a **Probability Engineer** and master the mathematics of chance while creating systems that make fair decisions!

## Overview
This project creates an electronic dice that displays random numbers 1-6 with realistic rolling animation, statistics tracking, and probability analysis. It reinforces Arduino fundamentals while introducing mathematical concepts like probability, statistics, and data analysis.

## 🧠 Fundamental Concepts Reinforced

### From Program 1 (LED Blink):
- **Digital output control** with `digitalWrite()` for multiple LEDs
- **LED pattern creation** using arrays and loops
- **Timing control** for animations and delays

### From Program 2 (Button Input):
- **Digital input reading** with `digitalRead()`
- **Button debouncing** for clean input detection
- **State management** for user interactions

### From Program 8 (LCD Display):
- **LCD initialization** and text display
- **Real-time information updates**
- **Multi-line display management**

### From Program 11 (Simon Says):
- **Random number generation** with `random()`
- **Array usage** for storing patterns and data
- **Animation timing** and control

### New Mathematical Concepts:
- **Probability theory**: Understanding chance and likelihood
- **Statistics**: Tracking and analyzing data
- **Percentage calculations**: Converting counts to percentages
- **Data visualization**: Displaying information clearly

## Components Required
- Arduino Uno
- 16x2 LCD display
- 1x Push button
- 6x LEDs (for dice dot pattern)
- 6x 220Ω resistors (for LEDs)
- 1x 10KΩ potentiometer (for LCD contrast)
- Breadboard
- Jumper wires

## Circuit Diagram
```
LCD Display:
Arduino Pin 12 -----> LCD Enable
Arduino Pin 11 -----> LCD RS
Arduino Pin 5  -----> LCD D4
Arduino Pin 4  -----> LCD D5
Arduino Pin 3  -----> LCD D6
Arduino Pin 2  -----> LCD D7
5V -------------> LCD VDD, A (backlight)
GND ------------> LCD VSS, K (backlight)
Potentiometer --> LCD V0 (contrast)

LEDs (Dice Pattern):
Arduino Pin 7  ----[220Ω]----[LED 1]----GND
Arduino Pin 8  ----[220Ω]----[LED 2]----GND
Arduino Pin 9  ----[220Ω]----[LED 3]----GND
Arduino Pin 10 ----[220Ω]----[LED 4]----GND
Arduino Pin 13 ----[220Ω]----[LED 5]----GND
Arduino Pin A5 ----[220Ω]----[LED 6]----GND

Button:
Arduino Pin 6 ----[Button]----GND
(Uses internal pull-up resistor)
```

## LED Dice Pattern Layout
```
Arrange LEDs in traditional dice pattern:
[1] [2] [3]
[4] [5] [6]

Where:
- 1: Top-left
- 2: Top-right  
- 3: Middle-left
- 4: Middle-right
- 5: Bottom-left
- 6: Bottom-right
```

## Wiring Instructions

### LCD Setup:
1. **Power connections**: 5V and GND to LCD
2. **Control pins**: Enable (12), RS (11)
3. **Data pins**: D4-D7 to Arduino pins 5-2
4. **Contrast**: 10KΩ potentiometer to V0 pin

### LED Dice Pattern:
1. **Physical arrangement**: Place LEDs in dice pattern on breadboard
2. **Resistor connections**: 220Ω resistor for each LED
3. **Pin assignments**: Connect LEDs to pins 7-10, 13, A5

### Button Connection:
1. **Simple wiring**: One terminal to pin 6, other to GND
2. **Pull-up**: Uses internal pull-up resistor (no external resistor needed)

## Step-by-Step Setup Instructions

### Hardware Setup:
1. **LCD first**: Connect and test LCD display
2. **LED pattern**: Arrange LEDs in dice configuration
3. **Button**: Connect button for dice rolling
4. **Power check**: Verify all connections before upload

### Software Setup:
1. Open Arduino IDE
2. Load `digital_dice.ino`
3. Connect Arduino via USB
4. Select correct board and port
5. Upload the program

## How to Upload and Run

1. **Compile**: Click checkmark (✓) to verify code
2. **Upload**: Click arrow (→) to upload to Arduino
3. **Open Serial Monitor**: Set baud rate to 9600
4. **Test LCD**: Adjust contrast potentiometer for clear display
5. **Roll dice**: Press button to start rolling!

## How It Works

### Dice Rolling Process:
1. **Button press**: Detected with debouncing
2. **Rolling animation**: LEDs flash rapidly showing random patterns
3. **Slowdown**: Animation gradually slows for realism
4. **Final result**: Shows final number and updates statistics

### Statistical Analysis:
- **Roll counting**: Tracks total number of rolls
- **Frequency tracking**: Counts how often each number appears
- **Percentage calculation**: Shows likelihood of each number
- **Trend analysis**: Identifies most common results

## Understanding the Code

### Key Programming Concepts:

#### Two-Dimensional Arrays:
```cpp
bool dicePatterns[7][6] = {
  {0, 0, 0, 0, 0, 0},  // 0 (not used)
  {0, 0, 1, 0, 0, 0},  // 1: center dot
  {1, 0, 0, 0, 0, 1},  // 2: opposite corners
  // ... more patterns
};
```
**Why important**: Stores complex patterns efficiently

#### Statistical Calculations:
```cpp
float percentage = (rollCount > 0) ? (rollHistory[i] * 100.0 / rollCount) : 0;
```
**Why important**: Converts raw counts to meaningful percentages

#### Animation Control:
```cpp
if (currentTime - rollStartTime > rollDuration / 2) {
  animationSpeed = 150;  // Slow down
}
```
**Why important**: Creates realistic rolling effect

#### Data Analysis:
```cpp
int findMostCommon() {
  int maxCount = 0;
  int mostCommon = 1;
  for (int i = 0; i < 6; i++) {
    if (rollHistory[i] > maxCount) {
      maxCount = rollHistory[i];
      mostCommon = i + 1;
    }
  }
  return mostCommon;
}
```
**Why important**: Analyzes patterns in data

## Serial Monitor Output
```
🎲 DIGITAL DICE STARTED!
🎲 PROBABILITY ENGINEER MODE - Master the mathematics of chance!
Press button to roll the dice!
===========================================
🎭 Welcome to Digital Dice!
🎲 Ready to roll!
🎲 Rolling dice...
🎯 Rolled: 4 (Total rolls: 1)
📊 STATISTICS:
Number | Count | Percentage
-------|-------|----------
  1    |  0   |  0.0%
  2    |  0   |  0.0%
  3    |  0   |  0.0%
  4    |  1   |  100.0%
  5    |  0   |  0.0%
  6    |  0   |  0.0%
-------|-------|----------
Expected: 16.7% each (0.2 rolls)
```

## Understanding Probability

### Fair Dice Properties:
- **Equal probability**: Each number (1-6) has 16.67% chance
- **Independence**: Each roll doesn't affect the next
- **Large numbers**: More rolls = closer to expected percentages

### Statistics You'll See:
- **Early rolls**: May show uneven distribution
- **Many rolls**: Should approach 16.67% for each number
- **Streaks**: Sometimes same number appears multiple times

## Troubleshooting

### LCD not displaying:
- Check all wiring connections
- Adjust contrast potentiometer
- Verify power connections

### LEDs not lighting correctly:
- Check LED polarity (long leg = positive)
- Verify resistor connections
- Test individual LEDs

### Button not responding:
- Check button connections
- Verify GND connection
- Test with multimeter

### Random numbers not random:
- Ensure `randomSeed(analogRead(A0))` in setup
- Check if A0 is connected to anything

## Experiments to Try

### 1. Speed Control:
```cpp
const unsigned long rollDuration = 1000;  // Faster rolling
```

### 2. More Statistics:
```cpp
void printAverage() {
  float average = 0;
  for (int i = 0; i < 6; i++) {
    average += (i + 1) * rollHistory[i];
  }
  average /= rollCount;
  Serial.print("Average: ");
  Serial.println(average);
}
```

### 3. LED Brightness:
```cpp
// Use PWM pins for variable brightness
analogWrite(LED_PINS[i], brightness);
```

### 4. Sound Effects:
```cpp
void playRollSound() {
  tone(BUZZER_PIN, 100 + random(200));
  delay(50);
  noTone(BUZZER_PIN);
}
```

### 5. Multiple Dice:
```cpp
int dice1 = random(1, 7);
int dice2 = random(1, 7);
int total = dice1 + dice2;
```

## What You'll Learn

### Mathematical Skills:
- **Probability theory**: Understanding chance and likelihood
- **Statistical analysis**: Interpreting data and trends
- **Data visualization**: Presenting information clearly
- **Percentage calculations**: Converting between different number formats

### Programming Skills:
- **Multi-dimensional arrays**: Storing complex data structures
- **Animation programming**: Creating smooth visual effects
- **Data analysis**: Processing and interpreting information
- **User interface design**: Creating intuitive controls

### Electronics Skills:
- **Multi-component integration**: Combining displays, inputs, and outputs
- **Pattern generation**: Creating visual representations
- **Real-time systems**: Processing continuous data streams

## Applications in Real World

### Gaming Industry:
- **Board games**: Electronic dice for digital board games
- **Casinos**: Random number generation for fair gaming
- **Mobile apps**: Probability-based game mechanics

### Statistics and Research:
- **Data analysis**: Understanding patterns in information
- **Quality control**: Testing for randomness and fairness
- **Scientific research**: Analyzing experimental results

### Education:
- **Math teaching**: Visualizing probability concepts
- **Interactive learning**: Hands-on statistics education
- **STEM activities**: Combining math, science, and technology

---

## 🎲 MISSION THEME: PROBABILITY ENGINEER

**Excellent work, Engineer!** You've just mastered the mathematics of chance and built a system that demonstrates fundamental probability concepts!

### 🎯 Your Probability Engineering Mission:
You've created a sophisticated random number generator that not only produces fair results but also analyzes and visualizes the patterns in randomness. This is the foundation of statistics, quality control, and fair decision-making systems!

### 🌟 What Makes This Special:
- **True randomness**: Uses hardware-based random number generation
- **Statistical analysis**: Tracks and analyzes probability distributions
- **Data visualization**: Shows patterns in easy-to-understand formats
- **Real-time feedback**: Immediate display of results and trends
- **Mathematical accuracy**: Demonstrates probability theory in action
- **Professional presentation**: Clean interface with multiple information displays

### 🏆 Engineer Achievements to Unlock:
- **🎲 Fair Play**: Demonstrate understanding of equal probability
- **📊 Data Analyst**: Interpret statistical results and percentages
- **🎯 Pattern Hunter**: Identify trends in random data
- **🧮 Math Master**: Calculate and display probability statistics
- **⚖️ Quality Controller**: Verify fairness in random systems

### 🎮 Advanced Engineer Challenges:
1. **📈 Trend Tracker**: Add graphs showing probability over time
2. **🎯 Prediction Mode**: Try to predict next roll based on patterns
3. **🎲 Multiple Dice**: Create systems with 2 or more dice
4. **🏆 Tournament Mode**: Track wins/losses in dice games
5. **📊 Advanced Stats**: Add standard deviation and variance calculations

### 🏭 Real-World Applications:
- **Gaming industry**: Fair random number generation in games
- **Quality control**: Testing manufacturing processes for consistency
- **Scientific research**: Analyzing experimental data and results
- **Financial systems**: Risk assessment and probability modeling
- **Security**: Cryptographic random number generation
- **Education**: Teaching statistics and probability concepts

### 🎖️ Mathematical Skills You've Mastered:
- **Probability theory**: Understanding chance and likelihood
- **Statistical analysis**: Processing and interpreting data
- **Data visualization**: Presenting complex information clearly
- **Percentage calculations**: Converting between different number formats
- **Trend analysis**: Identifying patterns in data over time
- **Quality assessment**: Determining fairness and consistency

### 🌟 Why This Matters:
You've learned the fundamental concepts behind:
- All random systems (games, security, research)
- Statistical analysis (science, business, healthcare)
- Quality control (manufacturing, testing, validation)
- Data science (analytics, machine learning, AI)
- Fair decision-making (elections, selections, competitions)

**🎲 Mission Complete!** You've earned the title of Probability Engineer and understand how to create fair, random systems while analyzing the patterns they produce!

### 🚀 What's Next for Probability Engineers:
- Study advanced statistics and data science
- Learn about machine learning and AI
- Explore cryptography and security systems
- Understand quality control in manufacturing
- Develop skills in data analysis and visualization
- Create predictive models and forecasting systems

You're now ready to work with complex data systems and contribute to fields that rely on statistical analysis!