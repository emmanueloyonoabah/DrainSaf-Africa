"""Pages de l'application : connexion, saisie terrain et tableaux de bord."""
from __future__ import annotations

from datetime import timedelta
from html import escape as esc

import pandas as pd
import streamlit as st

from . import auth, charts, data, ui
from . import config as cfg


# --------------------------------------------------------------------------- #
# Connexion
# --------------------------------------------------------------------------- #
def login_page() -> None:
    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown(
            f"""<div class="ds-login-hero">
            <div class="ds-brand"><div class="ds-brand-logo">💧</div><div><div class="ds-brand-name">{esc(cfg.APP_NAME)}</div>
            <div class="ds-brand-sub">Drainage urbain · Afrique</div></div></div>
            <h1>Anticiper les inondations,<br>entretenir mieux.</h1>
            <div class="lead">La plateforme d'inspection et de maintenance des caniveaux, dalots et bassins de rétention,
            pensée pour les réalités de Douala, Yaoundé et des villes africaines.</div>
            <div class="ds-feature"><i>📋</i><div><b>Saisie terrain structurée</b><span>Obstruction, état structurel, déchets, risque — horodaté et tracé.</span></div></div>
            <div class="ds-feature"><i>🚨</i><div><b>Alertes d'inondation imminente</b><span>Les ouvrages critiques remontent automatiquement à l'ingénieur.</span></div></div>
            <div class="ds-feature"><i>🛠️</i><div><b>Plan de curage prioritaire</b><span>Classement par gravité, équipe et délai d'intervention, exportable.</span></div></div>
            </div>""",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        with ui.card("login"):
            st.markdown("### Connexion")
            st.caption("Accédez à votre espace selon votre rôle.")
            with st.form("login_form"):
                login = st.text_input("Identifiant", placeholder="ex. inspecteur1")
                password = st.text_input("Mot de passe", type="password")
                submitted = st.form_submit_button("Se connecter", type="primary")
            if submitted:
                user = auth.authenticate(login, password)
                if user:
                    auth.sign_in(user)
                    st.rerun()
                st.error("Identifiant ou mot de passe incorrect.")
            with st.expander("Comptes de démonstration"):
                for role, ident, pwd in auth.DEMO_HINTS:
                    st.markdown(f"**{role}**  \n`{ident}` · `{pwd}`")


# --------------------------------------------------------------------------- #
# Saisie terrain
# --------------------------------------------------------------------------- #
def _render_receipt(rec: dict) -> None:
    tone = ui.ETAT_TONE[rec["etat"]]
    urgent = ""
    if rec["imminent"]:
        urgent = ('<div style="margin-top:10px;color:#991B1B;font-weight:600">🚨 Risque d\'inondation imminent : '
                  "une alerte est remontée à l'ingénieur municipal.</div>")
    st.markdown(
        f"""<div class="ds-receipt"><h4>✅ Inspection enregistrée avec succès</h4>
        <div style="color:#4B6B58;font-size:13px">Référence <b>{esc(rec['id'])}</b> · {esc(rec['horodatage'])} · saisie par {esc(rec['inspecteur'])}</div>
        <div class="ds-receipt-grid">
          <div><span>Ouvrage</span><b>{esc(rec['type_ouvrage'])}</b></div>
          <div><span>Localisation</span><b>{esc(rec['quartier'])} · {esc(rec['rue'])}</b></div>
          <div><span>Score de gravité</span><b>{rec['score']} / 100</b></div>
          <div><span>État calculé</span>{ui.badge(rec['etat'], tone)}</div>
          <div><span>Priorité</span><b>{esc(rec['priorite'])} ({esc(rec['delai'])})</b></div>
        </div>{urgent}</div>""",
        unsafe_allow_html=True,
    )
    st.toast("Inspection enregistrée", icon="✅")


def inspection_form(user: dict) -> None:
    ss = st.session_state
    ss.setdefault("form_v", 0)
    v = ss["form_v"]

    receipt = ss.pop("last_receipt", None)
    if receipt:
        _render_receipt(receipt)

    with ui.card("form"):
        ui.step_title(1, "Localisation de l'ouvrage", "Où se trouve l'ouvrage inspecté ?")
        ville = st.selectbox("Ville", list(cfg.VILLES_QUARTIERS), key="form_ville")
        with st.form(f"form_inspection_{v}", border=False):
            c1, c2 = st.columns(2)
            quartier = c1.selectbox("Quartier", cfg.VILLES_QUARTIERS[ville] + [cfg.AUTRE], key=f"q_{v}")
            quartier_autre = c2.text_input("Si « Autre » : précisez le quartier", key=f"qa_{v}")
            c3, c4 = st.columns(2)
            rue = c3.text_input("Rue / Axe *", placeholder="ex. Rue Joss, Carrefour Omnisport", key=f"rue_{v}")
            repere = c4.text_input("Repère de l'ouvrage", placeholder="ex. CAN-AKW-021 ou PK 2+350", key=f"rep_{v}",
                                   help="Identifiant ou point kilométrique : permet de suivre le même ouvrage dans le temps.")
            type_ouvrage = st.radio("Type d'ouvrage *", cfg.TYPES_OUVRAGE, horizontal=True, key=f"type_{v}")
            with st.expander("📍 Coordonnées GPS (optionnel — alimente la carte)"):
                g1, g2 = st.columns(2)
                lat = g1.number_input("Latitude", min_value=-90.0, max_value=90.0, value=None, step=0.0001,
                                      format="%.6f", key=f"lat_{v}", placeholder="ex. 4.051000")
                lon = g2.number_input("Longitude", min_value=-180.0, max_value=180.0, value=None, step=0.0001,
                                      format="%.6f", key=f"lon_{v}", placeholder="ex. 9.702000")

            st.divider()
            ui.step_title(2, "État de l'ouvrage", "Constats visuels sur le terrain")
            obstruction = st.radio("Niveau d'ensablement / obstruction *", cfg.OBSTRUCTION_LEVELS,
                                   horizontal=True, key=f"obs_{v}",
                                   help="Part de la section hydraulique obstruée par le sable, les sédiments ou les déchets.")
            structure = st.radio("État structurel *", cfg.STRUCTURE_LEVELS, horizontal=True, key=f"str_{v}")
            d1, d2 = st.columns([1, 2])
            dechets = d1.radio("Déchets solides majeurs ? *", cfg.DECHETS_LEVELS, horizontal=True, key=f"dec_{v}")
            nature = d2.multiselect("Nature des déchets (si « Oui »)", cfg.NATURE_DECHETS, key=f"nat_{v}")

            st.divider()
            ui.step_title(3, "Évaluation du risque", "Votre appréciation du risque d'inondation")
            criticite = st.radio("Niveau de criticité / risque d'inondation *", cfg.CRITICITE_LEVELS,
                                 horizontal=True, key=f"crit_{v}")
            observations = st.text_area("Observations complémentaires", max_chars=500, height=90, key=f"obsv_{v}",
                                        placeholder="Accès difficile, riverains, matériel nécessaire…")
            st.caption(f"Traçabilité automatique : saisie enregistrée au nom de **{user['name']}** avec horodatage précis.")
            submitted = st.form_submit_button("Enregistrer l'inspection", type="primary")

    if not submitted:
        return

    quartier_final = quartier_autre.strip() if quartier == cfg.AUTRE else quartier
    errors = []
    if not quartier_final:
        errors.append("Précisez le quartier (choix « Autre »).")
    if not rue.strip():
        errors.append("La rue / l'axe est obligatoire.")
    if (lat is None) != (lon is None):
        errors.append("Renseignez la latitude ET la longitude, ou aucune des deux.")
    if errors:
        for msg in errors:
            st.error(msg)
        return

    rec = data.new_record(
        user,
        ville=ville, quartier=quartier_final, rue=rue.strip(), repere=repere.strip(),
        type_ouvrage=type_ouvrage,
        latitude="" if lat is None else round(lat, 6), longitude="" if lon is None else round(lon, 6),
        obstruction=obstruction, etat_structurel=structure, dechets=dechets,
        nature_dechets=", ".join(nature) if dechets == "Oui" else "",
        criticite=criticite, observations=observations.strip().replace("\n", " "),
    )
    data.append_inspection(rec)
    scored = data.enrich(pd.DataFrame([rec])).iloc[0]
    ss["last_receipt"] = {
        "id": rec["id"], "horodatage": rec["horodatage"], "inspecteur": rec["inspecteur"],
        "type_ouvrage": rec["type_ouvrage"], "quartier": quartier_final, "rue": rec["rue"],
        "score": int(scored["score"]), "etat": scored["etat"], "priorite": scored["priorite"],
        "delai": scored["delai"], "imminent": bool(scored["imminent"]),
    }
    ss["form_v"] += 1
    st.rerun()


# --------------------------------------------------------------------------- #
# Vue d'ensemble
# --------------------------------------------------------------------------- #
def overview(df: pd.DataFrame, latest: pd.DataFrame) -> None:
    if latest.empty:
        st.info("Aucune inspection sur ce périmètre. Utilisez l'onglet « Nouvelle inspection ».")
        return
    idx = data.vulnerability_index(latest)
    n = len(latest)
    n_crit = int((latest["etat"] == cfg.ETAT_CRITIQUE).sum())
    n_alert = int((latest["etat"] == cfg.ETAT_ALERTE).sum())
    since = pd.Timestamp(data.now_local().replace(tzinfo=None)) - timedelta(days=30)
    recent = int((df["horodatage"] >= since).sum())
    tone = "green" if idx < cfg.VULN_OK else "orange" if idx < cfg.VULN_WARN else "red"
    status = {"green": "Réseau maîtrisé", "orange": "Réseau sous tension", "red": "Réseau à haut risque"}[tone]

    cols = st.columns(5)
    cards = [
        ("🛡️", "Indice de vulnérabilité", f"{idx:.0f} %", status, tone),
        ("🏗️", "Ouvrages suivis", str(n), f"{len(df)} inspections cumulées", "blue"),
        ("🚨", "Ouvrages critiques", str(n_crit), "Priorité P1 · ≤ 72 h", "red"),
        ("⚠️", "Ouvrages en alerte", str(n_alert), "Priorité P2 · ≤ 15 jours", "orange"),
        ("🗓️", "Inspections (30 j)", str(recent), "Activité terrain récente", "slate"),
    ]
    for col, (icon, label, value, sub, t) in zip(cols, cards):
        col.markdown(ui.kpi_card(icon, label, value, sub, t), unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    g, d, p = st.columns([1, 1.1, 1.3])
    with g, ui.card("gauge"):
        ui.card_title("Indice de vulnérabilité global", "Part des ouvrages à l'état critique")
        ui.show_plot(charts.gauge_vulnerability(idx), "gauge")
        st.markdown(ui.badge(status, tone), unsafe_allow_html=True)
    with d, ui.card("donut"):
        ui.card_title("État du réseau", "Dernière inspection de chaque ouvrage")
        ui.show_plot(charts.donut_etat(latest), "donut")
    with p, ui.card("drivers"):
        ui.card_title("Répartition des pannes", "Facteurs dominants des désordres constatés")
        ui.show_plot(charts.failure_drivers(latest), "drivers")
    st.caption(
        f"**Indice de vulnérabilité** = ouvrages à l'état *Critique* ÷ ouvrages suivis. "
        f"Un ouvrage est *Critique* si sa criticité déclarée est « Urgent / Critique » ou si son score de gravité "
        f"(obstruction + structure + déchets + criticité, sur 100) atteint {cfg.SEUIL_CRITIQUE}."
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    a, b = st.columns(2)
    with a, ui.card("obs_type"):
        ui.card_title("Obstruction par type d'ouvrage", "Niveau d'ensablement / obstruction constaté")
        ui.show_plot(charts.obstruction_by_type(latest), "obs_type")
    with b, ui.card("struct_type"):
        ui.card_title("État structurel par type d'ouvrage", "Bon état, fissures, effondrements")
        ui.show_plot(charts.structure_by_type(latest), "struct_overview")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    q, m = st.columns([1, 1.15])
    with q, ui.card("quartiers"):
        ui.card_title("Quartiers les plus exposés", "Score de gravité maximal par quartier, top 10")
        ui.show_plot(charts.risk_by_quartier(latest), "quartiers")
    with m, ui.card("map"):
        ui.card_title("Cartographie des ouvrages", "Ouvrages géolocalisés, colorés par état")
        fig = charts.map_assets(latest)
        if fig is None:
            st.info("Aucun ouvrage géolocalisé : renseignez les coordonnées GPS lors de la saisie.")
        else:
            ui.show_plot(fig, "map")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    with ui.card("timeline"):
        ui.card_title("Activité d'inspection", "Inspections hebdomadaires et part urgente / critique")
        ui.show_plot(charts.timeline(df), "timeline_all")


# --------------------------------------------------------------------------- #
# Priorisation des curages / réhabilitations
# --------------------------------------------------------------------------- #
def _style_priority(value: str) -> str:
    if str(value).startswith("P1"):
        return "background-color:#FDEBEB;color:#991B1B;font-weight:700"
    if str(value).startswith("P2"):
        return "background-color:#FEF3E1;color:#9A5B05;font-weight:700"
    return "background-color:#E8F6EE;color:#166534;font-weight:700"


def priorisation(latest: pd.DataFrame) -> None:
    if latest.empty:
        st.info("Aucune inspection sur ce périmètre.")
        return
    with ui.card("prio_filters"):
        f1, f2 = st.columns([1.4, 1])
        chosen = f1.multiselect("Niveaux de priorité", cfg.PRIORITE_LABELS, default=cfg.PRIORITE_LABELS[:2], key="prio_levels")
        types = f2.multiselect("Types d'ouvrage", cfg.TYPES_OUVRAGE, default=cfg.TYPES_OUVRAGE, key="prio_types")
    scope = latest[latest["type_ouvrage"].isin(types)]
    plan = data.maintenance_plan(scope, chosen)

    k = st.columns(4)
    k[0].markdown(ui.kpi_card("🚨", "P1 · Immédiate", str((scope["etat"] == cfg.ETAT_CRITIQUE).sum()), "≤ 72 h", "red"), unsafe_allow_html=True)
    k[1].markdown(ui.kpi_card("⚠️", "P2 · Court terme", str((scope["etat"] == cfg.ETAT_ALERTE).sum()), "≤ 15 jours", "orange"), unsafe_allow_html=True)
    k[2].markdown(ui.kpi_card("🟢", "P3 · Veille", str((scope["etat"] == cfg.ETAT_SAIN).sum()), "Entretien courant", "green"), unsafe_allow_html=True)
    k[3].markdown(ui.kpi_card("📋", "Interventions au plan", str(len(plan)), "selon les filtres", "blue"), unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    with ui.card("prio_table"):
        ui.card_title("Plan de maintenance et de curage prioritaire",
                      "Classé par score de gravité décroissant — dernière inspection de chaque ouvrage")
        if plan.empty:
            st.info("Aucun ouvrage pour les filtres choisis.")
        else:
            styler = plan.style
            styler = (getattr(styler, "map", None) or styler.applymap)(_style_priority, subset=["Priorité"])
            ui.show_df(
                styler, hide_index=True, height=min(620, 60 + 36 * len(plan)),
                column_config={
                    "Rang": st.column_config.NumberColumn("Rang", width="small"),
                    "Score de gravité /100": st.column_config.ProgressColumn(
                        "Score /100", min_value=0, max_value=100, format="%d"),
                    "Action recommandée": st.column_config.TextColumn("Action recommandée", width="large"),
                },
            )
            workload = plan["Équipe"].value_counts()
            st.markdown(
                "**Charge par équipe :** "
                + " ".join(ui.badge(f"{c} × {t}", "blue") for t, c in workload.items()),
                unsafe_allow_html=True,
            )
            sep = st.radio("Séparateur CSV", [";", ","], horizontal=True, key="prio_sep",
                           format_func=lambda s: "Point-virgule (Excel FR)" if s == ";" else "Virgule (standard)")
            st.download_button(
                "⬇️ Télécharger le Plan de Maintenance et de Curage Prioritaire (CSV)",
                data=data.to_csv_bytes(plan, sep), mime="text/csv", type="primary",
                file_name=f"plan_maintenance_curage_{data.now_local():%Y%m%d_%H%M}.csv", key="dl_plan_prio",
            )


# --------------------------------------------------------------------------- #
# Suivi structurel
# --------------------------------------------------------------------------- #
_EVOL_ICON = {"Dégradation": "🔺 Dégradation", "Stable": "➖ Stable", "Amélioration": "🔻 Amélioration", "1ʳᵉ inspection": "• 1ʳᵉ inspection"}


def structure(latest: pd.DataFrame) -> None:
    if latest.empty:
        st.info("Aucune inspection sur ce périmètre.")
        return
    n_crack = int((latest["structure_rang"] == 1).sum())
    n_collapse = int((latest["structure_rang"] == 2).sum())
    n_worse = int((latest["evol_structure"] == "Dégradation").sum())
    n_good = int((latest["structure_rang"] == 0).sum())
    k = st.columns(4)
    k[0].markdown(ui.kpi_card("✅", "En bon état", str(n_good), f"{100 * n_good / len(latest):.0f} % du parc", "green"), unsafe_allow_html=True)
    k[1].markdown(ui.kpi_card("〰️", "Fissurés", str(n_crack), "Réparation à planifier", "orange"), unsafe_allow_html=True)
    k[2].markdown(ui.kpi_card("🧱", "Effondrés / dalles manquantes", str(n_collapse), "Danger public potentiel", "red"), unsafe_allow_html=True)
    k[3].markdown(ui.kpi_card("📉", "En dégradation", str(n_worse), "vs inspection précédente", "orange" if n_worse else "green"), unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    a, b = st.columns([1, 1.6])
    with a, ui.card("struct_chart"):
        ui.card_title("Répartition structurelle", "Par type d'ouvrage")
        ui.show_plot(charts.structure_by_type(latest), "struct_tab")
    with b, ui.card("struct_table"):
        ui.card_title("Ouvrages sous surveillance structurelle",
                      "Ouvrages fissurés ou effondrés, avec évolution depuis la visite précédente")
        watch = latest[latest["structure_rang"] > 0].sort_values(
            ["structure_rang", "score"], ascending=False)
        if watch.empty:
            st.success("Aucun désordre structurel constaté.")
        else:
            view = pd.DataFrame({
                "État structurel": watch["etat_structurel"],
                "Évolution": watch["evol_structure"].map(_EVOL_ICON),
                "Ville": watch["ville"], "Quartier": watch["quartier"], "Rue": watch["rue"],
                "Ouvrage": watch["type_ouvrage"], "Repère": watch["repere"],
                "Inspections": watch["nb_inspections"],
                "Dernière visite": watch["horodatage"].dt.strftime("%d/%m/%Y"),
            })
            ui.show_df(view, hide_index=True, height=min(420, 60 + 36 * len(view)))


# --------------------------------------------------------------------------- #
# Historique par quartier
# --------------------------------------------------------------------------- #
def historique(df: pd.DataFrame) -> None:
    if df.empty:
        st.info("Aucune inspection enregistrée.")
        return
    with ui.card("hist_filters"):
        f1, f2, f3 = st.columns(3)
        villes = ["Toutes"] + sorted(df["ville"].unique())
        ville = f1.selectbox("Ville", villes, key="h_ville")
        base = df if ville == "Toutes" else df[df["ville"] == ville]
        quartier = f2.selectbox("Quartier", ["Tous"] + sorted(base["quartier"].unique()), key="h_quartier")
        types = f3.multiselect("Type d'ouvrage", cfg.TYPES_OUVRAGE, default=cfg.TYPES_OUVRAGE, key="h_types")
        g1, g2 = st.columns(2)
        crits = g1.multiselect("Criticité", cfg.CRITICITE_LEVELS, default=cfg.CRITICITE_LEVELS, key="h_crit")
        dmin, dmax = df["horodatage"].min().date(), df["horodatage"].max().date()
        period = g2.date_input("Période", value=(dmin, dmax), min_value=dmin, max_value=dmax, key="h_period")

    view = base[base["type_ouvrage"].isin(types) & base["criticite"].isin(crits)]
    if quartier != "Tous":
        view = view[view["quartier"] == quartier]
    if isinstance(period, (list, tuple)) and len(period) == 2:
        start, end = period
        view = view[(view["horodatage"].dt.date >= start) & (view["horodatage"].dt.date <= end)]

    k = st.columns(4)
    k[0].markdown(ui.kpi_card("🗂️", "Inspections", str(len(view)), "selon les filtres", "blue"), unsafe_allow_html=True)
    k[1].markdown(ui.kpi_card("🏗️", "Ouvrages distincts", str(view["ouvrage_key"].nunique()), "", "slate"), unsafe_allow_html=True)
    k[2].markdown(ui.kpi_card("🚨", "Urgentes / critiques", str(int((view["criticite"] == cfg.CRIT_URGENT).sum())), "", "red"), unsafe_allow_html=True)
    mean = f"{view['score'].mean():.0f} / 100" if len(view) else "—"
    k[3].markdown(ui.kpi_card("📊", "Score moyen", mean, "gravité", "orange"), unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    with ui.card("hist_table"):
        ui.card_title("Historique des inspections", "Du plus récent au plus ancien")
        if view.empty:
            st.info("Aucune inspection pour ces filtres.")
            return
        table = view.sort_values("horodatage", ascending=False)
        out = pd.DataFrame({
            "Date": table["horodatage"].dt.strftime("%d/%m/%Y %H:%M"),
            "Inspecteur": table["inspecteur"], "Ville": table["ville"], "Quartier": table["quartier"],
            "Rue": table["rue"], "Ouvrage": table["type_ouvrage"], "Obstruction": table["obstruction"],
            "Structure": table["etat_structurel"], "Déchets": table["dechets"],
            "Criticité": table["criticite"],
            "État": table["etat"].map(lambda e: f"{cfg.ETAT_ICONS[e]} {e}"),
            "Score": table["score"], "Observations": table["observations"],
        })
        ui.show_df(out, hide_index=True, height=min(520, 60 + 36 * len(out)),
                   column_config={"Score": st.column_config.ProgressColumn("Score /100", min_value=0, max_value=100, format="%d")})
        st.download_button(
            "⬇️ Exporter cet historique (CSV)", data=data.to_csv_bytes(data.history_export(view)),
            mime="text/csv", file_name=f"historique_inspections_{data.now_local():%Y%m%d_%H%M}.csv", key="dl_hist_view",
        )
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    with ui.card("hist_timeline"):
        ui.card_title("Évolution dans le temps", "Inspections hebdomadaires sur la sélection")
        ui.show_plot(charts.timeline(view), "timeline_hist")


# --------------------------------------------------------------------------- #
# Exports & données
# --------------------------------------------------------------------------- #
def exports(df: pd.DataFrame, latest: pd.DataFrame) -> None:
    a, b, c = st.columns(3)
    stamp = f"{data.now_local():%Y%m%d_%H%M}"
    with a, ui.card("exp_plan"):
        ui.card_title("Plan de maintenance prioritaire", "P1 + P2 — dernière inspection de chaque ouvrage")
        plan = data.maintenance_plan(latest, cfg.PRIORITE_LABELS[:2])
        st.metric("Interventions", len(plan))
        st.download_button("⬇️ Télécharger le plan (CSV)", data=data.to_csv_bytes(plan), mime="text/csv",
                           type="primary", file_name=f"plan_maintenance_curage_{stamp}.csv", key="dl_plan_exp")
    with b, ui.card("exp_state"):
        ui.card_title("État courant du réseau", "Un ouvrage par ligne, avec score et état")
        state = data.maintenance_plan(latest)
        st.metric("Ouvrages", len(state))
        st.download_button("⬇️ Télécharger l'état du réseau (CSV)", data=data.to_csv_bytes(state), mime="text/csv",
                           file_name=f"etat_reseau_{stamp}.csv", key="dl_state_exp")
    with c, ui.card("exp_hist"):
        ui.card_title("Historique complet", "Toutes les inspections enregistrées")
        st.metric("Inspections", len(df))
        st.download_button("⬇️ Télécharger l'historique (CSV)", data=data.to_csv_bytes(data.history_export(df)),
                           mime="text/csv", file_name=f"historique_complet_{stamp}.csv", key="dl_hist_exp")

    st.caption("Fichiers CSV encodés en UTF-8 (BOM), séparateur « ; » : s'ouvrent directement dans Excel avec les accents.")

    with st.expander("⚙️ Administration des données"):
        raw = data.load_raw()
        n_demo = int((raw["source"] == data.SOURCE_DEMO).sum())
        st.write(f"**{len(raw)}** inspections stockées dans `data/inspections.csv`, dont **{n_demo}** de démonstration.")
        confirm = st.checkbox("Je confirme vouloir modifier les données de démonstration", key="admin_confirm")
        d1, d2 = st.columns(2)
        if d1.button("Supprimer les données de démonstration", disabled=not confirm, key="admin_purge"):
            st.success(f"{data.purge_demo()} inspection(s) de démonstration supprimée(s).")
            st.rerun()
        if d2.button("Recharger un jeu de démonstration", disabled=not confirm, key="admin_reload"):
            st.success(f"{data.reload_demo()} inspection(s) de démonstration chargée(s).")
            st.rerun()
