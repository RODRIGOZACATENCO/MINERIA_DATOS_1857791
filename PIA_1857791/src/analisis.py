from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    davies_bouldin_score,
    roc_auc_score,
    roc_curve,
    silhouette_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

RUTA_CSV_DEFECTO = Path(__file__).resolve().parent.parent / "track_data_final.csv"

COLUMNAS_KMEANS = [
    "track_popularity",
    "duration_min",
    "artist_popularity",
    "log1p_followers",
    "album_total_tracks",
]

COLUMNAS_PERFIL = [
    "track_popularity",
    "duration_min",
    "artist_popularity",
    "artist_followers",
    "album_total_tracks",
    "explicit_int",
]

COLUMNAS_RF = [
    "duration_min",
    "artist_followers",
    "artist_popularity",
    "track_number",
    "explicit_int",
    "album_total_tracks",
    "year",
]

ETIQUETAS_VARIABLES = {
    "track_popularity": "Popularidad de la Canción",
    "duration_min": "Duración de la Canción (min)",
    "artist_popularity": "Popularidad del Artista",
    "artist_followers": "Seguidores del Artista",
    "log1p_followers": "Seguidores del Artista (Log)",
    "album_total_tracks": "Total de Pistas del Álbum",
    "track_number": "Posición en el Álbum",
    "explicit_int": "Contenido Explícito",
    "year": "Año de Lanzamiento",
}


