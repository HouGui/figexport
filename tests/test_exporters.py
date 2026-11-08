import hashlib
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests
from PIL import Image

from figexport.errors import ExportError
from figexport.export.drawio_exporter import DrawioExporter
from figexport.export.enums import ExportFormat
from figexport.export.puml_exporter import PumlExporter
from figexport.export.svg_exporter import SvgExporter
from figexport.export.tex_exporter import TexExporter
from figexport.tools import run_command
from figexport.utils import copy_file


@pytest.mark.parametrize("format", list(ExportFormat))
def test_real_svg_conversion(svg_file, format):
    output = Path(SvgExporter(format).export(svg_file, svg_file.parent / "out"))
    assert output.suffix == f".{format.value}"
    if format == ExportFormat.PDF:
        assert output.read_bytes().startswith(b"%PDF")
    elif format == ExportFormat.SVG:
        assert output.read_bytes() == svg_file.read_bytes()
    else:
        with Image.open(output) as image:
            assert image.size == (20, 10)
            assert image.format == ("JPEG" if format == ExportFormat.JPG else "PNG")
            if format == ExportFormat.JPG:
                assert all(channel > 240 for channel in image.getpixel((19, 5)))
    assert sorted(p.name for p in output.parent.iterdir()) == [output.name]


def test_failed_conversion_preserves_existing_output(svg_file, monkeypatch):
    target = svg_file.parent / "out/drawing.png"
    target.parent.mkdir()
    target.write_bytes(b"previous export")

    def fail(source, outputs):
        outputs[0].write_bytes(b"partial")
        raise RuntimeError("conversion failed")

    exporter = SvgExporter(ExportFormat.PNG)
    monkeypatch.setattr(exporter, "_convert", fail)
    with pytest.raises(ExportError, match="conversion failed"):
        exporter.export(svg_file, target.parent)
    assert target.read_bytes() == b"previous export"
    assert list(target.parent.iterdir()) == [target]


def test_successful_command_without_output_is_a_failure(svg_file, monkeypatch):
    exporter = SvgExporter()
    monkeypatch.setattr(exporter, "_convert", lambda *args: None)
    with pytest.raises(ExportError, match="non-empty"):
        exporter.export(svg_file, svg_file.parent / "out")


def test_binary_copy_and_same_file(tmp_path):
    source = tmp_path / "binary"
    source.write_bytes(bytes(range(256)))
    assert copy_file(source, source) == str(source)
    output = tmp_path / "nested/binary"
    copy_file(source, output)
    assert output.read_bytes() == source.read_bytes()


def test_direct_export_never_overwrites_input(svg_file):
    with pytest.raises(ExportError, match="overwrite source"):
        SvgExporter(ExportFormat.SVG).export(svg_file, svg_file.parent)


def test_missing_source(tmp_path):
    with pytest.raises(ExportError, match="does not exist"):
        SvgExporter().export(tmp_path / "missing.svg", tmp_path / "out")


@pytest.mark.parametrize(
    "error,match",
    [
        (FileNotFoundError(), "not found"),
        (PermissionError("denied"), "Could not run"),
        (subprocess.TimeoutExpired("tool", 2), "timed out"),
        (
            subprocess.CalledProcessError(
                3, "tool", output=b"stdout details", stderr=b"stderr details"
            ),
            "stderr details",
        ),
        (subprocess.CalledProcessError(3, "tool", output=b"latex log", stderr=None), "latex log"),
    ],
)
def test_subprocess_diagnostics(monkeypatch, error, match):
    monkeypatch.setattr(subprocess, "run", Mock(side_effect=error))
    with pytest.raises(ExportError, match=match):
        run_command(["tool", "file with spaces"], timeout=2)


def test_subprocess_uses_argv_and_timeout(monkeypatch, tmp_path):
    runner = Mock(return_value=subprocess.CompletedProcess([], 0, b"result", b""))
    monkeypatch.setattr(subprocess, "run", runner)
    assert run_command(["tool", "$(literal)"], timeout=7, cwd=tmp_path) == b"result"
    assert runner.call_args.args[0] == ["tool", "$(literal)"]
    assert runner.call_args.kwargs["timeout"] == 7
    assert "shell" not in runner.call_args.kwargs


def test_drawio_sanitizes_and_deduplicates_page_names(tmp_path):
    source = tmp_path / "diagram.drawio"
    source.write_text(
        '<mxfile><diagram name="../bad/name"/><diagram name="A B"/>'
        '<diagram name="A_B"/><diagram name="a_b"/><diagram/></mxfile>'
    )
    paths = DrawioExporter().output_paths(source, tmp_path / "out")
    assert len({p.name.casefold() for p in paths}) == 5
    assert all(p.parent == tmp_path / "out" for p in paths)
    assert paths[2].name == "diagram_A_B_2.pdf"
    assert paths[3].name == "diagram_a_b_3.pdf"


