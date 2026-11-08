from figexport.config import ExportConfig
from figexport.tools import find_drawio, tool_status


def test_configured_drawio_uses_only_that_executable(monkeypatch):
    monkeypatch.setattr(
        "figexport.tools.shutil.which", lambda name: name if name == "custom" else None
    )
    assert find_drawio("custom") == "custom"
    assert find_drawio("missing") is None


def test_drawio_path_discovery(monkeypatch):
    monkeypatch.setattr(
        "figexport.tools.shutil.which", lambda name: "/bin/drawio" if name == "drawio" else None
    )
    assert find_drawio() == "/bin/drawio"


def test_drawio_windows_install_location(tmp_path, monkeypatch):
    monkeypatch.setattr("figexport.tools.sys.platform", "win32")
    monkeypatch.setattr("figexport.tools.shutil.which", lambda name: None)
    monkeypatch.setenv("ProgramFiles", str(tmp_path))
    executable = tmp_path / "draw.io/draw.io.exe"
    executable.parent.mkdir()
    executable.write_text("binary placeholder")
    assert find_drawio() == str(executable)


def test_diagnostics_find_installed_jar(tmp_path):
    jar = tmp_path / "plantuml.jar"
    jar.write_bytes(b"placeholder")
    assert tool_status(ExportConfig({}, tmp_path))["plantuml"] == str(jar)
