import uvicorn

from typing import Annotated

from fastapi import FastAPI, status, Depends, HTTPException
from Dashboard import msg_sent_tod , OtherAPI
from Auth import JWTauth

#from Auth.jwt_auth_ref import get_current_employee 
from Auth.JWTauth import get_current_employee

from sqlalchemy.orm import Session
from app.Database.config import engine
from app.Database.session import get_db

from app.Database import config
config.Base.metadata.create_all(bind=engine)

app = FastAPI()

db_dependncy = Annotated[Session, Depends(get_db)]
emp_dependency = Annotated[dict, Depends(get_current_employee)]


app.include_router(msg_sent_tod.router, tags=["message_sent_today"])
app.include_router(JWTauth.router)
app.include_router(OtherAPI.router, tags=["Other APIs"])


@app.get("/", status_code=status.HTTP_200_OK)
async def employee(emp: emp_dependency, db: db_dependncy):
    if emp is None:
        raise HTTPException(status_code=401, detail="Authenticatin Failed")

    return {"Employee": emp}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
