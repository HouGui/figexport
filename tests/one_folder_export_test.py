import os

import pytest

from figexport.config import ExportConfig


@pytest.fixture
def root_path() -> str:
    """Returns the root path of the project."""
    test_dir = os.path.dirname(__file__)
    return os.path.dirname(os.path.dirname(test_dir))


def test_pdf_export_onefolder(root_path: str):
    """Test PDF export process for the given folder 'figures/introduction'.
    """
    # Read the configuration file into an ExportConfig object
    config = ExportConfig(os.path.join(root_path, "config.json"))
