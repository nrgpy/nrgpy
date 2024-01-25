from pathlib import Path
import pytest


@pytest.fixture
def test_file_directory():
    return Path(__file__).parent / "readers" / "files"

