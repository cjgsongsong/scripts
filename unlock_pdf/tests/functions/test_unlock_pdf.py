"""Tests for `unlock_pdf`."""

from pytest import MonkeyPatch, mark
from unlock_pdf.classes.path_dictionary import PathDictionary
from unlock_pdf.functions import unlock_pdf

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

@mark.parametrize(
    "test_pdf_file_paths",
    [
        ["test-0.pdf"],
        ["test-0.pdf, test-1.pdf"]
    ]
)
def test_unlock_pdf_calls_helper_functions(
    monkeypatch: MonkeyPatch,
    test_pdf_file_paths: list[str]
) -> None:
    """
    Assert that `unlock_pdf`
    calls whenever appropriate
    
    - `_get_passwords`
    - `_get_pdf_file_paths`
    - `_log_unlock_attempt`, and
    - `_unlock_pdf_file`.
    
    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_pdf_file_paths: Ordered list of unique paths of all PDF files to unlock.
    """

    test_path_dictionary = PathDictionary()
    test_passwords = ["password"]
    unlock_count = 0

    def _mock_log_unlock_attempt(path_dictionary: PathDictionary) -> None:
        """
        Mock function of `unlock_pdf.functions._log_unlock_attempt` that
        mocks printing file state count.
        
        :param path_dictionary: Dictionary that maps file states with file paths of PDF files.
        """

        assert path_dictionary == test_path_dictionary

    def _mock_unlock_pdf_file(
        file_path: str,
        passwords: list[str],
        path_dictionary: PathDictionary
    ) -> None:
        """
        Mock function of `unlock_pdf.functions._mock_unlock_pdf_file` that
        mocks unlocking of a PDF file.

        :param file_path: Sanitized file path of the PDF file to unlock.
        :param passwords: Passwords to attempt unlocking the PDF file with.
        :param path_dictionary: Dictionary that maps file states with file paths of PDF files.
        """

        nonlocal unlock_count

        assert file_path in test_pdf_file_paths
        assert path_dictionary == test_path_dictionary
        assert passwords == test_passwords

        unlock_count += 1

    monkeypatch.setattr(
        name = "_get_passwords",
        target = target,
        value = lambda: test_passwords
    )
    monkeypatch.setattr(
        name = "_get_pdf_file_paths",
        target = target,
        value = lambda: test_pdf_file_paths
    )
    monkeypatch.setattr(
        name = "_log_unlock_attempt",
        target = target,
        value = _mock_log_unlock_attempt
    )
    monkeypatch.setattr(
        name = "_unlock_pdf_file",
        target = target,
        value = _mock_unlock_pdf_file
    )

    unlock_pdf()

    assert unlock_count == len(test_pdf_file_paths)
