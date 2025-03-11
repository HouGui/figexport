from enum import Enum


class ExportFormat(Enum):
    PDF = "pdf"
    SVG = "svg"
    PNG = "png"
    JPG = "jpg"

    @staticmethod
    def from_str(value: str) -> "ExportFormat":
        """Converts a string to an ExportFormat enum value."""
        try:
            return ExportFormat(value)
        except ValueError:
            raise ValueError(f"Invalid ExportFormat: {value}")
