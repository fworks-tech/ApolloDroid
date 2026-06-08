"""Minimal localhost HTTP transport for ApolloDroid.

This server is intentionally small and dependency-free so the assistant core
can be exercised from desktop tooling or a future mobile bridge without adding
another web framework yet.
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .bridge import LocalBridge
from .models import ApolloCommandRequest


class ApolloHTTPServer:
    """Run a local JSON API around ApolloDroid's bridge layer."""

    def __init__(self, bridge: LocalBridge, host: str = "127.0.0.1", port: int = 5000):
        self._bridge = bridge
        self._host = host
        self._port = port
        self._server = self._build_server()
        self._thread: threading.Thread | None = None

    @property
    def address(self) -> tuple[str, int]:
        """Return the bound host and port."""
        host, port = self._server.server_address
        return str(host), int(port)

    def start(self) -> None:
        """Start serving requests on a daemon thread."""
        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the server and wait briefly for the thread to exit."""
        self._server.shutdown()
        self._server.server_close()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _build_server(self) -> ThreadingHTTPServer:
        bridge = self._bridge

        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                if self.path == "/api/status":
                    self._write_json(HTTPStatus.OK, asdict(bridge.status()))
                    return

                self._write_json(
                    HTTPStatus.NOT_FOUND,
                    {"ok": False, "error": "Not found"},
                )

            def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
                if self.path != "/api/command":
                    self._write_json(
                        HTTPStatus.NOT_FOUND,
                        {"ok": False, "error": "Not found"},
                    )
                    return

                payload = self._read_json_body()
                if payload is None:
                    self._write_json(
                        HTTPStatus.BAD_REQUEST,
                        {"ok": False, "error": "Invalid JSON body"},
                    )
                    return

                command = str(payload.get("command", "")).strip()
                if not command:
                    self._write_json(
                        HTTPStatus.BAD_REQUEST,
                        {"ok": False, "error": "command is required"},
                    )
                    return

                request = ApolloCommandRequest(
                    command=command,
                    source=str(payload.get("source", "http")),
                    acknowledge=bool(payload.get("acknowledge", False)),
                )
                response = bridge.submit_command(request)
                status = HTTPStatus.OK if response.ok else HTTPStatus.SERVICE_UNAVAILABLE
                self._write_json(status, asdict(response))

            def log_message(self, format: str, *args: Any) -> None:
                # Keep the default HTTP server quiet; Apollo logging handles status.
                return

            def _read_json_body(self) -> dict[str, Any] | None:
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                except ValueError:
                    return None

                body = self.rfile.read(content_length) if content_length > 0 else b"{}"
                try:
                    decoded = body.decode("utf-8") if body else "{}"
                    parsed = json.loads(decoded)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    return None

                return parsed if isinstance(parsed, dict) else None

            def _write_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
                encoded = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        return ThreadingHTTPServer((self._host, self._port), RequestHandler)