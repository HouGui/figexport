"""Tool discovery and subprocess diagnostics, with no shell invocation."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from figexport.errors import ExportError


def find_drawio(configured: str | Path | None = None) -> str | None:
    if configured:
        return shutil.which(str(configured))
    for command in ("drawio", "draw.io"):
        if executable := shutil.which(command):
            return executable
    candidates = [Path("/Applications/draw.io.app/Contents/MacOS/draw.io")]
    if sys.platform == "win32":
        for variable in ("ProgramFiles", "LOCALAPPDATA", "ProgramFiles(x86)"):
            if directory := os.environ.get(variable):
                candidates.append(Path(directory) / "draw.io" / "draw.io.exe")
                candidates.append(Path(directory) / "Programs" / "draw.io" / "draw.io.exe")
    return next((str(item) for item in candidates if item.is_file()), None)


def _text(value: bytes | str | None) -> str:
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value or ""


def run_command(
    command: list[str],
    *,
    timeout: float = 120,
    cwd: Path | None = None,
    input_data: bytes | None = None,
    binary_output: bool = False,
) -> bytes:
    """Run a converter and include its useful output in any failure."""
    try:
        result = subprocess.run(
            command, input=input_data, capture_output=True, check=True, timeout=timeout, cwd=cwd
        )
    except FileNotFoundError as exc:
        raise ExportError(
            f"Required tool '{command[0]}' was not found. Install it and "
            "add it to PATH, or configure its location."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ExportError(
            f"'{command[0]}' timed out after {timeout:g}s. Use --timeout to allow more time."
        ) from exc
    except subprocess.CalledProcessError as exc:
        details = _text(exc.stderr).strip()
        if not binary_output:
            details = "\n".join(part for part in (details, _text(exc.stdout).strip()) if part)
        raise ExportError(
            f"'{command[0]}' exited with code {exc.returncode}.\n"
            f"{details[-6000:] or 'No diagnostic output.'}"
        ) from exc
    except OSError as exc:
        raise ExportError(f"Could not run '{command[0]}': {exc}") from exc
    return result.stdout


def tool_status(config) -> dict[str, str | None]:
    """Inspect installations without starting tools or downloading anything."""
    try:
        import cairosvg

        cairo = f"CairoSVG {cairosvg.__version__}"
    except (ImportError, OSError) as exc:
        cairo = f"unavailable: {exc}"
    return {
        "svg": cairo,
        "drawio": find_drawio(config.drawio_path),
        "pdflatex": shutil.which("pdflatex"),
        "dvisvgm": shutil.which("dvisvgm"),
        "java": shutil.which("java"),
        "plantuml": (
            str(config.plantuml_path)
            if config.plantuml_path.is_file()
            else shutil.which("plantuml")
        ),
    }
