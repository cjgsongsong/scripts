"""Path dictionary class."""

from collections import UserDict

from typeguard import typechecked

from unlock_pdf.enumerations import FileState
from unlock_pdf.types import InitialPathDictionary, Paths

class PathDictionary(UserDict[FileState, Paths]):
    """Dictionary that maps file states with PDF file paths."""

    @typechecked
    def __init__(
        self,
        initial_path_dictionary: InitialPathDictionary = None
    ) -> None:
        """
        Initialize a path dictionary either

        - with an initial dictionary that maps file states with PDF file paths, or
        - with
          - every file state as key, and
          - an empty list of PDF file paths as each key's corresponding value.

        :param initial_path_dictionary: Initial dictionary
                                        that maps file states with PDF file paths.
        """

        super() \
            .__init__(
                initial_path_dictionary
                if initial_path_dictionary else
                {
                    file_state: []
                    for file_state in FileState
                }
            )

    @typechecked
    def add_path(
        self,
        file_path: str,
        file_state: FileState
    ) -> None:
        """
        Add the file path
        to the list of PDF file paths that resulted to the file state
        only if said file path is not in the said list yet.

        :param file_path: File path of a PDF file.
        :param file_state: State that a PDF file may be after an unlock attempt.
        """

        if file_path not in self[file_state]:
            self \
                [file_state] \
                .append(file_path)
