from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'subguard.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_AS_ASCII = False
