from io import BytesIO
from pathlib import Path

from figexport.errors import ExportError
from figexport.export.enums import ExportFormat
from figexport.export.fig_exporter import FigExporter
from figexport.utils import copy_file, save_jpeg


class SvgExporter(FigExporter):
    def _convert(self, source: Path, outputs: list[Path]) -> None:
        output = outputs[0]
        if self.format == ExportFormat.SVG:
            copy_file(source, output)
            return
        try:
            import cairosvg
        except (ImportError, OSError) as exc:
            raise ExportError(
                "SVG rendering requires Cairo. See docs/installation.md "
                f"for your operating system. Details: {exc}"
            ) from exc
        if self.format == ExportFormat.PDF:
            cairosvg.svg2pdf(url=str(source), write_to=str(output))
        elif self.format == ExportFormat.PNG:
            cairosvg.svg2png(url=str(source), write_to=str(output))
        else:
            png = cairosvg.svg2png(url=str(source))
            save_jpeg(BytesIO(png), output)
