# 🦯 Ariadne for Smart Glasses

**AI Assistant for the Visually Impaired – Built with AugmentOS**

> Hands-free scene understanding, sign reading, and object awareness using wearable smart glasses and AI.

---

## 📖 Table of Contents

- [Overview](#-overview)  
- [Features](#-features)  
- [Demo](#-demo)  
- [Setup](#-setup)  
- [Project Structure](#-project-structure)  
- [Step-by-Step Tutorial](#-step-by-step-tutorial)  
  - [1️⃣ Scene Description](#1️⃣-scene-description)  
  - [2️⃣ Sign Reader](#2️⃣-sign-reader)  
  - [3️⃣ Object Awareness](#3️⃣-object-awareness)  
  - [4️⃣ Voice Commands](#4️⃣-voice-commands)  
- [Enhancements](#-enhancements)  
- [Resources](#-resources)  
- [Contributing](#-contributing)  
- [Acknowledgments](#-acknowledgments)

---

## 🚀 Overview

**Ariadne** is an AI-powered assistant for visually impaired users, running on Mentra Live smart glasses with the AugmentOS SDK. It offers real-time:

- Environmental **scene description**  
- **Sign reading** via OCR  
- **Object detection** with spatial awareness  
- **Voice-command-based control**

> This project was created during the [Mentra × Y Combinator Smart Glasses Hackathon – July 2025](https://augmentos.org).

---

## ✨ Features

- 📸 Take a photo and **describe the scene** with AI-generated captions  
- 🔠 Capture text from signs and **read it aloud**  
- 🧭 Identify and position objects in the user’s surroundings  
- 🎙️ Respond to spoken commands like "Read sign" or "Describe scene"

---

## 📹 Demo

_(Insert your demo video or image preview here, e.g., GIF or YouTube link)_

---

## 🔧 Setup

### Prerequisites

- AugmentOS-compatible smart glasses (e.g., Mentra Live)  
- AugmentOS account and developer access ([console.augmentos.org](https://console.augmentos.org))  
- Node.js + bun + ngrok  
- `.env` file with API credentials (e.g., OpenAI Vision or Google OCR)

### Installation

```bash
git clone https://github.com/your-username/ariadne-smartglasses.git
cd ariadne-smartglasses
bun install
cp .env.example .env  # Add API keys
ngrok http 3000       # Share server endpoint
```

Register your ngrok URL and set display/mic permissions in the AugmentOS Developer Console.

---

## 📁 Project Structure

```bash
ariadne-smartglasses/
├── src/
│   ├── app.js          # Voice command handler
│   ├── scene.js        # Scene description
│   ├── ocr.js          # OCR sign reading
│   ├── spatial.js      # Object detection with directional mapping
│   └── utils.js        # Clockface logic + API helpers
├── .env.example        # API config
├── package.json
└── README.md
```

---

## 🧠 Step-by-Step Tutorial

### 1️⃣ Scene Description

```js
const image = await session.camera.capture();
const caption = await OpenAICaptionAPI(image);
await session.audio.speak(`Scene: ${caption}`);
```

---

### 2️⃣ Sign Reader

```js
const image = await session.camera.capture();
const text = await performOCR(image);
await session.audio.speak(`The sign says: ${text}`);
```

---

### 3️⃣ Object Awareness

```js
const objects = await detectObjects(image);
const directions = objects.map(obj => `There is a ${obj.label} at ${toClockDirection(obj.x)}`);
await session.audio.speak(directions.join(" "));
```

---

### 4️⃣ Voice Commands

```js
session.on('transcription', async (evt) => {
  const t = evt.transcript.toLowerCase();
  if (t.includes('describe')) await describeScene(session);
  if (t.includes('read')) await readSign(session);
  if (t.includes('around')) await describeObjects(session);
});
```

---

## 🔁 Enhancements

- [ ] Add vibration cue support  
- [ ] Chained commands (e.g., “Describe then read”)  
- [ ] Offline ML fallback with ONNX models

---

## 🌐 Resources

- [AugmentOS SDK](https://docs.augmentos.org)  
- [OpenAI GPT-Vision](https://platform.openai.com/docs/guides/vision)  
- [Google Vision API](https://cloud.google.com/vision)  
- [BLIP Captioning Model](https://github.com/salesforce/BLIP)  
- [YOLO for Object Detection](https://github.com/ultralytics/yolov5)

---

## 🤝 Contributing

Pull requests welcome! Suggestions for accessibility and features are encouraged.

```bash
git checkout -b feature/my-feature
# Make changes
open a PR 🚀
```

---

## 🙏 Acknowledgments

- Inspired by the global visually impaired community  
- Thanks to the open-source AI and accessibility ecosystem

> “The world needs to be built for everyone. We just made it a little more audible.”
