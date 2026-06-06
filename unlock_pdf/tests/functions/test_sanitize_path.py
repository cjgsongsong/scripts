"""Tests for `_sanitize_path`."""

# pyright: reportPrivateUsage=false

from pytest import mark
from unlock_pdf.functions import _sanitize_path

@mark.parametrize(
    "test_path," \
    "test_sanitized_path",
    [
        ('"test.pdf"', "test.pdf"),
        ("test.pdf", "test.pdf")
    ]
)
def test_sanitize_path_returns_sanitized_path(test_path: str, test_sanitized_path: str) -> None:
    """
    Assert that `_sanitize_path`
    returns the sanitized version of the given path
    when given a valid path.

    :param test_path: Directory path or file path of some PDF files to unlock.
    :param test_sanitized_path: Sanitized aforementioned path.
    """

    assert _sanitize_path(test_path) == test_sanitized_path
