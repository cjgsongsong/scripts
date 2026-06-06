"""Tests for `unlock-pdf` error message generation."""

from pytest import raises
from unlock_pdf.enumerations import ErrorMessage

def test_generate_failed_overwrite_error_message_generates_error_message() -> None:
    """
    Assert that `_generate_failed_overwrite_error_message`
    generates an error message for failed overwrite that

    - has the correct format, and
    - includes the given file path

    when given a valid file path.
    """

    assert ErrorMessage.FAILED_OVERWRITE("test.pdf") == "Unlocking test.pdf failed."

def test_generate_failed_overwrite_error_message_raises_exception() -> None:
    """
    Assert that `_generate_failed_overwrite_error_message`
    raises an appropriate exception
    when given an empty string as file path.
    """

    with raises(
        expected_exception = ValueError,
        match = "File path must be a non-empty string"
    ):
        ErrorMessage.FAILED_OVERWRITE("")
