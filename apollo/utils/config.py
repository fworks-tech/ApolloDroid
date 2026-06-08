"""
apollo/utils/config.py
============================================================
Configuration loader for ApolloDroid.

Reads API keys and settings from the .env file and exposes
them as a clean typed dataclass — no raw os.getenv() calls
scattered across the codebase.

Usage:
    config = ApolloConfig.load()
    print(config.anthropic_api_key)
============================================================
"""

import os
import logging
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


@dataclass
class ApolloConfig:
    """
    All runtime configuration for ApolloDroid.
    Loaded once at startup from .env file.

    Do not instantiate directly — use ApolloConfig.load().
    """

    # ---- API Keys ----
    picovoice_access_key: str    # Required: Porcupine wake word engine
    anthropic_api_key: str       # Required: Claude NLP brain

    # ---- Model / Backend ----
    anthropic_model: str         # Claude model ID (haiku = fast/cheap, sonnet = smarter)
    stt_backend: str             # "google" (online) or "whisper" (offline)

    # ---- Wake Word ----
    wake_word_model_path: str    # Path to .ppn file in ui/assets/
    wake_word_sensitivity: float # 0.0–1.0, default 0.5

    # ---- STT ----
    stt_timeout: float           # Seconds to wait for speech to start after wake word
    stt_phrase_limit: float      # Max seconds to record one command

    # ---- TTS ----
    tts_rate: int                # Speech rate in words per minute
    tts_volume: float            # Volume 0.0–1.0

    # ---- App ----
    debug: bool                  # Enable verbose debug logging

    @classmethod
    def load(cls, env_path: str | Path = ".env") -> "ApolloConfig":
        """
        Load configuration from the .env file.

        Args:
            env_path: Path to the .env file. Defaults to .env in the working directory.

        Returns:
            Populated ApolloConfig instance.

        Raises:
            ValueError: If required API keys are missing from .env.
        """
        # Load .env file into environment variables
        load_dotenv(dotenv_path=env_path)

        # Validate required keys before building the config object
        picovoice_key = os.getenv("PICOVOICE_ACCESS_KEY", "")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

        if not picovoice_key:
            raise ValueError(
                "PICOVOICE_ACCESS_KEY is missing from .env.\n"
                "Get a free key at: https://console.picovoice.ai/"
            )

        if not anthropic_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is missing from .env.\n"
                "Get a key at: https://console.anthropic.com/"
            )

        config = cls(
            # ---- Required API keys ----
            picovoice_access_key=picovoice_key,
            anthropic_api_key=anthropic_key,

            # ---- Model / Backend (with sensible defaults) ----
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
            stt_backend=os.getenv("STT_BACKEND", "google"),

            # ---- Wake word ----
            wake_word_model_path=os.getenv(
                "WAKE_WORD_MODEL_PATH",
                "ui/assets/hey_apollo_android.ppn"
            ),
            wake_word_sensitivity=float(os.getenv("WAKE_WORD_SENSITIVITY", "0.5")),

            # ---- STT ----
            stt_timeout=float(os.getenv("STT_TIMEOUT", "5.0")),
            stt_phrase_limit=float(os.getenv("STT_PHRASE_LIMIT", "10.0")),

            # ---- TTS ----
            tts_rate=int(os.getenv("TTS_RATE", "175")),
            tts_volume=float(os.getenv("TTS_VOLUME", "1.0")),

            # ---- App ----
            debug=os.getenv("DEBUG", "false").lower() == "true",
        )

        if config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.debug("Debug logging enabled.")
        else:
            logging.basicConfig(level=logging.INFO)

        logger.info("Configuration loaded successfully.")
        return config
