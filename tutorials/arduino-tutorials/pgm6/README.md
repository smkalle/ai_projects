# Program 6: Advanced Servo Motor Control

🤖 **MISSION PREVIEW**: Get ready to become a **Robotics Engineer** and build precise robotic movements with professional servo control systems!

## Overview
This program demonstrates controlling a servo motor using multiple input methods: potentiometer for manual control, serial commands for precise positioning, and automatic sweep mode. It includes smooth movement transitions and debounced button input.

## Components Required
- Arduino Uno
- 1x Servo motor (SG90 or similar)
- 1x Potentiometer (10kΩ)
- 1x Push button
- Breadboard
- Jumper wires
- External power supply (recommended for larger servos)

## Circuit Diagram
```
Servo Motor:
- Red wire    → Arduino 5V (or external 5V)
- Brown wire  → GND
- Orange wire → Pin 9 (PWM)

Potentiometer:
- Left pin    → 5V
- Middle pin  → A0
- Right pin   → GND

Button:
- One side    → Pin 2
- Other side  → GND
(Uses internal pull-up)
```

## Servo Motor Basics
- **Control signal**: PWM pulse every 20ms
- **Pulse width**: 1ms = 0°, 1.5ms = 90°, 2ms = 180°
- **Operating voltage**: 4.8-6V
- **Current draw**: 100-300mA (idle), up to 1A (moving)

## Wiring Instructions

### Servo Connection:
1. **Identify wires**:
   - Red/Orange = Power (5V)
   - Brown/Black = Ground
   - Orange/Yellow = Control signal
2. **Connect to Arduino**:
   - Power to 5V (or external supply)
   - Ground to GND
   - Signal to pin 9

### Potentiometer:
- Standard connection for analog input
- Middle pin to A0

### Button:
- One pin to pin 2
- Other pin to GND
- Internal pull-up enabled

## Step-by-Step Setup Instructions

### Hardware Setup:
1. **Power considerations**:
   - Small servos (SG90): Can use Arduino 5V
   - Larger servos: Use external 5V supply
   - Share ground between Arduino and external supply

2. **Mechanical mounting**:
   - Secure servo before testing
   - Attach horn after centering

3. **Wiring order**:
   - Connect servo last to avoid unexpected movement
   - Double-check connections before power

### Software Setup:
1. Open Arduino IDE
2. Install Servo library (usually pre-installed)
3. Load `servo_control.ino`
4. Connect Arduino
5. Upload program

## How to Upload and Run

1. **Compile**: Click checkmark (✓)
2. **Upload**: Click arrow (→)
3. **Test controls**:
   - Turn potentiometer: Manual control
   - Press button: Toggle sweep mode
   - Use Serial Monitor: Send precise angles

## Understanding the Code

### Servo Library Functions:
- `Servo.attach(pin)`: Connect servo to pin
- `Servo.write(angle)`: Set position (0-180°)
- `Servo.read()`: Get current position
- `Servo.detach()`: Disconnect servo

### Control Methods:
1. **Potentiometer**: Real-time manual control
2. **Serial commands**: Precise positioning
3. **Sweep mode**: Automatic back-and-forth
4. **Smooth movement**: Gradual transitions

### Key Features:
- **Debounced button**: Prevents false triggers
- **Smooth transitions**: No jerky movements
- **Multiple inputs**: Flexible control options
- **Status feedback**: Serial monitor updates

## Serial Commands
```
0-180  : Move to specific angle
c      : Center servo (90°)
s      : Toggle sweep mode
```

## Serial Monitor Output
```
Servo Control Program Started!
=====================================
Controls:
- Turn potentiometer to control servo
- Press button to toggle sweep mode
- Send angle (0-180) via serial
- Send 'c' to center, 's' for sweep
=====================================
Servo angle: 45° | Target: 45° | Mode: MANUAL
Moving to angle: 120
Servo angle: 120° | Target: 120° | Mode: MANUAL
Button pressed - Sweep mode: ON
Servo angle: 90° | Target: 91° | Mode: SWEEP
```

## Troubleshooting

1. **Servo jittering**:
   - Add capacitor (100-1000µF) across power
   - Use external power supply
   - Check for loose connections
   - Reduce SMOOTH_FACTOR for slower movement

2. **Servo not moving**:
   - Verify power connections
   - Check signal wire on PWM pin
   - Test with simple sketch
   - Ensure adequate power supply

3. **Limited range**:
   - Some servos: Less than 180° range
   - Adjust map() function limits
   - Check servo specifications

