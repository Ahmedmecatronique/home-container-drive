"""
Change a user's password (interactive).
Usage: python scripts/change_password.py <username>
The script will prompt for the new password (hidden).
"""
import sys
from getpass import getpass
from app.database import SessionLocal
from app import models
from app.auth import hash_password, verify_password


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/change_password.py <username>")
        return
    username = sys.argv[1]
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        print(f"User '{username}' not found.")
        return

    # Optionally require current password
    cur = getpass("Current password (leave empty to skip check): ")
    if cur:
        if not verify_password(cur, user.password_hash):
            print("Current password is incorrect.")
            return

    newp = getpass("New password: ")
    newp2 = getpass("Confirm new password: ")
    if newp != newp2:
        print("Passwords do not match.")
        return
    if not newp:
        print("Empty password not allowed.")
        return

    user.password_hash = hash_password(newp)
    db.add(user)
    db.commit()
    print(f"Password updated for user '{username}'.")


if __name__ == '__main__':
    main()
