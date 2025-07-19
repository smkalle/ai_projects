/*
  Program 10: Simple Data Logger
  This program demonstrates data logging using EEPROM storage with temperature
  and light sensor readings, LCD display, and data retrieval functionality
  
  🎓 MISSION COMPLETION: "Arduino Master"
  You've reached the pinnacle - building complete data acquisition systems!
  
  Hardware Required:
  - Arduino board
  - LM35 temperature sensor
  - LDR (Light Dependent Resistor)
  - 10K ohm resistor (for LDR)
  - 16x2 LCD display
  - Push buttons (3x) for navigation
  - 10K ohm resistors (for button pull-ups)
  - Jumper wires
  - Breadboard
*/

#include <LiquidCrystal.h>
#include <EEPROM.h>

// LCD initialization
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Pin definitions
const int TEMP_PIN = A0;      // Temperature sensor
const int LIGHT_PIN = A1;     // Light sensor (LDR)
const int BUTTON_LOG = 6;     // Manual log button
const int BUTTON_VIEW = 7;    // View data button
const int BUTTON_CLEAR = 8;   // Clear data button
const int STATUS_LED = 13;    // Status LED

// EEPROM settings
const int EEPROM_SIZE = 1024;  // Arduino Uno EEPROM size
const int RECORD_SIZE = 6;     // 2 bytes temp + 2 bytes light + 2 bytes timestamp
const int MAX_RECORDS = (EEPROM_SIZE - 10) / RECORD_SIZE;  // Reserve 10 bytes for metadata
const int RECORD_COUNT_ADDR = 0;  // Address to store record count
const int DATA_START_ADDR = 10;   // Start address for data records

// Variables
float temperature = 0.0;
int lightLevel = 0;
int recordCount = 0;
unsigned long lastLogTime = 0;
const unsigned long LOG_INTERVAL = 30000;  // Log every 30 seconds
bool manualLog = false;

// Button states
bool lastButtonLogState = HIGH;
bool lastButtonViewState = HIGH;
bool lastButtonClearState = HIGH;

// Display modes
enum DisplayMode {
  LIVE_DATA,
  VIEW_DATA,
  SYSTEM_INFO
};
DisplayMode currentMode = LIVE_DATA;
int viewIndex = 0;

void setup() {
  // Initialize pins
  pinMode(BUTTON_LOG, INPUT_PULLUP);
  pinMode(BUTTON_VIEW, INPUT_PULLUP);
  pinMode(BUTTON_CLEAR, INPUT_PULLUP);
  pinMode(STATUS_LED, OUTPUT);
  
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.clear();
  
  // Initialize Serial
  Serial.begin(9600);
  
  // Display startup message
  lcd.setCursor(0, 0);
  lcd.print("Data Logger v1.0");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  Serial.println("Arduino Data Logger Started!");
  Serial.println("🎓 ARDUINO MASTER MODE - Complete data acquisition system!");
  Serial.println("Commands: LOG, VIEW, CLEAR, STATUS");
  Serial.println("========================================");
  
  // Read record count from EEPROM
  recordCount = readRecordCount();
  
  // Validate record count
  if (recordCount > MAX_RECORDS) {
    recordCount = 0;
    saveRecordCount();
  }
  
  delay(2000);
  lcd.clear();
  
  // Display system info
  displaySystemInfo();
  delay(3000);
}

void loop() {
  // Read sensors
  readSensors();
  
  // Check buttons
  checkButtons();
  
  // Handle serial commands
  handleSerialCommands();
  
  // Auto-log data
  checkAutoLog();
  
  // Update display based on current mode
  updateDisplay();
  
  delay(100);
}

void readSensors() {
  // Read temperature (LM35: 10mV/°C)
  int tempReading = analogRead(TEMP_PIN);
  float voltage = tempReading * (5.0 / 1023.0);
  temperature = voltage * 100.0;
  
  // Read light level
  lightLevel = analogRead(LIGHT_PIN);
}

