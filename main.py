from fastapi import FastAPI
from app.database import Base, engine
from contextlib import asynccontextmanager
from app.routers import flats, residents, auth, users
from app import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) # Create tables on startup
    yield


app = FastAPI(title="Apartment System Management", lifespan=lifespan)
app.include_router(flats.router)
app.include_router(residents.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/health")
def getHealthStatus():
    return {"status":"ok"}
