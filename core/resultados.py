"""Resumen común para presentar y exportar ambos métodos sin recalcularlos."""

from dataclasses import dataclass
from fractions import Fraction

from core.casos_especiales import restricciones_no_activas
from core.models import (
    Estado,
    PasoSimplex,
    Problema,
    ResultadoGrafico,
    ResultadoSimplex,
)


@dataclass
class ResumenResultado:
    """Datos de presentación; None identifica propiedades ajenas al método gráfico."""

    estado: Estado
    z: Fraction | None
    solucion: dict[str, Fraction] | None
    pasos: list[PasoSimplex]
    advertencias: list[str]
    iteraciones: int | None
    degenerado: bool | None


def resumir_resultado(
    problema: Problema, resultado: ResultadoSimplex | ResultadoGrafico
) -> ResumenResultado:
    """Obtiene valores exactos del método aplicado, sin invocar otro solver."""
    if isinstance(resultado, ResultadoSimplex):
        return ResumenResultado(
            resultado.estado,
            resultado.z,
            resultado.solucion,
            resultado.pasos,
            resultado.advertencias,
            len(resultado.pasos) - 1,
            resultado.degenerado,
        )
    solucion = None
    avisos = resultado.advertencias[:]
    if resultado.estado == "multiple":
        avisos.append(
            "Existen infinitas soluciones óptimas; "
            "se muestra un vértice representativo."
        )
    if resultado.optimos:
        solucion = dict(zip(problema.nombres, resultado.optimos[0]))
        s, e = 0, 0
        for r in problema.restricciones:
            lhs = sum(
                (a * solucion[n] for a, n in zip(r.coefs, problema.nombres)), Fraction()
            )
            if r.tipo == "<=":
                s += 1
                solucion[f"s{s}"] = r.rhs - lhs
            elif r.tipo == ">=":
                e += 1
                solucion[f"e{e}"] = lhs - r.rhs
        for i, valor in restricciones_no_activas(problema, solucion):
            tipo = "holgura" if problema.restricciones[i - 1].tipo == "<=" else "exceso"
            avisos.append(f"La restricción R{i} no está activa ({tipo} = {valor}).")
    return ResumenResultado(
        resultado.estado, resultado.z_optimo, solucion, [], avisos, None, None
    )
