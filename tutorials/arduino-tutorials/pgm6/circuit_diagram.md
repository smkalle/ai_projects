# 🌈 Program 6: RGB LED Control Circuit Diagram

## 🎯 **COLOR SCIENTIST MISSION**
Master the science of light and color by building a full-spectrum LED controller!

---

## 📋 **Components Needed**
- **Arduino Uno** (1x)
- **RGB LED (Common Cathode)** (1x)
- **220Ω Resistors** (3x - one for each color)
- **Breadboard** (1x)
- **Jumper Wires** (5x)

---

## 🔌 **Circuit Diagram**

```
    Arduino Uno                     Breadboard
    ┌─────────────┐                ┌─────────────────┐
    │             │                │                 │
    │         D9  │────────────────┤ Red LED Pin     │
    │        D10  │────────────────┤ Green LED Pin   │
    │        D11  │────────────────┤ Blue LED Pin    │
    │             │                │                 │
    │         GND │────────────────┤ RGB LED Common  │
    │             │                │                 │
    └─────────────┘                └─────────────────┘
```

---

## 🔧 **Step-by-Step Wiring**

### **Step 1: RGB LED Identification**
**IMPORTANT**: Identify RGB LED pinout - Common Cathode vs Common Anode

```
Common Cathode RGB LED (4 pins):
┌─────────────────────┐
│  R   G   CC   B     │
│  │   │   │    │     │
│  1   2   3    4     │
└─────────────────────┘

Pin 1: Red Anode (+)
Pin 2: Green Anode (+)
Pin 3: Common Cathode (-)
Pin 4: Blue Anode (+)
```

### **Step 2: Breadboard Layout**
```
Breadboard Layout:
┌─────────────────────────────────┐
│  +  -  a  b  c  d  e  f  g  h  │
│                                 │
│  1  1  .  .  .  .  .  .  .  .  │ ← Red LED connection
│  2  2  .  .  .  .  .  .  .  .  │ ← Green LED connection
│  3  3  .  .  .  .  .  .  .  .  │ ← Common Cathode
│  4  4  .  .  .  .  .  .  .  .  │ ← Blue LED connection
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  .  .  .  .  .  .  .  .  │ ← Red resistor
│  7  7  .  .  .  .  .  .  .  .  │ ← Green resistor
│  8  8  .  .  .  .  .  .  .  .  │ ← Blue resistor
└─────────────────────────────────┘
```

### **Step 3: Install RGB LED**
Place RGB LED carefully - longest pin is usually common cathode

```
RGB LED Installation:
┌─────────────────────────────────┐
│  1  1  R  .  .  .  .  .  .  .  │ ← Pin 1 (Red anode)
│  2  2  G  .  .  .  .  .  .  .  │ ← Pin 2 (Green anode)
│  3  3  C  .  .  .  .  .  .  .  │ ← Pin 3 (Common cathode)
│  4  4  B  .  .  .  .  .  .  .  │ ← Pin 4 (Blue anode)
└─────────────────────────────────┘
```

### **Step 4: Install Current-Limiting Resistors**
Each color needs its own 220Ω resistor:

```
Resistor Installation:
┌─────────────────────────────────┐
│  1  1  R  Rr .  .  .  .  .  .  │ ← Red + resistor
│  2  2  G  Rg .  .  .  .  .  .  │ ← Green + resistor
│  3  3  C  .  .  .  .  .  .  .  │ ← Common cathode
│  4  4  B  Rb .  .  .  .  .  .  │ ← Blue + resistor
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  .  Rr .  .  .  .  .  .  │ ← Red resistor other end
│  7  7  .  Rg .  .  .  .  .  .  │ ← Green resistor other end
│  8  8  .  Rb .  .  .  .  .  .  │ ← Blue resistor other end
└─────────────────────────────────┘
```

### **Step 5: Connect Arduino Pins**
Connect PWM pins to control brightness:

```
Final Circuit:
┌─────────────────────────────────┐
│  1  1  R  Rr .  .  .  .  .  .  │ ← Red LED + resistor
│  2  2  G  Rg .  .  .  .  .  .  │ ← Green LED + resistor
│  3  3  C  ●  .  .  .  .  .  .  │ ← Common cathode to GND
│  4  4  B  Rb .  .  .  .  .  .  │ ← Blue LED + resistor
│  5  5  .  .  .  .  .  .  .  .  │
│  6  6  .  Rr─●  .  .  .  .  .  │ ← Red resistor to D9
│  7  7  .  Rg─●  .  .  .  .  .  │ ← Green resistor to D10
│  8  8  .  Rb─●  .  .  .  .  .  │ ← Blue resistor to D11
└─────────────────────────────────┘

● = Jumper wire connections
Rr = Red resistor (220Ω)
Rg = Green resistor (220Ω)
Rb = Blue resistor (220Ω)
```

