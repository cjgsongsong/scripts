"""Module for removing password protection from secured PDF files."""

import glob
import sys

import pikepdf

PDF_SEARCH_PATTERN = '/**/*.pdf'

def remove_password_protection(filepath: str, passwords: list[str]) -> None:
    """Overwrite a file as its unprotected version if it is password-protected."""

    try:
        pikepdf.open(filepath)

        print(f'No password protection exists for `{filepath}`.')
    except pikepdf.PasswordError as has_password_exception:
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
            raise ValueError(f'Given password(s) cannot open `{filepath}`.') \
                from has_password_exception

        print(f'Password protection is now removed for `{filepath}`.')

def batch_remove_password_protection(directory: str, passwords: list[str]) -> None:
    """Remove password protection from all PDF files in the specified directory."""

    for filepath in glob.iglob(directory + PDF_SEARCH_PATTERN, recursive=True):
        remove_password_protection(filepath, passwords)

batch_remove_password_protection(sys.argv[1], [sys.argv[2]])
