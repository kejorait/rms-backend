import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import jwt
from functools import wraps
from dotenv import load_dotenv
import yaml
import uvicorn

from routers import router

load_dotenv()

app = FastAPI()

ENV = os.getenv("ENV")

pg_user = os.getenv("PG_USER")
pg_pwd = os.getenv("PG_PWD")
pg_port = os.getenv("PG_PORT")
pg_db = os.getenv("PG_DB")
pg_host = os.getenv("PG_HOST")

DATABASE_URL = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = os.getenv("SECRET_KEY")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(token: str, role_list: list):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload["role_cd"] not in role_list:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authentication token",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


app.include_router(router.router)


if __name__ == "__main__":
    if ENV == "DEV":
        print("Running in development mode")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

    else:
        print("Running in production mode")
        # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
        uvicorn.run("main:app", host="0.0.0.0", port=3000)
