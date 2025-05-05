# db_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# เชื่อมต่อ PostgreSQL ผ่าน Public IP
DATABASE_URL = "postgresql+psycopg2://postgres:Man219551624@34.132.113.178:5432/postgres"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
