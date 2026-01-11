"""Module for synchronizing local repository states with their remote counterparts."""

from datetime import datetime
from git import Repo

CURRENT_DATETIME_FORMAT = '%Y-%m-%d-%H-%M-%S'
GIT_FILE_TYPE_EXTENSION = '.git'
GIT_REMOTE_SHOW_ORIGIN_COMMAND = 'git remote show origin'
GIT_REMOTE_SHOW_ORIGIN_MARKER = 'HEAD branch:'
REPOSITORY_INPUT_END_MARKER = ''
REPOSITORY_INPUT_PROMPT = (
    'Enter the paths of local repositories to sync.\n'
    'Quit entering paths by entering an empty string.\n'
    '>\n'
)

def _get_remote_main_branch_name(repository: str) -> str:
    """Extract the remote repository's main branch's name from `git remote show origin`'s output.
    
    Return said branch's name.
    """

    return str(
        Repo(repository)
            .git
            .execute(GIT_REMOTE_SHOW_ORIGIN_COMMAND, stdout_as_string=True)
    ) \
        .split(GIT_REMOTE_SHOW_ORIGIN_MARKER) \
        [1] \
        .split('\n') \
        [0] \
        .strip()

def _git_checkout_remote_main(repository: str) -> None:
    """Switch a local repository to its remote counterpart's main branch.
    
    Essentially, this is
    - `git checkout -b <REMOTE_MAIN_BRANCH>-<CURRENT_DATETIME>` if already in said branch
    - `git branch -D <REMOTE_MAIN_BRANCH>`
    - `git checkout <REMOTE_MAIN_BRANCH>`
    ```
    """

    local_repository = Repo(repository)
    current_branch = local_repository.active_branch
    current_branch_name = current_branch.name
    remote_main_branch_name = _get_remote_main_branch_name(repository)

    try:
        local_head_branch = local_repository \
            .heads \
            [remote_main_branch_name]

        if current_branch == local_head_branch:
            current_datetime = datetime \
                .today() \
                .strftime(CURRENT_DATETIME_FORMAT)

            current_branch.checkout(b=f'{current_branch_name}-{current_datetime}')

            print(f'Local repository switched to a copy branch `{local_repository.active_branch}`.')

        local_repository \
            .delete_head(local_head_branch, force=True)

        print(f'Local repository deleted its main branch `{current_branch_name}`.')
    except IndexError:
        print(f'Local repository has no `{remote_main_branch_name}` branch.')
    finally:
        remote_main_branch = local_repository \
            .remote() \
            .refs \
            [remote_main_branch_name]

        local_repository \
            .create_head(remote_main_branch_name, remote_main_branch) \
            .set_tracking_branch(remote_main_branch) \
            .checkout()

        print(f'Local repository switched to the main branch `{local_repository.active_branch}`.')

def _git_fetch(repository: str) -> None:
    """Synchronize a local repository state with its remote counterpart.
    
    Essentially, this is `git fetch`.
    """
    remote_repository = Repo(repository).remote()

    changed_branches = remote_repository.fetch(verbose=False)
    remote_repository_url = remote_repository \
        .url \
        .rstrip(GIT_FILE_TYPE_EXTENSION)

    print(f'Changes from remote repository in {remote_repository_url} have been fetched.')
    if len(changed_branches) > 0:
        for branch in changed_branches:
            print(f'Branch {branch} has changes.')

def git_batch_sync() -> None:
    """Synchronize local repository states with their remote counterparts."""

    print(REPOSITORY_INPUT_PROMPT, end='')

    repository_input = str(input())
    repositories: list[str] = []

    while repository_input != REPOSITORY_INPUT_END_MARKER:
        repositories.append(repository_input)

        repository_input = str(input())

    for repository in repositories:
        _git_fetch(repository)
        _git_checkout_remote_main(repository)

git_batch_sync()
