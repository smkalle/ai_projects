/*
  Project 15: Secret Knock Detector
  A security system that detects specific knock patterns to unlock LED "door"
  
  This project reinforces:
  - Analog input (vibration sensor) - from Program 4
  - Digital output (LEDs) - from Program 1
  - LCD display - from Program 8
  - Timing and pattern recognition - from Program 11
  - Arrays and pattern matching - from multiple programs
  
  🔒 MISSION PREVIEW: "Security Code Breaker"
  Master pattern recognition and security systems to protect important secrets!
  
  Hardware Required:
  - Arduino board
  - Piezo vibration sensor (or piezo buzzer as sensor)
  - 16x2 LCD display
  - 2x LEDs (Red = locked, Green = unlocked)
  - Push button (for programming new patterns)
  - Buzzer (for audio feedback)
  - 2x 220Ω resistors (for LEDs)
  - 1x 1MΩ resistor (for piezo sensor)
  - Breadboard and jumper wires
*/

#include <LiquidCrystal.h>

// Initialize LCD (reinforces LCD from Program 8)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Pin definitions
const int PIEZO_PIN = A0;       // Piezo sensor for knock detection
const int RED_LED_PIN = 9;      // Red LED (locked status)
const int GREEN_LED_PIN = 10;   // Green LED (unlocked status)
const int BUZZER_PIN = 6;       // Buzzer for audio feedback
const int PROGRAM_BUTTON = 7;   // Button to program new knock pattern

// Knock detection variables (reinforces analog input from Program 4)
const int KNOCK_THRESHOLD = 100;    // Minimum knock strength
const int KNOCK_TIMEOUT = 1500;     // Max time between knocks (ms)
const int KNOCK_COMPLETE_TIME = 2000; // Time to wait after last knock
const int MAX_KNOCKS = 10;          // Maximum knocks in pattern

// Pattern storage (reinforces arrays from multiple programs)
int secretPattern[MAX_KNOCKS];      // The secret knock pattern
int detectedPattern[MAX_KNOCKS];    // Currently detected pattern
int secretPatternLength = 0;        // Length of secret pattern
int detectedPatternLength = 0;      // Length of detected pattern

// Timing variables (reinforces timing concepts from multiple programs)
unsigned long lastKnockTime = 0;
unsigned long patternStartTime = 0;
unsigned long unlockTime = 0;
const unsigned long UNLOCK_DURATION = 5000;  // Stay unlocked for 5 seconds

// System state variables (reinforces state management)
enum SystemState {
  LOCKED,
  LISTENING,
  PROGRAMMING,
  UNLOCKED,
  PATTERN_MATCH
};
SystemState currentState = LOCKED;

// Default secret pattern (reinforces arrays and patterns)
int defaultPattern[] = {300, 150, 300, 150, 300};  // Long-short-long-short-long
int defaultPatternLength = 5;

// Button handling (reinforces button concepts from Program 2)
bool lastButtonState = HIGH;
unsigned long lastButtonTime = 0;
const unsigned long BUTTON_DEBOUNCE = 200;

// Pattern matching variables
const int PATTERN_TOLERANCE = 100;   // Tolerance for timing differences (ms)
int attempts = 0;                    // Track failed attempts
const int MAX_ATTEMPTS = 3;          // Lock out after 3 failed attempts
unsigned long lockoutTime = 0;
const unsigned long LOCKOUT_DURATION = 10000;  // 10 second lockout

// Display variables (reinforces display concepts from Program 8)
unsigned long lastDisplayUpdate = 0;
const unsigned long DISPLAY_UPDATE_INTERVAL = 100;

void setup() {
  // Initialize pins (reinforces pinMode from multiple programs)
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(PROGRAM_BUTTON, INPUT_PULLUP);
  
  // Initialize LCD (reinforces LCD setup from Program 8)
  lcd.begin(16, 2);
  lcd.clear();
  
  // Initialize serial communication (reinforces serial from all programs)
  Serial.begin(9600);
  Serial.println("🔒 SECRET KNOCK DETECTOR STARTED!");
  Serial.println("🔒 SECURITY CODE BREAKER MODE - Master pattern recognition!");
  Serial.println("Advanced security system with pattern recognition");
  Serial.println("===============================================");
  
  // Load default pattern (reinforces array operations)
  loadDefaultPattern();
  
  // Set initial state
  currentState = LOCKED;
  digitalWrite(RED_LED_PIN, HIGH);   // Show locked status
  digitalWrite(GREEN_LED_PIN, LOW);
  
  // Startup sequence (reinforces LED and sound control)
  startupSequence();
  
  Serial.println("🔐 System locked and ready");
  Serial.println("🚪 Knock the secret pattern to unlock");
}

