"""Typed request and response models for bridge-style integrations."""

from dataclasses import dataclass, field


@dataclass
class ApolloCommandRequest:
    """A command submitted by a UI or transport layer."""

    command: str
    source: str = "ui"
    acknowledge: bool = False


@dataclass
class ApolloCommandResponse:
    """Structured response returned after a command is processed."""

    ok: bool
    command: str
    action: str = "none"
    reply: str = ""
    params: dict = field(default_factory=dict)
    source: str = "ui"
    error: str = ""


@dataclass
class ApolloStatus:
    """Lightweight operational status for bridge consumers."""

    ready: bool
    service_running: bool
    pipeline_active: bool
    stt_backend: str
    anthropic_model: str