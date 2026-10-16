# PROMPT MAESTRO (v2, corregido): SimplexLab

**Solver de Programación Lineal con Método Gráfico y Simplex Gran M**

> **Instrucción para el agente de código que recibe este documento (Codex u otro):**
> Este documento es la especificación completa y autocontenida de un proyecto. Tú trabajas **directamente sobre el repositorio**: creas los archivos, ejecutas los comandos y corriges lo que falle. Debes construir **todo el proyecto, de la Fase 0 a la Fase 8, en una sola sesión y sin esperar confirmación**, pero **no puedes avanzar de fase si la puerta de calidad de la fase actual no pasa** (sección 13). Sigue **exactamente** estas especificaciones, sin omitir módulos ni simplificar la lógica. Si algo no está especificado, elige la opción más pedagógica y coherente con el resto del documento.

---

## 0. MODO DE TRABAJO (AGENTE DE CÓDIGO)

1. **Este archivo vive en `docs/PROMPT.md` y es de solo lectura.** No lo modifiques. Si detectas un error en él, regístralo en `docs/DISCREPANCIAS.md` (ver regla 6).
2. **Escribe los archivos directamente en el repositorio** (nada de "pegar código"). Crea y activa un entorno virtual `.venv` e instala dependencias con `pip`.
3. **Ejecuta tú mismo** `pytest`, `black` y `ruff` al terminar cada fase y corrige hasta que pasen. No declares una fase terminada sin haber visto los comandos en verde.
4. **Commits atómicos.** El repositorio está conectado a un remoto, así que el historial debe ser limpio y legible:
   - Cada commit contiene **un solo cambio lógico** y deja el proyecto en un estado coherente (el código del commit y sus tests van juntos; no mezcles cambios no relacionados).
   - Antes de cada commit, ejecuta `pytest -q`, `black --check .` y `ruff check .` sobre lo que cambiaste; no hagas commits que dejen los tests en rojo.
   - Mensajes en formato **Conventional Commits**, en español, en imperativo y sin punto final: `feat(core): agrega clase NumM con comparación lexicográfica`, `test(simplex): cubre el ejemplo Wyndor`, `fix(graphic): incluye el origen entre los vértices`, `docs: actualiza el README`. Tipos permitidos: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `style`.
   - Unidades típicas de commit: un módulo con sus tests, una corrección, una vista de la GUI, un archivo de documentación, la configuración de herramientas. Evita commits gigantes de "toda la fase".
   - Actualiza `CHANGELOG.md` en un commit `docs` propio al cerrar cada fase.
   - **No hagas `git push`, `git reset --hard`, `git rebase`, ni reescribas el historial.** Solo `git add` selectivo y `git commit` locales; el usuario decide cuándo subir los cambios. Nunca uses `git add .` a ciegas: revisa con `git status` que no entren `.venv/`, claves ni archivos de configuración local.
5. **Sin red** salvo `pip install` de las dependencias listadas. Los **tests nunca deben usar internet ni claves reales**: todo acceso a la API de Gemini se simula (mock). No uses servicios de pago. La única llamada de red del programa final es la del asistente de IA opcional (sección 9B), y solo cuando el usuario la dispara.
6. **Verificación independiente.** Los resultados de referencia de este documento se calcularon a mano y no se ejecutaron. Si tu código y el documento difieren:
   - Los **valores finales** (Z, solución) se validan contra `scipy.optimize.linprog` (solo en tests) y contra enumeración exhaustiva de vértices en 2 variables.
   - Las **tablas intermedias** deben seguir las reglas de la sección 5.3.
   - Si el documento resulta equivocado, **no fuerces el código para que coincida**: usa el valor verificado, corrige el test y anota el caso en `docs/DISCREPANCIAS.md` (qué decía el documento, qué obtuviste y cómo lo verificaste).
7. **Si una puerta de calidad falla 3 veces seguidas** con el mismo problema, detente, escribe el estado en `docs/BLOQUEOS.md` (qué intentaste, el error exacto y tu hipótesis) y termina con un informe. No pases a la siguiente fase con una puerta en rojo.
8. **Tests de GUI sin pantalla:** usa `QT_QPA_PLATFORM=offscreen` para que los tests de humo funcionen en entornos sin display.
9. **Informe final:** al terminar, deja `docs/INFORME_FINAL.md` con el estado de cada criterio de la sección 14 (cumple / no cumple / parcial), la salida de `pytest --cov`, y cómo ejecutar la app.

---

## 1. CONTEXTO Y OBJETIVO

### 1.1 Qué es SimplexLab

Aplicación de escritorio para resolver problemas de **Programación Lineal (PL)** continua con dos métodos:

1. **Método Gráfico**: solo para problemas con **exactamente 2 variables**. Se dibuja siempre en un plano cartesiano x₁–x₂. Muestra la región factible sombreada, los vértices con sus coordenadas y Z, y el punto óptimo resaltado. No hay iteraciones de líneas de nivel: solo el resultado final.
2. **Método Simplex con Gran M (Big-M)**: para 1 o más variables (se probará hasta 3 o 4) y cualquier combinación de restricciones `<=`, `>=`, `=`. Muestra **cada tabla**, resalta columna, fila y elemento pivote, indica qué variable entra y cuál sale, y narra las **operaciones elementales entre filas**.

Es una **herramienta académica** para estudiantes de Investigación de Operaciones, por eso:

- Los números se muestran en **fracciones exactas**, nunca en decimales aproximados.
- El paso a paso es **automático y explicativo**, no solo tablas crudas.
- Se manejan los **casos especiales** para que la app nunca dé resultados erróneos ni se caiga.

### 1.2 Referencia bibliográfica y convención

**Libro guía:** Taha, Hamdy A., *Investigación de Operaciones*, 9.ª edición.

**Convención de la fila objetivo: `Zj − Cj`** (fija, no configurable en esta versión).

| Sentido | Variable que entra | Criterio de parada (óptimo) |
|---|---|---|
| **Maximizar** | la de `Zj − Cj` **más negativo** | todos los `Zj − Cj ≥ 0` |
| **Minimizar** | la de `Zj − Cj` **más positivo** | todos los `Zj − Cj ≤ 0` |

**Importante (cambio respecto a la v1):** la minimización **no** se convierte a maximización. Se resuelve directamente invirtiendo el criterio de optimalidad, como hace Taha. Así las tablas coinciden con las del libro y los tests contra Taha son válidos.

- Costo de las artificiales en el Big-M: **−M** si se maximiza, **+M** si se minimiza.
- `Z` final se lee directamente de la última celda de la fila `Zj − Cj`. No hay cambios de signo.

### 1.3 Alcance

**Dentro del alcance**

- Maximización y minimización.
- Restricciones `<=`, `>=`, `=`, incluso mezcladas.
- Todas las variables son **no negativas** (`xᵢ ≥ 0`). Esto debe indicarse en la interfaz.
- Fracciones exactas con `fractions.Fraction` (biblioteca estándar).
- Big-M **simbólica**: M se trata como "infinitamente grande", nunca como un número concreto.
- Detección de casos especiales: óptimo múltiple, no factible, no acotado, degeneración, restricciones no activas.
- Interfaz de escritorio con menú de ayuda, glosario y tutorial.
- Exportación a PDF (fase final).
- Asistente de IA **opcional** (fase final) que convierte un enunciado en párrafo a función objetivo y restricciones, con dos modos: **A) manual**, sin clave ni red (copiar prompt / pegar respuesta), y **B) automático** con la API gratuita de **Google Gemini** (sección 9B).

