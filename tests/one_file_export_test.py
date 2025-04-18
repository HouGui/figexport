import os

import pytest

from figexport.export.enums import ExportFormat
from figexport.export.drawio_exporter import DrawioExporter
from figexport.export.puml_exporter import PumlExporter
from figexport.export.svg_exporter import SvgExporter
from figexport.export.tex_exporter import TexExporter
from test_helpers import is_valid_file


class TestFileExport:
    """Test suite for exporting one file at a time to multiple formats."""

    @pytest.mark.parametrize("export_format", 
                             [ExportFormat.PDF, ExportFormat.SVG, 
                              ExportFormat.PNG, ExportFormat.JPG])
    def test_svg_export(self, test_dir: str, 
                        test_export_dir: str, export_format: ExportFormat) -> None:
        """Tests the conversion of an SVG file to multiple formats.

        Args:
            test_dir: The path of the test directory.
            test_export_dir: The path of the test export directory.
            export_format: The output format being tested.
        """
        svg_figure_path = os.path.join(test_dir, "test_folder1", "Rectangle1_svg.svg")

        # Convert the input SVG file
        svg_exporter = SvgExporter(export_format)
        output_file = svg_exporter.export(svg_figure_path, test_export_dir)

        # Assert that the exported file is valid
        assert is_valid_file(output_file, export_format.value), \
               f"Export failed for format: {export_format}"
        
    @pytest.mark.parametrize("export_format", 
                             [ExportFormat.PDF, ExportFormat.SVG,
                              ExportFormat.PNG, ExportFormat.JPG])
    def test_puml_export(self, 
                         plantuml_url: str, 
                         test_dir: str, 
                         test_export_dir: str,
                         export_format: ExportFormat) -> None:
        """Tests the conversion of a PlantUML file to multiple formats.

        Args:
            test_dir: The path of the test directory.
            test_export_dir: The path of the test export directory.
        """
        puml_figure_path = os.path.join(test_dir, "test_folder1", "Sequence1_puml.puml")

        jar_path = os.path.join(test_dir, "plantuml.jar")
        puml_exporter = PumlExporter(export_format, jar_path, plantuml_url)
        output_file = puml_exporter.export(puml_figure_path, test_export_dir)

        # Assert that the exported file is valid
        assert is_valid_file(output_file, export_format.value), \
               f"Export failed for format: {export_format}"
        
    @pytest.mark.parametrize("export_format", 
                             [ExportFormat.PDF, ExportFormat.SVG,
                              ExportFormat.PNG, ExportFormat.JPG])
    def test_drawio_export(self, test_dir: str, 
                           test_export_dir: str, export_format: ExportFormat) -> None:
        """Tests the conversion of a Drawio file to multiple formats.

        Args:
            test_dir: The path of the test directory.
            test_export_dir: The path of the test export directory.
        """
        drawio_figure_path = os.path.join(test_dir, "test_folder1", "Rectangle1_drawio.drawio")

        # Convert the input Drawio file
        drawio_exporter = DrawioExporter(export_format)
        output = drawio_exporter.export(drawio_figure_path, test_export_dir)

        # Assert that the exported file(s) are valid
        if isinstance(output, list):
            for file in output:
                assert is_valid_file(file, export_format.value), \
                       f"Export failed for format: {export_format}"
        else:
            assert is_valid_file(output, export_format.value), \
                   f"Export failed for format: {export_format}"
            
    @pytest.mark.parametrize("export_format",
                             [ExportFormat.PDF, ExportFormat.SVG,
                              ExportFormat.PNG, ExportFormat.JPG])
    def test_tikz_export(self, test_dir: str, 
                         test_export_dir: str, export_format: ExportFormat) -> None:
        """Tests the conversion of a TikZ file to an SVG file.

        Args:
            test_dir: The path of the test directory.
            test_export_dir: The path of the test export directory.
        """
        tikz_figure_path = os.path.join(test_dir, "test_folder1", "Rectangle1_tikz.tex")

        # Convert the input Drawio file
        tikz_exporter = TexExporter(export_format)
        output_file = tikz_exporter.export(tikz_figure_path, test_export_dir)

        # Assert that the exported file is valid
        assert is_valid_file(output_file, export_format.value), \
               f"Export failed for format: {export_format}"
