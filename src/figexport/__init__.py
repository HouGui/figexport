"""Export heterogeneous figure sources to common image formats."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("figexport")
except PackageNotFoundError:
    __version__ = "0+unknown"
