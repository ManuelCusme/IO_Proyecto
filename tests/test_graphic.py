"""Vértices, recesión y concordancia entre métodos."""

from fractions import Fraction as F

import pytest

from core.graphic_solver import resolver_grafico
from core.models import Problema
from core.models import Restriccion as R
from core.simplex_solver import resolver_simplex
from tests.casos_taha import CASOS, aleatorios, vertices_independientes


def test_wyndor() -> None:
    """Incluye el origen y cada vértice extremo del polígono."""
    r = resolver_grafico(CASOS[0][0])
    assert set(r.vertices) == {(0, 0), (4, 0), (4, 3), (2, 6), (0, 6)}
    assert r.optimos == [(2, 6)] and r.z_optimo == 36
    assert r.region_acotada and len(r.region) == 5
    assert dict(zip(r.vertices, r.valores_z))[(4, 3)] == 27


@pytest.mark.parametrize("p,esperado", CASOS)
def test_ejemplos(p: Problema, esperado: F | None) -> None:
    """Las soluciones de los siete ejemplos coinciden con Simplex."""
    r = resolver_grafico(p)
    assert r.z_optimo == esperado
    assert r.estado == resolver_simplex(p).estado
    assert set(r.vertices) == set(vertices_independientes(p))


@pytest.mark.parametrize("p", [p for p in aleatorios() if len(p.nombres) == 2])
def test_aleatorios(p: Problema) -> None:
    """Contrasta geometría independiente con Simplex en todos los casos 2D."""
    r, s = resolver_grafico(p), resolver_simplex(p)
    assert r.z_optimo == s.z
    assert (r.estado in ("optimo", "multiple")) == (s.estado in ("optimo", "multiple"))
    if s.z is None:
        assert r.estado == s.estado
    assert set(r.vertices) == set(vertices_independientes(p))


def test_semirrecta_y_region_no_acotada() -> None:
    """Una región infinita puede tener óptimo finito o una cara óptima infinita."""
    r = resolver_grafico(Problema("min", [1, 0], [R([1, 0], ">=", 1)]))
    assert r.estado == "multiple" and r.z_optimo == 1
    assert not r.region_acotada and r.advertencias
    r = resolver_grafico(Problema("min", [1, 1], [R([1, 1], ">=", 1)]))
    assert r.z_optimo == 1
    with pytest.raises(ValueError, match="2 variables"):
        resolver_grafico(Problema("max", [1], [R([1], "<=", 1)]))
