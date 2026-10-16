"""Resúmenes de presentación obtenidos sin recalcular otro método."""

import pytest

from core.graphic_solver import resolver_grafico
from core.resultados import resumir_resultado
from core.simplex_solver import resolver_simplex
from tests.casos_taha import CASOS


@pytest.mark.parametrize("p,esperado", CASOS)
def test_ambos_metodos(p, esperado) -> None:
    """Ambos resúmenes conservan Z, estados y cantidades exactas."""
    grafico = resumir_resultado(p, resolver_grafico(p))
    simplex = resumir_resultado(p, resolver_simplex(p))
    assert grafico.z == simplex.z == esperado
    assert grafico.estado == simplex.estado
    assert grafico.iteraciones is None and grafico.degenerado is None
    assert not grafico.pasos
    if esperado is not None:
        assert (
            sum(a * grafico.solucion[n] for a, n in zip(p.coef_obj, p.nombres))
            == esperado
        )
        assert all(v >= 0 for v in grafico.solucion.values())
    else:
        assert grafico.solucion is None
