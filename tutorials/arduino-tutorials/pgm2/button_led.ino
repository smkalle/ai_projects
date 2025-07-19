/*
  🕵️ MISSION 2: SECRET AGENT SIGNAL CONTROLLER 🕵️
  
  Agent, your mission is to operate a covert communication system!
  Use the secret button to send coded light signals to other agents.
  Each button press toggles your signal light - but be careful,
  enemy spies might be watching!
  
  🎯 Mission Objective: Master the art of secret communication!
  
  🕵️ Agent Level: Novice Spy
  ⏰ Mission Duration: 20 minutes
  🏆 Achievement: "Signal Master" - You've mastered covert communication!
*/

// 🎛️ Secret Agent Equipment
const int SECRET_BUTTON = 2;     // Covert activation button
const int SIGNAL_LIGHT = 13;     // Secret communication light
const int MISSION_LED = 12;      // Mission status indicator (optional)

// 🕵️ Agent Communication Variables
int buttonState = 0;             // Current button reading
int lastButtonState = 0;         // Previous button state
boolean lightActive = false;     // Signal light status
unsigned long lastSignalTime = 0; // Track signal timing
int signalCount = 0;             // Count successful signals

// 🎯 Mission Settings
const int SIGNAL_TIMEOUT = 5000;  // 5 seconds before mission reset
const int DEBOUNCE_DELAY = 100;   // Button debounce time

void setup() {
  // 🔧 Initialize secret equipment
  pinMode(SIGNAL_LIGHT, OUTPUT);
  pinMode(SECRET_BUTTON, INPUT_PULLUP);
  pinMode(MISSION_LED, OUTPUT);
  
  // 📡 Establish secure communication channel
  Serial.begin(9600);
  Serial.println("🕵️ SECRET AGENT COMMUNICATION SYSTEM ACTIVATED 🕵️");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("🎯 MISSION BRIEFING:");
  Serial.println("   • Use secret button to toggle signal light");
  Serial.println("   • Each press sends a coded message");
  Serial.println("   • Watch for enemy surveillance!");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  // 🚨 Agent activation sequence
  Serial.println("🔐 ACTIVATING AGENT CREDENTIALS...");
  for(int i = 0; i < 3; i++) {
    digitalWrite(SIGNAL_LIGHT, HIGH);
    digitalWrite(MISSION_LED, HIGH);
    delay(150);
    digitalWrite(SIGNAL_LIGHT, LOW);
    digitalWrite(MISSION_LED, LOW);
    delay(150);
  }
  
  Serial.println("✅ AGENT ACTIVATED! You are now operational.");
  Serial.println("🎮 Press the secret button to begin mission...");
  digitalWrite(MISSION_LED, HIGH); // Mission ready indicator
}

void loop() {
  // 🔍 Monitor secret button
  buttonState = digitalRead(SECRET_BUTTON);
  
  // 🎯 Detect button press (agent activation)
  if (buttonState == LOW && lastButtonState == HIGH) {
    // 🚨 Agent has activated signal!
    lightActive = !lightActive;
    digitalWrite(SIGNAL_LIGHT, lightActive);
    
    signalCount++;
    lastSignalTime = millis();
    
    // 📡 Send status report to headquarters
    if (lightActive) {
      Serial.println("🟢 SIGNAL ACTIVE - Message transmitted to ally agents!");
      Serial.println("   🔊 \"All clear - mission proceeding as planned\"");
    } else {
      Serial.println("🔴 SIGNAL DEACTIVATED - Going dark to avoid detection!");
      Serial.println("   🤫 \"Switching to stealth mode\"");
    }
    
    // 🏆 Track agent performance
    Serial.println("📊 MISSION STATS: " + String(signalCount) + " signals sent");
    
    // 🎯 Check for mission milestones
    if (signalCount == 5) {
      Serial.println("🏆 MILESTONE ACHIEVED: 'Quick Communicator' - 5 signals sent!");
      celebrateAchievement();
    }
    if (signalCount == 10) {
      Serial.println("🏆 ELITE STATUS: 'Master Spy' - 10 signals sent!");
      eliteAgentSequence();
    }
    
    // 🕰️ Button debounce for clean signals
    delay(DEBOUNCE_DELAY);
  }
  
  // 🔍 Check for mission timeout (too long without activity)
  if (millis() - lastSignalTime > SIGNAL_TIMEOUT && signalCount > 0) {
    Serial.println("⚠️  MISSION TIMEOUT - Enemy may have detected activity!");
    Serial.println("🔄 Resetting communication system...");
    
    // Reset mission
    signalCount = 0;
    lightActive = false;
    digitalWrite(SIGNAL_LIGHT, LOW);
    
    // Warning flash
    for(int i = 0; i < 2; i++) {
      digitalWrite(MISSION_LED, LOW);
      delay(100);
      digitalWrite(MISSION_LED, HIGH);
      delay(100);
    }
    
    lastSignalTime = millis();
  }
  
  // 💾 Save current button state
  lastButtonState = buttonState;
}

void celebrateAchievement() {
  // 🎉 Quick celebration sequence
  for(int i = 0; i < 3; i++) {
    digitalWrite(SIGNAL_LIGHT, HIGH);
    digitalWrite(MISSION_LED, LOW);
    delay(100);
    digitalWrite(SIGNAL_LIGHT, LOW);
    digitalWrite(MISSION_LED, HIGH);
    delay(100);
  }
}

void eliteAgentSequence() {
  // 🌟 Elite agent unlock sequence
  Serial.println("🌟 UNLOCKING ELITE AGENT PROTOCOLS...");
  for(int i = 0; i < 5; i++) {
    digitalWrite(SIGNAL_LIGHT, HIGH);
    delay(50);
    digitalWrite(SIGNAL_LIGHT, LOW);
    delay(50);
  }
  Serial.println("🎖️ CONGRATULATIONS: You are now an ELITE SECRET AGENT!");
}

/*
  🎮 ADVANCED SPY MISSIONS:
  
  🔓 MORSE CODE CHALLENGE:
  - Send your name in morse code (dots = short press, dashes = long press)
  
  🔓 STEALTH MISSION:
  - Add a second button for "enemy detector" mode
  - If second button pressed, all lights turn off instantly!
  
  🔓 MULTI-AGENT OPERATION:
  - Connect multiple LEDs for different signal types
  - Red = Danger, Green = All Clear, Blue = Mission Complete
  
  🎯 ULTIMATE CHALLENGE: Build a complete spy communication network!
*/