/*
  Project 14: Pet Feeder Timer
  An automatic pet feeder with servo-controlled food dispensing and LCD countdown
  
  This project reinforces:
  - Servo motor control - from Program 7
  - LCD display - from Program 8
  - Button input - from Program 2
  - Timing systems - from multiple programs
  - Real-time scheduling and automation
  
  🐕 MISSION PREVIEW: "Pet Care Engineer"
  Design automated systems that take care of pets and solve real-world problems!
  
  Hardware Required:
  - Arduino board
  - Servo motor (for food dispenser)
  - 16x2 LCD display
  - 3x Push buttons (Set, Up, Down)
  - Buzzer (for feeding alerts)
  - LED (status indicator)
  - 220Ω resistor (for LED)
  - 10KΩ resistors (for buttons) or use INPUT_PULLUP
  - Small container/mechanism for food dispensing
  - Breadboard and jumper wires
*/

#include <Servo.h>
#include <LiquidCrystal.h>

// Create objects (reinforces library usage from Programs 7 & 8)
Servo feederServo;
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Pin definitions
const int SERVO_PIN = 9;        // Servo motor pin
const int BUTTON_SET = 6;       // Set button (enter setup mode)
const int BUTTON_UP = 7;        // Up button (increase time)
const int BUTTON_DOWN = 8;      // Down button (decrease time)
const int BUZZER_PIN = 10;      // Buzzer for alerts
const int LED_PIN = 13;         // Status LED
const int MANUAL_FEED_PIN = A0; // Manual feed button (analog pin used as digital)

// Timing variables (reinforces timing concepts from multiple programs)
unsigned long feedingIntervalMs = 6UL * 60UL * 60UL * 1000UL; // 6 hours in milliseconds
unsigned long lastFeedingTime = 0;
unsigned long nextFeedingTime = 0;
unsigned long currentTime = 0;
unsigned long setupStartTime = 0;

// Feeding schedule variables
int feedingHours = 6;           // Default 6 hours between feeds
int feedingMinutes = 0;         // Default 0 minutes
int maxHours = 24;              // Maximum 24 hours
int minHours = 1;               // Minimum 1 hour

// System state variables (reinforces state management)
enum SystemState {
  NORMAL_OPERATION,
  SETUP_HOURS,
  SETUP_MINUTES,
  FEEDING,
  MANUAL_FEED
};
SystemState currentState = NORMAL_OPERATION;

// Button handling variables (reinforces button concepts from Program 2)
bool lastSetState = HIGH;
bool lastUpState = HIGH;
bool lastDownState = HIGH;
bool lastManualState = HIGH;
unsigned long lastButtonTime = 0;
const unsigned long BUTTON_DEBOUNCE = 200;

// Feeding mechanism variables
const int SERVO_CLOSED = 0;     // Servo position when closed
const int SERVO_OPEN = 90;      // Servo position when open
const int FEED_DURATION = 2000; // How long to keep feeder open (ms)
int feedingCount = 0;           // Track number of feedings

// Display variables (reinforces display concepts from Program 8)
unsigned long lastDisplayUpdate = 0;
const unsigned long DISPLAY_UPDATE_INTERVAL = 1000; // Update every second

void setup() {
  // Initialize pins (reinforces pinMode from multiple programs)
  pinMode(BUTTON_SET, INPUT_PULLUP);
  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);
  pinMode(MANUAL_FEED_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize servo (reinforces servo setup from Program 7)
  feederServo.attach(SERVO_PIN);
  feederServo.write(SERVO_CLOSED);
  
  // Initialize LCD (reinforces LCD setup from Program 8)
  lcd.begin(16, 2);
  lcd.clear();
  
  // Initialize serial communication (reinforces serial from all programs)
  Serial.begin(9600);
  Serial.println("🐕 PET FEEDER TIMER STARTED!");
  Serial.println("🐕 PET CARE ENGINEER MODE - Design automated pet care systems!");
  Serial.println("Automatic feeding system with customizable schedule");
  Serial.println("================================================");
  
  // Display welcome message
  lcd.setCursor(0, 0);
  lcd.print("Pet Feeder v1.0");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  delay(2000);
  
  // Calculate initial feeding times
  calculateFeedingTimes();
  
  // Startup sequence (reinforces servo and display control)
  startupSequence();
  
  Serial.println("🍽️ System ready for feeding schedule");
  Serial.print("📅 Feed interval: ");
  Serial.print(feedingHours);
  Serial.print(" hours, ");
  Serial.print(feedingMinutes);
  Serial.println(" minutes");
}

void loop() {
  currentTime = millis();
  
  // Handle button inputs (reinforces button handling from Program 2)
  handleButtons();
  
  // Update display (reinforces display updates from Program 8)
  updateDisplay();
  
  // Handle different system states
  switch (currentState) {
    case NORMAL_OPERATION:
      handleNormalOperation();
      break;
    case SETUP_HOURS:
      handleSetupHours();
      break;
    case SETUP_MINUTES:
      handleSetupMinutes();
      break;
    case FEEDING:
      handleFeeding();
      break;
    case MANUAL_FEED:
      handleManualFeed();
      break;
  }
  
  // Status LED heartbeat (reinforces LED control from Program 1)
  static unsigned long lastHeartbeat = 0;
  if (currentTime - lastHeartbeat > 2000) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    lastHeartbeat = currentTime;
  }
}

