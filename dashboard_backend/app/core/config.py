from pydantic import BaseSettings, validator


# Load environment variables into a pydantic BaseSetting object
class AppConfig(BaseSettings):
    
    KSQL_HOST : str
    KSQL_PORT : str
    STREAM_NAME : str
    TOPIC_NAME : str 
    KSQL_URL : str = ""

    class Config:

        case_sensitive = True
        
    @validator("KSQL_URL", pre=True, always=True)
    def set_ksql_url(cls, v, values, **kwargs):
        return values['KSQL_HOST'] + ":" + values['KSQL_PORT'] 

app_config = AppConfig()