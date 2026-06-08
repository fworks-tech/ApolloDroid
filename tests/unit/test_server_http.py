from __future__ import annotations

import json
from http.client import HTTPConnection

import pytest

pytest.importorskip("apollo.server", reason="apollo.server not yet available on this branch")
from apollo.server import ApolloCommandResponse, ApolloHTTPServer, ApolloStatus, LocalBridge


class FakeBridge:
    def __init__(self) -> None:
        self.submitted = []

    def status(self) -> ApolloStatus:
        return ApolloStatus(
            ready=True,
            service_running=True,
            pipeline_active=False,
            stt_backend="google",
            anthropic_model="claude-haiku-4-5-20251001",
        )

    def submit_command(self, request):
        self.submitted.append(request)
        return ApolloCommandResponse(
            ok=True,
            command=request.command,
            action="none",
            reply="done",
            params={},
            source=request.source,
        )


def test_http_bridge_status_and_command_round_trip():
    fake_bridge = FakeBridge()
    bridge = LocalBridge(fake_bridge)
    server = ApolloHTTPServer(bridge, port=0)

    connection = None
    try:
        server.start()
        host, port = server.address

        connection = HTTPConnection(host, port, timeout=5)

        connection.request("GET", "/api/status")
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["ready"] is True
        assert payload["service_running"] is True

        connection.request(
            "POST",
            "/api/command",
            body=json.dumps({"command": "hello apollo", "source": "test"}),
            headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        payload = json.loads(response.read().decode("utf-8"))

        assert response.status == 200
        assert payload["ok"] is True
        assert payload["command"] == "hello apollo"
        assert payload["reply"] == "done"
        assert fake_bridge.submitted[0].command == "hello apollo"
    finally:
        if connection is not None:
            connection.close()
        server.stop()