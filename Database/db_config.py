from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


db_url = "postgresql://postgres:password@localhost:5432/Customer360"

engine = create_engine(db_url)


session = sessionmaker(autoflush= False, autocommit= False, bind=engine)