from app.dependencies.db import SessionLocal
from app.db.seeders.database_seeder import DatabaseSeeder

def init_db():
    db = SessionLocal()
    try:
        seeder = DatabaseSeeder(db)
        seeder.run()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created") 