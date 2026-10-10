## Limpieza de Datos

### Elementos Defectuosos Identificados (Bad Items)

Se detectaron dos clases de registros inconsistentes que sumaban un total de 6 filas defectuosas:

1. Registros corruptos o fantasma (2 observaciones):
  * Fila 3618 (track_id: 37ns6v0HK4zMV1PpRLIsbx) y 
  * Fila 4170 (track_id: 6N21iOdTYgYjDK1AyS0iUW).

2. Registros incompletos con datos de artista faltantes (4 observaciones):
  * Fila 436 (track_id: 3QhfFRPkhPCR1RMJWV1gde, track_name: 'Radio')
  * Fila 1396 (track_id: 2NbsBSshscKIPRG3kwBbfo, track_name: 'Never Felt So Alone')
  * Fila 3885 (track_id: 5EhZC8GFOVXrpiUW22jncE, track_name: 'Urban Twilight')
  * Fila 3886 (track_id: 0fM9dEhUFV4MHDuJgrcfOv, track_name: 'How You Get The Girl')


### Que se Cambio en el Conjunto de Datos

Para asegurar una base de datos solida y sin distorsiones estadisticas, se ejecutaron las siguientes acciones correctivas:

1. Eliminacion de registros corruptos:
Se eliminaron las filas 3618 y 4170.

2. Eliminacion de registros sin artista:
Se descartaron las filas 436, 1396, 3885 y 3886 para asegurar la integridad referencial estricta requerida por el esquema relacional en Tercera Forma Normal (3NF).

3. Normalizacion de texto:
Se aplico un formateo con recorte de espacios en blanco (strip) a todas las columnas categoricas y de texto.

## Modelado Entidad-Relacion y Diseno: 

1. Entidad TRACK (Pista o Cancion):
Representa la unidad de grabacion de audio.
- track_id: Identificador unico de la cancion en Spotify (Clave Primaria).
- track_name: Titulo descriptivo de la pista.
- track_number: Numero secuencial de la pista dentro del album.
- track_popularity: Indice de popularidad de la cancion (escala 0 a 100).
- track_duration_ms: Duracion de la cancion en milisegundos.
- explicit: Booleano que indica contenido explicito.
- album_id: Clave foranea que referencia al album contenedor.
- artist_name: Clave foranea que referencia al artista principal.

2. Entidad ALBUM (Album):
Representa la produccion discografica que agrupa pistas.
- album_id: Identificador alfanumerico unico del album (Clave Primaria).
- album_name: Titulo del album.
- album_release_date: Fecha de publicacion (YYYY o YYYY-MM-DD).
- album_total_tracks: Cantidad total de pistas del lanzamiento.
- album_type: Tipo de produccion ('album', 'single', 'compilation').
- artist_name: Clave foranea que referencia al artista creador.

3. Entidad ARTIST (Artista):
Representa al interprete o creador musical.
- artist_name: Nombre del artista (Clave Primaria).
- artist_popularity: Popularidad acumulada del artista (escala 0 a 100).
- artist_followers: Numero de seguidores en la plataforma.

4. Entidad GENRE (Genero Musical):
Catalogo de etiquetas estilisticas.
- genre_id: Identificador entero secuencial unico (Clave Primaria).
- genre_name: Nombre del genero o subgenero musical.

5. Entidad ARTIST_GENRE (Asociativa Artista - Genero):
Resuelve la relacion muchos a muchos (N:M) entre artistas y generos, eliminando la violacion de 1NF.
- artist_name: Clave foranea hacia ARTIST.
- genre_id: Clave foranea hacia GENRE.
- Clave Primaria Compuesta: (artist_name, genre_id).

### Claves, Restricciones y Cardinalidades

1. Relacion ARTIST - ALBUM (1 a N):
Un artista puede publicar uno o multiples albumes. Cada album pertenece a un artista.
- Clave foranea: ALBUM.artist_name -> ARTIST.artist_name.
- Restriccion: ON DELETE RESTRICT, ON UPDATE CASCADE.

2. Relacion ALBUM - TRACK (1 a N):
Un album agrupa una o multiples canciones. Cada cancion pertenece estrictamente a un album.
- Clave foranea: TRACK.album_id -> ALBUM.album_id.
- Restriccion: ON DELETE CASCADE, ON UPDATE CASCADE.

3. Relacion ARTIST - TRACK (1 a N):
Un artista interpreta una o varias canciones del catalogo.
- Clave foranea: TRACK.artist_name -> ARTIST.artist_name.
- Restriccion: ON DELETE RESTRICT, ON UPDATE CASCADE.

