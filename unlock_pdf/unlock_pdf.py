"""
Script for unlocking a password-protected PDF file.
"""

from os.path import isfile
from pikepdf import (
    PasswordError,
    Pdf,
    PdfError,
)

FILE_PATH_INPUT_PROMPT = (
    "Enter the path of the PDF file.\n"
    ">\n"
)
PASSWORD_INPUT_PROMPT = (
    "\n"
    "Enter next every password to attempt opening the PDF file with.\n"
    "Enter an empty string to quit.\n"
    ">"
)
PDF_FILE_EXTENSION = ".pdf"
QUOTATION_MARK = '"'

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

def _sanitize_file_path(file_path: str) -> str:
    """
    Remove quotation marks from the pasted file path.

    :param file_path: Path of the PDF file.
    :returns: Sanitized path of the PDF file.
    """

    return file_path \
        .removeprefix(QUOTATION_MARK) \
        .removesuffix(QUOTATION_MARK)

def unlock_pdf(
        file_path: str,
        passwords: list[str]
    ) -> None:
    """
    Overwrite the PDF file as its unprotected version.

    :param file_path: Path of the PDF file.
    :param passwords: Passwords to attempt opening the PDF file with.
    :raises FileNotFoundError: If the file path does not point to a valid PDF file.
    :raises PdfError: If the corresponding PDF file cannot be overwritten.
    :raises ValueError: If no password was given.
    """

    if not passwords:
        raise ValueError("At least one password must be given.")

    sanitized_file_path = _sanitize_file_path(file_path)

    if not _is_valid_pdf(sanitized_file_path):
        raise FileNotFoundError(f"`{sanitized_file_path}` is not a valid PDF file.")

    try:
        Pdf.open(sanitized_file_path)

        print(f"`{sanitized_file_path}` is unlocked.")
    except PasswordError:
        did_unlock = False

        for password in passwords:
            try:
                Pdf \
                    .open(
                        allow_overwriting_input = True,
                        filename_or_stream = sanitized_file_path,
                        password = password,
                    ) \
                    .save(sanitized_file_path)

                did_unlock = True

                break
            except PasswordError:
                continue
            except Exception as exception:
                raise PdfError(f"Overwriting `{sanitized_file_path}` failed.") from exception

        if did_unlock:
            print(f"`{sanitized_file_path}` is now unlocked.")
        else:
            print(f"`{sanitized_file_path}` is still locked.")

unlock_pdf(
    file_path = input(FILE_PATH_INPUT_PROMPT),
    passwords = _get_passwords()
)
