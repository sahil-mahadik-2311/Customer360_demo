import uvicorn

from typing import Annotated

from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from customer360.Database.config import engine
from customer360.Database.session import get_db
from customer360.api.dependencies import emp_dependency
from customer360.Database import config

config.Base.metadata.create_all(bind=engine)
from customer360 import api

app = FastAPI()

db_dependncy = Annotated[Session, Depends(get_db)]


app.include_router(api.router)

@app.get("/", status_code=status.HTTP_200_OK)
async def employee(emp: emp_dependency, db: db_dependncy):
    if emp is None:
        raise HTTPException(status_code=401, detail="Authenticatin Failed")

    return {"Employee": emp}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
