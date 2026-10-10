import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def limpiar_dataset(ruta_origen="track_data_final.csv", ruta_destino="track_data_cleaned.csv"):
    # Cargar conjunto original de datos
    df = pd.read_csv(ruta_origen)
    n_inicial = len(df)

    # Identificar filas con duracion no valida o fecha 0000
    filas_corruptas = df[(df["track_duration_ms"] <= 0) | (df["album_release_date"] == "0000") | df["track_name"].isnull()]
    
    # Identificar filas con datos de artista faltantes
    filas_artista_nulo = df[df["artist_name"].isnull()]

    # Filtrar solo registros validos
    df_limpio = df[
        (df["track_duration_ms"] > 0) &
        (df["album_release_date"] != "0000") &
        df["track_name"].notnull() &
        df["album_name"].notnull() &
        df["artist_name"].notnull()
    ].copy()

    # Limpiar espacios en blanco al inicio o fin de cadenas
    for col in df_limpio.columns:
        if df_limpio[col].dtype == "object":
            df_limpio[col] = df_limpio[col].astype(str).str.strip()

    # Guardar copia limpia del dataset
    df_limpio.to_csv(ruta_destino, index=False)

    return df_limpio, {
        "N_inicial": n_inicial,
        "N_final": len(df_limpio),
        "Filas_Corruptas": len(filas_corruptas),
        "Filas_Artista_Nulo": len(filas_artista_nulo),
        "Total_Eliminadas": n_inicial - len(df_limpio)
    }

def calcular_estadisticas_no_agrupadas(df, columna):
    # Filtrar valores no nulos
    s = df[columna].dropna()
    n = len(s)
    
    # Calculos estadisticos basales
    x_min = float(s.min())
    x_max = float(s.max())
    rango = x_max - x_min
    media = float(s.mean())
    mediana = float(s.median())
    varianza = float(s.var(ddof=1))
    desv_std = float(s.std(ddof=1))
    cv = (desv_std / media) * 100.0 if media != 0 else 0.0
    
    # Cuartiles y dispersion intercuartil
    q1 = float(s.quantile(0.25))
    q3 = float(s.quantile(0.75))
    iqr = q3 - q1
    
    # Momentos de distribucion: Asimetria y curtosis
    asimetria = float(s.skew())
    curtosis = float(s.kurtosis())
    
    return {
        "N": n, "Min": x_min, "Max": x_max, "Rango": rango,
        "Media": media, "Mediana": mediana, "Varianza": varianza,
        "DesvStd": desv_std, "CV": cv, "Q1": q1, "Q3": q3,
        "IQR": iqr, "Asimetria": asimetria, "Curtosis": curtosis
    }


