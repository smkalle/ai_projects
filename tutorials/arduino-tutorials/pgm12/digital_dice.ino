/*
  Project 12: Digital Dice
  An electronic dice that displays random numbers 1-6 with rolling animation
  
  This project reinforces:
  - Digital output (LEDs) - from Program 1
  - Digital input (button) - from Program 2
  - LCD display - from Program 8
  - Random number generation - from Program 11
  - Mathematical concepts (probability, modulo)
  
  🎲 MISSION PREVIEW: "Probability Engineer"
  Master the mathematics of chance and create systems that make fair decisions!
  
  Hardware Required:
  - Arduino board
  - 16x2 LCD display
  - 1x Push button
  - 6x LEDs (to represent dice dots)
  - 6x 220Ω resistors (for LEDs)
  - 1x 10KΩ resistor (for button) or use INPUT_PULLUP
  - 1x 10KΩ potentiometer (for LCD contrast)
  - Breadboard and jumper wires
*/

#include <LiquidCrystal.h>

// Initialize LCD library (reinforces LCD from Program 8)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// Pin definitions
const int BUTTON_PIN = 6;           // Roll button
const int LED_PINS[] = {7, 8, 9, 10, 13, A5};  // 6 LEDs for dice pattern
const int NUM_LEDS = 6;             // Number of LEDs

// Game variables
int currentRoll = 1;                // Current dice value
int rollCount = 0;                  // Total number of rolls
int rollHistory[6] = {0, 0, 0, 0, 0, 0};  // Count of each number (reinforces arrays)
bool isRolling = false;             // Animation state
int animationSpeed = 50;            // Animation speed (ms)

// Button handling (reinforces button concepts from Program 2)
bool lastButtonState = HIGH;
bool buttonPressed = false;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

// Timing variables (reinforces timing from multiple programs)
unsigned long lastRollTime = 0;
unsigned long rollStartTime = 0;
const unsigned long rollDuration = 2000;  // 2 seconds of rolling animation

// Dice patterns - which LEDs to light for each number (reinforces arrays and patterns)
bool dicePatterns[7][6] = {
  {0, 0, 0, 0, 0, 0},  // 0 (not used)
  {0, 0, 1, 0, 0, 0},  // 1: center dot
  {1, 0, 0, 0, 0, 1},  // 2: opposite corners
  {1, 0, 1, 0, 0, 1},  // 3: diagonal
  {1, 1, 0, 0, 1, 1},  // 4: four corners
  {1, 1, 1, 0, 1, 1},  // 5: four corners + center
  {1, 1, 1, 1, 1, 1}   // 6: all dots
};

void setup() {
  // Initialize pins (reinforces pinMode from Programs 1 & 2)
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
  }
  
  // Initialize LCD (reinforces LCD setup from Program 8)
  lcd.begin(16, 2);
  lcd.clear();
  
  // Initialize serial communication (reinforces serial from all programs)
  Serial.begin(9600);
  Serial.println("🎲 DIGITAL DICE STARTED!");
  Serial.println("🎲 PROBABILITY ENGINEER MODE - Master the mathematics of chance!");
  Serial.println("Press button to roll the dice!");
  Serial.println("===========================================");
  
  // Initialize random number generator (reinforces random from Program 11)
  randomSeed(analogRead(A0));
  
  // Display welcome message
  lcd.setCursor(0, 0);
  lcd.print("Digital Dice");
  lcd.setCursor(0, 1);
  lcd.print("Press to roll!");
  
  // Show initial dice pattern
  displayDice(1);
  
  // Startup animation (reinforces LED control from Program 1)
  startupAnimation();
}

void loop() {
  // Handle button input (reinforces button handling from Program 2)
  handleButton();
  
  // Handle rolling animation
  if (isRolling) {
    handleRollingAnimation();
  }
  
  // Update display periodically
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 1000) {
    updateDisplay();
    lastUpdate = millis();
  }
}

// Function to handle button presses (reinforces button concepts)
void handleButton() {
  bool reading = digitalRead(BUTTON_PIN);
  
  // Check if button state changed (debouncing)
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  // If button state has been stable for debounce delay
  if ((millis() - lastDebounceTime) > debounceDelay) {
    // If button state has changed
    if (reading != buttonPressed) {
      buttonPressed = reading;
      
      // If button was pressed (LOW because of pull-up)
      if (buttonPressed == LOW && !isRolling) {
        startRoll();
      }
    }
  }
  
  lastButtonState = reading;
}

// Function to start rolling animation
void startRoll() {
  isRolling = true;
  rollStartTime = millis();
  animationSpeed = 50;  // Start fast
  
  Serial.println("🎲 Rolling dice...");
  
  // Clear LCD and show rolling message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Rolling...");
  
  // Show rolling animation on second line
  lcd.setCursor(0, 1);
  lcd.print("* * * * * *");
}

