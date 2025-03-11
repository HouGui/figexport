import json
import os
from pathlib import Path

from figexport.export.enums import ExportFormat


class ExportConfig:
    """Export configuration settings of the figexport tool.

    Attributes:
        work_dir (Path): The working directory of the configuration 
                         (where the JSON file is located).
        export_dir (Path): The directory where the figures will be exported.
        export_format (ExportFormat): The format to export the figures to.
        export_mappings list[dict]: List of dictionaries containing the 
                                    specified input and export directories.
        plantuml_url (str): The URL to download the PlantUML jar file.
        plantuml_path (Path): The path to the PlantUML jar file.
    """
    def __init__(self, config_json: Path, cli_input_path: Path, format: str):
        """Initializes the ExportConfig object using the given JSON file.

        Args:
            config_json: The path to the JSON configuration file.
            cli_input_path: The command line interface path to export, overriding
                            the default directory(ies) in the config file.
        """
        self.work_dir = config_json.parent
        
        # Read the configuration from the JSON file, if it exists
        if os.path.exists(config_json):
            self.read_config(config_json, cli_input_path, format)
        else:
            raise FileNotFoundError(f"Config file '{config_json}' not found.")

    def read_config(self, config_json: str, cli_input_path: Path, format: str) -> None:
        """Loads the configuration from the JSON file.

        Args:
            config_json: The path to the JSON configuration file.
            cli_input_path: The command line interface path to export, overriding
                            the default directory(ies) in the config file.
        """
        with open(config_json, "r") as f:
            json_content = json.load(f)

        self.set_export_dir(json_content['export_relative_dir'])
        if format:
            self.export_format = ExportFormat.from_str(format)
        else:
            self.export_format = ExportFormat.from_str(json_content['export_format'])

        # Set the PlantUML data
        self.plantuml_url = json_content['plantuml']['url']
        self.plantuml_path = self.work_dir / json_content['plantuml']['filename']

        # Set the input and skip paths
        self.set_export_mappings(cli_input_path, json_content)
        self.set_skip_paths(json_content.get('skip_paths', []))

    def set_export_dir(self, export_rel_dir: str) -> str:
        """Sets the export directory for the PDF files.

        If the export directory is ".", the export directory will be set 
        to an empty string.

        Args:
            export_dir: The directory where the PDF files will be exported.
        """
        if export_rel_dir == ".":
            # Set as full path relative to the working directory
            self.export_dir = self.work_dir
        else:
            self.export_dir = self.work_dir / export_rel_dir

    def set_export_mappings(self, input_path: Path, json_content: dict) -> None:
        """Sets the input folders for the configuration.

        Args:
            input_path: The path to export the figures from to override
                        the default directory(ies) in the config file.
            json_content: The JSON content loaded from the configuration file.
        """
        if input_path:
            self.export_mappings = [{'input_path': input_path, 
                                     'export_dir': self.export_dir}]
        else:
            # Set the input paths based on the 'input_paths' node in the JSON file
            self.export_mappings = [
                { 'input_path': self.work_dir / mapping['input_relative_path'], 
                  'export_dir': self.export_dir / mapping['export_relative_dir']
                } for mapping in json_content.get('export_mappings', [])
            ] 

        if not self.export_mappings:
            raise ValueError("No export mappings found in the configuration file.")
        
    def set_skip_paths(self, skip_paths: list) -> None:
        """Sets the paths to skip during the export process.

        Args:
            skip_paths: List of paths to skip during the export process.
        """
        self.skip_paths = [self.work_dir / path for path in skip_paths]
