# 🗺️ Roadmap

## Near-term

### v1.0 Android stabilization
- Finish alarm, timer, weather, and search feature handlers.
- Complete the main screen and settings screen.
- Add unit and integration tests for the core assistant flow.
- Harden startup, shutdown, and background service behavior.

### v1.1 Core quality
- Improve config validation and error handling.
- Add better logging and command tracing.
- Expand automated tests around wake word, STT, and NLP routing.

## Platform expansion

### v1.5 React Native bridge
- Introduce a local HTTP bridge around the Python assistant core.
- Build a shared React Native UI for Android and iOS.
- Keep command processing in Python while the UI becomes cross-platform.

### v1.5 Live Talking
- Add streaming transcription.
- Add lower-latency partial responses.
- Support continuous conversation mode with short-lived context.

### v2.0 iOS release
- Ship the assistant on iOS using the same core logic.
- Validate permissions, audio handling, and background execution on Apple devices.
- Tune the UI and transport layer for iOS-specific constraints.

## Longer-term

### v2.1 Production polish
- Add release automation.
- Add crash and session diagnostics.
- Tighten security boundaries around local bridge traffic.

### v2.2 Extended assistant skills
- Add more feature agents.
- Improve command routing and natural language handling.
- Continue growing the onboarding and troubleshooting docs.

## Milestone principles

- Android stabilization comes first.
- React Native is a shared UI strategy, not a rewrite of the assistant core.
- Live talking is an incremental capability that builds on the bridge layer.
- iOS follows once the bridge and mobile assistant flows are stable.