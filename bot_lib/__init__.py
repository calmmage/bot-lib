from importlib.metadata import PackageNotFoundError
from calmapp import App
from calmapp import plugins

from .core import BotManager, setup_dispatcher, BotConfig
from .handlers import Handler, HandlerDisplayMode

try:
    import importlib.metadata

    __version__ = importlib.metadata.version(__package__ or __name__)
    del importlib
except PackageNotFoundError:
    import toml
    from pathlib import Path

    path = Path(__file__).parent.parent / "pyproject.toml"
    __version__ = toml.load(path)["tool"]["poetry"]["version"]
    del toml, Path, path
