# Configuration

Create a starting file with `figexport --init-config`, then edit it:

```json
{
  "export_dir": "_export",
  "export_format": "pdf",
  "directory_mappings": [
    {"source": "figures", "target": "."},
    {"source": "diagrams", "target": "diagrams"}
  ],
  "excluded_paths": ["figures/drafts"],
  "timeout": 120
}
```

Run `figexport -c figexport_config.json`. A positional CLI path replaces the input
mappings; `--format`, `--output-dir` and `--timeout` override their settings.
CLI exclusions are added to configured exclusions. Unknown keys and invalid
values are errors, so spelling mistakes cannot silently change an export.

| Setting | Default | Meaning |
| --- | --- | --- |
| `export_dir` | `_export` | Destination root |
| `export_format` | `pdf` | `pdf`, `svg`, `png` or `jpg` (case-insensitive; `jpeg` accepted) |
| `directory_mappings` | `[{"source": ".", "target": "."}]` | Non-empty list of source files/directories and destination subdirectories |
| `excluded_paths` | `[]` | Paths to skip, including descendants |
| `timeout` | `120` | Finite positive seconds per command or download connect/read |
| `tools` | `{}` | Optional tool locations and PlantUML download settings |

## Paths

Config paths are relative to the directory containing the config file, except
mapping `target`, which is relative to `export_dir`. An omitted `target` means `.`.
Targets must remain inside `export_dir`. Absolute source/output paths are allowed.
With the Python API, paths resolve against the explicit base directory.

CLI paths are relative to the working directory. `~` expands to the user directory;
environment variables in JSON are not expanded. On Windows, use forward slashes
or escape backslashes, for example `"C:/Program Files/draw.io/draw.io.exe"`.

## External tools

```json
{
  "tools": {
    "drawio": {"exe_path": "C:/Program Files/draw.io/draw.io.exe"},
    "plantuml": {"jar_name": "tools/plantuml.jar"}
  }
}
```

- `drawio.exe_path`: optional executable path or command name on PATH. Without it,
  FigExport checks PATH and common Windows/macOS installation locations.
- `plantuml.jar_name`: JAR location, default `plantuml.jar`. If absent and no
  download URL/checksum is configured, an installed `plantuml` command is used.
- `plantuml.download_url`: optional HTTPS URL. Download occurs only when exporting
  PlantUML and the JAR is missing. Pin a release URL for reproducible builds.
- `plantuml.sha256`: optional 64-digit hexadecimal checksum. When supplied, both
  existing and downloaded JARs are verified before use.

An SVG-only project needs no `tools` configuration. Downloaded tools are not
bundled in FigExport distributions.
