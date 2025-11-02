"""
Script to create an admin user in the database.
Fixed version using bcrypt directly.
"""
import bcrypt
from app.database import SessionLocal, engine, Base
from app.models import User

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Hash password using bcrypt directly
        password = "admin123"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Email: admin@example.com")
        print("Password: admin123")
        print("\nPlease change the password after first login!")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

