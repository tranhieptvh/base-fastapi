from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.seeders.database_seeder import DatabaseSeeder
import os
from dotenv import load_dotenv

def init_test_db():
    # Load test environment variables and override any existing ones
    load_dotenv('.env.test', override=True)
    
    # Force using test database URL
    os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    # Create new engine and session for test database
    engine = create_engine(os.getenv('DATABASE_URL'))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        seeder = DatabaseSeeder(db)
        seeder.run()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating initial test data")
    init_test_db()
    print("Initial test data created") 