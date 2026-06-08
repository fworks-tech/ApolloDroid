"""
apollo/core/tts/speaker.py
============================================================
Text-to-Speech: converts Apollo's text replies into spoken audio.

Uses pyttsx3 on desktop (dev machine) and routes through
plyer on Android (which uses the system TTS engine).

Design notes:
    - Speech runs on a background thread to avoid blocking
      the pipeline while Apollo is talking
    - Supports interrupt: if a new command arrives while Apollo
      is speaking, the current speech is stopped
    - Rate and volume are configurable via settings

Usage:
    speaker = Speaker(rate=175, volume=1.0)
    speaker.speak("Alarm set for 7 AM tomorrow.")
    speaker.stop()  # interrupt if mid-sentence
============================================================
"""

import logging
import threading
import platform

logger = logging.getLogger(__name__)


class Speaker:
    """
    Speaks text aloud using the platform's TTS engine.
    Non-blocking — speech runs on a background thread.
    """

    def __init__(self, rate: int = 175, volume: float = 1.0):
        """
        Args:
            rate:   Speech rate in words per minute (default: 175).
                    Range: 50 (very slow) to 300 (very fast).
            volume: Volume from 0.0 (silent) to 1.0 (full, default).
        """
        self._rate = rate
        self._volume = volume
        self._engine = None
        self._speaking = False
        self._lock = threading.Lock()

        self._init_engine()

    def speak(self, text: str) -> None:
        """
        Speak the given text aloud on a background thread.
        If already speaking, stops the current speech first.

        Args:
            text: The text Apollo should say aloud.
        """
        if not text:
            return

        # Stop any ongoing speech before starting new one
        self.stop()

        logger.info(f"TTS: Speaking: '{text}'")

        thread = threading.Thread(
            target=self._speak_blocking,
            args=(text,),
            daemon=True,
            name="TTSSpeakerThread",
        )
        thread.start()

    def stop(self) -> None:
        """Interrupt any currently playing speech."""
        if self._speaking and self._engine:
            try:
                self._engine.stop()
            except Exception as e:
                logger.warning(f"TTS: Error stopping engine: {e}")
            self._speaking = False

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _init_engine(self) -> None:
        """
        Initialize the TTS engine for the current platform.

        On Android: pyttsx3 uses Android's built-in TTS engine (Google TTS or Samsung TTS)
        On macOS:   pyttsx3 uses the 'say' command
        On Linux:   pyttsx3 uses espeak (install: sudo apt install espeak)
        On Windows: pyttsx3 uses SAPI5
        """
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self._rate)
            self._engine.setProperty("volume", self._volume)
            logger.debug(f"TTS: Engine initialized on {platform.system()}")
        except Exception as e:
            logger.error(f"TTS: Failed to initialize engine: {e}")
            self._engine = None

    def _speak_blocking(self, text: str) -> None:
        """
        Synchronously speak the text. Called on a background thread.
        pyttsx3's runAndWait() blocks until speech is complete.
        """
        if not self._engine:
            logger.warning("TTS: Engine not available — cannot speak.")
            return

        with self._lock:  # Prevent concurrent speech from two threads
            self._speaking = True
            try:
                self._engine.say(text)
                self._engine.runAndWait()  # Blocks thread until done speaking
            except Exception as e:
                logger.error(f"TTS: Speech error: {e}")
            finally:
                self._speaking = False