// Function to handle button inputs (reinforces button concepts)
void handleButtons() {
  if (currentTime - lastButtonTime > BUTTON_DEBOUNCE) {
    // Set button
    bool setPressed = (digitalRead(BUTTON_SET) == LOW) && (lastSetState == HIGH);
    if (setPressed) {
      handleSetButton();
      lastButtonTime = currentTime;
    }
    lastSetState = digitalRead(BUTTON_SET);
    
    // Up button
    bool upPressed = (digitalRead(BUTTON_UP) == LOW) && (lastUpState == HIGH);
    if (upPressed) {
      handleUpButton();
      lastButtonTime = currentTime;
    }
    lastUpState = digitalRead(BUTTON_UP);
    
    // Down button
    bool downPressed = (digitalRead(BUTTON_DOWN) == LOW) && (lastDownState == HIGH);
    if (downPressed) {
      handleDownButton();
      lastButtonTime = currentTime;
    }
    lastDownState = digitalRead(BUTTON_DOWN);
    
    // Manual feed button
    bool manualPressed = (digitalRead(MANUAL_FEED_PIN) == LOW) && (lastManualState == HIGH);
    if (manualPressed) {
      handleManualButton();
      lastButtonTime = currentTime;
    }
    lastManualState = digitalRead(MANUAL_FEED_PIN);
  }
}

// Function to handle normal operation mode
void handleNormalOperation() {
  // Check if it's time to feed (reinforces timing logic)
  if (currentTime >= nextFeedingTime) {
    Serial.println("🍽️ Feeding time!");
    currentState = FEEDING;
    playFeedingAlert();
  }
}

// Function to handle feeding process
void handleFeeding() {
  Serial.println("🥄 Dispensing food...");
  
  // Open feeder servo (reinforces servo control from Program 7)
  feederServo.write(SERVO_OPEN);
  
  // Keep feeder open for specified duration
  delay(FEED_DURATION);
  
  // Close feeder servo
  feederServo.write(SERVO_CLOSED);
  
  // Update feeding statistics
  feedingCount++;
  lastFeedingTime = currentTime;
  calculateFeedingTimes();
  
  Serial.print("✅ Feeding #");
  Serial.print(feedingCount);
  Serial.println(" completed");
  
  // Play completion sound
  playCompletionSound();
  
  // Return to normal operation
  currentState = NORMAL_OPERATION;
}

// Function to handle manual feeding
void handleManualFeed() {
  Serial.println("🖐️ Manual feeding activated");
  
  // Perform feeding sequence (same as automatic)
  feederServo.write(SERVO_OPEN);
  delay(FEED_DURATION);
  feederServo.write(SERVO_CLOSED);
  
  feedingCount++;
  Serial.print("✅ Manual feeding #");
  Serial.print(feedingCount);
  Serial.println(" completed");
  
  playCompletionSound();
  currentState = NORMAL_OPERATION;
}

// Function to handle set button press
void handleSetButton() {
  switch (currentState) {
    case NORMAL_OPERATION:
      currentState = SETUP_HOURS;
      setupStartTime = currentTime;
      Serial.println("⚙️ Entering hours setup mode");
      break;
    case SETUP_HOURS:
      currentState = SETUP_MINUTES;
      Serial.println("⚙️ Entering minutes setup mode");
      break;
    case SETUP_MINUTES:
      currentState = NORMAL_OPERATION;
      calculateFeedingTimes();
      Serial.println("✅ Setup complete, returning to normal operation");
      break;
  }
}

// Function to handle up button press
void handleUpButton() {
  switch (currentState) {
    case SETUP_HOURS:
      feedingHours++;
      if (feedingHours > maxHours) feedingHours = maxHours;
      Serial.print("⬆️ Hours: ");
      Serial.println(feedingHours);
      break;
    case SETUP_MINUTES:
      feedingMinutes += 15;  // Increment by 15 minutes
      if (feedingMinutes >= 60) feedingMinutes = 0;
      Serial.print("⬆️ Minutes: ");
      Serial.println(feedingMinutes);
      break;
  }
}

// Function to handle down button press
void handleDownButton() {
  switch (currentState) {
    case SETUP_HOURS:
      feedingHours--;
      if (feedingHours < minHours) feedingHours = minHours;
      Serial.print("⬇️ Hours: ");
      Serial.println(feedingHours);
      break;
    case SETUP_MINUTES:
      feedingMinutes -= 15;  // Decrement by 15 minutes
      if (feedingMinutes < 0) feedingMinutes = 45;
      Serial.print("⬇️ Minutes: ");
      Serial.println(feedingMinutes);
      break;
  }
}

