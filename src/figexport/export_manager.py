"""Deterministic discovery, collision checks and conversion reports."""

import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from figexport.config import ExportConfig
from figexport.errors import ConfigError, ExportError
from figexport.export.fig_exporter import FigExporter
from figexport.export.registry import EXPORTERS, ExporterFactory

logger = logging.getLogger(__name__)
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    "build",
    "dist",
    "site",
}


@dataclass
class ExportResult:
    source: str
    outputs: list[str]
    status: str
    message: str = ""


@dataclass
class ExportReport:
    results: list[ExportResult] = field(default_factory=list)

    @property
    def failed(self) -> int:
        return sum(result.status == "failed" for result in self.results)

    def to_dict(self) -> dict:
        counts = {
            status: sum(result.status == status for result in self.results)
            for status in ("exported", "planned", "skipped", "failed")
        }
        return {**counts, "results": [asdict(result) for result in self.results]}


@dataclass
class ExportTask:
    source: Path
    destination: Path
    exporter: FigExporter
    outputs: list[Path]
    error: str = ""


class ExportManager:
    def __init__(
        self, config: ExportConfig, *, exporters: dict[str, ExporterFactory] | None = None
    ) -> None:
        self.config = config
        self._factories = dict(EXPORTERS if exporters is None else exporters)
        self._exporters: dict[str, FigExporter] = {}

    def _exporter(self, suffix: str) -> FigExporter:
        if suffix not in self._exporters:
            self._exporters[suffix] = self._factories[suffix](self.config)
        return self._exporters[suffix]

    def _excluded(self, entry: Path) -> bool:
        resolved = entry.resolve()
        return any(
            resolved == skip or resolved.is_relative_to(skip) for skip in self.config.skip_paths
        )

    def _sources(self):
        output_roots = {self.config.export_dir}
        output_roots.update(mapping["export_dir"] for mapping in self.config.export_mappings)

        for mapping in self.config.export_mappings:
            source, destination = mapping["input_path"], mapping["export_dir"]
            if self._excluded(source):
                continue
            if source.is_file():
                if source.suffix.lower() not in self._factories:
                    raise ConfigError(
                        f"Unsupported input file '{source}'. "
                        f"Supported extensions: {', '.join(sorted(self._factories))}."
                    )
                yield source, destination
            elif source.is_dir():
                yield from self._walk_sources(source, destination, output_roots)
            else:
                raise ConfigError(
                    f"Input path '{source}' does not exist or is not a file/directory."
                )

    def _walk_sources(self, source: Path, destination: Path, output_roots: set[Path]):
        def onerror(error):
            raise error

        for current, directories, filenames in os.walk(source, onerror=onerror):
            folder = Path(current)
            directories[:] = sorted(
                name
                for name in directories
                if name not in IGNORED_DIRECTORIES
                and not (folder / name).is_symlink()
                and not self._excluded(folder / name)
                and (folder / name).resolve() not in output_roots
            )

            for name in sorted(filenames):
                entry = folder / name
                if (
                    entry.suffix.lower() in self._factories
                    and not entry.is_symlink()
                    and not self._excluded(entry)
                ):
                    yield entry, destination / folder.relative_to(source)

    def plan(self) -> list[ExportTask]:
        """Discover all tasks before writing, so collisions cannot overwrite sources."""
        tasks = []
        seen = set()
        for source, destination in self._sources():
            identity = (source.resolve(), destination.resolve())
            if identity in seen:
                continue
            seen.add(identity)

            exporter = self._exporter(source.suffix.lower())
            try:
                outputs = exporter.output_paths(source, destination)
                tasks.append(ExportTask(source, destination, exporter, outputs))
            except (ExportError, OSError) as exc:
                tasks.append(ExportTask(source, destination, exporter, [], str(exc)))

        self._validate_outputs(tasks)
        return tasks

    @staticmethod
    def _validate_outputs(tasks: list[ExportTask]) -> None:
        # Case-folding also prevents portable projects from colliding on Windows/macOS.
        sources = {str(task.source.resolve()).casefold() for task in tasks}
        targets: dict[str, Path] = {}
        for task in tasks:
            for output in task.outputs:
                key = str(output.resolve()).casefold()
                if key in sources:
                    raise ConfigError(
                        f"Output '{output}' would overwrite an input. "
                        "Choose a separate output directory or another format."
                    )
                if key in targets:
                    raise ConfigError(
                        f"Output collision at '{output}' between "
                        f"'{targets[key]}' and '{task.source}'. "
                        "Rename a source or use separate mapping targets."
                    )
                if not output.resolve().is_relative_to(task.destination.resolve()):
                    raise ConfigError(f"Output '{output}' escapes its destination directory.")
                targets[key] = task.source

    def run(
        self, *, dry_run: bool = False, keep_going: bool = False, overwrite: bool = True
    ) -> ExportReport:
        report = ExportReport()
        for task in self.plan():
            result = ExportResult(str(task.source), [str(p) for p in task.outputs], "planned")
            try:
                if task.error:
                    raise ExportError(task.error)
                if not overwrite and any(output.exists() for output in task.outputs):
                    result.status = "skipped"
                    result.message = "An output already exists (--no-overwrite)."
                elif not dry_run:
                    task.exporter.export(task.source, task.destination)
                    result.status = "exported"
                logger.info("%s: %s -> %s", result.status, task.source, ", ".join(result.outputs))
            except (ExportError, OSError) as exc:
                result.status = "failed"
                result.message = str(exc)
                logger.error(
                    "%s: %s", task.source, exc, exc_info=logger.isEnabledFor(logging.DEBUG)
                )
            report.results.append(result)
            if result.status == "failed" and not keep_going:
                break

        return report

    def export_file(self, input_file: Path, output_dir: Path) -> str | list[str]:
        """Convert a single file directly (batch collision checks require ``run``)."""
        suffix = Path(input_file).suffix.lower()
        if suffix not in self._factories:
            raise ConfigError(f"Unsupported input file '{input_file}'.")
        return self._exporter(suffix).export(input_file, output_dir)
