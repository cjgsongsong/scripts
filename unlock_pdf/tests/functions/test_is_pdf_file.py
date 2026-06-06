"""Tests for `_is_pdf_file`."""

# pyright: reportPrivateUsage=false

from pytest import MonkeyPatch, mark
from tests.utilities import generate_mock_boolean
from unlock_pdf.functions import _is_pdf_file

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

@mark.parametrize(
    "test_file_path, test_is_file," \
    "test_boolean",
    [
        (
            "corrupted-test.pdf", False,
            False
        ),
        (
            "test.pdf", True,
            True
        ),
        (
            "test.txt", False,
            False
        ),
        (
            "test.txt", True,
            False
        )
    ]
)
def test_is_pdf_file_returns_boolean(
    monkeypatch: MonkeyPatch,
    test_boolean: bool,
    test_file_path: str,
    test_is_file: bool
) -> None:
    """
    Assert that `_is_pdf_file`
    returns whether the file path directly points to a PDF file or not
    when given a valid file path.
    
    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_boolean: Whether the file path directly points to a PDF file or not.
    :param test_file_path: Mock path of a file.
    :param test_is_file: Mock boolean that tells whether the path directly points to a file or not.
    """

    monkeypatch.setattr(
        name = "isfile",
        target = target,
        value = generate_mock_boolean(
            test_boolean = test_is_file,
            test_path = test_file_path
        )
    )

    assert _is_pdf_file(test_file_path) == test_boolean
