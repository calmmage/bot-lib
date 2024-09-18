"""
BotManager class is responsible for setting up the bot, dispatcher etc.
"""
from dev.draft.lib_files.settings import Settings


class BotManager:
    def __init__(self, **kwargs):
        self.settings = Settings(**kwargs)

    def setup_dispatcher(self, dp):
        """
        Idea: register a help command from the handler - manually
        :param dp:
        :return:
        """
        # handler = BasicHandler()

        # dp.message.register(handler.help_handler, Command("help"))
        pass