**Fuera del alcance (NO implementar)**

- Simplex Dual y Método de las Dos Fases.
- Análisis de sensibilidad.
- Programación entera.
- Gráfico 3D. Si el usuario elige el método gráfico con 3 o más variables, mostrar el mensaje: *"El método gráfico solo aplica a problemas de 2 variables."* y deshabilitar esa vista.
- Variables libres (sin restricción de signo).
- Cualquier dependencia de pago o API de pago.

---

## 2. STACK TECNOLÓGICO

| Capa | Tecnología | Versión mín. | Motivo |
|---|---|---|---|
| Lenguaje | Python | 3.11 | Tipado moderno |
| GUI | PySide6 (Qt6) | 6.6 | Multiplataforma, widgets ricos |
| Aritmética exacta | `fractions.Fraction` | stdlib | Sin dependencias, rápido |
| Gráficos | Matplotlib | 3.8 | Canvas embebible en Qt |
| Excel (fase 8) | openpyxl | 3.1 | Exportar pasos |
| Tests | pytest, pytest-cov | 8.0 | Estándar |
| Verificación cruzada (**solo tests**) | scipy | 1.11 | Contrastar el Simplex con `linprog` |
| Formato / linter | black, ruff | 24.0 / 0.4 | Estilo uniforme |
| Empaquetado | PyInstaller | 6.x | `.exe` para Windows |
| IA opcional, modo B | API REST de Google Gemini (capa gratuita) vía `urllib` (stdlib) | n/a | Gratis, sin dependencias extra |

- **No se usa SymPy** en el núcleo: la M se modela con una clase propia (sección 5.1), que es más simple, más rápida y evita errores de simplificación simbólica.
- `scipy` va **únicamente** en `requirements-dev.txt` y se usa solo en tests; el programa final no depende de él.
- Todo funciona **sin internet**, excepto la descarga inicial de dependencias y el modo B del asistente de IA (Gemini).
- El PDF se genera con `QTextDocument` + `QPrinter` (ya incluidos en PySide6), así que no hace falta ReportLab.

---

## 3. ARQUITECTURA

### 3.1 Principio rector

> **`core/` no importa NADA de `gui/`.**

Toda la lógica matemática vive en `core/` y se prueba con pytest sin abrir ninguna ventana. La GUI es una capa delgada que solo consume resultados de `core/`.

### 3.2 Estructura de carpetas

La raíz del proyecto es **la carpeta del repositorio en la que ya estás** (por ejemplo `IO_Proyecto`). Crea `core/`, `gui/`, `tests/`, etc. directamente en ella, sin anidar otra carpeta con el nombre del proyecto. "SimplexLab" es solo el nombre de la aplicación (título de la ventana, README, `pyproject.toml`); el nombre de la carpeta es irrelevante para el código.

```
<raíz del repositorio>/   # carpeta actual del repo (p. ej. IO_Proyecto); NO crees una subcarpeta extra
├── core/
│   ├── __init__.py
│   ├── numeros.py           # Clase NumM (a·M + b) y utilidades de Fraction
│   ├── models.py            # Dataclasses: Restriccion, Problema, PasoSimplex, Resultados
│   ├── parser.py            # Texto → Problema (regex, sin eval)
│   ├── parser_ia.py         # Prompt (modo A) + cliente Gemini (modo B), fase 8
│   ├── graphic_solver.py    # Método gráfico 2D
│   ├── simplex_solver.py    # Simplex con Gran M
│   ├── casos_especiales.py  # Funciones de detección
│   ├── report.py            # Exportar PDF / LaTeX / Excel
│   └── ejemplos.py          # Problemas precargados
├── gui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── problem_panel.py
│   ├── ai_panel.py          # Asistente IA, modos A y B (fase 8, opcional)
│   ├── ai_settings_dialog.py # Clave y modelo de Gemini (fase 8)
│   ├── graphic_view.py
│   ├── simplex_view.py
│   ├── steps_bar.py
│   ├── resultado_panel.py
│   └── help/
│       ├── tutorial.html
│       ├── glosario.html
│       └── sobre.html
├── utils/
│   ├── __init__.py
│   ├── formato.py           # Fraction/NumM → texto ("3/2", "-M - 3")
│   └── logging_setup.py
├── tests/
│   ├── __init__.py
│   ├── casos_taha.py
│   ├── test_numeros.py
│   ├── test_models.py
│   ├── test_simplex.py
│   ├── test_graphic.py
│   ├── test_parser.py
│   └── test_parser_ia.py
├── resources/ (icons/, styles/)
├── main.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## 4. MÓDULO `core/models.py`

Dataclasses **sin lógica de cálculo**. Todo número es `Fraction`; los strings, ints y floats se convierten en `__post_init__` (los floats vía `Fraction(str(x))` para no arrastrar error binario).

### 4.1 `Restriccion`

```python
@dataclass
class Restriccion:
    coefs: list[Fraction]            # coeficientes de las variables originales
    tipo: Literal["<=", ">=", "="]
    rhs: Fraction                    # se conserva TAL CUAL lo ingresó el usuario
```

La normalización (RHS ≥ 0) se hace en el solver sobre una **copia**; la restricción original no se modifica, para poder mostrarla en reportes.

### 4.2 `Problema`

```python
@dataclass
class Problema:
    sentido: Literal["max", "min"]
    coef_obj: list[Fraction]
    restricciones: list[Restriccion]
    nombres: list[str] = field(default_factory=list)   # por defecto x1..xn
```

Validaciones en `__post_init__`: al menos 1 variable y 1 restricción; todas las restricciones con la misma cantidad de coeficientes que `coef_obj`; `nombres` sin repetidos. Lanzar `ValueError` con mensajes claros.

### 4.3 `PasoSimplex`

Una iteración completa, con todo lo necesario para reproducirla visualmente:

```python
@dataclass
class PasoSimplex:
    numero: int                       # 0, 1, 2, ...
    encabezados: list[str]            # ["x1","x2","s1","s2","s3","b"]
    base: list[str]                   # variable básica por fila de restricción
    cb: list[NumM]                    # costo de cada básica
    cj: list[NumM]                    # costos Cj por columna de variable
    tabla: list[list[Fraction]]       # filas de restricciones (incluye columna b)
    fila_z: list[NumM]                # fila Zj−Cj (incluye Z en la última celda)
    col_pivote: int | None
    fila_pivote: int | None
    elemento_pivote: Fraction | None
    entra: str | None
    sale: str | None
    razones: list[Fraction | None]    # bi/aij; None donde aij ≤ 0
    operaciones: list[str]            # ["F2 ← F2 / (2)", "F3 ← F3 − (2)·F2", ...]
    mensaje: str                      # narrativa del paso
    z: NumM                           # valor de Z en esta tabla
    advertencias: list[str]           # p. ej. "empate en razón mínima"
```

### 4.4 `ResultadoSimplex`

```python
@dataclass
class ResultadoSimplex:
    pasos: list[PasoSimplex]
    estado: Literal["optimo", "multiple", "no_factible", "no_acotado"]
    degenerado: bool                          # bandera independiente del estado
    z: Fraction | None
    solucion: dict[str, Fraction] | None      # incluye holguras y excesos
    advertencias: list[str]
