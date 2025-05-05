# setup_db.py
from db_models import Base
from db_config import engine

if __name__ == "__main__":
    print("Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

