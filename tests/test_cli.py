import json
import logging
import os
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest

from figexport.main import main


def test_default_cli_and_format_override_without_config(svg_file, monkeypatch, capsys):
    monkeypatch.chdir(svg_file.parent)
    assert main([str(svg_file), "-f", "PNG"]) == 0
    assert (svg_file.parent / "_export/drawing.png").read_bytes().startswith(b"\x89PNG")
    assert "1 exported" in capsys.readouterr().out


def test_json_dry_run_never_creates_outputs(svg_file, capsys):
    output = svg_file.parent / "dry"
    assert main([str(svg_file), "--dry-run", "--json", "-o", str(output)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["planned"] == 1
    assert report["results"][0]["outputs"] == [str(output / "drawing.pdf")]
    assert not output.exists()


def test_config_relative_paths_and_cli_relative_override(tmp_path, svg_file, monkeypatch):
    folder = tmp_path / "settings"
    folder.mkdir()
    config = folder / "config.json"
    config.write_text(json.dumps({"directory_mappings": [{"source": "../drawing.svg"}]}))
    monkeypatch.chdir(tmp_path)
    assert main(["-c", str(config), "-o", "cli-output", "-f", "svg"]) == 0
    assert (tmp_path / "cli-output/drawing.svg").exists()
    assert not (folder / "cli-output").exists()


@pytest.mark.parametrize(
    "content,fragment",
    [("{oops", "line 1, column 2"), ("[]", "JSON object"), ('{"export_frmat":"pdf"}', "Unknown")],
)
def test_bad_config_is_actionable(tmp_path, capsys, content, fragment):
    config = tmp_path / "bad.json"
    config.write_text(content)
    assert main(["-c", str(config), "--json"]) == 2
    captured = capsys.readouterr()
    assert fragment in captured.err
    assert "Traceback" not in captured.err
    assert json.loads(captured.out)["exit_code"] == 2


def test_missing_explicit_config(tmp_path, capsys):
    assert main(["-c", str(tmp_path / "missing.json")]) == 2
    assert "does not exist" in capsys.readouterr().err


def test_init_config_does_not_overwrite(tmp_path, capsys):
    target = tmp_path / "config.json"
    assert main(["--init-config", str(target)]) == 0
    original = target.read_bytes()
    assert main(["--init-config", str(target)]) == 1
    assert target.read_bytes() == original
    assert "Traceback" not in capsys.readouterr().err


def test_tools_check_is_informational(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["--check-tools", "--json"]) == 0
    assert "svg" in json.loads(capsys.readouterr().out)
    assert not (tmp_path / "_export").exists()


def test_invalid_format_is_argparse_error():
    with pytest.raises(SystemExit) as raised:
        main(["--format", "gif"])
    assert raised.value.code == 2


def test_quiet_and_no_overwrite(svg_file, capsys):
    output = svg_file.parent / "out"
    arguments = [str(svg_file), "-o", str(output), "-f", "svg", "-q"]
    assert main(arguments) == 0
    target = output / "drawing.svg"
    target.write_bytes(b"keep me")
    assert main(arguments + ["--no-overwrite"]) == 0
    assert target.read_bytes() == b"keep me"
    assert capsys.readouterr().out == ""


def test_exclude_descendants(svg_file, capsys):
    assert main([str(svg_file.parent), "--exclude", str(svg_file.parent), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["results"] == []


def test_logger_configuration_is_restored(svg_file):
    logger = logging.getLogger("figexport")
    before = (logger.level, logger.propagate, list(logger.handlers))
    main([str(svg_file), "--dry-run", "-q"])
    assert (logger.level, logger.propagate, logger.handlers) == before


def test_module_cli_version():
    result = subprocess.run(
        [sys.executable, "-m", "figexport", "--version"], capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 0
    assert result.stdout.startswith("figexport ")


def test_command_failure_exit_code(tmp_path, capsys):
    source = tmp_path / "bad.svg"
    source.write_text("not XML")
    assert main([str(source), "--json"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["failed"] == 1
    assert report["results"][0]["source"] == str(source)


def test_missing_input_and_invalid_timeout(tmp_path):
    assert main([str(tmp_path / "missing.svg")]) == 2
    assert main([str(tmp_path), "--timeout", "nan"]) == 2


def test_console_script_returns_failure(tmp_path):
    script = "figexport.exe" if os.name == "nt" else "figexport"
    executable = str(Path(sysconfig.get_path("scripts")) / script)
    result = subprocess.run(
        [executable, str(tmp_path / "missing.svg")], capture_output=True, text=True, timeout=20
    )
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


def test_dry_run_cannot_write_a_configuration(tmp_path):
    target = tmp_path / "config.json"
    with pytest.raises(SystemExit) as error:
        main(["--dry-run", "--init-config", str(target)])
    assert error.value.code == 2
    assert not target.exists()


def test_non_utf8_configuration_reports_its_path(tmp_path, capsys):
    config = tmp_path / "bad.json"
    config.write_bytes(b"\xff")
    assert main(["-c", str(config)]) == 2
    captured = capsys.readouterr()
    assert str(config) in captured.err and "UTF-8" in captured.err
