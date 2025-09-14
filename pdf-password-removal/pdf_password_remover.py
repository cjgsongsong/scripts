"""Module for removing password protection from secured PDF files."""

import glob
import os

import pikepdf

COPY_PASTE_AFFIX = '"'
FILE_PATH_INPUT_PROMPT = (
    'Enter the directory or file path of the PDF files.\n'
    '>\n'
)
PASSWORD_INPUT_PROMPT = (
    '\n'
    'Enter next the passwords to attempt opening any PDF file with.\n'
    'Quit entering passwords by entering an empty string.\n'
    '>\n'
)
PASSWORD_INPUT_END_MARKER = ''
PDF_FILE_TYPE_EXTENSION = '.pdf'
PDF_SEARCH_PATTERN = f'/**/*{PDF_FILE_TYPE_EXTENSION}'

def _remove_password_protection_per_file(file_path: str, passwords: list[str]) -> None:
    """Overwrite a PDF file as its unprotected version if it is password-protected."""

    try:
        pikepdf.open(file_path)

        print(f'No password protection exists for `{file_path}`.')
    except pikepdf.PasswordError as has_password_exception:
        did_overwrite = False

        for password in passwords:
            try:
                pikepdf \
                    .open(
                        file_path,
                        allow_overwriting_input=True,
                        password=password,
                    ) \
                    .save(file_path)

                did_overwrite = True

                break
            except pikepdf.PasswordError:
                continue

        if not did_overwrite:
            raise ValueError(f'Given password(s) cannot open `{file_path}`.') \
                from has_password_exception

        print(f'Password protection is now removed for `{file_path}`.')

def _get_pdf_file_paths(file_path_input: str) -> list[str]:
    """Get PDF file paths from input string.
    
    Return a PDF file path pattern if input is a valid directory.
    Return the file path input if it is a valid PDF file.
    Return an empty string otherwise.
    """

    if (
        file_path_input.endswith(PDF_FILE_TYPE_EXTENSION)
        and os.path.isfile(file_path_input)
    ):
        return [file_path_input]

    file_paths = []

    if os.path.isdir(file_path_input):
        file_paths = glob.glob(
            file_path_input + PDF_SEARCH_PATTERN,
            recursive=True,
        )

        if file_paths:
            return file_paths

    raise ValueError('Given file path has no valid PDF files.')

def remove_password_protection() -> None:
    """Remove password protection from all PDF files in file path input using password inputs."""

    file_paths = _get_pdf_file_paths(
        str(
            input(FILE_PATH_INPUT_PROMPT)
                .removeprefix(COPY_PASTE_AFFIX)
                .removesuffix(COPY_PASTE_AFFIX)
        )
    )

    print(PASSWORD_INPUT_PROMPT, end='')

    password_input = str(input())
    passwords: list[str] = []

    while password_input != PASSWORD_INPUT_END_MARKER:
        passwords.append(password_input)

        password_input = str(input())

    for file_path in file_paths:
        _remove_password_protection_per_file(file_path, passwords)

remove_password_protection()
