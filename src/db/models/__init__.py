# Empty init file

from src.db.models.user import User
from src.db.models.role import Role

# Export all models
__all__ = [
    "User",
    "Role",
]
