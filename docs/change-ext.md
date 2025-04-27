# File Extension Changer (`change-ext`)

## Overview

The `change-ext` command allows you to change file extensions for multiple files in a directory. This is useful for batch renaming files when you need to convert between different file formats or standardize extensions across a collection of files.

## Usage

```bash
filemate file change-ext [OPTIONS] FOLDER
```

## Arguments

- `FOLDER`: Path to the directory containing files whose extensions you want to change.

## Options

- `--to TEXT` (required): The target file extension (e.g., '.txt', 'png', 'jpeg'). The leading dot is optional.

- `--from TEXT`: Optional comma-separated list of source extensions to change (e.g., '.jpg,.jpeg' or 'txt'). If omitted, the command will process all files in the directory.

- `--output-dir, -o PATH`: Optional directory to save files with changed extensions. If not specified, files will be renamed in place.

- `--yes, -y`: Skip the confirmation prompt before changing extensions. Useful for scripting or batch operations.

- `--force, -f`: Force overwrite if a file with the target name already exists. Without this flag, files with naming conflicts will be skipped.

- `--dry-run`: Preview the changes without modifying any files. Shows what would happen without making actual changes.

## Examples

### Basic Usage

Change all .txt files to .md files in the current directory:

```bash
filemate file change-ext . --from txt --to md
```

### Change Multiple Extensions to One

Change both .jpg and .jpeg files to .webp:

```bash
filemate file change-ext ./images --from jpg,jpeg --to webp
```

### Change All Files to One Extension

Change all files in a directory to .bak (backup) files:

```bash
filemate file change-ext ./documents --to bak
```

### Save to Different Directory

Change extensions and save to a different directory:

```bash
filemate file change-ext ./source --from txt --to md --output-dir ./converted
```

### Skip Confirmation

Change extensions without confirmation prompt:

```bash
filemate file change-ext ./logs --from log --to txt --yes
```

### Force Overwrite

Change extensions and overwrite any existing files with the same name:

```bash
filemate file change-ext ./data --from csv --to xlsx --force
```

### Preview Changes

Preview what changes would be made without actually changing any files:

```bash
filemate file change-ext ./photos --from jpg --to png --dry-run
```

## Behavior Notes

- Files that already have the target extension are automatically skipped.
- Symbolic links in the source directory are skipped to prevent potential issues.
- By default, the command will prompt for confirmation before making changes.
- If a file with the target name already exists, it will be skipped unless `--force` is specified.
- The command provides a summary of actions taken, including counts of changed files and skipped files.

## Error Handling

The command handles several error conditions:

- If the source directory doesn't exist, an error is displayed.
- If the output directory doesn't exist, it will be created automatically.
- Permission errors are handled gracefully, with affected files being skipped.
- Conflicts (existing files with the target name) are detected and reported.

## Use Cases

1. **Format Migration**: Convert files from one format to another (e.g., .txt to .md).
2. **Backup Creation**: Create backup copies of files with .bak extension.
3. **Standardization**: Normalize file extensions across a project or collection.
4. **Preparation for Processing**: Change extensions before processing files with tools that expect specific extensions.
5. **Testing File Handlers**: Use with `--dry-run` to test how file handlers would process files with different extensions.

## Tips

- Use `--dry-run` first to preview changes before committing them.
- For batch processing across many directories, combine with shell scripts and use the `--yes` flag.
- When dealing with important files, consider using `--output-dir` to keep originals intact.
- The `--force` option should be used with caution as it can overwrite existing files.
