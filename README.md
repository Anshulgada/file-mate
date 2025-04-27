# FileMate

FileMate is your all-in-one, offline-first command-line tool for file manipulation and organization. Born out of the need for a robust, privacy-respecting alternative to online file utilities.

FileMate aims to be the Swiss Army knife for handling files of all types—images, PDFs, documents, and more—directly from your terminal.

## Table of Contents
- [Why FileMate?](#why-filemate)
- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Development Philosophy](#development-philosophy)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)


## Why FileMate?

Most file manipulation tools are either fragmented, online-only, or limited in scope.
FileMate was created to unify essential file operations under a single, extensible CLI, ensuring your data never leaves your machine.

Whether you're batch-renaming images, changing file extensions, or preparing for more advanced operations, FileMate is designed to be your trusted companion for all things file-related.


## Installation


**Available soon on [PyPI]!**

### Recommended Methods:

- **With [pipx] (isolated CLI install - recommended):**

  ```sh
  pipx install filemate
  ```

- **With [uv] (fast, modern Python package manager):**

  ```sh
  uv pip install --upgrade filemate
  ```

- **With [pip]:**

  ```sh
  pip install --upgrade filemate
  ```


### Planned One-Liner Install
A single command to install FileMate via curl or similar will be provided for convenience:

```bash
curl -sSf curl -sSf https://bit.ly/filemate | bash
```
Windows PowerShell:
```powershell
irm curl -sSf https://bit.ly/filemate | iex
```


### Install Scripts

- **Unix/macOS:** [`install.sh`](./install.sh) 🖥️
- **Windows:** [`install.ps1`](./install.ps1) 💻

These scripts will auto-detect your environment and install FileMate using pipx or pip as appropriate.


## 🚀 Features (Current & Roadmap)

### ✅ Implemented

- **File Renaming**: Sequentially rename files in a folder using customizable patterns. Handles conflicts and supports dry-run mode.
- **Change File Extension**: Bulk change file extensions with filtering and output directory options.

### 🔜 In Development / Planned

- 🔧 Metadata editing
- 📝 File deduplication
- 🔄 More powerful batch operations
- 🎨 Advanced image, PDF, and document manipulation
- 🗂️ Organize files into subfolders by date, extension, or type


## 📦 Usage

### ⚙️ Installation

FileMate requires **Python 3.12+** and is best installed with **pipx**, **[uv]**, or **pip**:

```bash
pipx install file-mate
# or
uv pip install .
# or
pip install file-mate
```


### `>_` CLI Overview
All commands are grouped under the `filemate` CLI. Use `--help` for details on any command.

#### 📂 File Group
General file and directory operations:

- **Rename files**
  ```sh
  filemate file rename <folder> [OPTIONS]
  ```
  - `--pattern`: Naming pattern (e.g., `img_{i}` or format specifiers like `{i:03d}`)
  - `--ext`: Filter by extension
  - `--start`: Starting index
  - `--output-dir`: Output directory
  - `--dry-run`: Preview changes

- **Change file extensions**
  ```sh
  filemate file change-ext <folder> [OPTIONS]
  ```
  - `--to`: Target extension (required)
  - `--from`: Source extension(s)
  - `--output-dir`: Output directory
  - `--dry-run`: Preview changes

For more, run `filemate --help` or see the docs.


## Project Structure

```
src/
  filemate/
    cli.py         # CLI entrypoint
    commands/      # Command groups
    core/          # Core logic
    utils/         # Helper utilities
tests/             # Pytest tests
docs/              # Documentation
```

Planning files: [`Plan.md`](./Plan.md), [`Planning.md`](./Planning.md), [`Test.md`](./Test.md)


## Development Philosophy

- 🛡️ **Offline-first:** Your data stays local
- 🧩 **Extensible:** Modular and pluggable
- 🐍 **Modern Python:** Typing, linting, formatting
- 🎨 **Rich UX**: Beautiful CLI with [`rich`](https://rich.readthedocs.io/) and [`rich-click`](https://ewels.github.io/rich-click/)
- ✅ **Tested:** Pytest coverage
- 🔄 **CI/CD:** GitHub Actions
- 🚥 **Pre-commit hooks:** Code quality enforced automatically


## Contributing

We welcome all contributions — big or small!
See the [Contributing Guidelines] or [open an issue].

## License

Distributed under the [MIT License].


## Acknowledgements

Built with love and powered by:

- [Click]
- [Rich]
- [rich-click]
- [Pydantic]
- And a passion for better file tools!


## 🚧 Status

> 🛠️ **FileMate** is under active development.
>
> ⏳ **Stay tuned** for more features and feel free to suggest or contribute new ideas!
>
> ⭐ Star the repo** to stay updated and help shape its future!


<!-- Link references -->
[Click]: https://click.palletsprojects.com/
[Contributing Guidelines]: CONTRIBUTING.md
[MIT License]: LICENSE
[pip]: https://pip.pypa.io/en/stable/getting-started/
[PyPI]: https://pypi.org/project/filemate/
[Pydantic]: https://docs.pydantic.dev/
[pipx]: https://pipx.pypa.io/stable/
[rich-click]: https://ewels.github.io/rich-click/
[Rich]: https://rich.readthedocs.io/
[open an issue]: https://github.com/Anshulgada/file-mate/issues
[uv]: https://github.com/astral-sh/uv
