from sqlalchemy.orm import Session
from typing import Optional

class BaseSeeder:
    def __init__(self, db: Session):
        self.db = db

    def run(self):
        """Run the seeder"""
        raise NotImplementedError("Seeder must implement run method")

    def call(self, seeder_class: type):
        """Call another seeder"""
        seeder = seeder_class(self.db)
        seeder.run()

    def truncate(self, model_class):
        """Truncate table before seeding"""
        self.db.query(model_class).delete()
        self.db.commit()

    def create(self, model_class, **kwargs):
        """Create a new record"""
        instance = model_class(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance 