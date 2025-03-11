import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

from figexport.export.fig_exporter import FigExporter
from figexport.export.enums import ExportFormat


class DrawioExporter(FigExporter):
    def __init__(self, 
                 export_format: ExportFormat = ExportFormat.PDF,
                 drawio_path = "C:\\Program Files\\draw.io\\draw.io.exe"):
        """Initializes the Draw.io exporter.

        Args:
            export_format: The image format to export.
            drawio_path: The path to the Draw.io executable, or the command if in PATH.
        """
        super().__init__(export_format)
        self.drawio_path = Path(drawio_path)

    def is_drawio_installed(self) -> bool:
        """Check if Draw.io is installed by checking its version."""
        try:
            subprocess.run([str(self.drawio_path), "--version"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def export(self, input_file: Path, output_dir: Path) -> str:
        """Export a Draw.io file to the specified format, using the actual page names.
        
        Args:
            input_file: drawio file to export.
            output_dir: The location where to store the exported files.
        
        Returns:
            Path of the exported file in case of one single page, 
            otherwise the list of exported file paths.
        """
        if not input_file.exists():
            raise FileNotFoundError(f'Input file "{input_file}" not found.')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = input_file.stem
        page_names = self.parse_page_names(input_file)
        
        output_files = []
        
        for page, page_name in enumerate(page_names):
            sanitized_name = page_name.replace(" ", "_")  # Ensure file-safe naming
            output_file = output_dir / f"{base_name}_{sanitized_name}.{self.format.value}"

            # Run the export command
            self._run_drawio(str(input_file), str(output_file), page, self.format.value)
            output_files.append(str(output_file))
        
        return output_files[0] if len(output_files) == 1 else output_files

    def parse_page_names(self, input_file: str) -> list:
        """Parses the names of all pages in a draw.io file.
        
        Args:
            input_file: The draw.io file to extract the page names from.
        """
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            diagrams = root.findall(".//diagram")

            # Extract names, or use index if no name is found
            page_names = [diag.get("name", f"Page_{idx}") for idx, diag in enumerate(diagrams)]
            return page_names
        except ET.ParseError:
            return ["Page_0"]  # Default to "Page_0" if parsing fails

    def _run_drawio(self, input_file: str, output_file: str, page: int, format: str) -> None:
        """Executes the Draw.io command to export the file."""
        command = [
            str(self.drawio_path), "--export", "--format", format,
            "--output", output_file, "--crop", "--page-index", str(page), input_file
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE)
    
    ### Required Abstract Methods ###
    def _to_svg(self, input_file: str, output_file_no_ext: str) -> str:
        return self._export_with_format(input_file, output_file_no_ext, "svg")

    def _to_png(self, input_file: str, output_file_no_ext: str) -> str:
        return self._export_with_format(input_file, output_file_no_ext, "png")

    def _to_jpg(self, input_file: str, output_file_no_ext: str) -> str:
        return self._export_with_format(input_file, output_file_no_ext, "jpg")

    def _to_pdf(self, input_file: str, output_file_no_ext: str) -> str:
        return self._export_with_format(input_file, output_file_no_ext, "pdf")

    def _export_with_format(self, input_file: str, output_file_no_ext: str, format: str) -> str:
        """Exports a Draw.io file to a specific format with proper page names."""
        output_dir = Path(output_file_no_ext).parent
        self.export(input_file, str(output_dir))  # Calls the main export function
        return f"{output_file_no_ext}.{format}"
