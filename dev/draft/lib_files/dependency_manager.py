from dev.draft.lib_files.nbl_settings import NBLSettings
from dev.draft.lib_files.utils.common import Singleton


class DependencyManager(metaclass=Singleton):
    def __init__(self, nbl_settings: NBLSettings = None):
        self._nbl_settings = nbl_settings

    @property
    def nbl_settings(self) -> NBLSettings:
        return self._nbl_settings


def get_dependency_manager() -> DependencyManager:
    return DependencyManager()
