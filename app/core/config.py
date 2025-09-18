from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "a_very_secret_key_that_should_be_in_a_env_file"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    OPENWEATHER_API_KEY: str = "your_actual_api_key_here"
    
    class Config:
        env_file = ".env"

settings = Settings()