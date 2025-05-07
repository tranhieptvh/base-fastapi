from app.db.models.role import Role
from app.db.seeders.base import BaseSeeder

class RoleSeeder(BaseSeeder):
    def run(self):
        print("Seeding roles...")
        
        # Truncate roles table
        self.truncate(Role)
        
        # Create roles
        admin_role = self.create(
            Role,
            name="admin"
        )
        print(f"Created admin role: {admin_role.name}")
        
        user_role = self.create(
            Role,
            name="user"
        )
        print(f"Created user role: {user_role.name}")
        
        print("Role seeding completed!") 