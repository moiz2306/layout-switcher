from unittest.mock import MagicMock
from keyboard_monitor import KeyboardMonitor


def test_hotkey_detection():
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    ctrl_shift = 0x60104
    assert monitor._is_hotkey(ctrl_shift, 49) is True


def test_hotkey_not_detected_without_modifiers():
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    assert monitor._is_hotkey(0, 49) is False


def test_cursor_moving_keys():
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    assert monitor._is_cursor_move(123) is True
    assert monitor._is_cursor_move(124) is True
    assert monitor._is_cursor_move(125) is True
    assert monitor._is_cursor_move(126) is True
    assert monitor._is_cursor_move(0) is False
