from layout_mapper import LayoutMapper


def test_en_to_ru_lowercase():
    mapper = LayoutMapper()
    assert mapper.convert("ghbdtn", "en_to_ru") == "привет"


def test_ru_to_en_lowercase():
    mapper = LayoutMapper()
    # р→h, е→t, ь→m, д→l
    assert mapper.convert("реьд", "ru_to_en") == "html"


def test_en_to_ru_uppercase():
    mapper = LayoutMapper()
    assert mapper.convert("Ghbdtn", "en_to_ru") == "Привет"


def test_ru_to_en_uppercase():
    mapper = LayoutMapper()
    assert mapper.convert("Реьд", "ru_to_en") == "Html"


def test_mixed_case():
    mapper = LayoutMapper()
    assert mapper.convert("GHbdtn", "en_to_ru") == "ПРивет"


def test_unmapped_characters_pass_through():
    mapper = LayoutMapper()
    assert mapper.convert("123", "en_to_ru") == "123"
    assert mapper.convert("hello1", "en_to_ru") == "руддщ1"


def test_punctuation_mapping():
    mapper = LayoutMapper()
    # ; maps to ж, ' maps to э
    assert mapper.convert(";", "en_to_ru") == "ж"
    assert mapper.convert("'", "en_to_ru") == "э"


def test_convert_word_returns_both():
    mapper = LayoutMapper()
    en_ver, ru_ver = mapper.convert_word("ghbdtn")
    assert en_ver == "ghbdtn"
    assert ru_ver == "привет"


def test_convert_word_ru_input():
    mapper = LayoutMapper()
    en_ver, ru_ver = mapper.convert_word("реьд")
    assert en_ver == "html"
    assert ru_ver == "реьд"


def test_is_cyrillic():
    mapper = LayoutMapper()
    assert mapper.is_cyrillic("привет") is True
    assert mapper.is_cyrillic("hello") is False
    assert mapper.is_cyrillic("hello1привет") is True  # has cyrillic chars


# --- Shift-level mapping ---


def test_shift_punctuation_en_to_ru():
    """Shift+key punctuation: ? → , (comma), & → ?, ^ → :, $ → ;, @ → \", # → №"""
    mapper = LayoutMapper()
    assert mapper.convert("?", "en_to_ru") == ","
    assert mapper.convert("&", "en_to_ru") == "?"
    assert mapper.convert("^", "en_to_ru") == ":"
    assert mapper.convert("$", "en_to_ru") == ";"
    assert mapper.convert("@", "en_to_ru") == '"'
    assert mapper.convert("#", "en_to_ru") == "№"


def test_shift_letters_en_to_ru():
    """Shift+key where EN punctuation → RU uppercase letter."""
    mapper = LayoutMapper()
    assert mapper.convert("~", "en_to_ru") == "Ё"
    assert mapper.convert("{", "en_to_ru") == "Х"
    assert mapper.convert("}", "en_to_ru") == "Ъ"
    assert mapper.convert(":", "en_to_ru") == "Ж"
    assert mapper.convert('"', "en_to_ru") == "Э"
    assert mapper.convert("<", "en_to_ru") == "Б"
    assert mapper.convert(">", "en_to_ru") == "Ю"


def test_shift_letters_ru_to_en():
    """RU uppercase letters → EN shift punctuation."""
    mapper = LayoutMapper()
    assert mapper.convert("Ё", "ru_to_en") == "~"
    assert mapper.convert("Х", "ru_to_en") == "{"
    assert mapper.convert("Ъ", "ru_to_en") == "}"
    assert mapper.convert("Ж", "ru_to_en") == ":"
    assert mapper.convert("Э", "ru_to_en") == '"'
    assert mapper.convert("Б", "ru_to_en") == "<"
    assert mapper.convert("Ю", "ru_to_en") == ">"


def test_shift_punctuation_ru_to_en():
    """RU shift punctuation → EN shift punctuation."""
    mapper = LayoutMapper()
    assert mapper.convert(",", "ru_to_en") == "?"  # RU comma (shift+/) → EN ?
    assert mapper.convert("?", "ru_to_en") == "&"  # RU ? → EN &
    assert mapper.convert(":", "ru_to_en") == "^"  # RU : → EN ^
    assert mapper.convert(";", "ru_to_en") == "$"  # RU ; → EN $
    assert mapper.convert('"', "ru_to_en") == "@"  # RU " → EN @
    assert mapper.convert("№", "ru_to_en") == "#"  # RU № → EN #
