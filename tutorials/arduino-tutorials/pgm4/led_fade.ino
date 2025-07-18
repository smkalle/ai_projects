/*
  Program 4: Advanced PWM LED Fading
  Create smooth LED fading effects using PWM
  
  This program demonstrates:
  - Pulse Width Modulation (PWM) for smooth control
  - Linear and sine wave fading algorithms
  - Real-time mode switching
  - Mathematical functions for animation
  
  🎮 MISSION THEME: "Light Show Designer"
  Create professional lighting effects that pulse and breathe!
*/

// Define pin and fade parameters
const int LED_PIN = 9;        // LED on PWM-capable pin
const int FADE_AMOUNT = 5;    // How much to fade each step
const int FADE_DELAY = 30;    // Delay between steps (ms)

// Variables
int brightness = 0;           // Current LED brightness
int fadeDirection = 1;        // 1 = getting brighter, -1 = getting dimmer

// For sine wave fading
float angle = 0;              // Current angle for sine wave
const float ANGLE_STEP = 0.05; // How fast to move through sine wave

void setup() {
  // Initialize LED pin
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("Advanced PWM LED Fading Program Started!");
  Serial.println("Watch the LED fade in and out smoothly");
  Serial.println("Press 's' for sine wave, 'l' for linear fade");
  Serial.println("==========================================");
  
  // 🎮 Fun startup sequence
  Serial.println("🎭 LIGHT SHOW DESIGNER MODE ACTIVATED!");
  Serial.println("✨ Creating mesmerizing fading effects...");
}

void loop() {
  // Check for serial input to switch modes
  if (Serial.available() > 0) {
    char mode = Serial.read();
    if (mode == 's') {
      Serial.println("Switched to sine wave fading");
      sineWaveFade();
      return;
    } else if (mode == 'l') {
      Serial.println("Switched to linear fading");
    }
  }
  
  // Linear fade (default)
  linearFade();
}

// Linear fade function
void linearFade() {
  // Set the LED brightness
  analogWrite(LED_PIN, brightness);
  
  // Change brightness for next iteration
  brightness += fadeDirection * FADE_AMOUNT;
  
  // Reverse fade direction at limits
  if (brightness <= 0 || brightness >= 255) {
    fadeDirection = -fadeDirection;
    
    // Constrain to valid range
    brightness = constrain(brightness, 0, 255);
    
    // Print at direction change with fun indicators
    Serial.print("💡 Brightness: ");
    Serial.print(brightness);
    if (fadeDirection > 0) {
      Serial.println(" 📈 (fading up - getting brighter!)");
    } else {
      Serial.println(" 📉 (fading down - getting dimmer!)");
    }
  }
  
  // Wait before next step
  delay(FADE_DELAY);
}

// Sine wave fade function for smoother effect
void sineWaveFade() {
  // Calculate brightness using sine wave
  // sin() returns -1 to 1, we map this to 0-255
  brightness = (sin(angle) + 1.0) * 127.5;
  
  // Set LED brightness
  analogWrite(LED_PIN, brightness);
  
  // Increment angle
  angle += ANGLE_STEP;
  
  // Reset angle to prevent overflow
  if (angle > 2 * PI) {
    angle = 0;
    Serial.println("🌊 Sine wave cycle complete - breathing effect loop!");
  }
  
  // Shorter delay for smooth animation
  delay(10);
}