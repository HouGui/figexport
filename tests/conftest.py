import os
from pathlib import Path

import pytest
import requests

SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="10">'
    '<rect width="10" height="10" fill="red"/></svg>'
)


def pytest_collection_modifyitems(items):
    if os.environ.get("FIGEXPORT_INTEGRATION") != "1":
        skip = pytest.mark.skip(reason="Set FIGEXPORT_INTEGRATION=1 to run native converter tests.")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip)


@pytest.fixture(autouse=True)
def offline_unit_tests(request, monkeypatch):
    if "integration" not in request.keywords:

        def deny_network(*args, **kwargs):
            pytest.fail("Unit tests must not make network requests.")

        monkeypatch.setattr(requests.sessions.Session, "request", deny_network)


@pytest.fixture
def svg_file(tmp_path):
    source = tmp_path / "drawing.svg"
    source.write_text(SVG, encoding="utf-8")
    return source


@pytest.fixture
def fixtures():
    return Path(__file__).parent / "fixtures"
