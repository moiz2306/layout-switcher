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
