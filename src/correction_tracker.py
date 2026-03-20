import threading
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class CorrectionEvent:
    original: str
    corrected: str
    timestamp: datetime


class CorrectionTracker:
    """Thread-safe in-memory tracker for correction events."""

    def __init__(self):
        self._lock = threading.Lock()
        self._today_count: int = 0
        self._today_date: date = date.today()
        self._recent: deque[CorrectionEvent] = deque(maxlen=10)

    def record(self, original: str, corrected: str):
        with self._lock:
            self._check_date_rollover()
            self._today_count += 1
            self._recent.append(CorrectionEvent(original, corrected, datetime.now()))

    @property
    def today_count(self) -> int:
        with self._lock:
            self._check_date_rollover()
            return self._today_count

    @property
    def recent(self) -> list[CorrectionEvent]:
        with self._lock:
            return list(self._recent)

    def _check_date_rollover(self):
        today = date.today()
        if today != self._today_date:
            self._today_count = 0
            self._today_date = today
