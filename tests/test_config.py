from copy import deepcopy
from pathlib import Path

import pytest

from figexport.config import ExportConfig
from figexport.errors import ConfigError
from figexport.export.enums import ExportFormat


def test_defaults_need_no_tools_or_mappings(tmp_path):
    config = ExportConfig({}, tmp_path)
    assert config.export_format is ExportFormat.PDF
    assert config.export_dir == tmp_path / "_export"
    assert config.export_mappings == [{"input_path": tmp_path, "export_dir": tmp_path / "_export"}]
    assert config.plantuml_url is None
    assert not config.export_dir.exists()


def test_config_paths_and_explicit_input(tmp_path):
    data = {
        "export_dir": "out",
        "directory_mappings": [{"source": "src", "target": "nested"}],
        "excluded_paths": ["src/excluded"],
        "tools": {"drawio": {"exe_path": "bin/drawio"}},
    }
    config = ExportConfig(data, tmp_path)
    assert config.export_mappings[0]["export_dir"] == tmp_path / "out/nested"
    assert config.skip_paths == [tmp_path / "src/excluded"]
    assert config.drawio_path == str(tmp_path / "bin/drawio")
    override = ExportConfig(data, tmp_path, tmp_path / "one.svg")
    assert override.export_mappings == [
        {"input_path": tmp_path / "one.svg", "export_dir": tmp_path / "out"}
    ]


@pytest.mark.parametrize("value", [[], "bad", 3, False])
def test_invalid_root(value, tmp_path):
    with pytest.raises(ConfigError, match="JSON object"):
        ExportConfig(value, tmp_path)


@pytest.mark.parametrize(
    "data,match",
    [
        ({"typo": 1}, "Unknown"),
        ({"export_format": "gif"}, "format"),
        ({"export_format": []}, "format"),
        ({"export_dir": ""}, "path string"),
        ({"export_dir": 42}, "path string"),
        ({"timeout": 0}, "positive"),
        ({"timeout": -1}, "positive"),
        ({"timeout": True}, "positive"),
        ({"timeout": "10"}, "positive"),
        ({"timeout": float("inf")}, "positive"),
        ({"timeout": float("nan")}, "positive"),
        ({"directory_mappings": []}, "non-empty list"),
        ({"directory_mappings": {}}, "non-empty list"),
        ({"directory_mappings": [{}]}, "source"),
        ({"directory_mappings": [{"source": ".", "target": "../escape"}]}, "inside"),
        ({"excluded_paths": "file.svg"}, "list"),
        ({"excluded_paths": [None]}, "path string"),
        ({"tools": []}, "JSON object"),
        ({"tools": {"unknown": {}}}, "Unknown"),
        ({"tools": {"drawio": {"exe_path": ""}}}, "non-empty"),
        ({"tools": {"plantuml": {"download_url": "http://example.org/p.jar"}}}, "HTTPS"),
        ({"tools": {"plantuml": {"download_url": 2}}}, "HTTPS"),
        ({"tools": {"plantuml": {"sha256": "bad"}}}, "hexadecimal"),
    ],
)
def test_validation(data, match, tmp_path):
    with pytest.raises(ConfigError, match=match):
        ExportConfig(data, tmp_path)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("PDF", ExportFormat.PDF),
        ("jpeg", ExportFormat.JPG),
        ("PNG", ExportFormat.PNG),
        ("svg", ExportFormat.SVG),
    ],
)
def test_format_aliases(value, expected):
    assert ExportFormat.from_str(value) == expected


def test_bare_command_and_hash(tmp_path):
    config = ExportConfig(
        {"tools": {"drawio": {"exe_path": "custom-drawio"}, "plantuml": {"sha256": "A" * 64}}},
        tmp_path,
    )
    assert config.drawio_path == "custom-drawio"
    assert config.plantuml_sha256 == "a" * 64


@pytest.mark.parametrize("executable", ["bin tools/drawio", r"bin tools\drawio.exe"])
def test_tool_settings_preserve_paths_and_input_data(tmp_path, executable):
    data = {
        "timeout": 2.5,
        "tools": {
            "drawio": {"exe_path": executable},
            "plantuml": {
                "jar_name": "tools/plantuml.jar",
                "download_url": "https://example.org/plantuml.jar",
                "sha256": "A" * 64,
            },
        },
    }
    original = deepcopy(data)

    config = ExportConfig(data, tmp_path)

    assert config.drawio_path == str((tmp_path / Path(executable)).resolve())
    assert config.plantuml_path == tmp_path / "tools/plantuml.jar"
    assert config.plantuml_url == "https://example.org/plantuml.jar"
    assert config.plantuml_sha256 == "a" * 64
    assert config.timeout == 2.5
    assert data == original
    assert not list(tmp_path.iterdir())


def test_explicit_input_still_validates_configured_mappings(tmp_path):
    with pytest.raises(ConfigError, match="inside export_dir"):
        ExportConfig(
            {"directory_mappings": [{"source": ".", "target": "../outside"}]},
            tmp_path,
            tmp_path / "figure.svg",
        )
