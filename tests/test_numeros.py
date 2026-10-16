"""Contrato aritmético y de presentación de NumM."""

from fractions import Fraction as F

import pytest

from core.numeros import NumM, fraccion
from utils.formato import formatear


def test_aritmetica() -> None:
    """La M domina constantes y las operaciones conservan fracciones."""
    assert NumM(-1, -100) < -3
    assert NumM(1, -100) > 100
    assert NumM(1, 2) + NumM(-1, 3) == 5
    assert 3 + NumM(1, 2) == NumM(1, 5)
    assert NumM(1, 2) - 3 == NumM(1, -1)
    assert 3 - NumM(1, 2) == NumM(-1, 1)
    assert -NumM(2, 3) == NumM(-2, -3)
    assert NumM(2, 3) * F(1, 2) == NumM(1, F(3, 2))
    assert F(1, 2) * NumM(2, 3) == NumM(1, F(3, 2))
    assert NumM().es_cero()
    assert NumM(-1, 200).es_negativo()
    assert NumM(0, 1).es_positivo()
    assert NumM() != "0"
    assert hash(NumM(c=3)) == hash(3)
    assert hash(NumM(1, 2)) == hash((F(1), F(2)))
    with pytest.raises(TypeError):
        NumM() * NumM()
    with pytest.raises(TypeError):
        NumM() + "M"


@pytest.mark.parametrize(
    "m,c,texto",
    [
        (-3, -3, "-3M - 3"),
        (1, 1, "M + 1"),
        (0, F(3, 2), "3/2"),
        (-1, 0, "-M"),
        (0, 0, "0"),
        (F(1, 2), -2, "1/2M - 2"),
    ],
)
def test_formato(m: int, c: int, texto: str) -> None:
    """El formato omite coeficientes unitarios y términos nulos."""
    assert formatear(NumM(m, c)) == texto


def test_decimal() -> None:
    """La conversión usa la representación decimal de entrada."""
    assert fraccion(0.1) == F(1, 10)
    assert NumM("1/2", "0.1") == NumM(F(1, 2), F(1, 10))
