import os
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path

class Setting:


    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')

    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME",'postgres')
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD",'password')
    DATABASE_SERVER = os.getenv("DATABASE_SERVER",'localhost')
    DATABASE_PORT = os.getenv("DATABASE_PORT",5432)
    DATABASE_NAME = os.getenv("DATABASE_NAME",'Customer360')
    DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}"
    MESSAGES_JSON_PATH = Path(__file__).parent.parent / "Raw_data" / "msg.json"

    STATUS_DELIVERED = "DELIVERED"  # Changed from "SENT" to "DELIVERED" as per request
    STATUS_FAILED = "FAILED"

setting = Setting()

    
