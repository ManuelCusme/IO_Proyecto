"""Validaciones de datos y conversión exacta."""

from fractions import Fraction

import pytest

from core.models import Problema, Restriccion


def test_conversion() -> None:
    """El RHS negativo y las entradas decimales se conservan exactamente."""
    r = Restriccion([0.1, "2/3"], ">=", -2)
    p = Problema("min", ["1/3", 2], [r])
    assert p.nombres == ["x1", "x2"]
    assert r.coefs == [Fraction(1, 10), Fraction(2, 3)]
    assert r.rhs == -2
    assert all(isinstance(c, Fraction) for c in p.coef_obj)


@pytest.mark.parametrize(
    "sentido,coefs,rs,nombres",
    [
        ("max", [], [], []),
        ("max", [1], [], []),
        ("otro", [1], [Restriccion([1], "<=", 1)], []),
        ("max", [1, 2], [Restriccion([1], "<=", 1)], []),
        ("max", [1, 2], [Restriccion([1, 1], "<=", 1)], ["x", "x"]),
        ("max", [1], [Restriccion([1], "<=", 1)], [""]),
    ],
)
def test_invalidos(sentido: str, coefs: list, rs: list, nombres: list) -> None:
    """Se rechazan dimensiones y nombres incoherentes."""
    with pytest.raises(ValueError):
        Problema(sentido, coefs, rs, nombres)


def test_operador_invalido() -> None:
    """Los operadores se validan antes de construir una tabla."""
    with pytest.raises(ValueError):
        Restriccion([1], "<", 1)
