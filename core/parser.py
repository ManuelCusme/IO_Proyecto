"""Parser de expresiones lineales basado en regex, sin evaluación de código."""

import re
from fractions import Fraction as F

from core.models import Problema, Restriccion

_VARIABLE = r"(?:x[1-9][0-9]*|[xyz])"
_NUMERO = r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:/[0-9]+)?"
_TERMINO = re.compile(
    rf"([+-]?)(?:({_NUMERO})(?:\*?({_VARIABLE}))?|({_VARIABLE}))", re.I
)
_OPERADOR = re.compile(r"<=|>=|==|=|≤|≥")
_MARCADORES = {"s.a.", "s.a", "sujeto a", "sujeto a:", "subject to", "st"}


class ParseError(Exception):
    """Error de sintaxis del problema, apto para mostrar al usuario."""


def extraer_leyenda(texto: str) -> list[str]:
    """Devuelve comentarios sin el símbolo # en su orden original."""
    return [
        s.strip()[1:].strip() for s in texto.splitlines() if s.strip().startswith("#")
    ]


def _expresion(texto: str) -> tuple[dict[str, F], F]:
    compacto = re.sub(r"\s+", "", texto).lower()
    coefs: dict[str, F] = {}
    constante = F()
    pos = 0
    while pos < len(compacto):
        match = _TERMINO.match(compacto, pos)
        if not match or pos and not match[1]:
            raise ValueError("Término lineal inválido")
        signo = -1 if match[1] == "-" else 1
        coef = F(match[2] or 1) * signo
        nombre = match[3] or match[4]
        if nombre:
            coefs[nombre] = coefs.get(nombre, F()) + coef
        else:
            constante += coef
        pos = match.end()
    if not compacto:
        raise ValueError("Expresión vacía")
    return coefs, constante


def _orden_variable(nombre: str) -> tuple[str, int]:
    match = re.fullmatch(r"([a-z]+)([0-9]*)", nombre)
    return match[1], int(match[2] or 0)


def parsear_problema(texto: str) -> Problema:
    """Convierte texto académico en un problema de aritmética exacta.

    Raises:
        ParseError: Si falta una sección o una expresión no es lineal.
    """
    lineas = [
        s.strip()
        for s in texto.splitlines()
        if s.strip() and not s.strip().startswith("#")
    ]
    match = re.match(
        r"^(maximizar|minimizar|max|min)\b\s*(.*)$", lineas[0] if lineas else "", re.I
    )
    if not match:
        raise ParseError("No se encontró el sentido (max/min) en la primera línea.")
    sentido = "max" if match[1].lower().startswith("max") else "min"
    objetivo = re.sub(r"^z\s*=\s*", "", match[2], flags=re.I)
    try:
        coefs, constante = _expresion(objetivo)
    except (ValueError, ZeroDivisionError):
        raise ParseError(
            "La función objetivo no contiene variables reconocibles."
        ) from None
    if not coefs:
        raise ParseError("La función objetivo no contiene variables reconocibles.")
    if constante:
        raise ParseError(
            "La función objetivo no admite un término constante independiente."
        )
    if len(lineas) < 2 or lineas[1].lower() not in _MARCADORES:
        raise ParseError("Falta la línea 's.a.' o 'sujeto a:'.")
    restricciones = []
    nombres_extra = set()
    for numero, linea in enumerate(lineas[2:], 1):
        normal = linea.replace("≥", ">=").replace("≤", "<=")
        if re.fullmatch(
            rf"\s*{_VARIABLE}(?:\s*,\s*{_VARIABLE})*\s*>=\s*0\s*", normal, re.I
        ):
            continue
        op = _OPERADOR.search(linea)
        if not op:
            raise ParseError(f"Restricción #{numero}: falta el operador (<=, >=, =).")
        partes = []
        for fragmento in (linea[: op.start()], linea[op.end() :]):
            try:
                partes.append(_expresion(fragmento))
            except (ValueError, ZeroDivisionError):
                raise ParseError(
                    f"Restricción #{numero}: no se pudo interpretar '{fragmento.strip()}'."
                ) from None
        (izquierda, ci), (derecha, cd) = partes
        variables = dict(izquierda)
        for n, c in derecha.items():
            variables[n] = variables.get(n, F()) - c
        nombres_extra.update(variables)
        tipo = {"≤": "<=", "≥": ">=", "==": "="}.get(op[0], op[0])
        restricciones.append((variables, tipo, cd - ci))
    nombres = list(coefs) + sorted(nombres_extra - set(coefs), key=_orden_variable)
    try:
        return Problema(
            sentido,
            [coefs.get(n, F()) for n in nombres],
            [
                Restriccion([c.get(n, F()) for n in nombres], t, b)
                for c, t, b in restricciones
            ],
            nombres,
        )
    except ValueError as error:
        raise ParseError(str(error)) from None
