"""Test authentication functions"""
from app.database import SessionLocal
from app.models import User
from app.auth import verify_password, get_password_hash
import bcrypt

db = SessionLocal()

# Test admin user password
admin = db.query(User).filter(User.username == 'admin').first()
if admin:
    print(f"Admin found: {admin.username}")
    print(f"Hash length: {len(admin.hashed_password)}")
    print(f"Hash starts with: {admin.hashed_password[:15]}")
    
    # Test verification with our function
    result1 = verify_password("admin123", admin.hashed_password)
    print(f"verify_password result: {result1}")
    
    # Test verification with bcrypt directly
    result2 = bcrypt.checkpw("admin123".encode('utf-8'), admin.hashed_password.encode('utf-8'))
    print(f"bcrypt.checkpw result: {result2}")
    
    # Test creating a new hash
    new_hash = get_password_hash("testpass123")
    print(f"New hash created: {new_hash[:15]}...")
    
    # Test verifying new hash
    result3 = verify_password("testpass123", new_hash)
    print(f"New hash verification: {result3}")
else:
    print("Admin user not found")

db.close()