void checkButtons() {
  // Log button
  bool buttonLogState = digitalRead(BUTTON_LOG);
  if (buttonLogState == LOW && lastButtonLogState == HIGH) {
    manualLog = true;
    digitalWrite(STATUS_LED, HIGH);
    delay(100);
    digitalWrite(STATUS_LED, LOW);
  }
  lastButtonLogState = buttonLogState;
  
  // View button
  bool buttonViewState = digitalRead(BUTTON_VIEW);
  if (buttonViewState == LOW && lastButtonViewState == HIGH) {
    if (currentMode == LIVE_DATA) {
      currentMode = VIEW_DATA;
      viewIndex = 0;
    } else if (currentMode == VIEW_DATA) {
      viewIndex = (viewIndex + 1) % recordCount;
      if (viewIndex == 0 && recordCount > 0) {
        currentMode = SYSTEM_INFO;
      }
    } else {
      currentMode = LIVE_DATA;
    }
  }
  lastButtonViewState = buttonViewState;
  
  // Clear button
  bool buttonClearState = digitalRead(BUTTON_CLEAR);
  if (buttonClearState == LOW && lastButtonClearState == HIGH) {
    clearAllData();
  }
  lastButtonClearState = buttonClearState;
}

void handleSerialCommands() {
  if (Serial.available() > 0) {
    String command = Serial.readString();
    command.trim();
    command.toUpperCase();
    
    if (command == "LOG") {
      manualLog = true;
    } else if (command == "VIEW") {
      viewAllData();
    } else if (command == "CLEAR") {
      clearAllData();
    } else if (command == "STATUS") {
      displaySystemInfo();
    } else {
      Serial.println("Unknown command. Use: LOG, VIEW, CLEAR, STATUS");
    }
  }
}

void checkAutoLog() {
  unsigned long currentTime = millis();
  
  if (manualLog || (currentTime - lastLogTime >= LOG_INTERVAL)) {
    logData();
    lastLogTime = currentTime;
    manualLog = false;
  }
}

void logData() {
  if (recordCount >= MAX_RECORDS) {
    Serial.println("EEPROM full! Clear data to continue logging.");
    return;
  }
  
  // Calculate storage address
  int address = DATA_START_ADDR + (recordCount * RECORD_SIZE);
  
  // Convert temperature to integer (multiply by 10 for one decimal place)
  int tempInt = (int)(temperature * 10);
  
  // Get timestamp (seconds since startup)
  unsigned long timestamp = millis() / 1000;
  int timestampInt = (int)(timestamp % 65536);  // Fit in 2 bytes
  
  // Store data in EEPROM
  EEPROM.write(address, highByte(tempInt));
  EEPROM.write(address + 1, lowByte(tempInt));
  EEPROM.write(address + 2, highByte(lightLevel));
  EEPROM.write(address + 3, lowByte(lightLevel));
  EEPROM.write(address + 4, highByte(timestampInt));
  EEPROM.write(address + 5, lowByte(timestampInt));
  
  // Update record count
  recordCount++;
  saveRecordCount();
  
  // Status indication
  digitalWrite(STATUS_LED, HIGH);
  delay(200);
  digitalWrite(STATUS_LED, LOW);
  
  // Serial output
  Serial.print("Data logged: ");
  Serial.print("Temp=");
  Serial.print(temperature, 1);
  Serial.print("°C, Light=");
  Serial.print(lightLevel);
  Serial.print(", Time=");
  Serial.print(timestamp);
  Serial.print("s, Record=");
  Serial.println(recordCount);
}

void updateDisplay() {
  switch (currentMode) {
    case LIVE_DATA:
      displayLiveData();
      break;
    case VIEW_DATA:
      displayStoredData();
      break;
    case SYSTEM_INFO:
      displaySystemInfo();
      break;
  }
}

void displayLiveData() {
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temperature, 1);
  lcd.print("C L:");
  lcd.print(map(lightLevel, 0, 1023, 0, 100));
  lcd.print("%   ");
  
  lcd.setCursor(0, 1);
  lcd.print("Records: ");
  lcd.print(recordCount);
  lcd.print("/");
  lcd.print(MAX_RECORDS);
  lcd.print("  ");
}

