"""Validate settings and resolve paths independently of conversion."""

import math
from pathlib import Path
from urllib.parse import urlparse

from figexport.errors import ConfigError
from figexport.export.enums import ExportFormat

DEFAULT_CONFIG = {
    "export_dir": "_export",
    "export_format": "pdf",
    "directory_mappings": [{"source": ".", "target": "."}],
    "excluded_paths": [],
}


def _object(value: object, label: str, allowed: set[str]) -> dict:
    if not isinstance(value, dict):
        raise ConfigError(f"{label} must be a JSON object.")

    unknown = value.keys() - allowed
    if unknown:
        raise ConfigError(f"Unknown {label} setting(s): {', '.join(sorted(unknown))}.")
    return value


def _path(value: object, base: Path, label: str) -> Path:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ConfigError(f"{label} must be a non-empty path string.")
    return (base / Path(value).expanduser()).resolve()


def _format(value: object) -> ExportFormat:
    try:
        return ExportFormat.from_str(value)
    except ValueError as exc:
        raise ConfigError(str(exc)) from exc


def _timeout(value: object) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise ConfigError("timeout must be a finite positive number of seconds.")
    return float(value)


def _mappings(value: object, base: Path, export_dir: Path) -> list[dict[str, Path]]:
    if not isinstance(value, list) or not value:
        raise ConfigError("directory_mappings must be a non-empty list.")

    mappings = []
    for index, mapping in enumerate(value):
        label = f"directory_mappings[{index}]"
        mapping = _object(mapping, label, {"source", "target"})
        source = _path(mapping.get("source"), base, f"{label}.source")
        target = _path(mapping.get("target", "."), export_dir, f"{label}.target")
        if not target.is_relative_to(export_dir):
            raise ConfigError(f"{label}.target must stay inside export_dir.")
        mappings.append({"input_path": source, "export_dir": target})
    return mappings


def _exclusions(value: object, base: Path) -> list[Path]:
    if not isinstance(value, list):
        raise ConfigError("excluded_paths must be a list of paths.")
    return [_path(item, base, "excluded_paths entry") for item in value]


def _drawio_path(value: object, base: Path) -> str | None:
    drawio = _object(value, "tools.drawio", {"exe_path"})
    executable = drawio.get("exe_path")
    if executable is None:
        return None
    if not isinstance(executable, str) or not executable.strip():
        raise ConfigError("tools.drawio.exe_path must be a non-empty string.")

    # Bare commands are searched on PATH; paths belong to the config directory.
    if "/" in executable or "\\" in executable:
        return str(_path(executable, base, "tools.drawio.exe_path"))
    return executable


def _plantuml_url(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        parsed = urlparse(value)
        if parsed.scheme == "https" and parsed.netloc:
            return value
    raise ConfigError("tools.plantuml.download_url must be an HTTPS URL.")


def _plantuml_sha256(value: object) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdefABCDEF" for c in value)
    ):
        raise ConfigError("tools.plantuml.sha256 must contain 64 hexadecimal digits.")
    return value.lower()


class ExportConfig:
    """Validated settings; configuration paths are relative to ``base_dir_path``."""

    def __init__(
        self,
        config_dict: dict | None = None,
        base_dir_path: Path | None = None,
        input_path: Path | None = None,
    ) -> None:
        data = _object(
            {} if config_dict is None else config_dict,
            "configuration",
            {*DEFAULT_CONFIG, "tools", "timeout"},
        )
        self.base_dir = Path(base_dir_path or Path.cwd()).resolve()
        self.export_dir = _path(data.get("export_dir", "_export"), self.base_dir, "export_dir")
        self.export_format = _format(data.get("export_format", "pdf"))
        self.timeout = _timeout(data.get("timeout", 120))

        self.export_mappings = _mappings(
            data.get("directory_mappings", DEFAULT_CONFIG["directory_mappings"]),
            self.base_dir,
            self.export_dir,
        )
        if input_path is not None:
            self.export_mappings = [
                {"input_path": Path(input_path).resolve(), "export_dir": self.export_dir}
            ]
        self.skip_paths = _exclusions(data.get("excluded_paths", []), self.base_dir)

        self._configure_tools(data.get("tools", {}))

    def _configure_tools(self, value: object) -> None:
        tools = _object(value, "tools", {"drawio", "plantuml"})
        self.drawio_path = _drawio_path(tools.get("drawio", {}), self.base_dir)

        plantuml = _object(
            tools.get("plantuml", {}), "tools.plantuml", {"jar_name", "download_url", "sha256"}
        )
        self.plantuml_path = _path(
            plantuml.get("jar_name", "plantuml.jar"), self.base_dir, "tools.plantuml.jar_name"
        )
        self.plantuml_url = _plantuml_url(plantuml.get("download_url"))
        self.plantuml_sha256 = _plantuml_sha256(plantuml.get("sha256"))
