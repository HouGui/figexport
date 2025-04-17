# FigExport
`FigExport` is a package for automatic export of figures of various formats to `PDF`, `SVG`, `PNG` 
or `JPG` files. It uses a JSON export configuration and includes a command line interface (CLI).

**List of Contents:**
- [Supported Input Formats](#supported-input-formats)
- [Installation](#installation)
  - [Install using Pre-built Executable](#install-using-pre-built-executable)
  - [Install from Source](#install-from-source)
- [Generate PyInstaller Executable](#generate-pyinstaller-executable)
- [Usage](#usage)
  - [Configuration File Example](#configuration-file-example)
- [License](#license)


## Supported Input Formats
Currently, `FigExport` supports the following formats of input files:
* `.svg`: Vector Graphics, created, for example, using the tool Inkscape.
* `.tex`: Tikz figures in LaTeX.
* `.drawio`: Draw.io diagrams, created using the Draw.io tool.
* `.puml`: PlantUML diagrams, can be created in VS Code using the PlantUML extension.

> **Note:** Other input formats in the folder(s) to process will be ignored during the
> export process.

## Installation
### Install using Pip
```sh
pip install figexport
```

### Install Pre-built Executable
A self-contained package is available on a the [Releases page](https://github.com/HouGui/figexport/releases).
To install a specific executable version:
1. Download the zip file of the version you want to use.
2. Extract the downloaded file.

To start the application from a terminal at any time, add the folder containing the `figexport` executable to
your system path.

### Install from Source
> **Note:**
> To avoid potential dependency conflicts on your system, it is highly recommended to use a 
> Python virtual environment.

* Clone this repository and create a Python virtual environment:
```sh
git clone https://github.com/HouGui/figexport.git && cd figexport
python -m venv env
```

* Activate the virtual environment, then install the package and its dependencies using `pip`:
```sh
pip install .
```
If you want to install in editable mode, add `-e` before the `.`, and if you want to install the package with 
the development dependencies, add `[dev]` after the `.`.

## Generate PyInstaller Executable
> **Note:**
> This step requires installing `FigExport` from source before (see [section](#install-from-source) above).

We use `PyInstaller` to generate a self-contained Windows executable for simple distribution:
```sh
cd src/figexport
pyinstaller main.py --name figexport
```

### Configuration File Example
`figexport_config.json`:
```json
{
    "export_relative_dir": "export",
    "export_format": "pdf",
    "plantuml": {
        "url": "https://sourceforge.net/projects/plantuml/files/plantuml.jar/download",
        "filename": "plantuml.jar"
    },
    "export_mappings": [
        {
            "input_relative_path": "figures_A",
            "export_relative_dir": "."
        },
        {
            "input_relative_path": "figures_B",
            "export_relative_dir": "figures_B"
        }

    ],
    "skip_paths": [
        "figures_A/subfolder_A1"
    ]
}
```

### Command Line Arguments
To be continued...

## License
You are free to use, modify, and distribute this software under the terms of the [MIT License](LICENSE).
