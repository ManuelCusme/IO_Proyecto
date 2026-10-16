"""Tablas de Taha y verificación independiente del solver exacto."""

from fractions import Fraction as F

import pytest

from core.models import Problema
from core.models import Restriccion as R
from core.numeros import NumM
from core.simplex_solver import ErrorInterno, resolver_simplex
from tests.casos_taha import (
    CASOS,
    aleatorios,
    referencia_scipy,
    vertices_independientes,
)


def test_wyndor() -> None:
    """Reproduce las tres tablas y las operaciones de la sección 5.8."""
    p = CASOS[0][0]
    resultado = resolver_simplex(p)
    a, b, c = resultado.pasos
    assert a.tabla == [[1, 0, 1, 0, 0, 4], [0, 2, 0, 1, 0, 12], [3, 2, 0, 0, 1, 18]]
    assert a.fila_z == [-3, -5, 0, 0, 0, 0]
    assert a.razones == [None, 6, 9]
    assert a.operaciones == ["F2 ← F2 / (2)", "F3 ← F3 − (2)·F2", "FZ ← FZ − (-5)·F2"]
    assert b.tabla == [
        [1, 0, 1, 0, 0, 4],
        [0, 1, 0, F(1, 2), 0, 6],
        [3, 0, 0, -1, 1, 6],
    ]
    assert b.fila_z == [-3, 0, 0, F(5, 2), 0, 30]
    assert c.tabla == [
        [0, 0, 1, F(1, 3), F(-1, 3), 2],
        [0, 1, 0, F(1, 2), 0, 6],
        [1, 0, 0, F(-1, 3), F(1, 3), 2],
    ]
    assert c.fila_z == [0, 0, 0, F(3, 2), 1, 36]
    assert resultado.solucion == {"x1": 2, "x2": 6, "s1": 2, "s2": 0, "s3": 0}
    assert any("R1 no está activa" in a for a in resultado.advertencias)
    assert not resultado.degenerado


def test_bigm() -> None:
    """Verifica M, eliminación de artificial y desempate de entrada por Bland."""
    r = resolver_simplex(CASOS[1][0])
    assert len(r.pasos) == 4
    assert r.pasos[0].fila_z == [NumM(-1, -2), NumM(-3, -3), 0, NumM(1), 0, NumM(-6)]
    assert r.pasos[1].encabezados == ["x1", "x2", "s1", "e1", "b"]
    assert r.pasos[1].fila_z == [-1, 0, 0, -1, 6]
    assert [p.entra for p in r.pasos] == ["x2", "x1", "e1", None]
    assert [p.sale for p in r.pasos] == ["a1", "s1", "x1", None]
    assert [p.z for p in r.pasos[1:]] == [6, 9, 12]
    assert r.solucion == {"x1": 0, "x2": 4, "s1": 0, "e1": 6}


@pytest.mark.parametrize("p,esperado", CASOS)
def test_ejemplos(p: Problema, esperado: F | None) -> None:
    """Contrasta todos los ejemplos con scipy y enumeración exacta de vértices."""
    r = resolver_simplex(p)
    s = referencia_scipy(p)
    assert r.z == esperado
    if esperado is not None:
        assert s.status == 0
        assert float(r.z) == pytest.approx((-1 if p.sentido == "max" else 1) * s.fun)
        valores = [
            sum(a * b for a, b in zip(p.coef_obj, v))
            for v in vertices_independientes(p)
        ]
        assert r.z == (max(valores) if p.sentido == "max" else min(valores))
    else:
        assert r.estado == {2: "no_factible", 3: "no_acotado"}[s.status]


@pytest.mark.parametrize("p", aleatorios())
def test_cruzado_aleatorio(p: Problema) -> None:
    """Contrasta estados y Z de 240 problemas mixtos con semilla fija."""
    r, s = resolver_simplex(p), referencia_scipy(p)
    if s.status == 0:
        assert r.estado in ("optimo", "multiple")
        assert float(r.z) == pytest.approx(
            (-1 if p.sentido == "max" else 1) * s.fun, abs=1e-7
        )
        if len(p.nombres) == 2:
            valores = [
                sum(a * b for a, b in zip(p.coef_obj, v))
                for v in vertices_independientes(p)
            ]
            assert r.z == (max(valores) if p.sentido == "max" else min(valores))
    else:
        assert s.status in (2, 3)
        assert r.estado == {2: "no_factible", 3: "no_acotado"}[s.status]
    for paso in r.pasos:
        assert len(paso.fila_z) == len(paso.encabezados)
        assert all(len(f) == len(paso.encabezados) for f in paso.tabla)
        assert all(isinstance(v, F) for f in paso.tabla for v in f)


def test_degenerado_rhs_y_artificial_cero() -> None:
    """Cubre empate, normalización y artificial básica nula."""
    p = Problema(
        "max", [1, 1], [R([-1, 0], ">=", -1), R([0, 1], "<=", 1), R([1, 1], "<=", 2)]
    )
    r = resolver_simplex(p)
    assert r.degenerado and r.z == 2
    assert p.restricciones[0].rhs == -1
    r = resolver_simplex(Problema("min", [1], [R([0], "=", 0), R([1], ">=", 1)]))
    assert r.z == 1 and r.degenerado
    assert any("Artificial en la base" in a for a in r.advertencias)


def test_limite(monkeypatch: pytest.MonkeyPatch) -> None:
    """La protección contra ciclado termina con un error controlado."""
    monkeypatch.setattr("core.simplex_solver.MAX_ITER", 0)
    with pytest.raises(ErrorInterno, match="límite"):
        resolver_simplex(CASOS[0][0])
