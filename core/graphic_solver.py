"""Geometría 2D exacta por enumeración de vértices y cono de recesión."""

from fractions import Fraction as F
from itertools import combinations
from math import atan2

from core.models import Problema, Restriccion, ResultadoGrafico

Punto = tuple[F, F]


def _cumple(
    punto: Punto, restricciones: list[Restriccion], homogeneo: bool = False
) -> bool:
    if min(punto) < 0:
        return False
    for r in restricciones:
        lhs = sum((a * x for a, x in zip(r.coefs, punto)), F())
        rhs = F() if homogeneo else r.rhs
        if (
            r.tipo == "<="
            and lhs > rhs
            or r.tipo == ">="
            and lhs < rhs
            or r.tipo == "="
            and lhs != rhs
        ):
            return False
    return True


def _ordenar(puntos: set[Punto]) -> list[Punto]:
    if not puntos:
        return []
    cx = sum(p[0] for p in puntos) / len(puntos)
    cy = sum(p[1] for p in puntos) / len(puntos)
    return sorted(puntos, key=lambda p: (atan2(float(p[1] - cy), float(p[0] - cx)), p))


def _vertices(restricciones: list[Restriccion]) -> list[Punto]:
    rectas = [(r.coefs[0], r.coefs[1], r.rhs) for r in restricciones]
    rectas.extend([(F(1), F(), F()), (F(), F(1), F())])
    puntos = set()
    for (a, b, c), (d, e, f) in combinations(rectas, 2):
        det = a * e - b * d
        if det:
            punto = ((c * e - b * f) / det, (a * f - c * d) / det)
            if _cumple(punto, restricciones):
                puntos.add(punto)
    return _ordenar(puntos)


def resolver_grafico(problema: Problema) -> ResultadoGrafico:
    """Enumera vértices y detecta direcciones infinitas sin tolerancias.

    Raises:
        ValueError: Si el problema no tiene exactamente dos variables.
    """
    if len(problema.coef_obj) != 2:
        raise ValueError("El método gráfico solo aplica a problemas de 2 variables.")
    rs = problema.restricciones
    rectas = [
        {"coefs": r.coefs[:], "rhs": r.rhs, "tipo": r.tipo, "nombre": f"R{i}"}
        for i, r in enumerate(rs, 1)
    ]
    vertices = _vertices(rs)
    if not vertices:
        return ResultadoGrafico([], [], [], None, "no_factible", True, rectas, [], [])
    direcciones = {(F(1), F()), (F(), F(1))}
    for r in rs:
        a, b = r.coefs
        if a or b:
            direcciones.update({(b, -a), (-b, a)})
    recesion = [d for d in direcciones if _cumple(d, rs, True)]
    valores = [
        sum((a * x for a, x in zip(problema.coef_obj, p)), F()) for p in vertices
    ]
    cambios = [
        sum((a * x for a, x in zip(problema.coef_obj, d)), F()) for d in recesion
    ]
    mejora = any(c > 0 if problema.sentido == "max" else c < 0 for c in cambios)
    z = (
        (max(valores) if problema.sentido == "max" else min(valores))
        if not mejora
        else None
    )
    optimos = [p for p, v in zip(vertices, valores) if v == z]
    multiple = len(optimos) > 1 or (bool(optimos) and 0 in cambios)
    estado = "no_acotado" if mejora else "multiple" if multiple else "optimo"
    avisos = []
    if optimos and 0 in cambios:
        avisos.append("Óptimo múltiple: existe una semirrecta de soluciones óptimas.")
    limite = max(F(10), max(max(p) for p in vertices) * F(3, 2))
    region = _vertices(
        rs + [Restriccion([1, 0], "<=", limite), Restriccion([0, 1], "<=", limite)]
    )
    if recesion:
        avisos.append("La región no es acotada; se recorta únicamente para dibujar.")
    return ResultadoGrafico(
        vertices,
        valores,
        optimos,
        z,
        estado,
        not recesion,
        rectas,
        [(float(x), float(y)) for x, y in region],
        avisos,
    )
