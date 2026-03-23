"""Integration tests — verify components work together.
Does NOT test actual keyboard events (requires permissions)."""
from layout_mapper import LayoutMapper
from language_detector import LanguageDetector
from word_buffer import WordBuffer
from config import Config


def test_full_flow_en_to_ru():
    """Simulate: user types 'ghbdtn ' in English layout, should detect as 'привет'."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in "ghbdtn":
        buf.add_char(ch)
    result = buf.add_char(" ")

    assert result is not None
    word, boundary = result
    assert word == "ghbdtn"

    en_ver, ru_ver = mapper.convert_word(word)
    assert en_ver == "ghbdtn"
    assert ru_ver == "привет"

    decision = detector.check(word, ru_ver)
    assert decision == "correct"


def test_full_flow_ru_to_en():
    """Simulate: user types 'реьд ' in Russian layout, should detect as 'html'."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in "реьд":
        buf.add_char(ch)
    result = buf.add_char(" ")

    word, boundary = result
    en_ver, ru_ver = mapper.convert_word(word)
    assert en_ver == "html"

    decision = detector.check(word, en_ver)
    assert decision == "correct"


def test_full_flow_valid_english_no_correction():
    """Simulate: user types 'hello ' — valid English, should NOT correct."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in "hello":
        buf.add_char(ch)
    result = buf.add_char(" ")

    word, boundary = result
    en_ver, ru_ver = mapper.convert_word(word)

    decision = detector.check(word, ru_ver)
    assert decision == "keep"


def test_full_flow_short_word_skipped():
    """Words of 2 chars or less should be skipped."""
    buf = WordBuffer()
    buf.add_char("h")
    buf.add_char("i")
    result = buf.add_char(" ")
    word, _ = result
    assert len(word) <= 2


def test_full_flow_ignore_word():
    """Words in ignore list should be skipped."""
    detector = LanguageDetector()
    assert detector.is_ignored("gg") is True
    assert detector.is_ignored("lol") is True


# --- Bug fix: words with layout-mapped punctuation must be detected ---


def test_full_flow_word_with_comma():
    """'hf,jnftn' (работает) — comma is 'б', must stay as one word."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in "hf,jnftn":
        buf.add_char(ch)
    result = buf.add_char(" ")

    assert result is not None
    word, boundary = result
    assert word == "hf,jnftn"

    en_ver, ru_ver = mapper.convert_word(word)
    assert ru_ver == "работает"

    decision = detector.check(word, ru_ver)
    assert decision == "correct"


def test_full_flow_word_with_apostrophe():
    """'nj (это) — apostrophe is 'э', must stay as one word."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in "'nj":
        buf.add_char(ch)
    result = buf.add_char(" ")

    assert result is not None
    word, boundary = result
    assert word == "'nj"

    en_ver, ru_ver = mapper.convert_word(word)
    assert ru_ver == "это"

    decision = detector.check(word, ru_ver)
    assert decision == "correct"


def test_full_flow_word_with_semicolon():
    """';bpym' (жизнь) — semicolon is 'ж', must stay as one word."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in ";bpym":
        buf.add_char(ch)
    result = buf.add_char(" ")

    assert result is not None
    word, boundary = result
    assert word == ";bpym"

    en_ver, ru_ver = mapper.convert_word(word)
    assert ru_ver == "жизнь"

    decision = detector.check(word, ru_ver)
    assert decision == "correct"


def test_full_flow_word_with_brackets():
    """'[jhjij' (хорошо) — bracket is 'х', must stay as one word."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in "[jhjij":
        buf.add_char(ch)
    result = buf.add_char(" ")

    assert result is not None
    word, boundary = result
    assert word == "[jhjij"

    en_ver, ru_ver = mapper.convert_word(word)
    assert ru_ver == "хорошо"

    decision = detector.check(word, ru_ver)
    assert decision == "correct"


def test_full_flow_word_with_period_and_comma():
    """'k.,jdm' (любовь) — period is 'ю', comma is 'б'."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    buf = WordBuffer()

    for ch in "k.,jdm":
        buf.add_char(ch)
    result = buf.add_char(" ")

    assert result is not None
    word, boundary = result
    assert word == "k.,jdm"

    en_ver, ru_ver = mapper.convert_word(word)
    assert ru_ver == "любовь"

    decision = detector.check(word, ru_ver)
    assert decision == "correct"


