from app.Database.config import session 

def get_db():

    db = session()

    try:
        yield db
    finally:
        db.close()