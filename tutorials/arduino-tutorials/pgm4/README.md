# Program 4: PWM LED Fading

## Overview
This program creates smooth LED fading effects using Pulse Width Modulation (PWM). It demonstrates both linear and sine wave fading patterns, showing how PWM can simulate analog output on digital pins.

## Components Required
- Arduino Uno
- 1x LED
- 1x 220Ω resistor
- Breadboard
- 2x Jumper wires

## Circuit Diagram
```
Arduino Pin 9 (PWM) ----[220Ω]----[LED+]
                                    |
Arduino GND -----------------------[LED-]
```

## Wiring Instructions
1. **LED placement**: Insert LED on breadboard (long leg = positive)
2. **Resistor**: Connect 220Ω resistor to LED positive leg
3. **Connections**:
   - Resistor to Arduino pin 9 (PWM pin)
   - LED negative to Arduino GND

## Step-by-Step Setup Instructions

### Hardware Setup:
1. **Choose PWM pin**: Use pin 9 (PWM pins: 3, 5, 6, 9, 10, 11)
2. **Connect LED**: Through resistor to chosen pin
3. **Ground connection**: Complete circuit to GND

### Software Setup:
1. Open Arduino IDE
2. Load `led_fade.ino`
3. Connect Arduino via USB
4. Select board and port

## How to Upload and Run

1. **Compile**: Click checkmark (✓)
2. **Upload**: Click arrow (→)
3. **Observe**: LED will start fading in and out
4. **Serial Monitor**: 
   - Open at 9600 baud
   - Type 's' for sine wave fade
   - Type 'l' for linear fade

## Understanding the Code

### What is PWM?
- **Pulse Width Modulation**: Rapid on/off switching
- **Duty Cycle**: Percentage of time signal is HIGH
- Creates "average" voltage between 0V and 5V

### PWM Visualization:
```
0% Duty Cycle (OFF):    ________________
25% Duty Cycle:         ‾‾‾‾____________
50% Duty Cycle:         ‾‾‾‾‾‾‾‾________
75% Duty Cycle:         ‾‾‾‾‾‾‾‾‾‾‾‾____
100% Duty Cycle (ON):   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
```

### Key Concepts:
- **analogWrite(pin, value)**: value from 0-255
- **Linear fade**: Constant rate of change
- **Sine wave fade**: Natural, smooth transition
- **constrain()**: Keeps values within bounds

### Fade Algorithms:

**Linear Fade:**
- Add/subtract fixed amount each step
- Reverse direction at limits
- Simple but can appear mechanical

**Sine Wave Fade:**
- Uses trigonometric function
- More natural appearance
- Smoother acceleration/deceleration

## Serial Monitor Interaction
```
LED Fading Program Started!
Watch the LED fade in and out smoothly
Press 's' for sine wave, 'l' for linear fade
Brightness: 0 (fading up)
Brightness: 255 (fading down)
Switched to sine wave fading
Sine wave cycle complete
```

## Troubleshooting

1. **LED not fading**:
   - Verify PWM-capable pin (3,5,6,9,10,11)
   - Check LED orientation
   - Test with fixed brightness first

2. **Flickering instead of smooth fade**:
   - Normal at very low brightness
   - Try sine wave mode
   - Check for loose connections

3. **Fade too fast/slow**:
   - Adjust FADE_DELAY constant
   - Change FADE_AMOUNT for speed

## Experiments to Try

1. **Breathing LED**: Mimic human breathing rhythm
   ```cpp
   // Inhale: 4 seconds, Exhale: 6 seconds
   int breathPhase = millis() % 10000;
   if (breathPhase < 4000) {
     brightness = map(breathPhase, 0, 4000, 0, 255);
   } else {
     brightness = map(breathPhase, 4000, 10000, 255, 0);
   }
   ```

2. **Multiple LEDs with phase shift**:
   ```cpp
   analogWrite(LED1, brightness);
   analogWrite(LED2, 255 - brightness);  // Opposite phase
   ```

