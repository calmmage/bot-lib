from pydantic_settings import BaseSettings

from dev.draft.lib_files.components.error_handler import ErrorHandlingSettings


class NBLSettings(BaseSettings):
    """New Bot Library settings"""

    error_handling: ErrorHandlingSettings = ErrorHandlingSettings()

    class Config:
        env_prefix = "NBL_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
