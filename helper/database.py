import os

from dotenv import load_dotenv
from sqlalchemy import QueuePool, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv(override=True)

pg_user = os.getenv("PG_USER")
pg_pwd = os.getenv("PG_PWD")
pg_port = os.getenv("PG_PORT")
pg_db = os.getenv("PG_DB")
pg_host = os.getenv("PG_HOST")

DATABASE_URL = f"postgresql+psycopg://{pg_user}:{pg_pwd}@{pg_host}:{pg_port}/{pg_db}"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,       # Use QueuePool (default pool implementation)
    pool_size=10,              # The size of the pool to hold connections (default: 5)
    max_overflow=20,           # Connections beyond pool_size (default: 10)
    pool_timeout=30,           # Timeout in seconds for getting a connection (default: 30)
    pool_recycle=1800,         # Recycle connections after 30 minutes (default: -1, no recycle)
    pool_pre_ping=True         # Test connections before use to avoid stale connections
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()