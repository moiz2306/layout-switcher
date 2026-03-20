import objc
from AppKit import (
    NSStatusBar,
    NSMenu,
    NSMenuItem,
    NSAttributedString,
    NSFont,
    NSColor,
    NSApp,
    NSVariableStatusItemLength,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
)
from Foundation import NSObject
from Quartz import CGPreflightListenEventAccess, CGPreflightPostEventAccess

from correction_tracker import CorrectionTracker
from config import Config


class StatusBar(NSObject):
    """Native macOS status bar icon with dropdown menu."""

    def initWithConfig_tracker_(self, config: Config, tracker: CorrectionTracker):
        self = objc.super(StatusBar, self).init()
        if self is None:
            return None
        self._config = config
        self._tracker = tracker
        self._settings_callback = None
        self._error_state = False
        self._status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        self._menu = NSMenu.alloc().init()
        self._menu.setDelegate_(self)
        self._status_item.setMenu_(self._menu)
        self.set_active()
        return self

    def set_settings_callback(self, callback):
        self._settings_callback = callback

    # --- State methods ---

    def set_active(self):
        self._error_state = False
        self._set_dot_color(NSColor.systemGreenColor())

    def set_disabled(self):
        self._error_state = False
        self._set_dot_color(NSColor.systemGrayColor())

    def set_error(self):
        self._error_state = True
        self._set_dot_color(NSColor.systemOrangeColor())

    def _set_dot_color(self, color):
        attrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(14),
            NSForegroundColorAttributeName: color,
        }
        title = NSAttributedString.alloc().initWithString_attributes_("●", attrs)
        self._status_item.button().setAttributedTitle_(title)

    # --- NSMenuDelegate ---

    @objc.typedSelector(b"v@:@")
    def menuNeedsUpdate_(self, menu):
        menu.removeAllItems()

        # Title row — show error details if in error state
        if self._error_state:
            status_text = "● Ошибка"
            title_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Layout Switcher   {status_text}", None, ""
            )
            title_item.setEnabled_(False)
            menu.addItem_(title_item)

            # Show which permissions are missing
            if not CGPreflightListenEventAccess():
                perm_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "⚠ Нет доступа: Input Monitoring", None, ""
                )
                perm_item.setEnabled_(False)
                menu.addItem_(perm_item)
            if not CGPreflightPostEventAccess():
                perm_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "⚠ Нет доступа: Accessibility", None, ""
                )
                perm_item.setEnabled_(False)
                menu.addItem_(perm_item)
        else:
            enabled = self._config.enabled
            status_text = "● Активен" if enabled else "● Выключен"
            title_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Layout Switcher   {status_text}", None, ""
            )
            title_item.setEnabled_(False)
            menu.addItem_(title_item)

            # Counter row
            count = self._tracker.today_count
            counter_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"Сегодня исправлено: {count}", None, ""
            )
            counter_item.setEnabled_(False)
            menu.addItem_(counter_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # Toggle
        toggle_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Включён", "toggleEnabled:", ""
        )
        toggle_item.setTarget_(self)
        toggle_item.setState_(1 if self._config.enabled else 0)
        menu.addItem_(toggle_item)

        # Recent corrections submenu
        recent = self._tracker.recent
        if recent:
            recent_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                "Последние исправления", None, ""
            )
            submenu = NSMenu.alloc().init()
            for event in reversed(recent):
                sub_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    f"{event.original} → {event.corrected}", None, ""
                )
                sub_item.setEnabled_(False)
                submenu.addItem_(sub_item)
            recent_item.setSubmenu_(submenu)
            menu.addItem_(recent_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # Settings
        settings_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Настройки...", "openSettings:", ","
        )
        settings_item.setTarget_(self)
        menu.addItem_(settings_item)

        menu.addItem_(NSMenuItem.separatorItem())

        # Quit
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Выход", "quitApp:", "q"
        )
        quit_item.setTarget_(self)
        menu.addItem_(quit_item)

    @objc.typedSelector(b"v@:@")
    def toggleEnabled_(self, sender):
        enabled = not self._config.enabled
        self._config.set_enabled(enabled)
        if enabled:
            self.set_active()
        else:
            self.set_disabled()

    @objc.typedSelector(b"v@:@")
    def openSettings_(self, sender):
        if self._settings_callback:
            self._settings_callback()

    @objc.typedSelector(b"v@:@")
    def quitApp_(self, sender):
        NSApp.terminate_(None)
