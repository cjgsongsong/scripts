"""Module for removing password protection from secured PDF files."""

import glob
import sys

import pikepdf

PDF_SEARCH_PATTERN = "/**/*.pdf"

def remove_password_protection(filepath: str, passwords: list[str]) -> None:
    """Overwrite the password-protected file in given file path as its unprotected version."""

    did_overwrite = False

    for password in passwords:
        try:
            pikepdf \
                .open(
                    filepath,
                    allow_overwriting_input=True,
                    password=password,
                ) \
                .save(filepath)

            did_overwrite = True

            break
        except pikepdf.PasswordError:
            continue

    if not did_overwrite:
        raise ValueError(f'Given password(s) cannot open `{filepath}`.')

def batch_remove_password_protection(directory: str, passwords: list[str]) -> None:
    """Remove password protection from all PDF files in the specified directory."""

    for filepath in glob.iglob(directory + PDF_SEARCH_PATTERN, recursive=True):
        remove_password_protection(filepath, passwords)

batch_remove_password_protection(sys.argv[1], [sys.argv[2]])
