"""Invariantes de separación y aritmética del núcleo."""

import ast
from pathlib import Path


def test_core_independiente_y_exacto() -> None:
    """Prohíbe imports de gui, evaluación de código y decimales matemáticos."""
    raiz = Path(__file__).resolve().parents[1]
    for archivo in (raiz / "core").glob("*.py"):
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom):
                assert not (nodo.module or "").startswith("gui")
            if isinstance(nodo, ast.Import):
                assert not any(a.name.startswith("gui") for a in nodo.names)
            if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                assert nodo.func.id not in ("print", "eval", "exec")
                if nodo.func.id == "float":
                    assert archivo.name == "graphic_solver.py"
            if isinstance(nodo, ast.Constant) and isinstance(nodo.value, float):
                assert archivo.name == "parser_ia.py" and nodo.value == 30.0
