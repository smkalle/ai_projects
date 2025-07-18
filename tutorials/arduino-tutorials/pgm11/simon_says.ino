/*
  Project 11: Simon Says Game
  A memory-based game where players repeat sequences of LED patterns
  
  This project reinforces:
  - Digital output (LEDs) - from Program 1
  - Digital input (buttons) - from Program 2  
  - Arrays and loops - new programming concepts
  - Random number generation - mathematical concepts
  - Game logic and state management
  
  🎮 MISSION PREVIEW: "Game Developer"
  Create your own electronic games with lights, sounds, and challenges!
  
  Hardware Required:
  - Arduino board
  - 4x LEDs (Red, Green, Blue, Yellow)
  - 4x Push buttons
  - 4x 220Ω resistors (for LEDs)
  - 4x 10KΩ resistors (for button pull-ups) or use INPUT_PULLUP
  - 1x Buzzer
  - Breadboard and jumper wires
*/

// Pin definitions - organizing our components
const int LED_PINS[] = {2, 3, 4, 5};     // LED pins (Red, Green, Blue, Yellow)
const int BUTTON_PINS[] = {6, 7, 8, 9};   // Button pins
const int BUZZER_PIN = 10;                 // Buzzer pin
const int NUM_LEDS = 4;                    // Number of LEDs/buttons

// Game variables
int gameSequence[50];           // Array to store the game sequence (reinforces arrays)
int playerSequence[50];         // Array to store player input
int gameLength = 0;             // Current sequence length
int playerIndex = 0;            // Current player position
int gameLevel = 1;              // Current game level
bool gameActive = false;        // Is game currently running?
bool playerTurn = false;        // Is it player's turn?

// Timing variables (reinforces timing concepts from previous programs)
unsigned long lastTime = 0;
const int SEQUENCE_SPEED = 800; // Speed of sequence playback (ms)
const int BUTTON_DEBOUNCE = 200; // Button debounce time

// Game states (reinforces state management)
enum GameState {
  WAITING_TO_START,
  SHOWING_SEQUENCE,
  PLAYER_INPUT,
  GAME_OVER,
  LEVEL_UP
};
GameState currentState = WAITING_TO_START;

void setup() {
  // Initialize pins (reinforces pinMode from Program 1 & 2)
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    pinMode(BUTTON_PINS[i], INPUT_PULLUP);  // Using internal pull-up resistors
  }
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize serial communication (reinforces serial from all programs)
  Serial.begin(9600);
  Serial.println("🎮 SIMON SAYS GAME STARTED!");
  Serial.println("🎮 GAME DEVELOPER MODE - Ready to create electronic games!");
  Serial.println("Press any button to start the game!");
  Serial.println("=========================================");
  
  // Initialize random number generator (new concept!)
  randomSeed(analogRead(A0));  // Use analog noise as random seed
  
  // Welcome light show (reinforces LED control from Program 1)
  startupLightShow();
}

void loop() {
  // Main game state machine (reinforces program structure)
  switch (currentState) {
    case WAITING_TO_START:
      waitingForStart();
      break;
    case SHOWING_SEQUENCE:
      showSequence();
      break;
    case PLAYER_INPUT:
      handlePlayerInput();
      break;
    case GAME_OVER:
      handleGameOver();
      break;
    case LEVEL_UP:
      handleLevelUp();
      break;
  }
}

// Function to handle waiting for game start
void waitingForStart() {
  // Check if any button is pressed (reinforces button input from Program 2)
  for (int i = 0; i < NUM_LEDS; i++) {
    if (digitalRead(BUTTON_PINS[i]) == LOW) {
      Serial.println("🎮 GAME STARTING!");
      startNewGame();
      delay(BUTTON_DEBOUNCE);  // Debounce delay
      return;
    }
  }
  
  // Idle animation - make LEDs "breathe" (reinforces LED control)
  static unsigned long lastBreathe = 0;
  if (millis() - lastBreathe > 1000) {
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(LED_PINS[i], HIGH);
      delay(50);
      digitalWrite(LED_PINS[i], LOW);
    }
    lastBreathe = millis();
  }
}

// Function to start a new game
void startNewGame() {
  gameLength = 0;
  playerIndex = 0;
  gameLevel = 1;
  gameActive = true;
  
  // Clear sequences (reinforces arrays)
  for (int i = 0; i < 50; i++) {
    gameSequence[i] = 0;
    playerSequence[i] = 0;
  }
  
  // Add first sequence element (reinforces random numbers)
  addToSequence();
  currentState = SHOWING_SEQUENCE;
  
  Serial.print("🎯 Level ");
  Serial.print(gameLevel);
  Serial.println(" - Watch the sequence!");
}

// Function to add new element to sequence
void addToSequence() {
  gameSequence[gameLength] = random(NUM_LEDS);  // Random number 0-3
  gameLength++;
  
  Serial.print("📈 Sequence length: ");
  Serial.println(gameLength);
}

