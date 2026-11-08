"""Common output planning, validation and staged conversion."""

from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory

from figexport.errors import ExportError
from figexport.export.enums import ExportFormat


class FigExporter(ABC):
    def __init__(
        self, export_format: ExportFormat = ExportFormat.PDF, *, timeout: float = 120
    ) -> None:
        self.format = export_format
        self.timeout = timeout

    def output_paths(self, input_file: Path, output_dir: Path) -> list[Path]:
        return [output_dir / f"{input_file.stem}.{self.format.value}"]

    def export(self, input_file: Path, output_dir: Path) -> str | list[str]:
        """Publish complete outputs only; conversion failure preserves existing files."""
        source, destination = Path(input_file).resolve(), Path(output_dir).resolve()
        if not source.is_file():
            raise ExportError(f"Input file '{source}' does not exist.")
        outputs = self.output_paths(source, destination)
        for output in outputs:
            if output.resolve() == source:
                raise ExportError(
                    f"Output would overwrite source '{source}'; choose another directory."
                )
            if not output.resolve().is_relative_to(destination):
                raise ExportError(f"Output '{output}' escapes its destination directory.")
        destination.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".figexport-", dir=destination) as temporary:
            staged = [Path(temporary) / output.name for output in outputs]
            try:
                self._convert(source, staged)
                for output in staged:
                    if not output.is_file() or output.stat().st_size == 0:
                        raise ExportError(f"Converter did not create a non-empty '{output.name}'.")
                for output, final in zip(staged, outputs, strict=True):
                    output.replace(final)
            except ExportError:
                raise
            except Exception as exc:
                raise ExportError(f"Could not export '{source}': {exc}") from exc
        paths = [str(output) for output in outputs]
        return paths[0] if len(paths) == 1 else paths

    @abstractmethod
    def _convert(self, source: Path, outputs: list[Path]) -> None:
        """Write each planned output into the supplied temporary directory."""
