from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def health():
    return {"status": "healthy"}


@app.get("/hello")
def health():
    return {"Message": "Hello Dev",
            "language" : "Marathi",
            "framework": "fastapi"
            }
