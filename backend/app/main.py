from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import events , weather


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(weather.router)


@app.get("/")
def root():
    return {"status": "Ok"}