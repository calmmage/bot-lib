from bot_lib.plugins import Plugin, GptPlugin

# from bot_lib.plugins import GptPlugin
from typing import List, Type
from bot_lib.migration_bot_base.core.app import App as OldApp


class App(OldApp):
    def __init__(self, plugins: List[Type[Plugin]] = None):
        if plugins is None:
            plugins = []
        self.plugins = {plugin.name: plugin() for plugin in plugins}

    @property
    def gpt(self) -> GptPlugin:
        if "gpt" not in self.plugins:
            raise AttributeError("GPT plugin is not enabled.")
        return self.plugins["gpt"]
