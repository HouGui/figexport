import re
from pathlib import Path

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException

from figexport.errors import ExportError
from figexport.export.enums import ExportFormat
from figexport.export.fig_exporter import FigExporter
from figexport.tools import find_drawio, run_command


class DrawioExporter(FigExporter):
    def __init__(
        self,
        drawio_path: str | Path | None = None,
        export_format: ExportFormat = ExportFormat.PDF,
        *,
        timeout: float = 120,
    ) -> None:
        super().__init__(export_format, timeout=timeout)
        self.drawio_path = drawio_path
        self._page_offset: int | None = None

    def is_drawio_installed(self) -> bool:
        return find_drawio(self.drawio_path) is not None

    @staticmethod
    def parse_page_names(input_file: str | Path) -> list[str]:
        try:
            root = ElementTree.parse(input_file).getroot()
        except (ElementTree.ParseError, DefusedXmlException) as exc:
            raise ExportError(f"Invalid draw.io XML in '{input_file}': {exc}") from exc
        if root.tag == "mxGraphModel":
            return ["Page_0"]
        diagrams = root.findall("diagram")
        if root.tag != "mxfile" or not diagrams:
            raise ExportError(f"No draw.io pages found in '{input_file}'.")
        return [diagram.get("name") or f"Page_{index}" for index, diagram in enumerate(diagrams)]

    def output_paths(self, input_file: Path, output_dir: Path) -> list[Path]:
        used = set()
        outputs = []
        for index, name in enumerate(self.parse_page_names(input_file)):
            # Page names must work on Windows too, including separators and controls.
            safe = re.sub(r'[<>:"/\\|?*\s\x00-\x1f]', "_", name).strip(". ")[:100]
            safe = safe or f"Page_{index}"
            unique, count = safe, 2
            while unique.casefold() in used:
                unique = f"{safe}_{count}"
                count += 1
            used.add(unique.casefold())
            outputs.append(output_dir / f"{input_file.stem}_{unique}.{self.format.value}")
        return outputs

    def _convert(self, source: Path, outputs: list[Path]) -> None:
        executable = find_drawio(self.drawio_path)
        if not executable:
            raise ExportError(
                "draw.io Desktop was not found. Install it or set "
                "tools.drawio.exe_path in your configuration."
            )
        if self._page_offset is None:
            version_output = run_command([executable, "--version"], timeout=self.timeout)
            version = re.search(rb"(?m)^v?(\d+)\.(\d+)\.(\d+)\s*$", version_output)
            if version is None:
                raise ExportError("Could not detect the draw.io version from --version output.")
            # draw.io changed its page-index convention in 27.0.2.
            self._page_offset = int(tuple(map(int, version.groups())) >= (27, 0, 2))
        for page, output in enumerate(outputs, start=self._page_offset):
            run_command(
                [
                    executable,
                    "--export",
                    "--format",
                    self.format.value,
                    "--output",
                    str(output),
                    "--crop",
                    "--page-index",
                    str(page),
                    str(source),
                ],
                timeout=self.timeout,
            )
