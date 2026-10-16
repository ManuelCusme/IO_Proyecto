# Informe final — SimplexLab

Fecha: 15 de octubre de 2026 (America/Bogota).

La aplicación está implementada directamente en la raíz del repositorio. Se
completaron las fases 0, 1A, 1B y 2–8 en orden, con puertas de calidad y commits
locales atómicos. No se ejecutó git push ni se reescribió el historial.
`docs/PROMPT.md` y `AGENTS.md` permanecen sin cambios.

## Estado de las fases

| Fase | Estado | Evidencia al cerrar |
|---|---|---|
| 0 — Preparación | Cumple | Python 3.11.0, .venv, estructura y 1 test |
| 1A — Números/modelos | Cumple | 17 tests; NumM y conversión exacta |
| 1B — Simplex | Cumple | 268 tests, tablas Taha, demo y SciPy |
| 2 — Geometría | Cumple | 360 tests; origen, recesión y cruce 2D |
| 3 — Parser | Cumple | 383 tests; variantes y siete ejemplos |
| 4 — GUI base | Cumple | 387 tests; siete ejemplos desde la ventana |
| 5 — Vista Simplex | Cumple | 388 tests; navegación, color y negrita |
| 6 — Vista gráfica | Cumple | 390 tests; canvas y exclusión de 3 variables |
| 7 — Ayuda/UX | Cumple | 391 tests; tres HTML y glosario completo |
| 8 — Extras | Cumple | 426 tests finales; exportación, IA simulada y distribución |

Cada fase tiene su entrada en CHANGELOG.md, guardada en un commit docs propio.
Las correcciones finales incluyen multiplicidad degenerada, selección exclusiva
del método gráfico, fuente portátil y paleta de resultados.

## Criterios de aceptación de la sección 14

### Funcionalidad

| Criterio | Estado | Evidencia |
|---|---|---|
| Wyndor: Z=36, (2,6), tablas 5.8 | Cumple | Comparación exacta de las tres tablas y operaciones |
| Big-M 5.9: Z=12, x2=4 y secuencia | Cumple | Cuatro tablas, eliminación de a1 y empate x1/e1 |
| Mínimos, mixtos e igualdad | Cumple | Siete ejemplos contra SciPy y vértices exactos |
| Todas las tablas y pivotes resaltados | Cumple | Vista con Cj, Cb, base, razones y Zj−Cj; prueba de color/negrita |
| Operaciones y variables entrante/saliente | Cumple | Instantáneas narradas y lista de operaciones por paso |
| Fracciones exactas y M simbólica | Cumple | Fraction y NumM; sin M numérica ni inversión del mínimo |
| Múltiple, no factible, no acotado, degeneración y no activas | Cumple | Casos especiales, regresiones y confirmación exacta de multiplicidad |
| Región, vértices, origen, coordenadas, Z y óptimo | Cumple | Geometría exacta y canvas; origen incluido cuando es factible |
| Gráfico deshabilitado con 3 o más variables | Cumple | Botón, acción y vista deshabilitados, con mensaje exigido |
| Formatos del parser de la sección 7 | Cumple | Regex sin eval; fracciones, decimales, comentarios y ambos lados |
| Tutorial, glosario, acerca de y ejemplos | Cumple | QTextBrowser, F1 y lista por doble clic |
| IA A sin clave; B opcional; revisión humana y secretos protegidos | Cumple | Copiar/pegar, formulario sin autorresolver, QSettings y tests HTTP simulados |

### Calidad

| Criterio | Estado | Evidencia |
|---|---|---|
| pytest completo y cobertura core ≥80% | Cumple | 426 pruebas; cobertura exacta 98,10% |
| Black y Ruff sin errores | Cumple | 47 archivos Python; Ruff incluye E501 (88 columnas) |
| Sin print en core/gui | Cumple | Auditoría AST de producción; solo la demo de consola imprime |
| Humo GUI offscreen | Cumple | Ventana, formulario, tablas, canvas, ayuda e IA |
| SciPy: siete ejemplos + al menos 200 aleatorios | Cumple | 240 PL mixtas, semilla fija, 2–4 variables y 2–5 restricciones |
| Docstrings y type hints en lo público | Cumple | Auditoría AST de la API de core, gui y utils |
| Cálculo matemático sin floats | Cumple | Fraction; conversiones de vértices solo para ordenar/dibujar |

El timeout HTTP `30.0` es infraestructura exigida por 9B.3; no interviene en
aritmética matemática. Las entradas float se convierten mediante su texto,
como exige la sección 4. SciPy y las tolerancias de contraste solo están en tests.

### HCI