```

**Cambio respecto a la v1:** "degenerado" **no es un estado**, es una bandera. Un problema puede ser óptimo y degenerado a la vez.

### 4.5 `ResultadoGrafico`

```python
@dataclass
class ResultadoGrafico:
    vertices: list[tuple[Fraction, Fraction]]
    valores_z: list[Fraction]
    optimos: list[tuple[Fraction, Fraction]]     # 1 vértice, o 2+ si es múltiple
    z_optimo: Fraction | None
    estado: Literal["optimo", "multiple", "no_factible", "no_acotado"]
    region_acotada: bool
    rectas: list[dict]                           # info de cada restricción para dibujar
    region: list[tuple[float, float]]            # polígono (floats solo para graficar)
    advertencias: list[str]
```

---

## 5. MÓDULO `core/simplex_solver.py` (el corazón)

### 5.1 Números con M: clase `NumM` (en `core/numeros.py`)

Todo número de la forma `a·M + b` con `a, b: Fraction`.

```python
@dataclass(frozen=True)
class NumM:
    m: Fraction = Fraction(0)    # coeficiente de M
    c: Fraction = Fraction(0)    # parte constante
```

Requisitos:

- `+`, `−`, negación, y **multiplicación por `Fraction`** (NumM × Fraction → NumM). No hace falta NumM × NumM: en las tablas, las filas de restricciones son `Fraction` puras y solo la fila `Zj − Cj`, `Cb` y `Cj` contienen M.
- Comparación **lexicográfica**, que interpreta M → +∞: primero se compara `m`, y si son iguales, `c`. Ejemplo: `−M − 100 < −3` es verdadero.
- `es_cero()`, `es_negativo()`, `es_positivo()` con la misma regla (el signo lo decide `m`; si `m == 0`, el signo lo decide `c`).
- `__str__` legible: `"-3M - 3"`, `"M + 1"`, `"3/2"`, `"-M"`, `"0"` (usado por `utils/formato.py`).
- Tests unitarios en `tests/test_numeros.py` (comparación, suma, resta, formato).

### 5.2 Construcción de la forma aumentada

**Paso 1: normalizar RHS.** Sobre una copia, si una restricción tiene `rhs < 0`, multiplicarla por −1 e invertir el sentido (`<=` ↔ `>=`; `=` se mantiene).

**Paso 2: variables añadidas.** Contadores independientes para cada tipo.

| Tipo (tras normalizar) | Se añade | Costo Cj en Z (max) | Costo Cj en Z (min) |
|---|---|---|---|
| `<=` | holgura `sᵢ` (+1) | 0 | 0 |
| `>=` | exceso `eᵢ` (−1) **y** artificial `aᵢ` (+1) | 0 y **−M** | 0 y **+M** |
| `=` | artificial `aᵢ` (+1) | **−M** | **+M** |

Orden de columnas: variables originales, holguras, excesos, artificiales, y al final `b`.

**Paso 3: tabla inicial.** La base inicial son las holguras (de las `<=`) y las artificiales (de las `>=` y `=`).

Fila objetivo:

```
Zj = Σ (Cb_i · fila_i[j])      Zj − Cj      (para cada columna j)
Z  = Σ (Cb_i · b_i)            (última celda)
```

No hace falta "limpiar" la M de las artificiales con operaciones previas: el cálculo directo de `Zj` con `Cb = ∓M` ya lo resuelve, y se muestra tal cual en la tabla 0.

### 5.3 Iteración (repetir hasta terminar)

1. **Criterio de entrada (columna pivote).** Entre las columnas de variables (no `b`):
   - `max`: la de `Zj − Cj` **más negativo**; si no hay negativos → óptimo.
   - `min`: la de `Zj − Cj` **más positivo**; si no hay positivos → óptimo.
   - Empate: la de menor índice de columna (regla de Bland).

2. **Criterio de salida (fila pivote).** Razón `bᵢ / aᵢ,col` **solo si** `aᵢ,col > 0`. Se elige la menor.
   - Si ninguna fila tiene `aᵢ,col > 0` → **NO ACOTADO**, terminar.
   - Si hay **empate** en la razón mínima: se agrega la advertencia *"Empate en la razón mínima: la siguiente solución será degenerada"*, se marca `degenerado = True` y se desempata eligiendo la fila cuya variable básica tenga menor índice de columna.

3. **Registrar el paso** antes de pivotear (tabla actual, pivote, entra/sale, razones, Z, narrativa).

4. **Pivoteo.** Operaciones registradas **en texto** en este formato (la `F` es la fila de la tabla, la fila Z se numera al final):

   ```
   F2 ← F2 / (2)
   F3 ← F3 − (2)·F2
   FZ ← FZ − (−5)·F2
   ```

   - `F_pivote ← F_pivote / pivote`.
   - Para cada otra fila (incluida la de Z) con `factor ≠ 0`: `F_i ← F_i − factor·F_pivote`.
   - Si `factor == 0`, **no se registra** esa operación (queda "sin cambio"), para no llenar el paso de ruido.

5. **Actualizar la base**: la variable que entra reemplaza a la que sale; actualizar `Cb`.

6. **Artificiales que salen de la base:** su columna se **elimina** de las tablas siguientes (como en Taha) y se avisa en la narrativa: *"a₁ salió de la base; su columna ya no se necesita."*

7. **Protección contra ciclado:** constante `MAX_ITER = 100`. Si se supera, terminar con un error controlado y mensaje claro (no excepción sin capturar). Aclarar en la documentación que Bland solo se usa en desempates, así que esta cota es una red de seguridad.

### 5.4 Análisis del resultado final

Al llegar a una tabla óptima:

1. Si alguna **artificial permanece en la base con valor > 0** → **NO FACTIBLE**.
2. Si una artificial permanece en la base con valor **= 0** → solución válida, con advertencia *"Artificial en la base con valor 0 (solución degenerada)"* y `degenerado = True`.
3. Si todo está limpio: buscar variables **no básicas, que no sean artificiales,** con `Zj − Cj = 0`.
   - Si existe alguna → **ÓPTIMO MÚLTIPLE** (advertencia: *"Existen infinitas soluciones óptimas"*).
   - Si no → **ÓPTIMO ÚNICO**.
4. Si alguna variable **básica** vale 0 en la solución final → `degenerado = True` con advertencia.

### 5.5 Extracción de la solución

- Variable básica: valor = `b` de su fila. No básica: 0.
- `Z` = última celda de la fila `Zj − Cj`. Para un problema factible su parte `m` debe ser 0; si no lo fuera, es un error interno: lanzar una excepción propia (`ErrorInterno`) con mensaje claro.

### 5.6 Restricciones no activas (reemplaza el "redundante" de la v1)

Para cada restricción original, mirar su holgura/exceso en el óptimo:

- `<=` con holgura **> 0** o `>=` con exceso **> 0** → la restricción **no está activa** (no limita la solución óptima). Se informa como advertencia: *"La restricción R1 no está activa (holgura = 2)."*
- **No** se la llama "redundante": una restricción redundante es una que se puede eliminar sin cambiar la región factible, y eso es una propiedad distinta.

### 5.7 Firma

```python
def resolver_simplex(problema: Problema) -> ResultadoSimplex:
    """Resuelve un problema de PL con Simplex Gran M.

    Raises:
        ValueError: si el problema no tiene variables o restricciones.
    """
```

### 5.8 Ejemplo trabajado de referencia: Wyndor Glass

```
max Z = 3x1 + 5x2
s.a.   x1          <= 4
            2x2    <= 12
       3x1 + 2x2   <= 18
