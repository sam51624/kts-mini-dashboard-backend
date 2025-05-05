# create_tables.py
from db_config import engine
from db_models import Base

# สร้างทุกตารางที่กำหนดใน db_models.py
Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully!")
