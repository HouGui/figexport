"""Real native-tool tests: deliberately fail when CI tool installation is incomplete."""

import os
from pathlib import Path

import pytest
from PIL import Image

from figexport.export.drawio_exporter import DrawioExporter
from figexport.export.enums import ExportFormat
from figexport.export.puml_exporter import PumlExporter
from figexport.export.tex_exporter import TexExporter

pytestmark = pytest.mark.integration


def assert_output(output, format):
    output = Path(output)
    assert output.is_file() and output.stat().st_size > 0
    if format == ExportFormat.PDF:
        assert output.read_bytes().startswith(b"%PDF")
    elif format == ExportFormat.SVG:
        assert b"<svg" in output.read_bytes()
    else:
        with Image.open(output) as image:
            image.verify()
            assert image.format == ("JPEG" if format == ExportFormat.JPG else "PNG")


@pytest.mark.parametrize("format", list(ExportFormat))
def test_native_tex(tmp_path, format):
    folder = tmp_path / "source with spaces"
    folder.mkdir()
    source = folder / "figure.tex"
    source.write_text(
        r"\documentclass{article}\pagestyle{empty}\begin{document}\input{label}\end{document}"
    )
    (folder / "label.tex").write_text("Relative include works.")
    output = TexExporter(format).export(source, tmp_path / "out")
    assert_output(output, format)
    assert sorted(p.name for p in folder.iterdir()) == ["figure.tex", "label.tex"]


@pytest.mark.parametrize("format", list(ExportFormat))
def test_native_plantuml(tmp_path, format):
    source = tmp_path / "diagram.puml"
    source.write_text("@startuml custom-name\n!include label.iuml\nAlice -> Bob: Hello\n@enduml")
    (tmp_path / "label.iuml").write_text("title Relative include works\n")
    jar = os.environ.get("FIGEXPORT_PLANTUML_JAR", "plantuml.jar")
    output = PumlExporter(jar, export_format=format).export(source, tmp_path / "out")
    assert_output(output, format)


@pytest.mark.parametrize("format", list(ExportFormat))
def test_native_drawio(tmp_path, fixtures, format):
    exporter = DrawioExporter(os.environ.get("FIGEXPORT_DRAWIO"), format)
    outputs = exporter.export(fixtures / "Rectangle1_drawio.drawio", tmp_path / "out")
    assert isinstance(outputs, list) and len(outputs) == 2
    for output in outputs:
        assert_output(output, format)


def test_native_invalid_plantuml(tmp_path):
    from figexport.errors import ExportError

    source = tmp_path / "bad.puml"
    source.write_text("@startuml\nthis is not valid PlantUML !@#$\n@enduml")
    with pytest.raises(ExportError):
        PumlExporter(os.environ.get("FIGEXPORT_PLANTUML_JAR", "plantuml.jar")).export(
            source, tmp_path / "out"
        )


def test_native_invalid_tex(tmp_path):
    from figexport.errors import ExportError

    source = tmp_path / "bad.tex"
    source.write_text(r"\documentclass{article}\begin{document}\undefinedcommand\end{document}")
    with pytest.raises(ExportError, match="Undefined"):
        TexExporter().export(source, tmp_path / "out")
