import pytest
import sys  # For skipping symlink test
from pathlib import Path
from unittest.mock import patch, MagicMock


from filemate.core.change_extension import change_extensions, ChangeExtConfig
from filemate.utils.create_test_helpers import create_test_files
from filemate.utils.test_output_checker import OutputChecker

# --- Test Cases ---


# 1. Basic Functionality
@pytest.mark.change_ext
def test_change_ext_basic(tmp_path: Path) -> None:
    """Test changing a single extension in the same directory."""
    _ = create_test_files(tmp_path, 3, ext=".txt")
    config = ChangeExtConfig(folder=tmp_path, new_extension=".bak")
    count = change_extensions(config, yes=True)

    assert count == 3
    assert not list(tmp_path.glob("*.txt"))  # Original should be gone
    assert len(list(tmp_path.glob("*.bak"))) == 3  # New extension should exist
    assert (tmp_path / "sample_0.bak").exists()
    assert (tmp_path / "sample_1.bak").exists()
    assert (tmp_path / "sample_2.bak").exists()


# 2. Handling '.' in 'to' extension
@pytest.mark.change_ext
def test_change_ext_to_no_dot(tmp_path: Path) -> None:
    """Test providing the 'to' extension without a leading dot."""
    _ = create_test_files(tmp_path, 2, ext=".md")
    # Pydantic model handles adding the dot internally
    config = ChangeExtConfig(folder=tmp_path, new_extension="txt")
    assert config.new_extension == ".txt"  # Verify internal normalization
    count = change_extensions(config, yes=True)

    assert count == 2
    assert not list(tmp_path.glob("*.md"))
    assert len(list(tmp_path.glob("*.txt"))) == 2
    assert (tmp_path / "sample_0.txt").exists()
    assert (tmp_path / "sample_1.txt").exists()


# 3. Filtering with --from (single extension)
@pytest.mark.change_ext
def test_change_ext_from_single(tmp_path: Path) -> None:
    """Test changing only files matching a specific source extension."""
    create_test_files(tmp_path, 2, ext=".txt")
    create_test_files(tmp_path, 2, ext=".log")
    config = ChangeExtConfig(
        folder=tmp_path, new_extension=".bak", from_extensions=[".txt"]
    )
    count = change_extensions(config, yes=True)

    assert count == 2
    assert not list(tmp_path.glob("sample_*.txt"))  # .txt files should be gone
    assert len(list(tmp_path.glob("*.bak"))) == 2  # Only 2 .bak files
    assert len(list(tmp_path.glob("*.log"))) == 2  # .log files should remain untouched


# 4. Filtering with --from (multiple extensions)
@pytest.mark.change_ext
def test_change_ext_from_multiple(tmp_path: Path) -> None:
    """Test changing files matching multiple source extensions."""
    # Use unique base names to avoid conflict during the test itself
    create_test_files(tmp_path, 1, ext=".txt", base_name="file_txt")  # file_txt_0.txt
    create_test_files(tmp_path, 1, ext=".log", base_name="file_log")  # file_log_0.log
    create_test_files(tmp_path, 1, ext=".md", base_name="file_md")  # file_md_0.md
    config = ChangeExtConfig(
        folder=tmp_path, new_extension=".backup", from_extensions=["txt", ".log"]
    )  # Mix with/without dot
    count = change_extensions(config, yes=True)

    assert count == 2  # Expecting 2 files changed
    assert not list(tmp_path.glob("file_txt*.txt"))
    assert not list(tmp_path.glob("file_log*.log"))
    assert len(list(tmp_path.glob("*.backup"))) == 2
    assert (tmp_path / "file_txt_0.backup").exists()
    assert (tmp_path / "file_log_0.backup").exists()
    assert len(list(tmp_path.glob("*.md"))) == 1  # .md remains


