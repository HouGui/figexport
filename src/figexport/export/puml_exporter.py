import hashlib
import re
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import requests

from figexport.errors import ExportError
from figexport.export.enums import ExportFormat
from figexport.export.fig_exporter import FigExporter
from figexport.export.svg_exporter import SvgExporter
from figexport.tools import run_command
from figexport.utils import save_jpeg


class PumlExporter(FigExporter):
    def __init__(
        self,
        jar_path: str | Path = "plantuml.jar",
        plantuml_url: str | None = None,
        export_format: ExportFormat = ExportFormat.PDF,
        *,
        timeout: float = 120,
        sha256: str | None = None,
    ) -> None:
        super().__init__(export_format, timeout=timeout)
        self.jar_path = Path(jar_path).resolve()
        self.plantuml_url = plantuml_url
        self.sha256 = sha256

    def _verify_checksum(self, source: Path) -> None:
        if self.sha256:
            digest = hashlib.sha256()
            with source.open("rb") as stream:
                for chunk in iter(lambda: stream.read(65536), b""):
                    digest.update(chunk)
            if digest.hexdigest() != self.sha256:
                raise ExportError(f"PlantUML SHA-256 mismatch for '{source}'.")

    def _ensure_plantuml_exists(self) -> None:
        if self.jar_path.is_file():
            self._verify_checksum(self.jar_path)
            return
        if not self.plantuml_url:
            raise ExportError(
                "PlantUML JAR was not found. Set tools.plantuml.jar_name to "
                "an installed JAR, install plantuml on PATH, or explicitly "
                "configure tools.plantuml.download_url."
            )
        temporary = None
        try:
            self.jar_path.parent.mkdir(parents=True, exist_ok=True)
            with requests.get(self.plantuml_url, stream=True, timeout=self.timeout) as response:
                response.raise_for_status()
                if not response.url.startswith("https://"):
                    raise ExportError("PlantUML download redirected to an insecure URL.")
                with NamedTemporaryFile(
                    dir=self.jar_path.parent, suffix=".part", delete=False
                ) as stream:
                    temporary = Path(stream.name)
                    for chunk in response.iter_content(chunk_size=65536):
                        stream.write(chunk)
            if not temporary.stat().st_size:
                raise ExportError("PlantUML download was empty.")
            self._verify_checksum(temporary)
            temporary.replace(self.jar_path)
        except (requests.RequestException, OSError) as exc:
            raise ExportError(f"Could not download PlantUML: {exc}") from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def _command(self) -> list[str]:
        if (
            not self.jar_path.exists()
            and not self.plantuml_url
            and not self.sha256
            and (executable := shutil.which("plantuml"))
        ):
            return [executable]
        if not shutil.which("java"):
            raise ExportError("Java was not found; install a Java runtime and add it to PATH.")
        self._ensure_plantuml_exists()
        return ["java", "-Djava.awt.headless=true", "-jar", str(self.jar_path)]

    def _convert(self, source: Path, outputs: list[Path]) -> None:
        data = source.read_bytes()
        if len(re.findall(rb"(?im)^\s*@start\w+\b", data)) != 1:
            raise ExportError("Use one @start... diagram per PlantUML source file.")
        output = outputs[0]
        intermediate_format = (
            "png" if self.format in (ExportFormat.PNG, ExportFormat.JPG) else "svg"
        )
        rendered = run_command(
            self._command()
            + ["-pipe", f"-t{intermediate_format}", "-charset", "UTF-8", "-failfast2"],
            cwd=source.parent,
            input_data=data,
            timeout=self.timeout,
            binary_output=True,
        )
        if self.format in (ExportFormat.SVG, ExportFormat.PNG):
            output.write_bytes(rendered)
        else:
            with TemporaryDirectory(prefix="plantuml-", dir=output.parent) as temporary:
                intermediate = Path(temporary) / f"figure.{intermediate_format}"
                intermediate.write_bytes(rendered)
                if self.format == ExportFormat.JPG:
                    save_jpeg(intermediate, output)
                else:
                    SvgExporter(self.format, timeout=self.timeout)._convert(intermediate, outputs)
