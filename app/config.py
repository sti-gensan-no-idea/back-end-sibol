from pydantic_settings import BaseSettings


class Settings(BaseSettings):

	# APP INFO
	APP_NAME: str
	APP_VERSION: str
	APP_DESCRIPTION: str

	# SUPABASE
	SUPABASE_URL: str
	SUPABASE_KEY: str
	SUPABASE_DB_URL: str
	
	# JWT
	SECRET_KEY: str
	ALGORITHM: str
	ACCESS_TOKEN_EXPIRY: int

	# SMTP
	SMTP_SERVER: str
	SMTP_PORT: int
	SMTP_USERNAME: str
	SMTP_PASSWORD: str

	class Config:
		env_file = ".env"

settings = Settings()