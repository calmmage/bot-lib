from pathlib import Path
from typing import Optional

from aiogram.enums import ParseMode
from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class DatabaseConfig(BaseSettings):
    conn_str: SecretStr = SecretStr("")
    name: str = ""

    model_config = {
        "env_prefix": "DATABASE_",
    }


class TelegramBotConfig(BaseSettings):
    token: SecretStr = SecretStr("")
    api_id: SecretStr = SecretStr("")
    api_hash: SecretStr = SecretStr("")

    send_long_messages_as_files: bool = True
    test_mode: bool = False
    allowed_users: list = []
    dev_message_timeout: int = 5 * 60  # dev message cleanup after 5 minutes

    parse_mode: Optional[ParseMode] = None
    send_preview_for_long_messages: bool = False

    model_config = {
        "env_prefix": "TELEGRAM_BOT_",
    }


DEFAULT_DATA_DIR = "app_data"


class AppConfig(BaseSettings):
    data_dir: Path = DEFAULT_DATA_DIR

    database: DatabaseConfig = DatabaseConfig()
    telegram_bot: TelegramBotConfig = TelegramBotConfig()
    # todo: use this setting. Deprecated
    enable_openai_api: bool = False
    enable_gpt_engine: bool = False
    openai_api_key: SecretStr = SecretStr("")

    # todo: use this setting
    enable_voice_recognition: bool = False
    process_audio_in_parallel: bool = False

    # todo: use this setting
    enable_scheduler: bool = False

    # todo: add extra {APP}_ prefix to all env vars?
    #  will this work?
    #  "env_prefix": "{APP}_TELEGRAM_BOT_",
