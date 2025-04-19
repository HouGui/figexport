import os

import pytest

from figexport.config import ExportConfig



def test_pdf_export_onefolder(root_path: str):
    """Test PDF export process for the given folder 'figures/introduction'.
    """
    print(f"Root path: {root_path}")
    # Read the configuration file into an ExportConfig object
    #config = ExportConfig(os.path.join(root_path, "config.json"))
