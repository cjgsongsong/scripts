"""Tests for `unlock-pdf` log message generation."""

from pytest import mark, raises
from unlock_pdf.enumerations import FileState, LogMessage

@mark.parametrize(
    "test_file_state, test_file_state_count," \
    "test_log_message",
    [
        (
            FileState.LOCKED, 0,
            "0 PDF files are still locked:"
        ),
        (
            FileState.NOT_LOCKED, 1,
            "1 PDF file is not locked:"
        ),
        (
            FileState.UNLOCKED, 2,
            "2 PDF files are unlocked:"
        )
    ]
)
def test_generate_file_state_count_log_message_generates_log_message(
    test_file_state: FileState,
    test_file_state_count: int,
    test_log_message: str
) -> None:
    """
    Assert that `_generate_file_state_count_log_message`
    generates a log message that

    - has the correct format,
    - includes
      - the given file state, and
      - the given file state count, and
    - uses the correct be verb.

    when given valid arguments.

    :param test_file_state: State of a PDF file after an unlock attempt.
    :param test_file_state_count: Number of PDF files that are in said file state.
    :param test_log_message: Log message detailing the number of PDF files
                             that are in said file state.
    """

    assert LogMessage.FILE_STATE_COUNT(
        file_state = test_file_state,
        file_state_count = test_file_state_count
    ) == test_log_message

def test_generate_file_state_count_log_message_raises_exception() -> None:
    """
    Assert that `_generate_file_state_count_log_message`
    raises an appropriate exception
    when given a negative file state count.
    """

    with raises(
        expected_exception = ValueError,
        match = "File state count must be a non-negative integer."
    ):
        LogMessage.FILE_STATE_COUNT(
            file_state = FileState.LOCKED,
            file_state_count = -1
        )
