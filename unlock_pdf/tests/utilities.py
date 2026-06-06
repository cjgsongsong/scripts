"""`unlock-pdf` test utility functions."""

from typing import Callable
from unlock_pdf.types import Inputs

def generate_mock_boolean(test_boolean: bool, test_path: str) -> Callable[[str], bool]:
    """
    Generate either
    
    - `_mock_isdir`,
    - `_mock_isfile`, or
    - `_mock_is_pdf_file`
    
    given
    
    - test boolean, and
    - test path.
    
    :param test_boolean: Mock boolean that tells whether the path satisfies a condition or not.
    :param test_path: Path.
    :returns: Mock function of either `os.path.isdir`, `os.path.isfile`, or
              `unlock-pdf.functions._is_pdf_file`.
    """

    def _mock_boolean(pathname: str) -> bool:
        """
        Mock function of either
        
        - `os.path.isdir`,
        - `os.path.isfile`, or
        - `unlock-pdf.functions._is_pdf_file`
        
        that
        returns a mock boolean that tells whether the path satisfies a condition or not.

        :param pathname: Path.
        :returns: Mock boolean that tells whether the path satisfies a condition or not.
        """

        assert pathname == test_path

        return test_boolean

    return _mock_boolean

def generate_mock_get_unique_inputs(
    test_inputs: Inputs,
    test_prompt: str
) -> Callable[[str], Inputs]:
    """
    Generate `_mock_get_unique_inputs`
    based on given mock inputs.

    :param test_inputs: Mock ordered list of unique inputs.
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

        return test_inputs

    return _mock_get_unique_inputs