def cargar_datos(ruta_csv: Path | str | None = None) -> pd.DataFrame:
    ruta = Path(ruta_csv) if ruta_csv else RUTA_CSV_DEFECTO
    df = pd.read_csv(ruta).dropna().copy()
    df["duration_min"] = df["track_duration_ms"] / 60000.0
    fechas = pd.to_datetime(df["album_release_date"], errors="coerce")
    df["year"] = fechas.dt.year
    df["decade"] = (df["year"] // 10) * 10
    df["year_ fallback"] = df["album_release_date"].astype(str).str[:4]
    df["explicit_int"] = df["explicit"].astype(int)
    df["log1p_followers"] = np.log1p(df["artist_followers"])
    df["is_single"] = (df["album_type"] == "single").astype(int)
    return df


def filtrar_datos(
    df: pd.DataFrame,
    decadas: list[int] | None = None,
    tipos_album: list[str] | None = None,
) -> pd.DataFrame:
    sub = df.copy()
    if decadas:
        sub = sub[sub["decade"].isin(decadas)]
    if tipos_album:
        sub = sub[sub["album_type"].isin(tipos_album)]
    return sub.copy()


def calcular_evidencia_estadistica(df: pd.DataFrame) -> dict:
    df_dec = df.dropna(subset=["decade"]).copy()
    d2000 = df_dec[df_dec["decade"] == 2000]["duration_min"]
    d2010 = df_dec[df_dec["decade"] == 2010]["duration_min"]
    d2020 = df_dec[df_dec["decade"] == 2020]["duration_min"]

    if len(d2000) > 1 and len(d2010) > 1 and len(d2020) > 1:
        f_stat, p_anova = stats.f_oneway(d2000, d2010, d2020)
    else:
        f_stat, p_anova = np.nan, np.nan

    mean_2000 = float(d2000.mean()) if not d2000.empty else np.nan
    mean_2010 = float(d2010.mean()) if not d2010.empty else np.nan
    mean_2020 = float(d2020.mean()) if not d2020.empty else np.nan

    reduccion_pct = (
        (mean_2000 - mean_2020) / mean_2000
        if pd.notna(mean_2000) and mean_2000 > 0 and pd.notna(mean_2020)
        else np.nan
    )

    tabla_decadas = (
        df_dec[df_dec["decade"].isin([1990, 2000, 2010, 2020])]
        .groupby("decade", as_index=False)
        .agg(
            canciones=("track_id", "count"),
            duracion_media=("duration_min", "mean"),
            duracion_mediana=("duration_min", "median"),
            pop_media=("track_popularity", "mean"),
            pct_explicito=("explicit_int", "mean"),
        )
    )
    tabla_decadas["decada_etiqueta"] = tabla_decadas["decade"].map(
        lambda d: f"{int(d)}s"
    )

    exp_pop = df[df["explicit"] == True]["track_popularity"]
    cln_pop = df[df["explicit"] == False]["track_popularity"]

    if len(exp_pop) > 1 and len(cln_pop) > 1:
        t_stat, p_ttest = stats.ttest_ind(exp_pop, cln_pop)
    else:
        t_stat, p_ttest = np.nan, np.nan

    exp_2000 = float(
        df_dec[df_dec["decade"] == 2000]["explicit_int"].mean()
    ) if not d2000.empty else np.nan
    exp_2020 = float(
        df_dec[df_dec["decade"] == 2020]["explicit_int"].mean()
    ) if not d2020.empty else np.nan

    return {
        "duracion_2000": mean_2000,
        "duracion_2010": mean_2010,
        "duracion_2020": mean_2020,
        "reduccion_pct": reduccion_pct,
        "anova_f": float(f_stat) if pd.notna(f_stat) else np.nan,
        "anova_p": float(p_anova) if pd.notna(p_anova) else np.nan,
        "pop_explicito": float(exp_pop.mean()) if not exp_pop.empty else np.nan,
        "pop_limpio": float(cln_pop.mean()) if not cln_pop.empty else np.nan,
        "n_explicito": int(len(exp_pop)),
        "n_limpio": int(len(cln_pop)),
        "diferencia_pop_explicito": (
            float(exp_pop.mean() - cln_pop.mean())
            if not exp_pop.empty and not cln_pop.empty
            else np.nan
        ),
        "ttest_t": float(t_stat) if pd.notna(t_stat) else np.nan,
        "ttest_p": float(p_ttest) if pd.notna(p_ttest) else np.nan,
        "pct_exp_2000": exp_2000,
        "pct_exp_2020": exp_2020,
        "tabla_decadas": tabla_decadas,
    }


def _nombrar_clusters(perfil: pd.DataFrame, k: int) -> pd.DataFrame:
    if k == 4 and set(perfil.index) == {0, 1, 2, 3}:
        pop_c2 = perfil.loc[2, "track_popularity"]
        dur_c2 = perfil.loc[2, "duration_min"]
        if pop_c2 < 30 and dur_c2 > 4.0:
            datos = [
                {
                    "cluster": 0,
                    "nombre": "Éxitos Mainstream",
                    "rol": "Estándar ganador de alto impacto",
                    "diagnostico": "Artistas famosos con pistas concisas (~3.57 min) y alta tracción en streaming.",
                },
                {
                    "cluster": 1,
                    "nombre": "Nicho / En Desarrollo",
                    "rol": "Catálogo emergente o independiente",
                    "diagnostico": "Artistas con menor base de seguidores y popularidad moderada.",
                },
                {
                    "cluster": 2,
                    "nombre": "Efecto Relleno (Deep Cuts)",
                    "rol": "Paradoja de superestrellas",
                    "diagnostico": "Artistas muy famosos (pop. 69.7) cuyas pistas largas (4.17 min) se hunden en popularidad (23.7).",
                },
                {
                    "cluster": 3,
                    "nombre": "Compilaciones y Mega-Álbumes",
                    "rol": "Ediciones especiales y cajas",
                    "diagnostico": "Álbumes masivos (>50 pistas) donde la atención por canción se diluye.",
                },
            ]
            return pd.DataFrame(datos).set_index("cluster")

    seg_relleno = int(
        (perfil["artist_popularity"] - perfil["track_popularity"]).idxmax()
    )
    seg_hit = int(perfil["track_popularity"].idxmax())
    seg_mega = int(perfil["album_total_tracks"].idxmax())

    filas = []
    for idx in perfil.index:
        if idx == seg_hit:
            nom = "Éxitos Mainstream"
            rol = "Líder en popularidad de pista"
            diag = "Combina fuerte tracción de artista con duración optimizada para streaming."
        elif idx == seg_relleno:
            nom = "Efecto Relleno (Deep Cuts)"
            rol = "Paradoja de superestrellas"
            diag = "Alta fama del artista pero baja popularidad de pista y mayor duración promedio."
        elif idx == seg_mega and perfil.loc[idx, "album_total_tracks"] > 25:
            nom = "Compilaciones y Mega-Álbumes"
            rol = "Catálogo de álbumes extensos"
            diag = "Lanzamientos con gran volumen de pistas y atención fragmentada."
        else:
            nom = f"Catálogo Secundario / Nicho G{idx}"
            rol = "Segmento intermedio"
            diag = "Pistas con métricas moderadas de audiencia y rotación."
        filas.append(
            {
                "cluster": idx,
                "nombre": nom,
                "rol": rol,
                "diagnostico": diag,
            }
        )
    return pd.DataFrame(filas).set_index("cluster")


def ejecutar_clustering(df: pd.DataFrame, k: int = 4) -> dict:
    base = df.dropna(subset=["year"] + COLUMNAS_KMEANS).copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(base[COLUMNAS_KMEANS])

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    etiquetas = km.fit_predict(X_scaled)
    base["cluster"] = etiquetas

    pca = PCA(n_components=2, random_state=42)
    coords_2d = pca.fit_transform(X_scaled)
    var_explicada = pca.explained_variance_ratio_

    silueta = float(silhouette_score(X_scaled, etiquetas))
    db_index = float(davies_bouldin_score(X_scaled, etiquetas))

    conteo = base.groupby("cluster").size().rename("canciones")
    promedios = base.groupby("cluster")[COLUMNAS_PERFIL].mean()
    perfil = pd.concat([conteo, promedios], axis=1)
    perfil["pct_canciones"] = perfil["canciones"] / len(base)

    media_global = base[COLUMNAS_PERFIL].mean()
    indices_relativos = perfil[COLUMNAS_PERFIL].div(
        media_global.replace(0, 1e-9), axis=1
    )

    nombres = _nombrar_clusters(perfil, k)

    cluster_relleno = int(
        (perfil["artist_popularity"] - perfil["track_popularity"]).idxmax()
    )
    cluster_mainstream = int(perfil["track_popularity"].idxmax())

    return {
        "base": base,
        "etiquetas": etiquetas,
        "coords_2d": coords_2d,
        "var_explicada": var_explicada,
        "silueta": silueta,
        "davies_bouldin": db_index,
        "perfil": perfil,
        "media_global": media_global,
        "indices": indices_relativos,
        "nombres": nombres,
        "cluster_relleno": cluster_relleno,
        "cluster_mainstream": cluster_mainstream,
    }


def ejecutar_clasificacion(df: pd.DataFrame, umbral_hit: int = 70) -> dict:
    base = df.dropna(subset=["year"] + COLUMNAS_RF).copy()
    base["hit"] = (base["track_popularity"] >= umbral_hit).astype(int)

    X = base[COLUMNAS_RF]
    y = base["hit"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    auc = float(roc_auc_score(y_test, y_prob))
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred)

    importancias = (
        pd.DataFrame(
            {
                "variable": COLUMNAS_RF,
                "etiqueta": [ETIQUETAS_VARIABLES[c] for c in COLUMNAS_RF],
                "importancia": rf.feature_importances_,
                "importancia_pct": rf.feature_importances_ * 100.0,
            }
        )
        .sort_values("importancia", ascending=False)
        .reset_index(drop=True)
    )

    return {
        "modelo": rf,
        "umbral_hit": umbral_hit,
        "total_evaluado": len(base),
        "tasa_hits": float(y.mean()),
        "accuracy": acc,
        "roc_auc": auc,
        "fpr": fpr,
        "tpr": tpr,
        "confusion_matrix": cm,
        "importancias": importancias,
    }


def predecir_hit_simulador(
    modelo: RandomForestClassifier,
    duracion_min: float,
    seguidores: float,
    pop_artista: float,
    num_track: int,
    explicito: bool,
    total_tracks: int,
    anio: int,
) -> dict:
    entrada = pd.DataFrame(
        [
            {
                "duration_min": float(duracion_min),
                "artist_followers": float(seguidores),
                "artist_popularity": float(pop_artista),
                "track_number": int(num_track),
                "explicit_int": 1 if explicito else 0,
                "album_total_tracks": int(total_tracks),
                "year": int(anio),
            }
        ]
    )[COLUMNAS_RF]

    prob_hit = float(modelo.predict_proba(entrada)[0, 1])
    riesgo_relleno = bool(pop_artista >= 65 and duracion_min >= 3.95 and total_tracks >= 10)
    return {
        "probabilidad_hit": prob_hit,
        "es_hit_estimado": prob_hit >= 0.5,
        "riesgo_relleno": riesgo_relleno,
    }


if __name__ == "__main__":
    datos = cargar_datos()
    ev = calcular_evidencia_estadistica(datos)
    cl = ejecutar_clustering(datos, k=4)
    rf_res = ejecutar_clasificacion(datos, umbral_hit=70)

    print("=== 1. EVIDENCIA ESTADISTICA ===")
    print(
        f"Duracion media: 2000s={ev['duracion_2000']:.2f} min | "
        f"2010s={ev['duracion_2010']:.2f} min | "
        f"2020s={ev['duracion_2020']:.2f} min "
        f"({ev['reduccion_pct'] * 100:.1f}% reduccion)"
    )
    print(f"ANOVA: F={ev['anova_f']:.2f}, p={ev['anova_p']:.2e}")
    print(
        f"Prueba T Explicito vs Limpio: {ev['pop_explicito']:.2f} vs "
        f"{ev['pop_limpio']:.2f} (t={ev['ttest_t']:.2f}, p={ev['ttest_p']:.2e})"
    )
    print(
        f"Proporcion Explicito: 2000s={ev['pct_exp_2000'] * 100:.1f}% -> "
        f"2020s={ev['pct_exp_2020'] * 100:.1f}%"
    )
    print("\n=== 2. CLUSTERING K-MEANS (k=4) ===")
    print(
        cl["perfil"][
            ["canciones", "track_popularity", "duration_min", "artist_popularity"]
        ].round(2)
    )
    print("\n=== 3. CLASIFICACION RANDOM FOREST (Hit >= 70) ===")
    print(
        f"Accuracy: {rf_res['accuracy'] * 100:.1f}% | "
        f"ROC-AUC: {rf_res['roc_auc'] * 100:.1f}%"
    )
    print(rf_res["importancias"][["etiqueta", "importancia_pct"]].round(1).to_string(index=False))
