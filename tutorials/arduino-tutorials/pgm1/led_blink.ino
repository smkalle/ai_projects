/*
  🚨 MISSION 1: LIGHTHOUSE KEEPER 🚨
  
  Welcome, young lighthouse keeper! Your job is to keep ships safe by operating
  the lighthouse beacon. This LED will be your lighthouse light that guides
  ships safely to shore in the dark night.
  
  Your Mission: Make the lighthouse beacon flash every second to warn ships!
  
  🎯 Challenge Level: Beginner Lighthouse Keeper
  ⏰ Time to Complete: 15 minutes
  🏆 Achievement: "First Light" - You've lit your first lighthouse!
*/

// 🗼 Our lighthouse beacon LED
const int LIGHTHOUSE_LED = 13;

// 🌊 Different flashing patterns for different weather conditions
const int CALM_WEATHER_DELAY = 1000;     // 1 second for calm seas
const int STORMY_WEATHER_DELAY = 300;    // Faster for storms!
const int FOG_PATTERN_DELAY = 2000;      // Slow for foggy nights

// 🎛️ Choose your weather condition (change this to try different patterns!)
const int CURRENT_WEATHER = CALM_WEATHER_DELAY;

void setup() {
  // 🔧 Set up our lighthouse beacon
  pinMode(LIGHTHOUSE_LED, OUTPUT);
  
  // 📡 Start the lighthouse communication system
  Serial.begin(9600);
  Serial.println("🚨 LIGHTHOUSE CONTROL SYSTEM ACTIVATED! 🚨");
  Serial.println("⚓ Welcome aboard, Lighthouse Keeper!");
  Serial.println("🌊 Your beacon is now protecting ships at sea...");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  
  // 🎺 Startup sequence - flash 3 times to signal we're ready!
  for(int i = 0; i < 3; i++) {
    digitalWrite(LIGHTHOUSE_LED, HIGH);
    Serial.println("🔆 LIGHTHOUSE SYSTEM STARTING... " + String(i+1) + "/3");
    delay(200);
    digitalWrite(LIGHTHOUSE_LED, LOW);
    delay(200);
  }
  
  Serial.println("✅ LIGHTHOUSE BEACON OPERATIONAL!");
  Serial.println("🚢 Ships can now see your light!");
}

void loop() {
  // 🌟 Turn the lighthouse beacon ON
  digitalWrite(LIGHTHOUSE_LED, HIGH);
  Serial.println("💡 BEACON ON  - Ships can see the light! 🚢");
  delay(CURRENT_WEATHER);
  
  // 🌚 Turn the lighthouse beacon OFF
  digitalWrite(LIGHTHOUSE_LED, LOW);
  Serial.println("⚫ BEACON OFF - Giving ships a moment to navigate 🧭");
  delay(CURRENT_WEATHER);
  
  // 📊 Every 10 cycles, give a status report
  static int flashCount = 0;
  flashCount++;
  if(flashCount >= 10) {
    Serial.println("📈 STATUS: " + String(flashCount) + " ships safely guided! 🏆");
    flashCount = 0;
  }
}

/*
  🎮 SUPER CHALLENGES FOR BRAVE LIGHTHOUSE KEEPERS:
  
  🌪️ STORM MODE: Change CURRENT_WEATHER to STORMY_WEATHER_DELAY
  🌫️ FOG MODE: Change CURRENT_WEATHER to FOG_PATTERN_DELAY
  
  🏗️ BUILD YOUR OWN PATTERNS:
  - Make it flash 3 times quickly, then pause
  - Create an SOS pattern: 3 short, 3 long, 3 short flashes
  - Add a second LED for a double lighthouse!
  
  🎯 ACHIEVEMENT UNLOCKED: "Master of the Seas" 🏆
  When you complete all challenges!
*/