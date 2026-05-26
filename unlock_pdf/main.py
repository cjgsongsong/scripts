"""
Script for unlocking password-protected PDF files.
"""

from enumerations import (
    ErrorMessage,
    FileState,
    InputPrompt,
    LogMessage,
    Path
)
from glob import glob
from os.path import isdir, isfile
from pikepdf import (
    PasswordError,
    Pdf,
    PdfError,
)
from typing import Literal

def _get_inputs(prompt: Literal[InputPrompt.PASSWORDS, InputPrompt.PATHS]) -> set[str]:
    """
    Get inputs until an empty string is given.
    
    :param prompt: Prompt on what inputs are being asked of the user.
    :returns: List of inputs
    """

    print(prompt)
    print(InputPrompt.END)
    print(InputPrompt.MARKER)

    user_input = input()
    user_inputs: set[str] = set()

    while user_input != "":
        user_inputs.add(user_input)

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
            pathname = path + Path.PDF_FILE_SEARCH_PATTERN,
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
        file_path.endswith(Path.PDF_FILE_EXTENSION)
        and isfile(file_path)
    )

def _log_unlock_attempt() -> None:
    """
    Log after the unlock attempt per file state
    - how many PDF files resulted to such state, and
    - what are the paths to said PDF files.
    """

    for file_state, pdf_file_paths in grouped_pdf_file_paths.items():
        file_state_count = len(pdf_file_paths)

        print(
            LogMessage.FILE_STATE_COUNT(
                file_state = file_state,
                file_state_count = file_state_count
            )
        )

        if file_state_count:
            for pdf_file_path in pdf_file_paths:
                print(pdf_file_path)
        else:
            print(LogMessage.NO_PDF_FILE_PATH)

        print()

def _sanitize_path(path: str) -> str:
    """
    Remove quotation marks from the pasted path.

    :param path: Path of either the directory containing the PDF file(s) or the PDF file.
    :returns: Sanitized path.
    """

    return path \
        .removeprefix(Path.QUOTATION_MARK) \
        .removesuffix(Path.QUOTATION_MARK)

def _unlock_pdf_file(
        file_path: str,
        passwords: set[str]
    ) -> None:
    """
    Overwrite the PDF file as its unlocked version.

    :param file_path: Sanitized path of the PDF file.
    :param passwords: Passwords to attempt unlocking the PDF file with.
    :raises PdfError: If unlocking the PDF file via `pikepdf` failed.
    """

    try:
        Pdf.open(file_path)

        grouped_pdf_file_paths \
            [FileState.NOT_LOCKED] \
            .append(file_path)
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

        grouped_pdf_file_paths \
            [FileState.UNLOCKED if did_unlock else FileState.LOCKED] \
            .append(file_path)

def unlock_pdf(
        passwords: set[str],
        paths: set[str]
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

    pdf_file_paths: set[str] = set()

    for path in paths:
        pdf_file_paths.update(
            _get_pdf_file_paths(
                _sanitize_path(path)
            )
        )

    if not pdf_file_paths:
        raise FileNotFoundError(ErrorMessage.NO_VALID_PATH)

    for pdf_file_path in pdf_file_paths:
        _unlock_pdf_file(
            file_path = pdf_file_path,
            passwords = passwords
        )

    _log_unlock_attempt()

grouped_pdf_file_paths: dict[FileState, list[str]] = {
    key: []
    for key in [
        file_state for file_state in FileState
    ]
}

# Enforce input order via parameter order
unlock_pdf(
    paths = _get_inputs(InputPrompt.PATHS),
    passwords = _get_inputs(InputPrompt.PASSWORDS)
)
