"""Demostración en consola de Wyndor, sin dependencias de la GUI."""

import sys

from core.models import Problema, Restriccion
from core.simplex_solver import resolver_simplex


def main() -> None:
    """Imprime todas las tablas y sus operaciones elementales."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = Problema(
        "max",
        [3, 5],
        [
            Restriccion([1, 0], "<=", 4),
            Restriccion([0, 2], "<=", 12),
            Restriccion([3, 2], "<=", 18),
        ],
    )
    r = resolver_simplex(p)
    for paso in r.pasos:
        print(paso.mensaje)
        print("Base", "Cb", *paso.encabezados, sep="\t")
        for base, cb, fila in zip(paso.base, paso.cb, paso.tabla):
            print(base, cb, *fila, sep="\t")
        print("Zj − Cj", "", *paso.fila_z, sep="\t")
        print("\n".join(paso.operaciones))
    print(f"Z* = {r.z}; {r.solucion}")


if __name__ == "__main__":
    main()
