# Python API

```python
from pathlib import Path
from figexport.config import ExportConfig
from figexport.export_manager import ExportManager

config = ExportConfig(
    {"export_dir": "images", "export_format": "png"},
    base_dir_path=Path.cwd(),
    input_path=Path("figures"),
)
manager = ExportManager(config)
report = manager.run(keep_going=True)
print(report.to_dict())
if report.failed:
    raise RuntimeError("Some figures could not be exported")
```

`ExportConfig` validates settings and resolves paths. `ExportManager.plan()` returns
planned tasks without creating outputs. `run(dry_run=False, keep_going=False,
overwrite=True)` returns an `ExportReport`; per-file failures are recorded in the
report. Invalid configuration or output collisions raise `ConfigError`.

For one backend directly:

```python
from pathlib import Path
from figexport.export.enums import ExportFormat
from figexport.export.svg_exporter import SvgExporter

output = SvgExporter(ExportFormat.PNG).export(Path("logo.svg"), Path("images"))
```

`export()` returns a filename string, or a list for multi-page draw.io exports.
Failures raise `ExportError` or a filesystem `OSError`; callers must not assume a
failed export returns `None`. Constructors do not write files or download tools.

Use the [backend extension guide](developers/index.md#adding-a-converter) to support
another input format. Applications can pass a custom `exporters` registry to
`ExportManager` without modifying built-in behavior.
