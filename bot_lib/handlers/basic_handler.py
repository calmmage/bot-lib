from bot_lib.handlers import Handler, HandlerDisplayMode


class BasicHandler(Handler):
    name = 'basic'
    display_mode = HandlerDisplayMode.FULL

    async def start_handler(self, message):
        await message.answer("start")

    async def help_handler(self, message):
        await message.answer("help")
