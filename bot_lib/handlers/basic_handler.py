import traceback
from datetime import datetime

from aiogram import types
from calmapp import App

from bot_lib.handlers import Handler, HandlerDisplayMode


class BasicHandler(Handler):
    name = "basic"
    display_mode = HandlerDisplayMode.FULL
    commands = {"start_handler": "start", "help_handler": "help"}

    @staticmethod
    async def start_handler(message, app: App):
        response_text = app.get_start_message()
        await message.answer(response_text)

    @staticmethod
    async def help_handler(message, app: App):
        response_text = app.get_help_message()
        await message.answer(response_text)

    has_error_handler = True

    # async def complex_error_handler(self, event: types.ErrorEvent, message: types.Message):
    #     # Get chat ID from the message.
    #     # This will vary depending on the library/framework you're using.
    #     chat_id = message.chat.id
    #     error_data = {
    #         "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
    #         "error": str(event.exception),
    #         "traceback": traceback.format_exc(),
    #     }
    #     # self.errors[chat_id].append(error_data)
    #
    #     # Respond to the user
    #     await message.answer("Oops, something went wrong! Use /error or /explain_error command if you " "want details")

    async def dummy_error_handler(self, event: types.ErrorEvent, message: types.Message):
        """
        log error to the logger
        also send a message to the user
        """

        error_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "error": str(event.exception),
            "traceback": traceback.format_exc(),
        }

        self.logger.error(error_data["traceback"])

        await message.answer("Oops, something went wrong :(")
