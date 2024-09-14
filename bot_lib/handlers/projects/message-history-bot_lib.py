from bot_lib import Handler, HandlerDisplayMode
from calmapp import App
from functools import wraps
from aiogram import BaseMiddleware


class MyHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        "dummy_command_handler": "dummy_command",
        "get_messages_count_handler": "get_messages_count",
    }

    has_chat_handler = True

    async def chat_handler(self, message, app: MyApp):
        input_str = await self.get_message_text(message)
        output_str = app.invoke(input_str)
        await self.reply_safe(output_str, message)

    async def dummy_command_handler(self, message, app: MyApp):
        output_str = app.dummy_command()
        await self.reply_safe(output_str, message)

    async def get_messages_count_handler(self, message, app: MyApp):
        result = app.get_messages_count(chat_id=message.chat.id)
        output_str = f"Messages count: {result}"
        # output_str = app.dummy_command()
        await self.reply_safe(output_str, message)
        # await message.answer(output_str)


# class SaveIncomingMiddleware(BaseMiddleware):
#     async def on_process_message(self, message: types.Message, data: dict):
#         c.execute("INSERT INTO messages (chat_id, message_text, direction) VALUES (?, ?, ?)", (message.chat.id, message.text, 'incoming'))
#         conn.commit()
