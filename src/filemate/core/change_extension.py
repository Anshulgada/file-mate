import shutil
from pathlib import Path
from typing import Optional, List, Set

from pydantic import BaseModel, field_validator, model_validator
from filemate.utils.validators import ensure_directory

from rich.console import Console
import os  # noqa: F401
import sys
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


class ChangeExtConfig(BaseModel):
    """
    Configuration for changing file extensions in a directory.

    :param folder: Path to the folder containing files.
    :param new_extension: The target extension (e.g., '.txt'). Must start with a dot.
    :param from_extensions: Optional list of source extensions to filter (e.g., ['.jpg', '.jpeg']).
                            If None, all files are considered.
    :param output_dir: Optional output directory for files with changed extensions.
    """

    folder: Path
    new_extension: str
    from_extensions: Optional[List[str]] = None
    output_dir: Optional[Path] = None

    _folder_exists = field_validator("folder")(ensure_directory)

    @field_validator("new_extension")
    def validate_and_normalize_new_extension(cls: "ChangeExtConfig", value: str) -> str:
        """Validates and ensures the new extension starts with a dot."""
        value = value.strip()
        if not value:
            raise ValueError("New extension cannot be empty.")
        # Prepend dot if missing
        if not value.startswith("."):
            value = f".{value}"
        return value

    @model_validator(mode="after")
    def process_from_extensions(self) -> "ChangeExtConfig":
        """Normalizes source extensions to lowercase and ensures leading dot."""
        # This validator primarily prepares the data if needed internally on the model.
        # The core function also does on-the-fly processing, which is fine.
        # Keeping this doesn't hurt but isn't strictly necessary if the main func handles it.
        if self.from_extensions:
            processed: Set[str] = set()
            for ext in self.from_extensions:
                ext = ext.strip().lower()
                if not ext:
                    continue
                if not ext.startswith("."):
                    processed.add(f".{ext}")
                else:
                    processed.add(ext)
            # Store processed extensions efficiently if needed later, or just use them
            # For simplicity, we might re-process in the main function if needed often
            # Or store the processed set: self.processed_from_extensions = processed
        return self


