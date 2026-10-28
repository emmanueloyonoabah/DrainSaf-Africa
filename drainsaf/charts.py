"""Graphiques Plotly au thème épuré (fond transparent, grille légère)."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import config as cfg

FONT = "Inter, system-ui, sans-serif"
OBSTRUCTION_COLORS = ["#A9CBEE", "#5B9BD5", cfg.ORANGE, cfg.RED]
STRUCTURE_COLORS = {cfg.STRUCT_GOOD: cfg.GREEN, cfg.STRUCT_CRACK: cfg.ORANGE, cfg.STRUCT_COLLAPSE: cfg.RED}


def _style(fig: go.Figure, height: int = 320, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=4, t=10, b=70 if legend else 10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, color=cfg.SLATE, size=12),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="top", y=-0.2, x=0, title_text=""),
        hoverlabel=dict(font_family=FONT, bgcolor="white", bordercolor=cfg.BORDER),
        bargap=0.35,
    )
    fig.update_xaxes(showgrid=False, linecolor=cfg.BORDER, zeroline=False, title_text="")
    fig.update_yaxes(gridcolor="#EEF2F7", zeroline=False, title_text="")
    return fig


def _empty(message: str, height: int = 280) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=13, color=cfg.SLATE_MID))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _style(fig, height, legend=False)


def gauge_vulnerability(index: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=round(index, 1),
            number=dict(suffix=" %", font=dict(size=40, family=FONT, color=cfg.NAVY)),
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1, tickcolor=cfg.BORDER, tickfont=dict(size=10)),
                bar=dict(color=cfg.NAVY, thickness=0.22),
                bgcolor="white",
                borderwidth=0,
                steps=[
                    dict(range=[0, cfg.VULN_OK], color="#CDEEDB"),
                    dict(range=[cfg.VULN_OK, cfg.VULN_WARN], color="#FCE3B8"),
                    dict(range=[cfg.VULN_WARN, 100], color="#F8CACA"),
                ],
            ),
        )
    )
    fig.update_layout(height=230, margin=dict(l=18, r=18, t=24, b=0), paper_bgcolor="rgba(0,0,0,0)", font=dict(family=FONT))
    return fig


def donut_etat(latest: pd.DataFrame) -> go.Figure:
    if latest.empty:
        return _empty("Aucune donnée")
    counts = latest["etat"].value_counts().reindex(cfg.ETATS, fill_value=0)
    fig = go.Figure(
        go.Pie(
            labels=counts.index,
            values=counts.values,
            hole=0.68,
            sort=False,
            marker=dict(colors=[cfg.ETAT_COLORS[e] for e in counts.index], line=dict(color="white", width=3)),
            textinfo="value",
            textfont=dict(size=13, color="white", family=FONT),
            hovertemplate="%{label} : %{value} ouvrage(s) (%{percent})<extra></extra>",
        )
    )
    fig.add_annotation(text=f"<b>{int(counts.sum())}</b><br><span style='font-size:11px'>ouvrages</span>",
                       showarrow=False, font=dict(size=24, color=cfg.NAVY, family=FONT))
    return _style(fig, 260)


def failure_drivers(latest: pd.DataFrame) -> go.Figure:
    """Répartition des pannes : facteurs dominants sur l'état courant du réseau."""
    if latest.empty:
        return _empty("Aucune donnée")
    data = {
        "Ensablement / obstruction > 50 %": int((latest["obstruction_rang"] >= 2).sum()),
        "Déchets solides majeurs": int((latest["dechets"] == "Oui").sum()),
        "Fissures": int((latest["structure_rang"] == 1).sum()),
        "Effondrement / dalles manquantes": int((latest["structure_rang"] == 2).sum()),
    }
    colors = [cfg.BLUE, cfg.SLATE_MID, cfg.ORANGE, cfg.RED]
    fig = go.Figure(
        go.Bar(
            x=list(data.values()),
            y=list(data.keys()),
            orientation="h",
            marker=dict(color=colors),
            text=list(data.values()),
            textposition="outside",
            hovertemplate="%{y} : %{x} ouvrage(s)<extra></extra>",
        )
    )
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(visible=False, range=[0, max(max(data.values()), 1) * 1.3])
    return _style(fig, 260, legend=False)


def _wrap(label: str) -> str:
    return label.replace(" ", "<br>", 1)


WRAPPED_TYPES = [_wrap(t) for t in cfg.TYPES_OUVRAGE]


def obstruction_by_type(latest: pd.DataFrame) -> go.Figure:
    if latest.empty:
        return _empty("Aucune donnée")
    t = latest.groupby(["type_ouvrage", "obstruction"]).size().reset_index(name="n")
    t["type_ouvrage"] = t["type_ouvrage"].map(_wrap)
    fig = px.bar(
        t, x="type_ouvrage", y="n", color="obstruction",
        category_orders={"obstruction": cfg.OBSTRUCTION_LEVELS, "type_ouvrage": WRAPPED_TYPES},
        color_discrete_sequence=OBSTRUCTION_COLORS,
        labels={"n": "Ouvrages", "obstruction": "Obstruction", "type_ouvrage": ""},
    )
    fig.update_traces(hovertemplate="%{x} · %{fullData.name} : %{y} ouvrage(s)<extra></extra>")
    return _style(fig, 320)


