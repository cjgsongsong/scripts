"""Tests for `_get_unique_inputs`."""

# pyright: reportPrivateUsage=false

from pytest import (
    CaptureFixture,
    MonkeyPatch,
    mark,
)
from unlock_pdf.enumerations import InputPrompt
from unlock_pdf.functions import _get_unique_inputs
from unlock_pdf.types import Inputs, MainInputPrompt

import builtins as target

@mark.parametrize(
    "test_prompt," \
    "test_printed_prompt",
    [
        (
            InputPrompt.PASSWORDS,
            "Enter every password to attempt unlocking each PDF file with."
        ),
        (
            InputPrompt.PATHS,
            "Enter every directory path and/or file path of the PDF files to unlock."
        )
    ]
)
def test_get_unique_inputs_prints_prompts(
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
    test_printed_prompt: MainInputPrompt,
    test_prompt: MainInputPrompt
) -> None:
    """
    Assert that `_get_unique_inputs`
    prints prompts

    - in correct order, and
    - including the given main input prompt

    when given a valid prompt.

    :param capsys: `pytest` fixture for capturing outputs.
    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_printed_prompt: Printed main input prompt.
    :param test_prompt: Mock prompt detailing what inputs are being asked of the user.
    """

    monkeypatch.setattr(
        name = "input",
        target = target,
        value = lambda: ""
    )

    _get_unique_inputs(test_prompt)

    assert (
        capsys \
            .readouterr() \
            .out
    ) == (
        test_printed_prompt + "\n"
        + "Enter an empty string to quit." + "\n"
        + ">" + "\n"
    )

@mark.parametrize(
    "test_user_inputs," \
    "test_unique_inputs",
    [
        (
            [""],
            [],
        ),
        (
            ["password", ""],
            ["password"]
        ),
        (
            [
                "password",
                "password",
                ""
            ],
            ["password"]
        ),
        (
            [
                "password",
                "another_password",
                ""
            ],
            ["password", "another_password"]
        )
    ]
)
def test_get_unique_inputs_returns_unique_inputs(
    monkeypatch: MonkeyPatch,
    test_unique_inputs: Inputs,
    test_user_inputs: list[str]
) -> None:
    """
    Assert that `_get_unique_inputs`
    returns all unique user inputs as an ordered list
    when given a valid prompt and valid user inputs.

    :param monkeypatch: `pytest` fixture for mocking functions.
    :param test_unique_inputs: Ordered list of unique inputs.
    :param test_user_inputs: Mock user inputs.
    """

    call_count = -1

    def _mock_input() -> str:
        """
        Mock function of `builtins.input` that
        returns a mock user input
        based on how many times the mock function has been called.

        :returns: Mock user input.
        """

        nonlocal call_count

        call_count += 1

        return test_user_inputs[call_count]

    monkeypatch.setattr(
        name = "input",
        target = target,
        value = _mock_input
    )

    assert _get_unique_inputs(InputPrompt.PASSWORDS) == test_unique_inputs
