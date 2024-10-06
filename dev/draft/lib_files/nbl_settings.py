from pydantic_settings import BaseSettings

from dev.draft.lib_files.components.error_handler import ErrorHandlingSettings
from dev.draft.lib_files.components.print_bot_url import PrintBotUrlSettings
from dev.examples.unsorted.database_mongodb.dp_mongo_comp import MongoDatabaseSettings


class NBLSettings(BaseSettings):
    """New Bot Library settings"""

    error_handling: ErrorHandlingSettings = ErrorHandlingSettings()
    mongo_database: MongoDatabaseSettings = MongoDatabaseSettings()
    print_bot_url: PrintBotUrlSettings = PrintBotUrlSettings()

    class Config:
        env_prefix = "NBL_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
