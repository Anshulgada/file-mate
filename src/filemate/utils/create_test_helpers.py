from pathlib import Path
from typing import List


def create_test_files(
    dir_path: Path,
    count: int,
    ext: str = ".txt",
    base_name: str = "sample",  # Add optional base_name parameter with default
) -> List[Path]:
    """
    Creates a specified number of test files in a directory.

    :param dir_path: The directory Path object where files will be created.
    :param count: The number of files to create.
    :param ext: The file extension to use (defaults to '.txt'). Ensure it includes the dot.
    :param base_name: The base name for the files before the index (defaults to 'sample').
    :return: A list of Path objects for the created files.
    """
    files = []
    for i in range(count):
        # Use the base_name parameter in the f-string
        file_path = dir_path / f"{base_name}_{i}{ext}"
        file_path.write_text(
            f"test content for {base_name}_{i}{ext}"
        )  # Added context to content
        files.append(file_path)
    return files
