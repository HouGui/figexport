import os
from pathlib import Path

import cairosvg
from PIL import Image

from figexport.export.fig_exporter import FigExporter
from figexport.export.enums import ExportFormat
from figexport.utils import get_output_file, copy_file


class SvgExporter(FigExporter):
    def __init__(self, export_format: ExportFormat = ExportFormat.PDF):
        """Initializes the SVG exporter.

        Args:
            export_format: The image format to export.
        """
        super().__init__(export_format)

    def _to_pdf(self, input_file: Path, output_folder: Path, suffix: str = "") -> str:
        # Get the output file path (same stem as input file)
        output_file = get_output_file(input_file, output_folder, ExportFormat.PDF, suffix)

        cairosvg.svg2pdf(url=str(input_file), write_to=output_file)
        return str(output_file)

    def _to_svg(self, input_file: Path, output_folder: Path, suffix: str = "") -> str:
        output_file = get_output_file(input_file, output_folder, ExportFormat.SVG, suffix)
        copy_file(str(input_file), output_file)
        return output_file

    def _to_png(self, input_file: Path, output_folder: Path, suffix: str = "") -> str:
        output_file = get_output_file(input_file, output_folder, ExportFormat.PNG, suffix)
        cairosvg.svg2png(url=str(input_file), write_to=output_file)
        return output_file

    def _to_jpg(self, input_file: Path, output_folder: Path, suffix: str = "") -> str:
        output_file = get_output_file(input_file, output_folder, ExportFormat.JPG, suffix)

        # Path of temporary intermediate PNG file
        temp_png_path = str(output_folder / f"{input_file.stem}__temp.png")

        cairosvg.svg2png(url=str(input_file), write_to=temp_png_path)
        img = Image.open(temp_png_path)
        img.convert("RGB").save(output_file, "JPEG")
        os.remove(temp_png_path)

        return output_file