// Function to handle rolling animation
void handleRollingAnimation() {
  unsigned long currentTime = millis();
  
  // Generate random number during roll (reinforces random numbers)
  if (currentTime - lastRollTime > animationSpeed) {
    currentRoll = random(1, 7);  // Random number 1-6
    displayDice(currentRoll);
    
    lastRollTime = currentTime;
    
    // Gradually slow down animation (makes it feel more realistic)
    if (currentTime - rollStartTime > rollDuration / 2) {
      animationSpeed = 150;  // Slow down
    }
  }
  
  // Check if roll is complete
  if (currentTime - rollStartTime > rollDuration) {
    finishRoll();
  }
}

// Function to finish the roll
void finishRoll() {
  isRolling = false;
  
  // Final random number (reinforces random concepts)
  currentRoll = random(1, 7);
  
  // Update statistics (reinforces math and arrays)
  rollCount++;
  rollHistory[currentRoll - 1]++;  // Array index 0-5 for rolls 1-6
  
  // Display result
  displayDice(currentRoll);
  
  Serial.print("🎯 Rolled: ");
  Serial.print(currentRoll);
  Serial.print(" (Total rolls: ");
  Serial.print(rollCount);
  Serial.println(")");
  
  // Show result on LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Rolled: ");
  lcd.print(currentRoll);
  
  lcd.setCursor(0, 1);
  lcd.print("Total: ");
  lcd.print(rollCount);
  lcd.print(" rolls");
  
  // Print statistics to serial (reinforces math concepts)
  printStatistics();
}

// Function to display dice pattern with LEDs (reinforces LED control and arrays)
void displayDice(int number) {
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], dicePatterns[number][i]);
  }
}

// Function to update LCD display
void updateDisplay() {
  if (!isRolling) {
    // Calculate and display statistics (reinforces math concepts)
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Last: ");
    lcd.print(currentRoll);
    lcd.print(" (");
    lcd.print(rollCount);
    lcd.print(" rolls)");
    
    // Show most common number
    int mostCommon = findMostCommon();
    lcd.setCursor(0, 1);
    lcd.print("Most: ");
    lcd.print(mostCommon);
    lcd.print(" (");
    lcd.print(rollHistory[mostCommon - 1]);
    lcd.print(" times)");
  }
}

// Function to find most commonly rolled number (reinforces arrays and loops)
int findMostCommon() {
  int maxCount = 0;
  int mostCommon = 1;
  
  for (int i = 0; i < 6; i++) {
    if (rollHistory[i] > maxCount) {
      maxCount = rollHistory[i];
      mostCommon = i + 1;  // Convert array index to dice number
    }
  }
  
  return mostCommon;
}

// Function to print statistics (reinforces math and probability concepts)
void printStatistics() {
  Serial.println("📊 STATISTICS:");
  Serial.println("Number | Count | Percentage");
  Serial.println("-------|-------|----------");
  
  for (int i = 0; i < 6; i++) {
    float percentage = (rollCount > 0) ? (rollHistory[i] * 100.0 / rollCount) : 0;
    
    Serial.print("  ");
    Serial.print(i + 1);
    Serial.print("    |  ");
    Serial.print(rollHistory[i]);
    Serial.print("   |  ");
    Serial.print(percentage, 1);
    Serial.println("%");
  }
  
  Serial.println("-------|-------|----------");
  Serial.print("Expected: 16.7% each (");
  Serial.print(rollCount / 6.0, 1);
  Serial.println(" rolls)");
  Serial.println();
}

// Function for startup animation (reinforces LED control)
void startupAnimation() {
  Serial.println("🎭 Welcome to Digital Dice!");
  
  // Show each dice pattern (reinforces loops and arrays)
  for (int num = 1; num <= 6; num++) {
    displayDice(num);
    delay(300);
  }
  
  // Flash all LEDs (reinforces LED control)
  for (int flash = 0; flash < 3; flash++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(LED_PINS[i], HIGH);
    }
    delay(200);
    
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(LED_PINS[i], LOW);
    }
    delay(200);
  }
  
  // Show starting pattern
  displayDice(1);
  
  Serial.println("🎲 Ready to roll!");
}

/*
  KEY CONCEPTS REINFORCED:
  
  From Program 1 (LED Blink):
  - digitalWrite() to control multiple LEDs
  - LED patterns and timing
  
  From Program 2 (Button Input):
  - digitalRead() and button debouncing
  - State management for user input
  
  From Program 8 (LCD Display):
  - LCD initialization and text display
  - Real-time information updates
  
  From Program 11 (Simon Says):
  - Random number generation
  - Arrays for storing patterns
  
  NEW MATHEMATICAL CONCEPTS:
  - Probability and statistics
  - Percentage calculations
  - Data analysis and trends
  - Modulo arithmetic (array indexing)
  
  NEW PROGRAMMING CONCEPTS:
  - Two-dimensional arrays (dicePatterns)
  - Statistical analysis
  - Animation timing and control
  - Data visualization
*/