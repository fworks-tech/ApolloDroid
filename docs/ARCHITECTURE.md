# 🏗️ Architecture Overview

## System diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ApolloDroid Runtime (Windows / Android)           │
│                                                                     │
│  ┌─────────────────────┐        ┌──────────────────────────────┐   │
│  │     Kivy UI          │        │    ApolloService (Thread)    │   │
│  │                     │        │                              │   │
│  │  PresenceWindow     │◀──────▶│  WakeWordDetector (always on)│   │
│  │  MainScreen         │ events │         │                    │   │
│  │  SettingsScreen     │        │         ▼ "Hey Apollo"       │   │
│  └─────────────────────┘        │  SpeechListener (records)    │   │
│           ▲                     │         │                    │   │
│           │ HTTP (port 5000)    │         ▼ transcribed text   │   │
│  ┌─────────────────────┐        │  NLPBrain → Claude API ────▶ 🌐  │
│  │   apollo/server/    │        │         │                    │   │
│  │  ApolloHTTPServer   │◀──────▶│  FeatureRouter               │   │
│  │  LocalBridge        │        │  ├── AlarmFeature            │   │
│  └─────────────────────┘        │  ├── TimerFeature            │   │
│                                 │  ├── WeatherFeature ───────▶ 🌐  │
│                                 │  └── SearchFeature ────────▶ 🌐  │
│                                 │         │                    │   │
│                                 │         ▼ response text      │   │
│                                 │  Speaker (TTS → audio out)   │   │
│                                 └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component responsibilities

### Kivy UI (`ui/`)
- **PresenceWindow** — always-on-top window showing Apollo's current state (idle / listening / thinking / speaking) with chat history
- **MainScreen** — status display and waveform visualization
- **SettingsScreen** — API keys, sensitivity, language preferences
- Communicates with ApolloService via thread-safe events and the local HTTP bridge

### HTTP Bridge (`apollo/server/`)
- **ApolloHTTPServer** — lightweight HTTP server on port 5000
- **LocalBridge** — adapter connecting the HTTP layer to ApolloService
- **Models** — Pydantic request/response types (`ApolloCommandRequest`, `ApolloCommandResponse`, `ApolloStatus`)
- Decouples UI from the service — any client (UI, scripts, future React Native app) can talk to Apollo via HTTP

### ApolloService (`apollo/background/service.py`)
- Runs on a dedicated thread — never touches the UI
- Owns the full pipeline: wake word → STT → NLP → feature → TTS
- State machine: `IDLE → LISTENING → PROCESSING → SPEAKING → IDLE`

### Core pipeline (`apollo/core/`)
- Each module has one job and a simple interface
- Testable in isolation (no platform dependencies at the module level)
- Swappable: e.g. replace Google STT with Whisper without changing other modules

### Features (`apollo/features/`)
- Stateless handlers — receive intent data, return response text
- Each feature declares what intents it handles
- New skills can be added without modifying existing code

### Utils (`apollo/utils/`)
- **Config** (`config.py`) — loads `.env` into a typed `Config` object
- **Logger** (`logger.py`) — structured centralized logging

---

## Threading model

```
Main Thread (Kivy event loop)
    └── UI rendering, touch events, PresenceWindow updates

ApolloService Thread (daemon)
    └── Wake word loop → STT → NLP → Feature → TTS
        (all blocking calls happen here, not on main thread)

ApolloHTTPServer Thread (daemon)
    └── Handles HTTP requests from UI or external clients
        (runs independently of the audio pipeline thread)
```

---

## Data flow example: "Hey Apollo, set a timer for 5 minutes"

```
1. WakeWordDetector  →  detects "Hey Apollo"  →  fires callback
2. SpeechListener    →  records "set a timer for 5 minutes"
3. NLPBrain          →  sends to Claude API
                     ←  returns { intent: "set_timer", duration_seconds: 300 }
4. FeatureRouter     →  routes to TimerFeature.handle()
5. TimerFeature      →  starts countdown, returns "Timer set for 5 minutes"
6. Speaker           →  speaks "Timer set for 5 minutes" aloud
7. PresenceWindow    →  displays the reply as a chat bubble
```

---

## Platform support

| Layer | Windows | Android |
|-------|---------|---------|
| Wake word | pvporcupine (SAPI) | pvporcupine (Android audio) |
| STT | SpeechRecognition + Google | SpeechRecognition + Google |
| NLP | anthropic SDK | anthropic SDK |
| TTS | pyttsx3 (SAPI5) | plyer text_to_speech |
| UI | Kivy desktop window | Kivy Android app |
| Background | Python thread / `python -m apollo` | Android foreground service |