```

**Tabla 0.** Base: s1, s2, s3. Fila Zj − Cj = [−3, −5, 0, 0, 0 | 0].

| Base | Cb | x1 | x2 | s1 | s2 | s3 | b |
|---|---|---|---|---|---|---|---|
| s1 | 0 | 1 | 0 | 1 | 0 | 0 | 4 |
| s2 | 0 | 0 | **2** | 0 | 1 | 0 | 12 |
| s3 | 0 | 3 | 2 | 0 | 0 | 1 | 18 |
| Zj−Cj | | −3 | **−5** | 0 | 0 | 0 | 0 |

- **Entra x₂** (−5, el más negativo).
- Razones: s1: no aplica (a = 0); s2: 12/2 = **6**; s3: 18/2 = 9. **Sale s₂.** Pivote = 2.
- Operaciones: `F2 ← F2 / (2)`, `F3 ← F3 − (2)·F2`, `FZ ← FZ − (−5)·F2`.

**Tabla 1:** Z = 30. Fila Zj − Cj = [−3, 0, 0, 5/2, 0 | 30]. **Entra x₁**; razones: s1: 4/1 = 4; x2: no aplica; s3: 6/3 = **2**. **Sale s₃.** Pivote = 3.
Operaciones: `F3 ← F3 / (3)`, `F1 ← F1 − (1)·F3`, `FZ ← FZ − (−3)·F3`.

**Tabla 2 (óptima):** fila Zj − Cj = [0, 0, 0, 3/2, 1 | 36]. **Z\* = 36, x₁ = 2, x₂ = 6, s₁ = 2, s₂ = 0, s₃ = 0.** Iteraciones: 2. Óptimo único. La restricción R1 no está activa (s₁ = 2).

Este ejemplo debe reproducirse **exactamente** en `tests/test_simplex.py`.

### 5.9 Ejemplo con Big-M (para tests)

```
max Z = 2x1 + 3x2
s.a.   x1 +  x2 <= 4
       x1 + 3x2 >= 6
```

Columnas: x1, x2, s1, e1, a1, b. **Resultado: Z\* = 12, x₁ = 0, x₂ = 4, estado óptimo.**

Secuencia esperada:

1. Tabla 0: `Zj − Cj` = [−M−2, −3M−3, 0, M, 0 | −6M]. Entra x₂, sale a₁ (razones 4 y 2). Se elimina la columna a₁.
2. Tabla 1: `Zj − Cj` = [−1, 0, 0, −1 | 6]. **Empate** en −1 entre x₁ y e₁: por Bland entra **x₁**. Sale s₁ (razón 3 contra 6).
3. Tabla 2: Z = 9 en (3, 1). Entra e₁, sale x₁.
4. Tabla 3 (óptima): Z = 12, x₂ = 4, e₁ = 6, x₁ = 0.

Este ejemplo prueba a la vez la M simbólica, la eliminación de la artificial y el desempate de Bland.

---

## 6. MÓDULO `core/graphic_solver.py`

Solo para problemas de **exactamente 2 variables**. Todo el cálculo es **exacto** (`Fraction`); solo la región para dibujar se convierte a `float`. **No se usan tolerancias numéricas.**

### 6.1 Algoritmo

1. **Conjunto de rectas.** Cada restricción `a·x₁ + b·x₂ {≤,≥,=} c` aporta la recta `a·x₁ + b·x₂ = c`. **Se añaden explícitamente** las rectas `x₁ = 0` y `x₂ = 0` (no negatividad). Esto es lo que garantiza que vértices como (0, 0) aparezcan; la v1 los perdía.
2. **Intersecciones.** Para cada par de rectas con determinante ≠ 0, resolver el sistema 2×2 con fracciones.
3. **Factibilidad exacta.** Un punto es factible si cumple **todas** las restricciones y `x₁ ≥ 0`, `x₂ ≥ 0` (comparaciones exactas).
4. **Eliminar duplicados** (comparación exacta de pares de `Fraction`).
5. **Ordenar** los vértices en sentido antihorario alrededor de su centroide (usando `atan2` en float solo para ordenar) para poder dibujar el polígono.
6. **Evaluar Z** en cada vértice.

### 6.2 Casos especiales

- **No factible:** no hay ningún vértice factible. (Con `x ≥ 0` incluido, una región factible no vacía siempre tiene al menos un vértice.)
- **No acotado:** la región tiene una dirección infinita `d` en la que Z mejora. Detección exacta:
  1. Direcciones candidatas: los dos sentidos del vector director de **cada** recta del conjunto (restricciones y ejes).
  2. `d` es **dirección de recesión** si cumple las restricciones homogéneas: `a·d₁ + b·d₂ ≤ 0` en las `<=`, `≥ 0` en las `>=`, `= 0` en las `=`, y `d₁ ≥ 0`, `d₂ ≥ 0`.
  3. Si existe una `d` de recesión con `c·d > 0` (max) o `c·d < 0` (min) → **NO ACOTADO**.
  4. Si hay `d` de recesión con `c·d = 0` y el óptimo está en un vértice, el óptimo es **múltiple con una semirrecta de soluciones** (informar con advertencia).
- **Óptimo múltiple:** dos o más vértices con el mismo Z óptimo (todo el segmento entre ellos es óptimo).
- **Región no acotada pero con óptimo:** es válido; para dibujar se limita el rango de los ejes a un valor razonable (1,5 × la mayor coordenada de los vértices, mínimo 10).

### 6.3 Firma y ejemplo

```python
def resolver_grafico(problema: Problema) -> ResultadoGrafico:
    """Resuelve por método gráfico un problema de exactamente 2 variables.

    Raises:
        ValueError: si el problema no tiene exactamente 2 variables.
    """
```

Para Wyndor, vértices esperados:

```
(0, 0) → Z = 0
(4, 0) → Z = 12
(4, 3) → Z = 27
(2, 6) → Z = 36   ← ÓPTIMO
(0, 6) → Z = 30
```

---

## 7. MÓDULO `core/parser.py`

Convierte texto del usuario a `Problema`. **No usa `eval` ni `sympify`**: se implementa con expresiones regulares y `Fraction`, que es más predecible con casos como `3x1`.

### 7.1 Formatos aceptados

```
max 3x1 + 5x2
s.a.
x1 <= 4
2x2 <= 12
3x1 + 2x2 <= 18
```

```
max Z = 3x1 + 5x2
sujeto a:
    x1       <= 4
    3x1+2x2  <= 18
    x1, x2 >= 0
```

### 7.2 Reglas

- Primera línea no vacía: empieza con `max`, `maximizar`, `min` o `minimizar` (sin distinguir mayúsculas). El resto es la función objetivo; se acepta el prefijo opcional `Z =`.
- Marcador de restricciones: `s.a.`, `s.a`, `sujeto a`, `sujeto a:`, `subject to`, `st`.
- Operadores: `<=`, `>=`, `=`, `≤`, `≥`, `==` (este último equivale a `=`).
- Términos: `3x1`, `-x2`, `2*x1`, `0.5x1`, `3/2x1`, `x` o `y` o `z`. Coeficientes enteros, decimales o fracciones.
- **Términos a ambos lados** del operador: se pasan las variables a la izquierda y las constantes a la derecha.
- Líneas de no negatividad (`x1, x2 >= 0`, `x1 >= 0`) se **detectan y se ignoran** (siempre se asume `x ≥ 0`).
- Las líneas que empiezan con `#` son **comentarios**: el parser las ignora, pero `extraer_leyenda` las devuelve para que la GUI muestre qué significa cada variable (por ejemplo `# x1 = mesas a fabricar`).
- Variables: se ordenan por aparición en la función objetivo; si no aparecen ahí, por orden alfabético/numérico (`x1, x2, ..., x10`). Una variable que no aparezca en una restricción lleva coeficiente 0.

