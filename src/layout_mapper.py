class LayoutMapper:
    """Bidirectional character mapping between QWERTY and ЙЦУКЕН layouts."""

    EN_CHARS = "`qwertyuiop[]asdfghjkl;'zxcvbnm,./"
    RU_CHARS = "ёйцукенгшщзхъфывапролджэячсмитьбю."

    # Shift-level mapping: same physical keys with Shift held.
    # Punctuation→letter: ~ { } : " < > → Ё Х Ъ Ж Э Б Ю
    # Punctuation→punctuation: ? @ # $ ^ & → , " № ; : ?
    EN_SHIFT_CHARS = '~{}:"<>?@#$^&'
    RU_SHIFT_CHARS = 'ЁХЪЖЭБЮ,"№;:?'

    def __init__(self):
        self._en_to_ru = {}
        self._ru_to_en = {}

        # Base level (no Shift)
        for en, ru in zip(self.EN_CHARS, self.RU_CHARS):
            self._en_to_ru[en] = ru
            self._ru_to_en[ru] = en
            # Only add case-shifted mappings when the character has a distinct
            # uppercase form (letters). Punctuation like ';' has upper() == itself,
            # so adding it would overwrite the correct lowercase mapping.
            if en.upper() != en:
                self._en_to_ru[en.upper()] = ru.upper()
            if ru.upper() != ru:
                self._ru_to_en[ru.upper()] = en.upper()

        # Shift level (Shift held — punctuation keys)
        for en, ru in zip(self.EN_SHIFT_CHARS, self.RU_SHIFT_CHARS):
            self._en_to_ru[en] = ru
            self._ru_to_en[ru] = en

    def convert(self, text: str, direction: str) -> str:
        mapping = self._en_to_ru if direction == "en_to_ru" else self._ru_to_en
        return "".join(mapping.get(ch, ch) for ch in text)

    def convert_word(self, word: str) -> tuple[str, str]:
        """Returns (english_version, russian_version) regardless of input layout."""
        if self.is_cyrillic(word):
            return self.convert(word, "ru_to_en"), word
        else:
            return word, self.convert(word, "en_to_ru")

    def is_cyrillic(self, text: str) -> bool:
        return any("\u0400" <= ch <= "\u04ff" for ch in text)
