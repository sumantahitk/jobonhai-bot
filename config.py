# config.py
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.freejobalert.com"
LIST_URL = BASE_URL + "/latest-notifications/"
JSON_FILE = "jobs.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Telegram

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")