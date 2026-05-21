"""
Script for unlocking a password-protected PDF file.
"""

from pikepdf import Pdf

FILE_PATH_INPUT_PROMPT = (
    "Enter the path of the PDF file.\n"
    ">\n"
)
PASSWORD_INPUT_PROMPT = (
    "\n"
    "Enter next the password to attempt opening the PDF file with.\n"
    ">\n"
)
QUOTATION_MARK = '"'

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
    :raises `pikepdf` Error: If the corresponding file cannot be opened or overwritten.
    """

    sanitized_file_path = _sanitize_file_path(file_path)

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
