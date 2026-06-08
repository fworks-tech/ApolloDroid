# 🧠 apollo/core

The **core engine** of Apollo — the low-level components that handle audio and intelligence.
All features (alarms, weather, search) are built on top of these four modules.

## Modules

| Module | Responsibility |
|--------|---------------|
| `wakeword/` | Listens for "Hey Apollo" 24/7 using Porcupine (offline) |
| `stt/` | Converts spoken audio → text after wake word fires |
| `nlp/` | Sends text to Claude API → gets intent + response |
| `tts/` | Converts Apollo's text response → spoken audio |

## Data flow

```
Microphone (always on)
    │
    ▼
[wakeword] ── "Hey Apollo" detected ──▶ [stt] ── "Set alarm for 7am" ──▶ [nlp]
                                                                              │
                                                              intent + response text
                                                                              │
                                                                          [tts] ──▶ 🔊 Speaker
```

## Design principles

- **Core modules are pure Python** — no Kivy, no Android-specific code here.
  This makes them testable on your desktop without a phone.
- Each module is a **class with a simple interface** — easy to swap implementations
  (e.g. replace Google STT with Whisper offline without touching other modules).
- All audio I/O is handled via callbacks or queues — core never blocks the UI thread.
