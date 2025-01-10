from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenAI settings
    OPENAI_API_KEY: str

    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_NUMBER: str

    # FHIR API settings
    CLIENT_ID: str
    CLIENT_SECRET: str
    FHIR_AUTH_URL: str = (
        "https://auth.onfhir.cl/realms/conectaton-dev/protocol/openid-connect/token"
    )
    FHIR_API_URL: str = "https://gateway.onfhir.cl/hl7cl/fhir/"

    # Application settings
    CONVERSATION_TIMEOUT: int = 30

    WAIT_TIME_FOR_APPOINTMENT_SECONDS: int = 1

    class Config:
        env_file = ".env"


settings = Settings()
