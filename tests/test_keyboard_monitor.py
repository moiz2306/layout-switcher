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


# --- Bug fixes: could_be_word, synthetic marker ---


def test_could_be_word_regular():
    """Regular alphabetic words pass the check."""
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    assert monitor._could_be_word("hello") is True
    assert monitor._could_be_word("ghbdtn") is True


def test_could_be_word_with_layout_chars():
    """Words containing layout-mapped chars (,.';[]`) pass the check."""
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    assert monitor._could_be_word("hf,jnftn") is True  # работает
    assert monitor._could_be_word("'nj") is True  # это
    assert monitor._could_be_word(";bpym") is True  # жизнь
    assert monitor._could_be_word("[jhjij") is True  # хорошо
    assert monitor._could_be_word("`krf") is True  # ёлка
    assert monitor._could_be_word("k.,jdm") is True  # любовь


def test_could_be_word_rejects_digits():
    """Words with digits should NOT pass."""
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    assert monitor._could_be_word("abc123") is False


def test_could_be_word_rejects_special_chars():
    """Words with non-layout-mapped special chars should NOT pass."""
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    assert monitor._could_be_word("hello!") is False
    assert monitor._could_be_word("a@b") is False
    assert monitor._could_be_word("test#") is False


def test_synthetic_marker_in_monitor():
    """SYNTHETIC_MARKER constants available in keyboard_monitor."""
    from keyboard_monitor import SYNTHETIC_MARKER_FIELD, SYNTHETIC_MARKER_VALUE
    assert SYNTHETIC_MARKER_FIELD == 42
    assert SYNTHETIC_MARKER_VALUE > 0


# --- Fast typing optimizations ---


def test_should_skip_stale_correction():
    """_is_stale() should return True when queue has newer items."""
    import queue as q
    monitor = KeyboardMonitor.__new__(KeyboardMonitor)
    monitor._detection_queue = q.Queue()
    # Empty queue — not stale
    assert monitor._is_stale() is False
    # Queue has items — stale
    monitor._detection_queue.put(("check", ("abc", " ")))
    assert monitor._is_stale() is True
