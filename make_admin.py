"""
make_admin.py
─────────────
Lance ce script UNE FOIS pour accorder les droits admin à un utilisateur existant.

Usage :
    python make_admin.py ton@email.com
"""

import sys
import os

# Ajoute le dossier racine du projet au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_user_by_email, set_user_admin


def main():
    init_db()

    if len(sys.argv) < 2:
        print("Usage : python make_admin.py <email>")
        sys.exit(1)

    email = sys.argv[1].strip()
    user = get_user_by_email(email)

    if not user:
        print(f"❌ Aucun utilisateur trouvé avec l'email : {email}")
        sys.exit(1)

    set_user_admin(user["id"], admin=True)
    print(f"✅ Droits admin accordés à : {user['username']} ({email})")


if __name__ == "__main__":
    main()
