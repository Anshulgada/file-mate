import rich_click as click
from pathlib import Path
from typing import Optional, List
from filemate.core.rename import rename_files, RenameConfig

from .file_group import file


@file.command(name="rename")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=str))
@click.option(
    "--pattern",
    default="file_{i}",
    help="Rename pattern using {i} as index placeholder. Supports format specifiers like {i:03d}.",
)
@click.option(
    "--ext",
    default=None,
    help="Optional comma-separated file extensions to include (e.g., .jpg,.png or jpg,png). Common image types: jpg, png, jpeg, gif, bmp, webp.",
)
@click.option("--start", default=1, type=int, help="Starting index. (default = 1)")
@click.option(
    "--output-dir",
    "-o",
    default=None,
    type=click.Path(file_okay=False, path_type=str),
    help="Optional directory to save renamed files.",
)
@click.option(
    "--source-prefix",
    "-sp",
    default=None,
    help="Optional prefix for source files to filter by.",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt before renaming.",  # NEW
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force overwrite if target filename exists during conflict resolution.",  # NEW
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview the files that would be renamed without making changes.",
)
def rename_files_in_directory(
    folder: str,
    pattern: str,
    ext: Optional[str],
    start: int,
    output_dir: Optional[str],
    source_prefix: Optional[str],
    yes: bool,  # NEW
    force: bool,  # NEW
    dry_run: bool,
) -> None:
    """
    Rename files in a directory using a given pattern.

    Files are processed in alphanumeric sorted order.

    Format specifiers like :03d can be used within the {i} placeholder (e.g., "img_{i:04d}").

    If a file with the same name already exists in the target directory,
    a conflict resolution process is initiated. You can choose to overwrite
    the existing file, skip the file, or rename the existing file to a new name.

    You can filter which files are renamed based on their extension and specify the starting
    index number used in the renaming pattern {i}. You can also filter files by their prefix
    using the --source-prefix option.

    By default, you will be asked for confirmation before renaming.
    Use -y or --yes to skip confirmation.
    Use -f or --force to overwrite existing files if name conflicts occur.
    Symbolic links in the source directory are skipped.

    You can pass multiple extensions using commas (e.g., '.jpg,.png' or 'jpg,png').

    Renamed files can optionally be moved to a separate output directory.
    """
    extensions: Optional[List[str]] = None
    if ext:
        extensions = [
            e.strip() if e.strip().startswith(".") else f".{e.strip()}"
            for e in ext.split(",")
            if e.strip()
        ]

    try:
        config = RenameConfig(
            folder=Path(folder),
            pattern=pattern,
            extensions=extensions,
            start=start,
            output_dir=Path(output_dir) if output_dir else None,
            source_prefix=source_prefix,
        )
        # Pass the new flags to the core function
        rename_files(
            config, dry_run=dry_run, yes=yes, force=force
        )  # Pass yes and force
    except Exception as e:
        # Catch validation errors from Pydantic or other unexpected errors
        click.echo(f"Error: {e}", err=True)
        # Consider exiting with non-zero status code here if needed
        import sys

        sys.exit(1)
