from pydantic_settings import BaseSettings

# option 1: pymongo


class MongoDatabaseSettings(BaseSettings):
    enabled: bool = False
    uri: str = "mongodb://localhost:27017"
    database: str = "test"

    class Config:
        env_prefix = "NBL_MONGO_DATABASE_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def setup_dispatcher(dp):
    # return dp
    pass


def initialise(settings: MongoDatabaseSettings):

    client = None

    return client
