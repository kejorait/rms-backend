import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

os.makedirs("./logs", exist_ok=True)
import router

load_dotenv()

app = FastAPI()
# Set up CORS for development environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENV = os.getenv("ENV")
WORKERS_COUNT = os.getenv("WORKERS_COUNT")

app.include_router(router.router)

if __name__ == "__main__":
    if ENV == "DEV":
        print("Running in development mode")
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)

    else:
        print("Running in production mode")
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), workers=WORKERS_COUNT)