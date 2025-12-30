from database import engine, Base
from models import user, letter

print("🔄 Updating Database Schema...")
Base.metadata.create_all(bind=engine)
print("✅ Database Schema Updated!")
