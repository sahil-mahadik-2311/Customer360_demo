from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base

from Secret import Setting

Base = declarative_base()


db_url = Setting.DATABASE_URL

engine = create_engine(db_url)


session = sessionmaker(autoflush= False, autocommit= False, bind=engine)