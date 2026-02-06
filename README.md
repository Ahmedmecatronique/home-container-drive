
# 🏠 HOME CONTAINER DRIVE

**Mini-cloud local portable, 100% offline**, basé sur **Raspberry Pi 4 + SSD externe**.  
Une solution simple et légère pour le **partage de fichiers**, le **stockage privé par utilisateur** et la **gestion multi-utilisateurs**, sans Internet.

---

## 🚀 Objectif du projet

HOME CONTAINER DRIVE vise à créer un **mini-serveur cloud local** capable de fonctionner :

- 📡 **Sans Internet**
- 🔌 **Sans routeur externe**
- 🔋 **Sur batterie**
- 👥 **Avec plusieurs utilisateurs**
- 💾 **Avec stockage sur SSD**

Cas d’usage :
- Travail d’équipe sur le terrain  
- Classes / ateliers  
- Partage de fichiers local  
- Mini-NAS portable  
- Projet académique (PFE)

---

## 🧱 Architecture générale

### 🔧 Matériel
- Raspberry Pi 4 (4 Go RAM recommandé)
- Raspberry Pi OS Lite
- micro-SD : OS + backend + frontend + base SQLite
- SSD USB : stockage des fichiers utilisateurs
- Alimentation via powerbank

### 🧠 Logiciel
- **Backend** : FastAPI (Python)
- **Frontend** : HTML / CSS / JavaScript (statique)
- **Base de données** : SQLite
- **Stockage fichiers** : système de fichiers Linux

---

## 📁 Organisation du projet

```

home_container_drive/
│
├── app/
│   ├── main.py              # Point d’entrée FastAPI
│   ├── database.py          # SQLite + SQLAlchemy
│   ├── models.py            # Modèles User & File
│   ├── schemas.py           # Schémas Pydantic
│   ├── auth.py              # Authentification (bcrypt + JWT)
│   ├── routes_auth.py       # /auth/login
│   ├── routes_workspace.py  # Workspace partagé
│   ├── routes_container.py  # Containers privés (en cours)
│   ├── routes_admin.py      # Admin (en cours)
│   └── **init**.py
│
├── data/
│   ├── workspace/           # Fichiers partagés
│   └── users/               # Containers privés par utilisateur
│
├── static/
│   ├── index.html           # Interface web
│   ├── styles.css           # CSS dashboard
│   └── app.js               # Logique frontend
│
├── scripts/                 # Scripts système (à venir)
├── logs/                    # Logs (prévu)
├── home_container.db        # Base SQLite
├── create_admin.py          # Script création admin
├── venv/                    # Environnement virtuel Python
└── README.md

````

---

## 👥 Rôles utilisateurs

Le système repose sur **3 rôles stricts** :

### 🔵 Utilisateur normal
- Accès au workspace partagé
- Upload / téléchargement
- ❌ Pas de suppression
- ❌ Pas de container privé

### 🟢 Utilisateur avancé
- Accès au workspace partagé
- Suppression **uniquement** de ses propres fichiers
- Container privé personnel (`/data/users/<username>/`)

### 🔴 Administrateur
- Accès total
- Gestion des utilisateurs
- Accès à tous les fichiers
- Supervision du stockage

---

## ✨ Fonctionnalités actuelles

✔ Serveur FastAPI opérationnel  
✔ Interface web responsive  
✔ Authentification (login)  
✔ Workspace partagé fonctionnel  
✔ Upload / download de fichiers  
✔ Base SQLite stable  
✔ Admin créé via script CLI  
✔ Accès local via navigateur  

---
