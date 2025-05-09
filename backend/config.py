import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///personal_assistant.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev') 