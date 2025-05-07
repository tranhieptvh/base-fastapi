# Empty init file

from app.db.models.user import User
from app.db.models.role import Role

# Export all models
__all__ = [
    "User",
    "Role",
]
