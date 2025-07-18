# Project 11: Simon Says Game

🎮 **MISSION PREVIEW**: Get ready to become a **Game Developer** and create your own electronic games with lights, sounds, and challenges!

## Overview
This project creates a classic Simon Says memory game where players must repeat increasingly complex sequences of LED patterns. It reinforces fundamental Arduino concepts while introducing game programming, arrays, and random number generation.

## 🧠 Fundamental Concepts Reinforced

### From Program 1 (LED Blink):
- **Digital output control** with `digitalWrite()`
- **Pin configuration** with `pinMode()`
- **Basic timing** with `delay()` and `millis()`

### From Program 2 (Button Input):
- **Digital input reading** with `digitalRead()`
- **Pull-up resistors** using `INPUT_PULLUP`
- **Button debouncing** to prevent false readings

### New Programming Concepts:
- **Arrays**: Store sequences of data
- **Loops**: Handle multiple similar components
- **Random numbers**: Create unpredictable game sequences
- **State machines**: Manage different game phases
- **Functions**: Organize code into reusable pieces

## Components Required
- Arduino Uno
- 4x LEDs (Red, Green, Blue, Yellow recommended)
- 4x Push buttons
- 4x 220Ω resistors (for LEDs)
- 1x Buzzer (optional but recommended)
- Breadboard
- Jumper wires

## Circuit Diagram
```
LEDs (with 220Ω resistors):
Arduino Pin 2 ----[220Ω]----[Red LED]----GND
Arduino Pin 3 ----[220Ω]----[Green LED]--GND
Arduino Pin 4 ----[220Ω]----[Blue LED]---GND
Arduino Pin 5 ----[220Ω]----[Yellow LED]-GND

Buttons (using internal pull-ups):
Arduino Pin 6 ----[Button 1]----GND
Arduino Pin 7 ----[Button 2]----GND
Arduino Pin 8 ----[Button 3]----GND
Arduino Pin 9 ----[Button 4]----GND

Buzzer:
Arduino Pin 10 ----[Buzzer+]
GND -----------[Buzzer-]
```

## Wiring Instructions

### LED Connections:
1. **LED setup**: Connect long leg (anode) to resistor, short leg to GND
2. **Resistor connections**: 220Ω resistor between Arduino pin and LED anode
3. **Pin assignments**: 
   - Red LED: Pin 2
   - Green LED: Pin 3
   - Blue LED: Pin 4
   - Yellow LED: Pin 5

### Button Connections:
1. **Simple wiring**: One button terminal to Arduino pin, other to GND
2. **Internal pull-ups**: Code uses `INPUT_PULLUP` (no external resistors needed)
3. **Pin assignments**:
   - Button 1: Pin 6
   - Button 2: Pin 7
   - Button 3: Pin 8
   - Button 4: Pin 9

### Buzzer Connection:
1. **Positive terminal**: Arduino Pin 10
2. **Negative terminal**: Arduino GND

## Step-by-Step Setup Instructions

### Hardware Setup:
1. **Plan your layout**: Arrange LEDs and buttons in a square pattern
2. **Wire LEDs first**: Connect each LED with its resistor to the assigned pins
3. **Add buttons**: Connect buttons to their pins (use internal pull-ups)
4. **Install buzzer**: Connect buzzer for sound effects
5. **Test connections**: Check all connections before powering up

### Software Setup:
1. Open Arduino IDE
2. Load `simon_says.ino`
3. Connect Arduino via USB
4. Select correct board and port
5. Upload the program

## How to Upload and Run

1. **Compile**: Click checkmark (✓) to verify code
2. **Upload**: Click arrow (→) to upload to Arduino
3. **Open Serial Monitor**: Set baud rate to 9600
4. **Game starts**: LEDs will do a startup sequence
5. **Press any button**: Start the game!

## Game Rules

### How to Play:
1. **Watch the sequence**: LEDs will light up in a pattern
2. **Repeat the pattern**: Press buttons in the same order
3. **Listen for feedback**: Buzzer plays different tones for each LED
4. **Level up**: Each successful round adds one more step
5. **Game over**: Wrong button press ends the game

### Scoring:
- **Level**: Shows current difficulty level
- **Sequence length**: Number of steps in current pattern
- **Final score**: Level reached when game ends

## Understanding the Code

### Key Programming Concepts:

#### Arrays (New Concept!):
```cpp
int gameSequence[50];     // Stores the game pattern
int playerSequence[50];   // Stores player input
```
**Why important**: Arrays let us store multiple values in one variable

#### Loops for Multiple Components:
```cpp
for (int i = 0; i < NUM_LEDS; i++) {
  pinMode(LED_PINS[i], OUTPUT);
}
```
**Why important**: Handles multiple similar components efficiently

#### Random Number Generation:
```cpp
randomSeed(analogRead(A0));  // Initialize randomness
int randomLED = random(NUM_LEDS);  // Get random number 0-3
```
**Why important**: Makes game unpredictable and fun

#### State Machine:
```cpp
enum GameState {
  WAITING_TO_START,
  SHOWING_SEQUENCE,
  PLAYER_INPUT,
  GAME_OVER
};
```
**Why important**: Organizes different game phases

### Game Logic Flow:
1. **Initialization**: Set up pins and variables
2. **Wait for start**: Idle animation until button pressed
3. **Show sequence**: Display LED pattern to player
4. **Get input**: Read player button presses
5. **Check correctness**: Compare player input to game sequence
6. **Level up or game over**: Continue or restart based on performance

