"""
Script for unlocking password-protected PDF files.
"""

from glob import glob
from os.path import isdir, isfile
from pikepdf import (
    PasswordError,
    Pdf,
    PdfError,
)

PASSWORD_INPUT_PROMPT = (
    "\n"
    "Enter every password to attempt opening the PDF file(s) with.\n"
    "Enter an empty string to quit.\n"
    ">"
)
PATH_INPUT_PROMPT = (
    "Enter the directory or file path of the PDF file(s).\n"
    ">\n"
)
PDF_FILE_EXTENSION = ".pdf"
PDF_FILE_SEARCH_PATTERN = f"/**/*{PDF_FILE_EXTENSION}"
QUOTATION_MARK = '"'

def _get_pdf_paths(path: str) -> list[str]:
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
    elif _is_valid_pdf(path):
        return [path]

    return []

def _get_passwords() -> list[str]:
    """
    Get password inputs until an empty string is given.

    :returns: List of password inputs.
    """

    print(PASSWORD_INPUT_PROMPT)

    password = input()
    passwords: list[str] = []

    while password != "":
        passwords.append(password)

        password = input()

    return passwords

def _is_valid_pdf(file_path: str) -> bool:
    """
    Validate if the file path
    - has the PDF file extension, and
    - points to a valid file.

    :param file_path: Path of the PDF file.
    :returns: Whether the file path points to a valid PDF file or not.
    """

    return (
        file_path.endswith(PDF_FILE_EXTENSION)
        and isfile(file_path)
    )

def _sanitize_path(path: str) -> str:
    """
    Remove quotation marks from the pasted path.

    :param path: Path of either the directory containing the PDF file(s) or the PDF file..
    :returns: Sanitized path of either the directory containing the PDF files or the PDF file.
    """

    return path \
        .removeprefix(QUOTATION_MARK) \
        .removesuffix(QUOTATION_MARK)

def _unlock_pdf(
        passwords: list[str],
        path: str
    ) -> None:
    """
    Overwrite the PDF file as its unlocked version.

    :param passwords: Passwords to attempt opening the PDF file with.
    :param path: Sanitized path of the PDF file.
    :raises PdfError: If unlocking the PDF file via `pikepdf` failed.
    """

    try:
        Pdf.open(path)

        print(f"`{path}` is not locked.")
    except PasswordError:
        did_unlock = False

        for password in passwords:
            try:
                Pdf \
                    .open(
                        allow_overwriting_input = True,
                        filename_or_stream = path,
                        password = password,
                    ) \
                    .save(path)

                did_unlock = True

                break
            except PasswordError:
                continue
            except Exception as exception:
                raise PdfError(f"Unlocking `{path}` failed.") from exception

        if did_unlock:
            print(f"`{path}` is now unlocked.")
        else:
            print(f"`{path}` is still locked.")

def unlock_pdf(
        passwords: list[str],
        path: str
    ) -> None:
    """
    Unlock password-protected PDF files in the specified path.

    :param passwords: Passwords to attempt opening the PDF files with.
    :param path: Path of either the directory containing the PDF file(s) or the PDF file.
    :raises FileNotFoundError: If the path and its subpaths do not point to any valid PDF file.
    :raises PdfError: If unlocking a PDF file via `_unlock_pdf` failed.
    :raises ValueError: If no password was given.
    """

    if not passwords:
        raise ValueError("At least one password must be given.")

    pdf_file_paths = _get_pdf_paths(
        _sanitize_path(path)
    )

    if not pdf_file_paths:
        raise FileNotFoundError("At least one path must point to a valid PDF file.")

    for pdf_file_path in pdf_file_paths:
        _unlock_pdf(
            passwords = passwords,
            path = pdf_file_path
        )

unlock_pdf(
    passwords = _get_passwords(),
    path = input(PATH_INPUT_PROMPT)
)
