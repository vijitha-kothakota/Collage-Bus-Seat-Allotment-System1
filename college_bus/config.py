import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'college-bus-secret-key-2026-secure')
    DB_PATH = os.path.join(BASE_DIR, 'database', 'bus.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Static uploads and QR codes
    QR_FOLDER = os.path.join(BASE_DIR, 'static', 'qr_codes')
    
    # Session cookie settings
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
