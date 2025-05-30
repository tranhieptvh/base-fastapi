from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.db.base import Base
from src.core.enums import RoleEnum

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="role")

    @classmethod
    def get_default_role(cls, db):
        """Get default user role"""
        return db.query(cls).filter_by(id=RoleEnum.USER.value).first()

    @classmethod
    def get_admin_role(cls, db):
        """Get admin role"""
        return db.query(cls).filter_by(id=RoleEnum.ADMIN.value).first() 