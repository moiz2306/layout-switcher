class WordBuffer:
    """Buffers keystrokes and detects word boundaries."""

    BOUNDARIES = frozenset(" \n\r\t.,!?;:()[]{}\"'<>/\\|@#$%^&*~`+-=")

    def __init__(self):
        self._buffer: list[str] = []

    def add_char(self, char: str) -> tuple[str, str] | None:
        """Add a character. Returns (word, boundary_char) if word boundary hit, else None."""
        if char in self.BOUNDARIES:
            word = "".join(self._buffer)
            self._buffer.clear()
            if word:
                return (word, char)
            return None
        self._buffer.append(char)
        return None

    def handle_backspace(self):
        if self._buffer:
            self._buffer.pop()

    def current_word(self) -> str:
        return "".join(self._buffer)

    def clear(self):
        self._buffer.clear()
