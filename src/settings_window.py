import os
import subprocess
import objc
from AppKit import (
    NSWindow,
    NSWindowStyleMaskTitled,
    NSWindowStyleMaskClosable,
    NSBackingStoreBuffered,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSTabView,
    NSTabViewItem,
    NSSwitch,
    NSTextField,
    NSButton,
    NSTableView,
    NSTableColumn,
    NSScrollView,
    NSFont,
    NSColor,
    NSView,
    NSOpenPanel,
    NSBezelStyleRounded,
    NSControlStateValueOn,
    NSControlStateValueOff,
    NSApp,
)
from Foundation import NSObject, NSMakeRect, NSBundle, NSURL
from pathlib import Path

from config import Config


_shared_instance = None


def get_settings_window(config: Config):
    """Get or create the singleton SettingsWindow."""
    global _shared_instance
    if _shared_instance is None:
        _shared_instance = SettingsWindow.alloc().initWithConfig_(config)
    return _shared_instance


class SettingsWindow(NSObject):
    """Native settings window with tabs."""

    def initWithConfig_(self, config: Config):
        self = objc.super(SettingsWindow, self).init()
        if self is None:
            return None
        self._config = config
        self._window = None
        self._apps_data = list(config.excluded_apps)
        self._words_data = list(config.ignore_words)
        self._apps_table = None
        self._words_table = None
        return self

    def show(self):
        if self._window is None:
            self._create_window()
        self._refresh_data()
        self._window.makeKeyAndOrderFront_(None)
        NSApp.activateIgnoringOtherApps_(True)

    def _refresh_data(self):
        self._apps_data = list(self._config.excluded_apps)
        self._words_data = list(self._config.ignore_words)
        if self._apps_table:
            self._apps_table.reloadData()
        if self._words_table:
            self._words_table.reloadData()

    def _create_window(self):
        rect = NSMakeRect(0, 0, 480, 400)
        style = NSWindowStyleMaskTitled | NSWindowStyleMaskClosable
        self._window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, style, NSBackingStoreBuffered, False
        )
        self._window.setTitle_("Layout Switcher — Настройки")
        self._window.center()
        self._window.setReleasedWhenClosed_(False)
        self._window.setCollectionBehavior_(NSWindowCollectionBehaviorCanJoinAllSpaces)

        tab_view = NSTabView.alloc().initWithFrame_(NSMakeRect(10, 10, 460, 370))

        # Tab 1: General
        tab1 = NSTabViewItem.alloc().initWithIdentifier_("general")
        tab1.setLabel_("Общее")
        tab1.setView_(self._create_general_tab())
        tab_view.addTabViewItem_(tab1)

        # Tab 2: Apps
        tab2 = NSTabViewItem.alloc().initWithIdentifier_("apps")
        tab2.setLabel_("Приложения")
        tab2.setView_(self._create_apps_tab())
        tab_view.addTabViewItem_(tab2)

        # Tab 3: Dictionary
        tab3 = NSTabViewItem.alloc().initWithIdentifier_("dict")
        tab3.setLabel_("Словарь")
        tab3.setView_(self._create_dictionary_tab())
        tab_view.addTabViewItem_(tab3)

        self._window.contentView().addSubview_(tab_view)

    def _create_general_tab(self):
        view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 440, 320))
        y = 270

        # Enabled toggle
        label = NSTextField.labelWithString_("Включён")
        label.setFrame_(NSMakeRect(20, y, 200, 20))
        view.addSubview_(label)
        self._enabled_switch = NSSwitch.alloc().initWithFrame_(NSMakeRect(350, y - 2, 50, 24))
        self._enabled_switch.setState_(NSControlStateValueOn if self._config.enabled else NSControlStateValueOff)
        self._enabled_switch.setTarget_(self)
        self._enabled_switch.setAction_(objc.selector(self._toggle_enabled, signature=b"v@:@"))
        view.addSubview_(self._enabled_switch)

        y -= 50

        # Hotkey display
        label2 = NSTextField.labelWithString_("Хоткей")
        label2.setFrame_(NSMakeRect(20, y, 200, 20))
        view.addSubview_(label2)
        hotkey_field = NSTextField.labelWithString_(self._format_hotkey(self._config.hotkey))
        hotkey_field.setFrame_(NSMakeRect(300, y, 120, 20))
        hotkey_field.setTextColor_(NSColor.secondaryLabelColor())
        view.addSubview_(hotkey_field)

        y -= 50

        # Notifications toggle
        label3 = NSTextField.labelWithString_("Уведомления")
        label3.setFrame_(NSMakeRect(20, y, 200, 20))
        view.addSubview_(label3)
        self._notif_switch = NSSwitch.alloc().initWithFrame_(NSMakeRect(350, y - 2, 50, 24))
        self._notif_switch.setState_(NSControlStateValueOn if self._config.show_notifications else NSControlStateValueOff)
        self._notif_switch.setTarget_(self)
        self._notif_switch.setAction_(objc.selector(self._toggle_notifications, signature=b"v@:@"))
        view.addSubview_(self._notif_switch)

        y -= 50

        # Launch at login toggle
        label4 = NSTextField.labelWithString_("Запускать при входе")
        label4.setFrame_(NSMakeRect(20, y, 200, 20))
        view.addSubview_(label4)
        self._login_switch = NSSwitch.alloc().initWithFrame_(NSMakeRect(350, y - 2, 50, 24))
        launch_agent = Path.home() / "Library" / "LaunchAgents" / "com.layout-switcher.plist"
        self._login_switch.setState_(NSControlStateValueOn if launch_agent.exists() else NSControlStateValueOff)
        self._login_switch.setTarget_(self)
        self._login_switch.setAction_(objc.selector(self._toggle_launch_at_login, signature=b"v@:@"))
        view.addSubview_(self._login_switch)

        return view

    def _create_apps_tab(self):
        view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 440, 320))

        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 50, 400, 240))
        self._apps_table = NSTableView.alloc().initWithFrame_(scroll.bounds())
        col = NSTableColumn.alloc().initWithIdentifier_("app")
        col.setTitle_("Приложение")
        col.setWidth_(380)
        self._apps_table.addTableColumn_(col)
        self._apps_table.setHeaderView_(None)
        self._apps_table.setDataSource_(self)
        self._apps_table.setDelegate_(self)
        scroll.setDocumentView_(self._apps_table)
        scroll.setHasVerticalScroller_(True)
        view.addSubview_(scroll)

        add_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 10, 30, 30))
        add_btn.setTitle_("+")
        add_btn.setBezelStyle_(NSBezelStyleRounded)
        add_btn.setTarget_(self)
        add_btn.setAction_(objc.selector(self._add_app, signature=b"v@:@"))
        view.addSubview_(add_btn)

        remove_btn = NSButton.alloc().initWithFrame_(NSMakeRect(55, 10, 30, 30))
        remove_btn.setTitle_("−")
        remove_btn.setBezelStyle_(NSBezelStyleRounded)
        remove_btn.setTarget_(self)
        remove_btn.setAction_(objc.selector(self._remove_app, signature=b"v@:@"))
        view.addSubview_(remove_btn)

        # Empty state label
        self._apps_empty_label = NSTextField.labelWithString_("Нет исключений — работает во всех приложениях")
        self._apps_empty_label.setFrame_(NSMakeRect(20, 150, 400, 20))
        self._apps_empty_label.setTextColor_(NSColor.secondaryLabelColor())
        self._apps_empty_label.setAlignment_(1)  # NSTextAlignmentCenter
        self._apps_empty_label.setHidden_(len(self._apps_data) > 0)
        view.addSubview_(self._apps_empty_label)

        return view

    def _create_dictionary_tab(self):
        view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 440, 320))

        scroll = NSScrollView.alloc().initWithFrame_(NSMakeRect(20, 80, 400, 210))
        self._words_table = NSTableView.alloc().initWithFrame_(scroll.bounds())
        col = NSTableColumn.alloc().initWithIdentifier_("word")
        col.setTitle_("Слово")
        col.setWidth_(380)
        self._words_table.addTableColumn_(col)
        self._words_table.setHeaderView_(None)
        self._words_table.setDataSource_(self)
        self._words_table.setDelegate_(self)
        scroll.setDocumentView_(self._words_table)
        scroll.setHasVerticalScroller_(True)
        view.addSubview_(scroll)

        self._word_input = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 40, 280, 24))
        self._word_input.setPlaceholderString_("Новое слово...")
        view.addSubview_(self._word_input)

        add_btn = NSButton.alloc().initWithFrame_(NSMakeRect(310, 38, 100, 28))
        add_btn.setTitle_("Добавить")
        add_btn.setBezelStyle_(NSBezelStyleRounded)
        add_btn.setTarget_(self)
        add_btn.setAction_(objc.selector(self._add_word, signature=b"v@:@"))
        view.addSubview_(add_btn)

        remove_btn = NSButton.alloc().initWithFrame_(NSMakeRect(20, 8, 100, 28))
        remove_btn.setTitle_("Удалить")
        remove_btn.setBezelStyle_(NSBezelStyleRounded)
        remove_btn.setTarget_(self)
        remove_btn.setAction_(objc.selector(self._remove_word, signature=b"v@:@"))
        view.addSubview_(remove_btn)

        return view

    # --- Actions ---

    def _toggle_enabled(self, sender):
        enabled = sender.state() == NSControlStateValueOn
        self._config.set_enabled(enabled)

    def _toggle_notifications(self, sender):
        on = sender.state() == NSControlStateValueOn
        self._config.set_show_notifications(on)

    def _toggle_launch_at_login(self, sender):
        on = sender.state() == NSControlStateValueOn
        project_dir = Path(__file__).parent.parent
        plist_template = project_dir / "com.layout-switcher.plist"
        target = Path.home() / "Library" / "LaunchAgents" / "com.layout-switcher.plist"
        config_dir = Path.home() / ".config" / "layout-switcher"

        if on and plist_template.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            content = plist_template.read_text()
            content = content.replace("__VENV_PYTHON__", str(project_dir / ".venv" / "bin" / "python3"))
            content = content.replace("__SRC_MAIN__", str(project_dir / "src" / "main.py"))
            content = content.replace("__LOG_DIR__", str(config_dir))
            target.write_text(content)
            subprocess.run(["launchctl", "load", str(target)], capture_output=True)
        elif not on and target.exists():
            subprocess.run(["launchctl", "unload", str(target)], capture_output=True)
            target.unlink(missing_ok=True)
        self._config.set_launch_at_login(on)

    def _add_app(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseFiles_(True)
        panel.setCanChooseDirectories_(False)
        panel.setAllowsMultipleSelection_(False)
        panel.setDirectoryURL_(NSURL.fileURLWithPath_("/Applications"))
        panel.setAllowedFileTypes_(["app"])
        panel.setMessage_("Выберите приложение для исключения")
        if panel.runModal() == 1:  # NSModalResponseOK
            url = panel.URL()
            if url:
                bundle = NSBundle.bundleWithURL_(url)
                if bundle:
                    name = bundle.objectForInfoDictionaryKey_("CFBundleName") or url.lastPathComponent().replace(".app", "")
                else:
                    name = url.lastPathComponent().replace(".app", "")
                if name and name not in self._apps_data:
                    self._apps_data.append(name)
                    self._config.set_excluded_apps(self._apps_data)
                    self._apps_table.reloadData()

    def _remove_app(self, sender):
        row = self._apps_table.selectedRow()
        if 0 <= row < len(self._apps_data):
            self._apps_data.pop(row)
            self._config.set_excluded_apps(self._apps_data)
            self._apps_table.reloadData()

    def _add_word(self, sender):
        word = self._word_input.stringValue().strip().lower()
        if word and word not in self._words_data:
            self._words_data.append(word)
            self._config.set_ignore_words(self._words_data)
            self._words_table.reloadData()
            self._word_input.setStringValue_("")

    def _remove_word(self, sender):
        row = self._words_table.selectedRow()
        if 0 <= row < len(self._words_data):
            self._words_data.pop(row)
            self._config.set_ignore_words(self._words_data)
            self._words_table.reloadData()

    # --- NSTableViewDataSource ---

    def numberOfRowsInTableView_(self, table):
        if table == self._apps_table:
            return len(self._apps_data)
        return len(self._words_data)

    def tableView_objectValueForTableColumn_row_(self, table, col, row):
        if table == self._apps_table:
            return self._apps_data[row] if row < len(self._apps_data) else ""
        return self._words_data[row] if row < len(self._words_data) else ""

    # --- Helpers ---

    def _format_hotkey(self, hotkey_str: str) -> str:
        return hotkey_str.replace("ctrl", "⌃").replace("shift", "⇧").replace("space", "Space").replace("+", "")
