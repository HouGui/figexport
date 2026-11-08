from pathlib import Path
from tempfile import TemporaryDirectory

from figexport.errors import ExportError
from figexport.export.enums import ExportFormat
from figexport.export.fig_exporter import FigExporter
from figexport.export.svg_exporter import SvgExporter
from figexport.tools import run_command
from figexport.utils import copy_file


class TexExporter(FigExporter):
    def _convert(self, source: Path, outputs: list[Path]) -> None:
        output = outputs[0]
        # Keep compilation files away from both sources and the final export folder.
        with TemporaryDirectory(prefix="latex-", dir=output.parent) as temporary:
            build_dir = Path(temporary)
            command = [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                "-no-shell-escape",
                "-jobname=figure",
                f"-output-directory={build_dir}",
            ]
            if self.format != ExportFormat.PDF:
                command.append("-output-format=dvi")
            command.append(str(source))
            run_command(command, cwd=source.parent, timeout=self.timeout)
            if self.format == ExportFormat.PDF:
                compiled = build_dir / "figure.pdf"
            else:
                compiled = build_dir / "figure.svg"
                run_command(
                    [
                        "dvisvgm",
                        "--no-fonts",
                        "--exact",
                        "--page=1",
                        f"--output={compiled}",
                        str(build_dir / "figure.dvi"),
                    ],
                    cwd=source.parent,
                    timeout=self.timeout,
                )
            if not compiled.is_file() or not compiled.stat().st_size:
                raise ExportError(f"LaTeX did not produce '{compiled.name}'.")
            if self.format in (ExportFormat.PDF, ExportFormat.SVG):
                copy_file(compiled, output)
            else:
                SvgExporter(self.format, timeout=self.timeout)._convert(compiled, outputs)