| Criterio | Estado | Evidencia |
|---|---|---|
| Validación inmediata, Resolver deshabilitado y tooltips | Cumple | Pruebas de entradas inválidas, formulario dinámico y mensajes |
| Atajos y paleta | Cumple | Ctrl+N/O/S/Z/Y/Q, F1, ←/→/Espacio en vista; colores de pivote y estados |
| Errores presentados sin traceback en la GUI | Cumple | Captura de errores de acciones, hook global y errores IA sanitizados |

La fuente libre DejaVu Sans incluida con Matplotlib se carga explícitamente
para mantener legibilidad incluso cuando Qt offscreen no encuentra fuentes del
sistema. Se inspeccionó una captura de la ventana con Wyndor.

## Verificación independiente y discrepancias

- Los siete valores finales de la sección 11 coinciden con scipy.optimize.linprog
  y la enumeración independiente exacta de vértices 2D.
- Los 240 problemas aleatorios coinciden con SciPy en factibilidad, acotación y Z.
  En dos variables se comparan también vértices y estados con el solver gráfico.
- Las tablas y operaciones de Wyndor y la secuencia Big-M coinciden exactamente.
- Se corrigió el falso positivo de multiplicidad en bases degeneradas: costo
  reducido cero no basta si ningún movimiento positivo es factible. La cara
  óptima se examina sin modificar las tablas didácticas originales.
- `docs/DISCREPANCIAS.md` registra esa corrección y el mínimo inexistente de
  pytest-cov 8.0, sustituido por pytest-cov≥7.0. La especificación no se modificó.

## Salida final de pytest con cobertura

Comando: `python -m pytest -q --cov=core --cov-report=term-missing`.
Entorno: `QT_QPA_PLATFORM=offscreen`, Windows, Python 3.11.0.

```text
........................................................................ [ 16%]
........................................................................ [ 33%]
........................................................................ [ 50%]
........................................................................ [ 67%]
........................................................................ [ 84%]
..................................................................       [100%]
=============================== tests coverage ================================
_______________ coverage: platform win32, python 3.11.0-final-0 _______________

Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
core\__init__.py               0      0   100%
core\casos_especiales.py      49      1    98%   88
core\ejemplos.py               1      0   100%
core\graphic_solver.py        60      0   100%
core\models.py                73      0   100%
core\numeros.py               59      0   100%
core\parser.py                77      3    96%   46, 75-76
core\parser_ia.py             78      1    99%   137
core\report.py               142      5    96%   144, 157, 184-186
core\resultados.py            35      0   100%
core\simplex_solver.py       112      3    97%   43, 190, 227
--------------------------------------------------------
TOTAL                        686     13    98%
Required test coverage of 80.0% reached. Total coverage: 98.10%
426 passed in 25.04s
```

Controles adicionales ejecutados: `python -m black --check .` (47 archivos sin
cambios) y `python -m ruff check .` (All checks passed!). Se verificó además la
sintaxis de SimplexLab.spec y la ausencia de cambios en la especificación.

## Alcance de las comprobaciones

- No se usaron claves reales ni se consultó Gemini. Los tests aíslan QSettings,
  eliminan GEMINI_API_KEY y bloquean urlopen salvo mocks explícitos.
- PDF, LaTeX y Excel se generan en carpetas temporales. Se verifica la cabecera
  PDF, el PDF con gráfico desde la ventana, fracciones LaTeX y reapertura del
  Excel con valor, color y negrita del pivote.
- En este equipo, faulthandler de pytest registra avisos nativos de primera
  oportunidad `0x80040155` al inicializar QPrinter con Qt offscreen. Qt los
  maneja: la suite final termina con código 0 y los PDF se generan. Es una
  observación del entorno de impresión, distinta del aborto de cancelación
  corregido mediante slots encolados y sincronización del cierre del hilo.
- La configuración de PyInstaller está lista y documentada. No se compiló un
  ejecutable, conforme al alcance de la fase 8.
- No hay bloqueos vigentes. No se alcanzó el umbral de tres fallos consecutivos
  del mismo problema que exige detenerse y generar docs/BLOQUEOS.md.

## Ejecutar la aplicación

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Alternativa sin activación: `.\.venv\Scripts\python.exe main.py`.
Si se prepara otro equipo, crear .venv con Python 3.11+ e instalar
`requirements.txt`, como explica README.md. Para abrir la GUI normalmente no
establecer QT_QPA_PLATFORM=offscreen; esa variable se usa en los tests.

La app funciona sin clave. El asistente se configura después desde
Herramientas → Configuración de IA; el modo manual siempre está disponible.
