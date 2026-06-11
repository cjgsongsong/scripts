"""Tests for `_unlock_pdf_file`."""

# pyright: reportPrivateUsage=false

from pikepdf import PasswordError, PdfError
from pytest import (
    MonkeyPatch,
    mark,
    raises
)
from unlock_pdf.classes.path_dictionary import PathDictionary
from unlock_pdf.enumerations import FileState
from unlock_pdf.functions import _unlock_pdf_file
from unlock_pdf.types import Passwords

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

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
        passwords = test_passwords,
        path_dictionary = PathDictionary()
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
            passwords = ["password"],
            path_dictionary = PathDictionary()
        )

locked_path_dictionary = PathDictionary({
    file_state: (
        ["test.pdf"]
        if file_state == FileState.LOCKED else
        []
    )
    for file_state in FileState
})
not_locked_path_dictionary = PathDictionary({
    file_state: (
        ["test.pdf"]
        if file_state == FileState.NOT_LOCKED else
        []
    )
    for file_state in FileState
})
unlocked_path_dictionary = PathDictionary({
    file_state: (
        ["test.pdf"]
        if file_state == FileState.UNLOCKED else
        []
    )
    for file_state in FileState
})

@mark.parametrize(
    "test_initial_path_dictionary, test_passwords, test_pdf_password," \
    "test_final_path_dictionary",
    [
        (
            PathDictionary(), ["password"], "password-0",
            locked_path_dictionary,
        ),
        (
            PathDictionary(), ["password"], "",
            not_locked_path_dictionary
        ),
        (
            PathDictionary(), ["password"], "password",
            unlocked_path_dictionary
        ),
        (
            locked_path_dictionary, ["password"], "password-0",
            locked_path_dictionary
        ),
        (
            not_locked_path_dictionary, ["password"], "",
            not_locked_path_dictionary
        ),
        (
            unlocked_path_dictionary, ["password"], "password",
            unlocked_path_dictionary
        )
    ]
)
def test_unlock_pdf_file_groups_pdf_file_path(
    monkeypatch: MonkeyPatch,
    test_final_path_dictionary: PathDictionary,
    test_initial_path_dictionary: PathDictionary,
    test_passwords: Passwords,
    test_pdf_password: str
) -> None:
    """
    Assert that `_unlock_pdf_file`
    adds a PDF file path to an appropriate file state group
    based on unlocking result.

    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_final_path_dictionary: Resulting dictionary that maps file states
                                       with file paths of PDF files.
    :param test_initial_path_dictionary: Starting dictionary that maps file states
                                         with file paths of PDF files.
    :param test_passwords: Passwords to attempt unlocking the PDF file with.
    :param test_pdf_password: Password needed to unlock the PDF file with.
    """

    test_path_dictionary = test_initial_path_dictionary

    monkeypatch.setattr(
        name = "Pdf",
        target = target,
        value = _MockPDF(test_pdf_password)
    )

    _unlock_pdf_file(
        file_path = "test.pdf",
        passwords = test_passwords,
        path_dictionary = test_path_dictionary
    )

    assert test_path_dictionary == test_final_path_dictionary