void loop() {
  // Handle button for programming mode (reinforces button handling)
  handleProgramButton();
  
  // Check for knock input (reinforces analog input from Program 4)
  checkForKnock();
  
  // Handle different system states
  switch (currentState) {
    case LOCKED:
      handleLockedState();
      break;
    case LISTENING:
      handleListeningState();
      break;
    case PROGRAMMING:
      handleProgrammingState();
      break;
    case UNLOCKED:
      handleUnlockedState();
      break;
    case PATTERN_MATCH:
      handlePatternMatch();
      break;
  }
  
  // Update display (reinforces display updates from Program 8)
  updateDisplay();
  
  // Check for lockout expiration
  if (currentState == LOCKED && attempts >= MAX_ATTEMPTS) {
    if (millis() - lockoutTime > LOCKOUT_DURATION) {
      attempts = 0;
      Serial.println("🔓 Lockout expired, system ready");
    }
  }
}

// Function to handle program button (reinforces button concepts)
void handleProgramButton() {
  bool buttonPressed = digitalRead(PROGRAM_BUTTON);
  
  if (buttonPressed == LOW && lastButtonState == HIGH && 
      millis() - lastButtonTime > BUTTON_DEBOUNCE) {
    
    if (currentState == LOCKED || currentState == UNLOCKED) {
      enterProgrammingMode();
    } else if (currentState == PROGRAMMING) {
      exitProgrammingMode();
    }
    
    lastButtonTime = millis();
  }
  
  lastButtonState = buttonPressed;
}

// Function to check for knock input (reinforces analog input)
void checkForKnock() {
  int sensorValue = analogRead(PIEZO_PIN);
  
  // Check if knock detected (reinforces threshold detection)
  if (sensorValue > KNOCK_THRESHOLD) {
    unsigned long currentTime = millis();
    
    // Calculate time since last knock
    unsigned long timeSinceLastKnock = currentTime - lastKnockTime;
    
    // Record knock timing
    if (currentState == LISTENING || currentState == PROGRAMMING) {
      recordKnock(timeSinceLastKnock);
    }
    
    lastKnockTime = currentTime;
    
    // Visual feedback (reinforces LED control from Program 1)
    digitalWrite(RED_LED_PIN, HIGH);
    delay(50);
    digitalWrite(RED_LED_PIN, currentState == LOCKED ? HIGH : LOW);
    
    // Audio feedback (reinforces buzzer control)
    tone(BUZZER_PIN, 400, 100);
    
    Serial.print("🔊 Knock detected! Strength: ");
    Serial.print(sensorValue);
    Serial.print(", Time since last: ");
    Serial.print(timeSinceLastKnock);
    Serial.println("ms");
  }
}

// Function to record knock timing
void recordKnock(unsigned long timeSinceLastKnock) {
  if (currentState == LISTENING) {
    // Record knock in detected pattern
    if (detectedPatternLength == 0) {
      // First knock - start pattern
      patternStartTime = millis();
      detectedPatternLength = 1;
      detectedPattern[0] = 0;  // First knock has no delay
    } else if (detectedPatternLength < MAX_KNOCKS) {
      // Subsequent knocks - record timing
      detectedPattern[detectedPatternLength] = timeSinceLastKnock;
      detectedPatternLength++;
    }
  } else if (currentState == PROGRAMMING) {
    // Record knock in secret pattern
    if (secretPatternLength == 0) {
      // First knock - start pattern
      secretPatternLength = 1;
      secretPattern[0] = 0;  // First knock has no delay
    } else if (secretPatternLength < MAX_KNOCKS) {
      // Subsequent knocks - record timing
      secretPattern[secretPatternLength] = timeSinceLastKnock;
      secretPatternLength++;
    }
  }
}

// Function to handle locked state
void handleLockedState() {
  // Check if system is in lockout
  if (attempts >= MAX_ATTEMPTS) {
    return;  // Don't listen during lockout
  }
  
  // Check for first knock to start listening
  if (millis() - lastKnockTime < 100) {  // Just detected a knock
    currentState = LISTENING;
    detectedPatternLength = 0;
    Serial.println("🎧 Started listening for pattern...");
  }
}

