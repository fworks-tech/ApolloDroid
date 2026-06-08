"""
apollo/background/service.py
============================================================
ApolloService — the main orchestrator that runs as an
Android Foreground Service, wiring together all core modules
into a single always-on voice assistant pipeline.

How it works:
    1. Start is called by the Kivy UI when the app launches
    2. A foreground service notification is posted (required by Android)
    3. WakeWordDetector starts on a background thread
    4. On each "Hey Apollo" detection, the pipeline runs:
           wake word → STT → NLP → feature dispatch → TTS
    5. After TTS, we return to idle wake word listening

Threading model:
    - Wake word loop:  dedicated daemon thread (always running)
    - STT + NLP + TTS: run on the same callback thread sequentially
      (blocking is fine since we don't want to detect wake word mid-command)
============================================================
"""

import logging
import threading
from typing import Optional

from apollo.core.wakeword import WakeWordDetector
from apollo.core.stt import SpeechListener
from apollo.core.nlp import ApolloBrain, ApolloResponse
from apollo.core.tts import Speaker
from apollo.utils.config import ApolloConfig

logger = logging.getLogger(__name__)


class ApolloService:
    """
    Orchestrates the full Apollo voice assistant pipeline.
    Designed to run as a long-lived service on Android.
    """

    def __init__(self, config: ApolloConfig):
        """
        Args:
            config: Loaded configuration (API keys, model, STT backend, sensitivity).
                    Populated from .env by ApolloConfig.
        """
        self._config = config
        self._is_active = False          # True when pipeline is processing (post-wake-word)
        self._pipeline_lock = threading.Lock()  # Prevents overlapping pipeline runs

        # Initialize all core modules
        self._speaker = Speaker(
            rate=config.tts_rate,
            volume=config.tts_volume,
        )

        self._stt = SpeechListener(
            backend=config.stt_backend,
            timeout=config.stt_timeout,
            phrase_limit=config.stt_phrase_limit,
        )

        self._brain = ApolloBrain(
            api_key=config.anthropic_api_key,
            model=config.anthropic_model,
        )

        self._wake_detector = WakeWordDetector(
            access_key=config.picovoice_access_key,
            model_path=config.wake_word_model_path,
            on_detection=self._on_wake_word,
            sensitivity=config.wake_word_sensitivity,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Start the Apollo service.
        Posts a foreground notification and begins wake word detection.
        Call this once from the Kivy app or Android service entry point.
        """
        logger.info("🚀 ApolloService starting...")
        self._post_foreground_notification()
        self._wake_detector.start()
        logger.info("✅ Apollo is ready. Listening for 'Hey Apollo'...")

    def stop(self) -> None:
        """
        Gracefully shut down Apollo.
        Stops wake word detection and releases all audio resources.
        """
        logger.info("ApolloService stopping...")
        self._wake_detector.stop()
        self._speaker.stop()
        logger.info("ApolloService stopped.")

    def get_status(self) -> dict[str, object]:
        """Return a lightweight snapshot of the service state for UI or bridge layers."""
        return {
            "service_running": self._wake_detector.is_running,
            "pipeline_active": self._is_active,
            "stt_backend": self._config.stt_backend,
            "anthropic_model": self._config.anthropic_model,
        }

    def process_text_command(
        self,
        command_text: str,
        *,
        acknowledge: bool = False,
    ) -> Optional[ApolloResponse]:
        """
        Process a text command without using the wake-word listener.

        This is the bridge-friendly entry point used by UI layers that already
        have a recognized command and want Apollo to run the same NLP → dispatch
        → TTS flow as the microphone pipeline.
        """
        if not self._pipeline_lock.acquire(blocking=False):
            logger.debug("Pipeline already running — ignoring external command.")
            return None

        try:
            return self._process_text_command_locked(
                command_text,
                acknowledge=acknowledge,
            )
        finally:
            self._pipeline_lock.release()

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    def _on_wake_word(self) -> None:
        """
        Called by WakeWordDetector on its audio thread when "Hey Apollo" fires.

        We use a lock to ensure only one pipeline runs at a time — if the user
        says "Hey Apollo" again while Apollo is already processing, we ignore it.
        """
        if not self._pipeline_lock.acquire(blocking=False):
            logger.debug("Pipeline already running — ignoring duplicate wake word.")
            return

        try:
            self._run_pipeline_locked()
        finally:
            # Always release the lock so future wake words are processed
            self._pipeline_lock.release()

    def _run_pipeline_locked(self) -> None:
        """
        Execute the full command pipeline:
            1. Acknowledge (so user knows Apollo heard them)
            2. Listen for the command (STT)
            3. Process command (NLP via Claude)
            4. Execute skill (feature dispatch)
            5. Speak the reply (TTS)
        """
        # Step 1: Acknowledge — give user immediate audio feedback
        self._speaker.speak("I'm listening.")

        # Step 2: Record and transcribe the command
        command_text = self._stt.listen()

        if not command_text:
            # User spoke the wake word but didn't follow with a command
            self._speaker.speak("Sorry, I didn't catch that.")
            return

        self._process_text_command_locked(command_text, acknowledge=False)

    def _process_text_command_locked(
        self,
        command_text: str,
        *,
        acknowledge: bool,
    ) -> Optional[ApolloResponse]:
        """Process an already-recognized command while the pipeline lock is held."""
        self._is_active = True

        try:
            if acknowledge:
                self._speaker.speak("I'm listening.")

            logger.info(f"Command: '{command_text}'")

            # Step 3: Process command with Claude
            response = self._brain.process(command_text)

            if not response:
                # Network error or API failure
                self._speaker.speak("I'm having trouble connecting right now. Please try again.")
                return None

            # Step 4: Dispatch to the appropriate feature handler
            # (Feature dispatcher will be implemented in features/)
            self._dispatch(response)

            # Step 5: Speak the response back to the user
            self._speaker.speak(response.reply)
            return response
        finally:
            self._is_active = False

    def _dispatch(self, response) -> None:
        """
        Route the NLP response to the correct feature handler.
        This is a stub — feature handlers will be implemented in apollo/features/.
        """
        action = response.action
        params = response.params

        logger.info(f"Dispatching action: '{action}' with params: {params}")

        # TODO: Import and call feature handlers as they're implemented
        # Example:
        # if action == "alarm":
        #     from apollo.features.alarm import AlarmFeature
        #     AlarmFeature().execute(params)
        # elif action == "timer":
        #     from apollo.features.timer import TimerFeature
        #     TimerFeature().execute(params)

        if action == "none":
            pass  # Claude already composed a conversational reply — just speak it

    # ------------------------------------------------------------------
    # Android foreground notification
    # ------------------------------------------------------------------

    def _post_foreground_notification(self) -> None:
        """
        Post the persistent notification required for Android Foreground Services.

        Android requires any foreground service to show a notification so the
        user is aware the app is running in the background. Without this,
        Android will kill the service after a few minutes.

        Uses plyer for cross-platform notification API.
        On desktop (dev), this is a no-op.
        """
        try:
            from plyer import notification
            notification.notify(
                title="Apollo is active",
                message="Say 'Hey Apollo' to give a command",
                app_name="ApolloDroid",
                # app_icon="ui/assets/apollo_icon.ico",  # Uncomment when icon is ready
                timeout=0,  # 0 = persistent (don't auto-dismiss)
            )
            logger.debug("Foreground notification posted.")
        except Exception as e:
            # On desktop or if plyer isn't available — non-fatal
            logger.debug(f"Could not post notification (non-Android env?): {e}")
