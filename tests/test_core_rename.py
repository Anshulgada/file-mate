import pytest
from pathlib import Path
from filemate.core.rename import rename_files, RenameConfig
from filemate.utils.test_helpers import create_test_files


# === Test Cases ===


def test_basic_rename(tmp_path: Path) -> None:
    _ = create_test_files(tmp_path, 3)
    config = RenameConfig(folder=tmp_path, pattern="renamed_{i}")
    count = rename_files(config)
    renamed = list(tmp_path.glob("renamed_*.txt"))

    assert count == 3
    assert len(renamed) == 3
    for f in renamed:
        assert f.exists()


def test_rename_with_extension_filter(tmp_path: Path) -> None:
    create_test_files(tmp_path, 2, ext=".txt")
    create_test_files(tmp_path, 2, ext=".jpg")
    config = RenameConfig(folder=tmp_path, pattern="filtered_{i}", ext=".jpg")
    count = rename_files(config)
    jpg_files = list(tmp_path.glob("filtered_*.jpg"))

    assert count == 2
    assert all(f.suffix == ".jpg" for f in jpg_files)


def test_rename_with_start_index(tmp_path: Path) -> None:
    create_test_files(tmp_path, 2)
    config = RenameConfig(folder=tmp_path, pattern="file_{i}", start=10)
    rename_files(config)
    expected_names = ["file_10.txt", "file_11.txt"]
    actual_names = sorted([f.name for f in tmp_path.glob("file_*.txt")])

    assert actual_names == expected_names


def test_rename_to_output_dir(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    create_test_files(input_dir, 2)

    config = RenameConfig(folder=input_dir, pattern="moved_{i}", output_dir=output_dir)
    count = rename_files(config)

    assert count == 2
    assert len(list(output_dir.iterdir())) == 2
    assert all(f.name.startswith("moved_") for f in output_dir.iterdir())


def test_rename_fails_on_invalid_dir(tmp_path: Path) -> None:
    fake_folder = tmp_path / "nonexistent"
    with pytest.raises(ValueError, match="is not a valid directory"):
        RenameConfig(folder=fake_folder)


def test_rename_handles_filename_conflict(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Create a conflict file in the output dir
    conflict_file = output_dir / "file_0.txt"
    conflict_file.write_text("already exists")

    # Create test files in the input dir
    create_test_files(input_dir, 1)  # creates sample_0.txt

    config = RenameConfig(folder=input_dir, pattern="file_{i}", output_dir=output_dir)
    renamed_count = rename_files(config)

    assert renamed_count == 1
    assert (output_dir / "file_1.txt").exists()  # skips file_0.txt which exists


def test_rename_conflict_renames_with_increment(tmp_path: Path) -> None:
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    # Simulate file_0.txt already exists in output
    (output_dir / "file_0.txt").write_text("existing")

    # Add a file to rename
    create_test_files(input_dir, 1)  # creates sample_0.txt

    config = RenameConfig(folder=input_dir, pattern="file_{i}", output_dir=output_dir)

    renamed_count = rename_files(config)

    assert renamed_count == 1
    # file_0.txt was already there, so renamed as file_1.txt
    assert not (output_dir / "file_0.txt").stat().st_size == 0
    assert (output_dir / "file_1.txt").exists()
    assert (output_dir / "file_1.txt").stat().st_size > 0
