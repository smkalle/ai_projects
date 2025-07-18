/*
  Program 7: Ultrasonic Distance Sensor
  Measure distance using HC-SR04 ultrasonic sensor
  
  This program demonstrates ultrasonic distance measurement
  with visual and audio feedback
  Author: Arduino Learning Series
  Date: 2025
*/

// Define pins
const int TRIG_PIN = 7;       // Trigger pin
const int ECHO_PIN = 6;       // Echo pin
const int LED_RED = 13;       // Red LED for close objects
const int LED_YELLOW = 12;    // Yellow LED for medium distance
const int LED_GREEN = 11;     // Green LED for far objects
const int BUZZER_PIN = 10;    // Buzzer for audio feedback

// Distance thresholds (in cm)
const int CLOSE_DISTANCE = 10;
const int MEDIUM_DISTANCE = 30;
const int MAX_DISTANCE = 400;     // Maximum sensor range

// Variables
long duration;                    // Time for echo
float distanceCm;                 // Distance in centimeters
float distanceInch;               // Distance in inches
float soundSpeed = 0.0343;        // Speed of sound in cm/µs at 20°C

// For averaging
const int NUM_READINGS = 5;
float readings[NUM_READINGS];
int readIndex = 0;
float total = 0;
float average = 0;

// For parking sensor mode
boolean parkingMode = false;
unsigned long lastBeepTime = 0;

void setup() {
  // Configure pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize serial
  Serial.begin(9600);
  Serial.println("Ultrasonic Distance Sensor Program Started!");
  Serial.println("==========================================");
  Serial.println("HC-SR04 Ultrasonic Sensor");
  Serial.println("Range: 2cm - 400cm");
  Serial.println("Press 'p' for parking mode, 'm' for measurement mode");
  Serial.println("==========================================");
  
  // Initialize readings array
  for (int i = 0; i < NUM_READINGS; i++) {
    readings[i] = 0;
  }
  
  // LED test sequence
  ledStartupSequence();
}

void loop() {
  // Check for serial commands
  checkSerialCommands();
  
  // Measure distance
  distanceCm = measureDistance();
  
  // Convert to inches
  distanceInch = distanceCm / 2.54;
  
  // Update LEDs based on distance
  updateLEDs(distanceCm);
  
  // Handle different modes
  if (parkingMode) {
    parkingSensorMode(distanceCm);
  } else {
    // Normal measurement mode - print every 500ms
    static unsigned long lastPrintTime = 0;
    if (millis() - lastPrintTime > 500) {
      printDistance();
      lastPrintTime = millis();
    }
  }
  
  // Small delay between measurements
  delay(50);
}

// Function to measure distance
float measureDistance() {
  // Clear trigger pin
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Send 10µs pulse to trigger
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Read echo pin - time until echo received
  duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
  
  // Calculate distance
  // Distance = (Time × Speed of Sound) / 2
  float distance = duration * soundSpeed / 2;
  
  // Check for out of range
  if (duration == 0 || distance > MAX_DISTANCE) {
    distance = MAX_DISTANCE;
  }
  
  // Add to averaging array
  total = total - readings[readIndex];
  readings[readIndex] = distance;
  total = total + readings[readIndex];
  readIndex = (readIndex + 1) % NUM_READINGS;
  average = total / NUM_READINGS;
  
  return average;
}

// Function to update LEDs
void updateLEDs(float distance) {
  // Turn off all LEDs first
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, LOW);
  
  // Light appropriate LED
  if (distance < CLOSE_DISTANCE) {
    digitalWrite(LED_RED, HIGH);
  } else if (distance < MEDIUM_DISTANCE) {
    digitalWrite(LED_YELLOW, HIGH);
  } else {
    digitalWrite(LED_GREEN, HIGH);
  }
}

// Function for parking sensor mode
void parkingSensorMode(float distance) {
  int beepInterval;
  
  if (distance < CLOSE_DISTANCE) {
    // Very close - continuous beep
    tone(BUZZER_PIN, 1000);
  } else if (distance < MEDIUM_DISTANCE) {
    // Calculate beep interval based on distance
    beepInterval = map(distance, CLOSE_DISTANCE, MEDIUM_DISTANCE, 100, 500);
    
    // Beep at calculated interval
    if (millis() - lastBeepTime > beepInterval) {
      tone(BUZZER_PIN, 1000, 50);
      lastBeepTime = millis();
    }
  } else {
    // Far away - no beep
    noTone(BUZZER_PIN);
  }
  
  // Print distance occasionally
  static unsigned long lastPrintTime = 0;
  if (millis() - lastPrintTime > 200) {
    Serial.print("Parking Distance: ");
    Serial.print(distanceCm, 1);
    Serial.println(" cm");
    lastPrintTime = millis();
  }
}

// Function to print distance
void printDistance() {
  Serial.print("Distance: ");
  Serial.print(distanceCm, 1);
  Serial.print(" cm (");
  Serial.print(distanceInch, 1);
  Serial.print(" inches) | ");
  
  // Add visual bar graph
  int barLength = map(distanceCm, 0, 100, 0, 20);
  barLength = constrain(barLength, 0, 20);
  
  Serial.print("[");
  for (int i = 0; i < 20; i++) {
    if (i < barLength) {
      Serial.print("=");
    } else {
      Serial.print(" ");
    }
  }
  Serial.print("] ");
  
  // Add status
  if (distanceCm < CLOSE_DISTANCE) {
    Serial.println("CLOSE!");
  } else if (distanceCm < MEDIUM_DISTANCE) {
    Serial.println("MEDIUM");
  } else if (distanceCm >= MAX_DISTANCE) {
    Serial.println("OUT OF RANGE");
  } else {
    Serial.println("FAR");
  }
}

// Function to check serial commands
void checkSerialCommands() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    switch (command) {
      case 'p':
      case 'P':
        parkingMode = true;
        Serial.println("Parking sensor mode activated!");
        break;
        
      case 'm':
      case 'M':
        parkingMode = false;
        noTone(BUZZER_PIN);
        Serial.println("Measurement mode activated!");
        break;
        
      case 'c':
      case 'C':
        // Calibrate temperature
        Serial.println("Enter temperature in Celsius:");
        while (!Serial.available()) delay(10);
        float temp = Serial.parseFloat();
        soundSpeed = 0.0331 + 0.0006 * temp;
        Serial.print("Sound speed adjusted for ");
        Serial.print(temp);
        Serial.println("°C");
        break;
    }
  }
}

// LED startup sequence
void ledStartupSequence() {
  digitalWrite(LED_RED, HIGH);
  delay(200);
  digitalWrite(LED_RED, LOW);
  digitalWrite(LED_YELLOW, HIGH);
  delay(200);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_GREEN, HIGH);
  delay(200);
  digitalWrite(LED_GREEN, LOW);
  tone(BUZZER_PIN, 1000, 100);
}