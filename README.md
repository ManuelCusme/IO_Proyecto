# SimplexLab

Aplicación de escritorio académica para programación lineal continua, con
**método gráfico 2D** y **Simplex Gran M simbólica**. Todas las variables son
no negativas; los cálculos usan `Fraction` y muestran fracciones exactas.

## Cómo iniciar el proyecto en Windows, paso a paso

Esta guía usa **PowerShell en Windows**, incluida la terminal integrada de
VS Code. SimplexLab abre una ventana de escritorio; no necesitas un navegador.
La aplicación funciona sin internet después de instalar las dependencias y no
requiere ninguna clave de API para resolver problemas.

### Primera instalación

1. **Comprueba que tienes Python 3.11 o posterior.** Abre PowerShell y ejecuta:

   ```powershell
   py --version
   ```

   Si el comando no existe o la versión es anterior a 3.11, instala Python para
   Windows y habilita las opciones del instalador para agregar Python al PATH
   y el lanzador `py`. Cierra y vuelve a abrir la terminal tras instalarlo.

2. **Entra en la carpeta del proyecto.** En este equipo la ruta es:

   ```powershell
   cd "C:\Users\Personal\IO_Proyecto"
   ```

   Si guardaste el proyecto en otra ubicación, sustituye la ruta. En VS Code
   puedes abrir esta carpeta y seleccionar **Terminal → Nueva terminal**.
   Verifica que estás en la raíz, donde se encuentran `main.py` y
   `requirements.txt`:

   ```powershell
   Get-Item main.py, requirements.txt
   ```

3. **Crea el entorno virtual**, solo si todavía no existe la carpeta `.venv`:

   ```powershell
   py -m venv .venv
   ```

   El entorno usa la versión de Python comprobada en el paso 1 y mantiene las
   dependencias del proyecto en su propia carpeta.

4. **Instala las dependencias** usando el Python del entorno virtual:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

   Este paso necesita internet. Espera a que termine sin errores antes de seguir.

5. **Inicia SimplexLab**:

   ```powershell
   .\.venv\Scripts\python.exe main.py
   ```

   Se abrirá la ventana de la aplicación. Mantén la terminal abierta mientras
   la usas. Para comprobar su funcionamiento, carga **Wyndor Glass (clásico)**
   y pulsa **Resolver**: debes obtener `Z* = 36`, `x1 = 2` y `x2 = 6`.
   Para salir, cierra la ventana.

### Cómo abrirlo las siguientes veces

Abre PowerShell y ejecuta estos dos comandos. No necesitas volver a crear el
entorno ni instalar las dependencias en cada inicio:

```powershell
cd "C:\Users\Personal\IO_Proyecto"
.\.venv\Scripts\python.exe main.py
```

### Activación opcional del entorno

Los comandos anteriores funcionan sin activar el entorno. Si prefieres usar
`python` directamente, activa `.venv` desde la raíz del proyecto:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Para salir del entorno cuando hayas cerrado la aplicación, ejecuta `deactivate`.
Si PowerShell bloquea `Activate.ps1` por su política de ejecución, usa el comando
directo `.\.venv\Scripts\python.exe main.py` de la sección anterior.

### Problemas al iniciar en Windows

- **No se encuentra `.\.venv\Scripts\python.exe`:** comprueba que estás en la
  carpeta del proyecto y crea el entorno siguiendo el paso 3 si aún no existe.
- **Aparece `ModuleNotFoundError`:** repite el paso 4 y ejecuta con el Python
  de `.venv` para usar las dependencias instaladas allí.
- **Aparece `No Python at ...`:** el entorno apunta a una instalación de Python
  que ya no existe. Comprueba `py --version` (3.11 o posterior). Desde la raíz
  del proyecto, renombra el entorno anterior y crea uno nuevo:

  ```powershell
  Rename-Item -LiteralPath .venv -NewName .venv_anterior
  py -m venv .venv
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  .\.venv\Scripts\python.exe main.py
  ```

  Si ya existe `.venv_anterior`, elige otro nombre para conservarlo.
- **No se encuentra `main.py`:** vuelve a la raíz con el comando `cd` indicado.
- **El proceso arranca pero no aparece la ventana después de ejecutar tests:**
  elimina el modo de pruebas de esa terminal y vuelve a iniciar:

  ```powershell
  Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
  .\.venv\Scripts\python.exe main.py
  ```

## Uso

1. Elige Maximizar/Minimizar y de 1 a 10 variables. Introduce coeficientes
   enteros, decimales o fracciones, operadores `<=`, `>=`, `=` y RHS.
