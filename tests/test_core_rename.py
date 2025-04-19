import pytest
import unittest
from pathlib import Path
from unittest.mock import patch  # Import patch for better permission test

from filemate.core.rename import rename_files, RenameConfig
from filemate.utils.test_helpers import create_test_files


# === Test Cases ===


def test_basic_rename(tmp_path: Path) -> None:
    # Setup: Create 3 test files
    create_test_files(tmp_path, 3)
    config = RenameConfig(folder=tmp_path, pattern="renamed_{i}")

    # Action: Rename files
    count = rename_files(config)

    # Assert: Check count and existence of renamed files
    renamed = list(tmp_path.glob("renamed_*.txt"))
    assert count == 3
    assert len(renamed) == 3
    for f in renamed:
        assert f.exists()


def test_rename_with_extension_filter(tmp_path: Path) -> None:
    # Setup: Create files with different extensions
    create_test_files(tmp_path, 2, ext=".txt")
    create_test_files(tmp_path, 2, ext=".jpg")
    config = RenameConfig(folder=tmp_path, pattern="filtered_{i}", extensions=[".jpg"])

    # Action: Rename only .jpg files
    count = rename_files(config)

    # Assert: Check count and that only .jpg files were renamed
    jpg_files = list(tmp_path.glob("filtered_*.jpg"))
    txt_files = list(tmp_path.glob("sample_*.txt"))  # Original .txt files should remain
    assert count == 2
    assert len(jpg_files) == 2
    assert all(f.suffix == ".jpg" for f in jpg_files)
    assert len(txt_files) == 2  # Ensure txt files were not renamed


def test_rename_with_start_index(tmp_path: Path) -> None:
    # Setup: Create test files
    create_test_files(tmp_path, 2)
    config = RenameConfig(folder=tmp_path, pattern="file_{i}", start=10)

    # Action: Rename with custom start index
    count = rename_files(config)

    # Assert: Check count and expected filenames
    expected_names = ["file_10.txt", "file_11.txt"]
    actual_names = sorted([f.name for f in tmp_path.glob("file_*.txt")])
    assert count == 2
    assert actual_names == expected_names


def test_rename_to_output_dir(tmp_path: Path) -> None:
    # Setup: Create input and output directories, add files to input
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    # output_dir is intentionally not created here to test creation
    create_test_files(input_dir, 2)

    config = RenameConfig(folder=input_dir, pattern="moved_{i}", output_dir=output_dir)

    # Action: Rename files into the output directory
    count = rename_files(config)

    # Assert: Check count, output dir creation, and files in output dir
    assert count == 2
    assert output_dir.exists()  # Check if output dir was created
    assert not list(input_dir.iterdir())  # Input directory should be empty
    assert len(list(output_dir.iterdir())) == 2
    assert all(f.name.startswith("moved_") for f in output_dir.iterdir())


def test_rename_fails_on_invalid_dir(tmp_path: Path) -> None:
    # Setup: Define a path to a non-existent directory
    fake_folder = tmp_path / "nonexistent"

    # Action & Assert: Check that initializing RenameConfig raises ValueError
    with pytest.raises(ValueError, match="is not a valid directory"):
        RenameConfig(folder=fake_folder)


def test_rename_handles_filename_conflict(tmp_path: Path) -> None:
    # Setup: Create input/output dirs, create a conflict file in output
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "file_1.txt").write_text(
        "already exists"
    )  # Conflict is file_1.txt now
    create_test_files(input_dir, 1)  # creates sample_0.txt

    # Action: Rename with a pattern that will initially conflict
    config = RenameConfig(
        folder=input_dir, pattern="file_{i}", output_dir=output_dir, start=1
    )
    renamed_count = rename_files(config)

    # Assert: Check count and that the file was renamed to the next available index
    assert renamed_count == 1
    assert (
        output_dir / "file_1.txt"
    ).read_text() == "already exists"  # Original conflict file is untouched
    assert (output_dir / "file_2.txt").exists()  # Renamed to the next index


def test_rename_conflict_renames_with_increment(tmp_path: Path) -> None:
    # Setup: Similar to above, ensure conflict resolution works
    input_dir = tmp_path / "in"
    input_dir.mkdir()
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    (output_dir / "file_1.txt").write_text(
        "existing"
    )  # start=1 default, so conflict is file_1.txt
    create_test_files(input_dir, 1)  # creates sample_0.txt

    # Action: Rename
    config = RenameConfig(
        folder=input_dir, pattern="file_{i}", output_dir=output_dir
    )  # Default start=1
    renamed_count = rename_files(config)

    # Assert: Check count and that the new file got the incremented name
    assert renamed_count == 1
    assert (
        output_dir / "file_1.txt"
    ).read_text() == "existing"  # Original conflict file
    assert (output_dir / "file_2.txt").exists()  # Renamed to next available index
    assert (output_dir / "file_2.txt").stat().st_size > 0


# === New Tests ===


# Use mocking for a more reliable permission error test
@patch(
    "pathlib.Path.rename",
    side_effect=PermissionError("Test permission denied, file cannot be renamed!"),
)
def test_rename_with_permission_error(
    mock_rename: unittest.mock.MagicMock, tmp_path: Path
) -> None:
    """
    Test renaming skips file and returns count 0 when PermissionError occurs.
    Uses mocking to reliably simulate the error.
    """
    # Setup: Create a directory and a file within it
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    file_path = create_test_files(input_dir, 1)[0]  # Creates sample_0.txt

    # Configure renaming
    config = RenameConfig(folder=input_dir, pattern="file_{i}")

    # Action: Try renaming files (mocked rename will raise PermissionError)
    renamed_count = rename_files(config)

    # Assert: Check that no files were counted as renamed and the original file still exists
    assert renamed_count == 0
    assert mock_rename.called  # Ensure our mock was actually triggered
    assert file_path.exists()  # The original file should still be there
    assert not (input_dir / "file_1.txt").exists()  # The target rename should not exist


