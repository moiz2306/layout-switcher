import threading
import queue
import logging
import time

from Quartz import (
    CGEventTapCreate,
    CGEventTapEnable,
    CGEventGetIntegerValueField,
    CGEventGetFlags,
    CFMachPortCreateRunLoopSource,
    CFRunLoopGetCurrent,
    CFRunLoopAddSource,
    CFRunLoopRun,
    CGEventMaskBit,
    kCGSessionEventTap,
    kCGHeadInsertEventTap,
    kCGEventTapOptionDefault,
    kCGEventKeyDown,
    kCGEventFlagsChanged,
    kCGEventLeftMouseDown,
    kCGKeyboardEventKeycode,
    kCFRunLoopCommonModes,
    kCGEventTapDisabledByTimeout,
    kCGEventFlagMaskControl,
    kCGEventFlagMaskShift,
)
from AppKit import (
    NSWorkspace,
    NSWorkspaceDidActivateApplicationNotification,
    NSNotificationCenter,
)

from word_buffer import WordBuffer
from layout_mapper import LayoutMapper
from language_detector import LanguageDetector
from auto_corrector import AutoCorrector
from app_filter import AppFilter
from config import Config

logger = logging.getLogger("layout-switcher")

SPACE_KEYCODE = 49
BACKSPACE_KEYCODE = 51
ARROW_KEYCODES = frozenset({123, 124, 125, 126})
RETURN_KEYCODE = 36
TAB_KEYCODE = 48


class KeyboardMonitor:
    """Global keyboard monitor using CGEventTap."""

    def __init__(self, config: Config, tracker=None):
        self._config = config
        self._tracker = tracker
        self._word_buffer = WordBuffer()
        self._layout_mapper = LayoutMapper()
        self._language_detector = LanguageDetector(config)
        self._auto_corrector = AutoCorrector()
        self._app_filter = AppFilter(config)
        self._detection_queue: queue.Queue = queue.Queue()
        self._last_completed_word: tuple[str, str] | None = None
        self._tap = None

    def start(self):
        NSWorkspace.sharedWorkspace().notificationCenter().addObserver_selector_name_object_(
            self, "_appDidActivate:", NSWorkspaceDidActivateApplicationNotification, None
        )

        worker = threading.Thread(target=self._detection_worker, daemon=True)
        worker.start()

        events = (
            CGEventMaskBit(kCGEventKeyDown)
            | CGEventMaskBit(kCGEventFlagsChanged)
            | CGEventMaskBit(kCGEventLeftMouseDown)
        )
        self._tap = CGEventTapCreate(
            kCGSessionEventTap, kCGHeadInsertEventTap, kCGEventTapOptionDefault,
            events, self._tap_callback, None,
        )

        if self._tap is None:
            logger.error("Failed to create event tap.")
            raise RuntimeError("Failed to create CGEventTap")

        source = CFMachPortCreateRunLoopSource(None, self._tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
        CGEventTapEnable(self._tap, True)
        logger.info("Layout Switcher started.")
        CFRunLoopRun()

    def _appDidActivate_(self, notification):
        self._auto_corrector.invalidate_undo()
        self._word_buffer.clear()

    def _tap_callback(self, proxy, event_type, event, refcon):
        if event_type == kCGEventTapDisabledByTimeout:
            logger.warning("Event tap disabled by timeout, re-enabling...")
            if self._tap:
                CGEventTapEnable(self._tap, True)
            return event

        if event_type == kCGEventLeftMouseDown:
            self._auto_corrector.invalidate_undo()
            self._word_buffer.clear()
            return event

        if event_type != kCGEventKeyDown:
            return event

        if self._auto_corrector.is_correcting:
            char = self._get_char_from_event(event)
            if char:
                self._auto_corrector.add_to_replay_buffer(char)
            return None

        keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
        flags = CGEventGetFlags(event)

        if self._is_hotkey(flags, keycode):
            self._detection_queue.put(("hotkey", None))
            return None

        if self._is_cursor_move(keycode):
            self._auto_corrector.invalidate_undo()
            self._word_buffer.clear()
            return event

        if not self._app_filter.should_process():
            return event

        if keycode == BACKSPACE_KEYCODE:
            self._word_buffer.handle_backspace()
            return event

        char = self._get_char_from_event(event)
        if char is None:
            return event

        result = self._word_buffer.add_char(char)
        if result is not None:
            word, boundary = result
            self._last_completed_word = (word, boundary)
            if len(word) > 2 and not self._language_detector.is_ignored(word) and word.isalpha():
                self._detection_queue.put(("check", (word, boundary)))

        return event

    def _detection_worker(self):
        while True:
            action, data = self._detection_queue.get()
            if action == "hotkey":
                self._handle_hotkey()
            elif action == "check":
                word, boundary = data
                self._check_and_correct(word, boundary)
            self._auto_corrector.replay_buffered(self)

    def _check_and_correct(self, word: str, boundary: str):
        en_version, ru_version = self._layout_mapper.convert_word(word)
        if self._layout_mapper.is_cyrillic(word):
            decision = self._language_detector.check(word, en_version)
            if decision == "correct":
                self._auto_corrector.correct(word, en_version, boundary)
                if self._tracker:
                    self._tracker.record(word, en_version)
        else:
            decision = self._language_detector.check(word, ru_version)
            if decision == "correct":
                self._auto_corrector.correct(word, ru_version, boundary)
                if self._tracker:
                    self._tracker.record(word, ru_version)

    def _handle_hotkey(self):
        if self._auto_corrector.has_undoable_correction():
            self._auto_corrector.undo()
        elif self._last_completed_word is not None:
            word, boundary = self._last_completed_word
            en_version, ru_version = self._layout_mapper.convert_word(word)
            if self._layout_mapper.is_cyrillic(word):
                self._auto_corrector.manual_convert(word, en_version, boundary)
            else:
                self._auto_corrector.manual_convert(word, ru_version, boundary)

    def _get_char_from_event(self, event) -> str | None:
        from Quartz import CGEventKeyboardGetUnicodeString
        length, chars = CGEventKeyboardGetUnicodeString(event, 4, None, None)
        if length > 0 and chars:
            return chars[0]
        return None

    def _is_hotkey(self, flags: int, keycode: int) -> bool:
        ctrl = flags & kCGEventFlagMaskControl
        shift = flags & kCGEventFlagMaskShift
        return bool(ctrl and shift and keycode == SPACE_KEYCODE)

    def _is_cursor_move(self, keycode: int) -> bool:
        return keycode in ARROW_KEYCODES
