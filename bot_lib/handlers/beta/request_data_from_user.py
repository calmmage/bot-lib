import asyncio

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot_lib import HandlerBase, HandlerDisplayMode


class CustomState(StatesGroup):
    Waiting = State("waiting_for_user_input")


class ExtensionHandler(HandlerBase):

    # Shared dictionary to store user inputs

    # region Move to base Handler
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_inputs = {}

    async def get_info_from_user(self, message: Message, question: str, state: FSMContext):
        chat_id = message.chat.id
        await state.set_state(CustomState.Waiting)
        # Create an Event for this specific chat
        if chat_id not in self.user_inputs:
            self.user_inputs[chat_id] = {"event": asyncio.Event(), "input": None}

        # Send the question
        await self.reply_safe(message, question)

        # Wait for the input
        await self.user_inputs[chat_id]["event"].wait()

        # Get and clear the input
        user_input = self.user_inputs[chat_id]["input"]
        self.user_inputs[chat_id]["input"] = None
        self.user_inputs[chat_id]["event"].clear()

        return user_input

    async def handle_user_input(self, message: Message, state: FSMContext):
        chat_id = message.chat.id

        if chat_id in self.user_inputs:
            # Store the user's input
            self.user_inputs[chat_id]["input"] = await self.get_message_text(message)
            # Set the event to unblock the waiting task
            self.user_inputs[chat_id]["event"].set()

        # Clear the state
        await state.clear()

    async def sample_request_data_command(self, message: types.Message, state: FSMContext):
        message_from_user = await self.get_message_text(message)
        message_from_user = self.strip_command(message_from_user)
        if not message_from_user:
            message_from_user = await self.get_info_from_user(
                message, "Please provide some data for the request", state
            )
        await self.reply_safe(message, "You provided: " + message_from_user)

    def register_extra_handlers(self, router):
        super().register_extra_handlers(router)
        router.message.register(self.handle_user_input, CustomState.Waiting)
        return router

    name = "main"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        "sample_request_data_command": ["sample_request_data_command"],
    }