@pytest.mark.parametrize(
    "content",
    [
        "<broken",
        "<mxfile/>",
        "<other/>",
        '<!DOCTYPE mxfile [<!ENTITY x "bad">]><mxfile><diagram name="&x;"/></mxfile>',
    ],
)
def test_invalid_drawio_is_not_silently_accepted(tmp_path, content):
    source = tmp_path / "bad.drawio"
    source.write_text(content)
    with pytest.raises(ExportError):
        DrawioExporter().output_paths(source, tmp_path)


def test_drawio_raw_graph(tmp_path):
    source = tmp_path / "raw.drawio"
    source.write_text("<mxGraphModel/>")
    assert DrawioExporter.parse_page_names(source) == ["Page_0"]


@pytest.mark.parametrize(
    "version,indices", [(b"26.2.2", ["0", "1"]), (b"27.0.2", ["1", "2"]), (b"32.6.1", ["1", "2"])]
)
def test_drawio_invocation_and_all_pages_are_staged(tmp_path, monkeypatch, version, indices):
    source = tmp_path / "diagram.drawio"
    source.write_text('<mxfile><diagram name="A"/><diagram name="B"/></mxfile>')
    commands = []
    monkeypatch.setattr("figexport.export.drawio_exporter.find_drawio", lambda _: "drawio")

    def run(command, **kwargs):
        if "--version" in command:
            return version
        commands.append(command)
        Path(command[command.index("--output") + 1]).write_bytes(b"figure")

    monkeypatch.setattr("figexport.export.drawio_exporter.run_command", run)
    outputs = DrawioExporter().export(source, tmp_path / "out")
    assert len(outputs) == len(commands) == 2
    assert [command[command.index("--page-index") + 1] for command in commands] == indices


def test_drawio_missing_executable(tmp_path, monkeypatch):
    source = tmp_path / "diagram.drawio"
    source.write_text('<mxfile><diagram name="A"/></mxfile>')
    monkeypatch.setattr("figexport.export.drawio_exporter.find_drawio", lambda _: None)
    with pytest.raises(ExportError, match="exe_path"):
        DrawioExporter().export(source, tmp_path / "out")


@pytest.mark.parametrize("format", list(ExportFormat))
def test_tex_compiles_in_source_directory_and_cleans_up(tmp_path, monkeypatch, format, svg_file):
    source = tmp_path / "figure with spaces.tex"
    source.write_text("document")
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        assert kwargs["cwd"] == source.parent
        if command[0] == "pdflatex":
            assert "-no-shell-escape" in command and "-halt-on-error" in command
            build = Path(
                next(
                    arg.split("=", 1)[1] for arg in command if arg.startswith("-output-directory=")
                )
            )
            (build / "figure.pdf").write_bytes(b"%PDF-test")
            (build / "figure.dvi").write_bytes(b"dvi")
            (build / "figure.log").write_text("log")
        else:
            svg = Path(next(arg.split("=", 1)[1] for arg in command if arg.startswith("--output=")))
            svg.write_bytes(svg_file.read_bytes())

    monkeypatch.setattr("figexport.export.tex_exporter.run_command", run)
    output = Path(TexExporter(format).export(source, tmp_path / "out"))
    assert output.is_file()
    assert list(output.parent.iterdir()) == [output]
    assert len(commands) == (1 if format == ExportFormat.PDF else 2)
    assert source.read_text() == "document"


def test_plantuml_initialization_is_offline(tmp_path):
    jar = tmp_path / "missing.jar"
    PumlExporter(jar, "https://example.org/plantuml.jar")
    assert not jar.exists()


def response_for(data):
    response = Mock()
    response.url = "https://example.org/plantuml.jar"
    response.iter_content.return_value = [data]
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


def test_plantuml_download_checksum_and_atomic_install(tmp_path, monkeypatch):
    data = b"example jar"
    getter = Mock(return_value=response_for(data))
    monkeypatch.setattr(requests, "get", getter)
    jar = tmp_path / "cache/plantuml.jar"
    exporter = PumlExporter(
        jar, "https://example.org/plantuml.jar", sha256=hashlib.sha256(data).hexdigest()
    )
    exporter._ensure_plantuml_exists()
    exporter._ensure_plantuml_exists()
    assert jar.read_bytes() == data
    assert getter.call_count == 1
    assert getter.call_args.kwargs["timeout"] == 120
    assert list(jar.parent.iterdir()) == [jar]