4. Relacion ARTIST - GENRE (N a M):
Un artista puede asociarse a multiples generos y un genero clasifica a multiples artistas. Se implementa mediante la tabla intermedia ARTIST_GENRE.
- Claves foraneas: ARTIST_GENRE.artist_name -> ARTIST.artist_name y ARTIST_GENRE.genre_id -> GENRE.genre_id.


## Clasificacion de Variables y Perfilado Inicial de Datos

### Clasificacion por Escala de Medicion

Se auditan las 15 columnas del conjunto de datos limpio:

| Columna | Naturaleza Estadistica | Escala de Medicion | Descripcion |
|---|---|---|---|
| track_id | Cualitativa Nominal | Nominal | Identificador alfanumerico de pista |
| track_name | Cualitativa Nominal | Nominal | Titulo de la pista musical |
| track_number | Cuantitativa Discreta | Intervalo / Conteo | Posicion de la pista en el album |
| track_popularity | Cuantitativa Discreta / Continua | Razon (0 a 100) | Nivel de popularidad de la cancion |
| track_duration_ms | Cuantitativa Continua | Razon (tiempo en ms) | Duracion del archivo de audio |
| explicit | Cualitativa Nominal Dicotomica | Nominal (Booleano) | Indicador de contenido explicito |
| artist_name | Cualitativa Nominal | Nominal | Nombre del artista musical |
| artist_popularity | Cuantitativa Discreta / Continua | Razon (0 a 100) | Popularidad acumulada del artista |
| artist_followers | Cuantitativa Discreta | Razon (conteo) | Cantidad de seguidores del artista |
| artist_genres | Cualitativa Nominal Multiple | Nominal | Lista de generos musicales |
| album_id | Cualitativa Nominal | Nominal | Identificador alfanumerico del album |
| album_name | Cualitativa Nominal | Nominal | Nombre del album discografico |
| album_release_date | Cualitativa Ordinal / Temporal | Cronologica | Fecha de publicacion del album |
| album_total_tracks | Cuantitativa Discreta | Razon (conteo >= 1) | Total de canciones en el album |
| album_type | Cualitativa Nominal | Nominal | Categoria ('album', 'single', 'compilation') |


### Parametros de Diseno de Clases (Regla de Sturges)

Para la muestra limpia de N = 8,772 observaciones:
- Calculo exacto de Sturges:
  k = 1 + 3.322 * log10(8,772) = 1 + 3.322 * 3.9431 = 14.0990
- Seleccion de k:
  Se adopta k = 15 clases (redondeo al entero impar mas cercano)

Parametros para Duracion (track_duration_ms):
- X_min = 4,388.00 ms, X_max = 811,077.00 ms
- Rango: R = 806,689.00 ms
- Ancho de intervalo de clase: c = R / k = 806,689.00 / 15 = 53,779.2667 ms

Parametros para Popularidad (track_popularity):
- X_min = 0.00 pts, X_max = 100.00 pts
- Rango: R = 100.00 pts
- Ancho de intervalo de clase: c = R / k = 100.00 / 15 = 6.6667 pts

### Tabla de Distribucion de Frecuencias: Duracion (track_duration_ms)

| Clase | Lim_Inf (ms) | Lim_Sup (ms) | Marca_xi (ms) | fi | fr | Fi | Fr |
|---|---|---|---|---|---|---|---|
| 1 | 4,388.00 | 58,167.27 | 31,277.63 | 47 | 0.005358 | 47 | 0.005358 |
| 2 | 58,167.27 | 111,946.53 | 85,056.90 | 301 | 0.034314 | 348 | 0.039672 |
| 3 | 111,946.53 | 165,725.80 | 138,836.17 | 1,464 | 0.166895 | 1,812 | 0.206566 |
| 4 | 165,725.80 | 219,505.07 | 192,615.43 | 3,453 | 0.393639 | 5,265 | 0.600205 |
| 5 | 219,505.07 | 273,284.33 | 246,394.70 | 2,506 | 0.285682 | 7,771 | 0.885887 |
| 6 | 273,284.33 | 327,063.60 | 300,173.97 | 686 | 0.078203 | 8,457 | 0.964090 |
| 7 | 327,063.60 | 380,842.87 | 353,953.23 | 187 | 0.021318 | 8,644 | 0.985408 |
| 8 | 380,842.87 | 434,622.13 | 407,732.50 | 57 | 0.006498 | 8,701 | 0.991906 |
| 9 | 434,622.13 | 488,401.40 | 461,511.77 | 41 | 0.004674 | 8,742 | 0.996580 |
| 10 | 488,401.40 | 542,180.67 | 515,291.03 | 10 | 0.001140 | 8,752 | 0.997720 |
| 11 | 542,180.67 | 595,959.93 | 569,070.30 | 11 | 0.001254 | 8,763 | 0.998974 |
| 12 | 595,959.93 | 649,739.20 | 622,849.57 | 2 | 0.000228 | 8,765 | 0.999202 |
| 13 | 649,739.20 | 703,518.47 | 676,628.83 | 3 | 0.000342 | 8,768 | 0.999544 |
| 14 | 703,518.47 | 757,297.73 | 730,408.10 | 2 | 0.000228 | 8,770 | 0.999772 |
| 15 | 757,297.73 | 811,077.00 | 784,187.37 | 2 | 0.000228 | 8,772 | 1.000000 |
| Total | - | - | - | 8,772 | 1.000000 | - | - |

