"""Module for removing password protection from secured PDF files."""

import glob
import sys

import pikepdf

PDF_SEARCH_PATTERN = "/**/*.pdf"

def remove_password_protection(filepath: str, password: str) -> None:
    """Overwrite the password-protected file in given file path as its unprotected version."""

    pikepdf \
        .open(
            filepath,
            allow_overwriting_input=True,
            password=password,
        ) \
        .save(filepath)

def batch_remove_password_protection(directory: str, password: str) -> None:
    """Remove password protection from all PDF files in the specified directory."""

    for filepath in glob.iglob(directory + PDF_SEARCH_PATTERN, recursive=True):
        remove_password_protection(filepath, password)

batch_remove_password_protection(sys.argv[1], sys.argv[2])
