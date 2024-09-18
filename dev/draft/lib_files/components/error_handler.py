import traceback
from datetime import datetime

from aiogram import types
from pydantic_settings import BaseSettings

from dev.draft.easter_eggs.main import get_easter_egg
from dev.draft.lib_files.utils.common import get_logger

logger = get_logger()


class ErrorHandlingSettings(BaseSettings):
    enabled: bool = True
    easter_eggs: bool = True

    class Config:
        env_prefix = "ERROR_HANDLING_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


async def error_handler(event: types.ErrorEvent):
    """
    log error to the logger
    also send a message to the user
    """
    from dev.draft.lib_files.dependency_manager import get_dependency_manager

    deps = get_dependency_manager()

    error_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        "error": str(event.exception),
        "traceback": traceback.format_exc(),
    }

    logger.error(error_data["traceback"])
    # logger.debug(type(event.update))

    if event.update.message:
        response = "Oops, something went wrong :("
        if deps.nbl_settings.error_handling.easter_eggs:
            response += f"\nHere, take this instead: \n{get_easter_egg()}"

        await event.update.message.answer(response)
