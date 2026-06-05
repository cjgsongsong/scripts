"""`unlock-pdf` test utility functions."""

from typing import Callable
from unlock_pdf.types import Inputs

def generate_mock_get_unique_inputs(
    mock_inputs: Inputs,
    test_prompt: str
) -> Callable[[str], Inputs]:
    """
    Generate `_mock_get_unique_inputs`
    based on given mock inputs.

    :param mock_inputs: Mock ordered list of unique inputs.
    :param test_prompt: Prompt detailing what inputs are being asked of the user.
    :returns: Mock function of `unlock-pdf.functions._get_unique_inputs`.
    """

    def _mock_get_unique_inputs(prompt: str) -> Inputs:
        """
        Mock function of `unlock-pdf.functions._get_unique_inputs` that
        returns mock unique inputs.
        
        :param prompt: Prompt detailing what inputs are being asked of the user.
        :returns: Mock ordered list of unique inputs.
        """

        assert prompt == test_prompt

        return mock_inputs

    return _mock_get_unique_inputs
