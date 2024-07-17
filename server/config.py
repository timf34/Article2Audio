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
AUDIO_FILE_NAME = "tmp/audio.mp3"
AUDIO_DATA_DIR_NAME = "data"
LAST_MODIFIED_FILE_NAME = "tmp/last_modified.txt"
DEVELOPMENT = False
