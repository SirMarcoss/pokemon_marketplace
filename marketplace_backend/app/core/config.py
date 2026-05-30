from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    DATABASE_URL : str
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 30
    STRIPE_SECRET_KEY : str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings() #It uses that template to create an actual object in memory,
                      # which reads the .env file and keeps the values ready.