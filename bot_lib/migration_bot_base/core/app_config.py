from typing import Optional

from aiogram.enums import ParseMode
from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


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
