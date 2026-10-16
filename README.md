# SimplexLab

Aplicación académica de escritorio para programación lineal con aritmética exacta,
método gráfico y Simplex Gran M simbólica. Python 3.11 o posterior.

## Desarrollo

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:QT_QPA_PLATFORM = "offscreen"
python -m pytest -q
python -m black --check .
python -m ruff check .
```

La especificación está en `docs/PROMPT.md`; las fases se registran en
`CHANGELOG.md`. No se necesita ninguna clave para desarrollar o probar.
