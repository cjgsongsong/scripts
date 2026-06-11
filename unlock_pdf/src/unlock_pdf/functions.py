"""`unlock-pdf` functions."""

from glob import escape, glob
from os.path import isdir, isfile
from pikepdf import (
    PasswordError,
    Pdf,
    PdfError
)
from typeguard import typechecked
from unlock_pdf.classes.path_dictionary import PathDictionary
from unlock_pdf.enumerations import (
    ErrorMessage,
    FileState,
    InputPrompt,
    LogMessage,
    Path
)
from unlock_pdf.types import (
    MainInputPrompt,
    Inputs,
    Passwords,
    Paths
)

@typechecked
def _get_passwords() -> Passwords:
    """
    Get the passwords to attempt unlocking each PDF file with.

    :raises TypeCheckError: If any argument or return value has an invalid type.
    :raises ValueError: If no password was given.
    :returns: Ordered list of unique passwords to attempt unlocking each PDF file with.
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
    :raises TypeCheckError: If any argument or return value has an invalid type.
    :returns: Ordered list of unique paths of all PDF files to unlock.
    """

    paths = _get_unique_inputs(InputPrompt.PATHS)
    pdf_file_paths: Paths = []

    for path in paths:
        subpaths = _get_pdf_file_subpaths(
            _sanitize_path(path)
        )

        for subpath in subpaths:
            if subpath not in pdf_file_paths:
                pdf_file_paths.append(subpath)

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
    :raises TypeCheckError: If any argument or return value has an invalid type.
    :returns: Ordered list of unique paths of some PDF files to unlock.
    """

    if isdir(path):
        return glob(
            pathname = escape(path) + Path.PDF_FILE_SEARCH_PATTERN,
            recursive = True
        )
    elif _is_pdf_file(path):
        return [path]

    return []

@typechecked
def _get_unique_inputs(prompt: MainInputPrompt) -> Inputs:
    """
    Get unique inputs until an empty string is given.
    
    :param prompt: Prompt detailing what inputs are being asked of the user.
    :raises TypeCheckError: If any argument or return value has an invalid type.
    :returns: Ordered list of unique inputs.
    """

    print(prompt)
    print(InputPrompt.END)
    print(InputPrompt.MARKER)

    user_inputs: Inputs = []

    user_input = input()
    while user_input != "":
        if user_input not in user_inputs:
            user_inputs.append(user_input)

        user_input = input()

    return user_inputs

@typechecked
def _is_pdf_file(file_path: str) -> bool:
    """
    Validate if a file path

    - has the PDF file extension, and
    - points to a file.

    :param file_path: Path of a file.
    :raises TypeCheckError: If any argument or return value has an invalid type.
    :returns: Whether the file path directly points to a PDF file or not.
    """

    return (
        file_path.endswith(Path.PDF_FILE_EXTENSION)
        and isfile(file_path)
    )

@typechecked
def _log_unlock_attempt(path_dictionary: PathDictionary) -> None:
    """
    Log for every file state

    - how many PDF files are in such file state, and
    - what are the file paths of those PDF files.

    :param path_dictionary: Dictionary that maps file states with PDF file paths.
    :raises TypeCheckError: If any argument or return value has an invalid type.
    """

    for file_state, pdf_file_paths in path_dictionary.items():
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
    :raises TypeCheckError: If any argument or return value has an invalid type.
    :returns: Sanitized aforementioned path.
    """

    return path \
        .removeprefix(Path.QUOTATION_MARK) \
        .removesuffix(Path.QUOTATION_MARK)

@typechecked
def _unlock_pdf_file(
        file_path: str,
        passwords: Passwords,
        path_dictionary: PathDictionary
    ) -> None:
    """
    Overwrite a PDF file as its unlocked version.

    :param file_path: Sanitized file path of the PDF file to unlock.
    :param passwords: Passwords to attempt unlocking the PDF file with.
    :param path_dictionary: Dictionary that maps file states with PDF file paths.
    :raises PdfError: If unlocking the PDF file via `pikepdf` failed.
    :raises TypeCheckError: If any argument or return value has an invalid type.
    """

    try:
        Pdf.open(file_path)

        path_dictionary.add_path(
            file_path = file_path,
            file_state = FileState.NOT_LOCKED
        )
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

        path_dictionary.add_path(
            file_path = file_path,
            file_state = FileState.UNLOCKED if did_unlock else FileState.LOCKED
        )
    except Exception as exception:
        raise PdfError(
            ErrorMessage.FAILED_OVERWRITE(file_path)
        ) from exception

@typechecked
def unlock_pdf() -> None:
    """
    Unlock password-protected PDF files for every inputted

    - directory path where some PDF files are, and/or
    - file path of a PDF file

    using inputted passwords to attempt unlocking each PDF file with.

    :raises FileNotFoundError: If every path does not ultimately point to a PDF file.
    :raises PdfError: If unlocking a PDF file via `_unlock_pdf` failed.
    :raises TypeCheckError: If any argument or return value has an invalid type.
    :raises ValueError: If no password was given.
    """

    # <NOTE>
    # Enforce input order via order of variable declaration.
    pdf_file_paths = _get_pdf_file_paths()
    passwords = _get_passwords()
    path_dictionary = PathDictionary()

    for pdf_file_path in pdf_file_paths:
        _unlock_pdf_file(
            file_path = pdf_file_path,
            passwords = passwords,
            path_dictionary = path_dictionary
        )

    _log_unlock_attempt(path_dictionary)
