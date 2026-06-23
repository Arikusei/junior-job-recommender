from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.services import app_state


@asynccontextmanager
async def lifespan(_: FastAPI):
    app_state.load()
    yield


app = FastAPI(
    title="Junior Job Recommender",
    description="Pet-project: semantic search, recommendations, A/B tests, monitoring",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(router)
