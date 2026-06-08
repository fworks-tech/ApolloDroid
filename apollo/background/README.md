# 🔄 background

The **always-on service** that keeps Apollo alive even when the screen is off or the user switches to another app.

## Requirements

| Requirement | Details |
|-------------|---------|
| Python `threading` | Built-in — no install needed |
| `plyer==2.1.0` | Android notification API (foreground service notification) |
| `FOREGROUND_SERVICE` permission | Declared in `pyproject.toml` — granted automatically |
| `POST_NOTIFICATIONS` permission | Required on Android 13+ — prompted at runtime |

---

## Why a foreground service?

Android aggressively kills background processes to save battery. A **Foreground Service** is an exception — it must show a persistent notification, but in exchange Android promises not to kill it.

This is the same mechanism used by Spotify, Google Maps, and phone call apps.

```
App launched
    ↓
ApolloService starts (foreground service with notification)
    ↓
WakeWordDetector starts on background thread
    ↓
User locks screen / switches apps
    ↓
Android: "Can I kill this process?" → No, it's a foreground service ✋
    ↓
Apollo keeps listening indefinitely
```

## Files

| File | Purpose |
|------|---------|
| `service.py` | `ApolloService` — orchestrates the full pipeline, runs as a Kivy Android Service |
| `boot_receiver.py` | Restarts the service automatically after phone reboot |
| `__init__.py` | Package exports |

## Pipeline orchestration

`ApolloService` wires together all core modules:

```
WakeWordDetector
    → on_detection callback
        → Speaker.speak("I'm listening")
        → SpeechListener.listen() → transcribed text
        → ApolloBrain.process(text) → ApolloResponse
        → FeatureDispatcher.dispatch(response) → action executed
        → Speaker.speak(response.reply)
        → back to listening
```

## Stopping the service

The service stops when:
- User explicitly disables Apollo in Settings
- User force-stops the app in Android settings
- Device runs critically low on memory (last resort by Android)

After a reboot, `boot_receiver.py` restarts it automatically.