### Metricas Agrupadas de Duracion

1. Media Agrupada:
x_bar = (sum fi * xi) / N = 1,844,883,323.51 / 8,772 = 210,315.0164 ms

2. Mediana Agrupada:
N / 2 = 4,386. Se ubica en la Clase 4 (Fi anterior = 1,812, Fi clase = 5,265).
- L_med = 165,725.80 ms
- F_{i-1} = 1,812
- f_med = 3,453
- c = 53,779.2667 ms
Formula: Med = L_med + [(N/2 - F_{i-1}) / f_med] * c
Med = 165,725.80 + [(4,386 - 1,812) / 3,453] * 53,779.2667 = 205,814.9493 ms

3. Clase Modal y Moda Agrupada:
Mayor frecuencia en Clase 4 (fi = 3,453 canciones).
- Intervalo modal: [165,725.80 ms, 219,505.07 ms]
- Delta_1 = fi - f_{i-1} = 3,453 - 1,464 = 1,989
- Delta_2 = fi - f_{i+1} = 3,453 - 2,506 = 947
Formula: Mo = L_mod + [Delta_1 / (Delta_1 + Delta_2)] * c
Mo = 165,725.80 + [1,989 / (1,989 + 947)] * 53,779.2667 = 202,158.6888 ms (~3 min 22 s)

4. Dispersion Agrupada:
- Varianza agrupada: s^2 = 4,195,317,568.3240 ms^2
- Desviacion estandar agrupada: s = 64,771.2712 ms
- Coeficiente de variacion agrupado: CV = 30.80%

### Tabla de Distribucion de Frecuencias: Popularidad (track_popularity)

| Clase | Lim_Inf (pts) | Lim_Sup (pts) | Marca_xi (pts) | fi | fr | Fi | Fr |
|---|---|---|---|---|---|---|---|
| 1 | 0.00 | 6.67 | 3.33 | 842 | 0.095987 | 842 | 0.095987 |
| 2 | 6.67 | 13.33 | 10.00 | 110 | 0.012540 | 952 | 0.108527 |
| 3 | 13.33 | 20.00 | 16.67 | 111 | 0.012654 | 1,063 | 0.121181 |
| 4 | 20.00 | 26.67 | 23.33 | 331 | 0.037734 | 1,394 | 0.158915 |
| 5 | 26.67 | 33.33 | 30.00 | 384 | 0.043776 | 1,778 | 0.202690 |
| 6 | 33.33 | 40.00 | 36.67 | 492 | 0.056088 | 2,270 | 0.258778 |
| 7 | 40.00 | 46.67 | 43.33 | 711 | 0.081053 | 2,981 | 0.339831 |
| 8 | 46.67 | 53.33 | 50.00 | 790 | 0.090059 | 3,771 | 0.429891 |
| 9 | 53.33 | 60.00 | 56.67 | 852 | 0.097127 | 4,623 | 0.527018 |
| 10 | 60.00 | 66.67 | 63.33 | 1,155 | 0.131669 | 5,778 | 0.658687 |
| 11 | 66.67 | 73.33 | 70.00 | 1,274 | 0.145235 | 7,052 | 0.803922 |
| 12 | 73.33 | 80.00 | 76.67 | 974 | 0.111035 | 8,026 | 0.914957 |
| 13 | 80.00 | 86.67 | 83.33 | 632 | 0.072047 | 8,658 | 0.987004 |
| 14 | 86.67 | 93.33 | 90.00 | 106 | 0.012084 | 8,764 | 0.999088 |
| 15 | 93.33 | 100.00 | 96.67 | 8 | 0.000912 | 8,772 | 1.000000 |
| Total | - | - | - | 8,772 | 1.000000 | - | - |

### Metricas Agrupadas de Popularidad

1. Media Agrupada:
x_bar = (sum fi * xi) / N = 461,613.33 / 8,772 = 52.6235 pts

