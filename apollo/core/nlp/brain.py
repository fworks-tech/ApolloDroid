"""
apollo/core/nlp/brain.py
============================================================
The AI brain of Apollo — powered by the Claude API.

Takes transcribed text from the STT module and asks Claude
to understand the intent and produce a structured action
response that the feature dispatcher can route.

Design decisions:
    - Keeps a short conversation history for follow-up commands
      ("make it 8am instead", "cancel that", etc.)
    - Returns structured JSON so routing is deterministic
    - Separates the spoken reply from the action payload
    - Uses the cheapest/fastest model by default (Haiku)
      but lets the caller override per-request

Usage:
    brain = ApolloBrain(api_key="sk-ant-...", model="claude-haiku-4-5-20251001")
    result = brain.process("set an alarm for 7am tomorrow")
    # result.action   → "alarm"
    # result.params   → {"time": "07:00", "offset_days": 1}
    # result.reply    → "Alarm set for 7 AM tomorrow."
============================================================
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import anthropic

from .prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Maximum number of past exchanges to keep in conversation history.
# Older messages are dropped to stay within the context window and reduce cost.
MAX_HISTORY_TURNS = 6  # 6 exchanges = 12 messages (6 user + 6 assistant)


@dataclass
class ApolloResponse:
    """
    Structured response from the Claude API.

    Attributes:
        action: The skill to invoke (e.g. "alarm", "weather", "search", "none").
                "none" means Claude handled it conversationally (no feature needed).
        params: Key-value parameters for the action (e.g. time, query, city).
        reply:  The spoken response Apollo should say aloud.
        raw:    The full raw JSON string from Claude (for debugging).
    """
    action: str
    params: dict
    reply: str
    raw: str = ""


@dataclass
class ConversationTurn:
    """One exchange in the conversation history (user command + Apollo reply)."""
    user: str
    assistant: str


class ApolloBrain:
    """
    Processes voice commands using the Claude API and returns
    structured action + spoken reply pairs.
    """

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        """
        Args:
            api_key: Your Anthropic API key from .env.
            model:   Claude model to use. Haiku is fast and cheap for most commands.
                     Options: claude-haiku-4-5-20251001 | claude-sonnet-4-20250514
        """
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._history: list[ConversationTurn] = []  # Rolling conversation history

    def process(self, command: str) -> Optional[ApolloResponse]:
        """
        Send a voice command to Claude and get back a structured response.

        Args:
            command: Transcribed text from the STT module (e.g. "set alarm for 7am").

        Returns:
            ApolloResponse with action, params, and reply text.
            None if the API call fails.
        """
        logger.info(f"NLP processing: '{command}'")

        # Build the full message list: system context + history + new command
        messages = self._build_messages(command)

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=512,         # Voice commands rarely need long responses
                system=SYSTEM_PROMPT,   # Defines Apollo's personality and skills
                messages=messages,
            )

            raw_text = response.content[0].text
            logger.debug(f"Claude raw response: {raw_text}")

            # Parse the structured JSON Claude was instructed to return
            parsed = self._parse_response(raw_text)

            if parsed:
                # Save this exchange to history for follow-up command context
                self._add_to_history(command, raw_text)

            return parsed

        except anthropic.APIConnectionError:
            logger.error("NLP: No internet connection — Claude API unreachable.")
            return None
        except anthropic.AuthenticationError:
            logger.error("NLP: Invalid Anthropic API key. Check ANTHROPIC_API_KEY in .env.")
            return None
        except anthropic.APIError as e:
            logger.error(f"NLP: Claude API error: {e}")
            return None

    def clear_history(self) -> None:
        """Reset conversation history. Call this after a long silence or new topic."""
        self._history.clear()
        logger.debug("NLP: Conversation history cleared.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_messages(self, command: str) -> list[dict]:
        """
        Construct the messages array for the Claude API.
        Includes recent conversation history for follow-up context.
        """
        messages = []

        # Add past turns as alternating user/assistant messages
        for turn in self._history[-MAX_HISTORY_TURNS:]:
            messages.append({"role": "user", "content": turn.user})
            messages.append({"role": "assistant", "content": turn.assistant})

        # Add the new command
        messages.append({"role": "user", "content": command})

        return messages

    def _parse_response(self, raw: str) -> Optional[ApolloResponse]:
        """
        Parse Claude's JSON response into an ApolloResponse object.

        Claude is instructed (via system prompt) to always return JSON like:
            {
                "action": "alarm",
                "params": { "time": "07:00", "offset_days": 1 },
                "reply": "Alarm set for 7 AM tomorrow."
            }
        """
        try:
            data = json.loads(raw)
            return ApolloResponse(
                action=data.get("action", "none"),
                params=data.get("params", {}),
                reply=data.get("reply", "Done."),
                raw=raw,
            )
        except json.JSONDecodeError:
            # Claude sometimes adds a short preamble before the JSON — try to extract it
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    data = json.loads(raw[start:end])
                    return ApolloResponse(
                        action=data.get("action", "none"),
                        params=data.get("params", {}),
                        reply=data.get("reply", "Done."),
                        raw=raw,
                    )
                except json.JSONDecodeError:
                    pass

            logger.error(f"NLP: Failed to parse Claude JSON: {raw[:200]}")
            # Return a graceful fallback so Apollo says something rather than silent failure
            return ApolloResponse(
                action="none",
                params={},
                reply="Sorry, I had trouble understanding that. Could you try again?",
                raw=raw,
            )

    def _add_to_history(self, user_message: str, assistant_message: str) -> None:
        """Add a completed exchange to history, pruning if over the limit."""
        self._history.append(ConversationTurn(user=user_message, assistant=assistant_message))
        # Keep only the most recent turns to manage context window size
        if len(self._history) > MAX_HISTORY_TURNS:
            self._history.pop(0)
