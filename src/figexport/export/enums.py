from enum import Enum


class ExportFormat(Enum):
    PDF = "pdf"
    SVG = "svg"
    PNG = "png"
    JPG = "jpg"

    @classmethod
    def from_str(cls, value: str) -> "ExportFormat":
        if isinstance(value, str):
            normalized = value.lower()
            if normalized == "jpeg":
                normalized = "jpg"
            try:
                return cls(normalized)
            except ValueError:
                pass
        raise ValueError(f"Invalid export format {value!r}; choose pdf, svg, png, or jpg.")
