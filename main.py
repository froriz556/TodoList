import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == "main":
    uvicorn.run("main:app", reload=True)