2. Mediana Agrupada:
N / 2 = 4,386. Cae en la Clase 9 (Fi anterior = 3,771, Fi clase = 4,623).
- L_med = 53.3333 pts
- F_{i-1} = 3,771
- f_med = 852
- c = 6.6667 pts
Formula: Med = 53.3333 + [(4,386 - 3,771) / 852] * 6.6667 = 58.1455 pts

3. Clase Modal y Moda Agrupada:
Mayor frecuencia en Clase 11 (fi = 1,274 canciones).
- Intervalo modal: [66.67 pts, 73.33 pts]
- Delta_1 = fi - f_{i-1} = 1,274 - 1,155 = 119
- Delta_2 = fi - f_{i+1} = 1,274 - 974 = 300
Formula: Mo = 66.6667 + [119 / (119 + 300)] * 6.6667 = 68.5601 pts

4. Dispersion Agrupada:
- Varianza agrupada: s^2 = 560.4102 pts^2
- Desviacion estandar agrupada: s = 23.6730 pts
- Coeficiente de variacion agrupado: CV = 44.99%

### Comparacion Cuantitativa

| Parametro Estadistico | Variable: Duracion (ms) | | | Variable: Popularidad (pts) | | |
|---|---|---|---|---|---|---|
| | No Agrupado | Agrupado | Error Relativo (%) | No Agrupado | Agrupado | Error Relativo (%) |
| Media Aritmetica | 210,201.46 | 210,315.02 | 0.05% | 52.24 | 52.62 | 0.73% |
| Mediana | 207,276.00 | 205,814.95 | 0.70% | 58.00 | 58.15 | 0.25% |
| Varianza Muestral | 4,002,277,063.49 | 4,195,317,568.32 | 4.82% | 579.28 | 560.41 | 3.26% |
| Desviacion Estandar | 63,263.55 | 64,771.27 | 2.38% | 24.07 | 23.67 | 1.64% |
| Coeficiente Variacion | 30.10% | 30.80% | 2.33% | 46.07% | 44.99% | 2.34% |

Analisis del Error de Agrupamiento:
- En la media aritmetica, el error relativo es del 0.05% para la duracion y del 0.73% para la popularidad, confirmando la precision de la regla de Sturges.
- En la mediana, el error se mantiene por debajo del 0.70%, capturando fielmente el centro de distribucion.


### Interpretacion

1. El 67.93% de las canciones se concentra en las Clases 4 y 5 de duracion (entre 2.76 y 4.55 minutos), con una moda calculada en 202,159 ms (aproximadamente 3 minutos con 22 segundos). Este comportamiento refleja la adaptacion historica a los formatos radiales comerciales y a los algoritmos de retencion de audiencia en streaming.

2. **Comportamiento de la Popularidad**
- la popularidad de las canciones no sigue un orden parejo, sino que se divide claramente en dos extremos:

- **Canciones casi sin reproducciones (Cerca de 0 puntos):** Casi el 10% de las canciones (9.60%) se encuentran en el nivel más bajo (de 0 a 7 puntos). Este grupo corresponde a temas recién subidos, canciones olvidadas o artistas independientes que aún no tienen oyentes ni difusión.
- **Canciones con éxito y audiencia activa (Entre 60 y 75 puntos):** La mayor concentración de canciones se encuentra en niveles medio-altos (alrededor del 40% del catálogo total), que son las pistas que los usuarios escuchan habitualmente en su día a día.

3. **Variabilidad, Casos Extremos y Fiabilidad de los Resultados:**

- **La duración es predecible, pero el éxito no:** La duración de las pistas tiene una variación moderada (30.8%), lo que indica que casi todos los creadores se apegan a formatos estándar de radio o streaming. En contraste, la popularidad varía mucho más (45.0%), reflejando lo impredecible que es el gusto del público y el alcance de cada tema.
- **Los megaéxitos son una minoría absoluta:** Apenas el 1.3% de las canciones supera los 86 puntos de popularidad, demostrando que alcanzar la cima global de Spotify está reservado para un grupo muy exclusivo de temas virales.
- **Presencia de canciones inusuales (casos extremos):** Existen piezas atípicas en el catálogo, desde pistas ultracortas de apenas 4 segundos (skits, intros o efectos de sonido) hasta canciones que sobrepasan los 13 minutos (grabaciones en vivo o temas instrumentales extensos).
- **Alta precisión estadística:** Al comparar los datos originales contra la agrupación de 15 clases, el margen de diferencia fue inferior al 0.73% en los promedios y medianas, lo cual comprueba que resumir miles de filas en grupos no provocó distorsiones ni pérdida de información relevante.
