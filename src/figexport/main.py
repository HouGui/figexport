import argparse
from pathlib import Path

from figexport.config import ExportConfig
from figexport.export_manager import ExportManager


# Path of default config file: <cwd>/figexport_config.json
DEFAULT_CONFIG_FILE = Path("figexport_config.json")


def parse_args() -> argparse.Namespace:
    """Parses the command-line arguments."""
    parser = argparse.ArgumentParser(description="Export figures.")

    parser.add_argument(
        "-c", "--config", type=Path, default=DEFAULT_CONFIG_FILE,
        help="Path to the configuration JSON file."
    )

    parser.add_argument(
        "-f", "--format", type=str, default=None,
        help="Format of the exported figures: pdf, svg, png, jpg."
    )

    parser.add_argument(
        "path", nargs="?", type=Path, default=None, 
         help="Path to a file or folder to export. If not provided, "
              "the path(s) from the configuration file will be used."
    )
    
    return parser.parse_args()


def main():
    """Main function of the figexport tool."""
    args = parse_args()
    
    # Resolve absolute paths
    cli_input_path = args.path.resolve() if args.path else None
    config_file_path = args.config.resolve()
    
    # Create the export configuration object
    config = ExportConfig(config_file_path, cli_input_path, args.format)
    
    # Initialize the export manager and run it
    pdf_exporter = ExportManager(config)
    pdf_exporter.run()


if __name__ == "__main__":
    main()
