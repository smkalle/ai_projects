/*
  Program 7: Servo Motor Control
  This program demonstrates controlling a servo motor with a potentiometer
  
  📺 MISSION PREVIEW: "Display Master"
  Create information displays with real-time data visualization!
  
  Hardware Required:
  - Arduino board
  - Servo motor (SG90 or similar)
  - Potentiometer (10K ohm)
  - Jumper wires
  - External power supply (optional, for larger servos)
*/

#include <Servo.h>

// Create servo object
Servo myServo;

// Define pins
const int SERVO_PIN = 9;      // PWM pin for servo
const int POT_PIN = A0;       // Analog pin for potentiometer

// Variables
int potValue = 0;
int servoAngle = 0;

void setup() {
  // Attach the servo to the pin
  myServo.attach(SERVO_PIN);
  
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("Servo Motor Control Program Started!");
  Serial.println("Turn the potentiometer to control servo position");
  Serial.println("📺 DISPLAY MASTER MODE - Ready for visual control!");
  
  // Move servo to initial position
  myServo.write(90);
  delay(1000);
}

void loop() {
  // Read potentiometer value (0-1023)
  potValue = analogRead(POT_PIN);
  
  // Map pot value to servo angle (0-180 degrees)
  servoAngle = map(potValue, 0, 1023, 0, 180);
  
  // Move servo to the mapped position
  myServo.write(servoAngle);
  
  // Print values for debugging
  Serial.print("🎛️ Potentiometer: ");
  Serial.print(potValue);
  Serial.print(" | ⚙️ Servo Angle: ");
  Serial.print(servoAngle);
  Serial.print(" degrees");
  
  // Add visual position indicator
  if (servoAngle < 60) {
    Serial.print(" ⬅️ LEFT");
  } else if (servoAngle > 120) {
    Serial.print(" ➡️ RIGHT");
  } else {
    Serial.print(" ⬆️ CENTER");
  }
  Serial.println();
  
  // Small delay for stability
  delay(15);
}

/*
  Additional Examples:
  
  1. Sweep Motion:
  for(int angle = 0; angle <= 180; angle++) {
    myServo.write(angle);
    delay(15);
  }
  
  2. Button Control:
  if(digitalRead(BUTTON_PIN) == HIGH) {
    myServo.write(180);
  } else {
    myServo.write(0);
  }
*/