from pydantic_settings import BaseSettings

from dev.draft.lib_files.components.bot_commands_menu import BotCommandsMenuSettings
from dev.draft.lib_files.components.error_handler import ErrorHandlerSettings
from dev.draft.lib_files.components.print_bot_url import PrintBotUrlSettings
from dev.examples.unsorted.database_mongodb.dp_mongo_comp import MongoDatabaseSettings


class NBLSettings(BaseSettings):
    """New Bot Library settings"""

    error_handling: ErrorHandlerSettings = ErrorHandlerSettings()
    mongo_database: MongoDatabaseSettings = MongoDatabaseSettings()
    print_bot_url: PrintBotUrlSettings = PrintBotUrlSettings()
    bot_commands_menu: BotCommandsMenuSettings = BotCommandsMenuSettings()

    class Config:
        env_prefix = "NBL_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
