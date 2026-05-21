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

    Pdf \
        .open(
            allow_overwriting_input = True,
            filename_or_stream = file_path,
            password = password,
        ) \
        .save(file_path)

unlock_pdf(
    file_path = input(FILE_PATH_INPUT_PROMPT),
    password = input(PASSWORD_INPUT_PROMPT),
)
