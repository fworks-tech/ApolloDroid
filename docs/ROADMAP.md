# 🗺️ Roadmap

## Active

### v0.2.0 — Talk to Apollo (Windows desktop)
The first end-to-end voice conversation experience — running as a background process on Windows.

- Wire the background service pipeline loop (detect → listen → think → speak)
- Add `python -m apollo` Windows desktop entry point
- Add Porcupine wake word model file (`hey_apollo_windows.ppn`)
- Build the Apollo presence window: always-on-top chat UI with listening/thinking/response states
- Desktop integration smoke test

> Tracked as **[Milestone 0: v0.2.0 — Talk to Apollo](https://github.com/fworks-tech/ApolloDroid/milestone/6)**

---

## Near-term

### v1.0 — Android stabilization
- Port the wired pipeline to Android via Briefcase
- Replace pyttsx3 with plyer TTS for Android
- Implement runtime mic + internet permission request on first launch
- Finish alarm, timer, weather, and search feature handlers ([#6](https://github.com/fworks-tech/ApolloDroid/issues/6)–[#10](https://github.com/fworks-tech/ApolloDroid/issues/10))
- Harden startup, shutdown, and background service behavior

### v1.1 — Skills & Commands
Complete the second tier of built-in skills:
- Smart home control via Home Assistant ([#6](https://github.com/fworks-tech/ApolloDroid/issues/6))
- WhatsApp / SMS dictation ([#7](https://github.com/fworks-tech/ApolloDroid/issues/7))
- Calendar & reminders via Google Calendar ([#8](https://github.com/fworks-tech/ApolloDroid/issues/8))
- Spotify / YouTube music control ([#9](https://github.com/fworks-tech/ApolloDroid/issues/9))
- On-the-fly spoken translation ([#10](https://github.com/fworks-tech/ApolloDroid/issues/10))

### v1.2 — Differentiators
What sets ApolloDroid apart:
- Privacy mode: local wake-word + offline fallback ([#11](https://github.com/fworks-tech/ApolloDroid/issues/11))
- Configurable assistant persona and voice ([#12](https://github.com/fworks-tech/ApolloDroid/issues/12))
- Session memory: Claude remembers past conversations ([#13](https://github.com/fworks-tech/ApolloDroid/issues/13))
- Brazilian Portuguese as a first-class language ([#14](https://github.com/fworks-tech/ApolloDroid/issues/14))

---

## Platform expansion

### v1.5 — React Native bridge
- Shared React Native UI for Android and iOS
- Keep command processing in Python, expose via local HTTP bridge (already built)
- Streaming Claude responses to reduce perceived latency ([#15](https://github.com/fworks-tech/ApolloDroid/issues/15))
- Offline response cache for no-network scenarios ([#16](https://github.com/fworks-tech/ApolloDroid/issues/16))

### v1.5 — Live Talking
- Streaming transcription and partial responses
- Continuous conversation mode with short-lived context

### v2.0 — iOS release
- Ship on iOS using the same Python core
- Validate permissions, audio handling, and background execution on Apple devices

---

## Longer-term

### v2.1 — Production polish
- Release automation, crash diagnostics, session telemetry
- Tighten security boundaries around local bridge traffic

### v2.2 — Extended skills
- More feature agents and improved command routing
- Expanded onboarding and troubleshooting docs

---

## Milestone principles

- Windows desktop first — prove the pipeline end-to-end without packaging overhead
- Android follows once the pipeline is solid
- React Native is a shared UI strategy, not a rewrite of the assistant core
- Live talking builds on the existing HTTP bridge layer
- iOS follows once bridge and mobile flows are stable
