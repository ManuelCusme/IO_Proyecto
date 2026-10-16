# SimplexLab

Aplicación de escritorio académica para programación lineal continua, con
**método gráfico 2D** y **Simplex Gran M simbólica**. Todas las variables son
no negativas; los cálculos usan `Fraction` y muestran fracciones exactas.

## Instalar y ejecutar

Requiere Python 3.11 o posterior. Desde la raíz de este repositorio:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

En Linux/macOS se activa con `source .venv/bin/activate`. La aplicación funciona
sin internet después de instalar dependencias. No requiere ninguna clave.

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