### 7.3 Errores (clase `ParseError`, mensajes en español y claros)

- `"No se encontró el sentido (max/min) en la primera línea."`
- `"La función objetivo no contiene variables reconocibles."`
- `"Falta la línea 's.a.' o 'sujeto a:'."`
- `"Restricción #2: falta el operador (<=, >=, =)."`
- `"Restricción #3: no se pudo interpretar '3x1 +* 2'."`

### 7.4 Firma

```python
class ParseError(Exception):
    """Error de sintaxis al parsear el problema."""

def parsear_problema(texto: str) -> Problema: ...

def extraer_leyenda(texto: str) -> list[str]:
    """Devuelve las líneas de comentario (sin el '#') en el orden en que aparecen."""
```

---

## 8. MÓDULO `core/casos_especiales.py`

Funciones puras, pequeñas y testeables (el solver las usa; se mantienen separadas por claridad):

```python
def detectar_multiple(fila_z, encabezados, base) -> bool:
    """True si hay una variable no básica y no artificial con Zj−Cj = 0."""

def detectar_no_factible(base, valores_b) -> bool:
    """True si una artificial está en la base con valor > 0."""

def detectar_no_acotado(columna_pivote) -> bool:
    """True si ningún aij > 0 en la columna pivote."""

def detectar_empate_razon(razones) -> bool:
    """True si hay empate en la razón mínima (posible degeneración)."""

def aplicar_bland(filas_empatadas, base, indices_columna) -> int:
    """Desempata eligiendo la fila cuya variable básica tiene menor índice."""

def restricciones_no_activas(problema, solucion) -> list[tuple[int, Fraction]]:
    """Restricciones originales con holgura/exceso > 0 en el óptimo."""
```

---

## 9. MÓDULO `core/report.py` (fase 8)

- **PDF:** `QTextDocument` + `QPrinter`. Incluye enunciado, método aplicado, cada tabla (con pivote marcado), operaciones por paso y resultado final. Para el método gráfico, la imagen del canvas.
- **LaTeX:** `.tex` con `amsmath`, tablas con `tabular`, fracciones con `\frac{a}{b}`.
- **Excel:** `openpyxl`, una hoja por paso con colores de pivote.

---

## 9B. ASISTENTE DE IA (fase 8, opcional)

**Objetivo:** que el usuario pegue un enunciado en párrafo (de un ejercicio) y obtenga la función objetivo y las restricciones **cargadas en el formulario**, listas para revisar.

### 9B.1 Principios

1. **La IA nunca resuelve nada.** Solo traduce el enunciado al **formato de texto de la sección 7**. Ese texto pasa por `parsear_problema`; el cálculo lo hace siempre el solver exacto.
2. **Nunca se resuelve automáticamente.** El problema se carga en el formulario con un aviso visible: *"Revisa los datos antes de resolver: la IA puede equivocarse al interpretar el enunciado."* El usuario pulsa **Resolver**.
3. **Dos modos que terminan en el mismo punto** (texto en formato estándar → `parsear_problema` → formulario):
   - **Modo A (manual, sin clave ni red):** la app genera el prompt; el usuario lo pega en el chat de IA que prefiera y pega la respuesta de vuelta.
   - **Modo B (automático, Gemini):** la app llama a la API gratuita de Google Gemini con la clave del usuario.
4. Si el modo B falla por cualquier motivo, el modo A sigue disponible y el mensaje de error lo sugiere.

### 9B.2 Plantilla del prompt (constante `PROMPT_EXTRACCION`, marcador `{enunciado}`)

```
Eres un asistente que convierte enunciados de Programación Lineal a un formato fijo.
Lee el enunciado y responde ÚNICAMENTE con un bloque de texto, sin explicaciones,
sin markdown y sin comillas, con exactamente este formato:

# x1 = <qué representa x1>
# x2 = <qué representa x2>
max <función objetivo>        (o: min <función objetivo>)
s.a.
<restricción 1>
<restricción 2>

Reglas:
1. Variables llamadas x1, x2, x3... en el orden en que se definen en el enunciado.
2. Operadores permitidos: <=, >=, =.
3. Coeficientes numéricos (enteros, decimales o fracciones a/b), sin unidades ni texto.
4. No incluyas restricciones de no negatividad (x1, x2 >= 0).
5. Si hay unidades distintas (horas y minutos, kg y g), conviértelo todo a una misma unidad.
6. Si el enunciado no es un problema de programación lineal o es ambiguo, responde
   exactamente: NO_ES_PL

Enunciado:
{enunciado}
```

### 9B.3 `core/parser_ia.py`

Sin dependencias nuevas: HTTP con `urllib.request` y `json` de la biblioteca estándar. **`core/` no importa nada de `gui/`**: la clave y el modelo se reciben como parámetros.

