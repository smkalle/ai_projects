# Project 14: Pet Feeder Timer

🐕 **MISSION PREVIEW**: Get ready to become a **Pet Care Engineer** and design automated systems that take care of pets while solving real-world problems!

## Overview
This project creates an automatic pet feeder with servo-controlled food dispensing, LCD countdown display, and customizable feeding schedules. It reinforces servo control, LCD display, and timing concepts while introducing automation and scheduling systems.

## 🧠 Fundamental Concepts Reinforced

### From Program 2 (Button Input):
- **Multi-button handling** with debouncing
- **State-based button responses** for different modes
- **User interface navigation** with button controls

### From Program 7 (Servo Control):
- **Servo positioning** with `servo.write()`
- **Mechanical automation** for food dispensing
- **Precise motor control** for reliable operation

### From Program 8 (LCD Display):
- **Multi-mode display** showing different information
- **Real-time updates** with countdown timers
- **User interface design** for easy interaction

### New Automation Concepts:
- **Scheduling systems**: Long-term timing and automation
- **State machine design**: Managing complex system behaviors
- **Configuration interfaces**: User-customizable settings
- **Real-world problem solving**: Practical pet care automation

## Components Required
- Arduino Uno
- Servo motor (SG90 or similar)
- 16x2 LCD display
- 3x Push buttons (Set, Up, Down)
- 1x Manual feed button
- Buzzer (for alerts)
- LED (status indicator)
- 220Ω resistor (for LED)
- 10KΩ potentiometer (for LCD contrast)
- Small container/mechanism for food dispensing
- Breadboard and jumper wires

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

Servo Motor:
Arduino Pin 9 -----> Servo Signal (Orange/Yellow)
5V ------------> Servo Power (Red)
GND -----------> Servo Ground (Brown/Black)

Buttons:
Arduino Pin 6 ----[SET Button]----GND
Arduino Pin 7 ----[UP Button]----GND
Arduino Pin 8 ----[DOWN Button]----GND
Arduino Pin A0 ---[MANUAL Button]----GND
(All buttons use internal pull-up resistors)

