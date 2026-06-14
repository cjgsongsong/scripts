"""Tests for entry point."""

from runpy import run_module

from pytest import mark, raises

from unlock_pdf.enumerations import Module

@mark.parametrize(
    "test_module",
    [Module.DIRECT_EXECUTION, "importing_module"]
)
def test_entry_point_raises_exception(test_module: str):
    """
    Assert that the entry point
    calls `unlock_pdf` only when the execution is valid,
    specifically by asserting that it
    raises an appropriate exception.

    Note that this test expects that a valid call to `unlock_pdf` will raise an exception as
    
    - inputs are expected, and
    - no mock function of `builtins.input` is provided.

    :param test_module: Name of executed module.
    """

    with raises(
        expected_exception = (
            OSError
            if test_module == Module.DIRECT_EXECUTION else
            RuntimeError
        ),
        match = (
            None
            if test_module == Module.DIRECT_EXECUTION else
            "`unlock_pdf` must only be executed if directly imported from " + \
            "`unlock_pdf.functions` and not from here."
        )
    ):
        run_module(
            mod_name = "unlock_pdf",
            run_name = test_module
        )