### **Step 6: Wire Connections**
- **Red wire**: Arduino D9 → Row 6, column 'c' (Red through resistor)
- **Green wire**: Arduino D10 → Row 7, column 'c' (Green through resistor)
- **Blue wire**: Arduino D11 → Row 8, column 'c' (Blue through resistor)
- **Black wire**: Arduino GND → Row 3, column 'c' (Common cathode)

---

## ⚡ **Circuit Explanation**

### **How RGB LEDs Work:**
1. **Three separate LEDs** in one package (Red, Green, Blue)
2. **Common cathode** connects all negative terminals
3. **PWM control** varies brightness of each color
4. **Color mixing** creates millions of possible colors

### **PWM (Pulse Width Modulation):**
```
PWM Value    Brightness    Duty Cycle
─────────────────────────────────────
0            Off           0%
64           25%           25%
128          50%           50%
192          75%           75%
255          Full          100%
```

### **Color Mixing Theory:**
```
Primary Colors:
Red   (255, 0, 0)   = Pure red
Green (0, 255, 0)   = Pure green
Blue  (0, 0, 255)   = Pure blue

Secondary Colors:
Yellow  (255, 255, 0)   = Red + Green
Magenta (255, 0, 255)   = Red + Blue
Cyan    (0, 255, 255)   = Green + Blue
White   (255, 255, 255) = All colors
```

### **Current Flow:**
```
Arduino PWM → Resistor → LED Anode → LED Cathode → Common → GND
     ↑                                                      ↓
     └─────────────── Circuit Complete ──────────────────────┘
```

---

## 🎨 **Visual Connection Guide**

```
   ARDUINO UNO
   ┌─────────────┐
   │  ┌─────────┐│
   │  │  RESET  ││
   │  └─────────┘│
   │             │
   │  D9 ●────────┼─── RED WIRE ──────────┐
   │             │                       │
   │ D10 ●────────┼─── GREEN WIRE ────────┼─┐
   │             │                       │ │
   │ D11 ●────────┼─── BLUE WIRE ─────────┼─┼─┐
   │             │                       │ │ │
   │ GND ●────────┼─── BLACK WIRE ────────┼─┼─┼─┐
   │             │                       │ │ │ │
   └─────────────┘                       │ │ │ │
                                         │ │ │ │
   BREADBOARD - RGB LED                  │ │ │ │
   ┌─────────────┐                       │ │ │ │
   │             │                       │ │ │ │
   │ ●─[220Ω]────┼───────────────────────┘ │ │ │
   │             │                         │ │ │
   │ ●─[220Ω]────┼─────────────────────────┘ │ │
   │             │                           │ │
   │ ●───────────┼───────────────────────────┘ │
   │             │                             │
   │ ●─[220Ω]────┼─────────────────────────────┘
   │             │
   │   [RGB LED] │
   │  R G CC B   │
   └─────────────┘
```

---

## 🌈 **Color Programming Guide**

### **Basic Color Functions:**
```cpp
// Set RGB color (0-255 for each channel)
void setColor(int red, int green, int blue) {
    analogWrite(9, red);     // Red pin
    analogWrite(10, green);  // Green pin
    analogWrite(11, blue);   // Blue pin
}

// Pre-defined colors
void showRed()     { setColor(255, 0, 0); }
void showGreen()   { setColor(0, 255, 0); }
void showBlue()    { setColor(0, 0, 255); }
void showWhite()   { setColor(255, 255, 255); }
void showOff()     { setColor(0, 0, 0); }
```

### **Color Transition Effects:**
```cpp
// Smooth color fade
void fadeColor(int fromR, int fromG, int fromB, 
               int toR, int toG, int toB, int steps) {
    for (int i = 0; i <= steps; i++) {
        int r = map(i, 0, steps, fromR, toR);
        int g = map(i, 0, steps, fromG, toG);
        int b = map(i, 0, steps, fromB, toB);
        setColor(r, g, b);
        delay(50);
    }
}

// Rainbow cycle
void rainbowCycle() {
    for (int i = 0; i < 256; i++) {
        setColor(wheelColor(i));
        delay(20);
    }
}
```

### **Advanced Color Patterns:**
```cpp
// Breathing effect
void breathingEffect(int r, int g, int b) {
    for (int brightness = 0; brightness <= 255; brightness++) {
        setColor((r * brightness) / 255, 
                 (g * brightness) / 255, 
                 (b * brightness) / 255);
        delay(10);
    }
    for (int brightness = 255; brightness >= 0; brightness--) {
        setColor((r * brightness) / 255, 
                 (g * brightness) / 255, 
                 (b * brightness) / 255);
        delay(10);
    }
}

// Strobe effect
void strobeEffect(int r, int g, int b, int times) {
    for (int i = 0; i < times; i++) {
        setColor(r, g, b);
        delay(100);
        setColor(0, 0, 0);
        delay(100);
    }
}
```

