from collections import defaultdict

from bot_lib.plugins import Plugin, GptPlugin

# from bot_lib.plugins import GptPlugin
from typing import List, Type
from bot_lib.migration_bot_base.core.app import App as OldApp


class App(OldApp):
    """"""

    name: str = None
    start_message = "Hello! I am {name}. {description}"
    help_message = "Help! I need somebody! Help! Not just anybody! Help! You know I need someone! Help!"

    def __init__(self, plugins: List[Type[Plugin]] = None):
        super().__init__()
        if plugins is None:
            plugins = []
        self.plugins = {plugin.name: plugin() for plugin in plugins}

    @property
    def gpt(self) -> GptPlugin:
        if "gpt" not in self.plugins:
            raise AttributeError("GPT plugin is not enabled.")
        return self.plugins["gpt"]

    @property
    def description(self):
        return self.__doc__

    def get_start_message(self):
        return self.start_message.format(name=self.name, description=self.description)

    def get_help_message(self):
        help_message = self.help_message
        if self.hidden_commands:
            help_message += "\n\nHidden commands:\n"
            for handler, commands in self.hidden_commands.items():

                help_message += f"\n{handler}:\n"
                for command in commands:
                    help_message += f"/{command}\n"

    hidden_commands = defaultdict(list)
