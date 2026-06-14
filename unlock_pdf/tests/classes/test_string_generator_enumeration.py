"""Tests for string generator enumeration class."""

from unlock_pdf.classes.string_generator_enumeration import StrGenEnum

def test_string_generator_enumeration_stringifies() -> None:
    """
    Assert that a string generator enumeration
    stringifies its member
    based on whether said member's value is a string or not.
    """

    class _TestStrGenEnum(StrGenEnum):
        """Test message enumeration."""

        NON_STRING = 0
        STRING = "test-value"

    assert str(_TestStrGenEnum.NON_STRING) == "_TestStrGenEnum.NON_STRING"
    assert str(_TestStrGenEnum.STRING) == "test-value"
