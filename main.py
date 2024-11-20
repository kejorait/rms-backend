import uvicorn
import app
import os
from dotenv import load_dotenv
load_dotenv(override=True)

ENV = os.getenv("ENV")
PORT = os.getenv("PORT")
WORKERS_COUNT = os.getenv("WORKERS_COUNT")

if __name__ == "__main__":
    if ENV == "DEV":
        uvicorn.run("app:app", host="0.0.0.0", port=int(PORT), reload=True)
    else:
        uvicorn.run("app:app", host="0.0.0.0", port=int(PORT), workers=int(WORKERS_COUNT) if WORKERS_COUNT else 1)