"""Predicados exactos para analizar casos especiales del Simplex."""

from fractions import Fraction

from core.models import Problema
from core.numeros import NumM


def detectar_multiple(
    fila_z: list[NumM], encabezados: list[str], base: list[str]
) -> bool:
    """Detecta costos reducidos nulos de variables no básicas no artificiales."""
    return any(
        z.es_cero() and n not in base and not n.startswith("a")
        for z, n in zip(fila_z, encabezados)
        if n != "b"
    )


def detectar_no_factible(base: list[str], valores_b: list[Fraction]) -> bool:
    """Detecta artificiales básicas estrictamente positivas."""
    return any(n.startswith("a") and b > 0 for n, b in zip(base, valores_b))


def detectar_no_acotado(columna_pivote: list[Fraction]) -> bool:
    """Indica que no existe coeficiente positivo para la razón mínima."""
    return not any(a > 0 for a in columna_pivote)


def detectar_empate_razon(razones: list[Fraction | None]) -> bool:
    """Comprueba si dos razones admisibles alcanzan el mínimo."""
    validas = [r for r in razones if r is not None]
    return bool(validas) and validas.count(min(validas)) > 1


def aplicar_bland(
    filas_empatadas: list[int], base: list[str], indices_columna: dict[str, int]
) -> int:
    """Desempata por el índice de la variable básica."""
    return min(filas_empatadas, key=lambda i: indices_columna[base[i]])


def restricciones_no_activas(
    problema: Problema, solucion: dict[str, Fraction]
) -> list[tuple[int, Fraction]]:
    """Calcula holguras y excesos sobre las restricciones originales."""
    resultado = []
    for i, r in enumerate(problema.restricciones, 1):
        lhs = sum(
            (a * solucion[n] for a, n in zip(r.coefs, problema.nombres)), Fraction()
        )
        diferencia = r.rhs - lhs if r.tipo == "<=" else lhs - r.rhs
        if r.tipo != "=" and diferencia > 0:
            resultado.append((i, diferencia))
    return resultado
