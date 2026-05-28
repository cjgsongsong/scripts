"""Tests for `unlock-pdf` enumerations."""

from pytest import mark, raises
from unlock_pdf.enumerations import (
    ErrorMessage,
    FileState,
    LogMessage
)

class TestMessageGeneration:
    """Tests for message generation."""

    def test_generate_failed_overwrite_error_message_errs_with_invalid_file_path(self) -> None:
        """
        Assert that `_generate_failed_overwrite_error_message`
        raises an appropriate exception
        when given an invalid file path.
        """

        with raises(
            expected_exception = ValueError,
            match = "File path must be a non-empty string"
        ):
            ErrorMessage.FAILED_OVERWRITE("")

    def test_generate_failed_overwrite_error_message_generates_with_valid_file_path(self) -> None:
        """
        Assert that `_generate_failed_overwrite_error_message`
        generates an error message for failed overwrite that

        - has the correct format, and
        - includes the given file path

        when given a valid file path.
        """

        assert ErrorMessage.FAILED_OVERWRITE("test.pdf") == "Unlocking test.pdf failed."

    def test_generate_file_state_count_log_message_errs_with_invalid_arguments(self) -> None:
        """
        Assert that `_generate_file_state_count_log_message`
        raises an appropriate exception
        when given an invalid argument.
        """

        with raises(
            expected_exception = ValueError,
            match = "File state count must be a non-negative integer."
        ):
            LogMessage.FILE_STATE_COUNT(
                file_state = FileState.LOCKED,
                file_state_count = -1
            )

    @mark.parametrize(
        "file_state, file_state_count," \
        "log_message",
        [
            (
                FileState.LOCKED,
                0,
                "0 PDF files are still locked:"
            ),
            (
                FileState.NOT_LOCKED,
                1,
                "1 PDF file is not locked:"
            ),
            (
                FileState.UNLOCKED,
                2,
                "2 PDF files are unlocked:"
            )
        ]
    )
    def test_generate_file_state_count_log_message_generates_with_valid_arguments(
        self,
        file_state: FileState,
        file_state_count: int,
        log_message: str
    ) -> None:
        """
        Assert that `_generate_file_state_count_log_message`
        generates a log message that

        - has the correct format,
        - is grammatically correct, and
        - includes
          - the given file state, and
          - the given file state count

        when given valid arguments.

        :param file_state: State of a PDF file after an unlock attempt.
        :param file_state_count: Number of PDF files that are in said file state.
        :param log_message: Log message detailing the number of PDF files
                            that are in said file state.
        """

        assert LogMessage.FILE_STATE_COUNT(
            file_state = file_state,
            file_state_count = file_state_count
        ) == log_message