# 5. Filtering with --from (case insensitivity)
@pytest.mark.change_ext
def test_change_ext_from_case_insensitive(tmp_path: Path) -> None:
    """Test that --from matching is case-insensitive."""
    create_test_files(tmp_path, 1, ext=".JPG")
    create_test_files(tmp_path, 1, ext=".png")
    config = ChangeExtConfig(
        folder=tmp_path, new_extension=".jpeg", from_extensions=[".jpg"]
    )  # Lowercase filter
    count = change_extensions(config, yes=True)

    assert count == 1
    assert not list(tmp_path.glob("*.JPG"))
    assert len(list(tmp_path.glob("*.jpeg"))) == 1
    assert (tmp_path / "sample_0.jpeg").exists()
    assert len(list(tmp_path.glob("*.png"))) == 1  # png remains


# 6. Filtering with --from (no matching files)
@pytest.mark.change_ext
def test_change_ext_from_no_match(tmp_path: Path) -> None:
    """Test behavior when --from filter matches no files."""
    create_test_files(tmp_path, 2, ext=".txt")
    config = ChangeExtConfig(
        folder=tmp_path, new_extension=".bak", from_extensions=[".log"]
    )
    count = change_extensions(config, yes=True)

    assert count == 0
    assert len(list(tmp_path.glob("*.txt"))) == 2  # Files remain untouched
    assert not list(tmp_path.glob("*.bak"))


# 7. Using --output-dir (directory exists)
@pytest.mark.change_ext
def test_change_ext_output_dir_exists(tmp_path: Path) -> None:
    """Test changing extensions and moving to an existing output directory."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    create_test_files(input_dir, 2, ext=".tmp")

    config = ChangeExtConfig(
        folder=input_dir, new_extension=".final", output_dir=output_dir
    )
    count = change_extensions(config, yes=True)

    assert count == 2
    assert not list(input_dir.iterdir())  # Input dir should be empty
    assert len(list(output_dir.glob("*.final"))) == 2
    assert (output_dir / "sample_0.final").exists()
    assert (output_dir / "sample_1.final").exists()


# 8. Using --output-dir (directory does not exist)
@pytest.mark.change_ext
def test_change_ext_output_dir_creation(tmp_path: Path) -> None:
    """Test that the output directory is created if it doesn't exist."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output_new"  # Does not exist
    input_dir.mkdir()
    create_test_files(input_dir, 1, ext=".raw")

    config = ChangeExtConfig(
        folder=input_dir, new_extension=".processed", output_dir=output_dir
    )
    count = change_extensions(config, yes=True)

    assert count == 1
    assert output_dir.exists() and output_dir.is_dir()
    assert not list(input_dir.iterdir())
    assert len(list(output_dir.glob("*.processed"))) == 1
    assert (output_dir / "sample_0.processed").exists()


# 9. Dry Run Functionality
@pytest.mark.change_ext
def test_change_ext_dry_run(tmp_path: Path, capsys: MagicMock) -> None:
    """Test --dry-run previews changes without modifying files."""
    _ = create_test_files(tmp_path, 2, ext=".txt")
    config = ChangeExtConfig(folder=tmp_path, new_extension=".md")
    count = change_extensions(config, dry_run=True, yes=True)

    # Use OutputChecker instead of raw capsys
    output = OutputChecker(capsys)

    assert count == 2  # Dry run should report count of files it *would* process
    assert len(list(tmp_path.glob("*.txt"))) == 2  # Original files remain
    assert not list(tmp_path.glob("*.md"))  # No new files created

    # Use assert_contains for more reliable assertions
    output.assert_contains(
        [
            "[DRY RUN]",
            "sample_0.txt → sample_0.md",
            "sample_1.txt → sample_1.md",
            "Files previewed for extension change: 2",
        ]
    )


