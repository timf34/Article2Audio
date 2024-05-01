"""
Create a .env file in the root directory of the project and add the following line:
OPENAI_KEY=your_openai_key
"""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_KEY')

