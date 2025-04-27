import pytest
import sys  # For checking platform for symlink test
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock  # For mocking click.confirm

# Adjust import path for your main cli entry point and helpers
from filemate.cli import cli  # Assuming 'cli' is your main @click.group() object
from filemate.utils.create_test_helpers import create_test_files

# --- Tests for 'file rename' ---


def test_cli_file_rename_pattern_format(tmp_path: Path) -> None:
    """Test rename pattern with format specifier like :03d."""
    create_test_files(tmp_path, 1, ext=".csv")  # sample_0.csv
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "file",
            "rename",
            str(tmp_path),
            "--pattern",
            "data_{i:03d}",  # Use formatting
            "--ext",
            ".csv",
            "--yes",  # Skip confirmation for testing
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Renamed: sample_0.csv → data_001.csv" in result.output
    assert (tmp_path / "data_001.csv").exists()
    assert not (tmp_path / "sample_0.csv").exists()


@patch("click.confirm")  # Mock the confirmation prompt
def test_cli_file_rename_confirm_yes(mock_confirm: MagicMock, tmp_path: Path) -> None:
    """Test rename confirmation prompt is shown and proceeds if confirmed."""
    create_test_files(tmp_path, 1, ext=".txt")
    mock_confirm.return_value = True  # Simulate user typing 'y'

    runner = CliRunner()
    # DO NOT pass --yes, so prompt should appear
    result = runner.invoke(cli, ["file", "rename", str(tmp_path)])

    mock_confirm.assert_called_once()  # Verify prompt was called
    assert result.exit_code == 0, result.output
    assert "Renamed: sample_0.txt → file_1.txt" in result.output
    assert (tmp_path / "file_1.txt").exists()


@patch("click.confirm")
def test_cli_file_rename_confirm_no(mock_confirm: MagicMock, tmp_path: Path) -> None:
    """Test rename confirmation prompt is shown and cancels if denied."""
    create_test_files(tmp_path, 1, ext=".txt")
    mock_confirm.return_value = False  # Simulate user typing 'n'

    runner = CliRunner()
    # DO NOT pass --yes
    result = runner.invoke(cli, ["file", "rename", str(tmp_path)])

    mock_confirm.assert_called_once()
    assert result.exit_code == 0  # Should exit cleanly after cancellation
    assert "Operation cancelled by user" in result.output
    assert (tmp_path / "sample_0.txt").exists()  # File unchanged
    assert not (tmp_path / "file_1.txt").exists()


def test_cli_file_rename_yes_flag(tmp_path: Path) -> None:
    """Test rename with --yes flag skips confirmation."""
    create_test_files(tmp_path, 1, ext=".txt")
    # No mocking needed, just pass the flag

    runner = CliRunner()
    result = runner.invoke(cli, ["file", "rename", str(tmp_path), "--yes"])  # Use --yes

    assert result.exit_code == 0, result.output
    assert "Renamed: sample_0.txt → file_1.txt" in result.output
    assert (tmp_path / "file_1.txt").exists()
    # Assert confirmation text is NOT in output (tricky, might require more specific checks)
    assert "Proceed with renaming?" not in result.output


def test_cli_file_rename_conflict_no_force(tmp_path: Path) -> None:
    """Test rename skips conflicting file without --force."""
    create_test_files(tmp_path, 1, ext=".txt")  # sample_0.txt
    (tmp_path / "file_1.txt").write_text("exists")  # Conflict file

    runner = CliRunner()
    result = runner.invoke(cli, ["file", "rename", str(tmp_path), "--yes"])

    assert result.exit_code == 0, result.output
    assert (
        "Error: Could not rename sample_0.txt" in result.output
    )  # Check error message
    assert "persisted after" in result.output
    assert (tmp_path / "sample_0.txt").exists()  # Original not renamed
    assert (tmp_path / "file_1.txt").read_text() == "exists"  # Conflict untouched
    assert "Files renamed successfully: 0" in result.output  # Check summary
    assert "Files skipped (due to naming conflicts): 1" in result.output


