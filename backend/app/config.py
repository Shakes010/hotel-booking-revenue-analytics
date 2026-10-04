import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'hotel_analytics_secret_key_mca_2026')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_super_secret_key_hotel_analytics')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    
    # Strict MySQL 8.0/8.4 Database Configuration
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DB = os.getenv('MYSQL_DB', 'hotel_analytics_db')

    # Strict MySQL Database URI (No SQLite fallback allowed)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