## Serial Monitor Output
```
🎮 SIMON SAYS GAME STARTED!
🎮 GAME DEVELOPER MODE - Ready to create electronic games!
Press any button to start the game!
=========================================
🎮 GAME STARTING!
🎯 Level 1 - Watch the sequence!
📈 Sequence length: 1
💡 Showing LED 2 (1/1)
🎮 Your turn! Repeat the sequence!
🎯 Player pressed button 2 (1/1)
✅ Correct!
🎉 Sequence complete!
🎊 LEVEL UP! Now on level 2
```

## Troubleshooting

### LEDs not lighting:
- Check LED polarity (long leg = positive)
- Verify resistor connections
- Test with simple blink sketch first

### Buttons not responding:
- Check button wiring to correct pins
- Verify GND connections
- Test button with multimeter

### Buzzer not working:
- Check buzzer polarity
- Verify pin 10 connection
- Test with simple tone sketch

### Game behaves erratically:
- Check for loose connections
- Verify button debouncing is working
- Monitor Serial output for debugging

## Experiments to Try

### 1. Speed Control:
```cpp
const int SEQUENCE_SPEED = 500;  // Make faster
```

### 2. More LEDs:
```cpp
const int NUM_LEDS = 6;  // Add more LEDs and buttons
```

### 3. Difficulty Levels:
```cpp
if (gameLevel > 5) {
  SEQUENCE_SPEED = 400;  // Faster at higher levels
}
```

### 4. Sound Effects:
```cpp
void playSuccessSound() {
  for (int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, 500 + (i * 100));
    delay(100);
  }
}
```

### 5. High Score System:
```cpp
int highScore = 0;
if (gameLevel > highScore) {
  highScore = gameLevel;
  Serial.print("🏆 NEW HIGH SCORE: ");
  Serial.println(highScore);
}
```

## What You'll Learn

### Programming Skills:
- **Array manipulation**: Working with lists of data
- **Loop control**: Efficient handling of multiple components
- **Random numbers**: Creating unpredictable behavior
- **State management**: Organizing complex program flow
- **Function design**: Breaking problems into smaller pieces

### Electronics Skills:
- **Multi-component projects**: Managing multiple inputs/outputs
- **User interface design**: Creating intuitive controls
- **Feedback systems**: Providing visual and audio responses
- **Timing systems**: Coordinating multiple events

### Problem-Solving Skills:
- **Game logic**: Designing rules and win conditions
- **User experience**: Making interfaces fun and responsive
- **Debugging**: Finding and fixing complex issues
- **System integration**: Combining hardware and software

## Applications in Real World

### Game Development:
- **Mobile games**: Touch interfaces and pattern matching
- **Educational games**: Learning through play
- **Arcade systems**: Physical game controls

### User Interface Design:
- **Control panels**: Industrial and consumer electronics
- **Interactive displays**: Museums and exhibitions
- **Accessibility devices**: Alternative input methods

### Testing and Quality Assurance:
- **System testing**: Automated testing procedures
- **User interaction**: Understanding human-computer interfaces
- **Performance optimization**: Making systems responsive

---

## 🎮 MISSION THEME: GAME DEVELOPER

**Awesome work, Developer!** You've just created your first electronic game from scratch!

### 🎯 Your Game Development Mission:
You've built a complete interactive game that combines hardware and software to create an engaging user experience. This is the foundation of all electronic games, from simple toys to complex video games!

### 🌟 What Makes This Special:
- **Interactive gameplay**: Real-time response to player actions
- **Progressive difficulty**: Game gets harder as you improve
- **Multi-sensory feedback**: Visual (LEDs), auditory (buzzer), and tactile (buttons)
- **Memory challenge**: Exercises and improves cognitive skills
- **Replayability**: Random sequences make each game different
- **Professional structure**: Organized code that's easy to modify and expand

### 🏆 Developer Achievements to Unlock:
- **🎮 First Game**: Successfully create and play your electronic game
- **🧠 Pattern Master**: Recognize and remember complex sequences
- **🎯 Level Crusher**: Reach level 10 or higher
- **🎨 Customizer**: Modify game speed, colors, or sounds
- **🏗️ Architect**: Understand and explain the game's code structure

### 🎮 Advanced Developer Challenges:
1. **🎵 Sound Designer**: Create unique tones for each LED
2. **⚡ Speed Demon**: Add progressive speed increases
3. **🏆 Score Keeper**: Implement high score tracking
4. **🎨 Visual Artist**: Add more LEDs for complex patterns
5. **🎭 Game Designer**: Create entirely new game rules

### 🏭 Real-World Applications:
- **Toy industry**: Electronic learning toys and games
- **Arcade gaming**: Physical interactive game systems
- **Educational technology**: Learning through play systems
- **Therapeutic devices**: Cognitive training and rehabilitation
- **Interface design**: Touch panels and control systems
- **Entertainment**: Interactive art installations

### 🎖️ Programming Skills You've Mastered:
- **Data structures**: Arrays to store game sequences
- **Control flow**: State machines and complex logic
- **Random generation**: Creating unpredictable experiences
- **Multi-threading**: Handling multiple inputs simultaneously
- **User interface**: Designing intuitive controls
- **System integration**: Combining hardware and software seamlessly

### 🌟 Why This Matters:
You've learned the fundamental concepts behind:
- All electronic games (from simple toys to complex consoles)
- Interactive user interfaces (touch screens, control panels)
- Real-time systems (immediate response to user input)
- Educational technology (learning through engagement)
- Accessibility technology (alternative input methods)

**🎮 Mission Complete!** You've earned the title of Game Developer and understand how to create engaging, interactive electronic experiences!

### 🚀 What's Next for Game Developers:
- Learn advanced programming languages (C++, Python, Java)
- Explore game engines (Unity, Unreal Engine)
- Study user experience (UX) design
- Understand computer graphics and animation
- Develop mobile and web applications
- Create virtual and augmented reality experiences

You're now ready to build more complex games and interactive systems!