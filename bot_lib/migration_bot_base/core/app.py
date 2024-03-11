from pathlib import Path

import asyncio
from typing import Type

import loguru
import mongoengine
import openai
from dotenv import load_dotenv

# from apscheduler.triggers.interval import IntervalTrigger
from bot_lib.migration_bot_base.core import DatabaseConfig, TelegramBotConfig
from bot_lib.migration_bot_base.core.app_config import AppConfig
from bot_lib.migration_bot_base.core.telegram_bot import TelegramBot
from bot_lib.migration_bot_base.utils.audio_utils import (
    DEFAULT_PERIOD,
    DEFAULT_BUFFER,
    split_and_transcribe_audio,
)
from bot_lib.migration_bot_base.utils.gpt_utils import Audio


class AppBase:
    _app_config_class: Type[AppConfig] = AppConfig
    _telegram_bot_class: Type[TelegramBot] = TelegramBot
    _database_config_class: Type[DatabaseConfig] = DatabaseConfig
    _telegram_bot_config_class: Type[TelegramBotConfig] = TelegramBotConfig

    def __init__(self, data_dir=None, config: _app_config_class = None):
        self.logger = loguru.logger.bind(component=self.__class__.__name__)
        if config is None:
            config = self._load_config()
        if data_dir is not None:
            config.data_dir = Path(data_dir)
        # make dir
        config.data_dir.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.db = self._connect_db()
        self.bot = self._telegram_bot_class(config.telegram_bot, app=self)
        self.logger.info(f"Loaded config: {self.config}")

    @property
    def data_dir(self):
        return self.config.data_dir

    # todo_optional: setter, moving the data to the new dir

    def _load_config(self, **kwargs):
        load_dotenv()
        database_config = self._database_config_class(**kwargs)
        telegram_bot_config = self._telegram_bot_config_class(**kwargs)
        return self._app_config_class(
            database=database_config, telegram_bot=telegram_bot_config, **kwargs
        )

    def _connect_db(self):
        try:
            return mongoengine.get_connection("default")
        except mongoengine.connection.ConnectionFailure:
            db_config = self.config.database
            conn_str = db_config.conn_str.get_secret_value()
            return mongoengine.connect(
                db=db_config.name,
                host=conn_str,
            )

    def run(self):
        self.logger.info(f"Starting {self.__class__.__name__}")
        asyncio.run(self.bot.run())


class App(AppBase):
    def __init__(self, data_dir=None, config: AppConfig = None):
        super().__init__(data_dir=data_dir, config=config)
        if self.config.enable_openai_api:
            # deprecate this
            self.logger.warning("OpenAI API is deprecated, use GPT Engine instead")
            self._init_openai()

        if self.config.enable_voice_recognition:
            self.logger.info("Initializing voice recognition")
            self._init_voice_recognition()

        self._scheduler = None
        if self.config.enable_scheduler:
            self.logger.info("Initializing scheduler")
            from apscheduler.schedulers.asyncio import AsyncIOScheduler

            # self._init_scheduler()
            self._scheduler = AsyncIOScheduler()

        self.gpt_engine = None
        if self.config.enable_gpt_engine:
            self.logger.info("Initializing GPT Engine")
            from gpt_kit.gpt_engine.gpt_engine import GptEngine

            self.gpt_engine = GptEngine(config.gpt_engine, app=self)
            # self._init_gpt_engine()

    def _init_openai(self):
        openai.api_key = self.config.openai_api_key.get_secret_value()

    # def _init_scheduler(self):
    #     self._scheduler = AsyncIOScheduler()

    # ------------------ GPT Engine ------------------ #

    # ------------------ Audio ------------------ #

    def _init_voice_recognition(self):
        # todo: check that codecs are installed
        #  install if necessary
        # todo: check that ffmpeg is installed
        # todo: check pyrogram token and api_id
        pass

    async def parse_audio(
        self,
        audio: Audio,
        period: int = DEFAULT_PERIOD,
        buffer: int = DEFAULT_BUFFER,
        parallel: bool = None,
    ):
        if parallel is None:
            parallel = self.config.process_audio_in_parallel
        chunks = await split_and_transcribe_audio(
            audio,
            period=period,
            buffer=buffer,
            parallel=parallel,
            logger=self.logger,
        )
        return chunks

    # --------------------------------------------- #

    async def _run_with_scheduler(self):
        # this seems stupid, but this is a tested working way, so i go with it
        # rework sometime later - probably can just start and not gather
        self._scheduler.start()
        await self.bot.run()

    def run(self):
        if self.config.enable_scheduler:
            self.logger.info("Running with scheduler")
            asyncio.run(self._run_with_scheduler())
        else:
            super().run()
