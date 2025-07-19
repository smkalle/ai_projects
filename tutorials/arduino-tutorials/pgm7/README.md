# Program 7: Servo Motor Control

## Overview
This program demonstrates how to control a servo motor using Arduino. The servo position is controlled by a potentiometer, allowing smooth movement from 0 to 180 degrees.

## Components Required
- Arduino board (Uno, Nano, Mega, etc.)
- Servo motor (SG90, MG90S, or similar)
- 10K ohm potentiometer
- Jumper wires
- Breadboard
- External 5V power supply (optional, for multiple or larger servos)

## Circuit Diagram
```
Arduino         Servo Motor
-------         -----------
5V      ------> Red wire (Power)
GND     ------> Brown/Black wire (Ground)
Pin 9   ------> Orange/Yellow wire (Signal)

Arduino         Potentiometer
-------         -------------
5V      ------> Left pin
A0      ------> Middle pin (wiper)
GND     ------> Right pin
```

## Wiring Instructions

### Servo Motor Connection:
1. Connect servo red wire to Arduino 5V
2. Connect servo brown/black wire to Arduino GND
3. Connect servo orange/yellow wire to Arduino pin 9

### Potentiometer Connection:
1. Connect left pin to Arduino 5V
2. Connect middle pin (wiper) to Arduino A0
3. Connect right pin to Arduino GND

### Important Notes:
- If using multiple servos or high-torque servos, use external 5V power supply
- Connect external power ground to Arduino ground
- Servo signal wire still connects to Arduino PWM pin

## Installation and Setup

1. **Install Arduino IDE**
   - Download from: https://www.arduino.cc/en/software
   - Install for your operating system

2. **Connect Arduino**
   - Connect Arduino to computer via USB cable
   - Select correct board: Tools → Board → Arduino Uno (or your board)
   - Select correct port: Tools → Port → COM# (Windows) or /dev/tty.* (Mac/Linux)

3. **No Additional Libraries Required**
   - The Servo library is included with Arduino IDE

## Running the Program

1. Open `servo_control.ino` in Arduino IDE
2. Click the Upload button (→) or press Ctrl+U
3. Open Serial Monitor (Tools → Serial Monitor or Ctrl+Shift+M)
4. Set baud rate to 9600
5. Turn the potentiometer to control servo position

## Expected Behavior

- Servo moves smoothly from 0° to 180° as you turn the potentiometer
- Serial Monitor displays current potentiometer value and servo angle
- Servo responds in real-time to potentiometer changes

## Understanding the Code

### Key Functions:
- `Servo.attach(pin)`: Attaches servo to specified pin
- `Servo.write(angle)`: Moves servo to specified angle (0-180)
- `map(value, fromLow, fromHigh, toLow, toHigh)`: Maps value from one range to another

### Code Flow:
1. Read analog value from potentiometer (0-1023)
2. Map this value to servo angle (0-180)
3. Move servo to mapped position
4. Display values on Serial Monitor

## Troubleshooting

### Servo not moving:
- Check all connections, especially power and ground
- Ensure servo signal wire is on PWM pin (pin 9)
- Try external power supply if servo draws too much current

### Servo jittering:
- Add small capacitor (100µF) across servo power lines
- Increase delay in loop
- Check for loose connections

### Incorrect range of motion:
- Some servos have different ranges (e.g., 0-90 degrees)
- Adjust map function parameters accordingly
- Test with fixed angles first: `myServo.write(0)`, `myServo.write(90)`, `myServo.write(180)`

## Modifications to Try

1. **Speed Control**: Add delays to slow down movement
```cpp
int lastAngle = 0;
if(servoAngle > lastAngle) {
  for(int i = lastAngle; i <= servoAngle; i++) {
    myServo.write(i);
    delay(15);
  }
}
lastAngle = servoAngle;
```

2. **Button Control**: Replace potentiometer with buttons
```cpp
if(digitalRead(BUTTON1) == HIGH) {
  myServo.write(0);
} else if(digitalRead(BUTTON2) == HIGH) {
  myServo.write(180);
}
```

3. **Auto Sweep**: Make servo sweep automatically
```cpp
for(int angle = 0; angle <= 180; angle += 5) {
  myServo.write(angle);
  delay(50);
}
```

## What You'll Learn
- PWM control for servos
- Reading analog inputs
- Mapping values between ranges
- Real-time control systems
- Servo motor basics

## Next Steps
- Try controlling multiple servos
- Build a robotic arm
- Create automated movements
- Combine with sensors for reactive control

---

## 📺 MISSION THEME: DISPLAY MASTER

**Excellent work, Master!** You've taken a major step toward creating visual control systems that respond to your touch!

### 🎯 Your Display Control Mission:
You've built a physical display controller where servo movement represents data visualization. This is the foundation for building interactive dashboards, analog meters, and mechanical displays!

### 🌟 What Makes This Special:
- **Real-time visualization**: Servo position changes instantly with potentiometer input
- **Physical feedback**: See and feel your control input through mechanical movement
- **Analog interface**: Bridge between digital control and physical world
- **Precise mapping**: Linear relationship between input and output
- **Visual indicators**: Serial Monitor shows position with directional arrows

### 🏆 Master Achievements to Unlock:
- **⬅️ Left Master**: Position servo at 0-60 degrees consistently
- **➡️ Right Master**: Position servo at 120-180 degrees consistently
- **⬆️ Center Master**: Hold servo steady at 90 degrees (center position)
- **🎯 Precision Controller**: Demonstrate smooth, controlled movements
- **📊 Data Visualizer**: Use servo position to represent different data values

### 🎮 Advanced Master Challenges:
1. **📊 Analog Meter**: Create a temperature gauge with servo pointer
2. **🎚️ Volume Control**: Use servo to show audio levels
3. **🌡️ Weather Display**: Show temperature ranges with servo position
4. **⚡ Battery Indicator**: Display power levels through servo movement
5. **🎮 Game Controller**: Create a physical control interface

### 🏭 Real-World Applications:
- **Industrial gauges**: Pressure, temperature, speed indicators
- **Audio equipment**: VU meters and level indicators
- **Automotive**: Fuel gauges, speedometers, tachometers
- **Medical devices**: Patient monitoring displays
- **Aerospace**: Flight instrument panels
- **Smart home**: Status indicators and control panels

### 🎨 Why This Matters:
You've mastered the fundamentals of:
- **Human-machine interfaces**: How people interact with systems
- **Data visualization**: Representing information through movement
- **Analog control**: Smooth, continuous input methods
- **Real-time systems**: Immediate response to user input
- **Physical computing**: Bridging digital and mechanical worlds

**📺 Mission Complete!** You've earned the title of Display Master and understand how to create engaging, responsive control interfaces!