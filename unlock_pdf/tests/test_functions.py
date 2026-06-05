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
from unlock_pdf.enumerations import FileState, InputPrompt
from unlock_pdf.functions import (
    _get_pdf_file_paths,
    _get_pdf_file_subpaths,
    _get_unique_inputs,
    _is_pdf_file,
    _log_unlock_attempt,
    _sanitize_path,
    _unlock_pdf_file,
    unlock_pdf
)
from unlock_pdf.types import GroupedPaths, MainInputPrompt

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

class TestGetPDFFilePaths:
    """Tests for `_get_pdf_file_paths`."""

    NO_PATH: list[str] = []

    def test_get_pdf_file_paths_errs_with_no_path(self, monkeypatch: MonkeyPatch) -> None:
        """
        Assert that `_get_pdf_file_paths`
        raises an appropriate exception
        when given no path.

        :param monkeypatch: `pytest` fixture for mocking functions.
        """

        def _mock_get_unique_inputs(prompt: str) -> list[str]:
            """
            Mock function of `unlock-pdf.functions._get_unique_inputs` that
            returns a mock ordered list of unique paths of all PDF files to unlock.
            
            :param prompt: Prompt detailing what inputs are being asked of the user.
            :returns Mock ordered list of unique paths of all PDF files to unlock.
            """

            assert \
                prompt == "Enter every directory path and/or file path of the PDF files to unlock."

            return self.NO_PATH

        monkeypatch.setattr(
            name = "_get_unique_inputs",
            target = target,
            value = _mock_get_unique_inputs
        )

        with raises(
            expected_exception = FileNotFoundError,
            match = "At least one path must ultimately point to a PDF file."
        ):
            _get_pdf_file_paths()

    @mark.parametrize(
        "paths, pdf_file_subpaths," \
        "pdf_file_paths",
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
    def test_get_pdf_file_paths_returns_with_valid_paths(
        self,
        monkeypatch: MonkeyPatch,
        paths: list[str],
        pdf_file_paths: list[str],
        pdf_file_subpaths: list[list[str]],
    ) -> None:
        """
        Assert that `_get_pdf_file_paths`
        returns the set of paths of all PDF files to unlock
        from inputted paths.

        :param monkeypatch: `pytest` fixture for mocking functions.
        :param paths: Mock return value of `_get_unique_inputs`.
        :param pdf_file_paths: Ordered list of unique paths of all PDF files to unlock.
        :param pdf_file_subpaths: List of mock return values of `_get_pdf_file_subpaths`.
        """

        call_count = -1

        def _mock_get_pdf_file_subpaths(path: str) -> list[str]:
            """
            Mock function of `unlock-pdf.functions._get_pdf_file_subpaths` that
            returns a mock ordered list of unique paths of some PDF files to unlock
            based on how many times the function has been called.

            :param path: Directory path or file path of some PDF files to unlock.
            :returns Mock ordered list of unique paths of some PDF files to unlock.
            """

            nonlocal call_count

            call_count += 1

            assert path in paths

            return pdf_file_subpaths[call_count]

        def _mock_get_unique_inputs(prompt: str) -> list[str]:
            """
            Mock function of `unlock-pdf.functions._get_unique_inputs` that
            returns a mock ordered list of unique paths of all PDF files to unlock.
            
            :param prompt: Prompt detailing what inputs are being asked of the user.
            :returns Mock ordered list of unique paths of all PDF files to unlock.
            """

            assert \
                prompt == "Enter every directory path and/or file path of the PDF files to unlock."

            return paths

        monkeypatch.setattr(
            name = "_get_pdf_file_subpaths",
            target = target,
            value = _mock_get_pdf_file_subpaths
        )
        monkeypatch.setattr(
            name = "_get_unique_inputs",
            target = target,
            value = _mock_get_unique_inputs
        )

        assert _get_pdf_file_paths() == pdf_file_paths

class TestGetPDFFileSubpaths:
    """Tests for `_get_pdf_file_subpaths`."""

    NO_PDF_FILE_SUBPATH: list[str] = list()

    @mark.parametrize(
        "path," \
        "glob_paths, is_directory, is_pdf_file," \
        "pdf_file_subpaths",
        [
            (
                "test-directory/",
                ["test-directory/test-0.pdf", "test-directory/test-1.pdf"],
                True,
                False,
                ["test-directory/test-0.pdf", "test-directory/test-1.pdf"]
            ),
            (
                "test.pdf",
                [],
                False,
                True,
                ["test.pdf"]
            ),
            (
                "",
                [],
                False,
                False,
                NO_PDF_FILE_SUBPATH
            )
        ]
    )
    def test_get_pdf_file_subpaths_returns_with_valid_path(
        self,
        glob_paths: list[str],
        is_directory: bool,
        is_pdf_file: bool,
        monkeypatch: MonkeyPatch,
        path: str,
        pdf_file_subpaths: list[str]
    ) -> None:
        """
        Asserts that `_get_pdf_file_subpaths`
        returns the set of paths of some PDF files to unlock
        when given a valid path.
        
        :param file_path_pattern: File path pattern to match.
        :param glob_paths: Mock return value of `glob.glob`.
        :param is_directory: Mock return value of `os.path.isdir`.
        :param is_pdf_file: Mock return value of `unlock-pdf.functions._is_pdf_file`. 
        :param monkeypatch: `pytest` fixture for mocking functions.
        :param path: Directory path or file path of some PDF files to unlock.
        :param pdf_file_subpaths: Ordered list of unique paths of some PDF files to unlock.
        """

        def _mock_glob(pathname: str, recursive: bool) -> list[str]:
            """
            Mock function of `glob.glob` that
            returns a list of paths that match the given file path pattern.
            
            :param pathname: File path pattern.
            :param recursive: Whether to recursively look for matches in directories or not.
            :returns List of paths that match the given file path pattern.
            """

            assert pathname == path + "/**/*.pdf"
            assert recursive is True

            return glob_paths

        def _mock_isdir(pathname: str) -> bool:
            """
            Mock function of `os.path.isdir` that
            returns a mock boolean that
            tells whether the path directly points to a directory or not.

            :param pathname: Path.
            :returns: Mock boolean that
                      tells whether the path directly points to a directory or not.
            """

            assert pathname == path

            return is_directory

        def _mock_is_pdf_file(pathname: str) -> bool:
            """
            Mock function of `unlock-pdf.functions._is_pdf_file` that
            returns a mock boolean that
            tells whether the file path directly points to a PDF file or not.

            :param pathname: Path.
            :returns: Mock boolean that
                      tells whether the file path directly points to a PDF file or not.
            """

            assert pathname == path

            return is_pdf_file

        monkeypatch.setattr(
            name = "_is_pdf_file",
            target = target,
            value = _mock_is_pdf_file
        )
        monkeypatch.setattr(
            name = "glob",
            target = target,
            value = _mock_glob
        )
        monkeypatch.setattr(
            name = "isdir",
            target = target,
            value = _mock_isdir
        )

        assert _get_pdf_file_subpaths(path) == pdf_file_subpaths

class TestGetUniqueInputs:
    """Tests for `_get_unique_inputs`."""

    NO_UNIQUE_INPUT: list[str] = []
    TARGET_INPUT_FUNCTION = "builtins.input"

    @mark.parametrize(
        "prompt," \
        "main_input_prompt",
        [
            (
                InputPrompt.PASSWORDS,
                "Enter every password to attempt unlocking each PDF file with."
            ),
            (
                InputPrompt.PATHS,
                "Enter every directory path and/or file path of the PDF files to unlock."
            )
        ]
    )
    def test_get_unique_inputs_prints_with_valid_prompt(
        self,
        capsys: CaptureFixture[str],
        main_input_prompt: MainInputPrompt,
        monkeypatch: MonkeyPatch,
        prompt: MainInputPrompt
    ) -> None:
        """
        Assert that `_get_unique_inputs`
        prints prompts

        - in correct order, and
        - including the given prompt

        when given a valid prompt.

        :param capsys: `pytest` fixture for capturing outputs.
        :param main_input_prompt: Printed main input prompt.
        :param monkeypatch: `pytest` fixture for mocking functions.
        :param prompt: Prompt detailing what inputs are being asked of the user.
        """

        monkeypatch.setattr(self.TARGET_INPUT_FUNCTION, lambda: "")

        _get_unique_inputs(prompt)

        assert (
            capsys \
                .readouterr() \
                .out
        ) == (
            main_input_prompt
            + "\n"
            + "Enter an empty string to quit."
            + "\n"
            + ">"
            + "\n"
        )

    @mark.parametrize(
        "user_inputs," \
        "unique_inputs",
        [
            (
                [""],
                NO_UNIQUE_INPUT,
            ),
            (
                ["password", ""],
                ["password"]
            ),
            (
                [
                    "password",
                    "password",
                    ""
                ],
                ["password"]
            ),
            (
                [
                    "password",
                    "another_password",
                    ""
                ],
                ["password", "another_password"]
            )
        ]
    )
    def test_get_unique_inputs_returns_with_valid_prompt(
        self,
        monkeypatch: MonkeyPatch,
        unique_inputs: list[str],
        user_inputs: list[str]
    ) -> None:
        """
        Assert that `_get_unique_inputs`
        returns all unique inputs as an ordered list
        when given a valid prompt.

        :param monkeypatch: `pytest` fixture for mocking functions.
        :param unique_inputs: Ordered list of unique inputs.
        :param user_inputs: User inputs.
        """

        call_count = -1

        def _mock_input() -> str:
            """
            Mock function of `builtins.input` that
            returns a mock user input based on how many times the function has been called.

            :returns: Mock user input.
            """
            nonlocal call_count

            call_count += 1

            return user_inputs[call_count]

        monkeypatch.setattr(self.TARGET_INPUT_FUNCTION, _mock_input)

        assert _get_unique_inputs(InputPrompt.PASSWORDS) == unique_inputs

class TestIsPDFFile:
    """Tests for `_is_pdf_file`."""

    @mark.parametrize(
        "file_path, is_file," \
        "flag_value",
        [
            (
                "corrupted-test.pdf",
                False,
                False
            ),
            (
                "test.pdf",
                True,
                True
            ),
            (
                "test.txt",
                False,
                False
            ),
            (
                "test.txt",
                True,
                False
            )
        ]
    )
    def test_is_pdf_file_returns_with_valid_file_path(
        self,
        file_path: str,
        flag_value: bool,
        is_file: bool,
        monkeypatch: MonkeyPatch
    ) -> None:
        """
        Assert that `_is_pdf_file`
        returns whether the file path directly points to a PDF file or not
        when given a valid file path.
        
        :param file_path: Path of a file.
        :param flag_value: Whether the file path directly points to a PDF file or not.
        :param is_file: Mock return value of `os.path.isfile`.
        :param monkeypatch: `pytest` fixture for mocking functions.
        """

        def _mock_isfile(path: str) -> bool:
            """
            Mock function of `os.path.isfile` that
            returns a mock boolean that tells whether the path directly points to a file or not.
            
            :param path: Path.
            :returns: Mock boolean that tells whether the path directly points to a file or not.
            """

            assert path == file_path

            return is_file

        monkeypatch.setattr(
            name = "isfile",
            target = target,
            value = _mock_isfile
        )

        assert _is_pdf_file(file_path) == flag_value

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
