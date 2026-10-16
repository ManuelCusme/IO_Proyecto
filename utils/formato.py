"""Representación común de cantidades exactas."""

from fractions import Fraction

from core.numeros import NumM


def formatear(valor: Fraction | NumM) -> str:
    """Devuelve una fracción o expresión simbólica legible."""
    return str(valor)
