from pathlib import Path


def ensure_directory(folder: Path) -> Path:
    """
    Ensure the provided path is an existing directory.

    :param folder: Path to validate.
    :type folder: Path
    :return: The same folder path if valid.
    :rtype: Path
    :raises ValueError: If the path is not a directory or doesn't exist.
    """
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"{folder} is not a valid directory.")
    return folder
