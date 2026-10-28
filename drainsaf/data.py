"""Stockage CSV, barème de criticité, priorisation et données de démonstration."""
from __future__ import annotations

import random
import threading
import uuid
from datetime import datetime, timedelta, timezone

import pandas as pd

from . import config as cfg

TZ = timezone(timedelta(hours=1))  # WAT (Douala / Yaoundé) = UTC+1
_LOCK = threading.Lock()
SOURCE_DEMO = "démo"

COLUMNS = [
    "id", "horodatage", "inspecteur", "inspecteur_login", "ville", "quartier",
    "rue", "repere", "type_ouvrage", "latitude", "longitude", "obstruction",
    "etat_structurel", "dechets", "nature_dechets", "criticite",
    "observations", "source",
]


def now_local() -> datetime:
    return datetime.now(TZ)


# --------------------------------------------------------------------------- #
# Lecture / écriture
# --------------------------------------------------------------------------- #
def ensure_store() -> None:
    cfg.DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not cfg.DATA_FILE.exists():
        with _LOCK:
            if not cfg.DATA_FILE.exists():
                seed_demo().to_csv(cfg.DATA_FILE, index=False, encoding="utf-8")


def load_raw() -> pd.DataFrame:
    ensure_store()
    df = pd.read_csv(cfg.DATA_FILE, dtype=str, keep_default_na=False, encoding="utf-8")
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNS]


def load_inspections() -> pd.DataFrame:
    """Toutes les inspections, enrichies (score, état, priorité, action…)."""
    return enrich(load_raw())


def new_record(user: dict, **fields) -> dict:
    ts = now_local()
    rec = {c: "" for c in COLUMNS}
    rec.update(
        id=f"INS-{ts:%y%m%d-%H%M%S}-{uuid.uuid4().hex[:4].upper()}",
        horodatage=ts.strftime("%Y-%m-%d %H:%M:%S"),
        inspecteur=user["name"],
        inspecteur_login=user["login"],
        source="terrain",
    )
    rec.update(fields)
    return rec


def append_inspection(record: dict) -> None:
    ensure_store()
    row = pd.DataFrame([record], columns=COLUMNS)
    with _LOCK:
        row.to_csv(cfg.DATA_FILE, mode="a", header=False, index=False, encoding="utf-8")


def purge_demo() -> int:
    """Supprime les inspections de démonstration ; renvoie le nombre supprimé."""
    raw = load_raw()
    keep = raw[raw["source"] != SOURCE_DEMO]
    with _LOCK:
        keep.to_csv(cfg.DATA_FILE, index=False, encoding="utf-8")
    return len(raw) - len(keep)


def reload_demo() -> int:
    """Remplace les données de démonstration par un jeu neuf."""
    purge_demo()
    demo = seed_demo()
    with _LOCK:
        demo.to_csv(cfg.DATA_FILE, mode="a", header=False, index=False, encoding="utf-8")
    return len(demo)


# --------------------------------------------------------------------------- #
# Barème de gravité, états et recommandations
# --------------------------------------------------------------------------- #
def _recommend(obs_rank: int, struct_rank: int, dechets: str, typ: str) -> tuple[str, str]:
    actions: list[str] = []
    if struct_rank == 2:
        actions.append("Réhabilitation structurelle (reconstruction des parois / pose de dalles)")
    elif struct_rank == 1:
        actions.append("Réparation des fissures (ragréage / injection)")
    if typ == "Bassin de rétention" and obs_rank >= 1:
        actions.append("Curage du bassin et dégagement des ouvrages d'entrée / sortie")
    elif obs_rank == 3:
        actions.append("Curage mécanique lourd (hydrocureur)")
    elif obs_rank == 2:
        actions.append("Curage mécanique")
    elif obs_rank == 1:
        actions.append("Curage manuel")
    if dechets == "Oui":
        actions.append("Enlèvement des déchets solides")
    if not actions:
        actions.append("Surveillance : inspection de routine")

    needs_civil = struct_rank >= 1
    needs_dredge = obs_rank >= 1 or dechets == "Oui"
    if needs_civil and needs_dredge:
        team = "Équipe mixte (curage + génie civil)"
    elif needs_civil:
        team = "Équipe génie civil / réhabilitation"
    elif needs_dredge:
        team = "Équipe de curage"
    else:
        team = "Inspection de routine"
    return " + ".join(actions), team


