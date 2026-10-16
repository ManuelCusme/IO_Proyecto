"""Datos intercambiados por los solvers y la interfaz."""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Literal

from core.numeros import NumM, fraccion

Estado = Literal["optimo", "multiple", "no_factible", "no_acotado"]


@dataclass
class Restriccion:
    """Restricción original, conservando el signo de su término independiente."""

    coefs: list[Fraction]
    tipo: Literal["<=", ">=", "="]
    rhs: Fraction

    def __post_init__(self) -> None:
        self.coefs = [fraccion(c) for c in self.coefs]
        self.rhs = fraccion(self.rhs)
        if self.tipo not in ("<=", ">=", "="):
            raise ValueError("El tipo de restricción debe ser <=, >= o =.")


@dataclass
class Problema:
    """Problema de programación lineal con variables no negativas."""

    sentido: Literal["max", "min"]
    coef_obj: list[Fraction]
    restricciones: list[Restriccion]
    nombres: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.coef_obj = [fraccion(c) for c in self.coef_obj]
        if self.sentido not in ("max", "min"):
            raise ValueError("El sentido debe ser max o min.")
        if not self.coef_obj or not self.restricciones:
            raise ValueError("Se requiere al menos una variable y una restricción.")
        n = len(self.coef_obj)
        if any(len(r.coefs) != n for r in self.restricciones):
            raise ValueError(
                "Las restricciones deben tener tantos coeficientes como variables."
            )
        self.nombres = (
            list(self.nombres) if self.nombres else [f"x{i+1}" for i in range(n)]
        )
        if len(self.nombres) != n or len(set(self.nombres)) != n:
            raise ValueError(
                "Los nombres deben ser únicos y coincidir con las variables."
            )
        if any(not isinstance(s, str) or not s.strip() for s in self.nombres):
            raise ValueError("Los nombres de variables no pueden estar vacíos.")


@dataclass
class PasoSimplex:
    """Instantánea independiente de la tabla antes de efectuar un pivote."""

    numero: int
    encabezados: list[str]
    base: list[str]
    cb: list[NumM]
    cj: list[NumM]
    tabla: list[list[Fraction]]
    fila_z: list[NumM]
    col_pivote: int | None
    fila_pivote: int | None
    elemento_pivote: Fraction | None
    entra: str | None
    sale: str | None
    razones: list[Fraction | None]
    operaciones: list[str]
    mensaje: str
    z: NumM
    advertencias: list[str]


@dataclass
class ResultadoSimplex:
    """Resultado y trazabilidad completa del método Simplex."""

    pasos: list[PasoSimplex]
    estado: Estado
    degenerado: bool
    z: Fraction | None
    solucion: dict[str, Fraction] | None
    advertencias: list[str]


@dataclass
class ResultadoGrafico:
    """Vértices exactos y geometría de presentación del método gráfico."""

    vertices: list[tuple[Fraction, Fraction]]
    valores_z: list[Fraction]
    optimos: list[tuple[Fraction, Fraction]]
    z_optimo: Fraction | None
    estado: Estado
    region_acotada: bool
    rectas: list[dict]
    region: list[tuple[float, float]]
    advertencias: list[str]
