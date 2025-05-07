from app.db.seeders.base import BaseSeeder
from app.db.seeders.role_seeder import RoleSeeder
from app.db.seeders.user_seeder import UserSeeder

class DatabaseSeeder(BaseSeeder):
    def run(self):
        print("Starting database seeding...")
        
        # Call all seeders in order
        self.call(RoleSeeder)  # Run RoleSeeder first
        self.call(UserSeeder)  # Then run UserSeeder
        # Add more seeders here as needed
        # self.call(ProductSeeder)
        # self.call(CategorySeeder)
        # etc...
        
        print("Database seeding completed!") 