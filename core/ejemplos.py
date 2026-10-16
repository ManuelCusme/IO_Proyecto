"""Ejemplos académicos precargados de SimplexLab."""

EJEMPLOS = {
    "Wyndor Glass (clásico)": """
max 3x1 + 5x2
s.a.
x1 <= 4
2x2 <= 12
3x1 + 2x2 <= 18
""",  # Z=36, (2, 6)
    "Mixto con Big-M": """
max 2x1 + 3x2
s.a.
x1 + x2 <= 4
x1 + 3x2 >= 6
""",  # Z=12, (0, 4)
    "Minimización con ≥": """
min 2x1 + 3x2
s.a.
x1 + x2 >= 4
x1 + 3x2 >= 6
""",  # Z=9, (3, 1)
    "Óptimo múltiple": """
max 2x1 + 4x2
s.a.
x1 + 2x2 <= 5
x1 + x2 <= 4
""",  # Z=10, segmento entre (3, 1) y (0, 5/2)
    "No factible": """
max x1 + x2
s.a.
x1 + x2 <= 2
x1 + x2 >= 5
""",
    "No acotado": """
max x1 + x2
s.a.
x1 - x2 <= 1
""",
    "Con igualdad": """
max 3x1 + 2x2
s.a.
2x1 + x2 <= 10
x1 + 3x2 = 12
""",  # Z=82/5, (18/5, 14/5)
}
