"""Tests for `_unlock_pdf_file`."""

# pyright: reportPrivateUsage=false

from copy import deepcopy
from pikepdf import PasswordError, PdfError
from pytest import (
    MonkeyPatch,
    mark,
    raises
)
from unlock_pdf.enumerations import FileState
from unlock_pdf.functions import _unlock_pdf_file
from unlock_pdf.types import GroupedPaths, Passwords

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

BASE_GROUPED_PDF_FILE_PATHS: GroupedPaths = {
    key: []
    for key in [
        file_state for file_state in FileState
    ]
}

class _MockPDF:
    """Mock class of `pikepdf.Pdf`."""

    def __init__(
        self,
        test_pdf_password: str,
        test_should_fail_on_open: bool = False,
        test_should_fail_on_save: bool = False
    ) -> None:
        """
        Initialize a mock instance of `pikepdf.Pdf`.
        
        :param: test_pdf_password: Password needed to unlock the PDF file with.
        """

        self.did_unlock = False
        self.test_pdf_password = test_pdf_password
        self.test_should_fail_on_open = test_should_fail_on_open
        self.test_should_fail_on_save = test_should_fail_on_save

    def open(
        self,
        filename_or_stream: str,
        allow_overwriting_input: bool = False,
        password: str = "",
    ) -> "_MockPDF":
        """
        Mock function of `pikepdf.Pdf.open` that
        mocks
        
        - opening a PDF file, or
        - raising an appropriate exception if
          - opening said PDF file fails, or
          - said PDF file is not locked.
        
        :param allow_overwriting_input: Whether if the PDF file can be overwritten or not.
        :param filename_or_stream: Sanitized file path of the PDF file to unlock.
        :param password: Password needed to unlock the PDF file with.
        :raises PasswordError: If the PDF file is not unlocked.
        :raises PdfError: If opening the PDF file fails.
        """

        if self.test_should_fail_on_open:
            raise PdfError

        assert allow_overwriting_input == (password != "")
        assert filename_or_stream == "test.pdf"

        if password != self.test_pdf_password:
            raise PasswordError

        if self.test_pdf_password != "":
            self.did_unlock = True

        return self

    def save(self, filename_or_stream: str) -> None:
        """
        Mock function of `pikepdf.Pdf.save` that
        mocks
        
        - overwriting a PDF file, or
        - raising an appropriate exception if overwriting said PDF file fails.

        :raises PdfError: If saving the PDF file fails.
        """

        if self.test_should_fail_on_save:
            raise PdfError

        assert self.did_unlock is True
        assert filename_or_stream == "test.pdf"

@mark.parametrize(
    "test_passwords, test_pdf_password," \
    "test_should_unlock",
    [
        (
            ["password"], "",
            False,
        ),
        (
            ["password"], "password-0",
            False,
        ),
        (
            ["password-0", "password-1"], "password-0",
            True
        ),
        (
            ["password-0", "password-1"], "password-1",
            True
        )
    ]
)
def test_unlock_pdf_file_attempts_unlocking(
    monkeypatch: MonkeyPatch,
    test_passwords: Passwords,
    test_pdf_password: str,
    test_should_unlock: bool
) -> None:
    """
    Assert that `_unlock_pdf_file`
    attempts unlocking a PDF file pointed at by the given file path.

    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_passwords: Passwords to attempt unlocking the PDF file with.
    :param test_pdf_password: Password needed to unlock the PDF file with.
    :param test_should_unlock: Whether the PDF file should have been unlocked or not.
    """

    test_pikepdf_pdf = _MockPDF(test_pdf_password)

    monkeypatch.setattr(
        name = "Pdf",
        target = target,
        value = test_pikepdf_pdf
    )

    _unlock_pdf_file(
        file_path = "test.pdf",
        grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS),
        passwords = test_passwords
    )

    assert test_pikepdf_pdf.did_unlock == test_should_unlock

@mark.parametrize(
    "test_should_fail_on_open, test_should_fail_on_save",
    [
        (True, False),
        (False, True)
    ]
)
def test_unlock_pdf_file_raises_exception(
    monkeypatch: MonkeyPatch,
    test_should_fail_on_open: bool,
    test_should_fail_on_save: bool
) -> None:
    """
    Assert that `_unlock_pdf_file`
    raises an appropriate exception
    when `pikepdf` fails.

    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_should_fail_on_open: Whether `pikepdf` should fail
                                     on attempt to open the PDF file or not.
    """

    monkeypatch.setattr(
        name = "Pdf",
        target = target,
        value = _MockPDF(
            test_pdf_password = "password",
            test_should_fail_on_open = test_should_fail_on_open,
            test_should_fail_on_save = test_should_fail_on_save
        )
    )

    with raises(
        expected_exception = PdfError,
        match = "Unlocking test.pdf failed."
    ):
        _unlock_pdf_file(
            file_path = "test.pdf",
            grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS),
            passwords = ["password"]
        )

locked_grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS)
not_locked_grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS)
unlocked_grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS)

locked_grouped_pdf_file_paths[FileState.LOCKED] = ["test.pdf"]
not_locked_grouped_pdf_file_paths[FileState.NOT_LOCKED] = ["test.pdf"]
unlocked_grouped_pdf_file_paths[FileState.UNLOCKED] = ["test.pdf"]

@mark.parametrize(
    "test_initial_grouped_pdf_file_paths, test_passwords, test_pdf_password," \
    "test_final_grouped_pdf_file_paths",
    [
        (
            BASE_GROUPED_PDF_FILE_PATHS, ["password"], "password-0",
            locked_grouped_pdf_file_paths,
        ),
        (
            BASE_GROUPED_PDF_FILE_PATHS, ["password"], "",
            not_locked_grouped_pdf_file_paths
        ),
        (
            BASE_GROUPED_PDF_FILE_PATHS, ["password"], "password",
            unlocked_grouped_pdf_file_paths
        ),
        (
            locked_grouped_pdf_file_paths, ["password"], "password-0",
            locked_grouped_pdf_file_paths
        ),
        (
            not_locked_grouped_pdf_file_paths, ["password"], "",
            not_locked_grouped_pdf_file_paths
        ),
        (
            unlocked_grouped_pdf_file_paths, ["password"], "password",
            unlocked_grouped_pdf_file_paths
        )
    ]
)
def test_unlock_pdf_file_groups_pdf_file_path(
    monkeypatch: MonkeyPatch,
    test_final_grouped_pdf_file_paths: GroupedPaths,
    test_initial_grouped_pdf_file_paths: GroupedPaths,
    test_passwords: Passwords,
    test_pdf_password: str
) -> None:
    """
    Assert that `_unlock_pdf_file`
    adds a PDF file path to an appropriate file state group
    based on unlocking result.

    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_final_grouped_pdf_file_paths: Resulting dictionary that maps file states with
                                              file paths of PDF files.
    :param test_initial_grouped_pdf_file_paths: Starting dictionary that maps file states with
                                                file paths of PDF files.
    :param test_passwords: Passwords to attempt unlocking the PDF file with.
    :param test_pdf_password: Password needed to unlock the PDF file with.
    """

    test_grouped_pdf_file_paths = deepcopy(test_initial_grouped_pdf_file_paths)

    monkeypatch.setattr(
        name = "Pdf",
        target = target,
        value = _MockPDF(test_pdf_password)
    )

    _unlock_pdf_file(
        file_path = "test.pdf",
        grouped_pdf_file_paths = test_grouped_pdf_file_paths,
        passwords = test_passwords
    )

    assert test_grouped_pdf_file_paths == test_final_grouped_pdf_file_paths
