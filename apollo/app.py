# apollo/app.py
# ============================================================
# Apollo's main entry point — the Kivy App class.
#
# Briefcase calls `main()` at the bottom of this file when the
# APK launches. From here, the Kivy event loop takes over and
# manages the UI lifecycle. The background service (always-on
# microphone + wake word) is started as a separate thread so
# it never blocks the UI.
# ============================================================

import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from apollo.background.service import ApolloService
from apollo.server import ApolloHTTPServer, LocalBridge
from apollo.utils.config import ApolloConfig
from apollo.utils.logger import get_logger
from ui.screens.main_screen import MainScreen
from ui.screens.settings_screen import SettingsScreen

logger = get_logger(__name__)


class ApolloApp(App):
    """
    The root Kivy application class.

    Kivy calls:
      - build()     → when the app first starts (return the root UI widget)
      - on_start()  → after the UI is ready (good place to start background work)
      - on_stop()   → when the app is closing (clean up resources)
      - on_pause()  → when the app goes to the background on Android
      - on_resume() → when the app comes back to the foreground
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load config (API keys, settings) from .env file
        self.config_data = ApolloConfig.load()

        # The background service runs on its own thread so the UI stays responsive
        self.service = ApolloService(config=self.config_data)
        self.bridge = LocalBridge(self.service)
        self.http_server = ApolloHTTPServer(self.bridge, host="127.0.0.1", port=5000)
        self._service_thread: threading.Thread | None = None

    def build(self) -> ScreenManager:
        """
        Called by Kivy to construct the UI.
        Returns the root widget — a ScreenManager that holds all screens.
        """
        self.title = "Apollo"

        # ScreenManager handles switching between app screens
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(SettingsScreen(name="settings"))

        return sm

    def on_start(self) -> None:
        """
        Called after the UI is fully built and displayed.
        This is where we start the background listening service.
        """
        logger.info("Apollo starting up...")
        self._start_background_services()

    def on_stop(self) -> None:
        """
        Called when the app is about to close.
        We must stop the background service and release the microphone.
        """
        logger.info("Apollo shutting down...")
        self.http_server.stop()
        self.service.stop()

        if self._service_thread and self._service_thread.is_alive():
            self._service_thread.join(timeout=3.0)

    def on_pause(self) -> bool:
        """
        Called on Android when the user presses Home or switches apps.
        Return True to allow the app to pause (instead of stopping fully).
        The background service keeps running even when the UI is paused.
        """
        logger.info("Apollo paused (still listening in background)")
        return True  # Keep running in background

    def on_resume(self) -> None:
        """Called when the user returns to the app after a pause."""
        logger.info("Apollo resumed")

    def _start_background_services(self) -> None:
        """
        Starts ApolloService and the local HTTP bridge on a background thread.
        Daemon=True means this thread dies automatically when the app closes,
        acting as a safety net in case on_stop() isn't called cleanly.
        """
        self._service_thread = threading.Thread(
            target=self._start_services,
            name="ApolloServicesThread",
            daemon=True,
        )
        self._service_thread.start()
        logger.info("Background services thread started")

    def _start_services(self) -> None:
        """Start the assistant service and the localhost bridge server."""
        self.service.start()
        self.http_server.start()
        logger.info("Local bridge server started at http://%s:%s", *self.http_server.address)


def main():
    """
    Entry point called by Briefcase when the APK launches.
    Also called by `briefcase dev` for desktop testing.
    """
    ApolloApp().run()


if __name__ == "__main__":
    main()
