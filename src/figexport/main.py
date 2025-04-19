import argparse
import json
from pathlib import Path

from figexport.config import ExportConfig
from figexport.export_manager import ExportManager


# Path of default config file: <cwd>/figexport_config.json
DEFAULT_CONFIG_FILE = Path("figexport_config.json")


def parse_config_file(config_file: Path, args: argparse.Namespace) -> dict:
    """Parses the configuration file and returns its content as a dictionary.

    Args:
        config_file: Path to the configuration file.
        args: Parsed command-line arguments, potentially containing
              override values.
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Config file '{config_file}' not found.")

    try:
        with open(config_file, "r") as f:
            config_dict = json.load(f)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in '{config_file}'.")

    # Set override values from command line arguments if provided
    if args.format:
        config_dict['export_format'] = args.format

    return config_dict


def parse_args() -> argparse.Namespace:
    """Parses the command-line arguments."""
    parser = argparse.ArgumentParser(description="Export figures.")

    parser.add_argument(
        "-c", "--config", type=Path, default=DEFAULT_CONFIG_FILE,
        help="Path to the configuration JSON file. Default: \"figexport_config.json\""
    )

    parser.add_argument(
        "-f", "--format", type=str, default=None,
        help="Format of the exported figures: pdf, svg, png, jpg."
             " Default: value in config file, or \"pdf\" if not specified."
    )

    parser.add_argument(
        "path", nargs="?", type=Path, default=None,
        help="Path to a file or folder to export. If not provided, "
             "the path(s) from the configuration file will be used."
    )

    return parser.parse_args()


def main():
    """Main function of the figexport command line tool."""
    args = parse_args()

    # Get the absolute path of the config file and the input path
    config_file_path = args.config.resolve()
    input_path = args.path.resolve() if args.path else None

    # Create the export configuration object
    config_dict = parse_config_file(config_file_path, args)
    config = ExportConfig(config_dict, config_file_path.parent, input_path)

    # Initialize the export manager and run it
    pdf_exporter = ExportManager(config)
    pdf_exporter.run()


if __name__ == "__main__":
    main()
