from pathlib import Path

from figexport.export.enums import ExportFormat


class ExportConfig:
    """Export configuration settings of the figexport tool.

    Attributes:
        base_dir (Path): The base directory of the export process
                         (where the JSON file is located).
        export_dir (Path): The directory where the figures will be exported.
        export_format (ExportFormat): The format to export the figures to.
        export_mappings list[dict]: List of dictionaries containing the
                                    specified input and export directories.
        plantuml_url (str): The URL to download the PlantUML jar file.
        plantuml_path (Path): The path to the PlantUML jar file.
    """
    def __init__(self, config_dict: dict, base_dir_path: Path, input_path: Path | None):
        """Initializes the ExportConfig object using the given JSON file.

        Args:
            config_json: The path to the JSON configuration file.
            input_path: The command line interface path to export, overriding
                            the default directory(ies) in the config file.
        """
        self.base_dir = base_dir_path
        self.set_export_dir(config_dict)

        # Set the export format (default is PDF)
        if 'export_format' in config_dict:
            self.export_format = ExportFormat.from_str(config_dict['export_format'])
        else:
            self.export_format = ExportFormat.PDF

        # Set the directory mappings and excluded paths
        self.set_dir_mappings(input_path, config_dict.get('directory_mappings', []))
        self.set_skip_paths(config_dict.get('excluded_paths', []))

        self.set_tools_config(config_dict['tools'])

    def set_export_dir(self, config_dict: dict) -> str:
        """Sets the full path of the export directory based on the relative path.
        Args:
            export_dir: The directory where the PDF files will be exported.
        """
        #  Check if the key 'export_dir' is present
        if 'export_dir' in config_dict:
            rel_export_dir = config_dict['export_dir']
        else:
            rel_export_dir = '_export'
            print(f"'export_dir' parameter not specified."
                  f" Default value '{rel_export_dir}' is used.")

        if rel_export_dir == ".":
            self.export_dir = self.base_dir
        else:
            self.export_dir = self.base_dir / rel_export_dir

    def set_dir_mappings(self, input_path: Path, mappings: dict) -> None:
        """Sets the directory mappings of the export configuration.

        Args:
            input_path: The path to export the figures from to override
                        the default directory(ies) in the config file.
            mappings: The JSON content loaded from the configuration file.
        """
        if input_path:
            self.export_mappings = [{'input_path': input_path,
                                     'export_dir': self.export_dir}]
        else:
            if not mappings:
                raise ValueError("No input paths found in the configuration file.")

            # Set the input paths based on the 'input_paths' node in the JSON file
            self.export_mappings = [
                {
                    'input_path': self.base_dir / mapping['source'],
                    'export_dir': self.export_dir / mapping['target']
                } for mapping in mappings
            ]

        if not self.export_mappings:
            raise ValueError("No export mappings found in the configuration file.")

    def set_skip_paths(self, skip_paths: list) -> None:
        """Sets the paths to skip during the export process.

        Args:
            skip_paths: List of paths to skip during the export process.
        """
        self.skip_paths = [self.base_dir / path for path in skip_paths]

    def set_tools_config(self, tools_dict: dict) -> None:
        """Sets the configuration for the tools used in the export process.

        Args:
            config_dict: The JSON content loaded from the configuration file.
        """
        # PlantUML settings
        self.plantuml_url = tools_dict['plantuml']['download_url']
        self.plantuml_path = self.base_dir / tools_dict['plantuml']['jar_name']

        # Draw.io settings
        drawio_path = tools_dict.get('drawio', {}).get('exe_path')
        self.drawio_path = Path(drawio_path) if drawio_path else None