def change_extensions(
    config: ChangeExtConfig,
    dry_run: bool = False,
    yes: bool = False,  # NEW: Skip confirmation
    force: bool = False,  # NEW: Force overwrite
) -> int:
    """
    Change extensions of files in the given folder.

    :param config: ChangeExtConfig model.
    :param dry_run: If True, simulate without changing files.
    :param yes: If True, skip the confirmation prompt before changing extensions.
    :param force: If True, overwrite existing files with the new extension name.
    :return: The number of files successfully processed.
    :raises ValueError: If config validation fails or folder is invalid.
    :raises FileExistsError: If a target filename already exists (not overwritten).
    """
    target_dir = config.output_dir or config.folder
    if config.output_dir and not config.output_dir.exists():
        try:
            # Ensure parent directories exist as well
            config.output_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[dim]Created output directory:[/dim] {config.output_dir}")
        except OSError as e:
            console.print(
                f"[red]Error creating output directory {config.output_dir}: {e}[/red]"
            )
            return 0  # Cannot proceed if output dir cannot be created

    # Pre-process from_extensions for efficient lookup
    source_ext_filter: Optional[Set[str]] = None
    if config.from_extensions:
        source_ext_filter = {
            (
                ext.lower().strip()
                if ext.lower().strip().startswith(".")
                else f".{ext.lower().strip()}"
            )
            for ext in config.from_extensions
            if ext.strip()
        }
        if (
            not source_ext_filter
        ):  # Handle case where list was provided but became empty
            source_ext_filter = None

    console.print(f"Processing files in: {config.folder}")
    if source_ext_filter:
        console.print(
            f"Filtering for source extensions: {', '.join(sorted(source_ext_filter))}"
        )
    console.print(f"Target extension: {config.new_extension}")
    if config.output_dir:
        console.print(f"Output directory: {config.output_dir}")

    # Iterate through files to get initial list of files and symlinks to consider (modified)
    files_to_consider = sorted(
        f for f in config.folder.iterdir() if f.is_file() or f.is_symlink()
    )

    # Filter list based on criteria (modified)
    files_to_process = []
    symlinks_skipped = 0
    already_done_skipped = 0
    for f in files_to_consider:
        if f.is_symlink():  # NEW: Skip symlinks
            console.print(f"[dim]Skipping symbolic link:[/dim] {f.name}")
            symlinks_skipped += 1
            continue

        original_suffix_lower = f.suffix.lower()

        # Skip if already has the target extension (original logic)
        if original_suffix_lower == config.new_extension.lower():
            # console.print(f"[dim]Skipped (already has target extension):[/dim] {f.name}") # Keep console clean maybe
            already_done_skipped += 1
            continue

        # Apply source extension filter (original logic)
        if source_ext_filter is None or original_suffix_lower in source_ext_filter:
            files_to_process.append(f)

    # Early exit if nothing to process (modified)
    if not files_to_process:
        console.print(
            "[yellow]No files found matching criteria to change extension.[/yellow]"
        )
        # Report skipped counts even if no files are processed further
        if already_done_skipped > 0:
            console.print(
                f"[dim]Files skipped (already have target extension): {already_done_skipped}[/dim]"
            )
        if symlinks_skipped > 0:
            console.print(f"[dim]Symbolic links skipped: {symlinks_skipped}[/dim]")
        return 0

    processed_count = 0
    skipped_conflicts = 0
    skipped_errors = 0

    # --- Confirmation Prompt (NEW) ---
    if not dry_run and not yes:
        console.print("\n--- Proposed Changes ---")
        preview_count = 0
        for file_obj in files_to_process:
            if preview_count >= 5:
                break
            preview_name = file_obj.stem + config.new_extension
            console.print(f"- {file_obj.name} → {preview_name}")
            preview_count += 1
        if len(files_to_process) > 5:
            console.print(f"- ... and {len(files_to_process) - 5} more file(s)")

        console.print(
            f"\nAbout to change extension to '{config.new_extension}' for {len(files_to_process)} file(s) in '{config.folder}'"
            f"{f' saving to directory {target_dir}' if config.output_dir else ''}."
        )
        if force:
            console.print(
                "[yellow]--force specified: Existing target files WILL be overwritten![/yellow]"
            )
        if not click.confirm("Proceed with changing extensions?"):
            console.print("[yellow]Operation cancelled by user.[/yellow]")
            return 0
    # --- End Confirmation ---

    # Main processing loop (modified)
    for file_obj in files_to_process:
        # Construct the new name and path (original logic)
        new_name = file_obj.stem + config.new_extension
        new_path = target_dir / new_name

        # --- Conflict Check (modified for --force) ---
        if new_path.exists() and new_path != file_obj:  # Check potential conflict
            if not force:  # If not forcing, skip
                console.print(
                    f"[yellow]Skipped (target exists):[/yellow] {file_obj.name} → {new_name} in {target_dir.name}"
                )
                skipped_conflicts += 1
                continue
            else:  # If forcing, warn and proceed
                console.print(
                    f"[yellow]--force specified: Overwriting existing file {new_path.name}[/yellow]"
                )
        # --- End Conflict Check ---

        # --- Perform Action (modified for dry_run, force, error handling) ---
        if dry_run:  # Original dry_run logic
            action_prefix = "[yellow][DRY RUN][/yellow]"
            console.print(f"{action_prefix} {file_obj.name} → {new_name}")
            processed_count += 1
        else:  # Apply changes
            action_prefix = "[green]Changed:[/green]"
            try:
                # Use shutil.move if changing directory OR overwriting, otherwise Path.rename (modified logic)
                if config.output_dir or (force and new_path.exists()):
                    shutil.move(str(file_obj), str(new_path))
                else:
                    file_obj.rename(new_path)

                processed_count += 1
                console.print(f"{action_prefix} {file_obj.name} → {new_name}")

            except PermissionError as e:  # Original error handling
                console.print(
                    f"[red]Permission denied (skipped):[/red] {file_obj.name} → {new_name} ({e})"
                )
                skipped_errors += 1
                continue
            except FileExistsError:  # Original error handling (race condition)
                console.print(f"[red]File already exists (skipped):[/red] {new_name}")
                skipped_conflicts += 1
                continue
            except Exception as e:  # Original error handling
                console.print(f"[red]Error processing {file_obj.name}:[/red] {str(e)}")
                skipped_errors += 1
                continue
        # --- End Perform Action ---

    # --- Consistent Summary (modified) ---
    console.print("\n--- Change Extension Summary ---")
    if dry_run:
        console.print(f"Files previewed for extension change: {processed_count}")
    else:
        console.print(f"Files extension changed successfully: {processed_count}")

    # Report skipped counts only if they occurred
    if skipped_conflicts > 0:
        console.print(f"Files skipped (due to target conflicts): {skipped_conflicts}")
    if skipped_errors > 0:
        console.print(f"Files skipped (due to errors): {skipped_errors}")
    if already_done_skipped > 0:
        console.print(
            f"Files skipped (already have target extension): {already_done_skipped}"
        )
    if symlinks_skipped > 0:
        console.print(f"Symbolic links skipped: {symlinks_skipped}")
    # --- End Summary ---

    return processed_count
