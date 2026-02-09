import uvicorn 

from fastapi import APIRouter , FastAPI
from Dashborad import msg_sent_tod

app = FastAPI()

app.include_router(msg_sent_tod.router,tags =["message_sent_avg"])


@app.get("/")
async def home():
    return f"Hello From DashBoard Page"




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
