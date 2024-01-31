#! python3

"""
Unit tests for utils.
"""

from rate_my_project.utils import to_snake_case


def test_one_word_already_in_snake_case_to_snake_case() -> None:
    """
    Convert one word without spaces in snake case to snake case.
    """
    assert to_snake_case("word_in_snake_case") == "word_in_snake_case"


def test_one_word_to_snake_case() -> None:
    """
    Convert one word without spaces not in snake case to snake case.
    """
    assert to_snake_case("WordInCamelCase") == "word_in_camel_case"


def test_multiple_words_with_spaces_to_snake_case() -> None:
    """
    Convert multiple words separated by spaces not in snake case to snake case.
    """
    assert to_snake_case("Word with spaces") == "word_with_spaces"
