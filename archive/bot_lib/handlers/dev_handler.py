from bot_lib.handlers import Handler, HandlerDisplayMode


class DevHandler(Handler):
    name = 'dev'
    display_mode = HandlerDisplayMode.HELP_MESSAGE

    async def ping_handler(self, message):
        await message.answer("ping")
