"""
Create a .env file in the root directory of the project and add the following line:
OPENAI_KEY=your_openai_key
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OPENAI_KEY = os.getenv('OPENAI_KEY')
LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD')
MP3_DATA_DIR_PATH = os.path.join(BASE_DIR, "data", "audio_data")
DATABASE_FILE_PATH = os.path.join(BASE_DIR, "data", "database.db")
RSS_FILE_PATH = os.path.join(BASE_DIR, "data", "rss.xml")

S3_BUCKET_URL = "https://article2audio.s3.amazonaws.com"
S3_BUCKET_NAME = "article2audio"
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)

DEVELOPMENT = False

