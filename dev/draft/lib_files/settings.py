from pydantic_settings import BaseSettings

class ErrorHandling(BaseSettings):
    enabled: bool = True

class Settings(BaseSettings):
    error_handling: ErrorHandling = ErrorHandling()