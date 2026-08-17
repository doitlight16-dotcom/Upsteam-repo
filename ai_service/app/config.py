from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KMG AI Concierge Microservice"
    API_V1_STR: str = "/api/v1"
    CHROMA_DB_PATH: str = "./chroma_db"
    COLLECTION_NAME: str = "adipec_knowledge"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()