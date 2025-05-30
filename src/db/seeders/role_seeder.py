from src.db.models.role import Role
from src.db.seeders.base import BaseSeeder
from src.core.enums import RoleEnum

class RoleSeeder(BaseSeeder):
    def run(self):
        print("Seeding roles...")
        
        # Create roles
        admin_role = self.create(
            Role,
            id=RoleEnum.ADMIN.value,
            name="admin"
        )
        print(f"Created admin role: {admin_role.name}")
        
        user_role = self.create(
            Role,
            id=RoleEnum.USER.value,
            name="user"
        )
        print(f"Created user role: {user_role.name}")
        
        print("Role seeding completed!") 