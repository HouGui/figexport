"""Small filesystem and image helpers shared by conversion backends."""

import shutil
from pathlib import Path


def copy_file(input_file: str | Path, output_file: str | Path) -> str:
    source, target = Path(input_file), Path(output_file)
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != target.resolve():
        shutil.copyfile(source, target)
    return str(target)


def save_jpeg(png_source, output_file: Path) -> None:
    """Composite transparency onto white instead of turning it black."""
    from PIL import Image

    with Image.open(png_source) as image:
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        background.save(output_file, "JPEG", quality=95)
