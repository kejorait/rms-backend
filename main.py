import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

os.makedirs("./logs", exist_ok=True)
import router

load_dotenv()

app = FastAPI()

ENV = os.getenv("ENV")
WORKERS_COUNT = os.getenv("WORKERS_COUNT")


@app.on_event("startup")
async def startup_event():
    print("Main application is starting up.")

app.include_router(router.router)


if __name__ == "__main__":
    if ENV == "DEV":
        print("Running in development mode")
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)

    else:
        print("Running in production mode")
        uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), workers=WORKERS_COUNT)

    # Start Socket.IO on port 8888
    # uvicorn.run(sio_app, host="0.0.0.0", port=1001)
