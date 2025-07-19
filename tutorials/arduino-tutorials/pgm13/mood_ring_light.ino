/*
  Project 13: Mood Ring Light
  An RGB LED that changes color based on temperature (like mood rings)
  
  This project reinforces:
  - Analog input (temperature sensor) - from Program 5
  - PWM output (RGB LED) - from Program 3
  - Analog input (potentiometer) - from Program 4
  - Value mapping and scaling - from multiple programs
  - Color theory and RGB mixing
  
  🌈 MISSION PREVIEW: "Color Scientist"
  Master the science of color mixing and create dynamic lighting systems!
  
  Hardware Required:
  - Arduino board
  - RGB LED (common cathode)
  - Temperature sensor (LM35 or TMP36)
  - Potentiometer (for manual color control)
  - 3x 220Ω resistors (for RGB LED)
  - 1x 10KΩ resistor (for potentiometer)
  - Breadboard and jumper wires
*/

// Pin definitions
const int TEMP_PIN = A0;        // Temperature sensor
const int POT_PIN = A1;         // Potentiometer for manual mode
const int RED_PIN = 9;          // RGB LED red pin (PWM)
const int GREEN_PIN = 10;       // RGB LED green pin (PWM)
const int BLUE_PIN = 11;        // RGB LED blue pin (PWM)

// Color and temperature variables
int redValue = 0;               // Red component (0-255)
int greenValue = 0;             // Green component (0-255)
int blueValue = 0;              // Blue component (0-255)
float temperature = 0.0;        // Current temperature
int potValue = 0;               // Potentiometer value
int brightness = 255;           // Overall brightness control

// Mode control
bool autoMode = true;           // Auto mode (temperature) vs manual mode (potentiometer)
unsigned long lastModeCheck = 0;
const unsigned long MODE_CHECK_INTERVAL = 1000;

// Temperature ranges for mood colors (reinforces ranges and mapping)
const float TEMP_COLD = 15.0;    // Cold temperature (°C)
const float TEMP_COOL = 20.0;    // Cool temperature
const float TEMP_WARM = 25.0;    // Warm temperature  
const float TEMP_HOT = 30.0;     // Hot temperature

// Smoothing variables (reinforces averaging from Program 5)
const int NUM_READINGS = 10;
float tempReadings[NUM_READINGS];
int readIndex = 0;
float tempTotal = 0;
float tempAverage = 0;

// Color transition variables (reinforces smooth animations)
int targetRed = 0, targetGreen = 0, targetBlue = 0;
const float TRANSITION_SPEED = 0.1;  // How fast colors change (0-1)

void setup() {
  // Initialize pins (reinforces pinMode from Programs 1, 3, 4)
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  
  // Initialize serial communication (reinforces serial from all programs)
  Serial.begin(9600);
  Serial.println("🌈 MOOD RING LIGHT STARTED!");
  Serial.println("🌈 COLOR SCIENTIST MODE - Master the science of color mixing!");
  Serial.println("Temperature-based color changing system");
  Serial.println("=========================================");
  
  // Initialize temperature readings array (reinforces arrays)
  for (int i = 0; i < NUM_READINGS; i++) {
    tempReadings[i] = 0;
  }
  
  // Startup color show (reinforces RGB control and loops)
  startupColorShow();
  
  Serial.println("🌡️ Auto mode: Colors change with temperature");
  Serial.println("🎨 Manual mode: Use potentiometer to control colors");
}

void loop() {
  // Read sensors (reinforces analog input from Programs 4 & 5)
  readTemperature();
  readPotentiometer();
  
  // Check for mode switching (reinforces user input logic)
  checkModeSwitch();
  
  // Update colors based on current mode
  if (autoMode) {
    updateColorsFromTemperature();
  } else {
    updateColorsFromPotentiometer();
  }
  
  // Apply smooth color transitions (reinforces smooth animations)
  smoothColorTransition();
  
  // Update RGB LED (reinforces PWM from Program 3)
  updateRGBLED();
  
  // Print status information
  printStatus();
  
  delay(50);  // Small delay for stability
}

// Function to read temperature with smoothing (reinforces analog input and averaging)
void readTemperature() {
  // Read raw sensor value
  int sensorValue = analogRead(TEMP_PIN);
  
  // Convert to voltage (reinforces math from Program 5)
  float voltage = sensorValue * (5.0 / 1023.0);
  
  // Convert to temperature (LM35: 10mV per °C, offset 500mV)
  float newTemp = (voltage - 0.5) * 100.0;
  
  // Apply smoothing (reinforces averaging from Program 5)
  tempTotal = tempTotal - tempReadings[readIndex];
  tempReadings[readIndex] = newTemp;
  tempTotal = tempTotal + tempReadings[readIndex];
  readIndex = (readIndex + 1) % NUM_READINGS;
  
  temperature = tempTotal / NUM_READINGS;
}

// Function to read potentiometer (reinforces analog input from Program 4)
void readPotentiometer() {
  potValue = analogRead(POT_PIN);
}

// Function to check for mode switching
void checkModeSwitch() {
  if (millis() - lastModeCheck > MODE_CHECK_INTERVAL) {
    // Check if potentiometer moved significantly (manual mode trigger)
    static int lastPotValue = 0;
    if (abs(potValue - lastPotValue) > 50) {
      autoMode = false;
      Serial.println("🎨 Switched to MANUAL mode (potentiometer control)");
    }
    
    // Auto-switch back to temperature mode after no pot movement
    static int potStableCount = 0;
    if (abs(potValue - lastPotValue) < 10) {
      potStableCount++;
      if (potStableCount > 20) {  // 20 seconds of no movement
        autoMode = true;
        potStableCount = 0;
        Serial.println("🌡️ Switched to AUTO mode (temperature control)");
      }
    } else {
      potStableCount = 0;
    }
    
    lastPotValue = potValue;
    lastModeCheck = millis();
  }
}

// Function to update colors based on temperature (reinforces mapping and color theory)
void updateColorsFromTemperature() {
  // Map temperature to color (reinforces mapping from Program 4)
  if (temperature < TEMP_COLD) {
    // Very cold = Deep blue
    targetRed = 0;
    targetGreen = 0;
    targetBlue = 255;
  }
  else if (temperature < TEMP_COOL) {
    // Cold = Blue to cyan transition
    float ratio = (temperature - TEMP_COLD) / (TEMP_COOL - TEMP_COLD);
    targetRed = 0;
    targetGreen = ratio * 255;
    targetBlue = 255;
  }
  else if (temperature < TEMP_WARM) {
    // Cool = Cyan to green transition
    float ratio = (temperature - TEMP_COOL) / (TEMP_WARM - TEMP_COOL);
    targetRed = 0;
    targetGreen = 255;
    targetBlue = 255 - (ratio * 255);
  }
  else if (temperature < TEMP_HOT) {
    // Warm = Green to yellow transition
    float ratio = (temperature - TEMP_WARM) / (TEMP_HOT - TEMP_WARM);
    targetRed = ratio * 255;
    targetGreen = 255;
    targetBlue = 0;
  }
  else {
    // Hot = Yellow to red transition
    float ratio = min(1.0, (temperature - TEMP_HOT) / 5.0);  // 5°C range for red
    targetRed = 255;
    targetGreen = 255 - (ratio * 255);
    targetBlue = 0;
  }
}

// Function to update colors based on potentiometer (reinforces color wheel theory)
void updateColorsFromPotentiometer() {
  // Map potentiometer to color wheel (reinforces mapping and color theory)
  float hue = map(potValue, 0, 1023, 0, 360);  // 0-360 degrees
  
  // Convert HSV to RGB (reinforces math and color theory)
  float s = 1.0;  // Full saturation
  float v = 1.0;  // Full brightness
  
  float c = v * s;
  float x = c * (1 - abs(fmod(hue / 60.0, 2) - 1));
  float m = v - c;
  
  float r, g, b;
  
  if (hue < 60) {
    r = c; g = x; b = 0;
  } else if (hue < 120) {
    r = x; g = c; b = 0;
  } else if (hue < 180) {
    r = 0; g = c; b = x;
  } else if (hue < 240) {
    r = 0; g = x; b = c;
  } else if (hue < 300) {
    r = x; g = 0; b = c;
  } else {
    r = c; g = 0; b = x;
  }
  
  targetRed = (r + m) * 255;
  targetGreen = (g + m) * 255;
  targetBlue = (b + m) * 255;
}

// Function for smooth color transitions (reinforces smooth animations)
void smoothColorTransition() {
  // Gradually move current colors toward target colors
  redValue += (targetRed - redValue) * TRANSITION_SPEED;
  greenValue += (targetGreen - greenValue) * TRANSITION_SPEED;
  blueValue += (targetBlue - blueValue) * TRANSITION_SPEED;
  
  // Ensure values stay within valid range
  redValue = constrain(redValue, 0, 255);
  greenValue = constrain(greenValue, 0, 255);
  blueValue = constrain(blueValue, 0, 255);
}

// Function to update RGB LED (reinforces PWM from Program 3)
void updateRGBLED() {
  // Apply brightness control (reinforces math operations)
  int finalRed = (redValue * brightness) / 255;
  int finalGreen = (greenValue * brightness) / 255;
  int finalBlue = (blueValue * brightness) / 255;
  
  // Write PWM values to LED pins (reinforces analogWrite from Program 3)
  analogWrite(RED_PIN, finalRed);
  analogWrite(GREEN_PIN, finalGreen);
  analogWrite(BLUE_PIN, finalBlue);
}

