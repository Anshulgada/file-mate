import rich_click as click
from pathlib import Path
from typing import Optional, List

from filemate.core.change_extension import change_extensions, ChangeExtConfig

from .file_group import file


@file.command(name="change-ext")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=str))
@click.option(
    "--to",
    "new_extension",  # Using 'new_extension' internally
    required=True,
    type=str,
    help="The target file extension (e.g., '.txt' or 'txt', 'png', 'jpeg' ). The leading dot is optional.",
)
@click.option(
    "--from",
    "from_extensions",  # Using 'from_extensions' internally
    default=None,
    type=str,
    help="Optional: Comma-separated list of source extensions to change (e.g., '.jpg,.jpeg' or 'txt'). If omitted, changes all files.",
)
@click.option(
    "--output-dir",
    "-o",
    default=None,
    type=click.Path(file_okay=False, path_type=str),
    help="Optional directory to save files with changed extensions.",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt before changing extensions.",  # NEW
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force overwrite if a file with the target name already exists.",  # NEW
)
@click.option(
    "--dry-run", is_flag=True, help="Preview the changes without modifying any files."
)
def change_extensions_in_directory(
    folder: str,
    new_extension: str,
    from_extensions: Optional[str],
    output_dir: Optional[str],
    yes: bool,  # NEW
    force: bool,  # NEW
    dry_run: bool,
) -> None:
    """
    Change the file extension for files in a directory.

    You can specify which source file extensions to target, or change all files in the directory.

    Can filter source extensions using --from.

    By default, asks for confirmation before changing files; use -y or --yes to skip.

    Use -f or --force to overwrite existing target files.
    If a file with the target name already exists, a conflict resolution process is initiated.
    Symbolic links in the source directory are skipped.

    Files that already have the target extension are skipped.
    Files can optionally be moved to an output directory during the process.
    """
    source_exts: Optional[List[str]] = None
    if from_extensions:
        source_exts = [ext.strip() for ext in from_extensions.split(",") if ext.strip()]
        if not source_exts:  # Handle empty list if input was just commas/spaces
            source_exts = None

    try:
        config = ChangeExtConfig(
            folder=Path(folder),
            new_extension=new_extension,
            from_extensions=source_exts,
            output_dir=Path(output_dir) if output_dir else None,
        )
        # Pass the new flags to the core function
        change_extensions(
            config, dry_run=dry_run, yes=yes, force=force
        )  # Pass yes and force

    except Exception as e:
        # Catch validation errors from Pydantic or other unexpected errors
        click.echo(f"Error: {e}", err=True)
        # Consider exiting with non-zero status code here if needed
        import sys

        sys.exit(1)
