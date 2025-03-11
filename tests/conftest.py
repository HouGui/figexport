import os

import pytest


@pytest.fixture
def test_dir() -> str:
    """Returns the full path of the test directory."""
    return os.path.dirname(__file__)


@pytest.fixture
def test_export_dir(test_dir: str) -> str:
    """Returns the path of the test export directory.

    Args:
        test_dir_path: The path of the test directory.
    """
    export_dir = os.path.join(test_dir, "_export")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


@pytest.fixture
def plantuml_url() -> str:
    """Returns the URL of the PlantUML JAR file."""
    return "https://sourceforge.net/projects/plantuml/files/plantuml.jar/download"