def enrich(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["horodatage"] = pd.to_datetime(df["horodatage"], errors="coerce")
    df = df.dropna(subset=["horodatage"])
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    key = (
        df["ville"] + "|" + df["quartier"] + "|" + df["rue"] + "|"
        + df["type_ouvrage"] + "|" + df["repere"]
    )
    df["ouvrage_key"] = key.str.lower().str.replace(r"\s+", " ", regex=True).str.strip()

    df["obstruction_rang"] = df["obstruction"].map(cfg.OBSTRUCTION_RANK).fillna(0).astype(int)
    df["structure_rang"] = df["etat_structurel"].map(cfg.STRUCTURE_RANK).fillna(0).astype(int)
    df["score"] = (
        df["obstruction"].map(cfg.OBSTRUCTION_POINTS).fillna(0)
        + df["etat_structurel"].map(cfg.STRUCTURE_POINTS).fillna(0)
        + df["dechets"].map(cfg.DECHETS_POINTS).fillna(0)
        + df["criticite"].map(cfg.CRITICITE_POINTS).fillna(0)
    ).astype(int)

    urgent = df["criticite"] == cfg.CRIT_URGENT
    df["imminent"] = urgent
    critique = urgent | (df["score"] >= cfg.SEUIL_CRITIQUE)
    alerte = ~critique & (
        (df["criticite"] == cfg.CRIT_MODERATE) | (df["score"] >= cfg.SEUIL_ALERTE)
    )
    df["etat"] = cfg.ETAT_SAIN
    df.loc[alerte, "etat"] = cfg.ETAT_ALERTE
    df.loc[critique, "etat"] = cfg.ETAT_CRITIQUE
    df["priorite"] = df["etat"].map(lambda e: cfg.PRIORITES[e][0])
    df["delai"] = df["etat"].map(lambda e: cfg.PRIORITES[e][1])

    recs = [
        _recommend(o, s, d, t)
        for o, s, d, t in zip(
            df["obstruction_rang"], df["structure_rang"], df["dechets"], df["type_ouvrage"]
        )
    ]
    df["action"] = [r[0] for r in recs]
    df["equipe"] = [r[1] for r in recs]

    df = df.sort_values("horodatage").reset_index(drop=True)
    grp = df.groupby("ouvrage_key", sort=False)
    df["obs_prec"] = grp["obstruction_rang"].shift(1)
    df["struct_prec"] = grp["structure_rang"].shift(1)
    df["nb_inspections"] = grp["id"].transform("count").astype(int)
    df["evol_structure"] = _evolution(df["structure_rang"], df["struct_prec"])
    df["evol_obstruction"] = _evolution(df["obstruction_rang"], df["obs_prec"])
    return df


def _evolution(current: pd.Series, previous: pd.Series) -> pd.Series:
    delta = current - previous
    out = pd.Series("1ʳᵉ inspection", index=current.index, dtype=object)
    out[delta > 0] = "Dégradation"
    out[delta == 0] = "Stable"
    out[delta < 0] = "Amélioration"
    return out


def latest_per_asset(df: pd.DataFrame) -> pd.DataFrame:
    """Dernière inspection de chaque ouvrage (état courant du réseau)."""
    if df.empty:
        return df
    last = df.sort_values("horodatage").groupby("ouvrage_key", sort=False).tail(1)
    return last.sort_values(["score", "horodatage"], ascending=[False, False]).reset_index(drop=True)


def vulnerability_index(latest: pd.DataFrame) -> float:
    """Part (%) des ouvrages à l'état Critique."""
    if latest.empty:
        return 0.0
    return 100.0 * float((latest["etat"] == cfg.ETAT_CRITIQUE).mean())


# --------------------------------------------------------------------------- #
# Plan de maintenance et exports
# --------------------------------------------------------------------------- #
PLAN_COLUMNS = {
    "rang": "Rang",
    "priorite": "Priorité",
    "delai": "Délai d'intervention",
    "ville": "Ville",
    "quartier": "Quartier",
    "rue": "Rue",
    "type_ouvrage": "Type d'ouvrage",
    "repere": "Repère",
    "score": "Score de gravité /100",
    "obstruction": "Obstruction",
    "etat_structurel": "État structurel",
    "dechets": "Déchets majeurs",
    "criticite": "Criticité déclarée",
    "action": "Action recommandée",
    "equipe": "Équipe",
    "date_inspection": "Dernière inspection",
    "inspecteur": "Inspecteur",
}


def maintenance_plan(latest: pd.DataFrame, priorities: list[str] | None = None) -> pd.DataFrame:
    plan = latest.copy()
    if priorities is not None:
        plan = plan[plan["priorite"].isin(priorities)]
    plan = plan.sort_values(["score", "horodatage"], ascending=[False, True]).reset_index(drop=True)
    plan["rang"] = plan.index + 1
    plan["date_inspection"] = plan["horodatage"].dt.strftime("%Y-%m-%d %H:%M")
    return plan[list(PLAN_COLUMNS)].rename(columns=PLAN_COLUMNS)


def to_csv_bytes(df: pd.DataFrame, sep: str = ";") -> bytes:
    """CSV UTF-8 avec BOM (accents corrects à l'ouverture dans Excel)."""
    return ("﻿" + df.to_csv(index=False, sep=sep)).encode("utf-8")


def history_export(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values("horodatage", ascending=False).copy()
    out["horodatage"] = out["horodatage"].dt.strftime("%Y-%m-%d %H:%M:%S")
    cols = [
        "id", "horodatage", "inspecteur", "ville", "quartier", "rue", "repere",
        "type_ouvrage", "obstruction", "etat_structurel", "dechets",
        "nature_dechets", "criticite", "score", "etat", "latitude",
        "longitude", "observations",
    ]
    return out[cols]


# --------------------------------------------------------------------------- #
# Données de démonstration (réalistes, reproductibles)
# --------------------------------------------------------------------------- #
# (ville, quartier, rue, repère, type, lat, lon, gravité 0-1, structure finale)
_DEMO_ASSETS = [
    ("Douala", "Bonabéri", "Rue de l'Hôpital", "CAN-BNB-012", "Caniveau ouvert", 4.0780, 9.6790, 0.85, 1),
    ("Douala", "New Bell", "Rue Joss", "DAL-NBL-004", "Dalot", 4.0420, 9.7160, 0.90, 2),
    ("Douala", "Akwa", "Boulevard de la Liberté", "CAN-AKW-021", "Caniveau fermé", 4.0510, 9.7020, 0.35, 0),
    ("Douala", "Bépanda", "Carrefour Omnisport", "BAS-BPD-001", "Bassin de rétention", 4.0640, 9.7370, 0.70, 0),
    ("Douala", "Makepe", "Rue Missoke", "CAN-MKP-033", "Caniveau ouvert", 4.0780, 9.7440, 0.55, 1),
    ("Douala", "Deido", "Rue Prince de Galles", "CAN-DEI-008", "Caniveau ouvert", 4.0600, 9.7150, 0.20, 0),
    ("Douala", "Bonamoussadi", "Carrefour Shell", "DAL-BMD-002", "Dalot", 4.0890, 9.7380, 0.60, 1),
    ("Douala", "Ndokotti", "Carrefour Ndokotti", "CAN-NDK-015", "Caniveau fermé", 4.0560, 9.7260, 0.45, 0),
    ("Douala", "Bonapriso", "Rue Njo-Njo", "CAN-BPR-006", "Caniveau fermé", 4.0440, 9.6920, 0.15, 0),
    ("Douala", "Logbessou", "Route de Logbessou", "BAS-LGB-002", "Bassin de rétention", 4.0950, 9.7650, 0.70, 1),
    ("Yaoundé", "Mvog-Mbi", "Ancienne route Mvog-Mbi", "CAN-MVM-010", "Caniveau ouvert", 3.8300, 11.5160, 0.90, 1),
    ("Yaoundé", "Mokolo", "Rue du Marché Mokolo", "DAL-MKL-003", "Dalot", 3.8700, 11.5120, 0.65, 2),
    ("Yaoundé", "Biyem-Assi", "Carrefour Biyem-Assi", "CAN-BYA-019", "Caniveau fermé", 3.8350, 11.4880, 0.30, 0),
    ("Yaoundé", "Ngoa-Ekellé", "Rue de l'Université", "CAN-NGE-007", "Caniveau ouvert", 3.8580, 11.5010, 0.50, 1),
    ("Yaoundé", "Etoudi", "Avenue d'Etoudi", "DAL-ETD-001", "Dalot", 3.9000, 11.5200, 0.25, 0),
    ("Yaoundé", "Mendong", "Carrefour Mendong", "BAS-MDG-001", "Bassin de rétention", 3.8190, 11.4950, 0.75, 0),
    ("Yaoundé", "Essos", "Rue de l'Hôpital Essos", "CAN-ESS-014", "Caniveau fermé", 3.8670, 11.5350, 0.40, 1),
    ("Yaoundé", "Bastos", "Rue des Ambassades", "CAN-BST-002", "Caniveau fermé", 3.8960, 11.5170, 0.10, 0),
]
_DEMO_INSPECTORS = [("Jean-Paul Kamga", "inspecteur1"), ("Aïcha Ndongo", "inspecteur2")]
_DEMO_NOTES = {
    2: ["Écoulement ralenti, dépôts de sable en amont.", "Odeurs et eau stagnante visibles."],
    3: ["Eau stagnante en saison des pluies, obstruction presque totale.",
        "Risque de débordement à la prochaine averse."],
}


def seed_demo() -> pd.DataFrame:
    rng = random.Random(2025)
    now = now_local()
    rows: list[dict] = []
    for ville, quartier, rue, repere, typ, lat, lon, sev_final, struct_final in _DEMO_ASSETS:
        n = rng.choice([1, 2, 2, 3]) if sev_final < 0.85 else rng.choice([2, 3])
        offsets = sorted(rng.sample(range(2, 150), n), reverse=True)
        offsets[-1] = rng.randint(1, 20)  # dernière visite récente
        offsets = sorted(offsets, reverse=True)
        for i, days in enumerate(offsets):
            steps_back = n - 1 - i
            sev = min(1.0, max(0.02, sev_final - 0.17 * steps_back + rng.uniform(-0.04, 0.04)))
            struct = struct_final if steps_back == 0 else max(0, struct_final - rng.choice([0, 1]))
            obs = "0-25 %" if sev < 0.25 else "25-50 %" if sev < 0.5 else "50-75 %" if sev < 0.75 else "> 75 %"
            waste = rng.random() < 0.25 + 0.55 * sev
            if struct == 2 or sev >= 0.78:
                crit = cfg.CRIT_URGENT
            elif sev >= 0.45 or struct == 1:
                crit = cfg.CRIT_MODERATE
            else:
                crit = cfg.CRIT_MINOR
            when = now - timedelta(days=days, hours=rng.randint(0, 6), minutes=rng.randint(0, 59))
            who, login = rng.choice(_DEMO_INSPECTORS)
            obs_rank = cfg.OBSTRUCTION_RANK[obs]
            notes = _DEMO_NOTES.get(obs_rank, [""])
            rows.append(
                dict(
                    id=f"DEMO-{len(rows) + 1:04d}",
                    horodatage=when.strftime("%Y-%m-%d %H:%M:%S"),
                    inspecteur=who,
                    inspecteur_login=login,
                    ville=ville,
                    quartier=quartier,
                    rue=rue,
                    repere=repere,
                    type_ouvrage=typ,
                    latitude=round(lat + rng.uniform(-0.0008, 0.0008), 6),
                    longitude=round(lon + rng.uniform(-0.0008, 0.0008), 6),
                    obstruction=obs,
                    etat_structurel=cfg.STRUCTURE_LEVELS[struct],
                    dechets="Oui" if waste else "Non",
                    nature_dechets=", ".join(rng.sample(cfg.NATURE_DECHETS, 2)) if waste else "",
                    criticite=crit,
                    observations=rng.choice(notes),
                    source=SOURCE_DEMO,
                )
            )
    return pd.DataFrame(rows, columns=COLUMNS)
