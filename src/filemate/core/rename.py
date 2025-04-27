from pathlib import Path
from typing import Optional, List, Set

from pydantic import BaseModel, field_validator
from filemate.utils.validators import ensure_directory

from rich.console import Console
import os
import sys
import shutil
import rich_click as click

# --- Initialize Console with Test Detection ---
# Detect if running under pytest or in CI to disable color codes for easier parsing
# More reliable test detection
is_testing = (
    "pytest" in sys.modules
    or any("pytest" in key for key in sys.modules.keys())
    or "CI" in os.environ
)
console_color_system = None if is_testing else "auto"  # None = no color codes
console = Console(color_system=console_color_system)  # type: ignore[arg-type] # noqa: F811
# --- End Console Init ---


class RenameConfig(BaseModel):
    """
    Configuration for renaming files in a directory.

    :param folder: Path to the folder containing files to rename.
    :type folder: Path

    :param pattern: Pattern for renaming files. Use `{i}` as a placeholder for the index.
                    Supports format specifiers like {i:03d}.
    :type pattern: str

    :param extensions: Optional list of file extensions to filter (e.g., ['.jpg', '.png']).
    :type extensions: Optional[List[str]]

    :param source_prefix: Optional prefix for source files to filter by.
    :type source_prefix: Optional[str]

    :param start: Starting index for file enumeration. (default is 1)
    :type start: int

    :param output_dir: Optional output directory for renamed files.
    :type output_dir: Optional[Path]
    """

    folder: Path
    pattern: str = "file_{i}"
    extensions: Optional[List[str]] = None
    source_prefix: Optional[str] = None  # NEW: filter by prefix if set
    start: int = 1
    output_dir: Optional[Path] = None

    _folder_exists = field_validator("folder")(ensure_directory)

    @field_validator("start", mode="before")
    def validate_start(cls: "RenameConfig", value: int) -> int:
        value = int(value)
        if value < 1:
            raise ValueError("Start index must be greater than or equal to 1.")
        return value


