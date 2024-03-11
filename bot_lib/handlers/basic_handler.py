from bot_lib.core import App

from bot_lib.handlers import Handler, HandlerDisplayMode


class BasicHandler(Handler):
    name = "basic"
    display_mode = HandlerDisplayMode.FULL
    commands = {"start_handler": "start", "help_handler": "help"}

    async def start_handler(self, message, app: App):
        response_text = app.get_start_message()
        await message.answer(response_text)

    async def help_handler(self, message, app: App):
        response_text = app.get_help_message()
        await message.answer(response_text)
