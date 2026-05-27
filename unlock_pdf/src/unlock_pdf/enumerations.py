"""`unlock-pdf` enumerations."""

from enum import StrEnum
from unlock_pdf.classes import MessageEnum

class ErrorMessage(MessageEnum):
    """Enumeration of error messages."""

    @classmethod
    def _generate_failed_overwrite_error_message(cls, file_path: str) -> str:
        """
        Generate an error message for failed overwrite based on the path of a PDF file.
        
        :param file_path: Path of a PDF file.
        :returns: Error message for failed overwrite.
        """

        return f"Unlocking `{file_path}` failed."

    FAILED_OVERWRITE = _generate_failed_overwrite_error_message
    NO_VALID_PASSWORD = "At least one password must be given."
    NO_VALID_PATH = "At least one path must ultimately point to a PDF file."

class FileState(StrEnum):
    """Enumeration of states that a PDF file may be after an unlock attempt."""

    LOCKED = "still locked"
    NOT_LOCKED = "not locked"
    UNLOCKED = "unlocked"

class InputPrompt(StrEnum):
    """Enumeration of input prompt constants."""

    END = "Enter an empty string to quit."
    MARKER = ">"
    PASSWORDS = "Enter every password to attempt unlocking the PDF file(s) with."
    PATHS = "Enter every directory path or file path of the PDF file(s) to unlock."

class LogMessage(MessageEnum):
    """Enumeration of log messages."""

    @classmethod
    def _generate_file_state_count_log_message(
        cls,
        file_state: FileState,
        file_state_count: int
    ) -> str:
        """
        Generate a log message based on
        - a file state, and
        - the number of PDF files that are in said file state.

        :param file_state: State of a PDF file after an unlock attempt.
        :param file_state_count: Number of PDF files that are in said file state.
        :returns: Log message detailing the number of PDF files that are in said file state.
        """

        be_verb = "is" if file_state_count == 1 else "are"
        plural_suffix = "" if file_state_count == 1 else "s"

        return f"{file_state_count} PDF file{plural_suffix} {be_verb} {file_state}:"

    FILE_STATE_COUNT = _generate_file_state_count_log_message
    NO_PDF_FILE_PATH = "-"

class Path(StrEnum):
    """Enumeration of path constants."""

    PDF_FILE_EXTENSION = ".pdf"
    PDF_FILE_SEARCH_PATTERN = "/**/*.pdf"
    QUOTATION_MARK = '"'

class Python(StrEnum):
    """Enumeration of Python constants."""

    DIRECT_EXECUTION_MODULE = "__main__"
