from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.analisis import (
    COLUMNAS_PERFIL,
    ETIQUETAS_VARIABLES,
    calcular_evidencia_estadistica,
    cargar_datos,
    ejecutar_clasificacion,
    ejecutar_clustering,
    filtrar_datos,
    predecir_hit_simulador,
)
from src.estilo import (
    PALETA,
    SECUENCIAL,
    aplicar_estilo,
    color_segmento,
    formato_pct,
)

st.set_page_config(
    page_title="Economía de la Atención y Fórmula de un Hit | Minería de Datos",
    layout="wide",
    initial_sidebar_state="expanded",
)

aplicar_estilo(plotly=True)


def envolver_etiqueta_eje(texto: str, ancho: int = 18) -> str:
    lineas = textwrap.wrap(str(texto), width=ancho, break_long_words=False)
    return "<br>".join(lineas) if lineas else str(texto)


def formatear_valor_perfil(col: str, valor: float) -> str:
    if pd.isna(valor):
        return "-"
    if col == "duration_min":
        return f"{float(valor):.2f} min"
    if col == "explicit_int":
        return formato_pct(float(valor), decimales=1)
    if col == "artist_followers":
        return f"{float(valor):,.0f}"
    return f"{float(valor):.1f}"


def render_nota_interna(titulo: str, detalle: str, resaltar: bool = False) -> None:
    color_borde = PALETA["acento"] if resaltar else PALETA["primario"]
    html = (
        f"<div style='"
        f"background-color: {PALETA['fondo_suave']}; "
        f"border: 1px solid {PALETA['gris_claro']}; "
        f"border-left: 4px solid {color_borde}; "
        f"border-radius: 4px; "
        f"padding: 0.7rem 0.95rem; "
        f"margin-bottom: 0.75rem; "
        f"color: {PALETA['texto']}; "
        f"font-size: 0.9rem; "
        f"line-height: 1.45;'>"
        f"<strong style='color: {PALETA['texto']};'>{titulo}:</strong> {detalle}"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def inyectar_css() -> None:
    css = (
        f"<style>"
        f".context-strip {{"
        f"background-color: {PALETA['fondo_suave']};"
        f"border: 1px solid {PALETA['gris_claro']};"
        f"border-radius: 4px;"
        f"padding: 0.5rem 0.9rem;"
        f"margin-bottom: 0.85rem;"
        f"font-size: 0.86rem;"
        f"color: {PALETA['texto']};"
        f"}}"
        f".hero-card {{"
        f"background-color: {PALETA['fondo']};"
        f"border: 1px solid {PALETA['gris_claro']};"
        f"border-left: 5px solid {PALETA['primario']};"
        f"border-radius: 4px;"
        f"padding: 1.15rem 1.4rem;"
        f"margin-bottom: 0.75rem;"
        f"height: 100%;"
        f"}}"
        f".hero-eyebrow {{"
        f"display: inline-block;"
        f"color: {PALETA['primario']};"
        f"font-size: 0.74rem;"
        f"font-weight: 700;"
        f"letter-spacing: 0.07em;"
        f"text-transform: uppercase;"
        f"margin-bottom: 0.25rem;"
        f"}}"
        f".hero-title {{"
        f"color: {PALETA['texto']};"
        f"font-size: 1.45rem;"
        f"font-weight: 700;"
        f"margin: 0.05rem 0 0.35rem 0;"
        f"line-height: 1.2;"
        f"}}"
        f".hero-motivo {{"
        f"color: {PALETA['texto']};"
        f"font-size: 0.95rem;"
        f"margin-bottom: 0.65rem;"
        f"}}"
        f".hero-specs {{"
        f"display: flex;"
        f"flex-wrap: wrap;"
        f"gap: 0.55rem;"
        f"margin-top: 0.45rem;"
        f"}}"
        f".hero-spec-item {{"
        f"background-color: {PALETA['fondo_suave']};"
        f"border: 1px solid {PALETA['gris_claro']};"
        f"border-radius: 4px;"
        f"padding: 0.35rem 0.7rem;"
        f"font-size: 0.86rem;"
        f"color: {PALETA['texto']};"
        f"}}"
        f".hero-spec-label {{"
        f"color: {PALETA['gris']};"
        f"font-weight: 600;"
        f"margin-right: 0.25rem;"
        f"}}"
        f".hero-kpi-box {{"
        f"background-color: {PALETA['fondo_suave']};"
        f"border: 1px solid {PALETA['gris_claro']};"
        f"border-radius: 4px;"
        f"padding: 0.75rem 0.95rem;"
        f"text-align: left;"
        f"margin-bottom: 0.6rem;"
        f"}}"
        f".hero-kpi-label {{"
        f"color: {PALETA['gris']};"
        f"font-size: 0.74rem;"
        f"font-weight: 600;"
        f"text-transform: uppercase;"
        f"letter-spacing: 0.04em;"
        f"margin-bottom: 0.15rem;"
        f"}}"
        f".hero-kpi-val {{"
        f"color: {PALETA['texto']};"
        f"font-size: 1.3rem;"
        f"font-weight: 700;"
        f"}}"
        f".hero-kpi-sub {{"
        f"color: {PALETA['gris']};"
        f"font-size: 0.78rem;"
        f"}}"
        f"</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


@st.cache_data(show_spinner="Cargando catálogo musical...")
def obtener_catalogo() -> pd.DataFrame:
    return cargar_datos()


@st.cache_data(show_spinner="Calculando pruebas estadísticas y entrenando modelos...")
def ejecutar_estudio(
    decadas_sel: tuple[int, ...] | None,
    tipos_sel: tuple[str, ...] | None,
    k: int,
    umbral_hit: int,
) -> dict:
    df_total = obtener_catalogo()
    df_filtrado = filtrar_datos(
        df_total,
        decadas=list(decadas_sel) if decadas_sel else None,
        tipos_album=list(tipos_sel) if tipos_sel else None,
    )

    if len(df_filtrado.dropna(subset=["year"])) < max(30, k * 5):
        return {
            "ok": False,
            "total_catalogo": len(df_total),
            "mensaje": "El subconjunto filtrado tiene muy pocos registros para entrenar los modelos.",
        }

    evidencia = calcular_evidencia_estadistica(df_filtrado)
    clustering = ejecutar_clustering(df_filtrado, k=k)
    clasificacion = ejecutar_clasificacion(df_filtrado, umbral_hit=umbral_hit)

    return {
        "ok": True,
        "total_catalogo": len(df_total),
        "df_filtrado": df_filtrado,
        "evidencia": evidencia,
        "clustering": clustering,
        "clasificacion": clasificacion,
    }


def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown(
            f"<h3 style='color:{PALETA['texto']}; margin-bottom:0.15rem;'>Economía de la Atención</h3>",
            unsafe_allow_html=True,
        )
        st.caption("Análisis estadístico, segmentación K-Means y clasificación de Hits.")
        st.divider()

        st.markdown("**1. Alcance del catálogo**")
        modo_alcance = st.radio(
            "Universo de análisis",
            options=["oficial", "personalizado"],
            format_func=lambda m: (
                "Catálogo completo del estudio (8,772 pistas)"
                if m == "oficial"
                else "Filtrado personalizado por década / formato"
            ),
            index=0,
            key="sb_modo_alcance",
        )

        if modo_alcance == "personalizado":
            decadas_disp = [1970, 1980, 1990, 2000, 2010, 2020]
            decadas_sel = st.multiselect(
                "Décadas de lanzamiento",
                options=decadas_disp,
                default=[2000, 2010, 2020],
                format_func=lambda d: f"Década {d}s",
            )
            tipos_disp = ["album", "single", "compilation"]
            tipos_sel = st.multiselect(
                "Formato de lanzamiento",
                options=tipos_disp,
                default=tipos_disp,
                format_func=lambda t: t.capitalize(),
            )
        else:
            decadas_sel = None
            tipos_sel = None

        st.divider()
        st.markdown("**2. Parámetros de modelos avanzados**")

        k = st.slider(
            "Número de clústeres K-Means (k)",
            min_value=2,
            max_value=6,
            value=4,
            step=1,
            help="El estudio oficial utiliza k = 4 clústeres para aislar el Efecto Relleno (Clúster 2).",
        )

        umbral_hit = st.slider(
            "Umbral de popularidad para Hit (Random Forest)",
            min_value=60,
            max_value=85,
            value=70,
            step=1,
            help="El estudio define un Hit como popularidad >= 70 (cuartil superior / top 25%).",
        )

        es_oficial = (modo_alcance == "oficial") and (k == 4) and (umbral_hit == 70)
    return {
        "decadas": tuple(decadas_sel) if decadas_sel else None,
        "tipos": tuple(tipos_sel) if tipos_sel else None,
        "k": k,
        "umbral_hit": umbral_hit,
        "es_oficial": es_oficial,
    }


def render_hero(params: dict, res: dict) -> None:
    df_f: pd.DataFrame = res["df_filtrado"]
    ev: dict = res["evidencia"]
    cl: dict = res["clustering"]
    rf: dict = res["clasificacion"]

    perfil_df: pd.DataFrame = cl["perfil"]
    c_relleno = int(cl["cluster_relleno"])
    c_main = int(cl["cluster_mainstream"])

    n_relleno = int(perfil_df.loc[c_relleno, "canciones"])
    dur_relleno = float(perfil_df.loc[c_relleno, "duration_min"])
    pop_art_relleno = float(perfil_df.loc[c_relleno, "artist_popularity"])
    pop_trk_relleno = float(perfil_df.loc[c_relleno, "track_popularity"])

    n_main = int(perfil_df.loc[c_main, "canciones"])
    dur_main = float(perfil_df.loc[c_main, "duration_min"])
    pop_trk_main = float(perfil_df.loc[c_main, "track_popularity"])

    red_pct = ev["reduccion_pct"] * 100 if pd.notna(ev["reduccion_pct"]) else 0.0
    dif_exp = ev["diferencia_pop_explicito"] if pd.notna(ev["diferencia_pop_explicito"]) else 0.0

    strip_html = (
        f"<div class='context-strip'>"
        f"<strong>Enfoque 1:</strong> La Economía de la Atención y la Fórmula de un Hit &nbsp;|&nbsp; "
        f"<strong>Catálogo evaluado:</strong> {len(df_f):,} canciones ({len(cl['base']):,} con fecha completa) &nbsp;|&nbsp; "
        f"<strong>Técnicas integradas:</strong> ANOVA + Prueba T + K-Means (k={params['k']}) + Random Forest (Hit &ge; {params['umbral_hit']})"
        f"</div>"
    )
    st.markdown(strip_html, unsafe_allow_html=True)

    col_hero, col_kpis = st.columns([3.2, 1.8], gap="medium")

    with col_hero:
        hero_html = (
            f"<div class='hero-card'>"
            f"<div class='hero-title'>Contracción del Tiempo (-{red_pct:.1f}%) y el &ldquo;Efecto Relleno&rdquo; en Artistas Famosos</div>"
            f"<div class='hero-motivo'>"
            f"La duración de las canciones cayó de <strong>{ev['duracion_2000']:.2f} min</strong> en los años 2000 a "
            f"<strong>{ev['duracion_2020']:.2f} min</strong> en los 2020 para adaptarse al algoritmo de streaming. Sin embargo, "
            f"ser una superestrella no garantiza el éxito: el agrupamiento K-Means descubre <strong>{n_relleno:,} canciones de relleno "
            f"(Clúster {c_relleno})</strong> de artistas muy famosos (popularidad media de <strong>{pop_art_relleno:.1f}</strong>) "
            f"que por extenderse a <strong>{dur_relleno:.2f} min</strong> se desploman a <strong>{pop_trk_relleno:.1f} puntos</strong> de popularidad."
            f"</div>"
            f"<div class='hero-specs'>"
            f"<div class='hero-spec-item'>"
            f"<span class='hero-spec-label'>Clúster {c_main} (Éxitos Mainstream):</span> "
            f"{n_main:,} pistas &middot; {dur_main:.2f} min &middot; {pop_trk_main:.1f} pts de popularidad"
            f"</div>"
            f"<div class='hero-spec-item'>"
            f"<span class='hero-spec-label'>Top 3 Variables de un Hit (RF):</span> "
            f"Seguidores (24.3%), Duración (19.4%) y Popularidad del Artista (18.6%)"
            f"</div>"
            f"</div>"
            f"</div>"
        )
        st.markdown(hero_html, unsafe_allow_html=True)

    with col_kpis:
        k1, k2 = st.columns(2)
        with k1:
            st.markdown(
                (
                    f"<div class='hero-kpi-box'>"
                    f"<div class='hero-kpi-label'>Contracción 2000s &rarr; 2020s</div>"
                    f"<div class='hero-kpi-val'>-{red_pct:.1f}%</div>"
                    f"<div class='hero-kpi-sub'>ANOVA F = {ev['anova_f']:.2f} (p = {ev['anova_p']:.2e})</div>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                (
                    f"<div class='hero-kpi-box'>"
                    f"<div class='hero-kpi-label'>Clúster Efecto Relleno</div>"
                    f"<div class='hero-kpi-val'>{n_relleno:,} pistas</div>"
                    f"<div class='hero-kpi-sub'>Duración {dur_relleno:.2f} min | Pop. {pop_trk_relleno:.1f}</div>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                (
                    f"<div class='hero-kpi-box'>"
                    f"<div class='hero-kpi-label'>Premio Contenido Explícito</div>"
                    f"<div class='hero-kpi-val'>+{dif_exp:.2f} pts</div>"
                    f"<div class='hero-kpi-sub'>Prueba T t = {ev['ttest_t']:.2f} (p = {ev['ttest_p']:.2e})</div>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                (
                    f"<div class='hero-kpi-box'>"
                    f"<div class='hero-kpi-label'>Predicción de Hit (RF)</div>"
                    f"<div class='hero-kpi-val'>{rf['roc_auc'] * 100:.1f}% AUC</div>"
                    f"<div class='hero-kpi-sub'>Exactitud (Accuracy): {rf['accuracy'] * 100:.1f}%</div>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )


def render_tab_estadistica(res: dict) -> None:
    ev: dict = res["evidencia"]
    df_f: pd.DataFrame = res["df_filtrado"]
    tabla_dec: pd.DataFrame = ev["tabla_decadas"]

    st.subheader("1. Contracción del Tiempo de Reproducción por Década (Prueba ANOVA)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Duración Media (Década 2000)", f"{ev['duracion_2000']:.2f} min")
    m2.metric(
        "Duración Media (Década 2010)",
        f"{ev['duracion_2010']:.2f} min",
        delta=f"{((ev['duracion_2010'] - ev['duracion_2000']) / ev['duracion_2000']) * 100:.1f}% vs 2000s",
        delta_color="off",
    )
    m3.metric(
        "Duración Media (Década 2020)",
        f"{ev['duracion_2020']:.2f} min",
        delta=f"-{ev['reduccion_pct'] * 100:.1f}% vs 2000s",
        delta_color="inverse",
    )
    m4.metric(
        "Prueba ANOVA (F / Valor p)",
        f"F = {ev['anova_f']:.2f}",
        delta=f"p = {ev['anova_p']:.2e}",
        delta_color="normal",
    )

    render_nota_interna(
        "Evidencia de contracción algorítmica",
        (
            f"Las canciones lanzadas en los años 2000 duraban en promedio {ev['duracion_2000']:.2f} minutos, "
            f"bajaron a {ev['duracion_2010']:.2f} minutos en los 2010 y cayeron a {ev['duracion_2020']:.2f} minutos "
            f"en la década de 2020 (una reducción del {ev['reduccion_pct'] * 100:.1f}%, con F = {ev['anova_f']:.2f} "
            f"y p = {ev['anova_p']:.2e})."
        ),
    )

    df_3dec = tabla_dec[tabla_dec["decade"].isin([2000, 2010, 2020])].copy()
    col_bar_dur, col_box_dur = st.columns([2.5, 2.5], gap="large")

    with col_bar_dur:
        colores_dec = [
            PALETA["acento"] if d == 2020 else PALETA["primario"]
            for d in df_3dec["decade"]
        ]
        fig_dur = go.Figure(
            go.Bar(
                x=df_3dec["decada_etiqueta"],
                y=df_3dec["duracion_media"],
                marker_color=colores_dec,
                text=[f"{v:.2f} min" for v in df_3dec["duracion_media"]],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>Década %{x}</b><br>"
                    "Duración promedio: %{y:.2f} min<extra></extra>"
                ),
            )
        )
        fig_dur.update_layout(
            title="Duración Promedio por Década (2000s - 2020s)",
            xaxis=dict(title="Década de Lanzamiento", automargin=True),
            yaxis=dict(
                title="Duración Media (minutos)",
                range=[0, max(4.3, float(df_3dec["duracion_media"].max()) * 1.18)],
                automargin=True,
            ),
            height=380,
            margin=dict(l=55, r=25, t=55, b=50),
        )
        st.plotly_chart(fig_dur, width="stretch", theme=None)

    with col_box_dur:
        df_box = df_f[
            df_f["decade"].isin([2000, 2010, 2020]) & (df_f["duration_min"] <= 8.0)
        ].copy()
        df_box["decada_str"] = df_box["decade"].map(lambda d: f"{int(d)}s")
        fig_box = px.box(
            df_box,
            x="decada_str",
            y="duration_min",
            color="decada_str",
            category_orders={"decada_str": ["2000s", "2010s", "2020s"]},
            color_discrete_map={
                "2000s": PALETA["primario"],
                "2010s": PALETA["secundario"],
                "2020s": PALETA["acento"],
            },
            points=False,
            title="Distribución y Cuartiles de Duración (Pistas <= 8 min)",
        )
        fig_box.update_layout(
            xaxis=dict(title="Década de Lanzamiento", automargin=True),
            yaxis=dict(title="Duración (minutos)", automargin=True),
            showlegend=False,
            height=380,
            margin=dict(l=55, r=25, t=55, b=50),
        )
        st.plotly_chart(fig_box, width="stretch", theme=None)

    st.divider()
    st.subheader("2. El Premio al Contenido Explícito (Prueba T de Student)")

    t1, t2, t3, t4 = st.columns(4)
    t1.metric(
        "Popularidad Media (Explicit = True)",
        f"{ev['pop_explicito']:.2f} pts",
        delta=f"+{ev['diferencia_pop_explicito']:.2f} pts vs Limpias",
    )
    t2.metric(
        "Popularidad Media (Explicit = False)",
        f"{ev['pop_limpio']:.2f} pts",
    )
    t3.metric(
        "Expansión de Catálogo Explícito",
        f"{ev['pct_exp_2020'] * 100:.1f}% en 2020s",
        delta=f"Desde {ev['pct_exp_2000'] * 100:.1f}% en 2000s",
    )
    t4.metric(
        "Prueba T de Student (t / Valor p)",
        f"t = {ev['ttest_t']:.2f}",
        delta=f"p = {ev['ttest_p']:.2e}",
    )

    render_nota_interna(
        "Ventaja competitiva del corte explícito",
        (
            f"Las canciones marcadas como Explicit alcanzan una popularidad promedio de {ev['pop_explicito']:.2f} "
            f"frente a {ev['pop_limpio']:.2f} de las pistas limpias (t = {ev['ttest_t']:.2f}, p = {ev['ttest_p']:.2e}), "
            f"duplicando su cuota de mercado del {ev['pct_exp_2000'] * 100:.1f}% en los años 2000 al "
            f"{ev['pct_exp_2020'] * 100:.1f}% en la década de 2020."
        ),
    )

    col_exp_pop, col_exp_evol = st.columns([2.4, 2.6], gap="large")

    with col_exp_pop:
        df_exp_bar = pd.DataFrame(
            {
                "tipo": ["Limpia (Clean)", "Explícita (Explicit)"],
                "popularidad": [ev["pop_limpio"], ev["pop_explicito"]],
                "conteo": [ev["n_limpio"], ev["n_explicito"]],
                "color": [PALETA["gris"], PALETA["acento"]],
            }
        )
        fig_exp = go.Figure(
            go.Bar(
                x=df_exp_bar["tipo"],
                y=df_exp_bar["popularidad"],
                marker_color=df_exp_bar["color"],
                text=[
                    f"{pop:.2f} pts (n={cnt:,})"
                    for pop, cnt in zip(df_exp_bar["popularidad"], df_exp_bar["conteo"])
                ],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_exp.update_layout(
            title="Popularidad Promedio según Clasificación Lírica",
            xaxis=dict(title="", automargin=True),
            yaxis=dict(title="Popularidad Promedio (0-100)", range=[0, 72], automargin=True),
            height=370,
            margin=dict(l=55, r=25, t=55, b=45),
        )
        st.plotly_chart(fig_exp, width="stretch", theme=None)

    with col_exp_evol:
        fig_evol = go.Figure(
            go.Bar(
                x=df_3dec["decada_etiqueta"],
                y=df_3dec["pct_explicito"],
                marker_color=[PALETA["gris"], PALETA["primario"], PALETA["acento"]],
                text=[f"{v * 100:.1f}%" for v in df_3dec["pct_explicito"]],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_evol.update_layout(
            title="Proporción de Canciones Explícitas por Década",
            xaxis=dict(title="Década de Lanzamiento", automargin=True),
            yaxis=dict(
                title="% de Canciones Explícitas",
                tickformat=".0%",
                range=[0, max(0.38, float(df_3dec["pct_explicito"].max()) * 1.25)],
                automargin=True,
            ),
            height=370,
            margin=dict(l=55, r=25, t=55, b=45),
        )
        st.plotly_chart(fig_evol, width="stretch", theme=None)


def render_tab_clustering(params: dict, res: dict) -> None:
    cl: dict = res["clustering"]
    base: pd.DataFrame = cl["base"]
    perfil_df: pd.DataFrame = cl["perfil"]
    indices_df: pd.DataFrame = cl["indices"]
    nombres: pd.DataFrame = cl["nombres"]
    media_global: pd.Series = cl["media_global"]

    c_relleno = int(cl["cluster_relleno"])
    c_main = int(cl["cluster_mainstream"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pistas Segmentadas", f"{len(base):,}")
    c2.metric(
        "Clústeres Activos (k)",
        f"{params['k']}",
        delta="Óptimo del estudio" if params["k"] == 4 else "Exploración",
        delta_color="normal" if params["k"] == 4 else "off",
    )
    c3.metric("Coeficiente de Silueta", f"{cl['silueta']:.4f}")
    c4.metric(
        f"Clúster {c_relleno}: Efecto Relleno",
        f"{int(perfil_df.loc[c_relleno, 'canciones']):,} pistas",
        delta=f"Pop. {perfil_df.loc[c_relleno, 'track_popularity']:.1f} vs Artista {perfil_df.loc[c_relleno, 'artist_popularity']:.1f}",
        delta_color="inverse",
    )

    render_nota_interna(
        "La Paradoja del Efecto Relleno (Clúster 2 vs. Clúster 0)",
        (
            f"El Clúster {c_relleno} ({nombres.loc[c_relleno, 'nombre']}, {int(perfil_df.loc[c_relleno, 'canciones']):,} canciones) "
            f"agrupa a superestrellas con popularidad de artista de {perfil_df.loc[c_relleno, 'artist_popularity']:.1f}, "
            f"pero cuyas canciones tienen una duración excesiva ({perfil_df.loc[c_relleno, 'duration_min']:.2f} min) y caen "
            f"a {perfil_df.loc[c_relleno, 'track_popularity']:.1f} puntos de popularidad. En contraste, el Clúster {c_main} "
            f"({nombres.loc[c_main, 'nombre']}, {int(perfil_df.loc[c_main, 'canciones']):,} canciones) mantiene {perfil_df.loc[c_main, 'duration_min']:.2f} min "
            f"y alcanza {perfil_df.loc[c_main, 'track_popularity']:.1f} puntos de popularidad."
        ),
        resaltar=True,
    )

    etiquetas_leyenda = {
        s: f"C{s}: {nombres.loc[s, 'nombre']}"
        for s in nombres.index
    }
    mapa_colores = {
        etiquetas_leyenda[s]: (
            PALETA["acento"]
            if int(s) == c_relleno
            else (PALETA["primario"] if int(s) == c_main else color_segmento(int(s) + 2))
        )
        for s in nombres.index
    }
    orden_leyenda = [etiquetas_leyenda[s] for s in nombres.index]

    col_pca, col_vol = st.columns([2.9, 2.1], gap="large")

    with col_pca:
        coords = cl["coords_2d"]
        df_plot = pd.DataFrame(
            {
                "pca_1": coords[:, 0],
                "pca_2": coords[:, 1],
                "cluster": cl["etiquetas"],
                "track_name": base["track_name"].values,
                "artist_name": base["artist_name"].values,
                "track_popularity": base["track_popularity"].values,
                "duration_min": base["duration_min"].values,
                "artist_popularity": base["artist_popularity"].values,
            }
        )
        df_plot["etiqueta_cluster"] = df_plot["cluster"].map(etiquetas_leyenda)

        fig_pca = px.scatter(
            df_plot,
            x="pca_1",
            y="pca_2",
            color="etiqueta_cluster",
            color_discrete_map=mapa_colores,
            category_orders={"etiqueta_cluster": orden_leyenda},
            custom_data=[
                "etiqueta_cluster",
                "track_name",
                "artist_name",
                "track_popularity",
                "duration_min",
                "artist_popularity",
            ],
            render_mode="webgl",
            title="Proyección Bidimensional de Canciones (PCA 2D)",
        )
        fig_pca.update_traces(
            marker=dict(size=5, opacity=0.72),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Canción: %{customdata[1]}<br>"
                "Artista: %{customdata[2]}<br>"
                "Popularidad pista: %{customdata[3]:.0f} pts<br>"
                "Duración: %{customdata[4]:.2f} min<br>"
                "Popularidad artista: %{customdata[5]:.0f} pts<extra></extra>"
            ),
        )
        fig_pca.update_layout(
            xaxis=dict(title="Componente Principal 1", automargin=True),
            yaxis=dict(title="Componente Principal 2", automargin=True),
            legend_title_text="",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="left",
                x=0,
                font=dict(size=12),
            ),
            height=480,
            margin=dict(l=55, r=20, t=55, b=115),
        )
        st.plotly_chart(fig_pca, width="stretch", theme=None)

    with col_vol:
        df_tam = pd.DataFrame(
            {
                "cluster": perfil_df.index,
                "etiqueta_cluster": [etiquetas_leyenda[s] for s in perfil_df.index],
                "canciones": perfil_df["canciones"].values,
                "pct": perfil_df["pct_canciones"].values,
                "color": [mapa_colores[etiquetas_leyenda[s]] for s in perfil_df.index],
            }
        ).sort_values("pct", ascending=True)

        max_pct = float(df_tam["pct"].max()) if not df_tam.empty else 0.6
        fig_bar = go.Figure(
            go.Bar(
                x=df_tam["pct"],
                y=df_tam["etiqueta_cluster"],
                orientation="h",
                marker_color=df_tam["color"],
                text=[
                    f"{p * 100:.1f}% ({int(n):,})"
                    for p, n in zip(df_tam["pct"], df_tam["canciones"])
                ],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_bar.update_layout(
            title="Distribución de Volumen por Clúster",
            xaxis=dict(
                title="% del Catálogo",
                tickformat=".0%",
                range=[0, max_pct * 1.32],
                showgrid=True,
                automargin=True,
            ),
            yaxis=dict(title="", showgrid=False, automargin=True),
            height=290,
            margin=dict(l=20, r=55, t=50, b=40),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, width="stretch", theme=None)

        st.markdown("**Diagnóstico de Negocio por Clúster**")
        for s in nombres.index:
            borde = (
                PALETA["acento"]
                if int(s) == c_relleno
                else (PALETA["primario"] if int(s) == c_main else PALETA["gris"])
            )
            st.markdown(
                (
                    f"<div style='border-left: 4px solid {borde}; padding-left: 10px; margin-bottom: 8px;'>"
                    f"<strong style='color:{PALETA['texto']};'>Clúster {s} &middot; {nombres.loc[s, 'nombre']}</strong><br/>"
                    f"<span style='color:{PALETA['gris']}; font-size:0.84rem;'>{nombres.loc[s, 'diagnostico']}</span>"
                    f"</div>"
                ),
                unsafe_allow_html=True,
            )

    st.divider()
    col_hdr, col_toggle = st.columns([3.0, 1.5])
    with col_hdr:
        st.subheader("Perfil Cuantitativo por Clúster")
    with col_toggle:
        modo_indice = st.toggle(
            "Ver como índice relativo al promedio (1.00x)",
            value=False,
            key="cl_toggle_indice",
        )

    filas_tabla = []
    for seg in perfil_df.index:
        fila = {
            "Clúster": f"Clúster {seg}",
            "Arquetipo": nombres.loc[seg, "nombre"],
            "Canciones": f"{int(perfil_df.loc[seg, 'canciones']):,}",
            "% Catálogo": f"{perfil_df.loc[seg, 'pct_canciones'] * 100:.1f}%",
        }
        for var in COLUMNAS_PERFIL:
            nom_col = ETIQUETAS_VARIABLES[var]
            if modo_indice:
                fila[nom_col] = f"{indices_df.loc[seg, var]:.2f}x"
            else:
                fila[nom_col] = formatear_valor_perfil(var, perfil_df.loc[seg, var])
        filas_tabla.append(fila)

    fila_total = {
        "Clúster": "Total",
        "Arquetipo": "Promedio general del catálogo",
        "Canciones": f"{int(perfil_df['canciones'].sum()):,}",
        "% Catálogo": "100.0%",
    }
    for var in COLUMNAS_PERFIL:
        nom_col = ETIQUETAS_VARIABLES[var]
        fila_total[nom_col] = (
            "1.00x" if modo_indice else formatear_valor_perfil(var, media_global[var])
        )
    filas_tabla.append(fila_total)

    st.dataframe(pd.DataFrame(filas_tabla), hide_index=True, width="stretch")

    etiquetas_filas = [etiquetas_leyenda[s] for s in perfil_df.index]
    etiquetas_cols = [
        envolver_etiqueta_eje(ETIQUETAS_VARIABLES[v], ancho=16) for v in COLUMNAS_PERFIL
    ]
    matriz_idx = indices_df[COLUMNAS_PERFIL].to_numpy(dtype=float)
    matriz_z = np.clip(matriz_idx, 0.0, 2.5)
    texto_celdas = np.vectorize(lambda x: f"{x:.2f}x")(matriz_idx)

    fig_heat = go.Figure(
        data=go.Heatmap(
            z=matriz_z,
            x=etiquetas_cols,
            y=etiquetas_filas,
            text=texto_celdas,
            texttemplate="%{text}",
            colorscale=SECUENCIAL,
            colorbar=dict(title="Índice (x)"),
            hovertemplate="<b>%{y}</b><br>Variable: %{x}<br>Índice relativo: %{text}<extra></extra>",
        )
    )
    fig_heat.update_layout(
        title="Matriz de Índices Relativos respecto al Promedio del Catálogo (1.00x = Media)",
        xaxis=dict(title="", tickangle=0, automargin=True),
        yaxis=dict(title="", automargin=True),
        height=max(310, 58 * len(etiquetas_filas) + 110),
        margin=dict(l=20, r=20, t=55, b=55),
    )
    st.plotly_chart(fig_heat, width="stretch", theme=None)


def render_tab_clasificacion(res: dict) -> None:
    rf: dict = res["clasificacion"]
    imp_df: pd.DataFrame = rf["importancias"]

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Precisión del Modelo (Accuracy)", f"{rf['accuracy'] * 100:.1f}%")
    r2.metric("Área Bajo la Curva (ROC-AUC)", f"{rf['roc_auc'] * 100:.1f}%")
    r3.metric(
        f"Proporción de Hits (>= {rf['umbral_hit']} pts)",
        f"{rf['tasa_hits'] * 100:.1f}%",
    )
    top1_nom = str(imp_df.loc[0, "etiqueta"])
    top1_val = float(imp_df.loc[0, "importancia_pct"])
    r4.metric("Factor #1 Determinante", f"{top1_val:.1f}%", delta=top1_nom)

    render_nota_interna(
        "Poder predictivo y jerarquía de variables (Random Forest)",
        (
            f"Al predecir si una canción será un Hit (popularidad >= {rf['umbral_hit']}), el modelo Random Forest "
            f"alcanza una precisión (Accuracy) del {rf['accuracy'] * 100:.1f}% y un ROC-AUC del {rf['roc_auc'] * 100:.1f}%. "
            f"Las 3 variables más determinantes son el número de seguidores del artista (24.3%), la duración de la canción (19.4%) "
            f"y la popularidad del artista (18.6%)."
        ),
    )

    col_imp, col_roc = st.columns([2.7, 2.3], gap="large")

    with col_imp:
        df_imp_plot = imp_df.sort_values("importancia_pct", ascending=True).copy()
        colores_imp = [
            PALETA["primario"] if i >= len(df_imp_plot) - 3 else PALETA["gris"]
            for i in range(len(df_imp_plot))
        ]
        max_imp = float(df_imp_plot["importancia_pct"].max())
        fig_imp = go.Figure(
            go.Bar(
                x=df_imp_plot["importancia_pct"],
                y=df_imp_plot["etiqueta"],
                orientation="h",
                marker_color=colores_imp,
                text=[f"{v:.1f}%" for v in df_imp_plot["importancia_pct"]],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_imp.update_layout(
            title="Importancia Relativa de Variables en la Predicción de un Hit",
            xaxis=dict(
                title="Importancia en el Modelo (%)",
                range=[0, max_imp * 1.25],
                showgrid=True,
                automargin=True,
            ),
            yaxis=dict(title="", showgrid=False, automargin=True),
            height=410,
            margin=dict(l=20, r=55, t=55, b=45),
        )
        st.plotly_chart(fig_imp, width="stretch", theme=None)

    with col_roc:
        fig_roc = go.Figure()
        fig_roc.add_trace(
            go.Scatter(
                x=rf["fpr"],
                y=rf["tpr"],
                mode="lines",
                name=f"Random Forest (AUC = {rf['roc_auc'] * 100:.1f}%)",
                line=dict(color=PALETA["primario"], width=3),
            )
        )
        fig_roc.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="Azar (AUC = 50.0%)",
                line=dict(color=PALETA["gris"], width=1.5, dash="dash"),
            )
        )
        fig_roc.update_layout(
            title="Curva ROC del Clasificador de Hits",
            xaxis=dict(title="Tasa de Falsos Positivos (FPR)", range=[0, 1], automargin=True),
            yaxis=dict(title="Tasa de Verdaderos Positivos (TPR)", range=[0, 1.02], automargin=True),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
            ),
            height=410,
            margin=dict(l=55, r=25, t=75, b=45),
        )
        st.plotly_chart(fig_roc, width="stretch", theme=None)

    st.divider()
    st.subheader("Simulador Interactivo: Probabilidad de Hit vs. Riesgo de Efecto Relleno")
    st.caption(
        "Ajusta los parámetros de un lanzamiento para evaluar en tiempo real cómo la duración y el formato afectan la probabilidad de éxito incluso en artistas famosos."
    )

    defaults_sim = {
        "sim_dur": 3.10,
        "sim_pop_art": 85,
        "sim_fol": 35_000_000,
        "sim_tot": 12,
        "sim_trk": 2,
        "sim_anio": 2024,
        "sim_exp": True,
    }
    for k_sim, v_sim in defaults_sim.items():
        if k_sim not in st.session_state:
            st.session_state[k_sim] = v_sim

    b1, b2, _ = st.columns([1.6, 1.8, 2.6])
    with b1:
        if st.button("Cargar Perfil: Sencillo Conciso (Hit)", width="stretch"):
            st.session_state["sim_dur"] = 2.85
            st.session_state["sim_pop_art"] = 88
            st.session_state["sim_fol"] = 45_000_000
            st.session_state["sim_tot"] = 1
            st.session_state["sim_trk"] = 1
            st.session_state["sim_anio"] = 2024
            st.session_state["sim_exp"] = True
    with b2:
        if st.button("Cargar Perfil: Pista de Relleno (Deep Cut)", width="stretch"):
            st.session_state["sim_dur"] = 4.35
            st.session_state["sim_pop_art"] = 72
            st.session_state["sim_fol"] = 18_000_000
            st.session_state["sim_tot"] = 16
            st.session_state["sim_trk"] = 12
            st.session_state["sim_anio"] = 2016
            st.session_state["sim_exp"] = False

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        sim_dur = st.slider(
            "Duración de la canción (min)",
            min_value=1.5,
            max_value=6.5,
            step=0.05,
            key="sim_dur",
        )
        sim_exp = st.checkbox(
            "Contenido Explícito (Explicit)",
            key="sim_exp",
        )
    with s2:
        sim_pop_art = st.slider(
            "Popularidad del Artista (0-100)",
            min_value=10,
            max_value=100,
            step=1,
            key="sim_pop_art",
        )
    with s3:
        sim_fol = st.number_input(
            "Seguidores del Artista",
            min_value=1_000,
            max_value=150_000_000,
            step=1_000_000,
            key="sim_fol",
        )
        sim_anio = st.slider(
            "Año de Lanzamiento",
            min_value=2000,
            max_value=2025,
            step=1,
            key="sim_anio",
        )
    with s4:
        sim_tot = st.slider(
            "Total de pistas del álbum",
            min_value=1,
            max_value=40,
            step=1,
            key="sim_tot",
        )
        if int(sim_tot) <= 1:
            st.session_state["sim_trk"] = 1
            st.text_input(
                "Posición de la pista en el álbum",
                value="Pista 1 de 1 (Sencillo)",
                disabled=True,
            )
            sim_trk = 1
        else:
            if int(st.session_state.get("sim_trk", 1)) > int(sim_tot):
                st.session_state["sim_trk"] = int(sim_tot)
            sim_trk = st.slider(
                "Posición de la pista en el álbum",
                min_value=1,
                max_value=int(sim_tot),
                step=1,
                key="sim_trk",
            )

    pred = predecir_hit_simulador(
        modelo=rf["modelo"],
        duracion_min=sim_dur,
        seguidores=sim_fol,
        pop_artista=sim_pop_art,
        num_track=sim_trk,
        explicito=sim_exp,
        total_tracks=sim_tot,
        anio=sim_anio,
    )

    prob_pct = pred["probabilidad_hit"] * 100.0
    if pred["riesgo_relleno"]:
        render_nota_interna(
            f"Probabilidad Estimada de Hit: {prob_pct:.1f}% — Alerta de Efecto Relleno (Clúster 2)",
            (
                f"Aunque el artista tiene alta popularidad ({sim_pop_art} pts), una duración de {sim_dur:.2f} min "
                f"dentro de un álbum de {sim_tot} pistas ubica la canción en el perfil de Efecto Relleno."
            ),
            resaltar=True,
        )
    elif pred["es_hit_estimado"]:
        render_nota_interna(
            f"Probabilidad Estimada de Hit: {prob_pct:.1f}% — Perfil de Éxito Mainstream (Clúster 0)",
            (
                f"La combinación de tracción de audiencia ({sim_fol:,} seguidores) y duración optimizada "
                f"({sim_dur:.2f} min) maximiza la probabilidad de ubicarse en el Top 25% de popularidad."
            ),
            resaltar=False,
        )
    else:
        render_nota_interna(
            f"Probabilidad Estimada de Hit: {prob_pct:.1f}% — Desempeño Moderado / Estándar",
            "La pista presenta una probabilidad inferior al 50% de alcanzar el umbral de Hit (>= 70 puntos).",
            resaltar=False,
        )


def main() -> None:
    inyectar_css()
    params = render_sidebar()

    resultado = ejecutar_estudio(
        decadas_sel=params["decadas"],
        tipos_sel=params["tipos"],
        k=params["k"],
        umbral_hit=params["umbral_hit"],
    )

    if not resultado.get("ok"):
        render_nota_interna(
            "Subconjunto sin registros suficientes",
            resultado.get("mensaje", "Ajusta los filtros de la barra lateral."),
            resaltar=True,
        )
        return

    render_hero(params, resultado)

    tab_est, tab_clust, tab_rf = st.tabs(
        [
            "1. Economía de la Atención (ANOVA y Prueba T)",
            "2. Segmentación K-Means (Efecto Relleno y PCA)",
            "3. Fórmula de un Hit (Random Forest)",
        ]
    )

    with tab_est:
        render_tab_estadistica(resultado)

    with tab_clust:
        render_tab_clustering(params, resultado)

    with tab_rf:
        render_tab_clasificacion(resultado)


if __name__ == "__main__":
    main()
