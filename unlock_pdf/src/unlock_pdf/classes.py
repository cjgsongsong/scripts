"""`unlock-pdf` classes."""

from enum import Enum
from typing import override

class MessageEnum(Enum):
    """`Enum` wrapper to emulate `StrEnum` behavior for its members with string values."""
    @override
    def __str__(self) -> str:
        """
        Override `Enum`'s default `__str__` behavior to return the member's value
        when accessing said member if said value is a string.
        """
        return (
            self.value
            if isinstance(self.value, str)
            else super().__str__()
        )