// Function to show the sequence to player
void showSequence() {
  static int sequenceIndex = 0;
  static unsigned long lastLED = 0;
  static bool ledOn = false;
  
  // Check if it's time to update the sequence display
  if (millis() - lastLED > SEQUENCE_SPEED / 2) {
    if (!ledOn) {
      // Turn on current LED in sequence
      if (sequenceIndex < gameLength) {
        digitalWrite(LED_PINS[gameSequence[sequenceIndex]], HIGH);
        playTone(200 + (gameSequence[sequenceIndex] * 100));  // Different tone for each LED
        ledOn = true;
        
        Serial.print("💡 Showing LED ");
        Serial.print(gameSequence[sequenceIndex] + 1);
        Serial.print(" (");
        Serial.print(sequenceIndex + 1);
        Serial.print("/");
        Serial.print(gameLength);
        Serial.println(")");
      }
    } else {
      // Turn off current LED and move to next
      digitalWrite(LED_PINS[gameSequence[sequenceIndex]], LOW);
      noTone(BUZZER_PIN);
      ledOn = false;
      sequenceIndex++;
      
      // Check if sequence is complete
      if (sequenceIndex >= gameLength) {
        sequenceIndex = 0;
        playerIndex = 0;
        currentState = PLAYER_INPUT;
        Serial.println("🎮 Your turn! Repeat the sequence!");
      }
    }
    lastLED = millis();
  }
}

// Function to handle player input
void handlePlayerInput() {
  static unsigned long lastButtonTime = 0;
  
  // Check each button (reinforces button input and loops)
  for (int i = 0; i < NUM_LEDS; i++) {
    if (digitalRead(BUTTON_PINS[i]) == LOW && (millis() - lastButtonTime > BUTTON_DEBOUNCE)) {
      // Button pressed!
      playerSequence[playerIndex] = i;
      
      // Light up corresponding LED (reinforces LED output)
      digitalWrite(LED_PINS[i], HIGH);
      playTone(200 + (i * 100));
      
      Serial.print("🎯 Player pressed button ");
      Serial.print(i + 1);
      Serial.print(" (");
      Serial.print(playerIndex + 1);
      Serial.print("/");
      Serial.print(gameLength);
      Serial.println(")");
      
      // Check if input is correct
      if (playerSequence[playerIndex] == gameSequence[playerIndex]) {
        Serial.println("✅ Correct!");
        playerIndex++;
        
        // Check if player completed the sequence
        if (playerIndex >= gameLength) {
          Serial.println("🎉 Sequence complete!");
          currentState = LEVEL_UP;
        }
      } else {
        Serial.println("❌ Wrong! Game Over!");
        currentState = GAME_OVER;
      }
      
      lastButtonTime = millis();
      
      // Turn off LED after short delay
      delay(200);
      digitalWrite(LED_PINS[i], LOW);
      noTone(BUZZER_PIN);
      
      break;  // Exit loop after handling button press
    }
  }
}

// Function to handle game over
void handleGameOver() {
  Serial.println("💀 GAME OVER!");
  Serial.print("🏆 You reached level ");
  Serial.print(gameLevel);
  Serial.print(" with ");
  Serial.print(gameLength);
  Serial.println(" steps!");
  
  // Game over animation (reinforces LED control and loops)
  for (int flash = 0; flash < 3; flash++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(LED_PINS[i], HIGH);
    }
    playTone(100);  // Low error tone
    delay(500);
    
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(LED_PINS[i], LOW);
    }
    noTone(BUZZER_PIN);
    delay(500);
  }
  
  Serial.println("🎮 Press any button to play again!");
  currentState = WAITING_TO_START;
}

// Function to handle level up
void handleLevelUp() {
  gameLevel++;
  Serial.print("🎊 LEVEL UP! Now on level ");
  Serial.println(gameLevel);
  
  // Level up animation (reinforces LED patterns)
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], HIGH);
    playTone(300 + (i * 100));  // Rising tone
    delay(100);
    digitalWrite(LED_PINS[i], LOW);
    noTone(BUZZER_PIN);
  }
  
  // Add new element to sequence and continue
  addToSequence();
  playerIndex = 0;
  currentState = SHOWING_SEQUENCE;
}

// Function to play tone on buzzer (reinforces basic output)
void playTone(int frequency) {
  tone(BUZZER_PIN, frequency);
}

// Function for startup light show (reinforces LED control and timing)
void startupLightShow() {
  Serial.println("🎭 Welcome to Simon Says!");
  
  // Chase pattern
  for (int round = 0; round < 2; round++) {
    for (int i = 0; i < NUM_LEDS; i++) {
      digitalWrite(LED_PINS[i], HIGH);
      playTone(300 + (i * 100));
      delay(150);
      digitalWrite(LED_PINS[i], LOW);
      noTone(BUZZER_PIN);
    }
  }
  
  // All flash
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], HIGH);
  }
  playTone(600);
  delay(500);
  
  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(LED_PINS[i], LOW);
  }
  noTone(BUZZER_PIN);
  delay(500);
  
  Serial.println("🎮 Ready to play!");
}

/*
  KEY CONCEPTS REINFORCED:
  
  From Program 1 (LED Blink):
  - digitalWrite() to control LEDs
  - pinMode() to set pin modes
  - Basic timing with delay()
  
  From Program 2 (Button Input):
  - digitalRead() to read button states
  - INPUT_PULLUP for button connections
  - Button debouncing techniques
  
  NEW PROGRAMMING CONCEPTS:
  - Arrays: gameSequence[], playerSequence[]
  - Loops: for loops to handle multiple LEDs/buttons
  - Random numbers: random() function
  - State machines: enum and switch statements
  - Functions: Breaking code into manageable pieces
  
  MATH CONCEPTS:
  - Sequences and patterns
  - Random number generation
  - Indexing and counting
  - Boolean logic (true/false states)
*/