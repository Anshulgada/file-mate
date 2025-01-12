# file_mate/tests/test_utils.py

import pytest
from file_mate import utils
import os

# Create a dummy test file
TEST_FILE = "test_file.txt"
TEST_DIR = "test_dir"


@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    """Setup and teardown method."""
    with open(TEST_FILE, 'w') as f:
        f.write("Test content")
    os.makedirs(TEST_DIR, exist_ok=True)
    yield
    os.remove(TEST_FILE)

    #Remove directory with content
    def remove_directory(path):
         for item in os.listdir(path):
             item_path = os.path.join(path,item)
             if os.path.isfile(item_path):
                 os.remove(item_path)
             elif os.path.isdir(item_path):
                   remove_directory(item_path)
         os.rmdir(path)

    remove_directory(TEST_DIR) if os.path.exists(TEST_DIR) else None


def test_validate_file_exists_success():
    utils.validate_file_exists(TEST_FILE)


def test_validate_file_exists_fail():
    with pytest.raises(FileNotFoundError):
        utils.validate_file_exists("non_existent_file.txt")


def test_get_file_type():
    file_type = utils.get_file_type(TEST_FILE)
    assert "text" in file_type.lower()


def test_validate_output_dir_create():
    output_file = os.path.join(TEST_DIR, "new_test", "test.txt")
    utils.validate_output_dir(output_file)
    assert os.path.exists(os.path.dirname(output_file))
    os.rmdir(os.path.dirname(output_file))


def test_validate_output_dir_exists():
    output_file = os.path.join(TEST_DIR, "test.txt")
    utils.validate_output_dir(output_file)
    assert os.path.exists(TEST_DIR)
