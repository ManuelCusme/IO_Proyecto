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

## Fase 4 — GUI base

- Formulario dinámico con validación, tooltips y campos exactos.
- Ventana 1200×800, resultados, historial y archivos locales de problemas.
- Ejemplos por doble clic, selección de método, tema y barra de estado.
- Navegación temporizada reutilizable y punto de entrada con manejo amigable de errores.
- Puerta: 387 tests; siete ejemplos resueltos desde la ventana offscreen;
  edición, historial y archivos verificados; black y ruff correctos.

## Fase 5 — Vista Simplex

- Tablas con Cj, Base, Cb, razones y Zj − Cj; M simbólica y fracciones exactas.
- Columna azul, fila verde y pivote amarillo en negrita; narrativa y operaciones.
- Anterior/siguiente, reproducción a 1,5 segundos y atajos contextuales.
- Puerta: 388 tests, navegación de Wyndor con colores y negrita; black y ruff correctos.

## Fase 6 — Vista gráfica

- Canvas Matplotlib y toolbar para zoom, desplazamiento y guardado de imagen.
- Rectas etiquetadas, región sombreada, vértices azules con fracciones y Z.
- Óptimos rojos, segmentos múltiples y tooltip de vértices.
- Desactivación explícita para dimensiones distintas de dos y selección de método.
- Puerta: 390 tests, cinco vértices y un óptimo en Wyndor; black y ruff correctos.
