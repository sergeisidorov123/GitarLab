from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password


def create_roles(session):
    """Ensure admin and user roles exist"""
    for role_name in ("user", "admin"):
        role = session.query(Role).filter(Role.name == role_name).first()
        if not role:
            session.add(Role(name=role_name))
    session.commit()


def create_admin_user():
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Create roles
        create_roles(db)

        # Get admin role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            # Update role if needed
            if admin_user.role_id != admin_role.id:
                admin_user.role_id = admin_role.id
                db.commit()
            print("Admin user already exists")
            return

        # Create admin user
        password_hash = hash_password("admin123")
        admin = User(
            username="admin",
            password_hash=password_hash,
            role_id=admin_role.id
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Admin user created: {admin.username} (ID: {admin.id})")
        print("Login credentials: admin / admin123")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()