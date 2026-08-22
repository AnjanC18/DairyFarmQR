import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dairy-smart-farm-secret-key-2026-mca')
    
    # MySQL connection string (default).
    # Format: mysql+pymysql://<user>:<password>@<host>/<database>
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('DB_PORT', '3306')
    MYSQL_DB = os.environ.get('DB_NAME', 'dairy_farm')
    
    MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLITE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'dairy.db')}"
    
    # Use environment DATABASE_URL or default to SQLite fallback if MySQL is not explicitly set
    # We default to SQLite for zero-setup local dev/testing, but easily switchable via USE_MYSQL=true or DATABASE_URL
    USE_MYSQL = os.environ.get('USE_MYSQL', 'false').lower() in ('true', '1', 't')
    
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or 
        (MYSQL_URI if USE_MYSQL else SQLITE_URI)
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'images')
    QR_FOLDER = os.path.join(STATIC_DIR, 'qr_codes')
    
    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(QR_FOLDER, exist_ok=True)
