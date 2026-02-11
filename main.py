import uvicorn

from typing import Annotated

from fastapi import FastAPI, status, Depends, HTTPException
from Dashborad import msg_sent_tod
from Auth import jwt_auth_ref

from Auth.jwt_auth_ref import get_current_user_info

from sqlalchemy.orm import Session
from Database.db_config import engine
from Database.init_db import get_db

from Database import db_config
db_config.Base.metadata.create_all(bind=engine)

app = FastAPI()

db_dependncy = Annotated[Session, Depends(get_db)]
emp_dependency = Annotated[dict, Depends(get_current_user_info)]


app.include_router(msg_sent_tod.router, tags=["message_sent_tod"])
app.include_router(jwt_auth_ref.router)


@app.get("/", status_code=status.HTTP_200_OK)
async def employee(emp: emp_dependency, db: db_dependncy):
    if emp is None:
        raise HTTPException(status_code=401, detail="Authenticatin Failed")

    return {"Employee": emp}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