def construir_tabla_frecuencias(df, columna, usar_impar=True):
    # Extraer valores de la columna
    s = df[columna].dropna()
    n = len(s)
    x_min = float(s.min())
    x_max = float(s.max())
    rango = x_max - x_min
    
    # Formula de Sturges: k = 1 + 3.322 * log10(N)
    k_sturges = 1.0 + 3.322 * math.log10(n)
    k_entero = round(k_sturges)
    
    # Redondear al entero impar mas cercano para clase central simetrica
    if usar_impar and (k_entero % 2 == 0):
        k = k_entero + 1
    else:
        k = k_entero
        
    # Ancho de intervalo de clase: c = R / k
    c = rango / k
    
    # Calcular frecuencias absolutas, relativas y acumuladas
    clases = []
    frecuencia_acumulada = 0
    suma_fi_xi = 0.0
    
    for i in range(k):
        lim_inf = x_min + i * c
        lim_sup = x_min + (i + 1) * c
        
        # Conteo de observaciones en el intervalo
        if i == k - 1:
            conteo = int(((s >= lim_inf) & (s <= x_max)).sum())
        else:
            conteo = int(((s >= lim_inf) & (s < lim_sup)).sum())
            
        # Marca de clase: promedio del limite inferior y superior
        marca_xi = (lim_inf + lim_sup) / 2.0
        
        # Frecuencias relativas y acumuladas
        frec_relativa = conteo / n
        frecuencia_acumulada += conteo
        frec_rel_acumulada = frecuencia_acumulada / n
        
        suma_fi_xi += conteo * marca_xi
        
        clases.append({
            "Clase": i + 1,
            "Lim_Inf": lim_inf,
            "Lim_Sup": lim_sup,
            "Marca_xi": marca_xi,
            "fi": conteo,
            "fr": frec_relativa,
            "Fi": frecuencia_acumulada,
            "Fr": frec_rel_acumulada
        })
        
    df_tabla = pd.DataFrame(clases)
    
    # Media de datos agrupados: x_bar = sum(fi * xi) / N
    media_agrupada = suma_fi_xi / n
    
    # Mediana agrupada: Li + [(N/2 - F_{i-1}) / f_med] * c
    mitad_n = n / 2.0
    idx_clase_mediana = df_tabla[df_tabla["Fi"] >= mitad_n].index[0]
    fila_mediana = df_tabla.iloc[idx_clase_mediana]
    f_ant = df_tabla.iloc[idx_clase_mediana - 1]["Fi"] if idx_clase_mediana > 0 else 0
    l_med = fila_mediana["Lim_Inf"]
    f_med = fila_mediana["fi"]
    mediana_agrupada = l_med + ((mitad_n - f_ant) / f_med) * c
    
    # Clase modal y calculo de moda agrupada por diferencias finitas
    idx_modal = df_tabla["fi"].idxmax()
    fila_modal = df_tabla.iloc[idx_modal]
    f_modal = fila_modal["fi"]
    f_modal_ant = df_tabla.iloc[idx_modal - 1]["fi"] if idx_modal > 0 else 0
    f_modal_pos = df_tabla.iloc[idx_modal + 1]["fi"] if idx_modal < (k - 1) else 0
    delta_1 = f_modal - f_modal_ant
    delta_2 = f_modal - f_modal_pos
    l_mod = fila_modal["Lim_Inf"]
    if (delta_1 + delta_2) != 0:
        moda_agrupada = l_mod + (delta_1 / (delta_1 + delta_2)) * c
    else:
        moda_agrupada = fila_modal["Marca_xi"]
        
    # Varianza muestral agrupada: s^2 = sum(fi * (xi - x_bar)^2) / (N - 1)
    suma_dif_cuad = sum(
        row["fi"] * ((row["Marca_xi"] - media_agrupada) ** 2)
        for _, row in df_tabla.iterrows()
    )
    varianza_agrupada = suma_dif_cuad / (n - 1)
    desv_std_agrupada = math.sqrt(varianza_agrupada)
    cv_agrupado = (desv_std_agrupada / media_agrupada) * 100.0
    
    metricas_agrupadas = {
        "N": n, "Rango": rango, "k_sturges": k_sturges, "k": k, "c": c,
        "Media": media_agrupada, "Mediana": mediana_agrupada,
        "Moda": moda_agrupada, "Clase_Modal": fila_modal["Clase"],
        "Clase_Modal_Lim_Inf": l_mod, "Clase_Modal_Lim_Sup": fila_modal["Lim_Sup"],
        "Clase_Modal_fi": f_modal, "Varianza": varianza_agrupada,
        "DesvStd": desv_std_agrupada, "CV": cv_agrupado
    }
    
    return df_tabla, metricas_agrupadas


def generar_graficos_variable(df, columna, df_tabla, metricas_agr, metricas_no_agr, nombre_etiqueta, unidad, ruta_salida):
    # Obtener valores limpios
    s = df[columna].dropna()
    
    # Crear tres graficos estadisticos complementarios
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=300)
    
    # 1. Histograma ajustado a intervalos de clase exactos
    ax_hist = axes[0]
    bordes = list(df_tabla["Lim_Inf"]) + [df_tabla.iloc[-1]["Lim_Sup"]]
    ax_hist.hist(s, bins=bordes, color="#38bdf8", edgecolor="#0369a1", linewidth=1.2, alpha=0.85)
    ax_hist.axvline(metricas_agr["Media"], color="#dc2626", linestyle="--", linewidth=1.5, label=f"Media Agr: {metricas_agr['Media']:.1f}")
    ax_hist.axvline(metricas_agr["Mediana"], color="#16a34a", linestyle="-.", linewidth=1.5, label=f"Mediana Agr: {metricas_agr['Mediana']:.1f}")
    ax_hist.axvline(metricas_agr["Moda"], color="#9333ea", linestyle=":", linewidth=1.5, label=f"Moda Agr: {metricas_agr['Moda']:.1f}")
    ax_hist.set_title(f"Histograma de Frecuencias\n({nombre_etiqueta})", fontsize=11, fontweight="bold")
    ax_hist.set_xlabel(f"{nombre_etiqueta} ({unidad})", fontsize=9.5)
    ax_hist.set_ylabel("Frecuencia Absoluta (fi)", fontsize=9.5)
    ax_hist.legend(fontsize=8, loc="upper right")
    ax_hist.grid(axis="y", linestyle=":", alpha=0.6)

    # 2. Ojiva de distribucion acumulada (curva ojiva)
    ax_ogiva = axes[1]
    puntos_x = [df_tabla.iloc[0]["Lim_Inf"]] + list(df_tabla["Lim_Sup"])
    puntos_y = [0] + list(df_tabla["Fi"])
    ax_ogiva.plot(puntos_x, puntos_y, marker="o", color="#0284c7", linewidth=2, markersize=4, label="Ojiva (Fi)")
    ax_ogiva.axhline(metricas_agr["N"] / 2.0, color="#16a34a", linestyle="--", linewidth=1.2, label=f"50% N = {metricas_agr['N']/2:.0f}")
    ax_ogiva.set_title(f"Ojiva Acumulativa\n({nombre_etiqueta})", fontsize=11, fontweight="bold")
    ax_ogiva.set_xlabel(f"{nombre_etiqueta} ({unidad})", fontsize=9.5)
    ax_ogiva.set_ylabel("Frecuencia Acumulada (Fi)", fontsize=9.5)
    ax_ogiva.legend(fontsize=8, loc="lower right")
    ax_ogiva.grid(True, linestyle=":", alpha=0.6)

    # 3. Diagrama de caja y bigotes (Boxplot) para cuantiles y dispersion
    ax_box = axes[2]
    bp = ax_box.boxplot(
        s, orientation="vertical", patch_artist=True,
        boxprops=dict(facecolor="#bae6fd", color="#0284c7", linewidth=1.2),
        whiskerprops=dict(color="#0284c7", linewidth=1.2),
        capprops=dict(color="#0284c7", linewidth=1.2),
        medianprops=dict(color="#dc2626", linewidth=1.8),
        flierprops=dict(marker="o", markersize=2.5, markerfacecolor="#f43f5e", markeredgecolor="none", alpha=0.4)
    )
    ax_box.set_title(f"Diagrama de Caja (Boxplot)\n({nombre_etiqueta})", fontsize=11, fontweight="bold")
    ax_box.set_ylabel(f"{nombre_etiqueta} ({unidad})", fontsize=9.5)
    ax_box.set_xticks([1])
    ax_box.set_xticklabels([nombre_etiqueta], fontsize=9)
    ax_box.grid(axis="y", linestyle=":", alpha=0.6)

    # Guardar en archivo PNG de alta resolucion
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=300)
    plt.close()
    print(f"Grafico guardado en: {ruta_salida}")


