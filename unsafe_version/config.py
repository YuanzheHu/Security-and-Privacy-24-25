import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'unsafe-secret-key'  # ❌ Unsafe, needs to be fixed later
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False