3. **Heartbeat pattern**:
   ```cpp
   // Double pulse like heartbeat
   void heartbeat() {
     fadeIn(100);   // Fast fade in
     fadeOut(100);  // Fast fade out
     delay(100);
     fadeIn(100);   // Second pulse
     fadeOut(100);
     delay(500);    // Pause between beats
   }
   ```

4. **Random flicker** (candle effect):
   ```cpp
   brightness = random(100, 255);
   analogWrite(LED_PIN, brightness);
   delay(random(50, 150));
   ```

5. **Gamma correction** for linear perception:
   ```cpp
   // Human eye perceives brightness logarithmically
   int gammaCorrected = pow(brightness/255.0, 2.2) * 255;
   ```

## Advanced Concepts

### PWM Frequency:
- Default: ~490Hz (pins 3,9,10,11)
- Higher: ~980Hz (pins 5,6)
- Can be modified for special applications

### PWM Resolution:
- Arduino Uno: 8-bit (256 levels)
- Some boards: 10-bit or higher

### Applications:
- Motor speed control
- LED dimming
- Sound generation
- Power regulation
- Servo control

## Code Variations

### Exponential Fade:
```cpp
brightness = pow(2, fadeStep/32.0) - 1;
```

### Bouncing Ball Effect:
```cpp
// Simulates bouncing with decay
float velocity = 0;
float position = 255;
float gravity = -2;
float damping = 0.9;
```

## What You've Learned
- PWM (Pulse Width Modulation) concepts
- Simulating analog output on digital pins
- Different fading algorithms
- Mathematical functions in Arduino
- Interactive serial control
- Smooth animation techniques

## Next Steps
Ready for Program 5: Temperature Sensor Reading!

---

## 🎮 MISSION THEME: LIGHT SHOW DESIGNER

**Welcome to the big leagues, Designer!** You've just created professional-grade lighting effects that could grace any stage or installation!

### 🎭 Your Creative Mission:
Transform your simple LED into a mesmerizing light show with two professional fading modes:
- **Linear Fade**: Steady, predictable lighting changes (perfect for architectural lighting)
- **Sine Wave Fade**: Natural, breathing-like effects (ideal for ambient lighting)

### ✨ What Makes This Special:
- **Seamless transitions**: No jerky movements - just smooth, professional fading
- **Interactive control**: Switch between modes in real-time using Serial Monitor
- **Mathematical precision**: Uses sine wave mathematics for natural-looking effects
- **Professional techniques**: The same PWM methods used in theater and film lighting

### 🏆 Designer Achievements to Unlock:
- **🎯 Mode Master**: Successfully switch between linear and sine wave modes
- **🌊 Breathing Expert**: Watch the sine wave create natural breathing effects
- **⚡ Speed Controller**: Modify fade speed by changing FADE_DELAY
- **🔧 Precision Artist**: Create custom fade amounts with FADE_AMOUNT

### 🎮 Advanced Designer Challenges:
1. **💓 Heartbeat Effect**: Create a double-pulse pattern like a heartbeat
2. **🕯️ Candle Simulation**: Add random flicker for realistic candle light
3. **🌈 Multi-LED Symphony**: Control multiple LEDs with phase shifts
4. **🎵 Music Visualization**: Make LEDs respond to sound (advanced)

### 🎪 Real-World Applications:
- **Stage lighting**: Theater and concert effects
- **Home automation**: Smart lighting systems
- **Art installations**: Interactive displays
- **Photography**: Mood lighting for portraits
- **Architecture**: Building facade lighting

### 🎨 Pro Tips for Your Light Show:
- **Sine wave** feels more natural and organic
- **Linear fade** gives precise, technical control
- **Combination effects** create the most interesting displays
- **Timing is everything** - experiment with different delays

**🎭 Mission Complete!** You've mastered the art of smooth lighting transitions - the foundation of all professional lighting design!