def test_cli_file_rename_conflict_force(tmp_path: Path) -> None:
    """Test rename overwrites conflicting file with --force."""
    create_test_files(tmp_path, 1, ext=".txt", base_name="source")  # source_0.txt
    (tmp_path / "file_1.txt").write_text("exists")  # Conflict file

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "file",
            "rename",
            str(tmp_path),
            "--pattern",
            "file_{i}",  # Explicit pattern leading to conflict
            "--ext",
            ".txt",
            "--force",  # Use force
            "--yes",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Overwriting existing file file_1.txt" in result.output  # Check warning
    assert "Renamed: source_0.txt → file_1.txt" in result.output
    assert not (tmp_path / "source_0.txt").exists()  # Original renamed
    assert (tmp_path / "file_1.txt").exists()  # Conflict file now overwritten
    # Check content if your helper adds unique content
    assert (tmp_path / "file_1.txt").read_text() != "exists"
    assert "Files renamed successfully: 1" in result.output  # Check summary


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Symlinks require special permissions or handling on Windows",
)
def test_cli_file_rename_skips_symlink(tmp_path: Path) -> None:
    """Test rename skips symbolic links by default."""
    target_file = tmp_path / "target.txt"
    target_file.write_text("target")
    link_file = tmp_path / "link.txt"
    link_file.symlink_to(target_file)

    runner = CliRunner()
    result = runner.invoke(cli, ["file", "rename", str(tmp_path), "--yes"])

    assert result.exit_code == 0, result.output
    assert "Skipping symbolic link: link.txt" in result.output
    assert link_file.is_symlink()  # Link still exists and is a link
    assert link_file.name == "link.txt"  # Link was not renamed
    assert (
        tmp_path / "file_1.txt"
    ).exists()  # Target file *was* renamed (assuming target.txt sorted after link.txt)
    assert "Symbolic links skipped: 1" in result.output  # Check summary


# --- Tests for 'file change-ext' ---

# (Keep existing tests like test_cli_file_change_ext_basic, missing_to, output_dir)


@patch("click.confirm")
def test_cli_file_change_ext_confirm_yes(
    mock_confirm: MagicMock, tmp_path: Path
) -> None:
    """Test change-ext confirmation prompt proceeds if confirmed."""
    create_test_files(tmp_path, 1, ext=".old")
    mock_confirm.return_value = True

    runner = CliRunner()
    result = runner.invoke(cli, ["file", "change-ext", str(tmp_path), "--to", ".new"])

    mock_confirm.assert_called_once()
    assert result.exit_code == 0, result.output
    assert "Changed: sample_0.old → sample_0.new" in result.output
    assert (tmp_path / "sample_0.new").exists()


@patch("click.confirm")
def test_cli_file_change_ext_confirm_no(
    mock_confirm: MagicMock, tmp_path: Path
) -> None:
    """Test change-ext confirmation cancels if denied."""
    create_test_files(tmp_path, 1, ext=".old")
    mock_confirm.return_value = False

    runner = CliRunner()
    result = runner.invoke(cli, ["file", "change-ext", str(tmp_path), "--to", ".new"])

    mock_confirm.assert_called_once()
    assert result.exit_code == 0
    assert "Operation cancelled by user" in result.output
    assert (tmp_path / "sample_0.old").exists()
    assert not (tmp_path / "sample_0.new").exists()


def test_cli_file_change_ext_yes_flag(tmp_path: Path) -> None:
    """Test change-ext with --yes flag skips confirmation."""
    create_test_files(tmp_path, 1, ext=".old")

    runner = CliRunner()
    result = runner.invoke(
        cli, ["file", "change-ext", str(tmp_path), "--to", ".new", "--yes"]
    )

    assert result.exit_code == 0, result.output
    assert "Changed: sample_0.old → sample_0.new" in result.output
    assert (tmp_path / "sample_0.new").exists()
    assert "Proceed with changing extensions?" not in result.output


