import logging
import os
from pathlib import Path

from figexport.config import ExportConfig
from figexport.export.drawio_exporter import DrawioExporter
from figexport.export.puml_exporter import PumlExporter
from figexport.export.svg_exporter import SvgExporter
from figexport.export.tex_exporter import TexExporter


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


class ExportManager:
    """Manager of the figure export process.

    Attributes:
        config (ExportConfig): Export configuration object.
        selected_dir (str): The selected directory to export the figures from.
        latex_builder (LatexBuilder): Specialized worker object for processing
                                      .tex files.
        drawio_exporter (DrawioExporter): Specialized worker object for processing
                                          .drawio files.
    """
    def __init__(self, config: ExportConfig):
        """Initializes the ExportManager object.

        Args:
            config: The ExportConfig object containing the configuration settings.
        """
        self.config: ExportConfig = config

        # Initialize the different exporter objects
        self.svg_exporter = SvgExporter(config.export_format)
        self.drawio_exporter = DrawioExporter(config.drawio_path, config.export_format)
        self.latex_builder = TexExporter(config.export_format)
        self.puml_exporter = PumlExporter(config.plantuml_path, config.plantuml_url,
                                          config.export_format)

        # Create the export folder if it does not exist
        os.makedirs(self.config.export_dir, exist_ok=True)

    def run(self):
        """Iterates through the input paths and exports the figures."""
        for mapping in self.config.export_mappings:
            input_path = mapping['input_path']
            export_dir = mapping['export_dir']

            if input_path in self.config.skip_paths:
                logging.info(f"Skipping the path '{input_path}'...")
                continue

            if input_path.is_file():
                self.export_file(input_path, export_dir)
            elif input_path.is_dir():
                self.process_input_dir(input_path, export_dir)
            else:
                raise RuntimeError(f"Input path '{input_path}' is neither "
                                   "a file, nor a directory.")

    def process_input_dir(self, input_path: Path, export_path: Path,
                          rel_path: Path = Path()) -> None:
        """Processes the input directory and exports the figures.

        Args:
            input_path: The input directory to process.
            export_path: The export directory.
            rel_path: The relative path to the input directory.
        """
        logging.info(f'\n*** Exporting the directory "{input_path}"...')

        for entry in input_path.iterdir():
            if entry in self.config.skip_paths:
                logging.info(f"Skipping the path '{entry}'...")
                continue

            if entry.is_file():
                self.export_file(entry, export_path / rel_path)
            else:  # Handle directories: recursive process
                new_rel_path = rel_path / entry.name
                self.process_input_dir(entry, export_path, new_rel_path)

    def export_file(self, input_file: Path, output_dir: str) -> None:
        """Converts an SVG/Tikz/Draw.io/PlantUML file to a PDF file.

        Args:
            input_file: The path to the input SVG/TeX/PlantUML file.
            output_dir: The path to the output directory.
        """
        if input_file.suffix == ".svg":
            output_file = self.svg_exporter.export(input_file, output_dir)
        elif input_file.suffix == ".tex":
            output_file = self.latex_builder.export(input_file, output_dir)
        elif input_file.suffix == ".drawio":
            output_file = self.drawio_exporter.export(input_file, output_dir)
        elif input_file.suffix == ".puml":
            output_file = self.puml_exporter.export(input_file, output_dir)
        else:
            print(f'Unsupported input format: "{input_file}" -> skipping conversion.')
            return

        logging.info(f"{input_file} -> {output_file}")