2. Carga un ejemplo por doble clic o completa el formulario; los errores se
   marcan en rojo y deshabilitan Resolver. Todas las variables son ≥ 0.
3. Pulsa Resolver. Para Wyndor se obtiene **Z*=36, x1=2, x2=6**.
4. Recorre las tablas con Anterior/Siguiente, ←/→ o Espacio dentro de la vista.
   Reproducir avanza cada 1,5 segundos. Azul: columna; verde: fila;
   amarillo y negrita: pivote. Las operaciones aparecen debajo.
5. En Gráfico, explora la región sombreada, vértices y óptimos; la toolbar
   permite zoom, pan y guardar imagen. El gráfico solo aplica a dos variables.
6. Resultado muestra valores, estado, degeneración y restricciones no activas.
   Archivo guarda/abre problemas JSON y exporta PDF, LaTeX o Excel. El PDF
   incluye las tablas, operaciones, resultado y gráfico cuando corresponde.
7. Tutorial (F1), Glosario y Acerca de están disponibles sin conexión.

Convención fija: `Zj − Cj`. En máximo entra el costo más negativo; en mínimo,
el más positivo, sin invertir Z. Artificiales: −M en máximo, +M en mínimo.
Bland solo desempata; el límite de 100 iteraciones protege contra ciclado.
La degeneración es independiente del estado. Un costo reducido nulo se confirma
con movimiento factible antes de declarar óptimos múltiples.

## Asistente IA opcional

Abre **Asistente IA** desde el formulario o Herramientas:

- **Modo A:** copia el prompt, úsalo en el chat que prefieras y pega la respuesta.
  No necesita clave ni red de la aplicación.
- **Modo B:** configura tu propia clave gratuita y el modelo en
  **Herramientas → Configuración de IA**. La prueba de conexión lista modelos
  disponibles. El modelo predeterminado está centralizado en `core/parser_ia.py`.
  Las llamadas corren en un hilo; Cancelar descarta la respuesta. Una conexión
  en curso puede tardar hasta su timeout de 30 s en finalizar.

Los dos modos cargan el formulario **sin resolverlo**. Revisa siempre la
interpretación, las unidades y las restricciones antes de pulsar Resolver.
Google recibe el enunciado en el modo B; no incluyas datos personales. En la capa
gratuita Google puede usar los datos para mejorar sus productos. Si no puedes
usar Gemini, el modo A permanece disponible.

La clave se guarda **sin cifrar** mediante QSettings en el equipo (en Windows,
`HKEY_CURRENT_USER\Software\SimplexLab\SimplexLab`, grupo `ia`). También se acepta
`GEMINI_API_KEY`; el valor guardado en el diálogo tiene prioridad. No se guardan
credenciales en archivos de problemas ni en informes. No incluyas claves en el
repositorio. Los tests eliminan la variable de entorno y aíslan QSettings.

## Desarrollo y validación

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -q
python -m pytest --cov=core --cov-report=term-missing
python -m black --check .
python -m ruff check .
python fase1_demo.py
```

SciPy se instala solo en desarrollo. Las pruebas comparan los siete ejemplos y
240 problemas aleatorios de semilla fija con HiGHS, y verifican vértices exactos
independientemente en dos variables. Ningún test usa internet ni claves reales;
`urllib.request.urlopen` está bloqueado salvo los mocks explícitos.

`core/` no importa `gui/`. El cálculo matemático no usa floats; solo el orden de
vértices y la geometría de dibujo convierten a float. La conversión de entradas
decimales pasa por texto para conservar la intención del usuario. El timeout
HTTP es un parámetro de infraestructura, no un valor matemático.

## Distribución Windows

La configuración está lista para PyInstaller 6.x; no es necesario compilar para
usar el programa desde Python:

```powershell
python -m PyInstaller --clean SimplexLab.spec
```

La distribución queda en `dist/SimplexLab/`. Incluye HTML de ayuda, estilos y
backend Qt de Matplotlib; excluye SciPy y herramientas de desarrollo. No se
incluyen configuraciones locales ni credenciales. La compilación del ejecutable
no forma parte de las pruebas de esta entrega.

## Documentación y licencia

- Especificación de solo lectura: `docs/PROMPT.md`.
- Discrepancias verificadas: `docs/DISCREPANCIAS.md`.
- Progreso por fases: `CHANGELOG.md`.
- Estado de aceptación y cobertura: `docs/INFORME_FINAL.md`.
- Licencia MIT. Bibliografía: Taha, *Investigación de Operaciones*, 9.ª edición.
