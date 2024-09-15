from pydantic_settings import BaseSettings

from bot_lib.migration_bot_base.core.telegram_bot import TelegramBot as OldTelegramBot


class HandlerUtilsSettings(BaseSettings):

    class Config:
        extra = "ignore"


class HandlerUtils(OldTelegramBot):
    def __init__(self, **kwargs):
        self.config = HandlerUtilsSettings(**kwargs)
        super().__init__()
