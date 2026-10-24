from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello" : "Naresh"}

@app.get("/health")
def getHealthStatus():
    return {"status":"ok"}
