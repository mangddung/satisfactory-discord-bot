# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BOT_PREFIX                = os.getenv("BOT_PREFIX", "!")
BOT_TOKEN                 = os.getenv("BOT_TOKEN")
BOT_STATUS_MESSAGE        = os.getenv("BOT_STATUS_MESSAGE", "Online")

DB_DIR                    = os.getenv("DB_DIR", "data")
APP_DB_URL              = os.getenv(
    "APP_DB_URL",
    "sqlite:///data/app.db"
)

SERVER_CHECK_INTERVAL   = int(os.getenv("SERVER_CHECK_INTERVAL", 60)) # seconds