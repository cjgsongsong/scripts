"""Tests for `_get_pdf_file_paths`."""

# pyright: reportPrivateUsage=false

from pytest import (
    MonkeyPatch,
    mark,
    raises
)
from tests.utilities import generate_mock_get_unique_inputs
from unlock_pdf.functions import _get_pdf_file_paths
from unlock_pdf.types import Paths

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

def test_get_pdf_file_paths_raises_exception(monkeypatch: MonkeyPatch) -> None:
    """
    Assert that `_get_pdf_file_paths`
    raises an appropriate exception
    when given no path.

    :param monkeypatch: `pytest` fixture for mocking functions.
    """

    monkeypatch.setattr(
        name = "_get_unique_inputs",
        target = target,
        value = generate_mock_get_unique_inputs(
            test_inputs = [],
            test_prompt = "Enter every directory path and/or file path of the PDF files to unlock."
        )
    )

    with raises(
        expected_exception = FileNotFoundError,
        match = "At least one path must ultimately point to a PDF file."
    ):
        _get_pdf_file_paths()

@mark.parametrize(
    "test_paths," \
    "test_pdf_file_subpaths," \
    "test_pdf_file_paths",
    [
        (
            ["test.pdf"],
            [["test.pdf"]],
            ["test.pdf"]
        ),
        (
            ["test-0.pdf", "test-directory/"],
            [
                ["test-0.pdf"],
                ["test-directory/test-1.pdf"]
            ],
            ["test-0.pdf", "test-directory/test-1.pdf"]
        )
    ]
)
def test_get_pdf_file_paths_returns_pdf_file_paths(
    monkeypatch: MonkeyPatch,
    test_paths: Paths,
    test_pdf_file_paths: Paths,
    test_pdf_file_subpaths: list[Paths],
) -> None:
    """
    Assert that `_get_pdf_file_paths`
    returns a set of paths of all PDF files to unlock
    from inputted paths.

    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_paths: Mock ordered list of unique paths.
    :param test_pdf_file_paths: Ordered list of unique paths of all PDF files to unlock.
    :param test_pdf_file_subpaths: Mock ordered list of unique paths of some PDF files to unlock.
    """

    call_count = -1

    def _mock_get_pdf_file_subpaths(path: str) -> Paths:
        """
        Mock function of `unlock-pdf.functions._get_pdf_file_subpaths` that
        returns mock paths of some PDF files to unlock
        based on how many times the mock function has been called.

        :param path: Directory path or file path of some PDF files to unlock.
        :returns Mock ordered list of unique paths of some PDF files to unlock.
        """

        nonlocal call_count

        call_count += 1

        assert path in test_paths

        return test_pdf_file_subpaths[call_count]

    monkeypatch.setattr(
        name = "_get_pdf_file_subpaths",
        target = target,
        value = _mock_get_pdf_file_subpaths
    )
    monkeypatch.setattr(
        name = "_get_unique_inputs",
        target = target,
        value = generate_mock_get_unique_inputs(
            test_inputs = test_paths,
            test_prompt = "Enter every directory path and/or file path of the PDF files to unlock."
        )
    )

    assert _get_pdf_file_paths() == test_pdf_file_paths
