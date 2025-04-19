from pathlib import Path
from typing import Optional, List

from pydantic import BaseModel, field_validator
from filemate.utils.validators import ensure_directory

from rich.console import Console


class RenameConfig(BaseModel):
    """
    Configuration for renaming files in a directory.

    :param folder: Path to the folder containing files to rename.
    :type folder: Path

    :param pattern: Pattern for renaming files. Use `{i}` as a placeholder for the index.
    :type pattern: str

    :param extensions: Optional list of file extensions to filter (e.g., ['.jpg', '.png']).
    :type extensions: Optional[List[str]]

    :param start: Starting index for file enumeration. (default is 1)
    :type start: int

    :param output_dir: Optional output directory for renamed files.
    :type output_dir: Optional[Path]
    """

    folder: Path
    pattern: str = "file_{i}"
    extensions: Optional[List[str]] = None
    start: int = 1
    output_dir: Optional[Path] = None

    _folder_exists = field_validator("folder")(ensure_directory)

    @field_validator("start", mode="before")
    def validate_start(cls: "RenameConfig", value: int) -> int:
        value = int(value)
        if value < 1:
            raise ValueError("Start index must be greater than or equal to 1.")
        return value


def rename_files(config: RenameConfig, dry_run: bool = False) -> int:
    """
    Rename files in the given folder using the specified pattern.

    :param config: RenameConfig model containing all required parameters.
    :type config: RenameConfig
    :return: The number of files successfully renamed.
    :rtype: int
    :param dry_run: If True, simulate renaming without changing files. (default is False)
    :type dry_run: bool
    :raises ValueError: If the folder is not a valid directory.
    :raises FileExistsError: If a generated filename already exists.
    """
    target_dir = config.output_dir or config.folder
    if config.output_dir and not config.output_dir.exists():
        config.output_dir.mkdir(parents=True, exist_ok=True)  # Add exist_ok

    files = sorted(
        f
        for f in config.folder.iterdir()
        if f.is_file()
        and (
            not config.extensions
            or f.suffix.lower() in [ext.lower().strip() for ext in config.extensions]
        )
    )

    console = Console()
    renamed_count = 0
    MAX_RENAME_ATTEMPTS = 10  # Max attempts to FIND a new name if conflicts occur

    # Use a separate variable for the index within the loop for conflict resolution
    current_file_index = config.start

    # Iterate through the files using enumerate just to get the original file object
    # We'll manage the numbering index (current_file_index) separately
    for file_obj in files:
        attempt = 0
        # Start with the current expected index
        resolved_index = current_file_index

        # Determine the first potential new path
        new_name = config.pattern.format(i=resolved_index) + file_obj.suffix
        new_path = target_dir / new_name

        # --- Conflict Resolution Loop ---
        # Keep trying until a non-existing path is found OR max attempts are reached
        while new_path.exists() and attempt < MAX_RENAME_ATTEMPTS:
            attempt += 1
            resolved_index += 1  # Increment index for the next try
            new_name = config.pattern.format(i=resolved_index) + file_obj.suffix
            new_path = target_dir / new_name
        # --- End Conflict Resolution Loop ---

        # Check if a usable name was found AFTER the loop
        if new_path.exists():
            # If it STILL exists here, we must have hit max attempts finding a free slot
            console.print(
                f"[red]Error: Could not rename {file_obj.name}. Conflict with {new_name} persisted after {attempt} attempts.[/red]"
            )
            # Do NOT increment current_file_index, maybe the next file can use it
            continue  # Skip this file

        # --- Proceed with rename using the determined (non-existing) new_path ---
        if dry_run:
            console.print(f"[yellow][DRY RUN][/yellow] {file_obj.name} → {new_name}")
            # In dry run, still increment the main index as if rename happened
            current_file_index = resolved_index + 1
        else:
            try:
                file_obj.rename(new_path)
                renamed_count += 1
                console.print(f"[green]Renamed:[/green] {file_obj.name} → {new_name}")
                # Increment the main index only after successful rename
                current_file_index = resolved_index + 1
            except PermissionError as e:
                console.print(
                    f"[red]Permission denied (skipped):[/red] {file_obj.name} → {new_name}"
                )
                console.print(f"[red]Error details:[/red] {str(e)}")
                # Do NOT increment current_file_index if skipped
                continue
            except FileExistsError:  # Should be rare now, but handles race conditions
                console.print(f"[red]File already exists (skipped):[/red] {new_name}")
                # Do NOT increment current_file_index if skipped
                continue
            except Exception as e:
                console.print(f"[red]Error renaming {file_obj.name}:[/red] {str(e)}")
                # Do NOT increment current_file_index if skipped
                continue

    return renamed_count
