# Practica 4: Pruebas Estadisticas
## Mineria de Datos | Dataset: Spotify Track Data 

## 1. Objetivo

Comprobar si existen diferencias reales entre grupos usando ANOVA y prueba t frente a Kruskal-Wallis y Mann-Whitney U, revisando primero si los supuestos de cada prueba se cumplen.

## 2. Que se comparo y por que

| Comparacion | Variable numerica | Grupos |
|---|---|---|
| 1 | track_popularity | explicit (Clean vs Explicit) |
| 2 | track_popularity | album_type (album, single, compilation) 
| 3 | track_duration_ms | album_type (album, single, compilation) 

La Comparacion 1 evalua si las canciones con contenido explicito tienen un desempeno en reproducciones diferente a las canciones aptas para todo publico.
La Comparacion 2 examina si el formato de publicacion (album de estudio, sencillo o recopilacion) influye en la popularidad del tema.
La Comparacion 3 analiza si la duracion de las pistas cambia segun el formato de lanzamiento.

## 3. Datos por grupo

Popularidad segun contenido explicito (explicit):

| explicit | Contenido | n |
|---|---|---|
| False | Clean | 6,582 |
| True | Explicit | 2,190 |

Popularidad y duracion segun tipo de album (album_type):

| album_type | Tipo | n |
|---|---|---|
| album | Album de estudio | 6,020 |
| single | Sencillo | 2,244 |
| compilation | Recopilacion | 508 |

Todos los grupos superan el minimo requerido de 30 casos para otorgar validez estadistica a las pruebas.

## 4. Comparacion 1: Popularidad segun contenido explicito

Levene arrojo un valor de 76.0117 con p-value = 3.3360e-18. Al ser p-value menor a 0.05, se rechaza la igualdad de varianzas. Esto confirma que la dispersion de la popularidad no es homogenea entre canciones explicitas y no explicitas.

Estadisticas descriptivas:
- Clean: Media = 50.48 pts, Mediana = 55.00 pts, Desviacion estandar = 24.27
- Explicit: Media = 57.53 pts, Mediana = 64.00 pts, Desviacion estandar = 22.64

Resultados de las pruebas:
- Prueba t de Welch (varianzas desiguales): t = -12.3992, grados de libertad = 3990.3, p-value = 1.1393e-34
- Prueba Mann-Whitney U: U = 5,845,742.0, p-value = 3.6426e-40
- Tamano del efecto: d de Cohen = -0.2954

Interpretacion:
Las canciones con contenido explicito tienen mejores numeros de popularidad que las canciones limpias (unos 7 puntos mas en promedio y 9 puntos mas en la mediana).

Como las varianzas de ambos grupos no son iguales, la prueba adecuada para reportar es Mann-Whitney U. Sin embargo, al revisar el tamano del efecto (d de Cohen = -0.2954), vemos que es un efecto pequeno. Esto significa que, aunque la diferencia existe en los datos, hacer una cancion explicita no te asegura el exito por si sola; la gran mayoria de lo que hace popular a una cancion depende de otros factores.

## 5. Comparacion 2: Popularidad segun tipo de album

Levene dio un estadistico de 52.0346 con p-value = 3.4255e-23, rechazando la igualdad de varianzas entre los tres grupos.

Estadisticas descriptivas:
- album: Media = 55.53 pts, Mediana = 61.00 pts, Desviacion estandar = 22.90
- single: Media = 46.09 pts, Mediana = 51.00 pts, Desviacion estandar = 25.60
- compilation: Media = 40.51 pts, Mediana = 44.00 pts, Desviacion estandar = 21.46

Resultados de las pruebas:
- ANOVA de una via: F = 198.3060, p-value = 5.8560e-85
- Kruskal-Wallis: H = 418.0297, p-value = 1.6827e-91
- Tamano del efecto (eta cuadrado ANOVA): 0.0433
- Tamano del efecto (eta cuadrado Kruskal-Wallis): 0.0474

Interpretacion:
Las canciones que forman parte de un album completo tienen mejor nivel de reproducciones (mediana de 61 puntos), seguidas por los sencillos sueltos (51 puntos), y al final las recopilaciones (44 puntos).

Dado que las varianzas son distintas entre los grupos, la prueba formal que corresponde usar es Kruskal-Wallis. El resultado confirma que las diferencias entre estos tres formatos son veridicas. Aun asi, el tamano del efecto (eta cuadrado de 0.043 a 0.047) es pequeno: el formato del lanzamiento solo explica entre el 4% y el 5% de la popularidad. Ayuda estar dentro de un album, pero casi todo el resultado sigue dependiendo del artista, la cancion y la promocion.

## 6. Comparacion 3: Duracion segun tipo de album

Levene obtuvo un estadistico de 50.0341 con p-value = 2.4748e-22, confirmando varianzas desiguales en la duracion de las pistas.

Estadisticas descriptivas:
- album: Media = 218,189.69 ms (3 min 38 s), Mediana = 214,947.50 ms (3 min 35 s), Desviacion estandar = 64,802.74
- single: Media = 187,759.58 ms (3 min 08 s), Mediana = 183,180.00 ms (3 min 03 s), Desviacion estandar = 49,568.38
- compilation: Media = 214,670.74 ms (3 min 35 s), Mediana = 213,039.50 ms (3 min 33 s), Desviacion estandar = 74,211.84

Resultados de las pruebas:
- ANOVA de una via: F = 199.0495, p-value = 2.8756e-85
- Kruskal-Wallis: H = 583.9101, p-value = 1.6052e-127
- Tamano del efecto (eta cuadrado ANOVA): 0.0434
- Tamano del efecto (eta cuadrado Kruskal-Wallis): 0.0664

Interpretacion:
Los sencillos son claramente mas cortos: duran alrededor de 3 minutos (mediana de 3 minutos con 3 segundos), mientras que las canciones en albumes y recopilaciones rondan los 3 minutos y medio (mediana de 3 minutos con 35 segundos). Son unos 32 segundos de diferencia.

Por la presencia de canciones muy cortas o muy largas y por las varianzas desiguales, la prueba que vale reportar es Kruskal-Wallis.El tamano del efecto (6.64% de varianza explicada) es moderado. Los sencillos se hacen mas breves para captar la atencion, mientras que en un album completo los artistas se toman mas tiempo para desarrollar sus pistas.

## 7. Usos para un artista o productor de musica

Para alguien que hace musica o trabaja con canciones en plataformas digitales:

1. Formato de publicacion: Sacar sencillos funciona muy bien para mantenerse presente, pero a mediano plazo agrupar la musica en un album completo ayuda a que las canciones alcancen mejores numeros de reproduccion.

2. Duracion de la cancion: La duracion que predomina esta en torno a los 3 minutos.

3. Letras explicitas: Aunque los temas explicitos muestran una puntuacion ligeramente mas alta, el efecto es chico.
