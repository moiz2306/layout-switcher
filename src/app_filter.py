from AppKit import NSWorkspace

from config import Config


class AppFilter:
    """Checks if the active application is in the exclusion list."""

    def __init__(self, config: Config):
        self._config = config

    def get_active_app(self) -> str:
        """Returns the name of the currently active application."""
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        return app.localizedName() if app else ""

    def is_excluded(self, app_name: str) -> bool:
        excluded = set(name.lower() for name in self._config.excluded_apps)
        return app_name.lower() in excluded

    def should_process(self) -> bool:
        return not self.is_excluded(self.get_active_app())
