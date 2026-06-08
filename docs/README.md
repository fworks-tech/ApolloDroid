# 📚 docs

Architecture guides and implementation references for ApolloDroid.

## Contents

| File | Description |
|------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full system diagram and data flow |
| [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) | Deployment strategy, bridge layer, and release rules |
| [ROADMAP.md](ROADMAP.md) | Milestones for Android, React Native, live talking, and iOS |

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Android Device                      │
│                                                      │
│  ┌──────────┐    ┌──────────────────────────────┐   │
│  │  Kivy UI │    │     ApolloService (BG)        │   │
│  │  (main   │◄───│                              │   │
│  │  screen, │    │  ┌─────────────────────────┐ │   │
│  │  settings│    │  │  WakeWordDetector        │ │   │
│  └──────────┘    │  │  (Porcupine, always-on) │ │   │
│                  │  └────────────┬────────────┘ │   │
│                  │               │ "Hey Apollo!" │   │
│                  │  ┌────────────▼────────────┐ │   │
│                  │  │  SpeechListener (STT)   │ │   │
│                  │  │  Google / Whisper       │ │   │
│                  │  └────────────┬────────────┘ │   │
│                  │               │ "set alarm…" │   │
│                  │  ┌────────────▼────────────┐ │   │
│                  │  │  ApolloBrain (NLP)      │ │   │
│                  │  │  Claude API             │ │   │
│                  │  └────────────┬────────────┘ │   │
│                  │               │ {action,reply}│   │
│                  │  ┌────────────▼────────────┐ │   │
│                  │  │  Feature Dispatcher     │ │   │
│                  │  │  alarm/timer/search/… │ │   │
│                  │  └────────────┬────────────┘ │   │
│                  │               │               │   │
│                  │  ┌────────────▼────────────┐ │   │
│                  │  │  Speaker (TTS)          │ │   │
│                  │  │  pyttsx3 / Android TTS  │ │   │
│                  │  └─────────────────────────┘ │   │
│                  └──────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
              ▲                    ▲
              │                    │
    ┌─────────┴──────┐   ┌─────────┴──────┐
    │  Picovoice     │   │  Anthropic     │
    │  (wake word)   │   │  Claude API    │
    └────────────────┘   └────────────────┘
```

## Data flow summary

1. **Idle** — WakeWordDetector runs continuously on background thread, consuming ~1% CPU
2. **Triggered** — "Hey Apollo" detected → pipeline activates
3. **Listen** — STT records and transcribes the command (~1–3s)
4. **Think** — Claude API processes command, returns action + reply (~0.5–1.5s)
5. **Act** — Feature handler executes the action (set alarm, fetch weather, etc.)
6. **Speak** — TTS speaks the reply aloud (~0.5–2s)
7. **Back to idle** — WakeWordDetector resumes listening

## Key design principles

- **Offline where possible** — wake word detection never touches the internet
- **Fail gracefully** — every pipeline step handles errors and tells the user what happened
- **Non-blocking** — all heavy work (audio, API calls) runs on background threads
- **Modular** — each core module can be swapped independently (e.g. switch STT backend)
