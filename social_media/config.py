''' Python-dotenv library to hide environment variables '''
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

JWT_SECRET = os.environ.get("JWT_SECRET")

JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM")
