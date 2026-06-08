"""
apollo/core/wakeword/detector.py
============================================================
Wake word detection using Picovoice Porcupine.

What this does:
    Continuously reads PCM audio frames from the microphone
    and feeds them to the Porcupine engine. When Porcupine
    detects "Hey Apollo", it calls the registered callback.

Key concepts:
    - Porcupine processes audio in fixed-size "frames"
      (512 samples at 16kHz = ~32ms per frame)
    - PyAudio handles the raw microphone I/O
    - Detection runs on a background thread so it never
      blocks the Kivy UI thread

Requirements:
    - PICOVOICE_ACCESS_KEY in .env
    - hey_apollo_android.ppn model in ui/assets/
    - RECORD_AUDIO permission granted at runtime on Android

Usage:
    detector = WakeWordDetector(
        access_key="your_key",
        model_path="ui/assets/hey_apollo_android.ppn",
        on_detection=lambda: print("Hey Apollo detected!")
    )
    detector.start()   # begins background thread
    # ... later ...
    detector.stop()    # releases mic and engine
============================================================
"""

import threading
import logging
from typing import Callable
from pathlib import Path

import pvporcupine
import pyaudio

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Always-on wake word detector that calls a callback when
    "Hey Apollo" is detected in the microphone audio stream.

    Runs entirely on a daemon thread — it will automatically
    stop when the main process exits.
    """

    def __init__(
        self,
        access_key: str,
        model_path: str | Path,
        on_detection: Callable[[], None],
        sensitivity: float = 0.5,
    ):
        """
        Args:
            access_key:   Your Picovoice access key (from .env).
            model_path:   Path to the .ppn wake word model file.
                          Train your own at console.picovoice.ai.
            on_detection: Callback fired every time "Hey Apollo"
                          is detected. Called from the audio thread.
            sensitivity:  Detection sensitivity, 0.0–1.0.
                          Higher = more sensitive but more false positives.
                          Recommended: 0.4–0.6 for indoor use.
        """
        self._access_key = access_key
        self._model_path = str(model_path)
        self._on_detection = on_detection
        self._sensitivity = sensitivity

        # Internal state
        self._porcupine = None      # Porcupine engine instance
        self._audio_stream = None   # PyAudio microphone stream
        self._pa = None             # PyAudio instance
        self._thread = None         # Background detection thread
        self._running = False       # Flag to stop the thread cleanly

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Initialize Porcupine and the microphone, then start the
        detection loop on a background daemon thread.

        Safe to call multiple times — does nothing if already running.
        """
        if self._running:
            logger.warning("WakeWordDetector is already running.")
            return

        logger.info("Initializing Porcupine wake word engine...")
        self._init_porcupine()
        self._init_audio()

        self._running = True

        # daemon=True means this thread dies automatically when the app exits
        self._thread = threading.Thread(
            target=self._detection_loop,
            name="WakeWordDetectorThread",
            daemon=True,
        )
        self._thread.start()
        logger.info("Wake word detection started. Listening for 'Hey Apollo'...")

    def stop(self) -> None:
        """
        Stop the detection loop and release microphone + engine resources.
        Blocks briefly until the detection thread finishes its current frame.
        """
        logger.info("Stopping wake word detection...")
        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)  # Wait up to 2s for clean shutdown

        self._cleanup()
        logger.info("Wake word detection stopped.")

    @property
    def is_running(self) -> bool:
        """True if the detection loop is currently active."""
        return self._running

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _init_porcupine(self) -> None:
        """
        Create the Porcupine engine with the custom "Hey Apollo" model.

        keyword_paths: list of paths to .ppn model files.
                       Each .ppn = one wake phrase.
        sensitivities: one sensitivity value per keyword_path.
        """
        self._porcupine = pvporcupine.create(
            access_key=self._access_key,
            keyword_paths=[self._model_path],
            sensitivities=[self._sensitivity],
        )
        logger.debug(
            f"Porcupine initialized | sample_rate={self._porcupine.sample_rate}Hz "
            f"| frame_length={self._porcupine.frame_length} samples"
        )

    def _init_audio(self) -> None:
        """
        Open a PyAudio input stream configured to match Porcupine's
        exact requirements: 16kHz, 16-bit mono PCM.

        Porcupine is strict about these values — any mismatch causes
        garbled or missed detections.
        """
        self._pa = pyaudio.PyAudio()
        self._audio_stream = self._pa.open(
            rate=self._porcupine.sample_rate,    # Must be 16000 Hz
            channels=1,                           # Mono — Porcupine requires single channel
            format=pyaudio.paInt16,               # 16-bit signed PCM
            input=True,                           # This is a microphone input stream
            frames_per_buffer=self._porcupine.frame_length,  # Read exactly one frame at a time
        )
        logger.debug("PyAudio microphone stream opened.")

    def _detection_loop(self) -> None:
        """
        Main audio processing loop. Runs on the background thread.

        Each iteration:
          1. Read one audio frame from the microphone (~32ms of audio)
          2. Feed it to Porcupine
          3. If Porcupine returns >= 0, a wake word was detected
          4. Call the user's callback
        """
        logger.debug("Detection loop started.")

        while self._running:
            try:
                # Read raw PCM bytes from the microphone
                pcm_bytes = self._audio_stream.read(
                    self._porcupine.frame_length,
                    exception_on_overflow=False,  # Skip frames on buffer overflow (busy system)
                )

                # Convert raw bytes → list of 16-bit integers Porcupine expects
                pcm_frame = list(
                    int.from_bytes(pcm_bytes[i:i+2], byteorder="little", signed=True)
                    for i in range(0, len(pcm_bytes), 2)
                )

                # Process the frame — returns index of detected keyword, or -1 for no detection
                keyword_index = self._porcupine.process(pcm_frame)

                if keyword_index >= 0:
                    # keyword_index matches the index in keyword_paths list
                    # Since we only have one keyword ("Hey Apollo"), index 0 = detection
                    logger.info("🎙️ Wake word detected!")
                    self._on_detection()

            except OSError as e:
                # Audio stream errors (device disconnected, permission revoked, etc.)
                logger.error(f"Audio stream error: {e}")
                break

        logger.debug("Detection loop exited.")

    def _cleanup(self) -> None:
        """Release all audio and Porcupine resources."""
        if self._audio_stream:
            self._audio_stream.stop_stream()
            self._audio_stream.close()
            self._audio_stream = None

        if self._pa:
            self._pa.terminate()
            self._pa = None

        if self._porcupine:
            self._porcupine.delete()
            self._porcupine = None
