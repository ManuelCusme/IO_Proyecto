"""Casos académicos de referencia y generador reproducible."""

import random
from fractions import Fraction as F
from itertools import combinations

from scipy.optimize import OptimizeResult, linprog

from core.models import Problema
from core.models import Restriccion as R

CASOS = [
    (
        Problema(
            "max",
            [3, 5],
            [R([1, 0], "<=", 4), R([0, 2], "<=", 12), R([3, 2], "<=", 18)],
        ),
        F(36),
    ),
    (Problema("max", [2, 3], [R([1, 1], "<=", 4), R([1, 3], ">=", 6)]), F(12)),
    (Problema("min", [2, 3], [R([1, 1], ">=", 4), R([1, 3], ">=", 6)]), F(9)),
    (Problema("max", [2, 4], [R([1, 2], "<=", 5), R([1, 1], "<=", 4)]), F(10)),
    (Problema("max", [1, 1], [R([1, 1], "<=", 2), R([1, 1], ">=", 5)]), None),
    (Problema("max", [1, 1], [R([1, -1], "<=", 1)]), None),
    (Problema("max", [3, 2], [R([2, 1], "<=", 10), R([1, 3], "=", 12)]), F(82, 5)),
]


def aleatorios(cantidad: int = 240) -> list[Problema]:
    """Genera restricciones mixtas, RHS de ambos signos y objetivos de ambos sentidos."""
    rng = random.Random(1052026)
    problemas = []
    for _ in range(cantidad):
        n, m = rng.randint(2, 4), rng.randint(2, 5)
        problemas.append(
            Problema(
                rng.choice(["max", "min"]),
                [rng.randint(-5, 5) for _ in range(n)],
                [
                    R(
                        [rng.randint(-4, 5) for _ in range(n)],
                        rng.choice(["<=", ">=", "="]),
                        rng.randint(-5, 15),
                    )
                    for _ in range(m)
                ],
            )
        )
    return problemas


def referencia_scipy(p: Problema) -> OptimizeResult:
    """Resuelve con HiGHS únicamente desde los tests."""
    au, bu, ae, be = [], [], [], []
    for r in p.restricciones:
        signo = -1 if r.tipo == ">=" else 1
        if r.tipo == "=":
            ae.append([float(v) for v in r.coefs])
            be.append(float(r.rhs))
        else:
            au.append([signo * float(v) for v in r.coefs])
            bu.append(signo * float(r.rhs))
    return linprog(
        [(-1 if p.sentido == "max" else 1) * float(c) for c in p.coef_obj],
        A_ub=au or None,
        b_ub=bu or None,
        A_eq=ae or None,
        b_eq=be or None,
        bounds=(0, None),
        method="highs",
        options={"presolve": False},
    )


def vertices_independientes(p: Problema) -> list[tuple[F, F]]:
    """Enumera intersecciones sin usar código de ninguno de los solvers."""
    rectas = [(r.coefs[0], r.coefs[1], r.rhs) for r in p.restricciones] + [
        (F(1), F(0), F(0)),
        (F(0), F(1), F(0)),
    ]
    puntos = set()
    for (a, b, c), (d, e, f) in combinations(rectas, 2):
        det = a * e - b * d
        if det == 0:
            continue
        x, y = (c * e - b * f) / det, (a * f - c * d) / det
        if x < 0 or y < 0:
            continue
        if all(
            {
                "<=": a * x + b * y <= r.rhs,
                ">=": a * x + b * y >= r.rhs,
                "=": a * x + b * y == r.rhs,
            }[r.tipo]
            for r in p.restricciones
            for a, b in [r.coefs]
        ):
            puntos.add((x, y))
    return sorted(puntos)
