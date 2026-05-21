"""
Script for unlocking a password-protected PDF file.
"""

from os.path import isfile
from pikepdf import PasswordError, Pdf

FILE_PATH_INPUT_PROMPT = (
    "Enter the path of the PDF file.\n"
    ">\n"
)
PASSWORD_INPUT_PROMPT = (
    "\n"
    "Enter next the password to attempt opening the PDF file with.\n"
    ">\n"
)
PDF_FILE_EXTENSION = ".pdf"
QUOTATION_MARK = '"'

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
        password: str
    ) -> None:
    """
    Overwrite the PDF file as its unprotected version.

    :param file_path: Path of the PDF file.
    :param password: Password to attempt opening the PDF file with.
    :raises FileNotFoundError: If the file path does not point to a valid PDF file.
    :raises `pikepdf` Error: If the corresponding file cannot be opened or overwritten.
    :raises ValueError: If the password is an empty string.
    """

    if password == "":
        raise ValueError("Password cannot be empty.")

    sanitized_file_path = _sanitize_file_path(file_path)

    if not _is_valid_pdf(sanitized_file_path):
        raise FileNotFoundError(f"`{sanitized_file_path}` is not a valid PDF file.")

    try:
        Pdf.open(sanitized_file_path)
    except PasswordError:
        Pdf \
            .open(
                allow_overwriting_input = True,
                filename_or_stream = sanitized_file_path,
                password = password,
            ) \
            .save(sanitized_file_path)

unlock_pdf(
    file_path = input(FILE_PATH_INPUT_PROMPT),
    password = input(PASSWORD_INPUT_PROMPT),
)
