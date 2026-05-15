from database import SessionLocal, Base, engine
from models import User
from auth import get_password_hash
import sys

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).filter_by(email="admin@uzbetech.local").first():
        admin = User(
            username="superadmin",
            email="admin@uzbetech.local",
            hashed_password=get_password_hash("UzbeTech2026!"),
            is_superadmin=True
        )
        db.add(admin)
        db.commit()
        print("Admin user created: admin@uzbetech.local / UzbeTech2026!")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    init_db()
