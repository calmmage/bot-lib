import logging
import random
from textwrap import dedent
from typing import Union

from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.types import Message
from bot_lib import Handler, HandlerDisplayMode
from bot_lib.handlers.handler import HandlerConfig
from dotenv import load_dotenv
from loguru import logger
from pydantic_settings import BaseSettings

from ef_matchmaking_bot.app import MyApp
from ef_matchmaking_bot.handlers.side_scenarios_handler import SideScenarioState, SSS
from ef_matchmaking_bot.handlers.topic_generation_handler import GenerateTopicState, GTS
from generate_session_idea_dev.prompts.find_common_idea import MikhailVariantPrompt, VitalyVariantPrompt
from generate_session_idea_dev.prompts.petr_prompt import (
    PetrPrompt,
    PetrPromptExpensive,
    PetrPromptNoReasoning5Topics,
    PetrPromptOneWord10Topics,
    PetrPromptTriplet5Topics,
    PetrPromptHardToGuess5Topics,
    PetrPromptOneWordNoExtras10Topics,
    PetrPromptTripletNoExtras10Topics,
)
from generate_session_idea_dev.utils.resolvers import (
    get_possible_people_by_name,
    get_interest_for_person,
    get_person_by_tg_handle,
)

# load_dotenv("/Users/calm/work/code/seasonal/2024_06_jun/experiments/generate-session-idea-dev/.env")
load_dotenv()


class Settings(BaseSettings):
    org_chat_id: int = -1002144718775
    discord_requests_channel_link: str = "https://discordapp.com/channels/1106702799938519211/1141804622206484500"
    discord_posts_channel_link: str = "https://discordapp.com/channels/1106702799938519211/1138152320018952202"
    notion_whois_link: str = (
        "https://www.notion.so/engineering-friends/641eaea7c7ad4881bbed5ea096a4421a?v=ca225d7c2b7b4762987407f53e2ae458&pvs=4"
    )


settings = Settings()


class AppState(StatesGroup):
    start = State("Start")


class ChatWithGPT(StatesGroup):
    start = State("Поболтать с GPT")


class MyHandlerConfig(HandlerConfig):
    debug_mode: bool = False


class MyHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        "start_command": "/start",
        "help_command": "/help",
        "cancel_handler": "/cancel",
        # "custom_button_scenario": "custom_button_scenario",
    }
    _config_class = MyHandlerConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.config = MyHandlerConfig()
        self.state_handlers = {
            AppState.start: self.start_command,
            GTS.start: self.gts_start_handler,
            GTS.select_specific_person: self.gts_select_specific_person_handler,
            GTS.pick_for_me: self.gts_pick_for_me_handler,
            GTS.select_random_person: self.gts_select_random_person_handler,
            GTS.view_notion: self.gts_view_notion_handler,
            # side scenarios
            SideScenarioState.start: self.side_scenario_start_handler,
            #     SideScenarioState.scenario_1: self.side_scenario_1_meet_someone_new_handler(),
        }
        self._allowed_users = [x.lower() for x in self.config.allowed_users] or None

        # self._ef_members = None
        # members_list = os.getenv("EF_MEMBERS")
        # if members_list:
        #     self.ef_members = json.loads(members_list)
        # else:
        #     self.ef_members = list(self.ef_members_names.keys())
        # self.ef_members = [x.lower() for x in self.ef_members]
        self.ef_members = [x.lower() for x in self.ef_members_names]
        if "ltgags" in self.ef_members:
            self.ef_members.remove("ltgags")

    has_chat_handler = True
    # has_chat_handler = False

    async def chat_handler(self, message, app: MyApp, state: FSMContext):

        output_str = self.general_message + "\n" + self.help_message
        await self.answer_safe(message, output_str, reply_markup=ReplyKeyboardRemove())
        await state.clear()

    @staticmethod
    def get_state_name(state: State) -> str:
        return state.state.split(":", 1)[1]

    stop_scenario_keyword = "Отмена"
    # @router.message(CommandStart())
    general_message = "Привет, это бот для генерации тем разговора для EF! "
    start_message = f'Жми "{get_state_name(GTS.start)}, чтобы начать! '
    help_message = "Точка входа - /start"

    async def start_command(self, message: Message, state: FSMContext, **kwargs) -> None:
        await state.set_state(AppState.start)

        output_str = self.general_message + "\n" + self.start_message
        await self.answer_safe(
            message,
            output_str,
            reply_markup=self.get_keyboard(
                states=[GenerateTopicState.start, SideScenarioState.start], back_button=False
            ),
        )

    @classmethod
    def get_keyboard(cls, states: list, cancel_button=True, back_button=False):
        keyboard = []
        for state in states:
            if isinstance(state, State):
                state = cls.get_state_name(state)
            keyboard.append([KeyboardButton(text=state)])
        last_line = []
        if cancel_button:
            last_line.append(KeyboardButton(text=cls.stop_scenario_keyword))
        if back_button:
            last_line.append(KeyboardButton(text=cls.back_keyword))
        if last_line:
            keyboard.append(last_line)
        return ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        )

    async def help_command(self, message, **kwargs):
        output_str = self.general_message + "\n" + self.help_message
        await self.answer_safe(message, output_str)

    async def cancel_handler(self, message: Message, state: FSMContext, **kwargs) -> None:
        """
        Allow user to cancel any action
        """
        current_state = await state.get_state()
        if current_state is None:
            return

        logging.info("Cancelling state %r", current_state)
        await state.clear()
        await message.answer(
            "Cancelled.",
            reply_markup=ReplyKeyboardRemove(),
        )

    async def gts_start_handler(self, message: Message, state: FSMContext, **kwargs) -> None:
        await state.set_state(GTS.start)
        await message.answer(
            "Выбирай сценарий",  # todo
            reply_markup=self.get_keyboard(
                states=[
                    GTS.select_specific_person,
                    GTS.pick_for_me,
                    GTS.view_notion,
                ]
            ),
        )

    default_allowed_users = [
        "larionovdanil",
        "Xallt",
        "palych65",
        "kudrinsky",
        "andrewtropin",
        "mikhail_mironov",
        "vitekmel",
        "gdialex",
        "Mikhail_Vodolagin",
        "petr_lavrov",
        "marklidenberg",
        "bogdan_litvak",
        "maksutov_aynur",
        "ghavr",
        "abreyman",
        "tatiana_medvedev",
        "Lipton_III",
        "beaubeurre",
        "fedyarer",
        "d20familiar",
        "nerewareen",
        "snimshchikov",
        "vankudr",
        "eovcharov",
        "mkuzin94",
        "etemenanki",
        "e2ae8frlng",
        "mishaovo",
        "aikoven",
        "vvvkamper",
        "Ltgags",
    ]

    @property
    def allowed_users(self):
        if self._allowed_users is None:
            # self._allowed_users = [x.lower() for x in json.loads(os.getenv("TELEGRAM_BOT_ALOWED_USERS"))]
            self._allowed_users = self.default_allowed_users
            self._allowed_users = [x.lower() for x in self.config.allowed_users]

        return self._allowed_users

    # region Authorization
    # todo: move authorisation to base handler?
    def filter_unauthorised(self, message):
        if not self.allowed_users:
            return False
        username = message.from_user.username.lstrip("@")
        return username not in self.allowed_users

    UNAUTHORISED_RESPONSE = dedent(
        """
        This is a private community bot.
        You are not authorized to use this bot.
        Contact @petr_lavrov to get access.
        """
    )

    async def unauthorized(self, message: Message):
        self.logger.info(f"Unauthorized user {message.from_user.username}")
        # todo 1: once a day respond to a particular user - in
        # if direct @ mention or /command that in self.has_command - always respond.
        if (
            message.chat.type == "private"
            or await self.check_message_mentions_bot(message)
            or await self.check_message_uses_bot_command(message)
        ):
            await self.answer_safe(message, self.UNAUTHORISED_RESPONSE, reply_markup=ReplyKeyboardRemove())
        else:
            pass

    # endregion Authorization

    def _create_router(self, **kwargs):
        """Register extra handlers BEFORE command handlers"""
        router = super()._create_router(**kwargs)

        router.message.register(self.unauthorized, self.filter_unauthorised)
        # cancel
        router.message.register(self.cancel_handler, F.text.casefold() == self.stop_scenario_keyword.lower())

        self.register_state_switch(router, AppState.start, GTS.start, self.gts_start_handler)
        self._register_group_2_handlers(router)
        self._register_group_3_handlers(router)
        self._register_side_scenario_handlers(router)
        # links to Notion
        self.register_state_switch(router, GTS.start, GTS.view_notion, self.gts_view_notion_handler)

        return router

    def setup_router(self, router: Router):
        super().setup_router(router)

    # region Group 2 - select specific person
    ef_members_names = {
        "petr_lavrov": ["Петр Лавров", "Петя Лавров", "Petr Lavrov"],
        "marklidenberg": ["Марк Лиденберг", "Mark Lidenberg"],
        "larionovdanil": ["Данил Ларионов", "Danil Larionov"],
        "Xallt": ["Mitya Shabat", "Dmitry Shabat", "Митя Шабат", "Дмитрий Шабат"],
        "palych65": ["Nikita Vasilyev", "Никита Васильев"],
        "kudrinsky": [
            "Alexei Kudrinsky",
            "Alex Kudrinsky",
            "Леша Кудринский",
            "Алексей Кудринский",
        ],
        "andrewtropin": ["Andrew Tropin", "Андрей Тропин"],
        "mikhail_mironov": ["Mikhail Mironov", "Михаил Миронов", "Миша Миронов"],
        "vitekmel": ["Viktor Omelyanenko", "Виктор Омельяненко", "Витя Омельяненко"],
        "gdialex": ["Alexander Votyakov", "Александр Вотяков", "Саша Вотяков"],
        "Mikhail_Vodolagin": [
            "Mikhail Vodolagin",
            "Михаил Водолагин",
            "Миша Водолагин",
        ],
        "bogdan_litvak": ["Bogdan Litvak", "Богдан Литвак"],
        "maksutov_aynur": ["Aynur Maksutov", "Айнур Максутов", "Айнур Максютов"],
        "ghavr": ["Andrey Gavriliuk", "Андрей Гаврилюк"],
        "abreyman": ["Alexander Breyman", "Александр Брейман", "Саша Брейман"],
        "tatiana_medvedev": [
            "Tatiana Medvedeva",
            "Татьяна Медведева",
            "Таня Медведева",
        ],
        "Lipton_III": ["Georgy Gorbachev", "Георгий Горбачев", "Гоша Горбачев"],
        "beaubeurre": ["Ilya Tyurin", "Илья Тюрин", "Илюха Тюрин"],
        "fedyarer": ["Fedor Ivlev", "Федор Ивлев", "Федя Ивлев"],
        "d20familiar": ["Vitaliy Agafonov", "Виталий Агафонов", "Виталик Агафонов"],
        "nerewareen": ["Arseniy Gorbachev", "Арсений Горбачев", "Сеня Горбачев"],
        "snimshchikov": ["Ilya Snimshchikov", "Илья Снимщиков"],
        "vankudr": ["Ivan Kudriavtsev", "Иван Кудрявцев", "Ваня Кудрявцев"],
        "eovcharov": ["Eugene Ovcharov", "Евгений Овчаров", "Женя Овчаров"],
        "mkuzin94": ["Mikhail Kuzin", "Михаил Кузин", "Миша Кузин"],
        "etemenanki": ["Ksenia Solovyeva", "Ксения Соловьева", "Кася Соловьева"],
        "e2ae8frlng": ["Konstantin Ershov", "Константин Ершов", "Костя Ершов"],
        "mishaovo": ["Misha Ovoshchnikov", "Миша Овощников", "Mikhail Ovoshchnikov"],
        "aikoven": ["Daniel Lytkin", "Даниэль Лыткин", "Даня Лыткин"],
        "vvvkamper": ["Roman Kurmazov", "Роман Курмазов", "Рома Курмазов"],
    }

    ef_members_dict = {vv: k for k, v in ef_members_names.items() for vv in v}

    async def find_user_handler(self, message: Message, state: FSMContext, **kwargs):
        user_query = await self.get_message_text(message)
        choices = get_possible_people_by_name(user_query)
        if len(choices) == 1:
            selection = choices[0]
            text = f"""Selected user: {selection}"""
            await self.answer_safe(message, text)
            await self.update_data_single(state, "selected_person_for_topic_gen", selection)
            # await self.person_selected_handler(message, state, selected_person_for_topic_gen=selection)
            await self.selecting_prompt(message, state)
        elif len(choices) == 0:
            await self.answer_safe(message, "No matches found")
        else:
            # if ambigous - ask list all and allow picking with a number
            text = "Multiple matches found. Please select from the list"
            # select from list
            await self._select_from_list(
                state=state,
                message=message,
                candidates=choices,
                reply_text=text,
                follow_up_handler=self.selecting_prompt,
            )

    # endregion Group 2 - select specific person
    # region Group 3 - select random person
    def _register_group_3_handlers(self, router):
        self.register_state_switch(
            router,
            GenerateTopicState.start,
            GenerateTopicState.pick_for_me,
            self.gts_pick_for_me_handler,
        )
        self.register_state_switch(
            router,
            GenerateTopicState.pick_for_me,
            GenerateTopicState.select_random_person,
            self.gts_select_random_person_handler,
        )
        self.register_state_switch(
            router,
            GenerateTopicState.pick_for_me,
            GenerateTopicState.suggest_by_common_interests,
            self.gts_suggest_by_common_interests_handler,
        )

    async def gts_pick_for_me_handler(self, message: Message, state: FSMContext, app: MyApp) -> None:
        reply_text = """Как будем выбирать?"""
        await state.set_state(GTS.pick_for_me)
        await self.answer_safe(
            message,
            reply_text,
            reply_markup=self.get_keyboard(
                states=[
                    GTS.select_random_person,
                    GTS.suggest_by_common_interests,
                ]
            ),
        )

    async def gts_select_random_person_handler(self, message: Message, state: FSMContext, app: MyApp) -> None:
        # step 1: tell who we picked
        person2 = random.choice(self.ef_members)
        reply_text = f"""Выбран случайный человек: {person2}"""
        await self.answer_safe(message, reply_text, reply_markup=ReplyKeyboardRemove())

        # step 2: generate a topic
        # state.set_data({"person2", person2})
        await self.person_selected_handler(message, state, selected_person_for_topic_gen=person2)

    async def gts_suggest_by_common_interests_handler(self, message: Message, state: FSMContext, app: MyApp) -> None:
        reply_text = dedent(
            """
            А это еще не сделано
            Любишь кататься - люби и саночки возить!
            Кодить сюда: https://github.com/engineering-friends/generate-session-idea-dev/blob/830e6a9723fdba669556dfa21d7a00febe34d52c/ef_matchmaking_bot/handler.py#L171-L176
            """
        )
        await self.answer_safe(message, reply_text, reply_markup=ReplyKeyboardRemove())

    # endregion Group 3 - select random person
    # region Group 4 - go to Notion
    async def gts_view_notion_handler(self, message: Message, state: FSMContext, app: MyApp) -> None:
        await state.set_state(GenerateTopicState.view_notion)
        # todo: make individual links - hardcode
        response_text = dedent(
            """
            Option 1:
            - Fill [your page](https://www.notion.so/engineering-friends/Tatyana-Medvedeva-9629f4c6e12847c9af810ffa0da58f79?pvs=4) to get topic suggestions
            Option 2:
            - See [everyone else's pages](https://www.notion.so/engineering-friends/641eaea7c7ad4881bbed5ea096a4421a?v=ca225d7c2b7b4762987407f53e2ae458&pvs=4) to pick a person to chat with:
            """
        )
        await self.answer_safe(
            message, response_text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN
        )

    # endregion Group 4 - go to Notion
    back_keyword = "Назад"

    def register_state_switch(
        self,
        router,
        state1,
        state2,
        handler,
        register_back_handler=True,
        back_handler=None,
    ):
        router.message.register(
            handler,
            state1,
            F.text.casefold() == self.get_state_name(state2).lower(),
        )

        # add 'back' hanlder:
        if register_back_handler:
            # todo: make this proper - track state switches and truly go back, not this way
            if back_handler is None:

                async def back_handler(message: Message, state: FSMContext, app: MyApp):
                    # await state.set_state(state1)
                    handler = self.state_handlers[state1]
                    await self.answer_safe(message, f"New State: {self.get_state_name(state1)}")
                    await handler(message=message, state=state, app=app)

            router.message.register(back_handler, F.text.casefold() == self.back_keyword.lower())

    # def register_extra_handlers(self, router):
    #     """
    #     Register extra handlers AFTER command handlers
    #     :param router:
    #     :return:
    #     """
    #
    #     pass

    def _register_group_2_handlers(self, router):
        # route 1
        # transition 1
        self.register_state_switch(
            router,
            GenerateTopicState.select_specific_person,
            GenerateTopicState.list_all_people,
            self.gts_list_all_people_handler,
        )
        # transition 2
        router.message.register(self.pick_from_list_handler, GTS.list_all_people)

        self.register_state_switch(
            router,
            GenerateTopicState.start,
            GenerateTopicState.select_specific_person,
            self.gts_select_specific_person_handler,
        )
        router.message.register(self.find_user_handler, GTS.select_specific_person)
        router.message.register(self.pick_from_list_handler, GTS.pick_from_list)

        # side scenarios
        self.register_state_switch(
            router,
            GenerateTopicState.select_specific_person,
            GenerateTopicState.select_random_person,
            self.gts_select_random_person_handler,
        )
        self.register_state_switch(
            router,
            GenerateTopicState.select_specific_person,
            GenerateTopicState.view_notion,
            self.gts_view_notion_handler,
        )

        router.message.register(
            self.selecting_prompt_handler,
            GTS.selecting_prompt,
        )

    async def gts_list_all_people_handler(self, message: Message, state: FSMContext, **kwargs) -> None:
        candidates = self.ef_members
        reply_text = """Список всех людей. Введи цифру, чтобы выбрать"""

        await self._select_from_list(
            state=state,
            message=message,
            candidates=candidates,
            reply_text=reply_text,
            follow_up_handler=self.selecting_prompt,
        )
        # await state.set_state(GenerateTopicState.list_all_people)

    async def _select_from_list(
        self,
        state,
        message,
        candidates,
        reply_text="Select from list, enter a number",
        follow_up_handler=None,
    ):
        await state.set_state(GenerateTopicState.pick_from_list)
        if follow_up_handler is None:
            follow_up_handler = self.selecting_prompt
        for i, person in enumerate(candidates):
            reply_text += f"\n{i+1}. {person}"
        await self.answer_safe(message, reply_text)
        await self.update_data(state, {"picker_candidates": candidates, "picker_follow_up_handler": follow_up_handler})

    async def person_selected_handler(
        self, message: Message, state: FSMContext, person1=None, selected_person_for_topic_gen=None, prompt_name=None
    ) -> None:
        data = await state.get_data()
        if person1 is None:
            person1 = get_person_by_tg_handle(self.get_user(message))
        if selected_person_for_topic_gen is None:
            # get from state
            selected_person_for_topic_gen = data["selected_person_for_topic_gen"]
        if prompt_name is None:
            prompt_name = data.get("prompt_name", "petr_prompt")
        # person2 = await state.get_data()["person2"]
        reply_text = f"""Generating a topic for {person1} and {selected_person_for_topic_gen}"""
        loading_message: Message = await self.answer_safe(
            message, reply_text, reply_markup=(ReplyKeyboardRemove() if not self.config.debug_mode else None)
        )
        # todo - support prompt names selection
        topics_suggestions = self.generate_suggestions(person1, selected_person_for_topic_gen, prompt_name=prompt_name)
        # await asyncio.sleep(5)
        reply_text = f"""Topic suggestions for {person1} and {selected_person_for_topic_gen}:\n"""
        if isinstance(topics_suggestions, list):
            for i, topic in enumerate(topics_suggestions):
                reply_text += f"{i+1}. {topic}\n"
        else:
            reply_text += topics_suggestions
        await self.answer_safe(
            message,
            reply_text,
            # todo: should we keep keyboard and state here to re-run?
            reply_markup=(ReplyKeyboardRemove() if not self.config.debug_mode else None),
        )
        await loading_message.delete()
        await state.clear()

    async def pick_from_list_handler(self, message: Message, state: FSMContext, **kwargs):
        data = await state.get_data()
        candidates = data["picker_candidates"]
        if isinstance(candidates, list):
            candidates = {str(i + 1): v for i, v in enumerate(candidates)}
        user_query = await self.get_message_text(message)
        if user_query in candidates:
            selection = candidates[user_query]
            await self.update_data_single(state, "selected_person_for_topic_gen", selection)
            follow_up_handler = data["picker_follow_up_handler"]
            try:
                await follow_up_handler(message, state)
            except Exception as e:
                logger.error("Follow-up handler failed for pick_from_list_handler", exc_info=e)
                await self.answer_safe(message, f"Error: {e}")

            # await state.set_state(data["next_state_after_person_selected"])
        else:
            await self.answer_safe(
                message,
                "Didn't find your choice in candidates.\n"
                f"Choice: {user_query} Candidates: {list(candidates.keys())}",
            )

    async def gts_select_specific_person_handler(self, message: Message, state: FSMContext, **kwargs) -> None:
        # step 1: select a person (provide their name)
        reply_text = """Напиши с кем хочешь созвониться (имя) или жми кнопку"""
        await state.set_state(GenerateTopicState.select_specific_person)
        await state.set_data(
            {
                "picker_candidates": {k: k for k in self.ef_members},
                "picker_follow_up_handler": self.person_selected_handler,
            }
        )

        await self.answer_safe(
            message,
            reply_text,
            reply_markup=self.get_keyboard(
                states=[
                    GTS.list_all_people,
                    GTS.pick_for_me,
                    GTS.select_random_person,
                    GTS.view_notion,
                ]
            ),
        )

    # region Side Scenarios

    def _register_side_scenario_handlers(self, r):
        self.register_state_switch(
            r,
            AppState.start,
            SSS.start,
            self.side_scenario_start_handler,
        )

        self.register_state_switch(
            r,
            SSS.start,
            SSS.meet_someone_new,
            self.side_scenario_1_meet_someone_new_handler,
        )

        self.register_state_switch(
            r,
            SSS.start,
            SSS.write_post,
            self.side_scenario_2_write_post_handler,
        )

        self.register_state_switch(
            r,
            SSS.start,
            SSS.want_to_chat,
            self.chat_handler,
        )

        self.register_state_switch(
            r,
            SSS.start,
            SSS.make_a_request,
            self.side_scenario_4_post_a_request_handler,
        )

        self._register_universal_state_handler(
            r,
            SSS.read_about_others,
            self.side_scenario_5_read_about_others_handler,
            ["Посмотреть профили людей в Notion"],
        )

        self.register_state_switch(
            r,
            SSS.start,
            SSS.my_notion_page,
            self.side_scenario_6_my_notion_page_handler,
        )

        self.register_state_switch(
            r,
            SSS.start,
            SSS.custom_post_image_style,
            self.side_scenario_7_custom_post_style_handler,
        )

        self._register_universal_state_handler(
            r,
            SSS.tell_about_ef,
            self.side_scenario_8_random_ef_facts_handler,
        )

    async def side_scenario_start_handler(self, message: Message, state: FSMContext, app: MyApp) -> None:
        # show available start scenarios as buttons
        reply_text = "Выбери сценарий"
        await state.set_state(SideScenarioState.start)
        await self.answer_safe(
            message,
            reply_text,
            reply_markup=self.get_keyboard(
                states=[
                    # "Чатбот в дискорде (и телегу) про “придумай” идею на сессию",
                    # "Чатбот про “найди мне про поговорить”",
                    # "Чатбот про веселье",
                    SSS.meet_someone_new,
                    SSS.write_post,
                    SSS.want_to_chat,
                    SSS.make_a_request,
                    SSS.read_about_others,
                    SSS.my_notion_page,
                    SSS.custom_post_image_style,
                    SSS.tell_about_ef,
                ]
            ),
        )

    # todo: config via env
    org_chat_id = -1002144718775

    # todo: allow retries using _register_universal_state_handler
    async def side_scenario_1_meet_someone_new_handler(self, message: Message, state: FSMContext, app: MyApp) -> None:
        # Send a message to an org chat "user wants to meet someone new"
        username = self.get_user(message)

        reply_text = """Варианты:"""
        # idea 1: написать матвею
        reply_text += """\n1. Написать Матвею @Ltgags "Я хочу познакомиться с кем-то из EF!" """

        buttons = []
        # idea 2: generate a random person
        # todo: bind existing handler for this
        buttons.append("Случайный человек")

        # todo: idea 3: pick someone based on interests and past history
        # todo: bonus: "I already know them" button

        # idea 4: list all people, link to Notion
        # todo: create handler for this - and bind it, list - all people and their telegram handles
        buttons.append("Выбрать из списка")
        # todo: bind existing handler for this
        buttons.append("Посмотреть профили людей в Notion")
        # buttons.append("Почитать про других людей")

        # send buttons
        await state.set_state(SideScenarioState.meet_someone_new)
        await self.reply_safe(message, reply_text, reply_markup=self.get_keyboard(buttons))
        await self.send_safe(self.org_chat_id, f"EF Bot Notification: User {username} wants to meet someone new!")

    async def side_scenario_2_write_post_handler(self, message: Message, state: FSMContext):
        username = self.get_user(message)
        reply_text = (
            f"Пока мы пишем посты через дискорд."
            f" Любой участник может написать пост в дискорд и он автоматически форвардится в телееграм канал EF Channel."
            f" Вот ссылка на сервер: {settings.discord_posts_channel_link}"
        )
        # todo: add support for writing posts through telegram bot
        await state.set_state(SideScenarioState.write_post)
        await self.reply_safe(message, reply_text)
        await self.send_safe(settings.org_chat_id, f"EF Bot Notification: User {username} wants to write a post!")

    # todo
    # todo: allow retries using _register_universal_state_handler
    async def side_scenario_3_want_to_chat_handler(self, message: Message, state: FSMContext):
        username = self.get_user(message)
        reply_text = "Хотите пообщаться? Отлично! Выберите один из вариантов:"
        buttons = ["Случайный собеседник", "Собеседник по интересам", "Кто-то, с кем давно не общались"]
        # todo: implement all the handlers and bind them
        await state.set_state(SideScenarioState.want_to_chat)
        await self.reply_safe(message, reply_text, reply_markup=self.get_keyboard(buttons))
        await self.send_safe(settings.org_chat_id, f"EF Bot Notification: User {username} wants to chat with someone!")

    async def side_scenario_4_post_a_request_handler(self, message: Message, state: FSMContext):
        username = self.get_user(message)
        # to make a request go to this discord url and post a request

        reply_text = (
            "Сейчас запросы делаем через дискорд - просто пишешь пост с запросом в тему 'запросы' и он форвардится в телеграм канал EF Channel. "
            f"Вот ссылка на сервер: {settings.discord_requests_channel_link}"
        )
        # todo: allow users to make requests through telegram bot
        await state.set_state(SideScenarioState.make_a_request)
        await self.reply_safe(message, reply_text)
        await self.send_safe(settings.org_chat_id, f"EF Bot Notification: User {username} has a request!")

    async def side_scenario_5_read_about_others_handler(self, message: Message, state: FSMContext):
        username = self.get_user(message)
        reply_text = f"Почитать о других участниках EF на страничке с Whois: {settings.notion_whois_link}"
        await state.set_state(SideScenarioState.read_about_others)
        await self.reply_safe(message, reply_text)
        await self.send_safe(settings.org_chat_id, f"EF Bot Notification: User {username} wants to read about others!")

    async def side_scenario_6_my_notion_page_handler(self, message: Message, state: FSMContext):
        username = self.get_user(message)
        # get notion page by user
        reply_text = (
            f"Заполнить свой профиль можно здесь.  {settings.notion_whois_link}"
            f"Саму страничку найди уж пожалуйста как-нибудь сам :) - ссылки пока не захардкодили"
        )
        await state.set_state(SideScenarioState.my_notion_page)
        await self.reply_safe(message, reply_text)
        # await self.send_safe(
        #     settings.org_chat_id, f"EF Bot Notification: User {username} wants to access their Notion page!"
        # )

    # todo
    async def side_scenario_7_custom_post_style_handler(self, message: Message, state: FSMContext):
        username = self.get_user(message)
        reply_text = "Наш бот-форвардер автоматически генерит обложки к "
        await state.set_state(SideScenarioState.custom_post_image_style)
        await self.reply_safe(message, reply_text)
        await self.send_safe(
            settings.org_chat_id, f"EF Bot Notification: User {username} wants to create a custom post style!"
        )

    # todo: allow retries using _register_universal_state_handler
    async def side_scenario_8_random_ef_facts_handler(self, message: Message, state: FSMContext, **kwargs):
        """
        Handles the scenario where the user requests to hear a random fact about EF.
        This includes details about old sessions, open requests, features, projects,
        and more. Randomly selects one fact and sends it to the user.

        Args:
            message (Message): The message object from the user.
            state (FSMContext): The current state of the user in the FSM.
        """
        username = self.get_user(message)
        # EF Menu
        ef_facts = []

        # idea 1: random old session
        # idea 2: random open request
        # idea 3: random feature
        features = [
            # 1) Forwarder bot - reposts from discord to telegram
            """EF Forwarder - бот, который пересылает сообщения из дискорда в телеграм""",
            # 2) Image geneartion - generates images for posts (if no image is provided)
            # bonus: you can customize the image style for your posts - in your Notion whois page
            f"""EF Image Generator - генератор картинок для постов (если картинка не предоставлена)
            Бонус: можно настроить стиль картинки для своих постов - на своей страничке в Notion
            {settings.notion_whois_link}""",
        ]
        # idea 4: random old post
        # idea 5: random "EF Project" or experiment
        actual_projects = [
            # Random Coffee
            """EF Random Coffee - еже-недельные встречи желающих по случаным парам
            - Ссылка на группу: https://t.me/+8qR31oi6zU0wNzhi
            Фишка: Делаем сезонами, чтобы не надоедало :) 
            """
            # Polls
            """EF Polls - опросы всем нравятся, делаем опросы :) 
            Предлагайте свои, пожалуйста - пишите @petr_lavrov. 
            Три типа опросов: - развлекательные, информационные, активные""",
            # ...
            """EF Challenges - спрашивайте у Марка и предлагайте свои!""",
            """EF Strava. 
            Strava - приложение для занятий спортом.
            Есть группа EF Strava, туда можно добавиться и следить за активностью других участников.
            А еще там есть leaderboard - соревноваться :) - Правда, только бег
            https://strava.app.link/rsHrEZbYyKb
            """,
        ]
        old_projects = [
            # Subscriptions review
            # EF Gaming - piko park, dnd, among us
        ]
        candidates = ef_facts + features + actual_projects + old_projects
        # todo: track 'read' facts
        reply_text = "Случайный факт про EF:\n"
        reply_text += random.choice(candidates)

        await state.set_state(SideScenarioState.tell_about_ef)
        await self.reply_safe(message, reply_text)
        await self.send_safe(settings.org_chat_id, f"EF Bot Notification: User {username} asked about EF!")

    def _register_universal_state_handler(self, router, state: Union[State, str], handler, extra_keywords=None):
        """
        Handler that is activated by receiving a message with a state name
        """
        if not isinstance(state, str):
            state = self.get_state_name(state)
        if isinstance(extra_keywords, str):
            extra_keywords = [extra_keywords]
        router.message.register(handler, F.text.casefold() == state.lower())
        for keyword in extra_keywords or []:
            router.message.register(handler, F.text.casefold() == keyword.lower())

    # endregion Side Scenarios

    prompts_dict = {
        "*petr_prompt_hard_to_guess_5_topics": PetrPromptHardToGuess5Topics,
        "mikhail_variant": MikhailVariantPrompt,
        "vitaly_prompt": VitalyVariantPrompt,
        # todo: add the rest
        "petr_prompt": PetrPrompt,
        "petr_prompt_no_reasoning_5_topics": PetrPromptNoReasoning5Topics,
        "petr_prompt_one_word_10_topics": PetrPromptOneWord10Topics,
        "petr_prompt_triplet_5_topics": PetrPromptTriplet5Topics,
        "petr_prompt_one_word_no_extras_10_topics": PetrPromptOneWordNoExtras10Topics,
        "petr_prompt_triplet_no_extras_10_topics": PetrPromptTripletNoExtras10Topics,
        "petr_prompt_expensive": PetrPromptExpensive,
        stop_scenario_keyword: None,
    }

    def generate_suggestions(self, person1, person2, prompt_name="mikhail_variant"):
        person1 = get_possible_people_by_name(person1)[0]
        person_1_interests = get_interest_for_person(person1)
        if not person_1_interests:
            return f"{person1} has not filled interests in their Notion page {settings.notion_whois_link}"
        person2 = get_possible_people_by_name(person2)[0]
        person_2_interests = get_interest_for_person(person2)
        if not person_2_interests:
            return f"{person2} has not filled interests in their Notion page {settings.notion_whois_link}"

        input_data = {
            "person_0_interests": person_1_interests,
            "person_1_interests": person_2_interests,
        }

        run_config = {
            "name": prompt_name,
            # "tags": ["exp-234"],
            # "metadata": {
            #     "approach": "bruteforce",
            #     "data_q": "poor",
            # },
        }

        prompt = self.prompts_dict[prompt_name]
        res = prompt.entry_point(**input_data, **run_config)

        logger.success(res)
        return res

    # allow user to select the prompt
    # handle when the prompt is selected
    async def selecting_prompt(self, message: Message, state: FSMContext, **kwargs):
        # ask user to select the prompt
        await state.set_state(GenerateTopicState.selecting_prompt)
        await self.answer_safe(
            message,
            "Выбери промпт",
            reply_markup=self.get_keyboard(states=list(self.prompts_dict.keys())),
        )

    async def selecting_prompt_handler(self, message: Message, state: FSMContext, **kwargs):
        prompt_name = await self.get_message_text(message)
        if prompt_name not in self.prompts_dict:
            await self.answer_safe(message, f"Unknown prompt {prompt_name}")
            return
        await self.update_data_single(state, "prompt_name", prompt_name)
        await self.person_selected_handler(message, state)

    @classmethod
    async def update_data_single(cls, state, key, val):
        await cls.update_data(state, {key: val})

    @staticmethod
    async def update_data(state, d):
        data = await state.get_data()
        data.update(d)
        await state.set_data(data)
