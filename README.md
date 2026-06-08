# 🔊 ApolloDroid

> Your personal voice assistant for Android — 100% Python, built by you.

ApolloDroid is a Python-based voice assistant that listens for **"Hey Apollo"**,
processes your voice commands, and responds intelligently — packaged as a real Android APK
using Kivy + Briefcase. No Android Studio required.

---

## ✨ Features

- 🎙️ **Wake word detection** — Always listening for "Hey Apollo" (offline, low battery)
- 🗣️ **Speech-to-text** — Converts your voice to commands in real time
- 🧠 **AI-powered NLP** — Understands natural language via Claude API
- 🔊 **Text-to-speech** — Apollo talks back to you
- ⏰ **Built-in skills** — Alarms, timers, weather, web search, and more
- 🔄 **Always-on background service** — Runs persistently on your device
- 💬 **Presence window** — See Apollo listening and responding in a live chat UI

---

## 🛠️ Requirements

### Your Development Machine (PC/Mac/Linux)

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Java JDK | 17+ | Required by Briefcase to build the Android APK |
| Android SDK | API 26+ | Auto-installed by Briefcase on first build |
| Git | Any | For version control |
| pip | Latest | Comes with Python — run `pip install --upgrade pip` |

> **Java JDK install:** [Adoptium JDK 17](https://adoptium.net/) is free and works on Windows/Mac/Linux.
> Briefcase will handle the Android SDK automatically — you do NOT need Android Studio.

### Your Android Phone

| Requirement | Notes |
|-------------|-------|
| Android 8.0+ (API 26) | Minimum supported version |
| USB Debugging enabled | Settings → Developer Options → USB Debugging |
| ~200MB free storage | For the app + Python runtime |

### API Keys (free tiers available)

| Service | Purpose | Get it at |
|---------|---------|-----------|
| Picovoice | Wake word "Hey Apollo" | [console.picovoice.ai](https://console.picovoice.ai/) |
| Anthropic | NLP brain (Claude API) | [console.anthropic.com](https://console.anthropic.com/) |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/fworks-tech/ApolloDroid.git
cd ApolloDroid
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Activate it:
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements-dev.txt
```

### 4. Add your API keys
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

### 5. Run on desktop (Windows/Mac/Linux)
```bash
python -m apollo
```

### 6. Build and deploy to Android
```bash
briefcase create android   # First time only — downloads Android SDK (~5 min)
briefcase build android
briefcase run android      # Phone must be connected via USB with debugging on
```

---

## 🏗️ Project Structure

```
ApolloDroid/
├── apollo/                     # Core Python application package
│   ├── core/                   # Engine: wake word, STT, TTS, NLP
│   │   ├── wakeword/           # Porcupine wake word detection
│   │   ├── stt/                # Speech-to-text pipeline
│   │   ├── tts/                # Text-to-speech output
│   │   └── nlp/                # Claude API integration (the "brain")
│   ├── server/                 # Local HTTP bridge (port 5000) for UI ↔ service
│   ├── features/               # Apollo skills (what Apollo can DO)
│   │   ├── alarm/              # Set and manage alarms
│   │   ├── timer/              # Countdown timers
│   │   ├── search/             # Web search
│   │   └── weather/            # Weather lookups
│   ├── background/             # Persistent background service
│   └── utils/                  # Shared helpers and config
├── ui/                         # Kivy UI layer
│   ├── screens/                # App screens (main, settings, presence window)
│   ├── widgets/                # Reusable UI components
│   └── assets/                 # Icons, fonts, images
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests (no device needed)
│   └── integration/            # Integration tests
├── docs/                       # Architecture diagrams and guides
├── scripts/                    # Dev helper scripts
├── pyproject.toml              # Briefcase config — defines the Android APK
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Dev-only dependencies (testing, linting)
└── .env.example                # Template for API keys
```

---

## 🧩 Tech Stack

| Component | Library | Why |
|-----------|---------|-----|
| UI framework | [Kivy](https://kivy.org/) | Cross-platform, runs on Android natively |
| Android packaging | [Briefcase](https://briefcase.readthedocs.io/) | Converts Python app → real Android APK |
| Wake word | [pvporcupine](https://pypi.org/project/pvporcupine/) | Offline, tiny, accurate |
| Speech-to-text | [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) | Easy Google STT integration |
| NLP / Brain | [anthropic](https://pypi.org/project/anthropic/) | Claude API Python SDK |
| Text-to-speech | [pyttsx3](https://pypi.org/project/pyttsx3/) / [plyer](https://pypi.org/project/plyer/) | pyttsx3 on desktop, plyer on Android |
| Async | Python `asyncio` + `threading` | Background audio loop |
| Config | [python-dotenv](https://pypi.org/project/python-dotenv/) | Loads .env API keys |

---

## 📋 Roadmap

### ✅ Done — v0.1.0 Initial Foundation
- [x] Project structure, CI, `.gitignore`, `.env.example`
- [x] `pyproject.toml` — Briefcase/Android config with all permissions
- [x] `requirements.txt` + `requirements-dev.txt`
- [x] `scripts/setup.sh` — one-command dev environment setup
- [x] `.github/workflows/ci.yml` — GitHub Actions CI (lint, type check, test)
- [x] `docs/ARCHITECTURE.md` + `docs/ROADMAP.md` — full system diagram
- [x] `apollo/app.py` — Kivy App entry point
- [x] `apollo/core/wakeword/detector.py` — Porcupine wake word loop
- [x] `apollo/core/stt/listener.py` — Speech-to-text pipeline
- [x] `apollo/core/tts/speaker.py` — Text-to-speech output
- [x] `apollo/core/nlp/brain.py` + `prompts.py` — Claude API brain
- [x] `apollo/background/service.py` — always-on background thread
- [x] `apollo/server/` — local HTTP bridge on port 5000
- [x] `apollo/utils/config.py` + `logger.py` — config and logging
- [x] `ui/screens/` — main screen + settings screen (Kivy)

### 🔲 Up Next — v0.2.0 Talk to Apollo

> Tracked as GitHub issues in [Milestone v0.2.0](https://github.com/fworks-tech/ApolloDroid/milestone/6)

- [ ] Wire background service pipeline loop (detect → listen → think → speak)
- [ ] Add `python -m apollo` Windows desktop entry point
- [ ] Add Porcupine wake word model file (`hey_apollo_windows.ppn`)
- [ ] Build Apollo presence window (chat UI with listening/thinking/response states)
- [ ] Desktop smoke test for full pipeline

### 🔲 Backlog — Skills & Commands

> Tracked as [GitHub Issues #6–#10](https://github.com/fworks-tech/ApolloDroid/issues)

- [ ] [#6] Smart home control via Home Assistant API
- [ ] [#7] WhatsApp / SMS dictation
- [ ] [#8] Calendar & reminders via Google Calendar API
- [ ] [#9] Spotify / YouTube music control
- [ ] [#10] On-the-fly spoken translation

### 🔲 Backlog — Differentiators

> Tracked as [GitHub Issues #11–#14](https://github.com/fworks-tech/ApolloDroid/issues)

- [ ] [#11] Privacy mode: local wake-word + offline fallback
- [ ] [#12] Configurable assistant persona and voice
- [ ] [#13] Session memory: Claude remembers past conversations
- [ ] [#14] Brazilian Portuguese as a first-class language

### 🚧 Milestones

| Milestone | Goal |
|-----------|------|
| [v0.2.0 — Talk to Apollo](https://github.com/fworks-tech/ApolloDroid/milestone/6) | Full voice pipeline running on Windows desktop |
| [Milestone 1: Core Pipeline](https://github.com/fworks-tech/ApolloDroid/milestone/1) | Android packaging and on-device testing |
| [Milestone 2: Skills & Commands](https://github.com/fworks-tech/ApolloDroid/milestone/2) | Smart home, messaging, calendar, music, translation |
| [Milestone 3: Differentiators](https://github.com/fworks-tech/ApolloDroid/milestone/3) | Privacy mode, personas, session memory, Portuguese |
| [Milestone 4: Technical Quality](https://github.com/fworks-tech/ApolloDroid/milestone/4) | Streaming responses, offline cache, test coverage |

> 📌 See all open issues at [github.com/fworks-tech/ApolloDroid/issues](https://github.com/fworks-tech/ApolloDroid/issues)

## 📚 Project Docs

- [Architecture overview](docs/ARCHITECTURE.md)
- [Production deployment](docs/PRODUCTION_DEPLOYMENT.md)
- [Roadmap](docs/ROADMAP.md)

---

## 📄 License

Proprietary / All Rights Reserved — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Fabio Ritzel Borges.
