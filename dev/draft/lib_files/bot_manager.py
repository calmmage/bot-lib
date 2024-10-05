"""
BotManager class is responsible for setting up the bot, dispatcher etc.
"""

from dev.draft.lib_files.components import error_handler

from dev.draft.lib_files.dependency_manager import DependencyManager
from dev.draft.lib_files.nbl_settings import NBLSettings
from dev.draft.lib_files.utils.common import Singleton

from dev.examples.unsorted.database_mongodb import dp_mongo_comp


class BotManager(metaclass=Singleton):
    def __init__(self, **kwargs):
        self.settings = NBLSettings(**kwargs)
        self.deps = DependencyManager(nbl_settings=self.settings)

        if self.settings.mongo_database.enabled:
            self.deps.mongo_database = dp_mongo_comp.initialise(self.settings.mongo_database)

    def setup_dispatcher(self, dp):
        """
        Idea: register a help command from the handler - manually
        :param dp:
        :return:
        """
        if self.settings.error_handling.enabled:
            error_handler.setup_dispatcher(dp)

        if self.settings.mongo_database.enabled:
            dp_mongo_comp.setup_dispatcher(dp)

    # def setup_bot(self, bot):
