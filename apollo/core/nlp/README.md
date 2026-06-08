# 🧠 core/nlp

The **AI brain** of Apollo. Takes the transcribed text from STT and uses Claude to understand intent, extract details, and generate a response or action.

## Requirements

| Requirement | Details |
|-------------|---------|
| `anthropic==0.29.0` | Official Anthropic Python SDK |
| `ANTHROPIC_API_KEY` | Set in `.env` — get at [console.anthropic.com](https://console.anthropic.com/) |
| `ANTHROPIC_MODEL` | Set in `.env` — default: `claude-haiku-4-5-20251001` |
| Internet connection | Required — Claude API is cloud-based |

---

## How it works

```
"set alarm for 7am tomorrow"
    ↓
Claude API (with system prompt defining Apollo's skills)
    ↓
Structured response: { "action": "alarm", "time": "07:00", "day": "+1" }
    ↓
Dispatcher routes to features/alarm
    ↓
Apollo says: "Alarm set for 7am tomorrow"
```

## Files

| File | Purpose |
|------|---------|
| `brain.py` | `ApolloBrain` class — sends commands to Claude, parses structured responses |
| `prompts.py` | System prompts that define Apollo's personality and available skills |
| `__init__.py` | Exports `ApolloBrain` as the public API |

## Model choice

Set `ANTHROPIC_MODEL` in `.env`:

| Model | Speed | Cost | Best for |
|-------|-------|------|---------|
| `claude-haiku-4-5-20251001` | Fast (~0.5s) | Cheapest | Most commands — recommended |
| `claude-sonnet-4-20250514` | Medium (~1.5s) | Medium | Complex, ambiguous commands |

Haiku handles most voice commands perfectly fine. Use Sonnet only if you find Haiku misunderstanding complex instructions.

## Context window

Apollo sends the last N commands as conversation history so Claude has context for follow-up commands like "make it 8am instead."

## Next step

Brain response → `features/` dispatcher routes to the correct skill handler.