# 10. Conflict Handling (Target Exists in Same Directory)
@pytest.mark.change_ext
def test_change_ext_conflict_same_dir(tmp_path: Path, capsys: MagicMock) -> None:
    """Test skipping when the target filename already exists in the source directory."""
    create_test_files(tmp_path, 1, ext=".txt")  # sample_0.txt
    (tmp_path / "sample_0.bak").write_text("already exists")  # Conflict file

    config = ChangeExtConfig(folder=tmp_path, new_extension=".bak")
    count = change_extensions(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    assert count == 0  # File should be skipped
    assert (tmp_path / "sample_0.txt").exists()  # Original remains
    assert (
        tmp_path / "sample_0.bak"
    ).read_text() == "already exists"  # Conflict file unchanged

    # Use assert_contains for more reliable assertions
    output.assert_contains(
        [
            "Skipped (target exists):",
            "sample_0.txt → sample_0.bak",
            "Files extension changed successfully: 0",
            "Files skipped (due to target conflicts): 1",
        ]
    )


# 11. Conflict Handling (Target Exists in Output Directory)
@pytest.mark.change_ext
def test_change_ext_conflict_output_dir(tmp_path: Path, capsys: MagicMock) -> None:
    """Test skipping when the target filename already exists in the output directory."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    create_test_files(input_dir, 1, ext=".txt")  # input/sample_0.txt
    (output_dir / "sample_0.bak").write_text("already exists")  # output/sample_0.bak

    config = ChangeExtConfig(
        folder=input_dir, new_extension=".bak", output_dir=output_dir
    )
    count = change_extensions(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    assert count == 0  # File should be skipped
    assert (input_dir / "sample_0.txt").exists()  # Original remains in input dir
    assert (
        output_dir / "sample_0.bak"
    ).read_text() == "already exists"  # Conflict file unchanged

    # Use assert_contains for more reliable assertions
    output.assert_contains(
        [
            "Skipped (target exists):",
            f"sample_0.txt → sample_0.bak in {output_dir.name}",
            "Files extension changed successfully: 0",
            "Files skipped (due to target conflicts): 1",
        ]
    )


# 12. Permission Error Handling (Mocking)
@pytest.mark.change_ext
@patch("pathlib.Path.rename", side_effect=PermissionError("Test Denied"))
def test_change_ext_permission_error_rename(
    mock_rename: MagicMock, tmp_path: Path, capsys: MagicMock
) -> None:
    """Test skipping file on PermissionError during rename (no output dir)."""
    file_path = create_test_files(tmp_path, 1, ext=".tmp")[0]
    config = ChangeExtConfig(folder=tmp_path, new_extension=".final")
    count = change_extensions(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    assert count == 0
    mock_rename.assert_called_once()
    assert file_path.exists()  # Original file remains
    assert not (tmp_path / "sample_0.final").exists()

    # Use assert_contains for more reliable assertions
    output.assert_contains(
        [
            "Permission denied (skipped):",
            "Test Denied",
            "Files extension changed successfully: 0",
            "Files skipped (due to errors): 1",
        ]
    )


@pytest.mark.change_ext
@patch("shutil.move", side_effect=PermissionError("Test Denied Move"))
def test_change_ext_permission_error_move(
    mock_move: MagicMock, tmp_path: Path, capsys: MagicMock
) -> None:
    """Test skipping file on PermissionError during move (with output dir)."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()  # Needs to exist for move attempt
    file_path = create_test_files(input_dir, 1, ext=".tmp")[0]

    config = ChangeExtConfig(
        folder=input_dir, new_extension=".final", output_dir=output_dir
    )
    count = change_extensions(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    assert count == 0
    mock_move.assert_called_once()
    assert file_path.exists()  # Original file remains in input dir
    assert not list(output_dir.iterdir())  # Output dir remains empty

    # Use assert_contains for more reliable assertions
    output.assert_contains(
        [
            "Permission denied (skipped):",
            "Test Denied Move",
            "Files extension changed successfully: 0",
            "Files skipped (due to errors): 1",
        ]
    )


# Add a new test for the --force flag
@pytest.mark.change_ext
def test_change_ext_force_overwrites_existing(
    tmp_path: Path, capsys: MagicMock
) -> None:
    """Test that --force overwrites existing files with the same name."""
    create_test_files(tmp_path, 1, ext=".txt", base_name="source")  # source_0.txt
    (tmp_path / "source_0.bak").write_text("pre-existing content")  # Conflict file

    config = ChangeExtConfig(folder=tmp_path, new_extension=".bak")
    count = change_extensions(config, yes=True, force=True)  # Use force=True

    # Use OutputChecker
    output = OutputChecker(capsys)

    assert count == 1  # File should be processed
    assert not (tmp_path / "source_0.txt").exists()  # Original should be gone
    assert (tmp_path / "source_0.bak").exists()  # Target file exists
    assert (
        tmp_path / "source_0.bak"
    ).read_text() != "pre-existing content"  # Content changed

    # Check for force-related messages
    output.assert_contains(
        [
            "--force specified: Overwriting existing file",
            "Changed:",
            "source_0.txt → source_0.bak",
            "Files extension changed successfully: 1",
        ]
    )


# Add a test for the output directory creation error handling
@pytest.mark.change_ext
def test_change_ext_output_dir_creation_error(
    tmp_path: Path, capsys: MagicMock
) -> None:
    """Test that the function exits gracefully if the output directory cannot be created."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output_fail"  # Does not exist
    input_dir.mkdir()
    create_test_files(input_dir, 1, ext=".raw")

    config = ChangeExtConfig(
        folder=input_dir, new_extension=".processed", output_dir=output_dir
    )

    # Apply patch only around the function call
    with patch(
        "pathlib.Path.mkdir", side_effect=OSError("Test Cannot Create Dir")
    ) as mock_mkdir:
        count = change_extensions(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    assert count == 0  # Should return 0 as no files were processed
    mock_mkdir.assert_called_once()  # Verify the mocked mkdir was called
    assert not output_dir.exists()  # Output dir still doesn't exist
    assert (input_dir / "sample_0.raw").exists()  # Input file untouched

    # Check for error messages
    output.assert_contains(
        ["Error creating output directory", "Test Cannot Create Dir"]
    )


# Test for the confirmation prompt with yes input
@pytest.mark.change_ext
@patch("filemate.core.change_extension.click.confirm")
def test_change_ext_confirm_prompt_yes_input(
    mock_confirm: MagicMock, tmp_path: Path, capsys: MagicMock
) -> None:
    """Test confirmation prompt proceeds if user inputs yes."""
    create_test_files(tmp_path, 1, ext=".old")
    mock_confirm.return_value = True  # Simulate user confirming
    config = ChangeExtConfig(folder=tmp_path, new_extension=".new")

    # Action: Call WITHOUT yes=True to trigger prompt
    count = change_extensions(config, yes=False)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    mock_confirm.assert_called_once()  # Check prompt was shown
    assert count == 1
    assert (tmp_path / "sample_0.new").exists()
    assert not (tmp_path / "sample_0.old").exists()

    # Check for confirmation-related messages
    output.assert_contains(
        [
            "Proposed Changes",
            "sample_0.old → sample_0.new",
            "Changed:",
            "Files extension changed successfully: 1",
        ]
    )


# Add a test for the confirmation prompt with no input
@pytest.mark.change_ext
@patch("filemate.core.change_extension.click.confirm")
def test_change_ext_confirm_prompt_no_input(
    mock_confirm: MagicMock, tmp_path: Path, capsys: MagicMock
) -> None:
    """Test confirmation prompt cancels if user inputs no."""
    create_test_files(tmp_path, 1, ext=".old")
    mock_confirm.return_value = False  # Simulate user cancelling
    config = ChangeExtConfig(folder=tmp_path, new_extension=".new")

    # Action: Call WITHOUT yes=True
    count = change_extensions(config, yes=False)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    mock_confirm.assert_called_once()
    assert count == 0
    assert not (tmp_path / "sample_0.new").exists()
    assert (tmp_path / "sample_0.old").exists()

    # Check for cancellation message
    output.assert_contains(
        [
            "Proposed Changes",
            "sample_0.old → sample_0.new",
            "Operation cancelled by user",
        ]
    )


# 13. Handling Empty Folder
@pytest.mark.change_ext
def test_change_ext_empty_folder(tmp_path: Path) -> None:
    """Test behavior with an empty input folder."""
    config = ChangeExtConfig(folder=tmp_path, new_extension=".bak")
    count = change_extensions(config, yes=True)
    assert count == 0


# 14. Handling Files Without Extensions
@pytest.mark.change_ext
def test_change_ext_no_extension_files(tmp_path: Path) -> None:
    """Test how files without extensions are handled."""
    (tmp_path / "file_no_ext").write_text("test")
    create_test_files(tmp_path, 1, ext=".txt")  # sample_0.txt

    # Scenario 1: --from is specified, should ignore no-ext file
    config1 = ChangeExtConfig(
        folder=tmp_path, new_extension=".bak", from_extensions=[".txt"]
    )
    count1 = change_extensions(config1, yes=True)
    assert count1 == 1
    assert not (tmp_path / "sample_0.txt").exists()
    assert (tmp_path / "sample_0.bak").exists()
    assert (tmp_path / "file_no_ext").exists()  # No-ext file untouched
    (tmp_path / "sample_0.bak").rename(tmp_path / "sample_0.txt")  # Reset for next test

    # Scenario 2: --from is omitted, should process no-ext file
    config2 = ChangeExtConfig(folder=tmp_path, new_extension=".dat")
    count2 = change_extensions(config2, yes=True)
    assert count2 == 2
    assert not (tmp_path / "sample_0.txt").exists()
    assert not (tmp_path / "file_no_ext").exists()
    assert (tmp_path / "sample_0.dat").exists()
    assert (tmp_path / "file_no_ext.dat").exists()  # No-ext file gets new extension


# 15. Handling Files with Multiple Dots
@pytest.mark.change_ext
def test_change_ext_multiple_dots(tmp_path: Path) -> None:
    """Test behavior with filenames containing multiple dots."""
    (tmp_path / "archive.tar.gz").write_text("test")
    (tmp_path / "document.v1.docx").write_text("test")

    # Scenario 1: Target specific last extension
    config1 = ChangeExtConfig(
        folder=tmp_path, new_extension=".backup", from_extensions=[".gz"]
    )
    count1 = change_extensions(config1, yes=True)
    assert count1 == 1
    assert not (tmp_path / "archive.tar.gz").exists()
    assert (tmp_path / "archive.tar.backup").exists()  # Correctly changes last ext
    assert (tmp_path / "document.v1.docx").exists()  # docx untouched
    (tmp_path / "archive.tar.backup").rename(tmp_path / "archive.tar.gz")  # Reset

    # Scenario 2: Change all (no --from)
    config2 = ChangeExtConfig(folder=tmp_path, new_extension=".final")
    count2 = change_extensions(config2, yes=True)
    assert count2 == 2
    assert not (tmp_path / "archive.tar.gz").exists()
    assert not (tmp_path / "document.v1.docx").exists()
    assert (tmp_path / "archive.tar.final").exists()  # Changes last suffix
    assert (tmp_path / "document.v1.final").exists()  # Changes last suffix


# 17. Validation Tests (via Config directly)
@pytest.mark.change_ext
def test_config_invalid_folder() -> None:
    """Test Pydantic validation prevents creating config with non-existent folder."""
    with pytest.raises(ValueError, match="is not a valid directory"):
        ChangeExtConfig(folder=Path("./non_existent_folder_xyz"), new_extension=".txt")


@pytest.mark.change_ext
def test_config_invalid_new_extension_empty() -> None:
    """Test Pydantic validation prevents empty new_extension."""
    with pytest.raises(ValueError, match="New extension cannot be empty"):
        ChangeExtConfig(folder=Path("."), new_extension=" ")  # Assuming '.' exists


# --- NEW TESTS for --yes, --force, symlinks ---


@pytest.mark.change_ext
def test_change_ext_yes_flag_skips_prompt(tmp_path: Path, capsys: MagicMock) -> None:
    """Test that yes=True flag bypasses the confirmation prompt."""
    create_test_files(tmp_path, 1, ext=".old")
    config = ChangeExtConfig(folder=tmp_path, new_extension=".new")

    # Action: Call WITH yes=True
    count = change_extensions(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 1
    assert (tmp_path / "sample_0.new").exists()

    # Check that no confirmation prompt appears in output
    output.assert_contains(["Changed:", "sample_0.old → sample_0.new"])
    output.assert_not_contains("Proceed with changes?")


@pytest.mark.change_ext
def test_change_ext_force_overwrite_conflict(tmp_path: Path, capsys: MagicMock) -> None:
    """Test force=True overwrites an existing target file."""
    create_test_files(tmp_path, 1, base_name="source", ext=".dat")  # source_0.dat
    (tmp_path / "source_0.bak").write_text("pre-existing data")  # Conflict file

    config = ChangeExtConfig(
        folder=tmp_path, new_extension=".bak"
    )  # Change source_0.dat -> source_0.bak
    # Action: Call with force=True and yes=True
    count = change_extensions(config, yes=True, force=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 1
    assert not (tmp_path / "source_0.dat").exists()
    assert (tmp_path / "source_0.bak").exists()
    assert (
        tmp_path / "source_0.bak"
    ).read_text() != "pre-existing data"  # Check content changed

    # Check for force-related messages
    output.assert_contains(["--force specified: Overwriting existing file"])


@pytest.mark.change_ext
def test_change_ext_no_force_skips_conflict(tmp_path: Path, capsys: MagicMock) -> None:
    """Test force=False (default) skips overwriting an existing target file."""
    create_test_files(tmp_path, 1, base_name="source", ext=".dat")  # source_0.dat
    (tmp_path / "source_0.bak").write_text("pre-existing data")  # Conflict file

    config = ChangeExtConfig(folder=tmp_path, new_extension=".bak")
    # Action: Call with force=False (default) and yes=True
    count = change_extensions(config, yes=True, force=False)

    # Use OutputChecker
    output = OutputChecker(capsys)

    # Assert
    assert count == 0  # File should be skipped due to conflict
    assert (tmp_path / "source_0.dat").exists()  # Original exists
    assert (
        tmp_path / "source_0.bak"
    ).read_text() == "pre-existing data"  # Conflict unchanged

    # Check for conflict-related messages
    output.assert_contains(
        ["Skipped (target exists):", "Files skipped (due to target conflicts): 1"]
    )


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Symlinks require special permissions or handling on Windows",
)
@pytest.mark.change_ext
def test_change_ext_skips_symlinks(tmp_path: Path, capsys: MagicMock) -> None:
    """Test that symbolic links are skipped by default."""
    target = tmp_path / "real_file.data"
    target.write_text("content")
    link = tmp_path / "link_to_file.data"
    link.symlink_to(target)
    create_test_files(tmp_path, 1, base_name="another", ext=".tmp")  # another_0.tmp

    config = ChangeExtConfig(folder=tmp_path, new_extension=".out")
    count = change_extensions(config, yes=True)

    # Use OutputChecker
    output = OutputChecker(capsys)

    assert count == 2  # Only real_file.data and another_0.tmp should be changed
    assert link.exists() and link.is_symlink()  # Link untouched
    assert link.name == "link_to_file.data"
    assert (tmp_path / "another_0.out").exists()  # Regular file changed
    assert (tmp_path / "real_file.out").exists()  # Target file changed

    # Check for symlink-related messages
    output.assert_contains(
        ["Skipping symbolic link: link_to_file.data", "Symbolic links skipped: 1"]
    )
