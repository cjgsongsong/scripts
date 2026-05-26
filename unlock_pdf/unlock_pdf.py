"""
Script for unlocking password-protected PDF files.
"""

from enum import Enum, StrEnum
from glob import glob
from os.path import isdir, isfile
from pikepdf import (
    PasswordError,
    Pdf,
    PdfError,
)
from typing import Literal

PDF_FILE_EXTENSION = ".pdf"
PDF_FILE_SEARCH_PATTERN = f"/**/*{PDF_FILE_EXTENSION}"
QUOTATION_MARK = '"'

class ErrorMessage(Enum):
    """Enumeration of error messages."""

    @classmethod
    def _generate_failed_overwrite_error_message(cls, file_path: str) -> str:
        """
        Generate an error message for failed overwrite based on the path of the PDF file.
        
        :param file_path: Path of the PDF file.
        :returns: Error message for failed overwrite.
        """

        return f"Unlocking `{file_path}` failed."

    FAILED_OVERWRITE = _generate_failed_overwrite_error_message
    NO_VALID_PASSWORD = "At least one password must be given."
    NO_VALID_PATH = "At least one path must ultimately point to a PDF file."

class FileState(StrEnum):
    """Enumeration of states a PDF file may be after an unlock attempt."""

    LOCKED = "still locked"
    NOT_LOCKED = "not locked"
    UNLOCKED = "unlocked"

class InputPrompt(StrEnum):
    """Enumeration of input prompt constants."""

    END = "Enter an empty string to quit."
    MARKER = ">"
    PASSWORDS = "Enter every password to attempt unlocking the PDF file(s) with."
    PATHS = "Enter every directory path or file path of the PDF file(s) to unlock."

file_state_counts = dict.fromkeys(
    [file_state for file_state in FileState],
    0
)

def _log_file_state_counts() -> None:
    """Log the counts of every file state after the unlock attempt."""

    print()
    for file_state, count in file_state_counts.items():
        be_verb = "is" if count == 1 else "are"
        plural_suffix = "" if count == 1 else "s"

        print(f"{count} PDF file{plural_suffix} {be_verb} {file_state.value}.")

def _get_inputs(prompt: Literal[InputPrompt.PASSWORDS, InputPrompt.PATHS]) -> list[str]:
    """
    Get inputs until an empty string is given.
    
    :param prompt: Prompt on what inputs are being asked of the user.
    :returns: List of inputs
    """

    print(prompt)
    print(InputPrompt.END)
    print(InputPrompt.MARKER)

    user_input = input()
    user_inputs: list[str] = []

    while user_input != "":
        user_inputs.append(user_input)

        user_input = input()

    return user_inputs

def _get_pdf_file_paths(path: str) -> list[str]:
    """
    Get the path(s) of PDF file(s) in the given path.

    :param path: Path of either the directory containing the PDF file(s) or the PDF file.
    :returns: List of paths of PDF files.
    """

    if isdir(path):
        return glob(
            pathname = path + PDF_FILE_SEARCH_PATTERN,
            recursive = True
        )
    elif _is_pdf_file(path):
        return [path]

    return []

def _is_pdf_file(file_path: str) -> bool:
    """
    Validate if the file path
    - has the PDF file extension, and
    - points to a file.

    :param file_path: Path of the PDF file.
    :returns: Whether the file path points to a PDF file or not.
    """

    return (
        file_path.endswith(PDF_FILE_EXTENSION)
        and isfile(file_path)
    )

def _sanitize_path(path: str) -> str:
    """
    Remove quotation marks from the pasted path.

    :param path: Path of either the directory containing the PDF file(s) or the PDF file.
    :returns: Sanitized path.
    """

    return path \
        .removeprefix(QUOTATION_MARK) \
        .removesuffix(QUOTATION_MARK)

def _unlock_pdf_file(
        file_path: str,
        passwords: list[str]
    ) -> None:
    """
    Overwrite the PDF file as its unlocked version.

    :param file_path: Sanitized path of the PDF file.
    :param passwords: Passwords to attempt unlocking the PDF file with.
    :raises PdfError: If unlocking the PDF file via `pikepdf` failed.
    """

    try:
        Pdf.open(file_path)

        file_state_counts[FileState.NOT_LOCKED] += 1

        print(f"`{file_path}` is not locked.")
    except PasswordError:
        did_unlock = False

        for password in passwords:
            try:
                Pdf \
                    .open(
                        allow_overwriting_input = True,
                        filename_or_stream = file_path,
                        password = password,
                    ) \
                    .save(file_path)

                did_unlock = True

                break
            except PasswordError:
                continue
            except Exception as exception:
                raise PdfError(
                    ErrorMessage.FAILED_OVERWRITE(file_path)
                ) from exception

        if did_unlock:
            file_state_counts[FileState.UNLOCKED] += 1

            print(f"`{file_path}` is now unlocked.")
        else:
            file_state_counts[FileState.LOCKED] += 1

            print(f"`{file_path}` is still locked.")

def unlock_pdf(
        passwords: list[str],
        paths: list[str]
    ) -> None:
    """
    Unlock password-protected PDF files in the specified path.

    :param passwords: Passwords to attempt unlocking the PDF files with.
    :param path: Path of either the directory containing the PDF file(s) or the PDF file.
    :raises FileNotFoundError: If every path and its subpaths do not point to any PDF file.
    :raises PdfError: If unlocking a PDF file via `_unlock_pdf` failed.
    :raises ValueError: If no password was given.
    """

    if not passwords:
        raise ValueError(ErrorMessage.NO_VALID_PASSWORD)

    pdf_file_paths: list[str] = []

    for path in paths:
        pdf_file_paths += _get_pdf_file_paths(
            _sanitize_path(path)
        )

    if not pdf_file_paths:
        raise FileNotFoundError(ErrorMessage.NO_VALID_PATH)

    for pdf_file_path in pdf_file_paths:
        _unlock_pdf_file(
            file_path = pdf_file_path,
            passwords = passwords
        )

    _log_file_state_counts()

# Enforce input order via parameter order
unlock_pdf(
    paths = _get_inputs(InputPrompt.PATHS),
    passwords = _get_inputs(InputPrompt.PASSWORDS)
)
