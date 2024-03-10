from bot_lib.plugins import Plugin
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv


class GptPlugin(Plugin):
    name = "gpt"

    def __init__(self, api_key: str = None):
        # todo: use plugin config instead
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API key is required for GPT plugin. "
                "Please provide it as an argument "
                "or in the environment variable OPENAI_API_KEY."
            )
        self._gpt = AsyncOpenAI(api_key=api_key)
        # self._gpt.api_key = api_key

    async def complete_text(self, text: str, max_tokens: int = 100):
        response = await self._gpt.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