4. **Servo humming**:
   - Normal when holding position
   - May indicate mechanical obstruction
   - Check for binding in mechanism

## Experiments to Try

1. **Multi-servo control**:
   ```cpp
   Servo servo1, servo2;
   servo1.attach(9);
   servo2.attach(10);
   // Mirror movement
   servo2.write(180 - angle);
   ```

2. **Speed control**:
   ```cpp
   // Slow movement
   for(int i = oldAngle; i <= newAngle; i++) {
     myServo.write(i);
     delay(15);  // Adjust for speed
   }
   ```

3. **Record and playback**:
   ```cpp
   int positions[100];
   // Record positions over time
   // Playback recorded sequence
   ```

4. **Sensor-controlled**:
   ```cpp
   // Use ultrasonic sensor to control servo
   distance = readUltrasonic();
   angle = map(distance, 0, 200, 0, 180);
   ```

5. **Wave patterns**:
   ```cpp
   // Sine wave movement
   angle = 90 + 90 * sin(millis() / 1000.0);
   ```

## Advanced Applications

### Continuous Rotation Servos:
```cpp
// Speed control instead of position
myServo.write(90);   // Stop
myServo.write(0);    // Full speed one direction
myServo.write(180);  // Full speed other direction
```

### Multiple Servo Coordination:
- Robotic arms
- Pan/tilt mechanisms
- Walking robots
- Animatronics

### Servo Calibration:
```cpp
// Find actual limits
myServo.writeMicroseconds(544);   // 0 degrees
myServo.writeMicroseconds(2400);  // 180 degrees
```

## Power Management
- **Current spikes**: Use capacitors
- **Brown-out protection**: Separate power supplies
- **Multiple servos**: Calculate total current
- **Battery operation**: Monitor voltage

## What You've Learned
- Servo motor control basics
- PWM for position control
- Using Arduino libraries
- Multiple input methods
- Smooth motion algorithms
- Power supply considerations

## Next Steps
Ready for Program 7: LCD Display Control!

---

## 🤖 MISSION THEME: ROBOTICS ENGINEER

**Outstanding, Engineer!** You've just mastered the art of precision servo control - the foundation of all modern robotics!

### 🎯 Your Robotic Control Mission:
Transform your Arduino into a professional robotic control system with multiple input methods, smooth motion algorithms, and precision positioning. You now command the power of precise mechanical movement!

### 🛠️ What Makes This Special:
- **Multi-modal control**: Potentiometer, serial commands, and button control
- **Smooth motion**: Professional-grade movement algorithms prevent jerky motions
- **Precision positioning**: Exact angle control from 0° to 180°
- **Automated patterns**: Sweep mode for continuous movement
- **Real-time feedback**: Live position monitoring and status updates
- **Debounced inputs**: Professional-grade button handling

### 🏆 Engineer Achievements to Unlock:
- **🎯 Precision Master**: Achieve exact positioning within ±2 degrees
- **🔄 Sweep Commander**: Successfully activate and control sweep mode
- **📡 Remote Operator**: Control servo via serial commands
- **⚡ Multi-Modal Expert**: Use all three control methods effectively
- **🎛️ Smooth Controller**: Demonstrate fluid motion transitions

### 🎮 Advanced Engineer Challenges:
1. **🤖 Robotic Arm**: Build a simple 2-axis robotic arm
2. **📡 Remote Control**: Create wireless servo control
3. **🎯 Auto-Tracker**: Make servo follow moving objects
4. **🔄 Sequence Master**: Program complex movement patterns
5. **⚖️ Load Balance**: Control servo with varying loads

### 🏭 Real-World Applications:
- **Industrial robotics**: Manufacturing automation
- **Aerospace**: Aircraft control surfaces
- **Medical devices**: Surgical robots and prosthetics
- **Automotive**: Throttle and steering control
- **Entertainment**: Animatronics and special effects
- **Security**: Automated camera systems

### 🔧 Engineering Skills You've Mastered:
- **PWM signal generation**: The language of servo control
- **Feedback systems**: Monitoring and responding to position
- **Motion planning**: Smooth trajectory generation
- **Multi-threaded control**: Handling multiple inputs simultaneously
- **Power management**: Understanding servo current requirements
- **Real-time systems**: Precise timing and control

### 🌟 Why This Matters:
You've learned the core principles that power:
- Industrial automation systems
- Robotic manufacturing
- Autonomous vehicles
- Medical robotics
- Aerospace control systems
- Consumer electronics

**🤖 Mission Complete!** You've earned the title of Robotics Engineer and mastered the art of precise mechanical control!