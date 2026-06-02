"""`unlock-pdf` types."""

from typing import Literal
from unlock_pdf.enumerations import FileState, InputPrompt

type MainInputPrompt = Literal[InputPrompt.PASSWORDS, InputPrompt.PATHS]
"""Prompt detailing what inputs are being asked of the user."""
type Passwords = list[str]
"""Ordered list of unique passwords."""
type Paths = list[str]
"""Ordered list of unique paths."""

type GroupedPaths = dict[FileState, Paths]
"""Dictionary that maps file states with file paths of PDF files."""
type Inputs = Passwords | Paths
"""Ordered list of either unique passwords or unique paths."""