Audio/Visual:
Arduino Pin 10 ----[Buzzer]----GND
Arduino Pin 13 ----[220Ω]----[LED]----GND
```

## Physical Setup

### Food Dispenser Mechanism:
1. **Container**: Small food container attached to servo
2. **Servo arm**: Attached to sliding door or rotating dispenser
3. **Mounting**: Secure servo to prevent movement during operation
4. **Food capacity**: Size container appropriately for pet's needs

### Button Layout:
- **SET**: Enter/exit setup mode
- **UP**: Increase time values
- **DOWN**: Decrease time values
- **MANUAL**: Immediate feeding (emergency/treat)

## Step-by-Step Setup Instructions

### Hardware Setup:
1. **LCD first**: Connect and test display with contrast adjustment
2. **Servo motor**: Connect and test movement range
3. **Buttons**: Wire all control buttons with pull-up resistors
4. **Audio/Visual**: Connect buzzer and status LED
5. **Mechanical**: Build food dispensing mechanism

### Software Setup:
1. Open Arduino IDE
2. Load `pet_feeder_timer.ino`
3. Connect Arduino via USB
4. Select correct board and port
5. Upload the program

## How to Upload and Run

1. **Compile**: Click checkmark (✓) to verify code
2. **Upload**: Click arrow (→) to upload to Arduino
3. **Test LCD**: Adjust contrast for clear display
4. **Test servo**: Verify food dispenser movement
5. **Set schedule**: Use buttons to configure feeding times

## How It Works

### Normal Operation:
1. **Countdown display**: Shows time until next feeding
2. **Automatic feeding**: Servo opens dispenser at scheduled time
3. **Alert system**: Buzzer sounds when feeding begins
4. **Status tracking**: Counts total number of feedings

### Setup Mode:
1. **Press SET**: Enter hours setup mode
2. **Use UP/DOWN**: Adjust feeding interval (1-24 hours)
3. **Press SET**: Enter minutes setup mode
4. **Use UP/DOWN**: Adjust minutes (0, 15, 30, 45)
5. **Press SET**: Save settings and return to normal

### Manual Feeding:
- **Press MANUAL**: Immediate food dispensing
- **Emergency use**: For treats or missed scheduled feedings
- **Counted separately**: Tracks manual vs automatic feedings

## Understanding the Code

### Key Programming Concepts:

#### State Machine Design:
```cpp
enum SystemState {
  NORMAL_OPERATION,
  SETUP_HOURS,
  SETUP_MINUTES,
  FEEDING,
  MANUAL_FEED
};
```
**Why important**: Organizes complex system behavior

#### Long-term Timing:
```cpp
unsigned long feedingIntervalMs = 6UL * 60UL * 60UL * 1000UL; // 6 hours
```
**Why important**: Handles scheduling over hours and days

#### Multi-button Interface:
```cpp
void handleButtons() {
  // Check all buttons with debouncing
  // Respond based on current state
}
```
**Why important**: Creates intuitive user interface

#### Servo Automation:
```cpp
void handleFeeding() {
  feederServo.write(SERVO_OPEN);
  delay(FEED_DURATION);
  feederServo.write(SERVO_CLOSED);
}
```
**Why important**: Reliable mechanical automation

## Serial Monitor Output
```
🐕 PET FEEDER TIMER STARTED!
🐕 PET CARE ENGINEER MODE - Design automated pet care systems!
Automatic feeding system with customizable schedule
================================================
🔧 Testing feeder mechanism...
✅ System test complete
🍽️ System ready for feeding schedule
📅 Feed interval: 6 hours, 0 minutes
⚙️ Entering hours setup mode
⬆️ Hours: 8
✅ Setup complete, returning to normal operation
📅 Next feeding in: 8h 0m
🍽️ Feeding time!
🥄 Dispensing food...
✅ Feeding #1 completed
```

## LCD Display Modes

### Normal Operation:
```
Next Feed: 
2h 45m (3 fed)
```

### Hours Setup:
```
Set Feed Hours:
>>> 8 hours <<<
```

### Minutes Setup:
```
Set Feed Minutes:
>>> 30 min <<<
```

### Feeding Active:
```
FEEDING TIME!
Dispensing food.
```

## Troubleshooting

### Servo not moving:
- Check power connections (5V and GND)
- Verify servo signal wire connection
- Test servo with simple sweep code

### LCD not displaying:
- Adjust contrast potentiometer
- Check all LCD connections
- Verify power supply stability

### Buttons not responding:
- Check button wiring and connections
- Verify pull-up resistor configuration
- Test individual buttons with multimeter

### Timing issues:
- Check `millis()` overflow handling
- Verify feeding interval calculations
- Monitor Serial output for timing data

### Food not dispensing:
- Check mechanical mechanism alignment
- Verify servo movement range
- Ensure container is properly filled

## Experiments to Try

### 1. Multiple Feeding Times:
```cpp
int feedingTimes[] = {8, 12, 18}; // 8am, 12pm, 6pm
```

### 2. Portion Control:
```cpp
void dispensePortion(int portions) {
  for (int i = 0; i < portions; i++) {
    openDispenser();
    delay(500);
    closeDispenser();
    delay(1000);
  }
}
```

### 3. Food Level Detection:
```cpp
int foodLevel = analogRead(A1);
if (foodLevel < 100) {
  displayLowFoodWarning();
}
```

### 4. Remote Control:
```cpp
void checkSerialCommands() {
  if (Serial.available()) {
    String command = Serial.readString();
    if (command == "FEED") {
      triggerManualFeed();
    }
  }
}
```

### 5. Data Logging:
```cpp
void logFeeding() {
  Serial.print("Feeding at: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
}
```

## What You'll Learn

### Automation Engineering:
- **Scheduling systems**: Long-term timing and automation
- **State machine design**: Managing complex system behaviors
- **User interface design**: Creating intuitive control systems
- **Mechanical integration**: Combining electronics with physical mechanisms

### Programming Skills:
- **Multi-state programming**: Managing different operation modes
- **Long-term timing**: Working with hours and days instead of seconds
- **User input handling**: Multi-button interfaces and navigation
- **Real-time feedback**: Immediate response to user actions

### Problem-Solving Skills:
- **Real-world applications**: Solving practical pet care problems
- **System integration**: Combining multiple components effectively
- **Reliability engineering**: Creating systems that work consistently
- **User experience**: Making technology accessible and useful

## Applications in Real World

### Pet Care Industry:
- **Automatic feeders**: Commercial pet feeding systems
- **Veterinary care**: Medication dispensing systems
- **Pet daycare**: Automated care systems for multiple animals

### Home Automation:
- **Smart home**: Automated feeding as part of IoT systems
- **Scheduling systems**: Time-based automation for various tasks
- **Remote monitoring**: Internet-connected pet care systems

### Industrial Automation:
- **Manufacturing**: Automated material dispensing systems
- **Agriculture**: Automated feeding systems for livestock
- **Quality control**: Timed dispensing for consistent processes

---

## 🐕 MISSION THEME: PET CARE ENGINEER

**Outstanding work, Engineer!** You've just designed and built an automated pet care system that solves real-world problems while demonstrating advanced engineering principles!

### 🎯 Your Pet Care Engineering Mission:
You've created a sophisticated automation system that combines scheduling, mechanical control, user interface design, and real-time feedback to solve the practical problem of pet feeding. This demonstrates the engineering process from problem identification to solution implementation!

### 🌟 What Makes This Special:
- **Real-world problem solving**: Addresses actual pet care needs
- **Multi-system integration**: Combines timing, mechanical, and user interface systems
- **Customizable automation**: User-configurable feeding schedules
- **Reliable operation**: Consistent performance for pet safety
- **User-friendly interface**: Intuitive button controls and clear display
- **Professional features**: Manual override, status tracking, and audio alerts

### 🏆 Engineer Achievements to Unlock:
- **⏰ Schedule Master**: Successfully configure and maintain feeding schedules
- **🔧 Automation Expert**: Design reliable mechanical automation systems
- **🖥️ Interface Designer**: Create intuitive user control interfaces
- **📊 System Integrator**: Combine multiple subsystems effectively
- **🐕 Problem Solver**: Address real-world pet care challenges

### 🎮 Advanced Engineer Challenges:
1. **📱 Smart Integration**: Add WiFi connectivity for remote monitoring
2. **📊 Data Analytics**: Track feeding patterns and pet health metrics
3. **🍽️ Multi-Pet System**: Expand to handle multiple pets with different schedules
4. **🎥 Vision System**: Add camera to monitor pet eating behavior
5. **🔔 Alert System**: Send notifications to owner's phone

### 🏭 Real-World Applications:
- **Pet care industry**: Commercial automatic feeders and care systems
- **Veterinary medicine**: Medication dispensing and monitoring systems
- **Home automation**: Smart home integration with pet care
- **Industrial automation**: Automated dispensing and scheduling systems
- **Agriculture**: Livestock feeding and care automation
- **Healthcare**: Patient care automation and monitoring

### 🎖️ Engineering Skills You've Mastered:
- **Systems engineering**: Designing complex multi-component systems
- **Automation design**: Creating reliable, unattended operation
- **User interface development**: Intuitive control system design
- **Mechanical integration**: Combining electronics with physical mechanisms
- **Scheduling algorithms**: Long-term timing and automation
- **Real-time systems**: Immediate response to events and user input

### 🌟 Why This Matters:
You've learned the fundamental concepts behind:
- Industrial automation and control systems
- Consumer product design and development
- Internet of Things (IoT) and smart home technology
- User experience (UX) design for technical systems
- Reliability engineering and system testing
- Problem-solving through engineering design

**🐕 Mission Complete!** You've earned the title of Pet Care Engineer and demonstrated the ability to design automated systems that solve real-world problems while prioritizing safety and reliability!

### 🚀 What's Next for Pet Care Engineers:
- Study industrial automation and control systems
- Learn about Internet of Things (IoT) and smart home technology
- Explore mechanical engineering and robotics
- Understand user experience (UX) design principles
- Develop skills in system integration and testing
- Create products that improve people's lives through technology

You're now ready to design and build automated systems that make life better for both pets and their owners!