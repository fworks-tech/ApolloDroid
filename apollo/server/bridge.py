"""Local bridge adapter around ApolloService.

This module keeps the transport boundary separate from the assistant core.
It is intentionally transport-agnostic so an HTTP server, React Native bridge,
or local desktop UI can all reuse the same service API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apollo.background.service import ApolloService

from .models import ApolloCommandRequest, ApolloCommandResponse, ApolloStatus


class LocalBridge:
    """Thin adapter between UI/transport layers and ApolloService."""

    def __init__(self, service: ApolloService):
        self._service = service

    def status(self) -> ApolloStatus:
        """Return the current operational status of Apollo."""
        snapshot = self._service.get_status()
        return ApolloStatus(
            ready=bool(snapshot["service_running"]),
            service_running=bool(snapshot["service_running"]),
            pipeline_active=bool(snapshot["pipeline_active"]),
            stt_backend=str(snapshot["stt_backend"]),
            anthropic_model=str(snapshot["anthropic_model"]),
        )

    def submit_command(self, request: ApolloCommandRequest) -> ApolloCommandResponse:
        """Send a recognized text command into the assistant pipeline."""
        response = self._service.process_text_command(
            request.command,
            acknowledge=request.acknowledge,
        )

        if response is None:
            return ApolloCommandResponse(
                ok=False,
                command=request.command,
                source=request.source,
                error="Apollo is busy or unavailable right now.",
            )

        return ApolloCommandResponse(
            ok=True,
            command=request.command,
            action=response.action,
            reply=response.reply,
            params=response.params,
            source=request.source,
        )