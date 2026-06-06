"""Tests for `unlock-pdf` classes."""

from unlock_pdf.enumerations import MessageEnum

def test_message_enum_stringifies() -> None:
    """
    Assert that a message enumeration
    stringifies its member
    based on whether said member's value is a string or not.
    """

    class _TestMessageEnum(MessageEnum):
        """Mock message enumeration."""

        NON_STRING = 0
        STRING = "test-value"

    assert str(_TestMessageEnum.NON_STRING) == "_TestMessageEnum.NON_STRING"
    assert str(_TestMessageEnum.STRING) == "test-value"
