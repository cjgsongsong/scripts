"""Tests for `unlock-pdf` functions."""

# pyright: reportPrivateUsage=false

from copy import deepcopy
from pikepdf import PasswordError, PdfError
from pytest import (
    CaptureFixture,
    MonkeyPatch,
    mark,
    raises
)
from unlock_pdf.enumerations import FileState
from unlock_pdf.functions import (
    _log_unlock_attempt,
    _sanitize_path,
    _unlock_pdf_file,
    unlock_pdf
)
from unlock_pdf.types import GroupedPaths

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

class TestLogUnlockAttempt:
    """Tests for `_log_unlock_attempt`."""

    def test_log_unlock_attempt_prints_with_valid_grouped_pdf_file_paths(
        self,
        capsys: CaptureFixture[str]
    ) -> None:
        """
        Assert that `_log_unlock_attempt`
        prints for every file state

        - how many PDF files are in such file state, and
        - what are the file paths of those PDF files

        when given valid grouped PDF file paths.

        :param capsys: `pytest` fixture for capturing outputs.
        """

        grouped_pdf_file_paths: GroupedPaths = {
            key: []
            for key in [
                file_state for file_state in FileState
            ]
        }
        grouped_pdf_file_paths[FileState.NOT_LOCKED] = ["test-0.pdf"]
        grouped_pdf_file_paths[FileState.UNLOCKED] = ["test-1.pdf", "test-2.pdf"]

        _log_unlock_attempt(grouped_pdf_file_paths)

        assert (
            capsys \
                .readouterr() \
                .out
        )== (
            "0 PDF files are still locked:"
            + "\n"
            + "-"
            + "\n"
            + "\n"
            + "1 PDF file is not locked:"
            + "\n"
            + "test-0.pdf"
            + "\n"
            + "\n"
            + "2 PDF files are unlocked:"
            + "\n"
            + "test-1.pdf"
            + "\n"
            + "test-2.pdf"
            + "\n"
            + "\n"
        )

class TestSanitizePath:
    """Tests for `_sanitize_path`."""

    @mark.parametrize(
        "path," \
        "sanitized_path",
        [
            ('"test.pdf"', "test.pdf"),
            ("test.pdf", "test.pdf")
        ]
    )
    def test_sanitize_path_returns_with_valid_path(
        self,
        path: str,
        sanitized_path: str
    ) -> None:
        """
        Assert that `_sanitize_path`
        returns the sanitized given path
        when given a valid path.

        :param path: Directory path or file path of some PDF files to unlock.
        :param sanitized_path: Sanitized aforementioned path.
        """

        assert _sanitize_path(path) == sanitized_path

