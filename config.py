from pydantic import BaseModel

class Settings(BaseModel):
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8001
    API_DEBUG: bool = True
    API_TITLE: str = "PaintFlow 2 API"
    API_VERSION: str = "2.0.0"
    
    DB_HOST: str = "dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com"
    DB_PORT: int = 5432
    DB_NAME: str = "labels_app_db"
    DB_USER: str = "admin"
    DB_PASSWORD: str = "KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
    
    FRONTEND_URL: str = "http://127.0.0.1:8001"
    CORS_ORIGINS: list = ["http://127.0.0.1:8001"]
    LOG_LEVEL: str = "INFO"

settings = Settings()
