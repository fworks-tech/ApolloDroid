# 🎙️ core/wakeword

Handles **offline, always-listening wake word detection** — the "Hey Apollo" trigger.

## Requirements

| Requirement | Details |
|-------------|---------|
| `pvporcupine==3.0.1` | Picovoice Porcupine Python SDK |
| `pyaudio==0.2.14` | Low-level microphone I/O |
| **Picovoice access key** | Free at [console.picovoice.ai](https://console.picovoice.ai/) — set `PICOVOICE_ACCESS_KEY` in `.env` |
| **Wake word model** | `hey_apollo_android.ppn` — train free at Picovoice Console, place in `ui/assets/` |
| `RECORD_AUDIO` permission | Must be granted at runtime on Android |

### PyAudio system dependencies

PyAudio wraps PortAudio — you need the native library installed on your dev machine:

```bash
# macOS
brew install portaudio

# Ubuntu / Debian / WSL2
sudo apt install portaudio19-dev python3-dev

# Windows (use WSL2 instead)
# Or: pip install pipwin && pipwin install pyaudio
```

> On Android, Porcupine uses its own native audio layer — PyAudio is not needed on the device.

---

## How it works

```
Microphone
    ↓ raw PCM bytes (16kHz, 16-bit mono)
PyAudio stream
    ↓ 512-sample frames (~32ms each)
Porcupine engine  ← tiny neural net runs entirely on-device
    ↓ keyword_index >= 0
WakeWordDetector callback
    ↓
STT pipeline activated
```

## Files

| File | Purpose |
|------|---------|
| `detector.py` | `WakeWordDetector` class — wraps Porcupine, runs detection loop on background thread |
| `__init__.py` | Exports `WakeWordDetector` as the public API |

## Battery impact

Porcupine is designed for always-on use. It consumes ~1–2% CPU on modern Android devices. The heavier STT and NLP pipelines only activate **after** the wake word fires.

## Training your own model

1. Go to [console.picovoice.ai](https://console.picovoice.ai/)
2. Sign in (free account)
3. Create a new wake word → type "Hey Apollo"
4. Select platform: **Android**
5. Download the `.ppn` file
6. Rename to `hey_apollo_android.ppn` and place in `ui/assets/`

## Sensitivity tuning

Set `WAKE_WORD_SENSITIVITY` in `.env` (0.0–1.0):

- **0.3–0.4** — Only detects when you speak clearly and close to the phone
- **0.5** — Good balance (recommended starting point)
- **0.7–0.8** — Very responsive but may trigger on similar sounds

## Next step

When wake word fires → `core/stt` takes over for full speech recognition.
