import os
from pathlib import Path

import pytest


@pytest.fixture
def test_dir() -> Path:
    """Returns the full path of the test directory as a Path object."""
    return Path(__file__).parent


@pytest.fixture
def test_export_dir(test_dir: Path) -> Path:
    """Returns the path of the test export directory as a Path object."""
    export_dir = test_dir / "_export"
    export_dir.mkdir(exist_ok=True)
    return export_dir


@pytest.fixture
def root_path(test_dir: Path) -> Path:
    """Returns the root path of the FigExport project."""
    return test_dir.parent


@pytest.fixture
def plantuml_url() -> str:
    """Returns the URL of the PlantUML JAR file."""
    return "https://github.com/plantuml/plantuml/releases/download/v1.2025.2/plantuml-1.2025.2.jar"


@pytest.fixture
def drawio_path() -> str:
    """Returns the path of the draw.io executable."""
    # For Windows, you can use the following path:
    if os.name == 'nt':
        return "C:/Program Files/draw.io/draw.io.exe"
    elif os.name == 'posix':
        return "/usr/bin/drawio"
    else:
        raise RuntimeError("Currently unsupported operating system for draw.io.")