# --- Trailing trimming: punctuation after words ---


def _try_with_trimming(word, mapper, detector):
    """Helper: try full word, then trim trailing layout chars."""
    from word_buffer import WordBuffer
    en_ver, ru_ver = mapper.convert_word(word)
    is_cyr = mapper.is_cyrillic(word)
    converted = en_ver if is_cyr else ru_ver
    decision = detector.check(word, converted)
    if decision == "correct":
        return word, converted

    trimmed = word
    trailing = ""
    while trimmed and trimmed[-1] in WordBuffer.LAYOUT_LETTER_KEYS:
        trailing = trimmed[-1] + trailing
        trimmed = trimmed[:-1]
        if len(trimmed) >= 2:
            en2, ru2 = mapper.convert_word(trimmed)
            conv2 = en2 if mapper.is_cyrillic(trimmed) else ru2
            d2 = detector.check(trimmed, conv2)
            if d2 == "correct":
                return trimmed, conv2
    return None, None


def test_trailing_trim_comma_after_word():
    """'ghbdtn,' → 'приветб' fails, trim ',' → 'ghbdtn' → 'привет' works."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    trimmed, converted = _try_with_trimming("ghbdtn,", mapper, detector)
    assert trimmed == "ghbdtn"
    assert converted == "привет"


def test_trailing_trim_period_after_word():
    """'ghbdtn.' → 'приветю' fails, trim '.' → 'привет' works."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    trimmed, converted = _try_with_trimming("ghbdtn.", mapper, detector)
    assert trimmed == "ghbdtn"
    assert converted == "привет"


def test_trailing_trim_bracket_comma():
    """'[jhjij,' → 'хорошоб' fails, trim ',' → '[jhjij' → 'хорошо' works."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    trimmed, converted = _try_with_trimming("[jhjij,", mapper, detector)
    assert trimmed == "[jhjij"
    assert converted == "хорошо"


def test_no_trimming_needed_for_full_word():
    """'hf,jnftn' → 'работает' works without trimming."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    trimmed, converted = _try_with_trimming("hf,jnftn", mapper, detector)
    assert trimmed == "hf,jnftn"
    assert converted == "работает"


# --- Boundary conversion ---


def test_boundary_slash_converts_to_period():
    """Boundary '/' should convert to '.' when correcting EN→RU."""
    mapper = LayoutMapper()
    assert mapper.convert("/", "en_to_ru") == "."


def test_boundary_question_converts_to_comma():
    """Boundary '?' should convert to ',' (RU comma) when correcting EN→RU."""
    mapper = LayoutMapper()
    assert mapper.convert("?", "en_to_ru") == ","


def test_boundary_ampersand_converts_to_question():
    """Boundary '&' should convert to '?' when correcting EN→RU."""
    mapper = LayoutMapper()
    assert mapper.convert("&", "en_to_ru") == "?"


# --- Two-letter words ---


def test_two_letter_word_ty():
    """'ns' → 'ты' — 2-letter word should be detectable."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    en_ver, ru_ver = mapper.convert_word("ns")
    assert ru_ver == "ты"
    assert detector.check("ns", ru_ver) == "correct"


def test_two_letter_word_on():
    """'jy' → 'он' — common 2-letter Russian word."""
    mapper = LayoutMapper()
    detector = LanguageDetector()
    en_ver, ru_ver = mapper.convert_word("jy")
    assert ru_ver == "он"
    assert detector.check("jy", ru_ver) == "correct"
