import objc
from AppKit import (
    NSWindow,
    NSWindowStyleMaskTitled,
    NSWindowStyleMaskFullSizeContentView,
    NSBackingStoreBuffered,
    NSTextField,
    NSButton,
    NSFont,
    NSColor,
    NSView,
    NSApp,
    NSModalResponseOK,
    NSBezelStyleRounded,
    NSTextAlignmentCenter,
    NSWorkspace,
)
from Foundation import NSObject, NSTimer, NSMakeRect, NSURL, NSRunLoop, NSDefaultRunLoopMode
from Quartz import CGPreflightListenEventAccess, CGPreflightPostEventAccess
from pathlib import Path


ONBOARDING_MARKER = Path.home() / ".config" / "layout-switcher" / ".onboarding_done"

STEPS = [
    {
        "icon": "🔐",
        "title": "Шаг 1 из 2 — Input Monitoring",
        "description": "Layout Switcher нужен доступ для чтения нажатий клавиш",
        "instruction": "System Settings → Privacy & Security → Input Monitoring",
        "url": "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent",
        "check": CGPreflightListenEventAccess,
    },
    {
        "icon": "⌨️",
        "title": "Шаг 2 из 2 — Accessibility",
        "description": "Необходим для автоматического исправления текста",
        "instruction": "System Settings → Privacy & Security → Accessibility",
        "url": "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        "check": CGPreflightPostEventAccess,
    },
]


def onboarding_done() -> bool:
    return ONBOARDING_MARKER.exists()


def mark_onboarding_done():
    ONBOARDING_MARKER.parent.mkdir(parents=True, exist_ok=True)
    ONBOARDING_MARKER.touch()


class OnboardingWindow(NSObject):
    """Step-by-step permission setup wizard."""

    def init(self):
        self = objc.super(OnboardingWindow, self).init()
        if self is None:
            return None
        self._current_step = 0
        self._timer = None
        self._window = None
        return self

    def run_modal(self):
        # Skip if both permissions already granted
        if all(step["check"]() for step in STEPS):
            mark_onboarding_done()
            return

        # Skip steps that are already granted
        while self._current_step < len(STEPS) and STEPS[self._current_step]["check"]():
            self._current_step += 1
        if self._current_step >= len(STEPS):
            mark_onboarding_done()
            return

        self._create_window()
        self._show_step(self._current_step)
        NSApp.runModalForWindow_(self._window)

    def _create_window(self):
        rect = NSMakeRect(0, 0, 420, 320)
        style = NSWindowStyleMaskTitled | NSWindowStyleMaskFullSizeContentView
        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, style, NSBackingStoreBuffered, False
        )
        self._window.setTitlebarAppearsTransparent_(True)
        self._window.setTitle_("")
        self._window.center()
        self._window.setMovableByWindowBackground_(True)

    def _show_step(self, index):
        step = STEPS[index]
        content = self._window.contentView()
        for subview in list(content.subviews()):
            subview.removeFromSuperview()

        w = 420

        # Icon
        icon_label = NSTextField.labelWithString_(step["icon"])
        icon_label.setFont_(NSFont.systemFontOfSize_(48))
        icon_label.setAlignment_(NSTextAlignmentCenter)
        icon_label.setFrame_(NSMakeRect(0, 220, w, 60))
        content.addSubview_(icon_label)

        # Title
        title_label = NSTextField.labelWithString_(step["title"])
        title_label.setFont_(NSFont.boldSystemFontOfSize_(18))
        title_label.setAlignment_(NSTextAlignmentCenter)
        title_label.setFrame_(NSMakeRect(20, 185, w - 40, 30))
        content.addSubview_(title_label)

        # Description
        desc_label = NSTextField.labelWithString_(step["description"])
        desc_label.setFont_(NSFont.systemFontOfSize_(13))
        desc_label.setAlignment_(NSTextAlignmentCenter)
        desc_label.setTextColor_(NSColor.secondaryLabelColor())
        desc_label.setFrame_(NSMakeRect(30, 155, w - 60, 25))
        content.addSubview_(desc_label)

        # Instruction
        inst_label = NSTextField.labelWithString_(step["instruction"])
        inst_label.setFont_(NSFont.systemFontOfSize_(11))
        inst_label.setAlignment_(NSTextAlignmentCenter)
        inst_label.setTextColor_(NSColor.tertiaryLabelColor())
        inst_label.setFrame_(NSMakeRect(30, 120, w - 60, 25))
        inst_label.setBackgroundColor_(NSColor.quaternaryLabelColor())
        inst_label.setDrawsBackground_(True)
        content.addSubview_(inst_label)

        # Buttons
        later_btn = NSButton.alloc().initWithFrame_(NSMakeRect(110, 60, 90, 32))
        later_btn.setTitle_("Позже")
        later_btn.setBezelStyle_(NSBezelStyleRounded)
        later_btn.setTarget_(self)
        later_btn.setAction_("skipStep:")
        content.addSubview_(later_btn)

        open_btn = NSButton.alloc().initWithFrame_(NSMakeRect(210, 60, 140, 32))
        open_btn.setTitle_("Открыть настройки")
        open_btn.setBezelStyle_(NSBezelStyleRounded)
        open_btn.setTarget_(self)
        open_btn.setAction_("openSettings:")
        content.addSubview_(open_btn)

        # Progress dots
        for i in range(len(STEPS)):
            dot = NSView.alloc().initWithFrame_(NSMakeRect(w // 2 - 15 + i * 20, 25, 10, 10))
            dot.setWantsLayer_(True)
            dot.layer().setCornerRadius_(5)
            if i <= self._current_step:
                dot.layer().setBackgroundColor_(NSColor.controlAccentColor().CGColor())
            else:
                dot.layer().setBackgroundColor_(NSColor.separatorColor().CGColor())
            content.addSubview_(dot)

        # Start permission check timer
        self._start_timer()

    def _start_timer(self):
        self._stop_timer()
        self._timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            2.0, self, "checkPermission:", None, True
        )

    def _stop_timer(self):
        if self._timer:
            self._timer.invalidate()
            self._timer = None

    @objc.typedSelector(b"v@:@")
    def checkPermission_(self, timer):
        step = STEPS[self._current_step]
        if step["check"]():
            self._advance_step()

    @objc.typedSelector(b"v@:@")
    def skipStep_(self, sender):
        self._advance_step()

    @objc.typedSelector(b"v@:@")
    def openSettings_(self, sender):
        step = STEPS[self._current_step]
        url = NSURL.URLWithString_(step["url"])
        NSWorkspace.sharedWorkspace().openURL_(url)

    def _advance_step(self):
        self._stop_timer()
        self._current_step += 1
        if self._current_step >= len(STEPS):
            mark_onboarding_done()
            NSApp.stopModal()
            self._window.close()
        else:
            # Skip already-granted steps
            if STEPS[self._current_step]["check"]():
                self._advance_step()
            else:
                self._show_step(self._current_step)
