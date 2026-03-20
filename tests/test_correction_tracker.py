import time
import threading
from datetime import date, datetime
from correction_tracker import CorrectionTracker, CorrectionEvent


def test_initial_state():
    tracker = CorrectionTracker()
    assert tracker.today_count == 0
    assert tracker.recent == []


def test_record_increments_count():
    tracker = CorrectionTracker()
    tracker.record("ghbdtn", "привет")
    assert tracker.today_count == 1
    tracker.record("реьд", "html")
    assert tracker.today_count == 2


def test_recent_stores_events():
    tracker = CorrectionTracker()
    tracker.record("ghbdtn", "привет")
    recent = tracker.recent
    assert len(recent) == 1
    assert recent[0].original == "ghbdtn"
    assert recent[0].corrected == "привет"
    assert isinstance(recent[0].timestamp, datetime)


def test_recent_max_10():
    tracker = CorrectionTracker()
    for i in range(15):
        tracker.record(f"word{i}", f"слово{i}")
    assert len(tracker.recent) == 10
    assert tracker.recent[0].original == "word5"
    assert tracker.recent[-1].original == "word14"


def test_date_rollover_resets_count():
    tracker = CorrectionTracker()
    tracker.record("test", "тест")
    assert tracker.today_count == 1
    tracker._today_date = date(2020, 1, 1)
    assert tracker.today_count == 0


def test_thread_safety():
    tracker = CorrectionTracker()
    errors = []

    def writer():
        try:
            for i in range(100):
                tracker.record(f"w{i}", f"с{i}")
        except Exception as e:
            errors.append(e)

    def reader():
        try:
            for _ in range(100):
                _ = tracker.today_count
                _ = tracker.recent
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer) for _ in range(3)]
    threads += [threading.Thread(target=reader) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    assert tracker.today_count == 300
