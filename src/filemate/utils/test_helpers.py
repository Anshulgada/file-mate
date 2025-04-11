from pathlib import Path


def create_test_files(dir_path: Path, count: int, ext: str = ".txt") -> list[Path]:
    files = []
    for i in range(count):
        file_path = dir_path / f"sample_{i}{ext}"
        file_path.write_text("test")
        files.append(file_path)
    return files