```python
class ErrorIA(Exception):
    """Error del asistente de IA (red, cuota, clave, respuesta inválida, NO_ES_PL)."""

PROMPT_EXTRACCION: str

def construir_prompt(enunciado: str) -> str:
    """Inserta el enunciado en la plantilla (modo A)."""

def limpiar_respuesta(texto: str) -> str:
    """Quita bloques ```, espacios extra y cualquier texto previo a la primera
    línea '#', 'max' o 'min'. Si el texto es 'NO_ES_PL' lanza ErrorIA."""

def problema_desde_respuesta(texto: str) -> tuple[Problema, list[str]]:
    """limpiar_respuesta + parsear_problema + extraer_leyenda.
    Es la ruta común de los modos A y B."""

class ClienteGemini:
    def __init__(self, api_key: str, modelo: str = "gemini-flash-lite-latest",
                 timeout: float = 30.0) -> None: ...
    def probar_conexion(self) -> list[str]:
        """GET /v1beta/models; devuelve los nombres de modelo disponibles."""
    def consultar(self, enunciado: str) -> str:
        """Devuelve el texto crudo de la respuesta."""

def analizar_enunciado(enunciado: str, cliente: ClienteGemini) -> tuple[Problema, list[str]]:
    """Consulta a Gemini y convierte la respuesta. Si hay ParseError, reintenta UNA
    vez enviando el mensaje de error y la respuesta previa; si vuelve a fallar,
    lanza ErrorIA con un mensaje claro."""
```

**Detalles de la API (REST):**

- Endpoint: `https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent`.
- La clave va en la cabecera `x-goog-api-key` (**nunca** en la URL, para que no aparezca en errores ni logs).
- Cuerpo: `{"contents": [{"parts": [{"text": <prompt>}]}], "generationConfig": {"temperature": 0}}`.
- La respuesta se lee de `candidates[0].content.parts[*].text` (concatenando las partes de texto). Si no hay candidatos (bloqueo de seguridad, respuesta vacía) → `ErrorIA`.
- Timeout de 30 s.
- **El nombre del modelo es configurable** y no se codifica en ningún otro sitio: los modelos gratuitos de Google cambian y se retiran con el tiempo. El valor por defecto es el alias `gemini-flash-lite-latest`.

**Mapeo de errores a mensajes en español (sin mostrar la clave):**

| Situación | Mensaje |
|---|---|
| HTTP 400 / 403 | "La clave de API no es válida o no tiene permiso. Revísala en Configuración de IA." |
| HTTP 404 | "El modelo configurado no existe o fue retirado. Usa «Probar conexión» y elige otro en Configuración de IA." |
| HTTP 429 | "Se agotó la cuota gratuita (por minuto o por día). Espera un momento o usa el modo manual (A)." |
| Timeout / sin red | "No se pudo conectar con Gemini. Revisa tu internet o usa el modo manual (A)." |
| Otro HTTP 5xx | "Gemini no está disponible ahora mismo. Intenta más tarde o usa el modo manual (A)." |
| Respuesta `NO_ES_PL` | "La IA no reconoció un problema de programación lineal en el texto. Revisa el enunciado." |

### 9B.4 Clave y configuración (`gui/ai_settings_dialog.py`)

- Diálogo **Herramientas → Configuración de IA** con: campo de clave (enmascarado), campo de modelo (editable, con valor por defecto), botón **Probar conexión** (usa `probar_conexion` y muestra los modelos disponibles) y un enlace de ayuda a Google AI Studio para obtener una clave gratuita.
- Se guarda **localmente** con `QSettings`. También se acepta la variable de entorno `GEMINI_API_KEY` como alternativa (la configuración del diálogo tiene prioridad). Avisar en el diálogo de que la clave se guarda sin cifrar en este equipo.
- La clave **nunca** se escribe en el repositorio, en logs, en mensajes de error ni en el PDF/Excel exportado. `.gitignore` debe cubrir cualquier archivo de configuración local.

### 9B.5 `gui/ai_panel.py`

Panel (pestaña o diálogo) **"Asistente IA"** accesible desde el panel de entrada, con:

1. Un `QTextEdit` grande para el **enunciado**.
2. Dos pestañas:
   - **Modo A: manual (sin clave).** Botón **Copiar prompt** (copia `construir_prompt(enunciado)` al portapapeles), un `QTextEdit` **"Pega aquí la respuesta de la IA"** y el botón **Cargar en el formulario**.
   - **Modo B: automático (Gemini).** Botón **Analizar con Gemini**. Deshabilitado, con tooltip que explica por qué, si no hay clave configurada. La llamada corre en un **`QThread`** (la interfaz no se congela) con un indicador de progreso y botón para cancelar.
3. Al terminar con éxito (cualquiera de los modos): se rellena el formulario con el `Problema`, se muestra la **leyenda de variables** (las líneas `#`) y el aviso de revisión de la sección 9B.1. Si hay error, se muestra el mensaje amigable de la tabla de 9B.3, sin traceback.
4. Texto de privacidad visible en el modo B: *"El enunciado se envía a Google. No incluyas datos personales. En la capa gratuita, Google puede usar los datos enviados para mejorar sus productos."*
5. Menú **Ayuda** y glosario: explicar qué hace el asistente y sus límites (puede equivocarse con enunciados largos o ambiguos; siempre hay que revisar).

### 9B.6 Casos de prueba sin red (`tests/test_parser_ia.py`)

Usar **respuestas simuladas** (cadenas fijas) para comprobar el camino completo `respuesta → problema_desde_respuesta → resolver_simplex`:

- Enunciado tipo Wyndor en párrafo con respuesta correcta → Z = 36, (2, 6).
- Respuesta envuelta en ```` ``` ```` y con texto previo ("Claro, aquí está:") → se limpia y se parsea.
- Respuesta `NO_ES_PL` → `ErrorIA` con el mensaje de la tabla.
- Respuesta con operador roto → un reintento (el *mock* verifica que el segundo pedido incluye el error) y luego éxito; si falla otra vez → `ErrorIA`.
- Mapeo de 400/403, 404, 429, 5xx y timeout a los mensajes de 9B.3.
- La clave no aparece en `str(error)`, en `repr(error)` ni en los registros (`caplog`).

---

## 10. INTERFAZ GRÁFICA (HCI)

### 10.1 Principios aplicados

- **Reconocimiento sobre recuerdo:** opciones visibles, nada escondido en menús profundos.
- **Feedback inmediato:** validación en vivo mientras se escribe.
- **Prevención de errores:** botón "Resolver" deshabilitado si el formulario es inválido.
- **Consistencia:** mismos colores, tipografía y espaciado en toda la app.
- **Ayuda contextual:** tooltip en cada campo.
- **Estado del sistema visible:** barra de estado ("Listo", "Resolviendo…", "Óptimo alcanzado", "Problema no factible").
- **Control del usuario:** deshacer/rehacer, ejemplos con un clic.
- Texto fijo en la interfaz: *"Todas las variables son ≥ 0."*

### 10.2 Paleta

| Uso | Color |
|---|---|
| Fondo principal | `#FAFAFA` |
| Fondo de paneles | `#FFFFFF` |
| Texto principal | `#212121` |
| Acento (botón primario) | `#1976D2` |
| Columna pivote | `#BBDEFB` |
| Fila pivote | `#C8E6C9` |
| Elemento pivote | `#FFE082` (negrita) |
| Fila Zj−Cj | `#F5F5F5` |
| Vértice factible | `#1976D2` |
| Punto óptimo | `#D32F2F` |
| Error / Éxito / Advertencia | `#C62828` / `#2E7D32` / `#F57C00` |

### 10.3 `main_window.py`

Mínimo 1200×800. Panel de entrada a la izquierda; a la derecha un `QStackedWidget` con vista gráfica, vista Simplex y resultado; barra de estado abajo.

Menús:

- **Archivo:** Nuevo (Ctrl+N), Abrir, Guardar, Exportar PDF, Salir.
- **Editar:** Deshacer, Rehacer, Limpiar.
- **Ver:** Vista gráfica, Vista Simplex, Modo oscuro.
- **Método:** Automático, Solo gráfico, Solo Simplex.
- **Ayuda:** Tutorial (F1), Glosario, Cargar ejemplo, Acerca de.

Reglas del modo automático: con 2 variables se muestran ambos métodos; con 3 o más solo Simplex (y se explica por qué el gráfico no aplica).

### 10.4 `problem_panel.py`

De arriba abajo:

1. **Sentido:** radio buttons Maximizar / Minimizar.
2. **Número de variables:** `QSpinBox` de 1 a 10 (por defecto 2).
3. **Función objetivo:** `Z = [__]x₁ + [__]x₂ …` (campos dinámicos).
4. **Restricciones:** `QTableWidget` con columnas `[x₁] [x₂] … [≤/≥/=] [RHS] [−]`, botón **+ Añadir restricción**.
5. Botones: **Cargar ejemplo**, **Limpiar**, **Resolver** (primario).

Validación en vivo: los campos aceptan enteros, decimales y fracciones (`3/2`); si hay error → fondo rojo + tooltip con el mensaje y "Resolver" deshabilitado.

### 10.5 `graphic_view.py`

Canvas Matplotlib (`FigureCanvasQTAgg`) con toolbar (zoom, pan, reset, guardar imagen).

- Ejes cartesianos con rejilla suave; solo primer cuadrante visible (x ≥ 0).
- Rectas de restricciones en colores distintos con etiqueta `R1, R2, …`.
- Región factible sombreada (gris, alpha 0,3).
- **Vértices** con punto azul y anotación `(4, 3)` / `Z = 27` (coordenadas como fracciones).
- **Óptimo** con punto rojo, más grande; en óptimo múltiple se resalta el segmento.
- Título: `Z* = 36 en (x1, x2) = (2, 6)`.
- Hover sobre un vértice: tooltip con coordenadas y Z.
- No hay animaciones ni líneas de nivel: solo el resultado final.

### 10.6 `simplex_view.py`

- Encabezado: `Paso 2 de 3`.
- Narrativa encima de la tabla, por ejemplo:

  ```
  Paso 1: Entra x₂ (Zj − Cj = −5, el más negativo).
          Sale s₂ (menor razón: 12/2 = 6).
          Elemento pivote: 2.
  ```

- Tabla `QTableWidget` con filas `Cj`, encabezados, filas de restricciones (con `Base` y `Cb`), y la fila `Zj − Cj`. Se muestran fracciones y expresiones con M (`-3M - 3`).
- Resaltado: columna pivote, fila pivote y elemento pivote (colores de la paleta, 100 % visibles).
- Lista **"Operaciones entre filas de este paso"** debajo de la tabla.
- Barra inferior: **◀ Anterior** | `Paso X / N` | **Siguiente ▶** | **▶ Reproducir** (cada 1,5 s; pasa a ⏸ Pausar). Atajos: `←`/`→` y `Espacio`.
- Todo es **automático con explicación**: el usuario no elige el pivote.

### 10.7 `resultado_panel.py`

Panel de solución final con estado, `Z*`, valores de todas las variables (originales, holguras, excesos), número de iteraciones y **advertencias** con iconos (múltiple, degenerado, restricción no activa).

Ejemplo para Wyndor:

```
SOLUCIÓN ÓPTIMA
Estado: Óptimo único
Z* = 36
x₁ = 2   x₂ = 6   s₁ = 2   s₂ = 0   s₃ = 0
Iteraciones: 2
```

### 10.8 Ayuda (`gui/help/`) en HTML dentro de `QTextBrowser`

- `tutorial.html`: guía paso a paso (con placeholders para capturas).
- `glosario.html`: variable básica/no básica; holgura/exceso/artificial; pivote, fila y columna pivote; Zj, Cj, Zj−Cj; región factible, vértice; óptimo múltiple, no factible, no acotado, degeneración, restricción no activa; regla de Bland; Big-M; razón mínima.
- `sobre.html`: versión, autor, licencia MIT, bibliografía (Taha).

### 10.9 Diálogo "Cargar ejemplo"

`QDialog` con `QListWidget` que lista los ejemplos de `core/ejemplos.py`; doble clic los carga en el formulario.

### 10.10 Robustez

- Nunca debe aparecer un traceback en la GUI: todo error se captura y se muestra como mensaje amigable.
- Dejar el hook para ejecutar la resolución en un `QThread` (no necesario para problemas pequeños).

---

## 11. EJEMPLOS PRECARGADOS (`core/ejemplos.py`) CON RESULTADO ESPERADO

```python
EJEMPLOS = {
    "Wyndor Glass (clásico)": """
