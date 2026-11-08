"""Errors safe to present to CLI users without a Python traceback."""


class FigexportError(Exception):
    """Base class for expected operational errors."""


class ConfigError(FigexportError, ValueError):
    """Invalid configuration or input selection."""


class ExportError(FigexportError, RuntimeError):
    """A converter failed or did not produce its expected output."""
