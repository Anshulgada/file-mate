import click
from pathlib import Path
from filemate.core.rename import rename_files, RenameConfig


@click.command(name="rename")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, path_type=str))
@click.option(
    "--pattern",
    default="file_{i}",
    help="Rename pattern using {i} as index placeholder.",
)
@click.option("--ext", default=None, help="Optional file extension filter.")
@click.option("--start", default=1, type=int, help="Starting index. (default = 1)")
@click.option(
    "--output-dir",
    default=None,
    type=click.Path(file_okay=False, path_type=str),
    help="Optional directory to save renamed files.",
)
def rename_files_in_directory(
    folder: Path, pattern: str, ext: str, start: int, output_dir: str
) -> None:
    """
    Rename files in a directory using a given pattern.

    :param folder: Directory containing files to rename.
    :param pattern: Pattern for new file names, must include `{i}`.
    :param ext: Optional extension filter (e.g., `.txt`).
    :param start: Starting index to begin renaming from. (default is 1)
    :param output_dir: Optional output directory to move renamed files into.
    """
    config = RenameConfig(
        folder=Path(folder),
        pattern=pattern,
        ext=ext,
        start=start,
        output_dir=Path(output_dir) if output_dir else None,
    )
    rename_files(config)
