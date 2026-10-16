"""Aritmética exacta y números simbólicos de la forma a·M + b."""

from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering


def fraccion(valor: Fraction | str | int | float) -> Fraction:
    """Convierte entradas decimales por su representación, sin error binario."""
    return valor if isinstance(valor, Fraction) else Fraction(str(valor))


@total_ordering
@dataclass(frozen=True, eq=False)
class NumM:
    """Número afín en M, con orden lexicográfico para M tendiendo a infinito."""

    m: Fraction = Fraction(0)
    c: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "m", fraccion(self.m))
        object.__setattr__(self, "c", fraccion(self.c))

    @staticmethod
    def _convertir(otro: object) -> "NumM":
        if isinstance(otro, NumM):
            return otro
        if isinstance(otro, (int, Fraction)):
            return NumM(c=otro)
        raise TypeError("Se esperaba NumM, Fraction o entero.")

    def __add__(self, otro: object) -> "NumM":
        otro = self._convertir(otro)
        return NumM(self.m + otro.m, self.c + otro.c)

    __radd__ = __add__

    def __neg__(self) -> "NumM":
        return NumM(-self.m, -self.c)

    def __sub__(self, otro: object) -> "NumM":
        return self + -self._convertir(otro)

    def __rsub__(self, otro: object) -> "NumM":
        return self._convertir(otro) - self

    def __mul__(self, otro: Fraction | int) -> "NumM":
        if not isinstance(otro, (int, Fraction)):
            raise TypeError("NumM solo se multiplica por Fraction o entero.")
        return NumM(self.m * otro, self.c * otro)

    __rmul__ = __mul__

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, (NumM, Fraction, int)):
            return False
        otro = self._convertir(otro)
        return (self.m, self.c) == (otro.m, otro.c)

    def __lt__(self, otro: object) -> bool:
        otro = self._convertir(otro)
        return (self.m, self.c) < (otro.m, otro.c)

    def __hash__(self) -> int:
        return hash(self.c) if not self.m else hash((self.m, self.c))

    def es_cero(self) -> bool:
        """Indica si ambas partes son cero."""
        return self == 0

    def es_negativo(self) -> bool:
        """Indica el signo según el término dominante."""
        return self < 0

    def es_positivo(self) -> bool:
        """Indica el signo según el término dominante."""
        return self > 0

    def __str__(self) -> str:
        if not self.m:
            return str(self.c)
        parte = "M" if abs(self.m) == 1 else f"{abs(self.m)}M"
        parte = ("-" if self.m < 0 else "") + parte
        if self.c:
            parte += f" {'+' if self.c > 0 else '-'} {abs(self.c)}"
        return parte
