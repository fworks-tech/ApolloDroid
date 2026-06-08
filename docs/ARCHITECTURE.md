# 🏗️ Architecture Overview

## System diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Android Device                        │
│                                                             │
│  ┌──────────────┐        ┌──────────────────────────────┐  │
│  │   Kivy UI    │        │    ApolloService (Thread)    │  │
│  │              │        │                              │  │
│  │ MainScreen   │◀──────▶│  WakeWordDetector (always on)│  │
│  │ Settings     │ events │         │                    │  │
│  └──────────────┘        │         ▼ "Hey Apollo"       │  │
│                          │  SpeechListener (records)    │  │
│                          │         │                    │  │
│                          │         ▼ transcribed text   │  │
│                          │  NLPBrain → Claude API ────▶ 🌐│  │
│                          │         │                    │  │
│                          │         ▼ intent + response  │  │
│                          │  FeatureRouter               │  │
│                          │  ├── AlarmFeature            │  │
│                          │  ├── TimerFeature            │  │
│                          │  ├── WeatherFeature ───────▶ 🌐│  │
│                          │  └── SearchFeature ────────▶ 🌐│  │
│                          │         │                    │  │
│                          │         ▼ response text      │  │
│                          │  Speaker (TTS → audio out)   │  │
│                          └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component responsibilities

### Kivy UI (`ui/`)
- Displays Apollo's status (idle / listening / thinking / speaking)
- Settings screen for API keys, sensitivity, language
- Communicates with ApolloService via thread-safe events

### ApolloService (`apollo/background/service.py`)
- Runs on a dedicated thread — never touches the UI
- Owns the full pipeline: wake word → STT → NLP → feature → TTS
- Uses a state machine: `IDLE → LISTENING → PROCESSING → SPEAKING → IDLE`

### Core pipeline (`apollo/core/`)
- Each module has one job and a simple interface
- Designed to be testable in isolation (no Android dependencies)
- Swappable: e.g. replace Google STT with Whisper without changing other modules

### Features (`apollo/features/`)
- Stateless handlers — receive intent data, return response text
- Each feature declares what intents it handles
- New skills can be added without modifying existing code

## Threading model

```
Main Thread (Kivy event loop)
    └── UI rendering, touch events, screen updates

ApolloService Thread (daemon)
    └── Wake word loop → STT → NLP → Feature → TTS
        (all blocking calls happen here, not on main thread)
```

## Data flow example: "Hey Apollo, set a timer for 5 minutes"

```
1. WakeWordDetector  →  detects "Hey Apollo"  →  fires callback
2. SpeechListener    →  records "set a timer for 5 minutes"
3. NLPBrain          →  sends to Claude API
                     ←  returns { intent: "set_timer", duration_seconds: 300 }
4. FeatureRouter     →  routes to TimerFeature.handle()
5. TimerFeature      →  starts countdown, returns "Timer set for 5 minutes"
6. Speaker           →  speaks "Timer set for 5 minutes" aloud
7. UI                →  updates to show active timer
```
