from sqlalchemy.ext.declarative import declarative_base

# Create base class for models
Base = declarative_base()

# Import all models here for Alembic to detect changes
from app.db.models import *  # noqa 