// Function to print status information
void printStatus() {
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 1000) {  // Print every second
    Serial.print("🌡️ Temp: ");
    Serial.print(temperature, 1);
    Serial.print("°C | 🎨 Mode: ");
    Serial.print(autoMode ? "AUTO" : "MANUAL");
    Serial.print(" | 🌈 RGB: (");
    Serial.print(redValue);
    Serial.print(", ");
    Serial.print(greenValue);
    Serial.print(", ");
    Serial.print(blueValue);
    Serial.print(") | ");
    
    // Print color name
    printColorName();
    
    Serial.println();
    lastPrint = millis();
  }
}

// Function to print human-readable color name
void printColorName() {
  if (redValue > 200 && greenValue < 100 && blueValue < 100) {
    Serial.print("🔴 RED");
  } else if (redValue > 200 && greenValue > 200 && blueValue < 100) {
    Serial.print("🟡 YELLOW");
  } else if (redValue < 100 && greenValue > 200 && blueValue < 100) {
    Serial.print("🟢 GREEN");
  } else if (redValue < 100 && greenValue > 200 && blueValue > 200) {
    Serial.print("🔵 CYAN");
  } else if (redValue < 100 && greenValue < 100 && blueValue > 200) {
    Serial.print("🔵 BLUE");
  } else if (redValue > 200 && greenValue < 100 && blueValue > 200) {
    Serial.print("🟣 MAGENTA");
  } else if (redValue > 150 && greenValue > 150 && blueValue > 150) {
    Serial.print("⚪ WHITE");
  } else {
    Serial.print("🌈 MIXED");
  }
}

// Function for startup color show (reinforces RGB control and timing)
void startupColorShow() {
  Serial.println("🎭 Welcome to Mood Ring Light!");
  Serial.println("🌈 Color demonstration...");
  
  // Red
  analogWrite(RED_PIN, 255);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 0);
  Serial.println("🔴 Red");
  delay(500);
  
  // Green  
  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 255);
  analogWrite(BLUE_PIN, 0);
  Serial.println("🟢 Green");
  delay(500);
  
  // Blue
  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 255);
  Serial.println("🔵 Blue");
  delay(500);
  
  // White
  analogWrite(RED_PIN, 255);
  analogWrite(GREEN_PIN, 255);
  analogWrite(BLUE_PIN, 255);
  Serial.println("⚪ White");
  delay(500);
  
  // Rainbow transition (reinforces smooth color changes)
  Serial.println("🌈 Rainbow transition...");
  for (int hue = 0; hue < 360; hue += 10) {
    float r, g, b;
    hsvToRgb(hue, 1.0, 1.0, &r, &g, &b);
    analogWrite(RED_PIN, r * 255);
    analogWrite(GREEN_PIN, g * 255);
    analogWrite(BLUE_PIN, b * 255);
    delay(50);
  }
  
  // Turn off
  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 0);
  
  Serial.println("🎨 Ready for mood detection!");
}

// Helper function to convert HSV to RGB (reinforces color theory and math)
void hsvToRgb(float h, float s, float v, float* r, float* g, float* b) {
  float c = v * s;
  float x = c * (1 - abs(fmod(h / 60.0, 2) - 1));
  float m = v - c;
  
  if (h < 60) {
    *r = c; *g = x; *b = 0;
  } else if (h < 120) {
    *r = x; *g = c; *b = 0;
  } else if (h < 180) {
    *r = 0; *g = c; *b = x;
  } else if (h < 240) {
    *r = 0; *g = x; *b = c;
  } else if (h < 300) {
    *r = x; *g = 0; *b = c;
  } else {
    *r = c; *g = 0; *b = x;
  }
  
  *r += m;
  *g += m;
  *b += m;
}

/*
  KEY CONCEPTS REINFORCED:
  
  From Program 3 (PWM LED Fade):
  - analogWrite() for controlling LED brightness
  - PWM principles for smooth control
  - Timing and animation concepts
  
  From Program 4 (Potentiometer Reading):
  - analogRead() for reading analog inputs
  - map() function for scaling values
  - Real-time input processing
  
  From Program 5 (Temperature Sensor):
  - Temperature sensor reading and calibration
  - Data smoothing and averaging
  - Analog to digital conversion
  
  NEW COLOR THEORY CONCEPTS:
  - RGB color mixing (additive color)
  - HSV color space (hue, saturation, value)
  - Color temperature relationships
  - Smooth color transitions
  
  NEW PROGRAMMING CONCEPTS:
  - Multi-mode operation (auto/manual)
  - Color space conversions
  - Smooth interpolation
  - State-based switching
*/