/*
  Program 9: Ultrasonic Distance Sensor
  This program demonstrates measuring distance using HC-SR04 ultrasonic sensor
  with multiple display modes and proximity alerts
  
  📊 MISSION PREVIEW: "Data Scientist"
  Master data collection, storage, and analysis with professional logging systems!
  
  Hardware Required:
  - Arduino board
  - HC-SR04 ultrasonic sensor
  - LED (for proximity alert)
  - Buzzer (optional)
  - 16x2 LCD display (optional)
  - 220 ohm resistor (for LED)
  - Jumper wires
  - Breadboard
*/

#include <LiquidCrystal.h>

// Pin definitions
const int TRIG_PIN = 7;      // Trigger pin
const int ECHO_PIN = 8;      // Echo pin
const int LED_PIN = 13;      // Alert LED
const int BUZZER_PIN = 6;    // Buzzer (optional)

// LCD pins (optional)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Variables
long duration;
float distance;
float averageDistance;
const int numReadings = 5;
float readings[numReadings];
int readIndex = 0;
float total = 0;

// Alert settings
const float ALERT_DISTANCE = 10.0;  // Alert when object is within 10cm
const float MAX_DISTANCE = 400.0;   // Maximum reliable distance (cm)

// Timing variables
unsigned long previousMillis = 0;
const long interval = 100;  // Read every 100ms

void setup() {
  // Initialize pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize LCD (comment out if not using LCD)
  lcd.begin(16, 2);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Distance Sensor");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  // Initialize smoothing array
  for (int i = 0; i < numReadings; i++) {
    readings[i] = 0;
  }
  
  Serial.println("HC-SR04 Distance Sensor Program Started!");
  Serial.println("📊 DATA SCIENTIST MODE - Ready for advanced sensing!");
  Serial.println("Distance | Status | Alert");
  Serial.println("---------|--------|------");
  
  delay(2000);
  lcd.clear();
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Read sensor every 100ms
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    // Measure distance
    distance = measureDistance();
    
    // Smooth the readings
    distance = smoothDistance(distance);
    
    // Display results
    displayResults();
    
    // Check for proximity alert
    checkProximityAlert();
  }
}

float measureDistance() {
  // Clear the trigger pin
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Send 10 microsecond pulse
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Read the echo pin
  duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30ms timeout
  
  // Calculate distance (speed of sound = 343 m/s)
  // Distance = (duration * 0.034) / 2
  float dist = (duration * 0.034) / 2;
  
  // Return valid distance or previous reading if out of range
  if (dist > 0 && dist <= MAX_DISTANCE) {
    return dist;
  } else {
    return averageDistance;  // Return previous average if invalid
  }
}

float smoothDistance(float newDistance) {
  // Remove oldest reading
  total -= readings[readIndex];
  
  // Add new reading
  readings[readIndex] = newDistance;
  total += readings[readIndex];
  
  // Move to next position
  readIndex = (readIndex + 1) % numReadings;
  
  // Calculate average
  averageDistance = total / numReadings;
  
  return averageDistance;
}

void displayResults() {
  // Serial Monitor output
  Serial.print(distance, 1);
  Serial.print(" cm | ");
  
  // Determine status
  String status = "";
  if (distance < 5) {
    status = "TOO CLOSE";
  } else if (distance < 20) {
    status = "NEAR";
  } else if (distance < 50) {
    status = "MEDIUM";
  } else if (distance < 100) {
    status = "FAR";
  } else {
    status = "VERY FAR";
  }
  
  Serial.print(status);
  Serial.print(" | ");
  
  if (distance <= ALERT_DISTANCE) {
    Serial.println("ALERT!");
  } else {
    Serial.println("OK");
  }
  
  // LCD Display (comment out if not using LCD)
  lcd.setCursor(0, 0);
  lcd.print("Distance: ");
  lcd.print(distance, 1);
  lcd.print(" cm  ");
  
  lcd.setCursor(0, 1);
  lcd.print(status);
  lcd.print("          ");  // Clear remaining characters
}

void checkProximityAlert() {
  if (distance <= ALERT_DISTANCE && distance > 0) {
    // Activate alert
    digitalWrite(LED_PIN, HIGH);
    
    // Buzzer alert pattern
    tone(BUZZER_PIN, 1000, 100);  // 1000Hz for 100ms
    
    // Visual indicator on LCD
    lcd.setCursor(14, 0);
    lcd.print("!!");
    
  } else {
    // Deactivate alert
    digitalWrite(LED_PIN, LOW);
    noTone(BUZZER_PIN);
    
    // Clear visual indicator
    lcd.setCursor(14, 0);
    lcd.print("  ");
  }
}

/*
  Additional Features:
  
  1. Distance-based LED brightness:
  int brightness = map(distance, 0, 50, 255, 0);
  analogWrite(LED_PIN, brightness);
  
  2. Multi-zone detection:
  void checkZones() {
    if (distance < 10) {
      // Zone 1: Red alert
    } else if (distance < 30) {
      // Zone 2: Yellow warning
    } else {
      // Zone 3: Green safe
    }
  }
  
  3. Distance logging:
  void logDistance() {
    Serial.print(millis());
    Serial.print(",");
    Serial.println(distance);
  }
  
  4. Motion detection:
  static float lastDistance = 0;
  if (abs(distance - lastDistance) > 5) {
    Serial.println("Motion detected!");
  }
  lastDistance = distance;
*/