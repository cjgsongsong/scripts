"""`unlock-pdf` entry point."""

from unlock_pdf.enumerations import Python
from unlock_pdf.functions import unlock_pdf

if __name__ == Python.DIRECT_EXECUTION_TOP_LEVEL_CODE:
    unlock_pdf()
