from word_buffer import WordBuffer

WORD_BOUNDARIES = {" ", "\n", "\r", "\t", ".", ",", "!", "?", ";", ":", "(", ")", "[", "]", "{", "}"}


def test_add_regular_char():
    buf = WordBuffer()
    result = buf.add_char("h")
    assert result is None
    assert buf.current_word() == "h"


def test_word_boundary_returns_word():
    buf = WordBuffer()
    buf.add_char("h")
    buf.add_char("i")
    result = buf.add_char(" ")
    assert result == ("hi", " ")


def test_buffer_cleared_after_boundary():
    buf = WordBuffer()
    buf.add_char("h")
    buf.add_char("i")
    buf.add_char(" ")
    assert buf.current_word() == ""


def test_multiple_words():
    buf = WordBuffer()
    buf.add_char("h")
    buf.add_char("i")
    result1 = buf.add_char(" ")
    buf.add_char("o")
    buf.add_char("k")
    result2 = buf.add_char("\n")
    assert result1 == ("hi", " ")
    assert result2 == ("ok", "\n")


def test_punctuation_is_boundary():
    buf = WordBuffer()
    buf.add_char("h")
    buf.add_char("i")
    result = buf.add_char("!")
    assert result == ("hi", "!")


def test_empty_word_on_consecutive_boundaries():
    buf = WordBuffer()
    buf.add_char(" ")
    result = buf.add_char(" ")
    assert result is None


def test_backspace_removes_last_char():
    buf = WordBuffer()
    buf.add_char("h")
    buf.add_char("e")
    buf.add_char("l")
    buf.handle_backspace()
    assert buf.current_word() == "he"


def test_backspace_on_empty():
    buf = WordBuffer()
    buf.handle_backspace()
    assert buf.current_word() == ""


def test_clear():
    buf = WordBuffer()
    buf.add_char("h")
    buf.add_char("i")
    buf.clear()
    assert buf.current_word() == ""


def test_has_digits_or_special():
    buf = WordBuffer()
    for ch in "abc123":
        buf.add_char(ch)
    result = buf.add_char(" ")
    assert result == ("abc123", " ")


def test_word_with_only_boundaries():
    buf = WordBuffer()
    result = buf.add_char(".")
    assert result is None
