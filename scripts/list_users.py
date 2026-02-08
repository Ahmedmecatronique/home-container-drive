"""
List users from the SQLite DB.
Usage: python scripts/list_users.py
"""
from datetime import datetime
from app.database import SessionLocal
from app import models


def main():
    db = SessionLocal()
    users = db.query(models.User).order_by(models.User.id).all()
    if not users:
        print("No users found in database.")
        return
    print(f"Found {len(users)} user(s):\n")
    print(f"{'ID':<4}{'USERNAME':<20}{'ROLE':<10}{'CREATED_AT'}")
    print("-" * 70)
    for u in users:
        created = u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "-"
        print(f"{u.id:<4}{u.username:<20}{u.role:<10}{created}")


if __name__ == '__main__':
    main()
