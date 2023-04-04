from pydantic import BaseSettings

# Load environment variables into a pydantic BaseSetting object
class AppConfig(BaseSettings):

    # QuestDB config
    DB_USER : str = None
    DB_PASSWORD : str = None
    DB_HOST : str = None
    DB_PORT : str = None
    DB_NAME : str = None
    DB_TRIAXIAL_OFFLOAD_TABLE_NAME : str = None

    # Application config
    UI_PORT : int = 5000

    # Misc config
    PHONE_SAMPLE_RATE : int = None

    class Config:

        case_sensitive = True

app_config = AppConfig()