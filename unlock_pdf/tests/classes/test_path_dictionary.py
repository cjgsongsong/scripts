"""Tests for path dictionary class."""

from pytest import mark
from unlock_pdf.classes.path_dictionary import PathDictionary
from unlock_pdf.enumerations import FileState
from unlock_pdf.types import InitialPathDictionary, Paths

@mark.parametrize(
    "test_initial_path_dictionary, test_initial_pdf_file_paths",
    [
        (
            {
                file_state: ["test.pdf"]
                for file_state in FileState
            },
            ["test.pdf"]
        ),
        (None, [])
    ]
)
def test_path_dictionary_initializes(
    test_initial_path_dictionary: InitialPathDictionary,
    test_initial_pdf_file_paths: Paths
) -> None:
    """
    Assert that a path dictionary
    initializes
    
    - its keys as file states, and 
    - its values as either
      - an empty list of PDF file paths, or
      - an initial list of PDF file paths.

    :param test_initial_path_dictionary: Initial dictionary
                                         that maps file states with PDF file paths.
    :param test_initial_pdf_file_paths: Initial list of PDF file paths of every file state.
    """

    test_path_dictionary = PathDictionary(test_initial_path_dictionary)

    for file_state in FileState:
        assert file_state in test_path_dictionary.keys()
        assert test_path_dictionary[file_state] == test_initial_pdf_file_paths

@mark.parametrize("test_file_state", FileState)
def test_path_dictionary_groups_file_path_by_file_state(test_file_state: FileState) -> None:
    """
    Assert that adding a file path to a path dictionary
    adds accordingly said file path
    to the list of PDF file paths
    that resulted to the given file state.
    
    :param test_file_state: Mock state that a PDF file may be after an unlock attempt.
    """

    test_path_dictionary = PathDictionary()

    test_path_dictionary.add_path(
        file_path = "test.pdf",
        file_state = test_file_state
    )

    for file_state in FileState:
        assert test_path_dictionary[file_state] == (
            ["test.pdf"]
            if file_state == test_file_state else
            []
        )
