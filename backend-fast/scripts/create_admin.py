import asyncio
import argparse
from sqlalchemy.orm import sessionmaker
from app.core.database import engine, Base
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.core.security import get_password_hash

async def create_admin(username, email, password, org_name):
    """Create an admin user and their organization."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if organization already exists
        organization = db.query(Organization).filter(Organization.name == org_name).first()
        if not organization:
            organization = Organization(name=org_name)
            db.add(organization)
            db.flush()

        # Check if user already exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User with email {email} already exists.")
            return

        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            organization_id=organization.id
        )
        db.add(admin_user)
        db.commit()

        print(f"Admin user '{username}' for organization '{org_name}' created successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new admin user and organization.")
    parser.add_argument("--username", required=True, help="Admin's username")
    parser.add_argument("--email", required=True, help="Admin's email")
    parser.add_argument("--password", required=True, help="Admin's password")
    parser.add_argument("--org", required=True, help="Organization name")

    args = parser.parse_args()

    asyncio.run(create_admin(args.username, args.email, args.password, args.org))
