# Discrepancias de la especificación

## Dependencia pytest-cov (sección 2)

La tabla agrupa pytest y pytest-cov bajo la versión mínima 8.0. Al instalar,
pip informa que pytest-cov solo está disponible hasta 7.1.0 y rechaza >=8.0.
Se usa pytest>=8.0 y pytest-cov>=7.0 para habilitar la cobertura exigida.
No se modifica docs/PROMPT.md.


## Óptimo múltiple degenerado (secciones 5.4 y 8)

El documento afirma que basta una variable no básica no artificial con Zj−Cj=0
para declarar infinitas soluciones. Es una condición necesaria, pero en bases
degeneradas puede no existir ningún desplazamiento factible positivo.

Caso verificado: max x1 + 0x2, con x1 <= 0, x2 <= 0 y no negatividad.
El criterio del documento indica múltiple por el costo reducido nulo de x2.
Sin embargo, la región solo contiene (0,0), Z=0: scipy.optimize.linprog devuelve
estado 0 y x=(0,0), y la enumeración independiente exacta solo encuentra (0,0).
El método gráfico también devuelve óptimo único.

Se conserva detectar_multiple como filtro de costos reducidos, y se confirma
la multiplicidad buscando un movimiento de longitud positiva o un rayo en la
cara óptima, explorando las bases degeneradas de costo cero. No se alteran las
tablas ni la secuencia de pivotes mostrada. Se añaden regresiones de región
singleton, objetivo nulo y concordancia completa de estados en los casos 2D.
