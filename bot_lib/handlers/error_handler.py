import pprint
import traceback
from datetime import datetime

from aiogram import types

from bot_lib.handlers.handlerbase import HandlerBase


class ErrorHandler(HandlerBase):
    # todo: rework to use reply_safe etc.

    async def error_handler(self, event: types.ErrorEvent, message: types.Message):
        # Get chat ID from the message.
        # This will vary depending on the library/framework you're using.
        chat_id = message.chat.id
        error_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            "error": str(event.exception),
            "traceback": traceback.format_exc(),
        }
        self.errors[chat_id].append(error_data)

        # Respond to the user
        await message.answer("Oops, something went wrong! Use /error or /explainerror command if you " "want details")

    commands = {
        "error_command_handler": "/error",
        "explain_error_command_handler": "/explainError",
    }

    # @mark_command("error", description="Get recent error text")
    async def error_command_handler(self, message: types.Message):
        chat_id = message.chat.id
        errors = self.errors[chat_id]
        if errors:
            error = errors[-1]
            error_message = pprint.pformat(error)
            filename = f"error_message_{error['timestamp']}.txt"
        else:
            error_message = "No recent error message captured"
            filename = ""
        await self.send_safe(
            text=error_message,
            chat_id=chat_id,
            reply_to_message_id=message.message_id,
            filename=filename,
            wrap=False,
        )

    # todo: add init check if gpt_engine is enabled
    # todo: add option to set up gpt engine at runtime (per user)
    # explain error
    # @mark_command("explainError", description="Explain error")
    async def explain_error_command_handler(self, message: types.Message):
        """
        Explain latest error with gpt
        """
        chat_id = message.chat.id
        errors = self.errors[chat_id]
        if errors:
            error = errors[-1]
            error_message = error["error"]
            filename = f"error_message_{error['timestamp']}.txt"
            gpt_answer = await self.app.gpt_engine.arun(
                prompt=error_message,
                user=message.from_user.username,
                system="Explain this error",
            )
            reply_message = f"GPT Explanation:\n{gpt_answer}"
        else:
            reply_message = "No recent error message captured"
            filename = ""
        await self.send_safe(
            text=reply_message,
            chat_id=chat_id,
            reply_to_message_id=message.message_id,
            filename=filename,
            wrap=False,
        )
