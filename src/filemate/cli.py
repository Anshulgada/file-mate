# src/filemate/cli.py

# Import commands here to ensure they are registered with the CLI
from filemate.commands.rename import rename_files_in_directory

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


cli.add_command(rename_files_in_directory, name="rename")


if __name__ == "__main__":
    cli()