---

## 🧪 **Testing Your Circuit**

### **Before Upload:**
1. **Check RGB LED pinout** - identify common cathode
2. **Verify resistor placement** - one for each color
3. **Confirm PWM pins** - D9, D10, D11 are PWM-capable
4. **Test connections** - no shorts between pins

### **Color Test Sequence:**
```cpp
void setup() {
    Serial.begin(9600);
    Serial.println("RGB LED Test Starting...");
    
    // Test each color individually
    Serial.println("Testing Red...");
    setColor(255, 0, 0);
    delay(1000);
    
    Serial.println("Testing Green...");
    setColor(0, 255, 0);
    delay(1000);
    
    Serial.println("Testing Blue...");
    setColor(0, 0, 255);
    delay(1000);
    
    Serial.println("Testing White...");
    setColor(255, 255, 255);
    delay(1000);
    
    Serial.println("Test Complete!");
    setColor(0, 0, 0);
}
```

### **Troubleshooting:**
- **No light**: Check common cathode connection to GND
- **Missing colors**: Verify individual resistor connections
- **Dim colors**: Check resistor values (should be 220Ω)
- **Wrong colors**: Check pin assignments (R=D9, G=D10, B=D11)

### **Advanced Testing:**
```cpp
// Test PWM levels
void testPWM() {
    Serial.println("Testing PWM levels...");
    for (int level = 0; level <= 255; level += 51) {
        Serial.print("PWM Level: ");
        Serial.println(level);
        setColor(level, 0, 0);  // Test red channel
        delay(500);
    }
}

// Test color mixing
void testColorMixing() {
    Serial.println("Testing color mixing...");
    setColor(255, 255, 0);   // Yellow
    delay(1000);
    setColor(255, 0, 255);   // Magenta
    delay(1000);
    setColor(0, 255, 255);   // Cyan
    delay(1000);
}
```

---

## 🎪 **Creative Color Projects**

### **Mood Lighting:**
```cpp
// Respond to ambient light
int lightLevel = analogRead(A0);
if (lightLevel < 200) {
    // Evening - warm colors
    setColor(255, 100, 0);
} else if (lightLevel < 600) {
    // Daytime - cool colors
    setColor(0, 150, 255);
} else {
    // Bright - white light
    setColor(255, 255, 255);
}
```

### **Music Visualizer:**
```cpp
// Sound-reactive lighting
int soundLevel = analogRead(A1);
int bass = map(soundLevel, 0, 1023, 0, 255);
setColor(bass, bass/2, 255-bass);
```

### **Temperature Indicator:**
```cpp
// Color-coded temperature display
float temp = readTemperature();
if (temp < 20) {
    setColor(0, 0, 255);    // Cold = Blue
} else if (temp < 25) {
    setColor(0, 255, 0);    // Comfortable = Green
} else {
    setColor(255, 0, 0);    // Hot = Red
}
```

---

## 🎉 **Success! You've Built a Color Controller!**

**Congratulations, Color Scientist!** Your RGB LED controller is now operational! You've learned PWM control, color theory, and advanced lighting effects - essential skills for display systems, mood lighting, and visual feedback interfaces!

### **Next Steps:**
- Add potentiometers for manual color control
- Create sound-reactive lighting
- Build a color-changing clock
- Add Bluetooth control for smartphone app

### **Advanced Features:**
```cpp
// Color memory system
struct Color {
    int r, g, b;
    String name;
};

Color colorPalette[] = {
    {255, 0, 0, "Red"},
    {0, 255, 0, "Green"},
    {0, 0, 255, "Blue"},
    {255, 255, 0, "Yellow"},
    {255, 0, 255, "Magenta"},
    {0, 255, 255, "Cyan"},
    {255, 255, 255, "White"}
};

// Smooth transitions
void smoothTransition(Color from, Color to, int duration) {
    int steps = duration / 10;
    for (int i = 0; i <= steps; i++) {
        int r = map(i, 0, steps, from.r, to.r);
        int g = map(i, 0, steps, from.g, to.g);
        int b = map(i, 0, steps, from.b, to.b);
        setColor(r, g, b);
        delay(10);
    }
}
```

### **Real-World Applications:**
- **Stage lighting**: Theater and concert effects
- **Architectural**: Building accent lighting
- **Automotive**: Interior mood lighting
- **Gaming**: Immersive feedback systems
- **Home automation**: Smart lighting systems

---

*Let your creativity shine in full spectrum! Keep building! 🚀*