def test_rename_with_file_existence_error(tmp_path: Path) -> None:
    """
    Test renaming correctly skips over a pre-existing file and renames to the next index.
    """
    # Setup: Create input/output, add a conflicting file to output
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    conflict_file_path = (
        output_dir / "file_1.txt"
    )  # Default start=1 conflicts with file_1.txt
    conflict_file_path.write_text("existing file")
    original_input_file = create_test_files(input_dir, 1)[0]  # sample_0.txt

    # Action: Rename files
    config = RenameConfig(
        folder=input_dir, pattern="file_{i}", output_dir=output_dir
    )  # Default start=1
    renamed_count = rename_files(config)

    # Assert: Check count, existence of the new file, and that the original conflict file remains untouched
    assert renamed_count == 1
    assert (output_dir / "file_2.txt").exists()  # Renamed to next available index
    assert (
        conflict_file_path.exists()
    )  # **** FIXED ASSERTION **** Ensure the original conflict file still exists
    assert (
        conflict_file_path.read_text() == "existing file"
    )  # Verify content wasn't changed
    assert (
        not original_input_file.exists()
    )  # Original input file should be gone (moved)


def test_rename_with_max_attempts(tmp_path: Path) -> None:
    """
    Test renaming correctly finds the next available index when multiple conflicts exist.
    """
    # Setup: Create input/output, add multiple conflicting files to output
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    # Simulate conflicts for file_1.txt, file_2.txt, file_3.txt (assuming start=1)
    for i in range(1, 4):  # Create conflicts for indices 1, 2, 3
        (output_dir / f"file_{i}.txt").write_text(f"existing file {i}")
    create_test_files(input_dir, 1)  # creates sample_0.txt

    # Action: Rename files
    config = RenameConfig(
        folder=input_dir, pattern="file_{i}", output_dir=output_dir
    )  # Default start=1
    renamed_count = rename_files(config)

    # Assert: Check count and that the file was renamed to the first available index (4)
    assert renamed_count == 1
    assert (output_dir / "file_4.txt").exists()  # Should be renamed to file_4.txt
    # Verify original conflict files still exist
    assert (output_dir / "file_1.txt").exists()
    assert (output_dir / "file_2.txt").exists()
    assert (output_dir / "file_3.txt").exists()


def test_rename_dry_run(tmp_path: Path) -> None:
    """
    Test the dry-run feature ensures no actual renaming occurs.
    """
    # Setup: Create input directory and files
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    original_files = create_test_files(input_dir, 2)  # sample_0.txt, sample_1.txt

    # Action: Perform dry run
    config = RenameConfig(folder=input_dir, pattern="file_{i}")
    renamed_count = rename_files(config, dry_run=True)

    # Assert: Check count is 0 and original files remain unchanged
    assert renamed_count == 0
    assert all(f.exists() for f in original_files)  # Original files still exist
    assert all(
        f.name.startswith("sample_") for f in input_dir.iterdir()
    )  # Names unchanged
    assert not list(input_dir.glob("file_*.txt"))  # No files with the new pattern exist


def test_rename_invalid_start_index(tmp_path: Path) -> None:
    """
    Test configuration raises ValueError for start index less than 1.
    """
    # Action & Assert: Check ValueError on config initialization
    with pytest.raises(
        ValueError, match="Start index must be greater than or equal to 1"
    ):
        RenameConfig(
            folder=tmp_path, pattern="file_{i}", start=0
        )  # Use tmp_path directly, must exist


def test_rename_output_dir_creation(tmp_path: Path) -> None:
    """
    Test that the output directory is automatically created if it doesn't exist.
    """
    # Setup: Create input dir, define non-existent output dir, create input files
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"  # Does not exist yet
    create_test_files(input_dir, 2)

    # Action: Rename files, specifying the non-existent output directory
    config = RenameConfig(folder=input_dir, pattern="file_{i}", output_dir=output_dir)
    renamed_count = rename_files(config)

    # Assert: Check count, existence of output dir, and renamed files within it
    assert renamed_count == 2
    assert output_dir.exists()  # Output directory should have been created
    assert output_dir.is_dir()
    assert len(list(output_dir.iterdir())) == 2
    assert all(f.name in ["file_1.txt", "file_2.txt"] for f in output_dir.iterdir())


def test_rename_without_extension_filter(tmp_path: Path) -> None:
    """
    Test renaming works correctly when no extension filter is provided.
    """
    # Setup: Create files with the same extension
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    create_test_files(
        input_dir, 3, ext=".log"
    )  # sample_0.log, sample_1.log, sample_2.log

    # Action: Rename without specifying extensions
    config = RenameConfig(folder=input_dir, pattern="log_{i}")
    renamed_count = rename_files(config)

    # Assert: Check count and that all files were renamed
    assert renamed_count == 3
    renamed_files = list(input_dir.glob("log_*.log"))
    assert len(renamed_files) == 3
    assert all(f.name in ["log_1.log", "log_2.log", "log_3.log"] for f in renamed_files)
