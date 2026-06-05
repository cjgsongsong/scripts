"""Tests for `_get_passwords`."""

# pyright: reportPrivateUsage=false

from pytest import (
    MonkeyPatch,
    mark,
    raises
)
from typing import Callable
from unlock_pdf.functions import _get_passwords
from unlock_pdf.types import Passwords

# <NOTE>
# As the source code prefers named imports over default imports,
# those named imports must be mocked by having the target be where they are named
# instead of where they actually came from.
#
# See https://pytest.org/en/7.4.x/reference/reference.html#pytest.MonkeyPatch.setattr.
import unlock_pdf.functions as target

def _generate_mock_get_unique_inputs(mock_passwords: Passwords) -> Callable[[str], Passwords]:
    """
    Generate `_mock_get_unique_inputs`
    based on given mock passwords.

    :param mock_passwords: Mock ordered list of unique passwords
                           to attempt unlocking each PDF file with. 
    :returns: Mock function of `unlock-pdf.functions._get_unique_inputs`.
    """

    def _mock_get_unique_inputs(prompt: str) -> Passwords:
        """
        Mock function of `unlock-pdf.functions._get_unique_inputs` that
        returns mock passwords to attempt unlocking each PDF file with.
        
        :param prompt: Prompt detailing what inputs are being asked of the user.
        :returns Mock ordered list of unique passwords to attempt unlocking each PDF file with.
        """

        assert prompt == "Enter every password to attempt unlocking each PDF file with."

        return mock_passwords

    return _mock_get_unique_inputs

def test_get_passwords_raises_exception(monkeypatch: MonkeyPatch) -> None:
    """
    Assert that `_get_passwords`
    raises an appropriate exception
    when given no password.
    
    :param monkeypatch: `pytest` fixture for mocking functions.
    """

    monkeypatch.setattr(
        name = "_get_unique_inputs",
        target = target,
        value = _generate_mock_get_unique_inputs([])
    )

    with raises(
        expected_exception = ValueError,
        match = "At least one password must be given."
    ):
        _get_passwords()

@mark.parametrize(
    "test_passwords",
    [
        ["password"],
        ["password-0", "password-1"]
    ]
)
def test_get_passwords_returns_passwords(
    monkeypatch: MonkeyPatch,
    test_passwords: Passwords
) -> None:
    """
    Assert that `_get_passwords`
    returns an ordered list of unique passwords to attempt unlocking each PDF file with
    from inputted passwords.

    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_passwords: Mock ordered list of unique passwords
                           to attempt unlocking each PDF file with.
    """

    monkeypatch.setattr(
        name = "_get_unique_inputs",
        target = target,
        value = _generate_mock_get_unique_inputs(test_passwords)
    )

    assert _get_passwords() == test_passwords
