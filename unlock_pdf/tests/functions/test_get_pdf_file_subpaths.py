"""Tests for `_get_pdf_file_subpaths`."""

# pyright: reportPrivateUsage=false

from pytest import MonkeyPatch, mark
from tests.utilities import generate_mock_boolean
from unlock_pdf.functions import _get_pdf_file_subpaths
from unlock_pdf.types import Paths

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

@mark.parametrize(
    "test_path," \
    "test_glob_paths, test_is_directory, test_is_pdf_file," \
    "test_pdf_file_subpaths",
    [
        (
            "test-directory/",
            ["test-directory/test-0.pdf", "test-directory/test-1.pdf"], True, False,
            ["test-directory/test-0.pdf", "test-directory/test-1.pdf"]
        ),
        (
            "test.pdf",
            [], False, True,
            ["test.pdf"]
        ),
        (
            "",
            [], False, False,
            []
        )
    ]
)
def test_get_pdf_file_subpaths_returns_pdf_file_subpaths(
    monkeypatch: MonkeyPatch,
    test_glob_paths: Paths,
    test_is_directory: bool,
    test_is_pdf_file: bool,
    test_path: str,
    test_pdf_file_subpaths: Paths
) -> None:
    """
    Asserts that `_get_pdf_file_subpaths`
    returns a set of paths of some PDF files to unlock
    when given a valid path.
    
    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_glob_paths: Mock list of paths that match the determined file path pattern.
    :param test_is_directory: Mock boolean that
                              tells whether the file path directly points to a directory or not.
    :param test_is_pdf_file: Mock boolean that
                             tells whether the file path directly points to a PDF file or not.
    :param test_path: Mock directory path or mock file path of some PDF files to unlock.
    :param test_pdf_file_subpaths: Ordered list of unique paths of some PDF files to unlock.
    """

    def _mock_glob(pathname: str, recursive: bool) -> Paths:
        """
        Mock function of `glob.glob` that
        returns a list of paths that match the determined file path pattern.
        
        :param pathname: File path pattern.
        :param recursive: Whether to recursively look for matches in directories or not.
        :returns List of paths that match the determined file path pattern.
        """

        assert pathname == test_path + "/**/*.pdf"
        assert recursive is True

        return test_glob_paths

    monkeypatch.setattr(
        name = "_is_pdf_file",
        target = target,
        value = generate_mock_boolean(
            test_boolean = test_is_pdf_file,
            test_path = test_path
        )
    )
    monkeypatch.setattr(
        name = "glob",
        target = target,
        value = _mock_glob
    )
    monkeypatch.setattr(
        name = "isdir",
        target = target,
        value = generate_mock_boolean(
            test_boolean = test_is_directory,
            test_path = test_path
        )
    )

    assert _get_pdf_file_subpaths(test_path) == test_pdf_file_subpaths
