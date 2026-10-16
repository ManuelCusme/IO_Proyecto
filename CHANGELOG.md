# Registro de cambios

## Fase 0 — Preparación

- Estructura raíz con paquetes core, gui, utils y tests; recursos y ayuda.
- Entorno .venv con Python 3.11, dependencias y configuración de calidad.
- Licencia MIT, README y exclusiones de archivos locales y secretos.
- Prueba de estructura y registro de la discrepancia de versión de pytest-cov.

## Fase 1A — Números y modelos

- NumM inmutable con orden lexicográfico, operaciones y formato simbólico.
- Dataclasses de problemas, restricciones, pasos y resultados.
- Puerta de calidad: 17 tests; black y ruff sin errores.

## Fase 1B — Simplex Gran M

- Convención Zj − Cj, minimización directa y M simbólica.
- Tablas completas, operaciones narradas, Bland en empates y eliminación de artificiales.
- Casos especiales separados y demo de consola compatible con Windows.
- Puerta: 268 tests; 7 ejemplos y 240 aleatorios contra SciPy; tablas Taha exactas;
  enumeración independiente de vértices 2D; demo, black y ruff correctos.

## Fase 2 — Núcleo gráfico

- Intersecciones exactas, ejes explícitos y cono de recesión homogéneo.
- Regiones infinitas con óptimo finito, segmentos y semirrectas óptimas.
- Recorte solo visual y orden antihorario de vértices.
- Puerta: 360 tests; Wyndor con origen y cruce aleatorio 2D; black y ruff correctos.

## Fase 3 — Parser y ejemplos

- Regex y Fraction para expresiones a ambos lados, formatos alternativos y comentarios.
- Mensajes de sintaxis en español, leyenda de variables y siete ejemplos precargados.
- Puerta: 383 tests; ejemplos parseados y resueltos; black y ruff correctos.