class TestUnlockPDF:
    """Tests for `unlock_pdf`."""

    @mark.parametrize(
        "pdf_file_paths",
        [
            ["test-0.pdf"],
            ["test-0.pdf, test-1.pdf"]
        ]
    )
    def test_unlock_pdf_calls_helper_functions(
        self,
        monkeypatch: MonkeyPatch,
        pdf_file_paths: list[str]
    ) -> None:
        """
        Assert that `unlock_pdf`
        calls whenever appropriate
        
        - `_get_passwords`
        - `_get_pdf_file_paths`
        - `_log_unlock_attempt`, and
        - `_unlock_pdf_file`.
        
        :param monkeypatch: `pytest` fixture for mocking functions.
        :param pdf_file_paths: Ordered list of unique paths of all PDF files to unlock.
        """

        test_grouped_pdf_file_paths: GroupedPaths = {
            key: []
            for key in [
                file_state for file_state in FileState
            ]
        }
        test_passwords = ["password"]
        unlock_count = 0

        def _mock_get_passwords() -> list[str]:
            """
            Mock function of `unlock_pdf.functions._get_passwords` that
            returns a mock ordered list of unique passwords to attempt unlocking each PDF file with.
            
            :returns Mock ordered list of unique passwords to attempt unlocking each PDF file with.
            """

            return test_passwords

        def _mock_get_pdf_file_paths() -> list[str]:
            """
            Mock function of `unlock_pdf.functions._get_pdf_file_paths` that
            returns a mock ordered list of unique paths of all PDF files to unlock.
            
            :returns Mock ordered list of unique paths of all PDF files to unlock.
            """

            return pdf_file_paths

        def _mock_log_unlock_attempt(grouped_pdf_file_paths: GroupedPaths) -> None:
            """
            Mock function of `unlock_pdf.functions._log_unlock_attempt` that
            mocks printing file state count.
            
            :param grouped_pdf_file_paths: Dictionary that maps file states
                                           with file paths of PDF files.
            """

            assert grouped_pdf_file_paths == test_grouped_pdf_file_paths

        def _mock_unlock_pdf_file(
            file_path: str,
            grouped_pdf_file_paths: GroupedPaths,
            passwords: list[str]
        ) -> None:
            """
            Mock function of `unlock_pdf.functions._mock_unlock_pdf_file` that
            mocks unlocking of a PDF file.

            :param file_path: Sanitized file path of the PDF file to unlock.
            :param grouped_pdf_file_paths: Dictionary that maps file states
                                           with file paths of PDF files.
            :param passwords: Passwords to attempt unlocking the PDF file with.
            """

            nonlocal unlock_count

            assert file_path in pdf_file_paths
            assert grouped_pdf_file_paths == test_grouped_pdf_file_paths
            assert passwords == test_passwords

            unlock_count += 1

        monkeypatch.setattr(
            name = "_get_passwords",
            target = target,
            value = _mock_get_passwords
        )
        monkeypatch.setattr(
            name = "_get_pdf_file_paths",
            target = target,
            value = _mock_get_pdf_file_paths
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

        assert unlock_count == len(pdf_file_paths)

class TestUnlockPDFFile:
    """Tests for `_unlock_pdf_file`."""

    BASE_GROUPED_PDF_FILE_PATHS: GroupedPaths = {
        key: []
        for key in [
            file_state for file_state in FileState
        ]
    }

    @mark.parametrize(
        "passwords, pdf_password," \
        "should_unlock",
        [
            (
                ["password"],
                "",
                False,
            ),
            (
                ["password"],
                "password-0",
                False,
            ),
            (
                ["password-0", "password-1"],
                "password-0",
                True
            ),
            (
                ["password-0", "password-1"],
                "password-1",
                True
            )
        ]
    )
    def test_unlock_pdf_file_attempts_unlocking(
        self,
        monkeypatch: MonkeyPatch,
        passwords: list[str],
        pdf_password: str,
        should_unlock: bool
    ) -> None:
        """
        Assert that `_unlock_pdf_file`
        attempts unlocking a PDF file pointed at by the given file path.

        :param monkeypatch: `pytest` fixture for mocking functions.
        :param passwords: Passwords to attempt unlocking the PDF file with.
        :param pdf_password: Password needed to unlock the PDF file with.
        :param should_unlock: Whether the PDF file should have been unlocked or not.
        """

        did_unlock = False
        class _MockPDF:
            """Mock class of `pikepdf.Pdf`."""

            @staticmethod
            def open(
                filename_or_stream: str,
                allow_overwriting_input: bool = False,
                password: str = "",
            ) -> "_MockPDF":
                """
                Mock function of `pikepdf.Pdf.open` that
                mocks
                
                - opening a PDF file, and
                - raising an appropriate exception if said PDF file is not locked.
                
                :param allow_overwriting_input: Whether if the PDF file can be overwritten or not.
                :param filename_or_stream: Sanitized file path of the PDF file to unlock.
                :param password: Password needed to unlock the PDF file with.
                :raises PasswordError: If the PDF file is not unlocked.
                """

                nonlocal did_unlock

                assert allow_overwriting_input == (password != "")
                assert filename_or_stream == "test.pdf"

                if password != pdf_password:
                    raise PasswordError

                if pdf_password != "":
                    did_unlock = True

                return _MockPDF()

            def save(self, filename_or_stream: str) -> None:
                """
                Mock function of `pikepdf.Pdf.save` that
                mocks overwriting a PDF file.
                """

                assert did_unlock is True
                assert filename_or_stream == "test.pdf"

        monkeypatch.setattr(
            name = "Pdf",
            target = target,
            value = _MockPDF
        )

        _unlock_pdf_file(
            file_path = "test.pdf",
            grouped_pdf_file_paths = deepcopy(self.BASE_GROUPED_PDF_FILE_PATHS),
            passwords = passwords
        )

        assert did_unlock == should_unlock

    @mark.parametrize(
        "should_fail_on_open",
        [True, False]
    )
    def test_unlock_pdf_file_errs_on_pikepdf_fail(
        self,
        monkeypatch: MonkeyPatch,
        should_fail_on_open: bool
    ) -> None:
        """
        Assert that `_unlock_pdf_file`
        raises an appropriate exception
        when `pikepdf` fails.

        :param monkeypatch: `pytest` fixture for mocking functions.
        :param should_fail_on_open: Whether `pikepdf` should fail
                                    on attempt to open the PDF file or not.
        """

        class _MockFailingPDF:
            """Mock class of failing `pikepdf.Pdf`."""

            @staticmethod
            def open(
                filename_or_stream: str,
                allow_overwriting_input: bool = False,
                password: str = "",
            ) -> "_MockFailingPDF":
                """
                Mock function of `pikepdf.Pdf.open` that
                mocks raising an appropriate exception if

                  - opening said PDF file fails, or
                  - said PDF file is not locked.
                
                :param allow_overwriting_input: Whether if the PDF file can be overwritten or not.
                :param filename_or_stream: Sanitized file path of the PDF file to unlock.
                :param password: Password needed to unlock the PDF file with.
                :raises PasswordError: If the PDF file is not unlocked.
                :raises PdfError: If opening the PDF file fails.
                """

                assert allow_overwriting_input == (password != "")
                assert filename_or_stream == "test.pdf"

                if should_fail_on_open:
                    raise PdfError
                elif not allow_overwriting_input:
                    raise PasswordError

                return _MockFailingPDF()

            def save(self, filename_or_stream: str) -> None:
                """
                Mock function of `pikepdf.Pdf.save` that
                mocks overwriting a PDF file.

                :raises PdfError: If saving the PDF file fails.
                """

                assert filename_or_stream == "test.pdf"

                raise PdfError

        monkeypatch.setattr(
            name = "Pdf",
            target = target,
            value = _MockFailingPDF
        )

        with raises(
            expected_exception = PdfError,
            match = "Unlocking test.pdf failed."
        ):
            _unlock_pdf_file(
                file_path = "test.pdf",
                grouped_pdf_file_paths = deepcopy(self.BASE_GROUPED_PDF_FILE_PATHS),
                passwords = ["password"]
            )

    locked_grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS)
    not_locked_grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS)
    unlocked_grouped_pdf_file_paths = deepcopy(BASE_GROUPED_PDF_FILE_PATHS)

    locked_grouped_pdf_file_paths[FileState.LOCKED] = ["test.pdf"]
    not_locked_grouped_pdf_file_paths[FileState.NOT_LOCKED] = ["test.pdf"]
    unlocked_grouped_pdf_file_paths[FileState.UNLOCKED] = ["test.pdf"]

    @mark.parametrize(
        "initial_grouped_pdf_file_paths, passwords, pdf_password," \
        "final_grouped_pdf_file_paths",
        [
            (
                BASE_GROUPED_PDF_FILE_PATHS,
                ["password"],
                "password-0",
                locked_grouped_pdf_file_paths,
            ),
            (
                BASE_GROUPED_PDF_FILE_PATHS,
                ["password"],
                "",
                not_locked_grouped_pdf_file_paths
            ),
            (
                BASE_GROUPED_PDF_FILE_PATHS,
                ["password"],
                "password",
                unlocked_grouped_pdf_file_paths
            ),
            (
                locked_grouped_pdf_file_paths,
                ["password"],
                "password-0",
                locked_grouped_pdf_file_paths
            ),
            (
                not_locked_grouped_pdf_file_paths,
                ["password"],
                "",
                not_locked_grouped_pdf_file_paths
            ),
            (
                unlocked_grouped_pdf_file_paths,
                ["password"],
                "password",
                unlocked_grouped_pdf_file_paths
            )
        ]
    )
    def test_unlock_pdf_file_groups_pdf_file_path(
        self,
        final_grouped_pdf_file_paths: GroupedPaths,
        initial_grouped_pdf_file_paths: GroupedPaths,
        monkeypatch: MonkeyPatch,
        passwords: list[str],
        pdf_password: str
    ) -> None:
        """
        Assert that `_unlock_pdf_file`
        adds a PDF file path to an appropriate file state group
        based on unlocking result.

        :param final_grouped_pdf_file_paths: Resulting dictionary that maps file states with
                                             file paths of PDF files.
        :param initial_grouped_pdf_file_paths: Starting dictionary that maps file states with
                                               file paths of PDF files.
        :param monkeypatch: `pytest` fixture for mocking functions.
        :param passwords: Passwords to attempt unlocking the PDF file with.
        :param pdf_password: Password needed to unlock the PDF file with.
        """

        did_unlock = False
        grouped_pdf_file_paths = deepcopy(initial_grouped_pdf_file_paths)

        class _MockPDF:
            """Mock class of `pikepdf.Pdf`."""

            @staticmethod
            def open(
                filename_or_stream: str,
                allow_overwriting_input: bool = False,
                password: str = "",
            ) -> "_MockPDF":
                """
                Mock function of `pikepdf.Pdf.open` that
                mocks
                
                - opening a PDF file, and
                - raising an appropriate exception if said PDF file is not locked.
                
                :param allow_overwriting_input: Whether if the PDF file can be overwritten or not.
                :param filename_or_stream: Sanitized file path of the PDF file to unlock.
                :param password: Password needed to unlock the PDF file with.
                :raises PasswordError: If the PDF file is not unlocked.
                """

                nonlocal did_unlock

                assert allow_overwriting_input == (password != "")
                assert filename_or_stream == "test.pdf"

                if password != pdf_password:
                    raise PasswordError

                if pdf_password != "":
                    did_unlock = True

                return _MockPDF()

            def save(self, filename_or_stream: str) -> None:
                """
                Mock function of `pikepdf.Pdf.save` that
                mocks overwriting a PDF file.
                """

                assert did_unlock is True
                assert filename_or_stream == "test.pdf"

        monkeypatch.setattr(
            name = "Pdf",
            target = target,
            value = _MockPDF
        )

        _unlock_pdf_file(
            file_path = "test.pdf",
            grouped_pdf_file_paths = grouped_pdf_file_paths,
            passwords = passwords
        )

        assert grouped_pdf_file_paths == final_grouped_pdf_file_paths