void displayStoredData() {
  if (recordCount == 0) {
    lcd.setCursor(0, 0);
    lcd.print("No data stored  ");
    lcd.setCursor(0, 1);
    lcd.print("Press LOG first ");
    return;
  }
  
  // Read stored data
  int address = DATA_START_ADDR + (viewIndex * RECORD_SIZE);
  
  int tempInt = (EEPROM.read(address) << 8) | EEPROM.read(address + 1);
  float storedTemp = tempInt / 10.0;
  
  int storedLight = (EEPROM.read(address + 2) << 8) | EEPROM.read(address + 3);
  
  int timestampInt = (EEPROM.read(address + 4) << 8) | EEPROM.read(address + 5);
  
  // Display data
  lcd.setCursor(0, 0);
  lcd.print("Rec ");
  lcd.print(viewIndex + 1);
  lcd.print(": ");
  lcd.print(storedTemp, 1);
  lcd.print("C     ");
  
  lcd.setCursor(0, 1);
  lcd.print("L:");
  lcd.print(map(storedLight, 0, 1023, 0, 100));
  lcd.print("% T:");
  lcd.print(timestampInt);
  lcd.print("s    ");
}

void displaySystemInfo() {
  lcd.setCursor(0, 0);
  lcd.print("Memory: ");
  lcd.print((recordCount * 100) / MAX_RECORDS);
  lcd.print("%    ");
  
  lcd.setCursor(0, 1);
  lcd.print("Free: ");
  lcd.print(MAX_RECORDS - recordCount);
  lcd.print(" records  ");
}

void viewAllData() {
  Serial.println("\n=== DATA LOG ===");
  Serial.println("Rec# | Temp(°C) | Light(%) | Time(s)");
  Serial.println("-----|----------|----------|--------");
  
  for (int i = 0; i < recordCount; i++) {
    int address = DATA_START_ADDR + (i * RECORD_SIZE);
    
    int tempInt = (EEPROM.read(address) << 8) | EEPROM.read(address + 1);
    float temp = tempInt / 10.0;
    
    int light = (EEPROM.read(address + 2) << 8) | EEPROM.read(address + 3);
    int lightPercent = map(light, 0, 1023, 0, 100);
    
    int timestamp = (EEPROM.read(address + 4) << 8) | EEPROM.read(address + 5);
    
    Serial.print(i + 1);
    Serial.print("    | ");
    Serial.print(temp, 1);
    Serial.print("     | ");
    Serial.print(lightPercent);
    Serial.print("       | ");
    Serial.println(timestamp);
  }
  
  Serial.println("================\n");
}

void clearAllData() {
  recordCount = 0;
  saveRecordCount();
  
  // Clear first few bytes of data area
  for (int i = DATA_START_ADDR; i < DATA_START_ADDR + 50; i++) {
    EEPROM.write(i, 0);
  }
  
  Serial.println("All data cleared!");
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Data Cleared!   ");
  lcd.setCursor(0, 1);
  lcd.print("Memory Reset    ");
  delay(2000);
}

int readRecordCount() {
  return (EEPROM.read(RECORD_COUNT_ADDR) << 8) | EEPROM.read(RECORD_COUNT_ADDR + 1);
}

void saveRecordCount() {
  EEPROM.write(RECORD_COUNT_ADDR, highByte(recordCount));
  EEPROM.write(RECORD_COUNT_ADDR + 1, lowByte(recordCount));
}

/*
  Additional Features:
  
  1. Real-time Clock integration:
  #include <RTClib.h>
  RTC_DS1307 rtc;
  
  2. SD Card logging:
  #include <SD.h>
  File dataFile = SD.open("datalog.txt", FILE_WRITE);
  
  3. Wireless data transmission:
  #include <WiFi.h>
  // Send data to web server
  
  4. Data compression:
  // Store differences instead of absolute values
  
  5. Circular buffer:
  // Overwrite oldest data when full
*/