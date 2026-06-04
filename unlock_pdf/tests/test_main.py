"""Tests for `unlock.pdf` entry point."""

from runpy import run_module
from pytest import mark, raises
from unlock_pdf.enumerations import Module

@mark.parametrize(
    "executed_module," \
    "exception_type, exception_message",
    [
        (
            Module.DIRECT_EXECUTION,
            OSError,
            None
        ),
        (
            Module.PACKAGE_EXECUTION,
            OSError,
            None
        ),
        (
            "importing_module",
            RuntimeError,
            "`unlock_pdf` must only be executed if directly imported from " + \
            "`unlock_pdf.functions` and not from here."
        )
    ]
)
def test_entry_point_errs_on_module_execution(
    exception_message: str | None,
    exception_type: type[Exception],
    executed_module: str
):
    """
    Assert that the `unlock.pdf` entry point
    calls `unlock_pdf` only on a direct execution
    as seen as when it
    raises an appropriate exception.

    Note that calling `unlock_pdf` in this test will raise an exception as
    
    - inputs are expected, and
    - no mock function of `builtins.input` is provided.

    :param exception_message: Message of exception raised, if relevant to be tested.
    :param exception_type: Type of exception raised.
    :param executed_module: Name of executed module.
    """

    with raises(
        expected_exception = exception_type,
        match = exception_message
    ):
        run_module(
            mod_name = "unlock_pdf",
            run_name = executed_module
        )
