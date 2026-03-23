import time
from auto_corrector import AutoCorrector, CorrectionRecord


def test_correction_record_creation():
    rec = CorrectionRecord(
        original="ghbdtn",
        corrected="привет",
        boundary=" ",
        timestamp=time.time(),
    )
    assert rec.original == "ghbdtn"
    assert rec.corrected == "привет"
    assert rec.char_count == 6


def test_undo_state_valid_within_timeout():
    ac = AutoCorrector()
    ac._last_correction = CorrectionRecord(
        original="ghbdtn",
        corrected="привет",
        boundary=" ",
        timestamp=time.time(),
    )
    assert ac.has_undoable_correction() is True


def test_undo_state_expired():
    ac = AutoCorrector()
    ac._last_correction = CorrectionRecord(
        original="ghbdtn",
        corrected="привет",
        boundary=" ",
        timestamp=time.time() - 15,
    )
    assert ac.has_undoable_correction() is False


def test_invalidate_undo():
    ac = AutoCorrector()
    ac._last_correction = CorrectionRecord(
        original="ghbdtn",
        corrected="привет",
        boundary=" ",
        timestamp=time.time(),
    )
    ac.invalidate_undo()
    assert ac.has_undoable_correction() is False


def test_correcting_flag():
    ac = AutoCorrector()
    assert ac.is_correcting is False


# --- Bug fixes: synthetic markers, delays, extra chars ---


def test_event_delay_constant():
    """Verify EVENT_DELAY constant exists and is reasonable."""
    from auto_corrector import EVENT_DELAY
    assert EVENT_DELAY > 0
    assert EVENT_DELAY < 0.1


def test_synthetic_marker_constants():
    """Verify synthetic event marker constants exist."""
    from auto_corrector import SYNTHETIC_MARKER_FIELD, SYNTHETIC_MARKER_VALUE
    assert SYNTHETIC_MARKER_FIELD == 42
    assert SYNTHETIC_MARKER_VALUE > 0


def test_correct_accepts_extra_param():
    """correct() should accept extra parameter for race condition fix."""
    import inspect
    sig = inspect.signature(AutoCorrector.correct)
    params = list(sig.parameters.keys())
    assert "extra" in params


def test_drain_replay_buffer():
    """drain_replay_buffer() returns and clears buffered chars."""
    ac = AutoCorrector()
    ac.add_to_replay_buffer("a")
    ac.add_to_replay_buffer("b")
    result = ac.drain_replay_buffer()
    assert result == ["a", "b"]
    assert ac.drain_replay_buffer() == []


# --- Fast typing optimizations ---


def test_block_delay_constant():
    """BLOCK_DELAY should exist and be larger than EVENT_DELAY for inter-block pauses."""
    from auto_corrector import BLOCK_DELAY, EVENT_DELAY
    assert BLOCK_DELAY > EVENT_DELAY
    assert BLOCK_DELAY < 0.05  # reasonable upper bound
