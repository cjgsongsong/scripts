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

## Usage

Supposing the user is at the repository's root directory, using the script is as follows.

1. Navigate to the script's package.

   ```bash
   cd unlock_pdf
   ```

2. Run using Poetry either the script's package

   ```bash
   poetry run unlock-pdf
   ```

   or the script's main file.

   ```bash
   poetry run python src/unlock_pdf/__main__.py
   ```

3. Enter every directory path or file path of the PDF files to unlock.

4. Enter an empty string to quit entering paths.

5. Enter every password to attempt unlocking the PDF files with.

6. Enter an empty string to quit entering passwords.

7. Verify the results of the unlock attempt.

## Example

```bash
\scripts\unlock_pdf> poetry run unlock-pdf
```

```bash
Enter every directory path or file path of the PDF file(s) to unlock.
Enter an empty string to quit.
>
"\1-locked-with-password-123.pdf"
"\2-locked-with-password-123.pdf"
"\3-not-locked.pdf"

Enter every password to attempt unlocking the PDF file(s) with.
Enter an empty string to quit.
>
123

0 PDF files are still locked:
-

1 PDF file is not locked:
\3-not-locked.pdf

2 PDF files are unlocked:
\1-locked-with-password-123.pdf
\2-locked-with-password-123.pdf

```

```bash
\scripts\unlock_pdf> _
```

## Changelog

- `v0.7.0`
  - allowed package execution
  - improved
    - documentation
    - logs
  - refactored code
- `v0.6.0`
  - ignored duplicates
    - passwords
    - paths
- `v0.5.0`
  - logged unlocking result by file state
  - refactored code
- `v0.4.0`
  - improved
    - documentation
    - input order
    - logs
  - refactored code
  - unlocked PDF files in given multiple paths with given multiple passwords
    - allowed directory path inputs
- `v0.3.0`
  - improved logs
  - unlocked PDF file in given file path with given multiple passwords
- `v0.2.0`
  - logged unlocking result
  - handled
    - failed overwrite
    - incorrect password
    - unprotected PDF file
  - sanitized file path input
  - validated inputs
- `v0.1.0`
  - unlocked PDF file in given file path with given password
- `v0.0.0`
  - initialized package