def rename_files(
    config: RenameConfig,
    dry_run: bool = False,
    yes: bool = False,  # NEW: Skip confirmation prompt
    force: bool = False,  # NEW: Force overwrite on conflict
) -> int:
    """
    Rename files in the given folder using the specified pattern.

    :param config: RenameConfig model containing all required parameters.
    :type config: RenameConfig
    :param dry_run: If True, simulate renaming without changing files. (default is False)
    :type dry_run: bool
    :param yes: If True, skip the confirmation prompt before renaming.
    :type yes: bool
    :param force: If True, overwrite existing files during conflict resolution.
    :type force: bool
    :return: The number of files successfully renamed or previewed.
    :rtype: int
    :raises ValueError: If the folder is not a valid directory or pattern format fails.
    :raises FileExistsError: If a generated filename already exists and force is False.
    """
    target_dir = config.output_dir or config.folder
    if config.output_dir and not config.output_dir.exists():
        try:
            config.output_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[dim]Created output directory:[/dim] {config.output_dir}")
        except OSError as e:
            console.print(
                f"[red]Error creating output directory {config.output_dir}: {e}[/red]"
            )

    # Prepare filters for extensions
    source_ext_filter: Optional[Set[str]] = None
    if config.extensions:
        source_ext_filter = {
            f".{ext}" if not ext.startswith(".") else ext
            for ext in (e.lower().strip() for e in config.extensions if e.strip())
        }

    # Get initial list of files to consider
    try:
        # IMPORTANT: Apply extensions filter correctly - only consider files with matching extensions
        files_to_consider = sorted(
            f
            for f in config.folder.iterdir()
            if (f.is_file() or f.is_symlink())
            and (not source_ext_filter or f.suffix.lower() in source_ext_filter)
            and (not config.source_prefix or f.name.startswith(config.source_prefix))
        )

    except FileNotFoundError:
        console.print(f"[red]Error: Source folder '{config.folder}' not found.[/red]")
        return 0
    except PermissionError:
        console.print(
            f"[red]Error: Permission denied reading folder '{config.folder}'.[/red]"
        )
        return 0

    # Filter files and count symlinks
    files_to_process = []
    symlinks_skipped = 0
    for f in files_to_consider:
        if f.is_symlink():
            console.print(f"[dim]Skipping symbolic link:[/dim] {f.name}")
            symlinks_skipped += 1
            continue  # Skip symlinks by default
        files_to_process.append(f)

    # Early exit if no files match
    if not files_to_process:
        console.print("[yellow]No files found matching criteria to rename.[/yellow]")
        if symlinks_skipped > 0:
            console.print(f"Symbolic links skipped: {symlinks_skipped}")
        return 0

    # Initialize counters
    renamed_count = 0
    previewed_count = 0  # Separate count for dry run
    skipped_conflicts = 0
    skipped_errors = 0
    MAX_RENAME_ATTEMPTS = 10  # Max attempts to FIND a new name if conflicts occur

    # --- Confirmation Prompt ---
    if not dry_run and not yes:
        console.print("\n--- Proposed Changes ---")
        preview_count_display = 0
        temp_index = config.start
        for file_obj in files_to_process:
            if preview_count_display >= 5:
                break
            try:
                preview_name = config.pattern.format(i=temp_index) + file_obj.suffix
                console.print(f"- {file_obj.name} → {preview_name}")
            except Exception:
                console.print(f"- {file_obj.name} → [red]Error applying pattern[/red]")
            temp_index += 1
            preview_count_display += 1
        if len(files_to_process) > preview_count_display:
            console.print(
                f"- ... and {len(files_to_process) - preview_count_display} more file(s)"
            )

        console.print(
            f"\nAbout to rename {len(files_to_process)} file(s) in '{config.folder}'"
            f"{f' to directory {target_dir}' if config.output_dir else ''}."
        )
        if force:
            console.print(
                "[yellow]--force specified: Existing target files WILL be overwritten![/yellow]"
            )
        if not click.confirm("Proceed with renaming?"):
            console.print("[yellow]Operation cancelled by user.[/yellow]")
            return 0
    # --- End Confirmation ---

    # Use a separate variable for the index within the loop for conflict resolution
    current_file_index = config.start

    # Iterate through the files using enumerate just to get the original file object
    # We'll manage the numbering index (current_file_index) separately
    for file_obj in files_to_process:
        attempt = 0
        # Start with the current expected index
        resolved_index = current_file_index
        new_path = None

        # Determine the first potential new path
        # Use str.format for pattern - it supports {i:03d} etc.
        try:
            formatted_base = config.pattern.format(i=resolved_index)
        except (
            ValueError,
            KeyError,
        ) as fmt_e:  # Handle potential bad format specifiers
            console.print(
                f"[red]Error applying pattern '{config.pattern}' for index {resolved_index}: {fmt_e}[/red]"
            )
            skipped_errors += 1
            current_file_index += 1
            continue  # Skip this file

        new_name = formatted_base + file_obj.suffix
        new_path = target_dir / new_name

        # --- Conflict Resolution Loop ---
        while (
            new_path.exists() and new_path != file_obj
        ):  # Don't conflict with self if renaming in place
            if force:
                console.print(
                    f"[yellow]--force specified: Overwriting existing file {new_path.name}[/yellow]"
                )
                break  # Stop trying to find a new name, proceed with overwrite

            if attempt >= MAX_RENAME_ATTEMPTS:
                break  # Max attempts reached

            attempt += 1
            resolved_index += 1  # Increment index for the next try

            # Re-try formatting inside the loop
            try:  # Add try-except here too
                formatted_base = config.pattern.format(i=resolved_index)
            except (ValueError, KeyError) as fmt_e:
                console.print(
                    f"[red]Error applying pattern '{config.pattern}' during conflict resolution for index {resolved_index}: {fmt_e}[/red]"
                )
                new_path = None  # Signal error occurred
                break  # Exit while loop on format error

            new_name = formatted_base + file_obj.suffix
            new_path = target_dir / new_name
        # --- End Conflict Resolution Loop ---

        if new_path is None:  # Error during pattern formatting
            skipped_errors += 1
            continue

        # Check if conflict resolution failed
        if new_path.exists() and not force and new_path != file_obj:
            console.print(
                f"[red]Error: Could not rename {file_obj.name}. Conflict with {new_name} persisted after {attempt} attempts.[/red]"
            )
            skipped_conflicts += 1
            current_file_index += 1
            continue

        # --- Proceed with rename ---
        if dry_run:
            console.print(f"[yellow][DRY RUN][/yellow] {file_obj.name} → {new_name}")
            previewed_count += 1  # Use previewed_count for dry run
            # In dry run, still increment the main index as if rename happened
            current_file_index = resolved_index + 1  # Increment index even on dry run
        else:
            try:
                # If moving to another dir OR overwriting, use move
                # If renaming in place without overwrite, rename is fine
                # shutil.move can handle cross-filesystem moves unlike os.rename
                if config.output_dir or (
                    force and new_path.exists()
                ):  # Need check here too for overwrite case
                    shutil.move(str(file_obj), str(new_path))
                else:
                    # Check if target exists *just before* rename if not forcing
                    # This helps catch race conditions but might add overhead
                    if not force and new_path.exists():
                        raise FileExistsError(
                            f"Target '{new_path.name}' created unexpectedly."
                        )
                    file_obj.rename(new_path)

                renamed_count += 1  # Increment actual rename count
                console.print(f"[green]Renamed:[/green] {file_obj.name} → {new_name}")
                # Increment the main index only after successful rename
                current_file_index = (
                    resolved_index + 1
                )  # Increment index only on success
            except PermissionError as e:
                console.print(
                    f"[red]Permission denied (skipped):[/red] {file_obj.name} → {new_name} ({e})"
                )
                # Do NOT increment current_file_index if skipped
                skipped_errors += 1
                current_file_index += 1
                continue
            except FileExistsError as e:  # Catch race condition or pre-check failure
                console.print(
                    f"[red]File already exists (skipped):[/red] {new_name} ({e})"
                )
                skipped_conflicts += 1  # Treat as conflict
                current_file_index += 1
                continue
            except Exception as e:
                console.print(f"[red]Error renaming {file_obj.name}:[/red] {str(e)}")
                skipped_errors += 1
                current_file_index += 1
                continue

    # --- Consistent Summary ---
    console.print("\n--- Rename Summary ---")
    final_count = 0  # Count to return
    if dry_run:
        console.print(f"Files previewed for rename: {previewed_count}")
        final_count = previewed_count  # Return preview count for dry run
    else:
        console.print(f"Files renamed successfully: {renamed_count}")
        final_count = renamed_count  # Return renamed count otherwise
    # Report skipped counts only if they occurred
    if skipped_conflicts > 0:
        console.print(f"Files skipped (due to naming conflicts): {skipped_conflicts}")
    if skipped_errors > 0:
        console.print(f"Files skipped (due to errors): {skipped_errors}")
    if symlinks_skipped > 0:
        console.print(f"Symbolic links skipped: {symlinks_skipped}")
    # --- End Summary ---

    return final_count  # Return the relevant count
