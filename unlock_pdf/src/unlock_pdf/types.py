"""`unlock-pdf` types."""

from typing import Literal
from unlock_pdf.enumerations import FileState, InputPrompt

type InputMainPrompt = Literal[InputPrompt.PASSWORDS, InputPrompt.PATHS]
"""Prompt detailing what inputs are being asked of the user."""
type Passwords = set[str]
"""Set of passwords."""
type Paths = set[str]
"""Set of paths."""

type GroupedPaths = dict[FileState, Paths]
"""Dictionary that maps file states with file paths of PDF files."""
type Inputs = Passwords | Paths
"""Set of either passwords or paths."""
