"""Module for removing password protection from secured PDF files."""

import sys
import pikepdf

def remove_password(filepath: str, password: str) -> None:
    """Overwrite the password-protected file in specified path as its unprotected version."""

    pikepdf \
        .open(
            filepath,
            allow_overwriting_input=True,
            password=password,
        ) \
        .save(filepath)

remove_password(sys.argv[1], sys.argv[2])
