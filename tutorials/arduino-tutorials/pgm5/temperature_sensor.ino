/*
  Program 5: Temperature Sensor Reading
  Read temperature using TMP36 sensor and create a smart climate control system
  
  This program demonstrates reading analog sensors and
  converting raw values to meaningful measurements
  
  🌡️ MISSION PREVIEW: "Weather Station Commander"
  Build a professional weather monitoring system with automatic climate control!
  
  Author: Arduino Learning Series
  Date: 2025
*/

// Define pins and constants
const int TEMP_PIN = A0;      // TMP36 connected to analog pin A0
const int LED_PIN = 13;       // Status LED
const int FAN_PIN = 9;        // Fan control (PWM pin)

// Temperature thresholds
const float COLD_THRESHOLD = 20.0;    // Below this is cold (°C)
const float HOT_THRESHOLD = 25.0;     // Above this is hot (°C)
const float FAN_ON_TEMP = 28.0;       // Turn fan on above this

// Variables
float temperature = 0;        // Current temperature in Celsius
float temperatureF = 0;       // Current temperature in Fahrenheit
int sensorValue = 0;          // Raw sensor reading
float voltage = 0;            // Sensor voltage
int fanSpeed = 0;             // Fan PWM value

// For averaging
const int NUM_READINGS = 10;
int readings[NUM_READINGS];
int readIndex = 0;
int total = 0;
int average = 0;

void setup() {
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("Temperature Sensor Program Started!");
  Serial.println("TMP36 Temperature Monitoring System");
  Serial.println("=====================================");
  Serial.println("🌡️ WEATHER STATION COMMANDER MODE - Ready to monitor climate!");
  
  // Initialize readings array
  for (int i = 0; i < NUM_READINGS; i++) {
    readings[i] = 0;
  }
  
  // Brief startup sequence
  digitalWrite(LED_PIN, HIGH);
  delay(500);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  // Read temperature using averaging
  sensorValue = readTemperatureAverage();
  
  // Convert to voltage (5V reference, 1024 steps)
  voltage = sensorValue * (5.0 / 1023.0);
  
  // Convert voltage to temperature
  // TMP36: 750mV at 25°C, 10mV per degree
  temperature = (voltage - 0.5) * 100.0;
  
  // Convert to Fahrenheit
  temperatureF = (temperature * 9.0 / 5.0) + 32.0;
  
  // Control fan based on temperature
  controlFan(temperature);
  
  // Update status LED
  updateStatusLED(temperature);
  
  // Print readings
  printTemperature();
  
  // Check for alerts
  checkTemperatureAlerts();
  
  // Delay between readings
  delay(1000);
}

// Function to read temperature with averaging
int readTemperatureAverage() {
  // Subtract old reading
  total = total - readings[readIndex];
  
  // Read new value
  readings[readIndex] = analogRead(TEMP_PIN);
  
  // Add to total
  total = total + readings[readIndex];
  
  // Advance index
  readIndex = (readIndex + 1) % NUM_READINGS;
  
  // Calculate average
  average = total / NUM_READINGS;
  
  return average;
}

// Function to control fan speed
void controlFan(float temp) {
  if (temp < FAN_ON_TEMP) {
    fanSpeed = 0;
  } else {
    // Map temperature to fan speed
    // FAN_ON_TEMP to 40°C maps to 0-255 PWM
    fanSpeed = map(temp * 10, FAN_ON_TEMP * 10, 400, 0, 255);
    fanSpeed = constrain(fanSpeed, 0, 255);
  }
  
  analogWrite(FAN_PIN, fanSpeed);
}

// Function to update status LED
void updateStatusLED(float temp) {
  if (temp < COLD_THRESHOLD) {
    // Slow blink for cold
    digitalWrite(LED_PIN, (millis() / 2000) % 2);
  } else if (temp > HOT_THRESHOLD) {
    // Fast blink for hot
    digitalWrite(LED_PIN, (millis() / 500) % 2);
  } else {
    // Steady on for normal
    digitalWrite(LED_PIN, HIGH);
  }
}

// Function to print temperature readings
void printTemperature() {
  Serial.print("🌡️ Raw: ");
  Serial.print(sensorValue);
  Serial.print(" | Voltage: ");
  Serial.print(voltage, 3);
  Serial.print("V | Temp: ");
  Serial.print(temperature, 1);
  Serial.print("°C (");
  Serial.print(temperatureF, 1);
  Serial.print("°F) | 💨 Fan: ");
  Serial.print(map(fanSpeed, 0, 255, 0, 100));
  Serial.print("% ");
  
  // Add temperature status emoji
  if (temperature < COLD_THRESHOLD) {
    Serial.print("❄️ COLD");
  } else if (temperature > HOT_THRESHOLD) {
    Serial.print("🔥 HOT");
  } else {
    Serial.print("😊 PERFECT");
  }
  Serial.println();
}

// Function to check temperature alerts
void checkTemperatureAlerts() {
  static float lastTemp = temperature;
  static unsigned long lastAlertTime = 0;
  
  // Alert every 10 seconds if temperature is extreme
  if (millis() - lastAlertTime > 10000) {
    if (temperature > 35.0) {
      Serial.println("⚠️  ALERT: High temperature detected!");
    } else if (temperature < 10.0) {
      Serial.println("⚠️  ALERT: Low temperature detected!");
    }
    
    // Rapid change detection
    if (abs(temperature - lastTemp) > 5.0) {
      Serial.println("⚠️  ALERT: Rapid temperature change!");
    }
    
    lastAlertTime = millis();
  }
  
  lastTemp = temperature;
}