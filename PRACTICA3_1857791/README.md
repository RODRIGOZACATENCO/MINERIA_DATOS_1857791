# Practica 3: Visualizacion de Datos


## Descripcion de las Graficas

1. Diagrama de Pastel
Muestra la distribucion porcentual de las canciones segun el tipo de lanzamiento (album_type).
- Album: 68.6% (6,020 canciones)
- Sencillo: 25.6% (2,244 canciones)
- Recopilacion: 5.8% (508 canciones)
La gran mayoria de las pistas del catalogo provienen de albumes completos de estudio, seguidas de lanzamientos individuales.

2. Histograma
Muestra la distribucion de frecuencias de la popularidad de las canciones (track_popularity) en una escala de 0 a 100 puntos dividida en 20 intervalos.
-  tiene un pico en niveles cercanos a cero (canciones recientes o con pocas reproducciones) y una concentracion principal entre 50 y 75 puntos.
- Los valores superiores a 85 puntos son poco frecuentes, lo que confirma que los grandes exitos representan una proporcion pequena del catalogo.

3. Diagrama de Caja
Compara la distribucion de la popularidad de las canciones agrupadas por tipo de lanzamiento (album, single y compilation).
- Las canciones pertenecientes a albumes presentan una mediana superior (alrededor de 61 puntos) y una mayor dispersion intercuartilica.
- Los sencillos  muestran una mediana cercana a 51 puntos.
- Las recopilaciones tienen la mediana mas baja (aproximadamente 44 puntos), con menor dispersion general.

4. Diagrama de Dispersion 
Representa la relacion entre la popularidad del artista (artist_popularity) en el eje X y la popularidad de sus canciones (track_popularity) en el eje Y.
- Se observa una correlacion positiva: los artistas con mayor popularidad tienden a posicionar sus canciones en puntuaciones mas altas.
- Sin embargo, tambien existen temas de artistas populares con baja popularidad individual (pistas secundarias o pistas instrumentales de album).

5. Diagrama de Barras 
Presenta el ranking de los 10 artistas con mayor numero de canciones dentro del conjunto de datos.
- Taylor Swift encabeza el listado con 330 canciones.
- Le siguen The Weeknd (151), Ariana Grande (101), Lana Del Rey (99), Nirvana (91), Drake (86), Post Malone (83), The Neighbourhood (77), Lady Gaga (72) y Olivia Rodrigo (70).
- Facilita la comparacion directa de volumen de contenido entre los artistas mas representados.

6. Diagrama de Lineas
Muestra la evolucion del numero de canciones lanzadas por anio en el periodo 2000 a 2024.
- Hay una tendencia creciente a lo largo del tiempo.
