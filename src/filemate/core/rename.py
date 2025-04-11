from pathlib import Path
from typing import Optional

from pydantic import BaseModel, field_validator
from filemate.utils.validators import ensure_directory

from rich.console import Console
from rich.progress import track


class RenameConfig(BaseModel):
    """
    Configuration for renaming files in a directory.

    :param folder: Path to the folder containing files to rename.
    :type folder: Path
    :param pattern: Pattern for renaming files. Use `{i}` as a placeholder for the index.
    :type pattern: str
    :param ext: Optional file extension filter (e.g., '.jpg').
    :type ext: Optional[str]
    :param start: Starting index for file enumeration. (default is 1)
    :type start: int
    :param output_dir: Optional output directory for renamed files.
    :type output_dir: Optional[Path]
    """

    folder: Path
    pattern: str = "file_{i}"
    ext: Optional[str] = None
    start: int = 1
    output_dir: Optional[Path] = None

    _folder_exists = field_validator("folder")(ensure_directory)


def rename_files(config: RenameConfig) -> int:
    """
    Rename files in the given folder using the specified pattern.

    :param config: RenameConfig model containing all required parameters.
    :type config: RenameConfig
    :return: The number of files successfully renamed.
    :rtype: int
    :raises ValueError: If the folder is not a valid directory.
    :raises FileExistsError: If a generated filename already exists.
    """
    target_dir = config.output_dir or config.folder
    if config.output_dir and not config.output_dir.exists():
        config.output_dir.mkdir(parents=True)

    files = sorted(
        f
        for f in config.folder.iterdir()
        if f.is_file() and (not config.ext or f.suffix == config.ext)
    )

    console = Console()
    renamed_count = 0

    for i, file in track(
        enumerate(files, start=config.start), description="Renaming files..."
    ):
        new_name = config.pattern.format(i=i) + file.suffix
        new_path = target_dir / new_name

        while new_path.exists():
            i += 1
            new_name = config.pattern.format(i=i) + file.suffix
            new_path = target_dir / new_name

        file.rename(new_path)
        renamed_count += 1
        console.print(f"[green]Renamed:[/green] {file.name} → {new_name}")

    return renamed_count
