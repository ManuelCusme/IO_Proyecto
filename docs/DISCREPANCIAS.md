# Discrepancias de la especificación

## Dependencia pytest-cov (sección 2)

La tabla agrupa pytest y pytest-cov bajo la versión mínima 8.0. Al instalar,
pip informa que pytest-cov solo está disponible hasta 7.1.0 y rechaza >=8.0.
Se usa pytest>=8.0 y pytest-cov>=7.0 para habilitar la cobertura exigida.
No se modifica docs/PROMPT.md.
