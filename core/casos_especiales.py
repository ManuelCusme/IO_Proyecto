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


def confirmar_multiple(
    tabla: list[list[Fraction]],
    fila_z: list[NumM],
    encabezados: list[str],
    base: list[str],
) -> bool:
    """Busca movimiento positivo en la cara óptima, pasando por bases degeneradas.

    Un costo reducido cero es necesario pero no suficiente: su razón mínima
    puede ser cero. Se exploran las bases de esa misma cara con aritmética exacta
    hasta hallar un segmento o rayo, o agotar las bases alcanzables.
    """
    ceros = [
        j
        for j, n in enumerate(encabezados)
        if n != "b" and not n.startswith("a") and fila_z[j].es_cero()
    ]
    inicial = [encabezados.index(n) for n in base]
    pendientes = [(tabla, inicial)]
    vistas = {frozenset(inicial)}
    while pendientes:
        actual, basicas = pendientes.pop()
        for col in ceros:
            if col in basicas:
                continue
            razones = [(r[-1] / r[col], i) for i, r in enumerate(actual) if r[col] > 0]
            if not razones or min(razones)[0] > 0:
                return True
            for razon, fila in razones:
                if razon != 0:
                    continue
                nueva_base = basicas[:]
                nueva_base[fila] = col
                clave = frozenset(nueva_base)
                if clave in vistas:
                    continue
                vistas.add(clave)
                pivote = actual[fila][col]
                pivoteada = [v / pivote for v in actual[fila]]
                nueva = [
                    (
                        pivoteada
                        if i == fila
                        else [a - r[col] * b for a, b in zip(r, pivoteada)]
                    )
                    for i, r in enumerate(actual)
                ]
                pendientes.append((nueva, nueva_base))
    return False
