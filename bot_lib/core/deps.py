from bot_lib.core.handler_utils import HandlerUtils


# todo: bind Deps to the Handler with BotManager
class Deps:
    def __init__(self, **kwargs):
        self._handler_utils = HandlerUtils(**kwargs)

    @property
    def handler_utils(self) -> HandlerUtils:
        return self._handler_utils
