import rich_click as click
from pathlib import Path
from typing import Optional, List
from filemate.core.rename import rename_files, RenameConfig


@click.command(name="rename")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=str))
@click.option(
    "--pattern",
    default="file_{i}",
    help="Rename pattern using {i} as index placeholder.",
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
    "--dry-run",
    is_flag=True,
    help="Preview the files that would be renamed without making changes.",
)
def rename_files_in_directory(
    folder: Path,
    pattern: str,
    ext: Optional[str],
    start: int,
    output_dir: Optional[str],
    dry_run: bool,
) -> None:
    """
    Rename files in a directory using a given pattern.

    Files are processed in alphanumeric sorted order.

    You can filter which files are renamed based on their extension and specify the starting
    index number used in the renaming pattern {i}.

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

    config = RenameConfig(
        folder=Path(folder),
        pattern=pattern,
        extensions=extensions,
        start=start,
        output_dir=Path(output_dir) if output_dir else None,
    )
    rename_files(config, dry_run=dry_run)
