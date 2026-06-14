"""String generator enumeration class."""

from enum import Enum
from typing import override

from typeguard import typechecked

class StrGenEnum(Enum):
    """`Enum` wrapper to emulate `StrEnum` behavior for its members with string values."""

    @override
    @typechecked
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
