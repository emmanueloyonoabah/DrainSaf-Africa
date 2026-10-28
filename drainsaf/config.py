"""Constantes métier, barèmes de criticité et palette de DrainSaf Africa."""
from __future__ import annotations

from pathlib import Path

APP_NAME = "DrainSaf Africa"
APP_TAGLINE = "Inspection, analyse et maintenance du drainage urbain"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "inspections.csv"

# --------------------------------------------------------------------------- #
# Rôles
# --------------------------------------------------------------------------- #
ROLE_FIELD = "inspecteur"
ROLE_ENGINEER = "ingenieur"
ROLE_LABELS = {
    ROLE_FIELD: "Inspecteur Terrain",
    ROLE_ENGINEER: "Ingénieur Municipal / Administrateur",
}

# --------------------------------------------------------------------------- #
# Palette (bleu technique, gris ardoise, accents sémantiques stricts)
# --------------------------------------------------------------------------- #
NAVY = "#0B2545"
BLUE = "#1262B3"
BLUE_SOFT = "#EAF2FB"
SLATE = "#334155"
SLATE_MID = "#64748B"
BORDER = "#E2E8F0"
GREEN = "#16A34A"
ORANGE = "#EA8A0C"
RED = "#DC2626"

# --------------------------------------------------------------------------- #
# Référentiels géographiques
# --------------------------------------------------------------------------- #
VILLES_QUARTIERS = {
    "Douala": [
        "Akwa", "Bépanda", "Bali", "Bonabéri", "Bonamoussadi", "Bonanjo",
        "Bonapriso", "Brazzaville", "Cité des Palmiers", "Deido", "Kotto",
        "Logbessou", "Logpom", "Makepe", "New Bell", "Ndokotti", "Nylon",
        "PK14", "Yassa",
    ],
    "Yaoundé": [
        "Bastos", "Biyem-Assi", "Briqueterie", "Emana", "Essos", "Etoudi",
        "Melen", "Mendong", "Messa", "Mokolo", "Mvan", "Mvog-Mbi",
        "Ngoa-Ekellé", "Nkolbisson", "Nlongkak", "Nsam", "Obili", "Tsinga",
    ],
    "Autre ville": [],
}
AUTRE = "Autre (à préciser)"

# --------------------------------------------------------------------------- #
# Typologie et critères d'inspection
# --------------------------------------------------------------------------- #
TYPES_OUVRAGE = ["Caniveau ouvert", "Caniveau fermé", "Dalot", "Bassin de rétention"]

OBSTRUCTION_LEVELS = ["0-25 %", "25-50 %", "50-75 %", "> 75 %"]
OBSTRUCTION_POINTS = dict(zip(OBSTRUCTION_LEVELS, [5, 12, 21, 30]))
OBSTRUCTION_RANK = {lvl: i for i, lvl in enumerate(OBSTRUCTION_LEVELS)}

STRUCT_GOOD = "Bon état"
STRUCT_CRACK = "Fissures"
STRUCT_COLLAPSE = "Effondrement de parois / dalles manquantes"
STRUCTURE_LEVELS = [STRUCT_GOOD, STRUCT_CRACK, STRUCT_COLLAPSE]
STRUCTURE_POINTS = dict(zip(STRUCTURE_LEVELS, [0, 12, 25]))
STRUCTURE_RANK = {lvl: i for i, lvl in enumerate(STRUCTURE_LEVELS)}

DECHETS_LEVELS = ["Non", "Oui"]
DECHETS_POINTS = {"Non": 0, "Oui": 10}
NATURE_DECHETS = ["Plastiques", "Sédiments", "Végétaux", "Gravats"]

CRIT_MINOR = "Mineur"
CRIT_MODERATE = "Modéré"
CRIT_URGENT = "Urgent / Critique"
CRITICITE_LEVELS = [CRIT_MINOR, CRIT_MODERATE, CRIT_URGENT]
CRITICITE_POINTS = dict(zip(CRITICITE_LEVELS, [5, 18, 35]))

# --------------------------------------------------------------------------- #
# État du réseau (dérivé du score de gravité /100) et priorités
# --------------------------------------------------------------------------- #
ETAT_SAIN = "Sain"
ETAT_ALERTE = "Alerte"
ETAT_CRITIQUE = "Critique"
ETATS = [ETAT_SAIN, ETAT_ALERTE, ETAT_CRITIQUE]
ETAT_COLORS = {ETAT_SAIN: GREEN, ETAT_ALERTE: ORANGE, ETAT_CRITIQUE: RED}
ETAT_ICONS = {ETAT_SAIN: "🟢", ETAT_ALERTE: "🟠", ETAT_CRITIQUE: "🔴"}

SEUIL_CRITIQUE = 65  # score >= 65 -> Critique (ou criticité déclarée « Urgent »)
SEUIL_ALERTE = 35    # score >= 35 -> Alerte

PRIORITES = {
    ETAT_CRITIQUE: ("P1 · Immédiate", "≤ 72 h"),
    ETAT_ALERTE: ("P2 · Court terme", "≤ 15 jours"),
    ETAT_SAIN: ("P3 · Veille", "≤ 60 jours (entretien courant)"),
}
PRIORITE_LABELS = [v[0] for v in PRIORITES.values()]

# Seuils de lecture de l'indice de vulnérabilité (% d'ouvrages critiques)
VULN_OK = 15
VULN_WARN = 30
