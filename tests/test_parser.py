"""Variantes sintácticas, errores claros y comentarios de variables."""

from fractions import Fraction as F

import pytest

from core.ejemplos import EJEMPLOS
from core.parser import ParseError, extraer_leyenda, parsear_problema
from core.simplex_solver import resolver_simplex
from tests.casos_taha import CASOS


@pytest.mark.parametrize("texto,referencia", list(zip(EJEMPLOS.values(), CASOS)))
def test_ejemplos(texto: str, referencia: tuple) -> None:
    """Los siete ejemplos se cargan y producen el resultado verificado."""
    p = parsear_problema(texto)
    assert p == referencia[0]
    assert resolver_simplex(p).z == referencia[1]


@pytest.mark.parametrize(
    "marcador", ["s.a.", "s.a", "sujeto a", "sujeto a:", "subject to", "st"]
)
def test_variantes(marcador: str) -> None:
    """Acepta decimales, fracciones, comentarios y no negatividad explícita."""
    texto = f"# x = mesas\nMAXIMIZAR Z = 0.5x + 3/2*y - z\n{marcador}\nx+y ≤ 4\n2*x == z+3\nx, y, z >= 0\nx >= 0"
    p = parsear_problema(texto)
    assert p.coef_obj == [F(1, 2), F(3, 2), -1]
    assert p.restricciones[1].coefs == [2, 0, -1]
    assert extraer_leyenda(texto) == ["x = mesas"]


def test_ambos_lados_y_orden() -> None:
    """Conserva orden del objetivo y ordena variables adicionales numéricamente."""
    p = parsear_problema("min x2 + x1\ns.a.\n-x1 + 2 >= x10 + x3 - 4")
    assert p.nombres == ["x2", "x1", "x3", "x10"]
    assert p.restricciones[0].coefs == [0, -1, -1, -1]
    assert p.restricciones[0].rhs == -6


@pytest.mark.parametrize(
    "texto,mensaje",
    [
        ("", "No se encontró el sentido (max/min) en la primera línea."),
        (
            "max 2\ns.a.\nx1<=1",
            "La función objetivo no contiene variables reconocibles.",
        ),
        ("max x1\nx1<=1", "Falta la línea 's.a.' o 'sujeto a:'."),
        ("max x1\ns.a.\nx1<=2\nx1+2", "Restricción #2: falta el operador (<=, >=, =)."),
        (
            "max x1\ns.a.\nx1<=2\nx1<=3\n3x1 +* 2 <= 4",
            "Restricción #3: no se pudo interpretar '3x1 +* 2'.",
        ),
        (
            "max x1\ns.a.\nx1 = __import__('os')",
            "Restricción #1: no se pudo interpretar",
        ),
        ("max x1\ns.a.\n1/0x1<=2", "Restricción #1: no se pudo interpretar"),
        ("max x1+2\ns.a.\nx1<=2", "La función objetivo no admite"),
        ("max x1\ns.a.", "Se requiere al menos una variable"),
    ],
)
def test_errores(texto: str, mensaje: str) -> None:
    """Nunca evalúa código ni deja escapar errores internos del parser."""
    with pytest.raises(ParseError) as error:
        parsear_problema(texto)
    assert str(error.value).startswith(mensaje)
