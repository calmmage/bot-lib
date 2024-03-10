from bot_lib.plugins import Plugin

# from bot_lib.plugins import GptPlugin
from typing import List, Type


class App:
    def __init__(self, plugins: List[Type[Plugin]] = None):
        if plugins is None:
            plugins = []
        self.plugins = {plugin.name: plugin() for plugin in plugins}

    # @property
    # def gpt(self) -> GptPlugin:
    #     if "gpt" not in self.plugins:
    #         raise AttributeError("GPT plugin is not enabled.")
    #     return self.plugins["gpt"]
