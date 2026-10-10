# Script para la generacion automatica de graficas de visualizacion de datos
# Practica 3 - Mineria de Datos

import os
import pandas as pd
import matplotlib.pyplot as plt

# Cargar el archivo de datos
nombre_archivo = "track_data_cleaned.csv" if os.path.exists("track_data_cleaned.csv") else "track_data_final.csv"
datos = pd.read_csv(nombre_archivo)

# Crear carpeta para almacenar las imagenes generadas
carpeta_salida = "graficas"
os.makedirs(carpeta_salida, exist_ok=True)

# Preparar datos para cada tipo de visualizacion
conteo_album = datos["album_type"].value_counts()
top_artistas = datos["artist_name"].value_counts().head(10)

anios = pd.to_datetime(datos["album_release_date"], errors="coerce").dt.year
conteo_anios = anios[(anios >= 2000) & (anios <= 2024)].value_counts().sort_index()

tipos_album = ["album", "single", "compilation"]
datos_caja = [datos[datos["album_type"] == tipo]["track_popularity"].dropna() for tipo in tipos_album]

# Lista de configuraciones para automatizar la creacion de graficas mediante un ciclo
configuraciones_graficas = [
    {
        "tipo": "pastel",
        "archivo": "grafica_1_pastel.png",
        "titulo": "Distribucion de Canciones por Tipo de Album",
        "datos": conteo_album,
        "etiquetas": ["Album", "Single", "Compilation"]
    },
    {
        "tipo": "histograma",
        "archivo": "grafica_2_histograma.png",
        "titulo": "Distribucion de la Popularidad de las Canciones",
        "datos": datos["track_popularity"],
        "eje_x": "Popularidad (puntos)",
        "eje_y": "Numero de canciones",
        "bins": 20
    },
    {
        "tipo": "caja",
        "archivo": "grafica_3_caja.png",
        "titulo": "Popularidad de Canciones por Tipo de Album",
        "datos": datos_caja,
        "etiquetas": ["Album", "Single", "Compilation"],
        "eje_x": "Tipo de album",
        "eje_y": "Popularidad (puntos)"
    },
    {
        "tipo": "dispersion",
        "archivo": "grafica_4_dispersion.png",
        "titulo": "Relacion entre Popularidad del Artista y de la Cancion",
        "x": datos["artist_popularity"],
        "y": datos["track_popularity"],
        "eje_x": "Popularidad del artista (puntos)",
        "eje_y": "Popularidad de la cancion (puntos)"
    },
    {
        "tipo": "barras",
        "archivo": "grafica_5_barras.png",
        "titulo": "Top 10 Artistas con Mas Canciones",
        "datos": top_artistas,
        "eje_x": "Numero de canciones",
        "eje_y": "Artista"
    },
    {
        "tipo": "lineas",
        "archivo": "grafica_6_lineas.png",
        "titulo": "Evolucion del Numero de Canciones por Anio (2000 - 2024)",
        "datos": conteo_anios,
        "eje_x": "Anio de lanzamiento",
        "eje_y": "Numero de canciones"
    }
]

# Ciclo principal para automatizar la generacion y guardado de las graficas
for config in configuraciones_graficas:
    plt.figure(figsize=(8, 5))
    tipo = config["tipo"]

    if tipo == "pastel":
        # Generar diagrama de pastel
        plt.pie(
            config["datos"],
            labels=config["etiquetas"],
            autopct="%1.1f%%",
            startangle=140,
            colors=["#4C72B0", "#55A868", "#C44E52"]
        )

    elif tipo == "histograma":
        # Generar histograma
        plt.hist(
            config["datos"],
            bins=config["bins"],
            color="#4C72B0",
            edgecolor="black"
        )
        plt.xlabel(config["eje_x"])
        plt.ylabel(config["eje_y"])
        plt.grid(axis="y", linestyle="--", alpha=0.7)

    elif tipo == "caja":
        # Generar diagrama de caja
        plt.boxplot(
            config["datos"],
            tick_labels=config["etiquetas"],
            patch_artist=True,
            boxprops=dict(facecolor="#A0C4DF", color="#1F497D"),
            medianprops=dict(color="red", linewidth=1.5)
        )
        plt.xlabel(config["eje_x"])
        plt.ylabel(config["eje_y"])
        plt.grid(axis="y", linestyle="--", alpha=0.7)

    elif tipo == "dispersion":
        # Generar diagrama de dispersion
        plt.scatter(
            config["x"],
            config["y"],
            alpha=0.3,
            color="#2B5C8F",
            s=20
        )
        plt.xlabel(config["eje_x"])
        plt.ylabel(config["eje_y"])
        plt.grid(True, linestyle="--", alpha=0.7)

    elif tipo == "barras":
        # Generar diagrama de barras horizontales
        plt.barh(
            config["datos"].index[::-1],
            config["datos"].values[::-1],
            color="#4C72B0",
            edgecolor="black"
        )
        plt.xlabel(config["eje_x"])
        plt.ylabel(config["eje_y"])
        plt.grid(axis="x", linestyle="--", alpha=0.7)

    elif tipo == "lineas":
        # Generar diagrama de lineas
        plt.plot(
            config["datos"].index,
            config["datos"].values,
            marker="o",
            color="#2B5C8F",
            linewidth=2
        )
        plt.xlabel(config["eje_x"])
        plt.ylabel(config["eje_y"])
        plt.grid(True, linestyle="--", alpha=0.7)

    # Titulo y ajustes de presentacion
    plt.title(config["titulo"], fontsize=12, pad=10)
    plt.tight_layout()

    # Guardar archivo de imagen
    ruta_guardado = os.path.join(carpeta_salida, config["archivo"])
    plt.savefig(ruta_guardado, dpi=300)
    plt.close()

    print(f"Grafica generada: {config['archivo']}")
