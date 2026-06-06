"""Tests for `unlock-pdf` entry point."""

from pytest import mark, raises
from runpy import run_module
from unlock_pdf.enumerations import Module

@mark.parametrize(
    "test_executed_module," \
    "test_exception_type, test_exception_message",
    [
        (
            Module.DIRECT_EXECUTION,
            OSError, None
        ),
        (
            Module.PACKAGE_EXECUTION,
            OSError, None
        ),
        (
            "importing_module",
            RuntimeError,
            "`unlock_pdf` must only be executed if directly imported from " + \
            "`unlock_pdf.functions` and not from here."
        )
    ]
)
def test_entry_point_raises_exception(
    test_exception_message: str | None,
    test_exception_type: type[Exception],
    test_executed_module: str
):
    """
    Assert that the entry point
    calls `unlock_pdf` only when the execution is valid,
    specifically by asserting that it
    raises an appropriate exception.

    Note that this test expects that a valid call to `unlock_pdf` will raise an exception as
    
    - inputs are expected, and
    - no mock function of `builtins.input` is provided.

    :param test_exception_message: Message of exception raised, if relevant to be tested.
                                   Otherwise, `None`.
    :param test_exception_type: Type of exception raised.
    :param test_executed_module: Name of executed module.
    """

    with raises(
        expected_exception = test_exception_type,
        match = test_exception_message
    ):
        run_module(
            mod_name = "unlock_pdf",
            run_name = test_executed_module
        )
