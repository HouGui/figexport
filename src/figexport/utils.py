import os
from pathlib import Path

from figexport.export.enums import ExportFormat


def get_output_file(input_file: Path, output_folder: Path, 
                    format: ExportFormat, suffix: str = "") -> str:
    """Gets the output file path without extension.

    Args:
        input_file: The path of the input file.
        output_folder: The path of the output folder.
        format: The export format.
        suffix: The suffix to append to the output file name.
    """
    extension = format.value.lower()
    return str(output_folder / f"{input_file.stem}{suffix}.{extension}")


def copy_file(input_file: str, output_file: str) -> str:
    """Copies a file to an output file path.

    Args:
        input_file: The path of the input file.
        output_file: The path of the output file.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(input_file, "r") as f:
        with open(output_file, "w") as f_out:
            f_out.write(f.read())
    return output_file
