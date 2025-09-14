"""Module for removing password protection from secured PDF files."""

import glob
import os
import sys

import pikepdf

PDF_SEARCH_PATTERN = '/**/*.pdf'

def _get_pdf_file_paths(file_path_input: str) -> list[str]:
    """Get PDF file paths from input string.
    
    Return a PDF file path pattern if input is a valid directory.
    Return the file path input if it is a valid PDF file.
    Return an empty string otherwise.
    """

    if file_path_input.endswith('.pdf') and os.path.isfile(file_path_input):
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

def remove_password_protection(file_path: str, passwords: list[str]) -> None:
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

def batch_remove_password_protection(file_path_input: str, passwords: list[str]) -> None:
    """Remove password protection from all PDF files in the specified directory."""

    for file_path in _get_pdf_file_paths(file_path_input):
        remove_password_protection(file_path, passwords)

batch_remove_password_protection(sys.argv[1], [sys.argv[2]])
