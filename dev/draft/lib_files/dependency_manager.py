from aiogram import Bot

from dev.draft.lib_files.nbl_settings import NBLSettings
from dev.draft.lib_files.utils.common import Singleton


class DependencyManager(metaclass=Singleton):
    def __init__(self, nbl_settings: NBLSettings = None, bot: Bot = None, mongo_database=None):
        self._nbl_settings = nbl_settings
        self._bot = bot
        self._mongo_database = mongo_database

    @property
    def nbl_settings(self) -> NBLSettings:
        return self._nbl_settings

    # @nbl_settings.setter
    # def nbl_settings(self, value):
    #     self._nbl_settings = value

    @property
    def bot(self) -> Bot:
        return self._bot

    @bot.setter
    def bot(self, value):
        self._bot = value

    @property
    def mongo_database(self):
        return self._mongo_database

    @mongo_database.setter
    def mongo_database(self, value):
        self._mongo_database = value


def get_dependency_manager() -> DependencyManager:
    return DependencyManager()
