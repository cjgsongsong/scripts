# `unlock-pdf`

This script is for unlocking password-protected PDF files.

For other scripts, see the [main `README`](../README.md).

## Prerequisites

### Main Prerequisites

As inferable from the code and as specified in `pyproject.toml`, the following are needed to install and run this script.

- Application that supports script execution via a command-line interface
  - e.g.
    - [Windows Terminal](https://aka.ms/terminal)
    - [Visual Studio Code](https://code.visualstudio.com)
    - etc.
- Command-line interface
  - e.g.
    - [Command Prompt](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cmd)
    - [Windows PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell)
    - etc.
- [Git](https://git-scm.com/install/windows)
  - must be `v2.54.0.windows` or above or equivalent
- [Python](https://www.python.org/downloads)
  - must be `v3.14` or above
  - preferably installed via the official installation manager

### Python-related Prerequisites

Once Python is successfully installed, the following are also needed.

- [`pipx`](https://pipx.pypa.io/stable/how-to/install-pipx/#on-windows)
  - installed via

    ```bash
    pip install pipx --user
    ```

  - must be `v1.12.0` or above

- [Poetry](https://python-poetry.org/docs/#installing-with-pipx)
  - installed via

    ```bash
    pipx install poetry
    ```

  - must be `v2.4.1` or above
  - preferably configured to generate a virtual environment in the directory where a command was executed via

    ```bash
    poetry config virtualenvs.in-project true --local
    ```

## Installation

1. Clone the repository containing the script.

   ```bash
   git clone https://github.com/cjgsongsong/scripts.git
   ```

2. Navigate to the script's package.

   ```bash
   cd unlock_pdf
   ```

3. Install the script's dependencies.

   ```bash
   poetry install
   ```
