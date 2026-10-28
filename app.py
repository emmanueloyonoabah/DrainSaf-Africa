"""DrainSaf Africa — point d'entrée Streamlit.

Lancement :  streamlit run app.py
"""
import pandas as pd
import streamlit as st

from drainsaf import auth, data, ui, views
from drainsaf import config as cfg

st.set_page_config(
    page_title=f"{cfg.APP_NAME} · Drainage urbain",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)


def sidebar(user: dict, cities: list[str] | None = None) -> str:
    """Barre latérale ; renvoie le périmètre (ville) choisi par l'ingénieur."""
    scope = "Toutes les villes"
    with st.sidebar:
        ui.sidebar_brand()
        ui.sidebar_user(user["name"], cfg.ROLE_LABELS[user["role"]])
        if cities is not None:
            scope = st.selectbox("Périmètre", ["Toutes les villes"] + cities, key="scope")
            st.caption(f"Données au {data.now_local():%d/%m/%Y à %H:%M} (WAT)")
            if st.button("🔄 Actualiser", key="refresh"):
                st.rerun()
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("Se déconnecter", key="logout"):
            auth.sign_out()
            st.rerun()
    return scope


def field_app(user: dict) -> None:
    sidebar(user)
    ui.page_header(
        "Saisie d'inspection terrain",
        "Renseignez l'état de l'ouvrage inspecté : le score de gravité et la priorité sont calculés automatiquement.",
        [cfg.ROLE_LABELS[user["role"]], f"{data.now_local():%d/%m/%Y}"],
    )
    views.inspection_form(user)


def engineer_app(user: dict) -> None:
    df_all = data.load_inspections()
    cities = sorted(df_all["ville"].unique()) if not df_all.empty else []
    scope = sidebar(user, cities)
    df = df_all if scope == "Toutes les villes" else df_all[df_all["ville"] == scope]
    latest = data.latest_per_asset(df)

    ui.page_header(
        "Tableau de bord du réseau de drainage",
        "Criticité, priorisation des curages, suivi structurel et exports.",
        [scope, f"{len(latest)} ouvrages", f"{len(df)} inspections"],
    )
    imminent = latest[latest["imminent"]] if not latest.empty else latest
    ui.alert_banner(imminent)

    tabs = st.tabs([
        "📊 Vue d'ensemble", "🚧 Priorisation curage", "🧱 Suivi structurel",
        "🗂️ Historique par quartier", "📝 Nouvelle inspection", "⬇️ Exports & données",
    ])
    with tabs[0]:
        views.overview(df, latest)
    with tabs[1]:
        views.priorisation(latest)
    with tabs[2]:
        views.structure(latest)
    with tabs[3]:
        views.historique(df)
    with tabs[4]:
        views.inspection_form(user)
    with tabs[5]:
        views.exports(df, latest)


def main() -> None:
    user = auth.current_user()
    ui.inject_css(login=user is None)
    if user is None:
        views.login_page()
    elif user["role"] == cfg.ROLE_ENGINEER:
        engineer_app(user)
    else:
        field_app(user)


main()
