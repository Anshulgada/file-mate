# Dynamically load the version from pyproject.toml using importlib.metadata
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("file-mate")  # Must match [project.name] in pyproject.toml
except PackageNotFoundError:
    __version__ = "0.0.0-dev"  # Fallback when not installed (e.g. in dev mode)
