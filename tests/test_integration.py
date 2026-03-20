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
