# AGENTS.md: SimplexLab

La especificación completa del proyecto está en `docs/PROMPT.md`. Léela completa antes de escribir código y síguela al pie de la letra.

## Reglas permanentes

- `docs/PROMPT.md` es de solo lectura. Los errores que detectes en él se anotan en `docs/DISCREPANCIAS.md`.
- `core/` nunca importa nada de `gui/`.
- Aritmética exacta con `fractions.Fraction` y la clase `NumM` (a·M + b). Nada de floats en `core/`, salvo para ordenar vértices y dibujar.
- Python 3.11+, entorno virtual `.venv`, estilo `black` (88 columnas) y `ruff`.
- Antes de dar algo por terminado, ejecuta: `pytest -q`, `black --check .`, `ruff check .`.
- Tests de GUI con `QT_QPA_PLATFORM=offscreen`.
- Commits atómicos (un cambio lógico por commit, con sus tests) y mensajes en Conventional Commits en español (`feat(core): ...`, `fix(graphic): ...`). Nunca `git push`, `git reset --hard` ni `git rebase`. Usa `git add` selectivo y revisa `git status` antes de cada commit.
- No avances de fase con una puerta de calidad en rojo.
- Sin servicios de pago. La única llamada de red del programa es el asistente de IA opcional (API gratuita de Gemini, sección 9B de `docs/PROMPT.md`). Los tests nunca usan internet ni claves reales, y la clave de API nunca se escribe en el repo, en logs ni en mensajes de error.
