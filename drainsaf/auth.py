"""Authentification par rôles basée sur st.session_state.

Les comptes de démonstration ci-dessous peuvent être remplacés (déploiement)
par des comptes définis dans `st.secrets["users"]` — voir GUIDE.md.
"""
from __future__ import annotations

import hashlib
import hmac
import time

import streamlit as st

from .config import ROLE_ENGINEER, ROLE_FIELD

SESSION_KEY = "user"

# Mots de passe de démonstration (affichés sur l'écran de connexion) :
#   inspecteur1 / Inspect2025   inspecteur2 / Inspect2026   ingenieur / Drain2025
DEMO_USERS = {
    "inspecteur1": {
        "name": "Jean-Paul Kamga",
        "role": ROLE_FIELD,
        "password_sha256": "6256d08af1fcf7e9f8fc13c808fb302dcb9d1a7ac4f57bddabf1b3d081231dcd",
    },
    "inspecteur2": {
        "name": "Aïcha Ndongo",
        "role": ROLE_FIELD,
        "password_sha256": "f6dc16ffc34da73d72deb5425a2d0bee8c06d338d34209be740435250a8c8d12",
    },
    "ingenieur": {
        "name": "Ing. Marie Etoundi",
        "role": ROLE_ENGINEER,
        "password_sha256": "481945303974b5dcb7fddba45bab7d842359bbc9134bb263f141ae45da68a73d",
    },
}
DEMO_HINTS = [
    ("Inspecteur Terrain", "inspecteur1", "Inspect2025"),
    ("Ingénieur Municipal", "ingenieur", "Drain2025"),
]


def _users() -> dict:
    """Comptes issus de st.secrets si présents, sinon comptes de démonstration."""
    try:
        secret_users = st.secrets.get("users")
        if secret_users:
            return {str(k): dict(v) for k, v in secret_users.items()}
    except Exception:  # pas de fichier secrets en local
        pass
    return DEMO_USERS


def authenticate(login: str, password: str) -> dict | None:
    users = _users()
    account = users.get(login.strip())
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    expected = (account or {}).get("password_sha256", "0" * 64)
    ok = hmac.compare_digest(digest, str(expected))  # temps constant
    if account and ok and account.get("role") in (ROLE_FIELD, ROLE_ENGINEER):
        return {"login": login.strip(), "name": account.get("name", login), "role": account["role"]}
    time.sleep(0.6)  # freine les essais répétés
    return None


def sign_in(user: dict) -> None:
    st.session_state[SESSION_KEY] = user


def sign_out() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def current_user() -> dict | None:
    return st.session_state.get(SESSION_KEY)
