"""Thème (CSS) et composants HTML réutilisables."""
from __future__ import annotations

from html import escape as esc

import streamlit as st

from . import config as cfg

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
  --navy:#0B2545; --blue:#1262B3; --blue-600:#0F5199; --blue-50:#EAF2FB;
  --s900:#0F172A; --s700:#334155; --s500:#64748B; --s300:#CBD5E1; --s200:#E2E8F0; --s100:#F1F5F9;
  --bg:#F3F5F9; --card:#FFFFFF;
  --green:#16A34A; --green-50:#E8F6EE; --orange:#EA8A0C; --orange-50:#FEF3E1;
  --red:#DC2626; --red-50:#FDEBEB;
}
.stApp, .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4,
.stApp input, .stApp textarea, .stApp button, .stApp li { font-family:'Inter',system-ui,sans-serif; }
.stApp { background:var(--bg); color:var(--s900); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility:hidden; height:0; }
header[data-testid="stHeader"] { background:transparent; }
.block-container { padding-top:1.4rem; padding-bottom:3rem; max-width:1360px; }
h1,h2,h3 { color:var(--s900); letter-spacing:-.01em; }

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] { background:linear-gradient(185deg,#0B2545 0%,#10345F 100%); border-right:none; }
section[data-testid="stSidebar"] label p, section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#CBD5E1; }
section[data-testid="stSidebar"] .stButton > button {
  background:rgba(255,255,255,.08); color:#fff; border:1px solid rgba(255,255,255,.2); }
section[data-testid="stSidebar"] .stButton > button:hover { background:rgba(255,255,255,.16); border-color:#fff; color:#fff; }
.ds-brand { display:flex; align-items:center; gap:12px; padding:6px 2px 14px; }
.ds-brand-logo { width:42px; height:42px; border-radius:12px; display:grid; place-items:center; font-size:22px;
  background:linear-gradient(135deg,#1F7AD6,#0E4D8F); box-shadow:0 6px 16px rgba(18,98,179,.45); }
.ds-brand-name { color:#fff; font-weight:800; font-size:17px; line-height:1.1; letter-spacing:-.01em; }
.ds-brand-sub { color:#93B4D8; font-size:11.5px; font-weight:500; }
.ds-user { background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.12); border-radius:12px; padding:12px 14px; margin:6px 0 14px; }
.ds-user-name { color:#fff; font-weight:700; font-size:14px; }
.ds-user-role { color:#93B4D8; font-size:12px; margin-top:2px; }

/* ---------- Page header ---------- */
.ds-hero { background:linear-gradient(120deg,#0B2545 0%,#1262B3 100%); border-radius:16px; padding:22px 26px; color:#fff;
  display:flex; align-items:center; justify-content:space-between; gap:18px; margin-bottom:16px;
  box-shadow:0 8px 24px rgba(11,37,69,.18); }
.ds-hero h1 { color:#fff; font-size:25px; margin:0; font-weight:800; }
.ds-hero p { color:#CFE0F5; margin:4px 0 0; font-size:13.5px; }
.ds-chip { display:inline-block; background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.22);
  color:#fff; font-size:12px; font-weight:600; padding:5px 11px; border-radius:999px; margin-left:6px; white-space:nowrap; }

/* ---------- Alert banner ---------- */
.ds-alert { display:flex; gap:14px; align-items:flex-start; background:var(--red-50); border:1px solid #F5BDBD;
  border-left:6px solid var(--red); border-radius:12px; padding:14px 18px; margin-bottom:16px; }
.ds-alert-ok { background:var(--green-50); border-color:#B7E3C8; border-left-color:var(--green); align-items:center; }
.ds-dot { width:12px; height:12px; border-radius:50%; background:var(--red); margin-top:5px; flex:none;
  box-shadow:0 0 0 0 rgba(220,38,38,.6); animation:ds-pulse 1.8s infinite; }
@keyframes ds-pulse { 70% { box-shadow:0 0 0 12px rgba(220,38,38,0); } 100% { box-shadow:0 0 0 0 rgba(220,38,38,0); } }
.ds-alert-title { font-weight:800; color:#991B1B; font-size:14.5px; }
.ds-alert-ok .ds-alert-title { color:#166534; }
.ds-alert-body { color:#7F1D1D; font-size:13px; margin-top:3px; line-height:1.55; }
.ds-alert-body b { color:#991B1B; }

/* ---------- KPI cards ---------- */
.ds-kpi { position:relative; background:var(--card); border:1px solid var(--s200); border-radius:14px; padding:16px 18px 16px 20px;
  display:flex; gap:14px; align-items:center; box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 14px rgba(15,23,42,.03); overflow:hidden; height:100%; }
.ds-kpi::before { content:""; position:absolute; left:0; top:0; bottom:0; width:5px; background:var(--accent,var(--blue)); }
.ds-kpi-ico { width:44px; height:44px; border-radius:12px; display:grid; place-items:center; font-size:21px; flex:none;
  background:var(--accent-soft,var(--blue-50)); }
.ds-kpi-label { color:var(--s500); font-size:11.5px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; }
.ds-kpi-value { color:var(--s900); font-size:28px; font-weight:800; line-height:1.15; letter-spacing:-.02em; }
.ds-kpi-sub { color:var(--s500); font-size:12px; margin-top:1px; }
.ds-blue { --accent:#1262B3; --accent-soft:#EAF2FB; }
.ds-green { --accent:#16A34A; --accent-soft:#E8F6EE; }
.ds-orange { --accent:#EA8A0C; --accent-soft:#FEF3E1; }
.ds-red { --accent:#DC2626; --accent-soft:#FDEBEB; }
.ds-slate { --accent:#475569; --accent-soft:#F1F5F9; }

/* ---------- Cards / sections ---------- */
div[class*="st-key-card_"] { background:var(--card); border:1px solid var(--s200); border-radius:14px; padding:18px 20px;
  box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 14px rgba(15,23,42,.03); }
.ds-card-title { font-weight:700; font-size:15px; color:var(--s900); margin:0; }
.ds-card-sub { color:var(--s500); font-size:12.5px; margin:2px 0 8px; }
.ds-step { display:flex; align-items:center; gap:10px; margin:6px 0 8px; }
.ds-step-n { width:26px; height:26px; border-radius:50%; background:var(--blue); color:#fff; font-weight:700; font-size:13px;
  display:grid; place-items:center; flex:none; }
.ds-step-t { font-weight:700; font-size:15.5px; color:var(--s900); }
.ds-step-s { color:var(--s500); font-size:12.5px; margin:-2px 0 6px 36px; }
.ds-note { background:var(--blue-50); border:1px solid #CFE2F7; color:#17406E; border-radius:10px; padding:10px 14px; font-size:12.8px; line-height:1.55; }

/* ---------- Badges ---------- */
.ds-badge { display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:700; }
.ds-b-green { background:var(--green-50); color:#166534; }
.ds-b-orange { background:var(--orange-50); color:#9A5B05; }
.ds-b-red { background:var(--red-50); color:#991B1B; }
.ds-b-blue { background:var(--blue-50); color:#0F4A87; }

/* ---------- Receipt ---------- */
.ds-receipt { background:var(--green-50); border:1px solid #B7E3C8; border-left:6px solid var(--green); border-radius:12px; padding:16px 20px; margin-bottom:16px; }
.ds-receipt h4 { margin:0 0 6px; color:#166534; font-size:16px; }
.ds-receipt-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:8px 20px; margin-top:8px; }
.ds-receipt-grid div span { display:block; color:#4B6B58; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
.ds-receipt-grid div b { color:var(--s900); font-size:14px; }

/* ---------- Widgets ---------- */
.stTabs [data-baseweb="tab-list"] { gap:4px; background:#fff; border:1px solid var(--s200); border-radius:12px; padding:5px; margin-bottom:10px; flex-wrap:wrap; }
.stTabs [data-baseweb="tab"] { height:40px; border-radius:9px; padding:0 14px; font-weight:600; color:var(--s500); background:transparent; }
.stTabs [data-baseweb="tab"]:hover { color:var(--blue); }
.stTabs [aria-selected="true"] { background:var(--blue-50); color:var(--blue); }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button { width:100%; border-radius:10px; font-weight:700; padding:.55rem 1rem; transition:all .15s; }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {
  background:linear-gradient(135deg,#1F7AD6,#1262B3); border:none; color:#fff; box-shadow:0 4px 12px rgba(18,98,179,.28); }
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
  background:linear-gradient(135deg,#1A6FC6,#0F5199); transform:translateY(-1px); }
[data-testid="stForm"] { border:none; padding:0; background:transparent; }
div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] { border-radius:10px !important; }
[data-testid="stMain"] div[role="radiogroup"] { gap:8px; flex-wrap:wrap; }
[data-testid="stMain"] div[role="radiogroup"] > label, [data-testid="stMain"] label[data-testid="stRadioOption"] {
  background:#fff; border:1px solid var(--s300); border-radius:10px; padding:7px 14px; margin:0; transition:all .15s; }
[data-testid="stMain"] div[role="radiogroup"] > label:hover, [data-testid="stMain"] label[data-testid="stRadioOption"]:hover { border-color:var(--blue); }
[data-testid="stMain"] div[role="radiogroup"] > label:has(input:checked), [data-testid="stMain"] label[data-testid="stRadioOption"][data-selected="true"] {
  border-color:var(--blue); background:var(--blue-50); box-shadow:0 0 0 1px var(--blue) inset; }
[data-testid="stDataFrame"] { border:1px solid var(--s200); border-radius:12px; overflow:hidden; }
[data-testid="stExpander"] { background:#fff; border:1px solid var(--s200) !important; border-radius:12px; }
"""

_LOGIN_CSS = """
section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] { display:none; }
.ds-login-hero { background:linear-gradient(150deg,#0B2545 0%,#1262B3 100%); border-radius:20px; padding:44px 40px; color:#fff; min-height:560px;
  box-shadow:0 18px 40px rgba(11,37,69,.28); position:relative; overflow:hidden; }
.ds-login-hero::after { content:"💧"; position:absolute; right:-18px; bottom:-34px; font-size:210px; opacity:.07; }
.ds-login-hero h1 { color:#fff; font-size:38px; font-weight:800; margin:18px 0 6px; line-height:1.1; }
.ds-login-hero .lead { color:#CFE0F5; font-size:15.5px; max-width:460px; line-height:1.6; }
.ds-feature { display:flex; gap:12px; align-items:flex-start; margin-top:18px; }
.ds-feature i { font-style:normal; width:36px; height:36px; border-radius:10px; background:rgba(255,255,255,.14); display:grid; place-items:center; font-size:18px; flex:none; }
.ds-feature b { display:block; font-size:14.5px; }
.ds-feature span { color:#B9D0EC; font-size:13px; }
"""


def inject_css(login: bool = False) -> None:
    css = _CSS + (_LOGIN_CSS if login else "")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
# Composants
# --------------------------------------------------------------------------- #
def card(name: str):
    """Conteneur « carte » stylé (clé unique obligatoire)."""
    return st.container(key=f"card_{name}")


def card_title(title: str, subtitle: str = "") -> None:
    sub = f'<div class="ds-card-sub">{esc(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="ds-card-title">{esc(title)}</div>{sub}', unsafe_allow_html=True)


def step_title(number: int, title: str, subtitle: str = "") -> None:
    html = f'<div class="ds-step"><div class="ds-step-n">{number}</div><div class="ds-step-t">{esc(title)}</div></div>'
    if subtitle:
        html += f'<div class="ds-step-s">{esc(subtitle)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def page_header(title: str, subtitle: str, chips: list[str] | None = None) -> None:
    chips_html = "".join(f'<span class="ds-chip">{esc(c)}</span>' for c in (chips or []))
    st.markdown(
        f'<div class="ds-hero"><div><h1>{esc(title)}</h1><p>{esc(subtitle)}</p></div><div>{chips_html}</div></div>',
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    st.markdown(
        f'<div class="ds-brand"><div class="ds-brand-logo">💧</div><div><div class="ds-brand-name">{esc(cfg.APP_NAME)}</div>'
        '<div class="ds-brand-sub">Drainage urbain · Afrique</div></div></div>',
        unsafe_allow_html=True,
    )


def sidebar_user(name: str, role_label: str) -> None:
    st.markdown(
        f'<div class="ds-user"><div class="ds-user-name">👤 {esc(name)}</div><div class="ds-user-role">{esc(role_label)}</div></div>',
        unsafe_allow_html=True,
    )


def kpi_card(icon: str, label: str, value: str, sub: str = "", tone: str = "blue") -> str:
    return (
        f'<div class="ds-kpi ds-{tone}"><div class="ds-kpi-ico">{icon}</div><div>'
        f'<div class="ds-kpi-label">{esc(label)}</div><div class="ds-kpi-value">{esc(value)}</div>'
        f'<div class="ds-kpi-sub">{esc(sub)}</div></div></div>'
    )


def badge(text: str, tone: str = "blue") -> str:
    return f'<span class="ds-badge ds-b-{tone}">{esc(text)}</span>'


ETAT_TONE = {cfg.ETAT_SAIN: "green", cfg.ETAT_ALERTE: "orange", cfg.ETAT_CRITIQUE: "red"}


def alert_banner(imminent) -> None:
    """Bandeau d'alerte : ouvrages dont le risque d'inondation est imminent."""
    n = len(imminent)
    if n == 0:
        st.markdown(
            '<div class="ds-alert ds-alert-ok"><div><div class="ds-alert-title">✅ Aucun ouvrage en risque d\'inondation imminent</div>'
            '<div class="ds-alert-body" style="color:#166534">Tous les ouvrages suivis sont sous contrôle sur le périmètre sélectionné.</div></div></div>',
            unsafe_allow_html=True,
        )
        return
    items = []
    for _, r in imminent.head(4).iterrows():
        items.append(f'<b>{esc(r["quartier"])}</b> · {esc(r["rue"])} <i>({esc(r["type_ouvrage"])})</i>')
    more = f" — et {n - 4} autre(s)" if n > 4 else ""
    plural = "s" if n > 1 else ""
    st.markdown(
        f'<div class="ds-alert"><div class="ds-dot"></div><div>'
        f'<div class="ds-alert-title">⚠️ {n} ouvrage{plural} en risque d\'inondation imminent — intervention immédiate requise</div>'
        f'<div class="ds-alert-body">{" &nbsp;·&nbsp; ".join(items)}{esc(more)}</div></div></div>',
        unsafe_allow_html=True,
    )


def info_note(text: str) -> None:
    st.markdown(f'<div class="ds-note">{text}</div>', unsafe_allow_html=True)


def show_df(df, **kwargs) -> None:
    """st.dataframe pleine largeur, compatible avec toutes les versions récentes de Streamlit."""
    try:
        st.dataframe(df, width="stretch", **kwargs)
    except Exception:
        st.dataframe(df, use_container_width=True, **kwargs)


def show_plot(fig, key: str) -> None:
    st.plotly_chart(fig, config={"displayModeBar": False}, key=f"plot_{key}")
