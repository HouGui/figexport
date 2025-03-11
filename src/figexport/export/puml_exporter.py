import subprocess
from pathlib import Path

from PIL import Image
import requests

from figexport.export.fig_exporter import FigExporter
from figexport.export.svg_exporter import SvgExporter
from figexport.export.enums import ExportFormat
from figexport.utils import get_output_file


class PumlExporter(FigExporter):
    def __init__(self, jar_path: str, plantuml_url: str, 
                 export_format: ExportFormat = ExportFormat.PDF):
        """Initializes the PlantUML exporter.

        Args:
            jar_path (str): The path to the PlantUML JAR file.
            plantuml_url: The URL to download PlantUML if not found.
            export_format: The image format to export.
        """
        super().__init__(export_format)
        self.jar_path = Path(jar_path)
        self.plantuml_url = plantuml_url
        self.svg_exporter = SvgExporter(self.format)

        self._ensure_plantuml_exists()

    def _ensure_plantuml_exists(self) -> None:
        """Ensures the PlantUML JAR file is available, downloading it if necessary.
        """
        if not self.jar_path.exists():
            print(f"{self.jar_path} not found. Downloading...")
            try:
                response = requests.get(self.plantuml_url, stream=True)
                response.raise_for_status()
                with open(self.jar_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"{self.jar_path} downloaded successfully.")
            except requests.RequestException as e:
                raise RuntimeError(f"Error downloading PlantUML: {e}")
        else:
            print(f"{self.jar_path} found, skipping download.")

    def _get_file_stem(self, file_path: str) -> str:
        """Returns the filename without extension.
        
        Args:
            file_path: The path of the file.
        """
        return Path(file_path).stem

    def _run_plantuml(self, 
                      input_file: str, 
                      output_format: str, 
                      output_dir: str) -> None:
        """Executes the PlantUML JAR with the given input file and format.
        
        Args:
            input_file: The path to the input PUML file.
            output_format: The output format (e.g., "svg", "png").
            output_dir: The output directory.
        """
        command = ["java", "-jar", str(self.jar_path), f"-t{output_format}",
                   input_file, "-charset", "UTF-8", "-o", output_dir]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("Error during PlantUML conversion: "
                               f"{e.stderr.decode()}")

    def _to_pdf(self, input_file: Path, output_dir: Path) -> str:
        """Converts a PUML file to PDF via an intermediate SVG.

        Args:
            input_file: The path to the input PUML file.
            output_dir: Path of the output directory.
        """
        # Create a __puml_temp folder to store the intermediate SVG file
        temp_dir = output_dir / "__puml_temp"

        svg_file = self._to_svg(input_file, temp_dir)
        output_file = self.svg_exporter.export(Path(svg_file), output_dir)

        # Remove the temporary SVG file and directory
        Path(svg_file).unlink()
        temp_dir.rmdir()

        return output_file

    def _to_svg(self, input_file: Path, output_dir: Path) -> str:
        self._run_plantuml(input_file, "svg", output_dir)
        return get_output_file(input_file, output_dir, ExportFormat.SVG)

    def _to_png(self, input_file: Path, output_dir: Path, suffix: str = "") -> str:
        output_file = get_output_file(input_file, output_dir, ExportFormat.PNG, suffix)
        
        # If suffix is provided, generate in a __temp folder
        if suffix:
            temp_dir = output_dir / "__puml_temp"
            self._run_plantuml(input_file, "png", temp_dir)
            temp_output_file = get_output_file(input_file, temp_dir, ExportFormat.PNG)

            # Move the output file to the target location and remove the temp folder
            Path(temp_output_file).rename(output_file)
            temp_dir.rmdir()
        else:
            self._run_plantuml(input_file, "png", output_dir)

        return output_file

    def _to_jpg(self, input_file: Path, output_dir: Path) -> str:
        # Convert PUML to PNG first
        temp_png_file = self._to_png(input_file, output_dir, "__temp")

        # Convert PNG to JPG
        output_path = get_output_file(input_file, output_dir, ExportFormat.JPG)
        with Image.open(temp_png_file) as img:
            img.convert("RGB").save(output_path, "JPEG")

        # Clean up temporary PNG
        Path(temp_png_file).unlink()

        return output_path
