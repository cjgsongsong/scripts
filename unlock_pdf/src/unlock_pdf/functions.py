"""`unlock-pdf` functions."""

from glob import glob
from os.path import isdir, isfile
from pikepdf import (
    PasswordError,
    Pdf,
    PdfError
)
from typeguard import typechecked
from unlock_pdf.enumerations import (
    ErrorMessage,
    FileState,
    InputPrompt,
    LogMessage,
    Path
)
from unlock_pdf.types import (
    GroupedPaths,
    MainInputPrompt,
    Inputs,
    Passwords,
    Paths
)

@typechecked
def _get_passwords() -> Passwords:
    """
    Get the passwords to attempt unlocking each PDF file with.

    :raises ValueError: If no password was given.
    :returns: Set of passwords to attempt unlocking each PDF file with.
    """

    passwords = _get_unique_inputs(InputPrompt.PASSWORDS)

    if not passwords:
        raise ValueError(ErrorMessage.NO_VALID_PASSWORD)

    return passwords

@typechecked
def _get_pdf_file_paths() -> Paths:
    """
    Get the paths of all PDF files to unlock from every inputted

    - directory path where some PDF files are, and/or
    - file path of a PDF file.

    :raises FileNotFoundError: If every path does not ultimately point to a PDF file.
    :returns: Set of paths of all PDF files to unlock.
    """

    paths = _get_unique_inputs(InputPrompt.PATHS)
    pdf_file_paths: Paths = set()

    for path in paths:
        pdf_file_paths.update(
            _get_pdf_file_subpaths(
                _sanitize_path(path)
            )
        )

    if not pdf_file_paths:
        raise FileNotFoundError(ErrorMessage.NO_VALID_PATH)

    return pdf_file_paths

@typechecked
def _get_pdf_file_subpaths(path: str) -> Paths:
    """
    Get the paths of some PDF files to unlock from either

    - a directory path where some PDF files are, or
    - a file path of a PDF file.

    :param path: Directory path or file path of some PDF files to unlock.
    :returns: Set of paths of some PDF files to unlock.
    """

    if isdir(path):
        return set(
            glob(
                pathname = path + Path.PDF_FILE_SEARCH_PATTERN,
                recursive = True
            )
        )
    elif _is_pdf_file(path):
        return set(path)

    return set()

@typechecked
def _get_unique_inputs(prompt: MainInputPrompt) -> Inputs:
    """
    Get unique inputs until an empty string is given.
    
    :param prompt: Prompt detailing what inputs are being asked of the user.
    :returns: Set of unique inputs.
    """

    print(prompt)
    print(InputPrompt.END)
    print(InputPrompt.MARKER)

    user_inputs: Inputs = set()

    user_input = input()
    while user_input != "":
        user_inputs.add(user_input)

        user_input = input()

    return user_inputs

@typechecked
def _is_pdf_file(file_path: str) -> bool:
    """
    Validate if a file path

    - has the PDF file extension, and
    - points to a file.

    :param file_path: Path of a file.
    :returns: Whether the file path directly points to a PDF file or not.
    """

    return (
        file_path.endswith(Path.PDF_FILE_EXTENSION)
        and isfile(file_path)
    )

@typechecked
def _log_unlock_attempt(grouped_pdf_file_paths: GroupedPaths) -> None:
    """
    Log for every file state

    - how many PDF files are in such file state, and
    - what are the file paths of those PDF files.

    :param grouped_pdf_file_paths: Dictionary that maps file states with file paths of PDF files.
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

@typechecked
def _sanitize_path(path: str) -> str:
    """
    Remove quotation marks from a pasted path.

    :param path: Directory path or file path of some PDF files to unlock.
    :returns: Sanitized aforementioned path.
    """

    return path \
        .removeprefix(Path.QUOTATION_MARK) \
        .removesuffix(Path.QUOTATION_MARK)

@typechecked
def _unlock_pdf_file(
        file_path: str,
        grouped_pdf_file_paths: GroupedPaths,
        passwords: Passwords
    ) -> None:
    """
    Overwrite a PDF file as its unlocked version.

    :param file_path: Sanitized file path of the PDF file to unlock.
    :param grouped_pdf_file_paths: Dictionary that maps file states with file paths of PDF files.
    :param passwords: Passwords to attempt unlocking the PDF file with.
    :raises PdfError: If unlocking the PDF file via `pikepdf` failed.
    """

    try:
        Pdf.open(file_path)

        grouped_pdf_file_paths \
            [FileState.NOT_LOCKED] \
            .add(file_path)
    except PasswordError:
        did_unlock = False

        for password in passwords:
            try:
                Pdf \
                    .open(
                        allow_overwriting_input = True,
                        filename_or_stream = file_path,
                        password = password
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
            .add(file_path)

@typechecked
def unlock_pdf() -> None:
    """
    Unlock password-protected PDF files for every inputted

    - directory path where some PDF files are, and/or
    - file path of a PDF file

    using inputted passwords to attempt unlocking each PDF file with.

    :raises FileNotFoundError: If every path does not ultimately point to a PDF file.
    :raises PdfError: If unlocking a PDF file via `_unlock_pdf` failed.
    :raises ValueError: If no password was given.
    """

    # <NOTE>
    # Enforce input order via order of variable declaration.
    pdf_file_paths = _get_pdf_file_paths()
    passwords = _get_passwords()

    grouped_pdf_file_paths: GroupedPaths = {
        key: set()
        for key in [
            file_state for file_state in FileState
        ]
    }

    for pdf_file_path in pdf_file_paths:
        _unlock_pdf_file(
            grouped_pdf_file_paths = grouped_pdf_file_paths,
            file_path = pdf_file_path,
            passwords = passwords
        )

    _log_unlock_attempt(grouped_pdf_file_paths)
