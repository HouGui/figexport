"""Register source extensions here when adding a conversion backend."""

from collections.abc import Callable

from figexport.config import ExportConfig
from figexport.export.drawio_exporter import DrawioExporter
from figexport.export.fig_exporter import FigExporter
from figexport.export.puml_exporter import PumlExporter
from figexport.export.svg_exporter import SvgExporter
from figexport.export.tex_exporter import TexExporter

ExporterFactory = Callable[[ExportConfig], FigExporter]

EXPORTERS: dict[str, ExporterFactory] = {
    ".svg": lambda config: SvgExporter(config.export_format, timeout=config.timeout),
    ".tex": lambda config: TexExporter(config.export_format, timeout=config.timeout),
    ".drawio": lambda config: DrawioExporter(
        config.drawio_path, config.export_format, timeout=config.timeout
    ),
    ".puml": lambda config: PumlExporter(
        config.plantuml_path,
        config.plantuml_url,
        config.export_format,
        timeout=config.timeout,
        sha256=config.plantuml_sha256,
    ),
}