def structure_by_type(latest: pd.DataFrame) -> go.Figure:
    if latest.empty:
        return _empty("Aucune donnée")
    t = latest.groupby(["type_ouvrage", "etat_structurel"]).size().reset_index(name="n")
    t["type_ouvrage"] = t["type_ouvrage"].map(_wrap)
    t["etat_structurel"] = t["etat_structurel"].replace({cfg.STRUCT_COLLAPSE: "Effondrement / dalles manquantes"})
    fig = px.bar(
        t, x="type_ouvrage", y="n", color="etat_structurel",
        category_orders={"etat_structurel": ["Bon état", "Fissures", "Effondrement / dalles manquantes"],
                         "type_ouvrage": WRAPPED_TYPES},
        color_discrete_map={"Bon état": cfg.GREEN, "Fissures": cfg.ORANGE,
                            "Effondrement / dalles manquantes": cfg.RED},
        labels={"n": "Ouvrages", "etat_structurel": "État structurel", "type_ouvrage": ""},
    )
    fig.update_traces(hovertemplate="%{x} · %{fullData.name} : %{y} ouvrage(s)<extra></extra>")
    return _style(fig, 320)


def risk_by_quartier(latest: pd.DataFrame, top: int = 10) -> go.Figure:
    if latest.empty:
        return _empty("Aucune donnée")
    # Pire ouvrage de chaque quartier (score max) + nombre d'ouvrages suivis
    worst = latest.sort_values("score", ascending=False).drop_duplicates("quartier")
    counts = latest.groupby("quartier").size().rename("nb")
    worst = worst.join(counts, on="quartier").head(top)
    fig = px.bar(
        worst, y="quartier", x="score", color="etat", orientation="h",
        category_orders={"etat": cfg.ETATS, "quartier": list(worst["quartier"])},
        color_discrete_map=cfg.ETAT_COLORS,
        custom_data=["nb", "type_ouvrage"],
        labels={"score": "Score de gravité max", "etat": "État", "quartier": ""},
    )
    fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(range=[0, 100], gridcolor="#EEF2F7")
    fig.update_traces(
        hovertemplate="%{y} · score max %{x}/100<br>%{customdata[1]} · %{customdata[0]} ouvrage(s) suivi(s)<extra></extra>"
    )
    return _style(fig, 340)


def timeline(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty("Aucune donnée")
    d = df.set_index("horodatage")
    weekly = d["id"].resample("W").count()
    urgent = d[d["criticite"] == cfg.CRIT_URGENT]["id"].resample("W").count().reindex(weekly.index, fill_value=0)
    fig = go.Figure()
    fig.add_bar(x=weekly.index, y=weekly.values, name="Inspections", marker_color="#A9CBEE",
                hovertemplate="Semaine du %{x|%d/%m/%Y} : %{y} inspection(s)<extra></extra>")
    fig.add_scatter(x=urgent.index, y=urgent.values, name="Dont urgentes / critiques", mode="lines+markers",
                    line=dict(color=cfg.RED, width=2.5), marker=dict(size=7),
                    hovertemplate="Semaine du %{x|%d/%m/%Y} : %{y} urgente(s)<extra></extra>")
    fig.update_yaxes(rangemode="tozero")
    return _style(fig, 300)


def map_assets(latest: pd.DataFrame) -> go.Figure | None:
    d = latest.dropna(subset=["latitude", "longitude"])
    if d.empty:
        return None
    new_api = hasattr(px, "scatter_map")
    fn = px.scatter_map if new_api else px.scatter_mapbox
    span = max(d["latitude"].max() - d["latitude"].min(), d["longitude"].max() - d["longitude"].min())
    zoom = 13 if span < 0.05 else 11.5 if span < 0.2 else 10 if span < 0.5 else 9 if span < 1 else 7.2 if span < 3 else 5.5
    fig = fn(
        d, lat="latitude", lon="longitude", color="etat",
        category_orders={"etat": cfg.ETATS},
        color_discrete_map=cfg.ETAT_COLORS,
        hover_name="quartier",
        hover_data={"latitude": False, "longitude": False, "etat": False, "type_ouvrage": True, "rue": True, "score": True},
        zoom=zoom, center=dict(lat=float(d["latitude"].mean()), lon=float(d["longitude"].mean())),
    )
    fig.update_traces(marker=dict(size=14))
    fig.update_layout(**{"map_style" if new_api else "mapbox_style": "open-street-map"})
    fig.update_layout(
        height=340, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=0.01, x=0.01, title_text="",
                    bgcolor="rgba(255,255,255,.85)"),
        font=dict(family=FONT),
    )
    return fig
