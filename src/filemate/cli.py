# ruff: noqa: F401 --> To remove unused import warnings for whole file

# Import commands here to ensure they are registered with the CLI
from filemate.commands import rename
from filemate.commands import change_extension

# Import the group commands
from filemate.commands.file_group import file

import rich_click as click
from filemate import __version__  # Import version defined in __init__.py


@click.group(
    context_settings=dict(
        help_option_names=["-h", "--help"],
        auto_envvar_prefix="FILEMATE",
    )
)
@click.version_option(
    __version__,  # Dynamically pull version string
    "--version",
    "-v",
    message="%(prog)s version %(version)s",
)
def cli() -> None:
    """FileMate: Your CLI tool for file operations."""
    pass


# Add the top-level groups
cli.add_command(file)

if __name__ == "__main__":
    cli()