def test_cli_file_change_ext_conflict_no_force(tmp_path: Path) -> None:
    """Test change-ext skips conflicting file without --force."""
    create_test_files(tmp_path, 1, ext=".txt")  # sample_0.txt
    (tmp_path / "sample_0.bak").write_text("exists")  # Conflict file

    runner = CliRunner()
    result = runner.invoke(
        cli, ["file", "change-ext", str(tmp_path), "--to", ".bak", "--yes"]
    )

    assert result.exit_code == 0, result.output
    assert "Skipped (target exists):" in result.output
    assert "sample_0.txt → sample_0.bak" in result.output
    assert (tmp_path / "sample_0.txt").exists()  # Original not changed
    assert (tmp_path / "sample_0.bak").read_text() == "exists"  # Conflict untouched
    assert "Files extension changed successfully: 0" in result.output
    assert "Files skipped (due to target conflicts): 1" in result.output


def test_cli_file_change_ext_conflict_force(tmp_path: Path) -> None:
    """Test change-ext overwrites conflicting file with --force."""
    create_test_files(tmp_path, 1, ext=".txt", base_name="source")  # source_0.txt
    (tmp_path / "source_0.bak").write_text("exists")  # Conflict file

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "file",
            "change-ext",
            str(tmp_path),
            "--from",
            ".txt",
            "--to",
            ".bak",
            "--force",  # Use force
            "--yes",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Overwriting existing file source_0.bak" in result.output  # Check warning
    assert "Changed: source_0.txt → source_0.bak" in result.output
    assert not (tmp_path / "source_0.txt").exists()  # Original changed
    assert (tmp_path / "source_0.bak").exists()  # Conflict file now overwritten
    assert (tmp_path / "source_0.bak").read_text() != "exists"  # Check content
    assert "Files extension changed successfully: 1" in result.output


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Symlinks require special permissions or handling on Windows",
)
def test_cli_file_change_ext_skips_symlink(tmp_path: Path) -> None:
    """Test change-ext skips symbolic links by default."""
    target_file = tmp_path / "target.data"
    target_file.write_text("target")
    link_file = tmp_path / "link.data"
    link_file.symlink_to(target_file)
    # Add another regular file to ensure some processing happens
    create_test_files(tmp_path, 1, ext=".tmp")  # sample_0.tmp

    runner = CliRunner()
    result = runner.invoke(
        cli, ["file", "change-ext", str(tmp_path), "--to", ".new", "--yes"]
    )

    assert result.exit_code == 0, result.output
    assert "Skipping symbolic link: link.data" in result.output
    assert link_file.is_symlink()  # Link still exists and is a link
    assert link_file.suffix == ".data"  # Link suffix not changed
    assert (tmp_path / "sample_0.new").exists()  # Regular file was processed
    assert "Symbolic links skipped: 1" in result.output  # Check summary


# (Keep existing CLI help tests)
def test_cli_file_rename_help() -> None:
    """Test the --help message for file rename."""
    runner = CliRunner()
    result = runner.invoke(cli, ["file", "rename", "--help"])
    assert result.exit_code == 0
    assert "Usage: cli file rename [OPTIONS] FOLDER" in result.output
    assert "--pattern TEXT" in result.output
    assert "--yes" in result.output  # Check new options
    assert "--force" in result.output
    assert ":03d" in result.output  # Check pattern format hint


def test_cli_file_change_ext_help() -> None:
    """Test the --help message for file change-ext."""
    runner = CliRunner()
    result = runner.invoke(cli, ["file", "change-ext", "--help"])
    assert result.exit_code == 0
    assert "Usage: cli file change-ext [OPTIONS] FOLDER" in result.output
    assert "--to TEXT" in result.output
    assert "--yes" in result.output  # Check new options
    assert "--force" in result.output