@pytest.mark.parametrize("failure", ["network", "hash", "empty", "redirect"])
def test_plantuml_download_failure_leaves_no_partial_jar(tmp_path, monkeypatch, failure):
    response = response_for(b"" if failure == "empty" else b"bad jar")
    if failure == "network":
        response.iter_content.side_effect = requests.ConnectionError("disconnected")
    if failure == "redirect":
        response.url = "http://example.org/insecure.jar"
    monkeypatch.setattr(requests, "get", Mock(return_value=response))
    jar = tmp_path / "plantuml.jar"
    exporter = PumlExporter(
        jar, "https://example.org/jar", sha256="0" * 64 if failure == "hash" else None
    )
    with pytest.raises(ExportError):
        exporter._ensure_plantuml_exists()
    assert not jar.exists()
    assert not list(tmp_path.glob("*.part"))


@pytest.mark.parametrize("format", list(ExportFormat))
def test_plantuml_pipe_keeps_relative_includes_and_output_name(
    tmp_path, monkeypatch, svg_file, format
):
    import cairosvg

    source = tmp_path / "diagram.puml"
    source.write_text("@startuml custom-name\nA -> B\n@enduml")
    exporter = PumlExporter(tmp_path / "jar", export_format=format)
    monkeypatch.setattr(exporter, "_command", lambda: ["java", "-jar", "jar"])

    def run(command, **kwargs):
        assert kwargs["cwd"] == source.parent
        assert kwargs["input_data"] == source.read_bytes()
        assert "-pipe" in command and "-failfast2" in command
        return cairosvg.svg2png(url=str(svg_file)) if "-tpng" in command else svg_file.read_bytes()

    monkeypatch.setattr("figexport.export.puml_exporter.run_command", run)
    output = Path(exporter.export(source, tmp_path / "out"))
    assert output.name == f"diagram.{format.value}"
    assert list(output.parent.iterdir()) == [output]


def test_multiple_plantuml_diagrams_are_rejected(tmp_path):
    source = tmp_path / "multi.puml"
    source.write_text("@startuml\n@enduml\n@startuml\n@enduml")
    with pytest.raises(ExportError, match="one @start"):
        PumlExporter().export(source, tmp_path / "out")


def test_plantuml_without_jar_or_download_has_actionable_error(tmp_path):
    with pytest.raises(ExportError, match="jar_name"):
        PumlExporter(tmp_path / "missing.jar")._ensure_plantuml_exists()


def test_plantuml_command_discovery_and_missing_java(tmp_path, monkeypatch):
    monkeypatch.setattr("figexport.export.puml_exporter.shutil.which", lambda name: None)
    with pytest.raises(ExportError, match="Java"):
        PumlExporter(tmp_path / "missing.jar")._command()
    monkeypatch.setattr("figexport.export.puml_exporter.shutil.which", lambda name: "plantuml")
    assert PumlExporter(tmp_path / "missing.jar")._command() == ["plantuml"]
    jar = tmp_path / "installed.jar"
    jar.write_bytes(b"test jar")
    assert PumlExporter(jar)._command()[-2:] == ["-jar", str(jar)]


def test_existing_plantuml_jar_checksum_is_verified(tmp_path):
    jar = tmp_path / "installed.jar"
    jar.write_bytes(b"modified")
    with pytest.raises(ExportError, match="SHA-256 mismatch"):
        PumlExporter(jar, sha256="0" * 64)._ensure_plantuml_exists()


def test_drawio_failed_second_page_preserves_all_existing_pages(tmp_path, monkeypatch):
    source = tmp_path / "diagram.drawio"
    source.write_text('<mxfile><diagram name="A"/><diagram name="B"/></mxfile>')
    output = tmp_path / "out"
    output.mkdir()
    for name in ("A", "B"):
        (output / f"diagram_{name}.pdf").write_bytes(b"previous")
    monkeypatch.setattr("figexport.export.drawio_exporter.find_drawio", lambda _: "drawio")

    def run(command, **kwargs):
        if "--version" in command:
            return b"32.6.1"
        target = Path(command[command.index("--output") + 1])
        target.write_bytes(b"new")
        if target.stem.endswith("B"):
            raise ExportError("second page failed")

    monkeypatch.setattr("figexport.export.drawio_exporter.run_command", run)
    with pytest.raises(ExportError, match="second page"):
        DrawioExporter().export(source, output)
    assert sorted(p.name for p in output.iterdir()) == ["diagram_A.pdf", "diagram_B.pdf"]
    assert all(p.read_bytes() == b"previous" for p in output.iterdir())


def test_unknown_drawio_version_fails_clearly(tmp_path, monkeypatch):
    source = tmp_path / "diagram.drawio"
    source.write_text('<mxfile><diagram name="A"/></mxfile>')
    monkeypatch.setattr("figexport.export.drawio_exporter.find_drawio", lambda _: "drawio")
    monkeypatch.setattr("figexport.export.drawio_exporter.run_command", lambda *a, **k: b"unknown")
    with pytest.raises(ExportError, match="detect the draw.io version"):
        DrawioExporter().export(source, tmp_path / "out")
