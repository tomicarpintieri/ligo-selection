# Memoria final — sesgo de selección en detecciones de ondas gravitacionales

## Pregunta

Una detección de LIGO no es una muestra neutral de las fusiones que ocurren en
el universo. La distancia, la masa, la orientación y la posición en el cielo
cambian la probabilidad de que una señal supere el umbral de detección. Este
proyecto cuantifica las piezas principales de ese sesgo con datos de GW150914 y
una red de dos detectores.

## Método

El análisis parte de los datos públicos de H1 y L1, verificados contra hashes
SHA-256. Se estima una PSD con Welch mediano, se aplica filtrado adaptado y se
usa una forma de onda TaylorF2 no giratoria: amplitud a orden 0PN y fase a
3.5PN. El horizonte se calcula a partir de la SNR, y la respuesta angular se
obtiene con los patrones de antena de un interferómetro en L. Finalmente se
incorporan las posiciones de H1 y L1, el tiempo sideral y el retardo geométrico
entre sitios.

## Resultados principales

- El control recupera GW150914 con SNR 19.81 en H1 y 13.54 en L1; L1 llega
  7.08 ms antes.
- La forma de onda propia coincide con la referencia LAL con match 1.000. Su
  exponente de amplitud respecto de la masa chirp se midió como 0.83333.
- Para GW150914, el horizonte óptimo calculado es 1969.9 Mpc y el volumen
  euclídeo correspondiente es 32.02 Gpc³.
- El promedio sobre orientación y cielo reduce el rango respecto del horizonte
  por un factor 2.2649. Un detector individual tiene cuatro direcciones ciegas.
- La respuesta conjunta H1–L1 cubre esos puntos ciegos de forma complementaria.
  El máximo tiempo de vuelo geométrico calculado con coordenadas de LIGO y
  WGS84 es 10.013 ms.
- El piloto de inyecciones H1–L1 recupera el 39.6 % de 96 fuentes inyectadas,
  frente a 4.2 % de cruces por encima del umbral en el control sin inyección.
  La eficiencia se registra por distancia en `figures/f07_injection_efficiency.png`.

## Validación y reproducibilidad

Todos los resultados se regeneran desde los datos de entrada hasheados. Los
tests verifican el control de GW150914, la comparación contra LAL, escalas de
amplitud y horizonte, promedios analíticos del patrón de antena, tiempo sideral,
retardos de red, procedencia de números y figuras, y la página pública. Al
cierre de esta memoria, la suite completa tiene 55 tests aprobados.

La procedencia de cada número y figura está en `provenance/numbers.json` y
`provenance/claims.yaml`. La reproducción completa se ejecuta con:

```powershell
.venv\Scripts\python.exe scripts\reproduce.py
```

## Límites y trabajo futuro

TaylorF2 describe solamente el inspiral. Para sistemas pesados como GW150914
subestima la detectabilidad porque no incluye la fusión y el ringdown. El
volumen reportado es euclídeo. El piloto de inyecciones usa esa forma de onda
SPA y una SNR de red en cuadratura, por lo que no es todavía una campaña IMR ni
una búsqueda coherente.

El siguiente paso es reemplazar el piloto por formas de onda IMR para una grilla
de masas, calibrar el umbral con una tasa de falsos positivos más grande y usar
una estadística coherente. Esa campaña permitiría convertir esta base validada
en una función de selección directamente utilizable para inferencia de
poblaciones.
