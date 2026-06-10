"""Path dictionary class."""

from collections import UserDict
from typeguard import typechecked
from unlock_pdf.enumerations import FileState
from unlock_pdf.types import Paths

class PathDictionary(UserDict[FileState, Paths]):
    """Dictionary that maps file states with file paths of PDF files."""

    @typechecked
    def __init__(self) -> None:
        """Initialize a path dictionary."""

        super().__init__({
            key: []
            for key in [
                file_state for file_state in FileState
            ]
        })

    @typechecked
    def add_path(
        self,
        file_path: str,
        file_state: FileState
    ) -> None:
        """
        Add the given file path
        to the list of PDF file paths
        that resulted to the given file state
        only if said file path has not been previously added to the said list yet.

        :param file_path: File path of a PDF file to unlock.
        :param file_state: State that a PDF file may be after an unlock attempt.
        """

        if file_path not in self[file_state]:
            self[file_state].append(file_path)
