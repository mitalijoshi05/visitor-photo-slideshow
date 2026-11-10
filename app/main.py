from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # server start hote hi tables ban jayein
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"message": "Visitor Photo Slideshow is running"}