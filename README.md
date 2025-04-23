# FigExport
`FigExport` is a package for automatic export of figures of [heterogeneous formats](#input-file-formats) 
to `PDF`, `SVG`, `PNG` or `JPG` files. 
It uses a JSON export configuration and includes a user-friendly command line interface (CLI).

**List of Contents:**
- [Input File Formats](#input-file-formats)
- [Installation](#installation)
- [Usage](#usage)
  - [Configuration File Example](#configuration-file-example)
  - [Command Line Arguments](#command-line-arguments)
- [Developer Section](#developer-section)
  - [Install from Source](#install-from-source)
- [License](#license)


## Input File Formats
`FigExport` supports the following input file formats:
* `.svg`: Vector graphic figures
* `.drawio`: Draw.io diagrams, created using the [Draw.io](https://www.drawio.com/) tool
* `.tex`: LaTeX documents, e.g., containing a TikZ figure (recommended: `\documentclass{standalone}`)
* `.puml`: PlantUML diagrams

> **Note:** Other file formats in the input folder(s) will be ignored during the export process.

## Installation
```sh
pip install figexport
```

## Usage
In `FigExport`, the main export object (class `ExportManager`) is configured with an `ExportConfig` object,
which can be initialized by parsing a JSON configuration file.
If not provided, the setting parameters in `ExportConfig` will be set to their default values.

In the CLI tool, the JSON configuration file can be directly passed to the `ExportManager` class
using the ``-c/--config`` option.

### Configuration File Parameters
> **Note:**
> The path parameters in the configuration file are interpreted as relative to the given the **`root_dir`**,
> except `directory_mappings/target`, which is interpreted as relative to the export directory.<br>
> In the CLI tool, the `root_dir` is set to the folder where the configuration file is located, or, if
> not provided, to the current working directory.

| Parameter          | Description                                             | Default value (if not specified) |
|--------------------|---------------------------------------------------------|----------------------------------|
| `export_dir`       | Path to the directory to save the exported figures to.  | `_export`                        |
| `export_format`    | The file format to export the figures in.               | `pdf`                            |

### Configuration File Example
`figexport_config.json`:
```json
{
    "export_dir": "export",
    "export_format": "pdf",
    "directory_mappings": [
        {
            "source": "figures_A",
            "target": "."
        },
        {
            "source": "figures_B",
            "target": "figures_B"
        }

    ],
    "excluded_paths": [
        "figures_A/subfolder_A1"
    ],
    "tools": {
        "drawio": {
            "exe_path": "C:/Program Files/Draw.io/draw.io.exe",
        },
        "plantuml": {
            "download_url": "https://github.com/plantuml/plantuml/releases/download/v1.2025.2/plantuml-1.2025.2.jar",
            "jar_name": "plantuml.jar"
        }
    }
}
```

### Command Line Arguments
* CLI usage: 
```bash
figexport [-h] [-c CONFIG] [-f FORMAT] [path]
```
* Positional arguments:

| Option             | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| path               | Path to a file or folder to export. If not provided, the path(s) from the configuration file will be used. |        

* Options:

| Option             | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| -h, --help         | Show the help message and exit                                        |
| -c/--config CONFIG | Path to the configuration JSON file. Default: "figexport_config.json" |
| -f/--format FORMAT | Format of the exported figures: pdf, svg, png, jpg. Default: value in config file, or "pdf" if not specified. |

## Developer Section
### Install from Source
> **Note:**
> To avoid potential dependency conflicts on your system, it is recommended to use a Python virtual environment.

* Clone this repository and create a Python virtual environment:
```sh
git clone https://github.com/HouGui/figexport.git && cd figexport
python -m venv env
```

* Activate the virtual environment, then install the package and its dependencies using `pip`:
```sh
pip install -e .[dev]
```
`-e` installs the package in editable mode, and `[dev]` includes the dev dependencies in the installation.

## License
You are free to use, modify, and distribute this software under the terms of the [MIT License](LICENSE).
