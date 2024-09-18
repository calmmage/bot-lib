"""
BotManager class is responsible for setting up the bot, dispatcher etc.
"""

from dev.draft.lib_files.components.error_handler import error_handler
from dev.draft.lib_files.dependency_manager import DependencyManager
from dev.draft.lib_files.nbl_settings import NBLSettings
from dev.draft.lib_files.utils.common import Singleton


class BotManager(metaclass=Singleton):
    def __init__(self, **kwargs):
        self.settings = NBLSettings(**kwargs)
        self.deps = DependencyManager(nbl_settings=self.settings)

    def setup_dispatcher(self, dp):
        """
        Idea: register a help command from the handler - manually
        :param dp:
        :return:
        """
        if self.settings.error_handling.enabled:
            dp.errors.register(error_handler)

    # def setup_bot(self, bot):
