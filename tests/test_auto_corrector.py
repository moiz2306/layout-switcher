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
