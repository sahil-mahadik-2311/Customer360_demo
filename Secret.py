import os
from dotenv import load_dotenv
load_dotenv()

class Setting:


    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = os.getenv('ALGORITHM')

    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME",'postgres')
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD",'password')
    DATABASE_SERVER = os.getenv("DATABASE_SERVER",'localhost')
    DATABASE_PORT = os.getenv("DATABASE_PORT",5432)
    DATABASE_NAME = os.getenv("DATABASE_NAME",'Customer360')
    DATABASE_URL = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_NAME}"

setting = Setting()