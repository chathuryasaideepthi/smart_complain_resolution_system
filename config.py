import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+mysqlconnector://root:password@localhost/smart_complaint_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'smart_complaint_system', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe')