max 3x1 + 5x2
s.a.
x1 <= 4
2x2 <= 12
3x1 + 2x2 <= 18
""",   # Z=36, (2, 6)
    "Mixto con Big-M": """
max 2x1 + 3x2
s.a.
x1 + x2 <= 4
x1 + 3x2 >= 6
""",   # Z=12, (0, 4)
    "Minimización con ≥": """
min 2x1 + 3x2
s.a.
x1 + x2 >= 4
x1 + 3x2 >= 6
""",   # Z=9, (3, 1)
    "Óptimo múltiple": """
max 2x1 + 4x2
s.a.
x1 + 2x2 <= 5
x1 + x2 <= 4
""",   # Z=10, segmento entre (3, 1) y (0, 5/2)
    "No factible": """
max x1 + x2
s.a.
x1 + x2 <= 2
x1 + x2 >= 5
""",
    "No acotado": """
max x1 + x2
s.a.
x1 - x2 <= 1
""",
    "Con igualdad": """
max 3x1 + 2x2
s.a.
2x1 + x2 <= 10
x1 + 3x2 = 12
""",   # Z=82/5, (18/5, 14/5)
}
```

---

## 12. TESTS Y CONVENCIONES

### 12.1 Tests (pytest, cobertura ≥ 80 % en `core/`)

- `tests/casos_taha.py`: problemas con resultado esperado (los de la sección 11 y problemas del libro de Taha).
- `test_numeros.py`: comparación lexicográfica con M, suma, resta, producto por `Fraction`, formato.
- `test_models.py`: validación de longitudes, nombres automáticos, conversión a `Fraction`.
- `test_simplex.py`: Wyndor (reproducir las tablas 0, 1 y 2 de la sección 5.8), Big-M (sección 5.9, incluido el desempate de Bland), minimización, igualdad, no factible, no acotado, óptimo múltiple, degeneración, operaciones fila registradas, tablas bien formadas, restricciones no activas.
- `test_graphic.py`: vértices de Wyndor **incluido (0, 0)**, óptimo, no factible, no acotado, óptimo múltiple, caso con igualdad.
- `test_parser.py`: formato estándar, variantes, `x1, x2 >= 0` ignorado, términos a ambos lados, fracciones y decimales, errores con mensajes claros.
- Test cruzado: para problemas de 2 variables, el óptimo del Simplex debe coincidir con el del método gráfico.
- GUI: solo tests de humo (la ventana abre y no se cae).

### 12.2 Estilo y nombres

- Dominio en español (`Problema`, `resolver_simplex`, `pasos`, `tabla`); infraestructura en inglés (`main_window`, `on_resolve_clicked`).
- Constantes en mayúsculas (`MAX_ITER`, `COLOR_PIVOTE`).
- Docstrings en formato Google, type hints en todas las funciones públicas, línea máxima de 88 (black), imports ordenados.
- Sin `print()` en producción (usar `logging`), sin `except:` pelados.
- Comentarios solo para explicar el **por qué**, y en la matemática, la lógica paso a paso.

---

## 13. FASES (AUTÓNOMAS, CON PUERTA DE CALIDAD)

Ejecuta las fases **en orden y de corrido**, sin pedir confirmación. Al final de cada una debes pasar su **puerta de calidad**; solo entonces cierras la fase (con su commit de `CHANGELOG.md`) y continúas. Dentro de cada fase, los commits son atómicos según la regla 4 de la sección 0.

**Puerta común a toda fase** (además de la específica):

```
pytest -q            # todo en verde
black --check .      # sin cambios pendientes
ruff check .         # sin errores
```

### Fase 0: Preparación del repositorio
`git init` (si no existe), `.gitignore` (Python, `.venv`, `__pycache__`, `dist/`, `build/`), entorno virtual, estructura de carpetas de la sección 3.2 (con `__init__.py`), `README.md` mínimo, `CHANGELOG.md`, `LICENSE` (MIT), y `docs/PROMPT.md` (este archivo).
**Puerta:** `python --version` ≥ 3.11 y la estructura existe.

### Fase 1A: Números y modelos
`requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, `core/__init__.py`, `core/numeros.py`, `utils/__init__.py`, `utils/formato.py`, `core/models.py`, `tests/__init__.py`, `tests/test_numeros.py`, `tests/test_models.py`.
**Puerta específica:** los tests de `NumM` cubren comparación lexicográfica con M (`-M - 100 < -3`), suma, resta, producto por `Fraction` y formato (`"-3M - 3"`).

### Fase 1B: Núcleo Simplex
`core/casos_especiales.py`, `core/simplex_solver.py`, `tests/casos_taha.py`, `tests/test_simplex.py`, `fase1_demo.py` (resuelve Wyndor y muestra el paso a paso en consola; este script **sí puede usar `print`**).
**Puerta específica:**
- Wyndor reproduce las tablas de la sección 5.8 y el ejemplo Big-M la secuencia de la sección 5.9 (regla 6 de la sección 0 si hay diferencias).
- Test de verificación cruzada con `scipy.optimize.linprog`: los 7 ejemplos de la sección 11 y **al menos 200 problemas aleatorios** pequeños (semilla fija, 2 a 4 variables, 2 a 5 restricciones, tipos mezclados) coinciden en estado y valor de Z.
- `python fase1_demo.py` se ejecuta sin errores.

### Fase 2: Núcleo gráfico
`core/graphic_solver.py`, `tests/test_graphic.py`.
**Puerta específica:** vértices de Wyndor incluyendo (0, 0); y para los problemas aleatorios de 2 variables, el óptimo del método gráfico coincide con el del Simplex.

### Fase 3: Parser
`core/parser.py`, `core/ejemplos.py`, `tests/test_parser.py`.
**Puerta específica:** los 7 ejemplos de la sección 11 se parsean y se resuelven con el resultado esperado; los errores de la sección 7.3 se producen con su mensaje; las líneas `#` se ignoran y `extraer_leyenda` las devuelve.

### Fase 4: GUI base
`main.py`, `gui/__init__.py`, `gui/main_window.py`, `gui/problem_panel.py`, `gui/resultado_panel.py`, `gui/steps_bar.py`.
**Puerta específica:** test de humo offscreen que abre `MainWindow`, carga cada ejemplo, pulsa "Resolver" y no lanza excepciones.

### Fase 5: Vista Simplex paso a paso
`gui/simplex_view.py`.
**Puerta específica:** test de humo que navega todos los pasos de Wyndor y comprueba que la celda pivote tiene el color y la negrita esperados.

### Fase 6: Vista gráfica
`gui/graphic_view.py`.
**Puerta específica:** test de humo que dibuja Wyndor, y comprueba que existen N puntos de vértice y 1 punto de óptimo; con 3 variables la vista gráfica queda deshabilitada con el mensaje de la sección 1.3.

### Fase 7: Ayuda y UX
`gui/help/tutorial.html`, `gui/help/glosario.html`, `gui/help/sobre.html`, y su integración en el menú Ayuda (F1).
**Puerta específica:** los tres archivos HTML cargan en un `QTextBrowser` y el glosario contiene todos los términos de la sección 10.8.

### Fase 8: Extras
`core/report.py` (PDF, LaTeX, Excel), `core/parser_ia.py`, `gui/ai_panel.py`, `gui/ai_settings_dialog.py`, `tests/test_parser_ia.py`, configuración de PyInstaller en `pyproject.toml` (o `.spec`).
**Puerta específica:**
- Los tres exportadores generan archivos no vacíos en un directorio temporal (el `.xlsx` se reabre con `openpyxl`).
- `parser_ia` cumple la sección 9B. Los tests (`tests/test_parser_ia.py`) simulan la API con *mocks* de `urllib.request.urlopen`: cubren prompt, limpieza de respuesta, `NO_ES_PL`, reintento tras `ParseError`, mapeo de errores HTTP (400/403, 404, 429, timeout, sin red) y que la clave nunca aparezca en mensajes, logs ni excepciones. **Sin internet ni clave real.**
- Si no hay clave, la app funciona igual: el modo B queda deshabilitado con un tooltip que sugiere el modo A.
- No hace falta generar el `.exe`; basta con dejar la configuración lista y documentada en el `README.md`.

---

## 14. CRITERIOS DE ACEPTACIÓN

**Funcionalidad**

- [ ] Wyndor: Z = 36, x₁ = 2, x₂ = 6, con las tablas de la sección 5.8.
- [ ] Problema Big-M (5.9): Z = 12, x₂ = 4, con la secuencia indicada.
- [ ] Mínimo, mixtos y con igualdad dan los resultados esperados (sección 11).
- [ ] Muestra todas las tablas con columna, fila y elemento pivote resaltados.
- [ ] Muestra las operaciones entre filas y qué variable entra y cuál sale.
- [ ] Todo en fracciones exactas; la M se ve simbólica en las tablas.
- [ ] Detecta múltiple, no factible, no acotado y degeneración; informa restricciones no activas.
- [ ] El gráfico muestra región sombreada, todos los vértices **(incluido el origen)** con coordenadas y Z, y el óptimo.
- [ ] Con 3 o más variables el método gráfico se deshabilita con mensaje claro.
- [ ] El parser acepta los formatos de la sección 7.
- [ ] Ayuda (tutorial, glosario, acerca de) y ejemplos de un clic.
- [ ] Asistente de IA: el modo A (copiar prompt / pegar respuesta) funciona sin clave; el modo B (Gemini) se deshabilita sin clave; nunca resuelve solo, siempre carga el formulario para revisar; la clave no aparece en logs ni errores.

**Calidad**

- [ ] `pytest` pasa al 100 % con cobertura ≥ 80 % en `core/`.
- [ ] `black --check .` y `ruff check .` sin errores.
- [ ] Sin `print()` en `core/` ni `gui/`.
- [ ] Tests de humo de GUI en modo offscreen pasan.
- [ ] Verificación cruzada con `scipy.optimize.linprog` pasa (7 ejemplos + 200 aleatorios).
- [ ] Docstrings y type hints en todo lo público.
- [ ] Cero floats en `core/`, salvo el ordenamiento de vértices y la región para dibujar.

**HCI**

- [ ] Validación en vivo, "Resolver" deshabilitado si hay errores, tooltips en todos los campos.
- [ ] Atajos de teclado funcionando y paleta respetada.
- [ ] La app nunca muestra un traceback.

---

## 15. NOTAS FINALES PARA LA IA

1. **No omitas módulos.** Mantén `casos_especiales.py` separado aunque parezca redundante.
2. **La M es simbólica**, representada con `NumM` (nunca un número grande como 1000000).
3. **Cero floats** en `core/`. La conversión a `float` solo ocurre al graficar y al ordenar vértices.
4. **Registra cada paso** completo: tabla, operaciones, razones, narrativa y Z.
5. **Respeta la convención de Taha:** la minimización no se convierte a maximización.
6. **Verifica con los ejemplos trabajados** (secciones 5.8 y 5.9) antes de dar la fase por terminada. Si tus tablas no coinciden, el error está en tu código.
7. **Autonomía con control:** avanza fase tras fase sin pedir confirmación, pero **nunca con una puerta de calidad en rojo** (sección 13). Ante un bloqueo, sigue la regla 7 de la sección 0.

---

## 16. INSTRUCCIÓN DE ARRANQUE

Empieza ahora por la **Fase 0** y continúa con la 1A, 1B, 2, 3, 4, 5, 6, 7 y 8, en ese orden, aplicando las reglas de la sección 0 y la puerta de calidad de cada fase.

Cada archivo debe estar completo, con imports, docstrings, type hints y comentarios explicativos. No dejes `pass` ni `TODO`. Al terminar la Fase 8, genera `docs/INFORME_FINAL.md` y resume el resultado.
