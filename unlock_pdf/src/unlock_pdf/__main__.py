"""`unlock-pdf` entry point."""

from unlock_pdf.enumerations import ErrorMessage, Module
from unlock_pdf.functions import unlock_pdf

if __name__ == Module.DIRECT_EXECUTION:
    unlock_pdf()
else:
    raise RuntimeError(
        ErrorMessage.NO_INVALID_EXECUTION
    )
