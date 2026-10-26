from fastapi import FastAPI

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine) # Create tables on startup
    yield


app = FastAPI("Apartment System Management", lifespan=lifespan)
app.include_router(flats.router)
app.include_router(residents.router)

@app.get("/health")
def getHealthStatus():
    return {"status":"ok"}
