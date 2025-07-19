/*
  Program 6: Advanced Servo Motor Control
  Control servo position with potentiometer and serial commands
  
  This program demonstrates servo motor control using the
  Servo library with multiple input methods
  
  🤖 MISSION PREVIEW: "Robotics Engineer"
  Build precise robotic movements with smooth servo control!
  
  Author: Arduino Learning Series
  Date: 2025
*/

#include <Servo.h>

// Create servo object
Servo myServo;

// Define pins
const int SERVO_PIN = 9;      // Servo control pin
const int POT_PIN = A0;       // Potentiometer for manual control
const int BUTTON_PIN = 2;     // Button for sweep mode

// Variables
int potValue = 0;             // Potentiometer reading
int servoAngle = 90;          // Current servo angle
int targetAngle = 90;         // Target angle for smooth movement
boolean sweepMode = false;    // Sweep mode flag
int sweepDirection = 1;       // 1 or -1 for sweep direction
unsigned long lastSweepTime = 0;
const int SWEEP_DELAY = 15;   // Delay between sweep steps

// Smooth movement variables
const float SMOOTH_FACTOR = 0.1;  // How quickly to move (0-1)

// Button debouncing
int buttonState = HIGH;
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY = 50;

void setup() {
  // Attach servo to pin
  myServo.attach(SERVO_PIN);
  
  // Initialize servo to center position
  myServo.write(90);
  
  // Setup button with pull-up
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  
  // Initialize serial
  Serial.begin(9600);
  Serial.println("Advanced Servo Control Program Started!");
  Serial.println("=====================================");
  Serial.println("🤖 ROBOTICS ENGINEER MODE - Ready for precise control!");
  Serial.println("Controls:");
  Serial.println("- Turn potentiometer to control servo");
  Serial.println("- Press button to toggle sweep mode");
  Serial.println("- Send angle (0-180) via serial");
  Serial.println("- Send 'c' to center, 's' for sweep");
  Serial.println("=====================================");
}

void loop() {
  // Check for serial commands
  checkSerialCommands();
  
  // Check button for sweep mode toggle
  checkButton();
  
  // Handle different modes
  if (sweepMode) {
    performSweep();
  } else {
    // Read potentiometer for manual control
    potValue = analogRead(POT_PIN);
    targetAngle = map(potValue, 0, 1023, 0, 180);
  }
  
  // Smooth movement to target angle
  smoothMove();
  
  // Small delay
  delay(10);
}

// Function to check serial commands
void checkSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    // Check for special commands
    if (command == "c" || command == "C") {
      targetAngle = 90;
      sweepMode = false;
      Serial.println("Centering servo at 90°");
    } 
    else if (command == "s" || command == "S") {
      sweepMode = !sweepMode;
      Serial.print("Sweep mode: ");
      Serial.println(sweepMode ? "ON" : "OFF");
    }
    else {
      // Try to parse as angle
      int angle = command.toInt();
      if (angle >= 0 && angle <= 180) {
        targetAngle = angle;
        sweepMode = false;
        Serial.print("Moving to angle: ");
        Serial.println(angle);
      } else {
        Serial.println("Invalid command. Enter 0-180, 'c' for center, 's' for sweep");
      }
    }
  }
}

// Function to check button state with debouncing
void checkButton() {
  int reading = digitalRead(BUTTON_PIN);
  
  // Check if button state changed
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  // Check if enough time has passed
  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    // If button state has changed
    if (reading != buttonState) {
      buttonState = reading;
      
      // Toggle sweep mode on button press (LOW when pressed)
      if (buttonState == LOW) {
        sweepMode = !sweepMode;
        Serial.print("Button pressed - Sweep mode: ");
        Serial.println(sweepMode ? "ON" : "OFF");
      }
    }
  }
  
  lastButtonState = reading;
}

// Function to perform sweep motion
void performSweep() {
  if (millis() - lastSweepTime > SWEEP_DELAY) {
    targetAngle += sweepDirection;
    
    // Reverse direction at limits
    if (targetAngle <= 0 || targetAngle >= 180) {
      sweepDirection = -sweepDirection;
      targetAngle = constrain(targetAngle, 0, 180);
    }
    
    lastSweepTime = millis();
  }
}

// Function for smooth servo movement
void smoothMove() {
  // Calculate difference
  float diff = targetAngle - servoAngle;
  
  // Only move if difference is significant
  if (abs(diff) > 0.5) {
    // Apply smoothing
    servoAngle += diff * SMOOTH_FACTOR;
    
    // Write to servo
    myServo.write(int(servoAngle));
    
    // Print status occasionally
    static unsigned long lastPrintTime = 0;
    if (millis() - lastPrintTime > 500) {
      Serial.print("🤖 Servo angle: ");
      Serial.print(int(servoAngle));
      Serial.print("° | Target: ");
      Serial.print(targetAngle);
      Serial.print("° | Mode: ");
      Serial.print(sweepMode ? "🔄 SWEEP" : "🎛️ MANUAL");
      
      // Add precision indicator
      if (abs(targetAngle - servoAngle) < 2) {
        Serial.print(" ✅ PRECISE");
      } else {
        Serial.print(" ⚡ MOVING");
      }
      Serial.println();
      lastPrintTime = millis();
    }
  }
}