// Function to handle listening state
void handleListeningState() {
  // Check for pattern completion timeout
  if (millis() - lastKnockTime > KNOCK_COMPLETE_TIME && detectedPatternLength > 0) {
    currentState = PATTERN_MATCH;
    Serial.println("🔍 Pattern complete, checking match...");
  }
  
  // Check for pattern timeout
  if (millis() - lastKnockTime > KNOCK_TIMEOUT && detectedPatternLength > 0) {
    Serial.println("⏰ Pattern timeout, resetting...");
    currentState = LOCKED;
    detectedPatternLength = 0;
  }
}

// Function to handle programming state
void handleProgrammingState() {
  // Check for pattern completion timeout
  if (millis() - lastKnockTime > KNOCK_COMPLETE_TIME && secretPatternLength > 0) {
    exitProgrammingMode();
  }
}

// Function to handle unlocked state
void handleUnlockedState() {
  // Check if unlock time has expired
  if (millis() - unlockTime > UNLOCK_DURATION) {
    currentState = LOCKED;
    digitalWrite(RED_LED_PIN, HIGH);
    digitalWrite(GREEN_LED_PIN, LOW);
    Serial.println("🔒 System automatically locked");
  }
}

// Function to handle pattern matching
void handlePatternMatch() {
  bool patternMatches = comparePatterns();
  
  if (patternMatches) {
    // Pattern matches - unlock system
    currentState = UNLOCKED;
    unlockTime = millis();
    attempts = 0;  // Reset failed attempts
    
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, HIGH);
    
    playUnlockSound();
    Serial.println("✅ PATTERN MATCH! System unlocked!");
  } else {
    // Pattern doesn't match - increment attempts
    attempts++;
    currentState = LOCKED;
    
    playFailSound();
    Serial.print("❌ Pattern mismatch! Attempt ");
    Serial.print(attempts);
    Serial.print(" of ");
    Serial.println(MAX_ATTEMPTS);
    
    if (attempts >= MAX_ATTEMPTS) {
      lockoutTime = millis();
      Serial.println("🚨 TOO MANY FAILED ATTEMPTS! System locked for 10 seconds");
    }
  }
  
  // Reset detected pattern
  detectedPatternLength = 0;
}

// Function to compare detected pattern with secret pattern (reinforces arrays and logic)
bool comparePatterns() {
  // Check if pattern lengths match
  if (detectedPatternLength != secretPatternLength) {
    Serial.println("📏 Pattern length mismatch");
    return false;
  }
  
  // Compare each timing in the pattern
  for (int i = 1; i < secretPatternLength; i++) {  // Start from 1 (skip first knock)
    int secretTiming = secretPattern[i];
    int detectedTiming = detectedPattern[i];
    int difference = abs(secretTiming - detectedTiming);
    
    Serial.print("🔍 Comparing timing ");
    Serial.print(i);
    Serial.print(": Secret=");
    Serial.print(secretTiming);
    Serial.print(", Detected=");
    Serial.print(detectedTiming);
    Serial.print(", Diff=");
    Serial.println(difference);
    
    if (difference > PATTERN_TOLERANCE) {
      Serial.println("⚠️  Timing difference too large");
      return false;
    }
  }
  
  return true;
}

// Function to enter programming mode
void enterProgrammingMode() {
  currentState = PROGRAMMING;
  secretPatternLength = 0;
  
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, LOW);
  
  Serial.println("🔧 PROGRAMMING MODE ACTIVATED");
  Serial.println("📝 Knock your new secret pattern now...");
  
  // Flash both LEDs to indicate programming mode
  for (int i = 0; i < 3; i++) {
    digitalWrite(RED_LED_PIN, HIGH);
    digitalWrite(GREEN_LED_PIN, HIGH);
    delay(200);
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, LOW);
    delay(200);
  }
}

// Function to exit programming mode
void exitProgrammingMode() {
  if (secretPatternLength > 0) {
    Serial.println("✅ New pattern saved!");
    Serial.print("📊 Pattern length: ");
    Serial.println(secretPatternLength);
    
    // Print pattern for debugging
    Serial.print("🔑 Pattern timings: ");
    for (int i = 0; i < secretPatternLength; i++) {
      Serial.print(secretPattern[i]);
      if (i < secretPatternLength - 1) Serial.print(", ");
    }
    Serial.println();
  } else {
    Serial.println("⚠️  No pattern detected, keeping old pattern");
  }
  
  currentState = LOCKED;
  digitalWrite(RED_LED_PIN, HIGH);
  digitalWrite(GREEN_LED_PIN, LOW);
}

