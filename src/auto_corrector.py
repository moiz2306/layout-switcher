import time
import threading
from dataclasses import dataclass

from Quartz import (
    CGEventCreateKeyboardEvent,
    CGEventPost,
    CGEventSetFlags,
    CGEventSourceCreate,
    kCGEventSourceStateHIDSystemState,
    kCGHIDEventTap,
    kCGEventFlagMaskShift,
)


UNDO_TIMEOUT = 10  # seconds


@dataclass
class CorrectionRecord:
    original: str
    corrected: str
    boundary: str
    timestamp: float

    @property
    def char_count(self) -> int:
        return len(self.original)


BACKSPACE_KEYCODE = 51
RETURN_KEYCODE = 36
SPACE_KEYCODE = 49
TAB_KEYCODE = 48


class AutoCorrector:
    """Simulates keyboard input to correct words via CGEvent."""

    def __init__(self):
        self._last_correction: CorrectionRecord | None = None
        self._is_correcting = False
        self._lock = threading.Lock()
        self._replay_buffer: list[str] = []
        self._source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

    @property
    def is_correcting(self) -> bool:
        return self._is_correcting

    def has_undoable_correction(self) -> bool:
        if self._last_correction is None:
            return False
        return (time.time() - self._last_correction.timestamp) < UNDO_TIMEOUT

    def invalidate_undo(self):
        self._last_correction = None

    def add_to_replay_buffer(self, char: str):
        """Buffer a keystroke that arrived during correction."""
        self._replay_buffer.append(char)

    def replay_buffered(self, monitor):
        """Replay any keystrokes that were buffered during correction."""
        if not self._replay_buffer:
            return
        chars = self._replay_buffer[:]
        self._replay_buffer.clear()
        for char in chars:
            self._type_string(char)

    def correct(self, original: str, corrected: str, boundary: str):
        """Delete the original word + boundary, type the corrected word + boundary."""
        with self._lock:
            self._is_correcting = True
            try:
                delete_count = len(original) + len(boundary)
                self._send_backspaces(delete_count)
                self._type_string(corrected)
                self._type_string(boundary)
                self._last_correction = CorrectionRecord(
                    original=original,
                    corrected=corrected,
                    boundary=boundary,
                    timestamp=time.time(),
                )
            finally:
                self._is_correcting = False

    def undo(self):
        """Undo the last correction."""
        if not self.has_undoable_correction():
            return
        rec = self._last_correction
        with self._lock:
            self._is_correcting = True
            try:
                delete_count = len(rec.corrected) + len(rec.boundary)
                self._send_backspaces(delete_count)
                self._type_string(rec.original)
                self._type_string(rec.boundary)
                self._last_correction = None
            finally:
                self._is_correcting = False

    def manual_convert(self, original: str, converted: str, boundary: str):
        """Manually convert last word (triggered by hotkey)."""
        self.correct(original, converted, boundary)

    def _send_backspaces(self, count: int):
        for _ in range(count):
            ev_down = CGEventCreateKeyboardEvent(self._source, BACKSPACE_KEYCODE, True)
            ev_up = CGEventCreateKeyboardEvent(self._source, BACKSPACE_KEYCODE, False)
            CGEventPost(kCGHIDEventTap, ev_down)
            CGEventPost(kCGHIDEventTap, ev_up)

    def _type_string(self, text: str):
        """Type a string by creating keyboard events with unicode characters."""
        from Quartz import CGEventKeyboardSetUnicodeString
        for char in text:
            ev_down = CGEventCreateKeyboardEvent(self._source, 0, True)
            ev_up = CGEventCreateKeyboardEvent(self._source, 0, False)
            CGEventKeyboardSetUnicodeString(ev_down, len(char), char)
            CGEventKeyboardSetUnicodeString(ev_up, len(char), char)
            CGEventPost(kCGHIDEventTap, ev_down)
            CGEventPost(kCGHIDEventTap, ev_up)
