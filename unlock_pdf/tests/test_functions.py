"""Tests for `unlock-pdf` functions."""

# pyright: reportPrivateUsage=false

from pytest import (
    CaptureFixture,
    MonkeyPatch,
    mark
)
from unlock_pdf.enumerations import InputPrompt
from unlock_pdf.functions import (
    _get_unique_inputs,
    _is_pdf_file,
    _sanitize_path
)
from unlock_pdf.types import MainInputPrompt

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

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
