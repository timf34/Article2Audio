"""
Create a .env file in the root directory of the project and add the following line:
OPENAI_KEY=your_openai_key
"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')
LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')
MP3_DATA_DIR_PATH = "data/audio_data"
DATABASE_FILE_PATH = "data/database.db"
RSS_FILE_PATH = "data/rss.xml"
DEVELOPMENT = False