// Function to load default pattern (reinforces arrays)
void loadDefaultPattern() {
  secretPatternLength = defaultPatternLength;
  for (int i = 0; i < defaultPatternLength; i++) {
    secretPattern[i] = defaultPattern[i];
  }
  
  Serial.println("🔑 Default pattern loaded:");
  Serial.print("📊 Pattern: ");
  for (int i = 0; i < secretPatternLength; i++) {
    Serial.print(secretPattern[i]);
    if (i < secretPatternLength - 1) Serial.print(", ");
  }
  Serial.println();
}

// Function to update LCD display (reinforces display concepts)
void updateDisplay() {
  if (millis() - lastDisplayUpdate > DISPLAY_UPDATE_INTERVAL) {
    lcd.clear();
    
    // Line 1: System status
    lcd.setCursor(0, 0);
    switch (currentState) {
      case LOCKED:
        if (attempts >= MAX_ATTEMPTS) {
          lcd.print("LOCKED OUT!");
          lcd.setCursor(0, 1);
          int timeLeft = (LOCKOUT_DURATION - (millis() - lockoutTime)) / 1000;
          lcd.print("Wait: ");
          lcd.print(timeLeft);
          lcd.print("s");
        } else {
          lcd.print("SECURE LOCK");
          lcd.setCursor(0, 1);
          lcd.print("Knock pattern");
        }
        break;
      case LISTENING:
        lcd.print("LISTENING...");
        lcd.setCursor(0, 1);
        lcd.print("Knocks: ");
        lcd.print(detectedPatternLength);
        break;
      case PROGRAMMING:
        lcd.print("PROGRAMMING");
        lcd.setCursor(0, 1);
        lcd.print("Knock pattern");
        break;
      case UNLOCKED:
        lcd.print("UNLOCKED!");
        lcd.setCursor(0, 1);
        int timeLeft = (UNLOCK_DURATION - (millis() - unlockTime)) / 1000;
        lcd.print("Auto-lock: ");
        lcd.print(timeLeft);
        lcd.print("s");
        break;
      case PATTERN_MATCH:
        lcd.print("CHECKING...");
        lcd.setCursor(0, 1);
        lcd.print("Please wait");
        break;
    }
    
    lastDisplayUpdate = millis();
  }
}

// Function to play unlock sound (reinforces buzzer control)
void playUnlockSound() {
  tone(BUZZER_PIN, 800, 200);
  delay(250);
  tone(BUZZER_PIN, 1000, 200);
  delay(250);
  tone(BUZZER_PIN, 1200, 300);
}

// Function to play fail sound
void playFailSound() {
  tone(BUZZER_PIN, 300, 500);
  delay(600);
  tone(BUZZER_PIN, 200, 500);
}

// Function for startup sequence (reinforces LED and sound control)
void startupSequence() {
  Serial.println("🔧 Initializing security system...");
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Security System");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  // LED test sequence
  for (int i = 0; i < 3; i++) {
    digitalWrite(RED_LED_PIN, HIGH);
    tone(BUZZER_PIN, 500, 200);
    delay(300);
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(GREEN_LED_PIN, HIGH);
    tone(BUZZER_PIN, 700, 200);
    delay(300);
    digitalWrite(GREEN_LED_PIN, LOW);
  }
  
  // Final status
  digitalWrite(RED_LED_PIN, HIGH);
  tone(BUZZER_PIN, 400, 100);
  
  delay(1000);
  Serial.println("✅ System initialization complete");
}

/*
  KEY CONCEPTS REINFORCED:
  
  From Program 1 (LED Blink):
  - digitalWrite() for LED status indicators
  - Visual feedback and state indication
  
  From Program 4 (Potentiometer Reading):
  - analogRead() for sensor input
  - Threshold detection and signal processing
  
  From Program 8 (LCD Display):
  - LCD text display and real-time updates
  - Multi-state display management
  
  From Program 11 (Simon Says):
  - Pattern recognition and array manipulation
  - Timing measurement and comparison
  
  NEW SECURITY CONCEPTS:
  - Pattern recognition and matching
  - Security timeouts and lockouts
  - Access control systems
  - Signal processing and noise filtering
  
  NEW PROGRAMMING CONCEPTS:
  - Advanced state machines
  - Pattern analysis algorithms
  - Security system design
  - Real-time signal processing
*/