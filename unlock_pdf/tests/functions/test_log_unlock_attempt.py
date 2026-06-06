"""Tests for `_log_unlock_attempt`."""

# pyright: reportPrivateUsage=false

from pytest import CaptureFixture
from unlock_pdf.enumerations import FileState
from unlock_pdf.functions import _log_unlock_attempt
from unlock_pdf.types import GroupedPaths

def test_log_unlock_attempt_prints_per_file_state(capsys: CaptureFixture[str]) -> None:
    """
    Assert that `_log_unlock_attempt`
    prints per file state

    - how many PDF files are in such file state, and
    - what are the file paths of those PDF files

    when given valid grouped PDF file paths.

    :param capsys: `pytest` fixture for capturing outputs.
    """

    grouped_pdf_file_paths: GroupedPaths = {
        key: []
        for key in [
            file_state for file_state in FileState
        ]
    }
    grouped_pdf_file_paths[FileState.NOT_LOCKED] = ["test-0.pdf"]
    grouped_pdf_file_paths[FileState.UNLOCKED] = ["test-1.pdf", "test-2.pdf"]

    _log_unlock_attempt(grouped_pdf_file_paths)

    assert (
        capsys \
            .readouterr() \
            .out
    )== (
        "0 PDF files are still locked:" + "\n"
        + "-" + "\n"
        + "\n"
        + "1 PDF file is not locked:" + "\n"
        + "test-0.pdf" + "\n"
        + "\n"
        + "2 PDF files are unlocked:" + "\n"
        + "test-1.pdf" + "\n"
        + "test-2.pdf" + "\n"
        + "\n"
    )
