"""
ui/app.py
============================================================
ApolloApp — the root Kivy application class.

This is what Briefcase runs when the APK launches.
It sets up the screen manager, starts the background
Apollo service, and handles app lifecycle events.

Kivy apps always subclass `App` and implement `build()`
which returns the root widget displayed to the user.
============================================================
"""

import logging
import threading

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from apollo.utils.config import ApolloConfig
from apollo.background.service import ApolloService

logger = logging.getLogger(__name__)


class ApolloApp(App):
    """
    Root Kivy application for ApolloDroid.

    Kivy lifecycle:
        build()   → return root widget (called once at startup)
        on_start  → app is fully visible, safe to start services
        on_stop   → user or OS is closing the app — clean up here
        on_pause  → Android sent app to background (screen off, etc.)
        on_resume → app comes back to foreground
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._service: ApolloService | None = None
        self._config: ApolloConfig | None = None

    def build(self):
        """
        Called by Kivy to create and return the root widget.
        The ScreenManager holds all app screens and handles navigation.

        Returns:
            ScreenManager as the root UI widget.
        """
        self.title = "ApolloDroid"
        self.icon = "ui/assets/apollo_icon.png"

        # ScreenManager handles navigation between screens
        sm = ScreenManager()

        # TODO: Add screens as they're implemented
        # from ui.screens.main import MainScreen
        # from ui.screens.settings import SettingsScreen
        # sm.add_widget(MainScreen(name="main"))
        # sm.add_widget(SettingsScreen(name="settings"))

        return sm

    def on_start(self):
        """
        Called after build() when the UI is fully ready.
        Safe to start background services here.
        """
        logger.info("App started — initializing Apollo service...")

        # Load config on a background thread to avoid freezing the UI
        # while reading .env and validating keys
        threading.Thread(target=self._start_service, daemon=True).start()

    def on_stop(self):
        """Called when the app is closing — clean up all resources."""
        if self._service:
            logger.info("App stopping — shutting down Apollo service...")
            self._service.stop()

    def on_pause(self):
        """
        Android calls this when the app goes to background.
        Return True to allow pause (False would close the app).
        The foreground service keeps Apollo running even when paused.
        """
        logger.debug("App paused.")
        return True  # Allow the app to be paused (not closed)

    def on_resume(self):
        """Called when the app returns to the foreground."""
        logger.debug("App resumed.")

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _start_service(self):
        """Initialize config and start the Apollo background service."""
        try:
            self._config = ApolloConfig.load()
            self._service = ApolloService(self._config)
            self._service.start()
        except ValueError as e:
            # Missing API keys — show setup screen
            logger.error(f"Configuration error: {e}")
            # TODO: Navigate to onboarding/setup screen
        except Exception as e:
            logger.error(f"Failed to start Apollo service: {e}")
