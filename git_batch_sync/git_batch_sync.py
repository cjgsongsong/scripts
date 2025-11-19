"""Module for synchronizing local repository states with their remote counterparts."""

from git import Repo

GIT_FETCH_COMMAND = 'git fetch origin'
REPOSITORY_INPUT_PROMPT = (
    'Enter the paths of local repositories to sync.\n'
    'Quit entering paths by entering an empty string.\n'
    '>\n'
)
REPOSITORY_INPUT_END_MARKER = ''

def _git_sync(repository: str) -> None:
    """Synchronize a local repository state with its remote counterpart."""
    repo = Repo(repository)
    print(repo)
    print(repository)

def git_batch_sync() -> None:
    """Synchronize local repository states with their remote counterparts."""

    print(REPOSITORY_INPUT_PROMPT, end='')

    repository_input = str(input())
    repositories: list[str] = []

    while repository_input != REPOSITORY_INPUT_END_MARKER:
        repositories.append(repository_input)

        repository_input = str(input())

    for repository in repositories:
        _git_sync(repository)

git_batch_sync()
