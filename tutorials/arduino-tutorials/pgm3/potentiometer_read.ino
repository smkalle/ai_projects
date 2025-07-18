/*
  Program 3: PWM LED Fade with Potentiometer
  Master analog input and PWM output control
  
  This program demonstrates:
  - Analog input reading (potentiometer)
  - PWM output control (LED brightness)
  - Value mapping and voltage calculation
  - Real-time feedback system
  
  🎮 MISSION THEME: "Dimmer Switch Engineer"
  Build a professional dimmer system that responds to your touch!
*/

// Define pin numbers
const int POT_PIN = A0;    // Potentiometer connected to analog pin A0
const int LED_PIN = 9;     // LED connected to PWM pin 9

// Variables for storing values
int potValue = 0;          // Raw potentiometer reading (0-1023)
int ledBrightness = 0;     // LED brightness value (0-255)
float voltage = 0.0;       // Calculated voltage

void setup() {
  // Initialize LED pin as output
  pinMode(LED_PIN, OUTPUT);
  
  // Analog pins are input by default, no need to set pinMode
  
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("PWM LED Fade Control Program Started!");
  Serial.println("Turn the potentiometer to control LED brightness");
  Serial.println("Watch the real-time values change below:");
  Serial.println("==========================================");
  
  // 🎮 Fun startup sequence
  Serial.println("🎛️ DIMMER SWITCH ENGINEER MODE ACTIVATED!");
  Serial.println("🔧 Turn the knob to control your LED brightness!");
}

void loop() {
  // Read the potentiometer value (0-1023)
  potValue = analogRead(POT_PIN);
  
  // Convert to LED brightness (0-255) for PWM
  ledBrightness = map(potValue, 0, 1023, 0, 255);
  
  // Calculate actual voltage (0-5V)
  voltage = potValue * (5.0 / 1023.0);
  
  // Set LED brightness using PWM
  analogWrite(LED_PIN, ledBrightness);
  
  // Print values to Serial Monitor
  Serial.print("Raw Value: ");
  Serial.print(potValue);
  Serial.print("\t");
  
  Serial.print("Voltage: ");
  Serial.print(voltage);
  Serial.print("V\t");
  
  Serial.print("LED Brightness: ");
  Serial.print(ledBrightness);
  Serial.print(" (");
  Serial.print(map(ledBrightness, 0, 255, 0, 100));
  Serial.print("%)");
  
  // 🎮 Add fun brightness indicator
  Serial.print("\t");
  int percentage = map(ledBrightness, 0, 255, 0, 100);
  if (percentage == 0) {
    Serial.print("💡 OFF");
  } else if (percentage < 25) {
    Serial.print("🌙 DIM");
  } else if (percentage < 50) {
    Serial.print("🔆 LOW");
  } else if (percentage < 75) {
    Serial.print("💡 MEDIUM");
  } else if (percentage < 100) {
    Serial.print("🌟 BRIGHT");
  } else {
    Serial.print("☀️ MAXIMUM");
  }
  Serial.println();
  
  // Small delay for stability
  delay(100);
}