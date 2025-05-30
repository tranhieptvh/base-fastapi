from src.core.security import get_password_hash
from src.db.models.user import User
from src.db.models.role import Role
from src.db.seeders.base import BaseSeeder

class UserSeeder(BaseSeeder):
    def run(self):
        print("Seeding users...")
        
        # Get roles
        admin_role = self.db.query(Role).filter_by(name="admin").first()
        user_role = self.db.query(Role).filter_by(name="user").first()
        
        if not admin_role or not user_role:
            raise Exception("Roles not found. Please run RoleSeeder first.")
        
        # Create admin user
        admin = self.create(
            User,
            email="admin@example.com",
            username="admin",
            password=get_password_hash("admin123"),
            full_name="Admin User",
            role_id=admin_role.id,
            is_active=True
        )
        print(f"Created admin user: {admin.email}")
        
        # Create regular user
        user = self.create(
            User,
            email="user@example.com",
            username="user",
            password=get_password_hash("user123"),
            full_name="Regular User",
            role_id=user_role.id,
            is_active=True
        )
        print(f"Created regular user: {user.email}")
        
        print("User seeding completed!") 