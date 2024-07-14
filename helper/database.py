from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

pg_user = os.getenv("PG_USER")
pg_pwd = os.getenv("PG_PWD")
pg_port = os.getenv("PG_PORT")
pg_db = os.getenv("PG_DB")
pg_host = os.getenv("PG_HOST")

DATABASE_URL = f"postgresql://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()