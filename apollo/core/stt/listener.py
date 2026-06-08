"""
apollo/core/stt/listener.py
============================================================
Speech-to-Text: records audio after the wake word fires and
returns the transcribed text to the NLP engine.

Supports two backends, configured via STT_BACKEND in .env:
    - "google"  → Google Cloud Speech API (online, fast)
    - "whisper" → OpenAI Whisper (offline, ~1.5GB model)

Key design decisions:
    - Records ONLY after wake word fires (not continuous recording)
    - Adjusts for ambient noise before each recording
    - Returns None on failure instead of raising, so the pipeline
      can gracefully tell the user "I didn't catch that"

Usage:
    listener = SpeechListener(backend="google")
    text = listener.listen()
    if text:
        print(f"You said: {text}")
    else:
        print("Didn't catch that — try again")
============================================================
"""

import logging
from typing import Optional

import speech_recognition as sr

logger = logging.getLogger(__name__)


class SpeechListener:
    """
    Records one voice command after the wake word fires and
    returns it as a text string.
    """

    def __init__(
        self,
        backend: str = "google",
        timeout: float = 5.0,
        phrase_limit: float = 10.0,
    ):
        """
        Args:
            backend:      STT backend to use: "google" or "whisper".
                          Set via STT_BACKEND in .env.
            timeout:      Seconds to wait for speech to start.
                          If user doesn't speak within this time → return None.
            phrase_limit: Max seconds to record a single command.
                          Prevents Apollo from listening forever if user walks away.
        """
        self._backend = backend
        self._timeout = timeout
        self._phrase_limit = phrase_limit
        self._recognizer = sr.Recognizer()

        # Tune these to reduce false positives in noisy environments
        # energy_threshold: minimum audio energy to consider as speech
        # dynamic_energy_threshold: auto-adjust based on ambient noise
        self._recognizer.dynamic_energy_threshold = True
        self._recognizer.pause_threshold = 0.8  # Seconds of silence = end of phrase

    def listen(self) -> Optional[str]:
        """
        Record audio from the microphone and return transcribed text.

        This is a blocking call — it returns only after the user finishes
        speaking or the timeout is reached.

        Returns:
            Transcribed text string if successful.
            None if no speech detected or transcription failed.
        """
        logger.info("STT: Listening for command...")

        with sr.Microphone() as source:
            # Adjust for ambient noise for 0.3s before recording
            # This prevents background noise from being mistaken for speech
            logger.debug("STT: Calibrating for ambient noise...")
            self._recognizer.adjust_for_ambient_noise(source, duration=0.3)

            try:
                # Record until silence is detected or phrase_limit reached
                audio = self._recognizer.listen(
                    source,
                    timeout=self._timeout,           # Wait this long for speech to start
                    phrase_time_limit=self._phrase_limit,  # Max recording length
                )
                logger.debug("STT: Audio captured, sending to backend...")

            except sr.WaitTimeoutError:
                # User said the wake word but didn't follow with a command
                logger.warning("STT: No speech detected within timeout.")
                return None

        # Transcribe the recorded audio
        return self._transcribe(audio)

    def _transcribe(self, audio: sr.AudioData) -> Optional[str]:
        """
        Send audio to the configured STT backend and return the text.

        Args:
            audio: Recorded audio data from the microphone.

        Returns:
            Transcribed string, or None on failure.
        """
        try:
            if self._backend == "google":
                # Google Speech Recognition — free, online, no API key needed for basic use
                # For high volume, get a Google Cloud API key and pass it as:
                # sr.recognize_google(audio, key="your_key")
                text = self._recognizer.recognize_google(audio)

            elif self._backend == "whisper":
                # OpenAI Whisper — runs entirely offline on-device
                # Model is downloaded automatically on first use (~1.5GB for "base" model)
                # Model options: tiny, base, small, medium, large (bigger = slower + more accurate)
                text = self._recognizer.recognize_whisper(audio, model="base")

            else:
                logger.error(f"STT: Unknown backend '{self._backend}'. Use 'google' or 'whisper'.")
                return None

            logger.info(f"STT result: '{text}'")
            return text.lower().strip()  # Normalize: lowercase and trim whitespace

        except sr.UnknownValueError:
            # Audio was recorded but couldn't be understood (mumbled, too quiet, etc.)
            logger.warning("STT: Speech unintelligible.")
            return None

        except sr.RequestError as e:
            # Network error or Google API issue (only affects online backends)
            logger.error(f"STT: Backend request failed: {e}")
            return None
