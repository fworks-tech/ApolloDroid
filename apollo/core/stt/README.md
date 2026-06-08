# 🗣️ core/stt

Handles **Speech-to-Text** — converts your spoken command (after "Hey Apollo") into a text string that the NLP engine can process.

## Requirements

| Requirement | Details |
|-------------|---------|
| `SpeechRecognition==3.10.4` | STT wrapper library |
| `pyaudio==0.2.14` | Microphone input after wake word |
| Internet connection | Required for Google STT backend (default) |
| `RECORD_AUDIO` permission | Already requested by wake word module |

### Optional: Offline STT (Whisper)

To use OpenAI Whisper instead of Google (no internet needed):

```bash
pip install openai-whisper torch
```

Then set in `.env`:
```
STT_BACKEND=whisper
```

> ⚠️ Whisper downloads a ~1.5GB model on first use. Not ideal for low-storage phones — Google STT is recommended for mobile.

---

## How it works

```
Wake word fires
    ↓
STT starts listening (adjusts for ambient noise)
    ↓
User speaks command ("set alarm for 7am")
    ↓ silence detected = end of command
Google Speech API (or Whisper)
    ↓
"set alarm for 7am"  → passed to core/nlp
```

## Files

| File | Purpose |
|------|---------|
| `listener.py` | `SpeechListener` class — records audio after wake word, returns transcribed text |
| `__init__.py` | Exports `SpeechListener` as the public API |

## Backends

| Backend | Pros | Cons | Config |
|---------|------|------|--------|
| **Google** (default) | Fast, accurate, free | Requires internet | `STT_BACKEND=google` |
| **Whisper** | Fully offline, very accurate | Large model, slower on phone | `STT_BACKEND=whisper` |

## Timeout settings

The listener stops recording when:
- Silence is detected after speech (phrase timeout)
- Maximum recording time is reached (prevents infinite listening)

Both are configurable in `config/settings.py`.

## Next step

Transcribed text → `core/nlp` to understand intent and generate a response.
