from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import Base, engine
from routers.team import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Team Directory API", lifespan=lifespan)
app.include_router(router)