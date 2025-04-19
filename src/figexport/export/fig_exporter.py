"""
Module for exporting images in various formats.

Classes:
    FigExporter: Abstract base class for image exporters.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from figexport.export.enums import ExportFormat


class FigExporter(ABC):
    """Abstract base class for image exporters."""

    def __init__(self, export_format: ExportFormat) -> None:
        """Empty constructor for the FigExporter class.

        Args:
            export_format: The format to which the image will be exported.
        """
        self.format = export_format

    def export(self, input_file: Path, output_dir: Path) -> str:
        """Exports the input file to the specified format.

        Args:
            input_file: The path of the input file.
            output_dir: The path of the output directory.
        """
        self._validate_paths(input_file, output_dir)

        try:
            if self.format == ExportFormat.PDF:
                return self._to_pdf(input_file, output_dir)
            elif self.format == ExportFormat.SVG:
                return self._to_svg(input_file, output_dir)
            elif self.format == ExportFormat.PNG:
                return self._to_png(input_file, output_dir)
            elif self.format == ExportFormat.JPG:
                return self._to_jpg(input_file, output_dir)
            else:
                raise ValueError("Unsupported format. "
                                 "Please use ExportFormat.PDF, ExportFormat.SVG, "
                                 "ExportFormat.PNG, or ExportFormat.JPG.")
        except Exception as e:
            print(f"Error during conversion: {e}")
            return None

    def _validate_paths(self, input_file: Path, output_dir: Path) -> Path:
        """Validates the input file and output directory paths.

        Args:
            input_file: The path of the input file.
            output_dir: The path of the output folder.
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file '{input_file}' not found.")
        output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _to_pdf(self, input_file: Path, output_dir: Path, suffix: str = "") -> str:
        """Converts the input file to a PDF file in the given output directory.

        Args:
            input_file: The path of the input file.
            output_folder: The path of the output directory.
            suffix: The suffix to add to the output file name. Default: empty string.
        """
        pass

    @abstractmethod
    def _to_svg(self, input_file: Path, output_dir: Path, suffix: str = "") -> str:
        """Converts the input file to an SVG file in the given output directory.

        Args:
            input_file: The path of the input file.
            output_dir: The path of the output directory.
            suffix: The suffix to add to the output file name. Default: empty string.
        """
        pass

    @abstractmethod
    def _to_png(self, input_file: Path, output_dir: Path, suffix: str = "") -> str:
        """Converts the input file to a PNG file in the given output directory.

        Args:
            input_file: The path of the input file.
            output_dir: The path of the output directory.
            suffix: The suffix to add to the output file name. Default: empty string.
        """
        pass

    @abstractmethod
    def _to_jpg(self, input_file: Path, output_dir: Path, suffix: str = "") -> str:
        """Converts the input file to a JPG file in the given output directory.

        Args:
            input_file: The path of the input file.
            output_dir: The path of the output directory.
            suffix: The suffix to add to the output file name. Default: empty string.
        """
        pass
