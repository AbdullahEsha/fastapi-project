#filepath @main.py

from fastapi import FastAPI
from routes.authRouter import authRouter
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(authRouter, prefix="/api/v1/auth")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5000)



