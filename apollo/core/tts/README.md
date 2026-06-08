# 🔊 core/tts

Handles **Text-to-Speech** — Apollo's voice. Converts Claude's text reply into spoken audio on the device.

## Requirements

| Requirement | Details |
|-------------|---------|
| `pyttsx3==2.90` | Offline TTS engine |
| `plyer==2.1.0` | Android TTS bridge (used on-device) |
| No API key needed | TTS runs entirely offline |

### Platform notes

| Platform | TTS Engine Used |
|----------|----------------|
| Windows (dev + v0.2.0 target) | SAPI5 via `pyttsx3` — works out of the box |
| Android (device) | Android system TTS via `plyer` — **pyttsx3 is not used on Android** |
| macOS (dev) | `say` command via `pyttsx3` |
| Linux (dev) | `espeak` via `pyttsx3` — install: `sudo apt install espeak` |

> **Android note:** `pyttsx3` cannot drive Android's audio stack. On Android, `Speaker` uses `plyer.tts` instead. This swap is handled by the platform detection in `speaker.py`.

---

## Files

| File | Purpose |
|------|---------|
| `speaker.py` | `Speaker` class — speaks a text string aloud |
| `__init__.py` | Exports `Speaker` as the public API |

## Voice settings

Configurable in `config/settings.py`:
- **Rate** — speech speed (words per minute), default: 175
- **Volume** — 0.0 to 1.0, default: 1.0
- **Voice** — system voice ID (platform-dependent)

## Next step

After Apollo speaks the reply → returns to idle, waiting for next "Hey Apollo".
