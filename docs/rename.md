# `filemate file rename`

Renames files within a specified directory based on a sequential pattern.

This command processes files in alphanumeric sorted order and allows you to customize the renaming pattern, filter by file extension, set a starting number, and optionally move the renamed files to a different directory.

## Usage

```bash
filemate file rename [OPTIONS] FOLDER
```

## Arguments

*   `FOLDER` _(required)_: The path to the directory containing the files you want to rename. This directory must exist.

## Options

*   `--pattern TEXT`:
    *   Specifies the pattern for the new filenames.
    *   Must include the placeholder `{i}` which will be replaced by the sequential index number.
    *   Supports format specifiers like `{i:03d}` for zero-padded numbers.
    *   _Default_: `"file_{i}"`

*   `--ext TEXT`:
    *   Filters the files to be renamed based on their extension(s).
    *   Provide a comma-separated list of extensions (e.g., `.jpg,.png` or `jpg,png`). Leading dots are optional and will be added automatically.
    *   If omitted, all files in the `FOLDER` are considered for renaming.
    *   _Examples_: `jpg,png,gif`, `.txt`, `jpeg`
    *   _Default_: `None`

*   `--start INTEGER`:
    *   Sets the starting index number for the `{i}` placeholder in the pattern.
    *   Must be an integer greater than or equal to 1.
    *   _Default_: `1`

*   `--output-dir PATH`, `-o PATH`:
    *   Specifies an alternative directory where the renamed files should be saved (moved).
    *   If the directory does not exist, it will be created automatically.
    *   If omitted, files are renamed within the original `FOLDER`.
    *   _Default_: `None`

*   `--yes`, `-y`:
    *   Skips the confirmation prompt before renaming files.
    *   Useful for batch operations or scripts where manual confirmation is not desired.
    *   _Flag_: `--yes` or `-y`

*   `--force`, `-f`:
    *   Forces overwrite if target filename exists during conflict resolution.
    *   Use with caution as it will replace existing files without warning.
    *   _Flag_: `--force` or `-f`

*   `--source-prefix TEXT`:
    *   Filters files to be renamed based on their filename prefix.
    *   Only files whose names start with the specified prefix will be processed.
    *   Useful for targeting specific groups of files (e.g., `IMG_` for camera images).
    *   _Default_: `None`

*   `--dry-run`:
    *   Performs a simulation of the renaming process without actually changing any files.
    *   Prints the intended changes to the console (e.g., `[DRY RUN] old_name.txt → new_name_1.txt`).
    *   Useful for previewing the results before applying them.
    *   _Flag_: `--dry-run`

## Behavior

*   **Sorting**: Files within the `FOLDER` are processed in standard alphanumeric sort order before renaming begins.
*   **Conflict Resolution**: If a target filename generated by the pattern already exists (either in the source `FOLDER` or `output-dir`), the command will automatically increment the index `{i}` and try the next number (e.g., if `file_1.txt` exists, it will try `file_2.txt`). It will attempt this up to 10 times (`MAX_RENAME_ATTEMPTS`) for each file before skipping that file with an error message.
*   With the `--force` or `-f` option, existing files will be overwritten instead of attempting conflict resolution.
*   **Confirmation**: By default, you will be asked to confirm before renaming files. Use the `--yes` or `-y` option to skip this confirmation step.
*   **Error Handling**:
    *   Files skipped due to persistent naming conflicts are reported.
    *   Files skipped due to `PermissionError` during the rename operation are reported.
    *   Other unexpected errors during renaming are reported, and the specific file is skipped.
    *   Symbolic links in the source directory are skipped.
*   **Output**: The command uses `rich` to display progress and the outcome of each file operation (Renamed, Dry Run, Skipped/Error) in the console.

## Examples

1.  **Basic Usage:** Rename all files in `photos` folder with the pattern `vacation_{i}`.
    ```bash
    filemate file rename photos --pattern "vacation_{i}"
    # Result: file1.jpg -> vacation_1.jpg, file2.png -> vacation_2.png, etc.
    ```

2.  **Filter by Prefix:** Rename only files starting with "IMG_" in the `camera` folder.
    ```bash
    filemate file rename camera --pattern "photo_{i}" --source-prefix "IMG_"
    # Result: IMG_1234.jpg -> photo_1.jpg, IMG_5678.png -> photo_2.png, etc.
    ```

3.  **Basic Rename:** Rename all `.txt` files in `my_docs` starting from 1, using the default pattern `file_{i}`.
    ```bash
    filemate file rename my_docs --ext .txt
    # Example result: report.txt -> file_1.txt, summary.txt -> file_2.txt
    ```

4.  **Custom Pattern and Start Index:** Rename `.jpg` images in `vacation_pics` to `Vacation_{i}.jpg`, starting the numbering from 100.
    ```bash
    filemate file rename vacation_pics --pattern "Vacation_{i}" --start 100 --ext .jpg
    # Example result: IMG_001.jpg -> Vacation_100.jpg, IMG_002.jpg -> Vacation_101.jpg
    ```

5.  **Multiple Extensions and Output Directory:** Rename `.png` and `.gif` files from `source_images` into a new directory `processed_images`, using the pattern `image_{i}`.
    ```bash
    filemate file rename source_images --ext png,gif --pattern "image_{i}" --output-dir processed_images
    # Result: Renamed png/gif files moved to processed_images/image_1.*, processed_images/image_2.* etc.
    # processed_images directory is created if it doesn't exist.
    ```

6.  **Dry Run:** Preview renaming all files in `downloads` folder with the pattern `download_{i}` without making changes.
    ```bash
    filemate file rename downloads --pattern "download_{i}" --dry-run
    # Output will show "[DRY RUN] old_name.ext -> download_1.ext", etc.
    ```

7.  **Combining Options:** Rename `.jpeg` and `.jpg` files in `camera_roll`, starting from 50, moving them to `sorted_photos`, using pattern `Photo_{i}`.
    ```bash
    filemate file rename camera_roll -o sorted_photos --ext jpeg,jpg --start 50 --pattern "Photo_{i}"
    # Result: Renamed jpeg/jpg files moved to sorted_photos/Photo_50.*, sorted_photos/Photo_51.* etc.
    ```

8.  **Skip Confirmation:** Rename all files in `documents` folder without confirmation prompt.
    ```bash
    filemate file rename documents --pattern "doc_{i}" --yes
    # Files will be renamed without asking for confirmation
    ```

9.  **Force Overwrite:** Rename files in `photos` folder, overwriting any existing files with the same name.
    ```bash
    filemate file rename photos --pattern "photo_{i}" --force
    # Existing files will be overwritten if name conflicts occur
    ```

10. **Combined Filtering:** Rename only files starting with "DSC_" and having ".jpg" extension in the `vacation` folder, using a custom pattern with zero-padding, and skipping confirmation.
    ```bash
    filemate file rename vacation --pattern "hawaii_{i:03d}" --source-prefix "DSC_" --ext jpg --yes
    # Result: DSC_1234.jpg -> hawaii_001.jpg, DSC_5678.jpg -> hawaii_002.jpg, etc.
    # Other files like IMG_1234.jpg or DSC_1234.png will be ignored
    ```
