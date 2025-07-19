/*
  Program 8: LCD Display
  This program demonstrates displaying text and sensor data on a 16x2 LCD
  
  📏 MISSION PREVIEW: "Distance Detective"
  Build advanced sensing systems with precision distance measurement!
  
  Hardware Required:
  - Arduino board
  - 16x2 LCD display (HD44780 compatible)
  - 10K ohm potentiometer (for contrast)
  - Temperature sensor (LM35 or TMP36)
  - Jumper wires
  - Breadboard
*/

#include <LiquidCrystal.h>

// Initialize LCD library with interface pins
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Define pins
const int TEMP_PIN = A0;     // Temperature sensor pin
const int CONTRAST_PIN = A1; // Optional: contrast control

// Variables
float temperature = 0.0;
float voltage = 0.0;
unsigned long previousMillis = 0;
const long interval = 1000;  // Update every second

void setup() {
  // Set up LCD's number of columns and rows
  lcd.begin(16, 2);
  
  // Initialize serial communication
  Serial.begin(9600);
  
  // Display startup message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Arduino LCD Demo");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  Serial.println("LCD Display Program Started!");
  Serial.println("📏 DISTANCE DETECTIVE MODE - Ready for precision sensing!");
  
  // Wait for 2 seconds
  delay(2000);
  
  // Clear the display
  lcd.clear();
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Update display every second
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    // Read temperature sensor
    int sensorValue = analogRead(TEMP_PIN);
    voltage = sensorValue * (5.0 / 1023.0);
    
    // Convert to temperature (for LM35: 10mV/°C)
    temperature = voltage * 100.0;
    
    // Display temperature on LCD
    lcd.setCursor(0, 0);
    lcd.print("Temperature:");
    
    lcd.setCursor(0, 1);
    lcd.print(temperature, 1);
    lcd.print(" C  ");
    
    // Display voltage
    lcd.setCursor(8, 1);
    lcd.print(voltage, 2);
    lcd.print("V");
    
    // Print to serial monitor
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C | Voltage: ");
    Serial.print(voltage);
    Serial.println(" V");
  }
  
  // Check for scrolling text demo
  static unsigned long scrollTimer = 0;
  static int scrollPosition = 0;
  static bool showScrollDemo = false;
  
  // Every 10 seconds, show scrolling demo
  if (currentMillis - scrollTimer >= 10000) {
    scrollTimer = currentMillis;
    showScrollDemo = !showScrollDemo;
    
    if (showScrollDemo) {
      scrollingTextDemo();
    }
  }
}

void scrollingTextDemo() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Scrolling Text");
  
  String message = "    This is a long scrolling message demonstration!    ";
  
  for (int i = 0; i < message.length() - 15; i++) {
    lcd.setCursor(0, 1);
    lcd.print(message.substring(i, i + 16));
    delay(300);
  }
  
  delay(1000);
  lcd.clear();
}

/*
  Additional LCD Functions:
  
  1. Custom Characters:
  byte heart[8] = {
    0b00000,
    0b01010,
    0b11111,
    0b11111,
    0b11111,
    0b01110,
    0b00100,
    0b00000
  };
  lcd.createChar(0, heart);
  lcd.write(byte(0));
  
  2. Blinking Cursor:
  lcd.blink();
  lcd.noBlink();
  
  3. Cursor Control:
  lcd.cursor();
  lcd.noCursor();
  
  4. Display Control:
  lcd.display();
  lcd.noDisplay();
*/