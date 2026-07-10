import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///mediai.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 86400
       # ADD THESE
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = False
    
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 1025))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False").lower() == "true"
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@mediai.local")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "app/static/uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
