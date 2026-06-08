# ⚡ features

Apollo's **skills** — the actions it can take after the NLP brain identifies an intent.

Each feature is a self-contained module with a single `execute(params)` method.
The background service dispatcher routes NLP responses here based on the `action` field.

---

## Available skills

| Folder | Action key | Example command |
|--------|-----------|----------------|
| `alarm/` | `"alarm"` | "Set an alarm for 7am tomorrow" |
| `timer/` | `"timer"` | "Set a timer for 10 minutes" |
| `search/` | `"search"` | "Search for the best Python books" |
| `weather/` | `"weather"` | "What's the weather in Miami?" |

---

## Requirements

| Requirement | Details |
|-------------|---------|
| `plyer==2.1.0` | Android alarm, notification, and vibration API |
| `requests==2.32.3` | HTTP for weather and search features |
| `OPENWEATHER_API_KEY` | Optional — set in `.env` for weather skill |
| `python-dateutil==2.9.0` | Smart date/time parsing for alarms |

---

## Adding a new skill

1. Create a folder: `apollo/features/myskill/`
2. Add `__init__.py` and `myskill.py` with a class that has `execute(params: dict) -> str`
3. Add the action key to `core/nlp/prompts.py` so Claude knows about it
4. Add a dispatch case in `background/service.py`

That's it — Apollo will automatically route matching commands to your new skill.

---

## Folder structure

```
features/
├── alarm/
│   ├── alarm.py        # AlarmFeature.execute() — schedules an Android alarm
│   └── README.md
├── timer/
│   ├── timer.py        # TimerFeature.execute() — countdown timer
│   └── README.md
├── search/
│   ├── search.py       # SearchFeature.execute() — web search
│   └── README.md
└── weather/
    ├── weather.py      # WeatherFeature.execute() — current weather
    └── README.md
```