// Function to handle manual feed button
void handleManualButton() {
  if (currentState == NORMAL_OPERATION) {
    currentState = MANUAL_FEED;
  }
}

// Function to update LCD display (reinforces display concepts from Program 8)
void updateDisplay() {
  if (currentTime - lastDisplayUpdate > DISPLAY_UPDATE_INTERVAL) {
    lcd.clear();
    
    switch (currentState) {
      case NORMAL_OPERATION:
        displayNormalMode();
        break;
      case SETUP_HOURS:
        displaySetupHours();
        break;
      case SETUP_MINUTES:
        displaySetupMinutes();
        break;
      case FEEDING:
        displayFeeding();
        break;
      case MANUAL_FEED:
        displayManualFeed();
        break;
    }
    
    lastDisplayUpdate = currentTime;
  }
}

// Function to display normal operation mode
void displayNormalMode() {
  // Line 1: Current status
  lcd.setCursor(0, 0);
  lcd.print("Next Feed: ");
  
  // Calculate time until next feeding
  unsigned long timeUntilFeed = nextFeedingTime - currentTime;
  int hoursLeft = timeUntilFeed / (60UL * 60UL * 1000UL);
  int minutesLeft = (timeUntilFeed % (60UL * 60UL * 1000UL)) / (60UL * 1000UL);
  
  // Line 2: Countdown
  lcd.setCursor(0, 1);
  if (hoursLeft > 0) {
    lcd.print(hoursLeft);
    lcd.print("h ");
  }
  lcd.print(minutesLeft);
  lcd.print("m (");
  lcd.print(feedingCount);
  lcd.print(" fed)");
}

// Function to display setup hours mode
void displaySetupHours() {
  lcd.setCursor(0, 0);
  lcd.print("Set Feed Hours:");
  lcd.setCursor(0, 1);
  lcd.print(">>> ");
  lcd.print(feedingHours);
  lcd.print(" hours <<<");
}

// Function to display setup minutes mode
void displaySetupMinutes() {
  lcd.setCursor(0, 0);
  lcd.print("Set Feed Minutes:");
  lcd.setCursor(0, 1);
  lcd.print(">>> ");
  lcd.print(feedingMinutes);
  lcd.print(" min <<<");
}

// Function to display feeding mode
void displayFeeding() {
  lcd.setCursor(0, 0);
  lcd.print("FEEDING TIME!");
  lcd.setCursor(0, 1);
  lcd.print("Dispensing food.");
}

// Function to display manual feed mode
void displayManualFeed() {
  lcd.setCursor(0, 0);
  lcd.print("MANUAL FEEDING");
  lcd.setCursor(0, 1);
  lcd.print("Please wait...");
}

// Function to calculate feeding times
void calculateFeedingTimes() {
  feedingIntervalMs = (feedingHours * 60UL + feedingMinutes) * 60UL * 1000UL;
  nextFeedingTime = lastFeedingTime + feedingIntervalMs;
  
  Serial.print("📅 Next feeding in: ");
  Serial.print(feedingHours);
  Serial.print("h ");
  Serial.print(feedingMinutes);
  Serial.println("m");
}

// Function to play feeding alert sound (reinforces buzzer control)
void playFeedingAlert() {
  for (int i = 0; i < 3; i++) {
    tone(BUZZER_PIN, 800);
    delay(300);
    noTone(BUZZER_PIN);
    delay(200);
  }
}

// Function to play completion sound
void playCompletionSound() {
  tone(BUZZER_PIN, 1000);
  delay(200);
  tone(BUZZER_PIN, 1200);
  delay(200);
  noTone(BUZZER_PIN);
}

// Function for startup sequence (reinforces servo and display control)
void startupSequence() {
  Serial.println("🔧 Testing feeder mechanism...");
  
  // Test servo movement
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Testing Feeder");
  lcd.setCursor(0, 1);
  lcd.print("Please wait...");
  
  // Test open/close cycle
  feederServo.write(SERVO_OPEN);
  delay(1000);
  feederServo.write(SERVO_CLOSED);
  delay(1000);
  
  // Test sound system
  playCompletionSound();
  
  Serial.println("✅ System test complete");
  
  // Show ready message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("System Ready!");
  lcd.setCursor(0, 1);
  lcd.print("Press SET to cfg");
  delay(2000);
}

/*
  KEY CONCEPTS REINFORCED:
  
  From Program 2 (Button Input):
  - digitalRead() and button debouncing
  - Multiple button handling
  - State-based button responses
  
  From Program 7 (Servo Control):
  - Servo.attach() and servo.write()
  - Servo positioning and control
  - Mechanical automation
  
  From Program 8 (LCD Display):
  - LCD initialization and text display
  - Multi-mode display updates
  - Real-time information display
  
  NEW AUTOMATION CONCEPTS:
  - Scheduling and timing systems
  - State machine design
  - User interface design
  - Automated mechanical control
  
  NEW PROGRAMMING CONCEPTS:
  - Long-term timing (hours and minutes)
  - Multi-state user interfaces
  - Configuration and settings
  - Real-world problem solving
*/