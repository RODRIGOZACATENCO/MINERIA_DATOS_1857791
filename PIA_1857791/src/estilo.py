from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

PALETA = {
    "primario": "#0F6E78",
    "secundario": "#2A9D8F",
    "acento": "#E76F51",
    "texto": "#1F2933",
    "gris": "#6B7280",
    "gris_claro": "#E5E7EB",
    "fondo": "#FFFFFF",
    "fondo_suave": "#F3F7F7",
}

COLORES_SEGMENTOS = [
    "#0F6E78",
    "#E76F51",
    "#E9C46A",
    "#264653",
    "#8AB17D",
    "#9C6ADE",
    "#F4A261",
    "#5DA9E9",
]

COLORES_ESTADO = {
    "activo": PALETA["primario"],
    "en_fuga": PALETA["acento"],
    "inactivo": PALETA["gris"],
}

SECUENCIAL = ["#F3F7F7", "#BFE3E0", "#7CC4BE", "#2A9D8F", "#0F6E78", "#0A4A51"]
DIVERGENTE = ["#E76F51", "#F4B9A6", "#F3F7F7", "#7CC4BE", "#0F6E78"]

FUENTES = ["Open Sans", "Segoe UI", "Arial", "DejaVu Sans"]

TAMANO_DIAPOSITIVA = (12, 6.75)
TAMANO_APP = (8, 4.5)

CARPETA_FIGURAS = Path(__file__).resolve().parent.parent / "reports" / "figuras"


def color_segmento(i: int) -> str:
    return COLORES_SEGMENTOS[int(i) % len(COLORES_SEGMENTOS)]


def colores_segmentos(k: int) -> list[str]:
    return [color_segmento(i) for i in range(k)]


def formato_pesos(x: float) -> str:
    return f"${x:,.0f}"


def formato_pct(x: float, decimales: int = 0) -> str:
    return f"{x * 100:.{decimales}f}%"


def eje_pesos(ax, eje: str = "y") -> None:
    _eje(ax, eje).set_major_formatter(FuncFormatter(lambda v, _: formato_pesos(v)))


def eje_pct(ax, eje: str = "y", decimales: int = 0) -> None:
    _eje(ax, eje).set_major_formatter(
        FuncFormatter(lambda v, _: formato_pct(v, decimales))
    )


def _eje(ax, eje: str):
    return ax.yaxis if eje == "y" else ax.xaxis


def mapa_secuencial():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("farmacia_seq", SECUENCIAL)


def mapa_divergente():
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("farmacia_div", DIVERGENTE)


def estilo_matplotlib() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": FUENTES,
        "font.size": 12,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 12,
        "axes.labelcolor": PALETA["texto"],
        "axes.edgecolor": PALETA["gris_claro"],
        "axes.facecolor": PALETA["fondo"],
        "axes.prop_cycle": mpl.cycler(color=COLORES_SEGMENTOS),
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": PALETA["gris_claro"],
        "grid.linewidth": 0.8,
        "xtick.color": PALETA["gris"],
        "ytick.color": PALETA["gris"],
        "text.color": PALETA["texto"],
        "legend.frameon": False,
        "figure.facecolor": PALETA["fondo"],
        "figure.figsize": TAMANO_DIAPOSITIVA,
        "figure.dpi": 100,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
    })


def guardar_figura(
    fig,
    nombre: str,
    carpeta: Path | None = None,
    sin_titulo: bool = False,
) -> Path:
    carpeta = carpeta or CARPETA_FIGURAS
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.png"
    if not sin_titulo:
        fig.savefig(ruta, facecolor=PALETA["fondo"])
        return ruta

    titulos = [(ax, ax.get_title(loc="left")) for ax in fig.axes]
    suptitulo = fig._suptitle.get_text() if fig._suptitle else None
    for ax, _ in titulos:
        ax.set_title("", loc="left")
    if suptitulo:
        fig.suptitle("")
    fig.savefig(ruta, facecolor=PALETA["fondo"])
    for ax, t in titulos:
        ax.set_title(t, loc="left")
    if suptitulo:
        fig.suptitle(suptitulo, x=0.01, ha="left", fontsize=16, fontweight="bold")
    return ruta


NOMBRE_PLANTILLA_PLOTLY = "farmacia"


def plantilla_plotly():
    import plotly.graph_objects as go
    import plotly.io as pio

    plantilla = go.layout.Template(
        layout=dict(
            font=dict(family=", ".join(FUENTES), size=14, color=PALETA["texto"]),
            title=dict(font=dict(size=20), x=0, xanchor="left"),
            colorway=COLORES_SEGMENTOS,
            colorscale=dict(sequential=SECUENCIAL, diverging=DIVERGENTE),
            paper_bgcolor=PALETA["fondo"],
            plot_bgcolor=PALETA["fondo"],
            xaxis=dict(
                showgrid=False,
                linecolor=PALETA["gris_claro"],
                tickcolor=PALETA["gris"],
                zeroline=False,
            ),
            yaxis=dict(
                gridcolor=PALETA["gris_claro"],
                linecolor=PALETA["gris_claro"],
                zeroline=False,
            ),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=40, r=20, t=60, b=40),
            hoverlabel=dict(font=dict(family=", ".join(FUENTES))),
        )
    )
    pio.templates[NOMBRE_PLANTILLA_PLOTLY] = plantilla
    return plantilla


def aplicar_estilo(plotly: bool = True) -> None:
    estilo_matplotlib()
    if plotly:
        import plotly.io as pio
        plantilla_plotly()
        pio.templates.default = NOMBRE_PLANTILLA_PLOTLY
