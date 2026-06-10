"""`unlock-pdf` enumerations."""

from enum import StrEnum
from typeguard import typechecked
from unlock_pdf.classes.string_generator_enumeration import StrGenEnum

class ErrorMessage(StrGenEnum):
    """Enumeration of error messages."""

    @classmethod
    @typechecked
    def _generate_failed_overwrite_error_message(cls, file_path: str) -> str:
        """
        Generate an error message for failed overwrite based on the path of a PDF file.
        
        :param file_path: Path of a PDF file.
        :raises TypeCheckError: If any argument or return value has an invalid type.
        :raises ValueError: If the file path is an empty string.
        :returns: Error message for failed overwrite.
        """

        if not file_path:
            raise ValueError(cls.EMPTY_FILE_PATH)

        return f"Unlocking {file_path} failed."

    EMPTY_FILE_PATH = "File path must be a non-empty string."
    FAILED_OVERWRITE = _generate_failed_overwrite_error_message
    NEGATIVE_FILE_STATE_COUNT = "File state count must be a non-negative integer."
    NO_INVALID_EXECUTION = "`unlock_pdf` must only be executed if directly imported from " + \
                           "`unlock_pdf.functions` and not from here."
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
    PASSWORDS = "Enter every password to attempt unlocking each PDF file with."
    PATHS = "Enter every directory path and/or file path of the PDF files to unlock."

class LogMessage(StrGenEnum):
    """Enumeration of log messages."""

    @classmethod
    @typechecked
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
        :raises TypeCheckError: If any argument or return value has an invalid type.
        :raises ValueError: If the file state count is a negative integer.
        :returns: Log message detailing the number of PDF files that are in said file state.
        """

        if file_state_count < 0:
            raise ValueError(ErrorMessage.NEGATIVE_FILE_STATE_COUNT)

        be_verb = "is" if file_state_count == 1 else "are"
        plural_suffix = "" if file_state_count == 1 else "s"

        return f"{file_state_count} PDF file{plural_suffix} {be_verb} {file_state}:"

    FILE_STATE_COUNT = _generate_file_state_count_log_message
    NO_PDF_FILE_PATH = "-"

class Module(StrEnum):
    """Enumeration of module names."""

    DIRECT_EXECUTION = "__main__"

class Path(StrEnum):
    """Enumeration of path constants."""

    PDF_FILE_EXTENSION = ".pdf"
    PDF_FILE_SEARCH_PATTERN = "/**/*.pdf"
    QUOTATION_MARK = '"'
