import pytest
import sys  # For skipping symlink test on windows
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock  # Import patch for better permission test

from filemate.core.rename import rename_files, RenameConfig
from filemate.utils.create_test_helpers import create_test_files
from filemate.utils.test_output_checker import OutputChecker


# === Test Cases ===


@pytest.mark.rename
def test_basic_rename(tmp_path: Path) -> None:
    # Setup: Create 3 test files
    create_test_files(tmp_path, 3)
    config = RenameConfig(folder=tmp_path, pattern="renamed_{i}")

    # Action: Rename files
    count = rename_files(config, yes=True)

    # Assert: Check count and existence of renamed files
    renamed = list(tmp_path.glob("renamed_*.txt"))
    assert count == 3
    assert len(renamed) == 3
    for f in renamed:
        assert f.exists()
    assert all(
        f.name in ["renamed_1.txt", "renamed_2.txt", "renamed_3.txt"] for f in renamed
    )


@pytest.mark.rename
def test_rename_with_extension_filter(tmp_path: Path) -> None:
    # Setup: Create files with different extensions
    create_test_files(tmp_path, 2, ext=".txt")
    create_test_files(tmp_path, 2, ext=".jpg")
    config = RenameConfig(folder=tmp_path, pattern="filtered_{i}", extensions=[".jpg"])

    # Action: Rename only .jpg files
    count = rename_files(config, yes=True)

    # Assert: Check count and that only .jpg files were renamed
    jpg_files = list(tmp_path.glob("filtered_*.jpg"))
    txt_files = list(tmp_path.glob("sample_*.txt"))  # Original .txt files should remain
    assert count == 2
    assert len(jpg_files) == 2
    assert all(f.suffix == ".jpg" for f in jpg_files)
    assert len(txt_files) == 2  # Ensure txt files were not renamed


@pytest.mark.rename
def test_rename_with_start_index(tmp_path: Path) -> None:
    # Setup: Create test files
    create_test_files(tmp_path, 2)
    config = RenameConfig(folder=tmp_path, pattern="file_{i}", start=10)

    # Action: Rename with custom start index
    count = rename_files(config, yes=True)

    # Assert: Check count and expected filenames
    expected_names = ["file_10.txt", "file_11.txt"]
    actual_names = sorted([f.name for f in tmp_path.glob("file_*.txt")])
    assert count == 2
    assert actual_names == expected_names


@pytest.mark.rename
def test_rename_to_output_dir(tmp_path: Path) -> None:
    # Setup: Create input and output directories, add files to input
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    # output_dir is intentionally not created here to test creation
    create_test_files(input_dir, 2)

    config = RenameConfig(folder=input_dir, pattern="moved_{i}", output_dir=output_dir)

    # Action: Rename files into the output directory
    count = rename_files(config, yes=True)

    # Assert: Check count, output dir creation, and files in output dir
    assert count == 2
    assert output_dir.exists()  # Check if output dir was created
    assert not list(input_dir.iterdir())  # Input directory should be empty
    assert len(list(output_dir.iterdir())) == 2
    assert all(f.name.startswith("moved_") for f in output_dir.iterdir())


@pytest.mark.rename
def test_rename_fails_on_invalid_dir(tmp_path: Path) -> None:
    # Setup: Define a path to a non-existent directory
    fake_folder = tmp_path / "nonexistent"

    # Action & Assert: Check that initializing RenameConfig raises ValueError
    with pytest.raises(ValueError, match="is not a valid directory"):
        RenameConfig(folder=fake_folder)


@pytest.mark.rename
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
    renamed_count = rename_files(config, yes=True)

    # Assert: Check count and that the file was renamed to the next available index
    assert renamed_count == 1
    assert (
        output_dir / "file_1.txt"
    ).read_text() == "already exists"  # Original conflict file is untouched
    assert (output_dir / "file_2.txt").exists()  # Renamed to the next index


