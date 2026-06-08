# 🔊 ApolloDroid

> Your personal voice assistant for Android — 100% Python, built by you.

ApolloDroid is a Python-based Android voice assistant that listens for **"Hey Apollo"**,
processes your voice commands, and responds intelligently — packaged as a real Android APK
using Kivy + Briefcase. No Android Studio required.

---

## ✨ Features

- 🎙️ **Wake word detection** — Always listening for "Hey Apollo" (offline, low battery)
- 🗣️ **Speech-to-text** — Converts your voice to commands in real time
- 🧠 **AI-powered NLP** — Understands natural language via Claude API
- 🔊 **Text-to-speech** — Apollo talks back to you
- ⏰ **Built-in skills** — Alarms, timers, weather, web search, and more
- 🔄 **Always-on background service** — Runs persistently on your Android device

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
pip install -r requirements.txt
```

### 4. Add your API keys
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

### 5. Run on desktop first (for testing)
```bash
briefcase dev
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
│   ├── server/                 # Local bridge layer for UI and future transports
│   ├── features/               # Apollo skills (what Apollo can DO)
│   │   ├── alarm/              # Set and manage alarms
│   │   ├── timer/              # Countdown timers
│   │   ├── search/             # Web search
│   │   └── weather/            # Weather lookups
│   ├── background/             # Persistent background service
│   └── utils/                  # Shared helpers and config
├── ui/                         # Kivy UI layer
│   ├── screens/                # App screens (main, settings, onboarding)
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
| Text-to-speech | [pyttsx3](https://pypi.org/project/pyttsx3/) | Offline TTS, works cross-platform |
| Async | Python `asyncio` + `threading` | Background audio loop |
| Config | [python-dotenv](https://pypi.org/project/python-dotenv/) | Loads .env API keys |

---

## 📋 Roadmap

### ✅ Done — Scaffold & Core Engine
- [x] Project structure, `.gitignore`, `.env.example`
- [x] `pyproject.toml` — Briefcase/Android config with all permissions
- [x] `requirements.txt` + `requirements-dev.txt`
- [x] `scripts/setup.sh` — one-command dev environment setup
- [x] `.github/workflows/ci.yml` — GitHub Actions CI (lint, type check, test)
- [x] `docs/ARCHITECTURE.md` — full system diagram
- [x] `apollo/app.py` — Kivy App entry point
- [x] `apollo/core/wakeword/detector.py` — Porcupine wake word loop
- [x] `apollo/core/stt/listener.py` — Speech-to-text pipeline
- [x] `apollo/core/tts/speaker.py` — Text-to-speech output
- [x] `apollo/core/nlp/brain.py` + `prompts.py` — Claude API brain
- [x] `apollo/background/service.py` — always-on background thread
- [x] `apollo/utils/config.py` + `logger.py` — config and logging
- [x] READMEs for every folder

### 🔲 Up Next — tracked as GitHub Issues
- [ ] [#1] Implement `features/alarm/` — set, list, cancel alarms
- [ ] [#2] Implement `features/timer/` — countdown timers with TTS alert
- [ ] [#3] Implement `features/weather/` — OpenWeatherMap integration
- [ ] [#4] Implement `features/search/` — web search + summarize result
- [ ] [#5] Build `ui/screens/main_screen.py` — status display + waveform
- [ ] [#6] Build `ui/screens/settings_screen.py` — API keys, sensitivity, language
- [ ] [#7] Unit tests for all core modules
- [ ] [#8] Integration test for full pipeline end-to-end
- [ ] [#9] Onboarding flow — mic permission + first-time API key setup
- [ ] [#10] Play Store release prep — icons, screenshots, store listing

### 🚧 Next Milestones
- [ ] **v1.0 Android stabilization** — complete the assistant, UI, and feature set
- [ ] **v1.5 React Native bridge** — shared mobile UI for Android + iOS with the Python core behind a local bridge
- [ ] **v1.5 Live Talking** — real-time transcription, streaming responses, and continuous conversation mode
- [ ] **v2.0 iOS launch** — production-ready iOS build once the bridge and live talking flow are stable

> 📌 See all open issues at [github.com/fworks-tech/ApolloDroid/issues](https://github.com/fworks-tech/ApolloDroid/issues)

## 📚 Project Docs

- [Architecture overview](docs/ARCHITECTURE.md)
- [Production deployment](docs/PRODUCTION_DEPLOYMENT.md)
- [Roadmap](docs/ROADMAP.md)

---

## 📄 License

Proprietary / All Rights Reserved — see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Fabio Ritzel Borges.
