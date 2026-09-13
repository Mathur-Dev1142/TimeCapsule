from fastapi import FastAPI
from app.routers import events , weather


app = FastAPI()
app.include_router(events.router)
app.include_router(weather.router)


@app.get("/")
def root():
    return {"status": "Ok"}