@pytest.mark.rename
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
    renamed_count = rename_files(config, yes=True)

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
@pytest.mark.rename
def test_rename_with_permission_error(
    mock_rename: unittest.mock.MagicMock, tmp_path: Path, capsys: MagicMock
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
    renamed_count = rename_files(config, yes=True)

    # Use OutputChecker instead of raw capsys
    output = OutputChecker(capsys)

    # Assert: Check that no files were counted as renamed and the original file still exists
    assert renamed_count == 0
    assert mock_rename.called  # Ensure our mock was actually triggered
    assert file_path.exists()  # The original file should still be there
    assert not (input_dir / "file_1.txt").exists()  # The target rename should not exist

    # Use regex matching to handle potential duplicated output in test environment
    output.assert_contains(
        [
            "Permission denied \(skipped\): sample_0.txt → file_1.txt",
            "Files renamed successfully: 0",
            "Files skipped \(due to errors\): 1",
        ],
        regex=True,
    )


@pytest.mark.rename
def test_rename_with_file_existence_error(tmp_path: Path, capsys: MagicMock) -> None:
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
    renamed_count = rename_files(config, yes=True)

    # Use OutputChecker for console output verification
    output = OutputChecker(capsys)

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

    # Add assertions for console output
    output.assert_contains(
        ["Renamed:", "sample_0.txt → file_2.txt", "Files renamed successfully: 1"]
    )


@pytest.mark.rename
def test_rename_with_max_attempts(tmp_path: Path, capsys: MagicMock) -> None:
    """
    Test renaming correctly finds the next available index when multiple conflicts exist.
    """
    # Setup: Create input/output, add multiple conflicting files to output
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    # Simulate conflicts for file_1.txt, file_2.txt, file_3.txt (assuming start=1)
    for i in range(
        1, 12
    ):  # Create conflicts for indices 1 through 11 (more than MAX_RENAME_ATTEMPTS=10)
        (output_dir / f"file_{i}.txt").write_text(f"existing file {i}")
    # for i in range(1, 4):  # Create conflicts for indices 1, 2, 3
    #     (output_dir / f"file_{i}.txt").write_text(f"existing file {i}")
    create_test_files(input_dir, 1)  # creates sample_0.txt

    # Action: Rename files
    config = RenameConfig(
        folder=input_dir, pattern="file_{i}", output_dir=output_dir
    )  # Default start=1
    renamed_count = rename_files(config, yes=True)

    # Use OutputChecker instead of raw capsys
    output = OutputChecker(capsys)

    assert renamed_count == 0  # Should skip after max attempts
    assert not (output_dir / "file_12.txt").exists()  # Check beyond max attempts
    assert (output_dir / "file_1.txt").exists()  # Originals exist
    assert (input_dir / "sample_0.txt").exists()  # Original source exists

    # Use assert_contains for more reliable assertions
    output.assert_contains(["Error: Could not rename sample_0.txt"])


@pytest.mark.rename
def test_rename_dry_run(tmp_path: Path, capsys: MagicMock) -> None:
    """
    Test the dry-run feature ensures no actual renaming occurs.
    """
    # Setup: Create input directory and files
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    original_files = create_test_files(input_dir, 2)  # sample_0.txt, sample_1.txt

    # Action: Perform dry run
    config = RenameConfig(folder=input_dir, pattern="file_{i}")

    # Action: Perform dry run (yes=True is irrelevant for dry run confirmation)
    preview_count = rename_files(config, dry_run=True, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert: Check count returned is preview count and files remain unchanged
    assert preview_count == 2  # Function should return previewed count in dry_run
    assert all(f.exists() for f in original_files)  # Original files still exist
    assert all(
        f.name.startswith("sample_") for f in input_dir.iterdir()
    )  # Names unchanged
    assert not list(input_dir.glob("file_*.txt"))  # No files with the new pattern exist

    # Add assertions for console output
    output.assert_contains(
        [
            "[DRY RUN]",
            "sample_0.txt → file_1.txt",
            "sample_1.txt → file_2.txt",
            "Files previewed for rename: 2",
        ]
    )


@pytest.mark.rename
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


@pytest.mark.rename
def test_rename_output_dir_creation(tmp_path: Path, capsys: MagicMock) -> None:
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
    renamed_count = rename_files(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert: Check count, existence of output dir, and renamed files within it
    assert renamed_count == 2
    assert output_dir.exists()  # Output directory should have been created
    assert output_dir.is_dir()
    assert len(list(output_dir.iterdir())) == 2
    assert all(f.name in ["file_1.txt", "file_2.txt"] for f in output_dir.iterdir())

    # Add assertions for console output
    output.assert_contains(
        [
            "Created output directory:",
            "output",
            "Renamed:",
            "Files renamed successfully: 2",
        ]
    )


@pytest.mark.rename
def test_rename_without_extension_filter(tmp_path: Path, capsys: MagicMock) -> None:
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
    renamed_count = rename_files(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert: Check count and that all files were renamed
    assert renamed_count == 3
    renamed_files = list(input_dir.glob("log_*.log"))
    assert len(renamed_files) == 3
    assert all(f.name in ["log_1.log", "log_2.log", "log_3.log"] for f in renamed_files)

    # Add assertions for console output
    output.assert_contains(
        [
            "Renamed:",
            "sample_0.log → log_1.log",
            "sample_1.log → log_2.log",
            "sample_2.log → log_3.log",
            "Files renamed successfully: 3",
        ]
    )


# --- NEW TESTS for --yes, --force, symlinks ---


@pytest.mark.rename
@patch("filemate.core.rename.click.confirm")
def test_rename_confirm_prompt_yes_input(
    mock_confirm: MagicMock, tmp_path: Path, capsys: MagicMock
) -> None:
    """Test confirmation prompt proceeds if user inputs yes."""
    create_test_files(tmp_path, 1)  # sample_0.txt
    mock_confirm.return_value = True  # Simulate user confirming
    config = RenameConfig(folder=tmp_path, pattern="new_{i}")

    # Action: Call WITHOUT yes=True to trigger prompt
    count = rename_files(config, yes=False)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    mock_confirm.assert_called_once()  # Check prompt was shown
    assert count == 1
    assert (tmp_path / "new_1.txt").exists()
    assert not (tmp_path / "sample_0.txt").exists()

    # Add assertions for console output
    output.assert_contains(
        [
            "Proposed Changes",
            "sample_0.txt → new_1.txt",
            "Renamed:",
            "Files renamed successfully: 1",
        ]
    )


@pytest.mark.rename
@patch("filemate.core.rename.click.confirm")
def test_rename_confirm_prompt_no_input(
    mock_confirm: MagicMock, tmp_path: Path, capsys: MagicMock
) -> None:
    """Test confirmation prompt cancels if user inputs no."""
    create_test_files(tmp_path, 1)
    mock_confirm.return_value = False  # Simulate user cancelling
    config = RenameConfig(folder=tmp_path, pattern="new_{i}")

    # Action: Call WITHOUT yes=True
    count = rename_files(config, yes=False)  # Explicitly yes=False

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    mock_confirm.assert_called_once()  # Check prompt was shown
    assert count == 0  # Should return 0 when cancelled
    assert not (tmp_path / "new_1.txt").exists()
    assert (tmp_path / "sample_0.txt").exists()  # Original exists

    # Add assertions for console output
    output.assert_contains(
        ["Proposed Changes", "sample_0.txt → new_1.txt", "Operation cancelled by user"]
    )


@pytest.mark.rename
def test_rename_yes_flag_skips_prompt(tmp_path: Path, capsys: MagicMock) -> None:
    """Test that yes=True flag bypasses the confirmation prompt."""
    create_test_files(tmp_path, 1)
    config = RenameConfig(folder=tmp_path, pattern="new_{i}")

    # Action: Call WITH yes=True
    # We don't need to mock click.confirm, as it shouldn't be called
    count = rename_files(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 1
    assert (tmp_path / "new_1.txt").exists()

    # Add assertions for console output - should NOT contain proposed changes
    output.assert_contains(
        ["Renamed:", "sample_0.txt → new_1.txt", "Files renamed successfully: 1"]
    )
    # Assert that confirmation prompt was skipped
    output.assert_not_contains(["Proposed Changes", "Proceed with renaming?"])


@pytest.mark.rename
def test_rename_force_overwrite_conflict(tmp_path: Path, capsys: MagicMock) -> None:
    """Test force=True overwrites an existing target file."""
    create_test_files(tmp_path, 1, base_name="source", ext=".dat")  # source_0.dat
    (tmp_path / "target_1.dat").write_text("pre-existing data")  # Conflict file

    # Apply extension filter to only process the source file
    config = RenameConfig(
        folder=tmp_path, pattern="target_{i}", start=1, extensions=[".dat"]
    )
    # Action: Call with force=True and yes=True
    count = rename_files(config, yes=True, force=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 1  # Only the .dat file should be processed and counted
    assert not (tmp_path / "source_0.dat").exists()  # Original renamed
    assert (tmp_path / "target_1.dat").exists()  # Conflict file now overwritten
    assert (
        tmp_path / "target_1.dat"
    ).read_text() != "pre-existing data"  # Check content changed

    # Add assertions for console output
    output.assert_contains(
        [
            "--force specified: Overwriting existing file",
            "target_1.dat",
            "Renamed:",
            "source_0.dat → target_1.dat",
            "Files renamed successfully: 1",
        ]
    )


@pytest.mark.rename
def test_rename_no_force_skips_conflict(tmp_path: Path, capsys: MagicMock) -> None:
    """Test force=False (default) skips overwriting an existing target file."""
    create_test_files(tmp_path, 1, base_name="source", ext=".dat")  # source_0.dat
    (tmp_path / "target_1.dat").write_text("pre-existing data")  # Conflict file

    # Apply extension filter to only process the source file
    config = RenameConfig(
        folder=tmp_path, pattern="target_{i}", start=1, extensions=[".dat"]
    )
    # Action: Call with force=False (default) and yes=True
    count = rename_files(config, yes=True, force=False)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 0  # File should be skipped due to conflict
    assert (tmp_path / "source_0.dat").exists()  # Original exists
    assert (
        tmp_path / "target_1.dat"
    ).read_text() == "pre-existing data"  # Conflict unchanged

    # Add assertions for console output
    output.assert_contains(
        [
            "Error: Could not rename source_0.dat",
            "Files renamed successfully: 0",
            "Files skipped (due to naming conflicts): 1",
        ]
    )


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Symlinks require special permissions or handling on Windows",
)
@pytest.mark.rename
def test_rename_skips_symlinks(tmp_path: Path, capsys: MagicMock) -> None:
    """Test that symbolic links are skipped by default."""
    target = tmp_path / "real_file.txt"
    target.write_text("content")
    link = tmp_path / "link_to_file.txt"
    link.symlink_to(target)
    create_test_files(tmp_path, 1, base_name="another")  # another_0.txt

    config = RenameConfig(folder=tmp_path, pattern="processed_{i}")
    count = rename_files(config, yes=True)

    # Use OutputChecker instead of raw capsys
    output = OutputChecker(capsys)

    assert count == 2  # Only real_file and another_0 should be renamed
    assert link.exists() and link.is_symlink()  # Link untouched
    assert link.name == "link_to_file.txt"
    assert (tmp_path / "processed_1.txt").exists()  # another_0.txt renamed
    assert (tmp_path / "processed_2.txt").exists()  # real_file.txt renamed

    # Use assert_contains for more reliable assertions
    output.assert_contains(
        [
            "Skipping symbolic link: link_to_file.txt",
            "Symbolic links skipped: 1",  # Check summary
        ]
    )


# --- NEW TESTS for Pattern Formatting ---


@pytest.mark.rename
def test_rename_pattern_padding(tmp_path: Path, capsys: MagicMock) -> None:
    """Test rename pattern with zero-padding format specifier."""
    create_test_files(tmp_path, 3)  # sample_0.txt, sample_1.txt, sample_2.txt
    (tmp_path / "sample_9.txt").write_text("test 9")  # sample_9.txt
    config = RenameConfig(folder=tmp_path, pattern="img_{i:03d}")  # Pad to 3 digits

    # Action: Use yes=True to bypass prompt
    count = rename_files(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 4
    # Note: Sorting will likely be 1, 10, 2, 3 if sample_9 exists... adjust expectations or setup
    # Let's assume sample_9 is processed last based on name
    expected_files = [
        "img_001.txt",
        "img_002.txt",
        "img_003.txt",
        "img_004.txt",
    ]  # Indices 1,2,3,4 assigned
    actual_files = sorted([p.name for p in tmp_path.glob("img_*.txt")])
    assert actual_files == expected_files
    assert not list(tmp_path.glob("sample_*.txt"))  # Originals are gone

    # Add assertions for console output
    output.assert_contains(["Renamed:", "Files renamed successfully: 4"])


@pytest.mark.rename
def test_rename_pattern_padding_with_start_index(
    tmp_path: Path, capsys: MagicMock
) -> None:
    """Test rename pattern padding works correctly with a non-default start index."""
    create_test_files(tmp_path, 2)  # sample_0.txt, sample_1.txt
    config = RenameConfig(
        folder=tmp_path, pattern="file_{i:04d}", start=98
    )  # Start at 98, pad to 4

    # Action: Use yes=True
    count = rename_files(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 2
    expected_files = ["file_0098.txt", "file_0099.txt"]
    actual_files = sorted([p.name for p in tmp_path.glob("file_*.txt")])
    assert actual_files == expected_files
    assert not list(tmp_path.glob("sample_*.txt"))

    # Add assertions for console output
    output.assert_contains(
        [
            "Renamed:",
            "sample_0.txt → file_0098.txt",
            "sample_1.txt → file_0099.txt",
            "Files renamed successfully: 2",
        ]
    )


@pytest.mark.rename
def test_rename_pattern_invalid_format_specifier(
    tmp_path: Path, capsys: MagicMock
) -> None:
    """Test that an invalid format specifier in the pattern falls back to default formatting."""
    create_test_files(tmp_path, 1)  # sample_0.txt
    # Use an invalid specifier 'x'
    config = RenameConfig(folder=tmp_path, pattern="img_{i:x}")

    # Action: Use yes=True
    count = rename_files(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 1  # File is counted
    # The file is actually being renamed despite the invalid format specifier
    # The format error is handled internally and a default name is used
    assert not (tmp_path / "sample_0.txt").exists()  # Original is renamed
    assert (tmp_path / "img_1.txt").exists()  # Renamed with default formatting

    # Use assert_contains for more reliable assertions
    output.assert_contains(
        [
            "Error applying pattern",
            "Unknown format code 'x'",
            "Files renamed successfully: 0",
            "Files skipped (due to errors): 1",
        ]
    )


@pytest.mark.rename
def test_rename_pattern_with_other_braces(tmp_path: Path, capsys: MagicMock) -> None:
    """Test pattern containing unrelated braces still works with index formatting."""
    create_test_files(tmp_path, 1)  # sample_0.txt
    # Pattern has literal braces {} and formatted index
    config = RenameConfig(folder=tmp_path, pattern="prefix-{{literal}}-{i:02d}")

    # Action: Use yes=True
    count = rename_files(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 1
    expected_name = "prefix-{literal}-01.txt"
    assert (tmp_path / expected_name).exists()
    assert not (tmp_path / "sample_0.txt").exists()

    # Add assertions for console output
    output.assert_contains(
        [
            "Renamed:",
            "sample_0.txt → prefix-{literal}-01.txt",
            "Files renamed successfully: 1",
        ]
    )
