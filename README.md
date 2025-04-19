# FigExport
`FigExport` is a package for automatic export of figures of [heterogeneous formats](#input-file-formats) 
to `PDF`, `SVG`, `PNG` or `JPG` files. 
It uses a JSON export configuration and includes a user-friendly command line interface (CLI).

**List of Contents:**
- [Input File Formats](#input-file-formats)
- [Installation](#installation)
  - [Using Pip](#using-pip)
  - [Using Pre-built Executable](#using-pre-built-executable)
- [Usage](#usage)
  - [Configuration File Example](#configuration-file-example)
- [Developer Section](#developer-section)
  - [Install from Source](#install-from-source)
  - [Generate PyInstaller Executable](#generate-pyinstaller-executable)
- [License](#license)


## Input File Formats
`FigExport` supports the following input files formats:
* `.svg`: Vector graphic figures
* `.drawio`: Draw.io diagrams, created using the [Draw.io](https://www.drawio.com/) tool
* `.tex`: LaTeX documents, e.g., containing a TikZ figure (recommended: `\documentclass{standalone}`)
* `.puml`: PlantUML diagrams

> **Note:** Other file formats in the input folder(s) will be ignored during the export process.

## Installation
### Using Pip
```sh
pip install figexport
```

### Using Pre-built Executable
A self-contained package is available on a the [Releases page](https://github.com/HouGui/figexport/releases).
To install a specific executable version:
1. Download the zip file of the version you want to use.
2. Extract the downloaded file.

To start the application from a terminal at any time, add the folder containing the `figexport` executable to
your system path.

## Usage
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
  path                  Path to a file or folder to export. If not provided, the path(s) from the
                        configuration file will be used.

* Options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to the configuration JSON file. Default: "figexport_config.json"
  -f FORMAT, --format FORMAT
                        Format of the exported figures: pdf, svg, png, jpg. Default: value in config file,  
                        or "pdf" if not specified.
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

### Generate PyInstaller Executable
> **Note:**
> This step requires installing `FigExport` from source before (see [section](#install-from-source) above).

We use `PyInstaller` to generate a self-contained Windows executable for simple distribution:
```sh
cd src/figexport
pyinstaller main.py --name figexport
```

## License
You are free to use, modify, and distribute this software under the terms of the [MIT License](LICENSE).
