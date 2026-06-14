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

        @staticmethod
        def _test_generate_string() -> str:
            """Generate a test generated string."""

            return "test-generated-string"

        NON_STRING = 0
        STRING = "test-string"
        STRING_GENERATOR = _test_generate_string

    assert str(_TestStrGenEnum.NON_STRING) == "_TestStrGenEnum.NON_STRING"
    assert str(_TestStrGenEnum.STRING) == "test-string"
    assert str(_TestStrGenEnum.STRING_GENERATOR()) == "test-generated-string"
