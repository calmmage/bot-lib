import textwrap

from aiogram.types import Message

from bot_lib import App, Handler, HandlerDisplayMode

from bot_lib import (
    setup_dispatcher,
)


def setup_dispatcher_new(dp, bot_config, extra_handlers=None):
    """
    Set up dispatcher with bot config and handlers
    """
    setup_dispatcher(dp, bot_config, extra_handlers=extra_handlers)


class MyHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL

    gpt_model = "gpt-4"
    gpt_max_tokens = 500
    gpt_temperature = 0.7
    # todo: get formatting enum from the bot (parse mode)

    gpt_system_message = textwrap.dedent(
        """
        You're telegram chat bot and you receive a conversation with the user
        Generate response using telegram HTML for formatting
        """
    ).strip()
    warmup_messages = [
        (
            "Hey, how are you?",
            "I'm great! Been checking out the <bold>latest</bold> GPT models",
        ),
    ]

    def build_warmup_messages(self):
        for user, assistant in self.warmup_messages:
            yield {"role": "user", "content": user}
            yield {"role": "assistant", "content": assistant}

    commands = {
        "chat_handler": "chat",
    }

    # todo: somehow auto-register this?
    async def chat_handler(self, message: Message, app: App):
        # Use self.app.gpt to generate a response
        user_message = self.strip_command(message.text)
        response = await app.gpt.complete_text(
            text=user_message,
            model=self.gpt_model,
            max_tokens=self.gpt_max_tokens,
            temperature=self.gpt_temperature,
            system=self.gpt_system_message,
            # warmup_messages=list(self.build_warmup_messages()),
            warmup_messages=self.warmup_messages,
        )
        await message.reply(response)