def ejecutar_analisis_completo():
    # Paso 1: Limpieza de datos y exportacion del nuevo archivo limpio
    df_limpio, reporte_limpieza = limpiar_dataset("track_data_final.csv", "track_data_cleaned.csv")

    # Analisis de variables continuas principales
    variables_a_evaluar = [
        ("track_duration_ms", "Duracion de Cancion", "ms", "graficos_duracion.png"),
        ("track_popularity", "Popularidad de Pista", "pts", "graficos_popularidad.png")
    ]

    for col, etiqueta, unidad, archivo_img in variables_a_evaluar:
        print("\n" + "=" * 80)
        print(f"ANALISIS DE DATOS AGRUPADOS: {etiqueta} ({col})")
        print("=" * 80)

        # Baseline no agrupado
        no_agr = calcular_estadisticas_no_agrupadas(df_limpio, col)
        
        # Tabla de frecuencias con regla de Sturges
        df_tabla, agr = construir_tabla_frecuencias(df_limpio, col, usar_impar=True)

        print("\nTABLA DE DISTRIBUCION DE FRECUENCIAS:")
        tabla_str = df_tabla.to_string(
            index=False,
            formatters={
                "Lim_Inf": "{:.2f}".format,
                "Lim_Sup": "{:.2f}".format,
                "Marca_xi": "{:.2f}".format,
                "fr": "{:.6f}".format,
                "Fr": "{:.6f}".format
            }
        )
        print(tabla_str)

        # Comparacion de metricas y error de agrupamiento
        err_media = abs(agr["Media"] - no_agr["Media"])
        err_rel_media = (err_media / no_agr["Media"]) * 100 if no_agr["Media"] != 0 else 0
        err_var = abs(agr["Varianza"] - no_agr["Varianza"])
        err_rel_var = (err_var / no_agr["Varianza"]) * 100 if no_agr["Varianza"] != 0 else 0
        err_mediana = abs(agr["Mediana"] - no_agr["Mediana"])

        print("\nMETRICAS DE TENDENCIA CENTRAL:")
        print(f"  - Media Agrupada:     {agr['Media']:.4f}  | Exacta No Agrupada: {no_agr['Media']:.4f}  | Error: {err_media:.4f} ({err_rel_media:.2f}%)")
        print(f"  - Mediana Agrupada:   {agr['Mediana']:.4f}  | Exacta No Agrupada: {no_agr['Mediana']:.4f}  | Error: {err_mediana:.4f}")
        print(f"  - Clase Modal:        Clase {agr['Clase_Modal']} [{agr['Clase_Modal_Lim_Inf']:.2f} - {agr['Clase_Modal_Lim_Sup']:.2f}] con fi={agr['Clase_Modal_fi']}")
        print(f"  - Moda Agrupada (Int):{agr['Moda']:.4f}")

        print("\nMETRICAS DE DISPERSION:")
        print(f"  - Varianza Agrupada:  {agr['Varianza']:.4f}  | Exacta No Agrupada: {no_agr['Varianza']:.4f}  | Error: {err_var:.4f} ({err_rel_var:.2f}%)")
        print(f"  - Desv. Std Agrupada: {agr['DesvStd']:.4f}  | Exacta No Agrupada: {no_agr['DesvStd']:.4f}")
        print(f"  - Coef. de Variacion: {agr['CV']:.2f}%  | Exacto No Agrupado: {no_agr['CV']:.2f}%")


if __name__ == "__main__":
    ejecutar_analisis_completo()
