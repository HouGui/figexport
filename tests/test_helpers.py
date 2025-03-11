import os


def is_valid_file(file_path: str, extension: str) -> bool:
    """Checks if a file exists, has the correct extension, and is not empty.

    Args:
        file_path: The path to the file.
        extensions: A list of valid file extensions.

    Returns:
        True if the file is valid, False otherwise.
    """
    right_extension = os.path.isfile(file_path) \
                      and file_path.lower().endswith(extension)
    not_empty = os.path.getsize(file_path) > 0
    return  right_extension and not_empty
