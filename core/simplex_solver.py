"""Simplex primal con Gran M simbólica y convención Zj − Cj de Taha."""

from fractions import Fraction

from core.casos_especiales import (
    aplicar_bland,
    detectar_empate_razon,
    detectar_multiple,
    detectar_no_acotado,
    detectar_no_factible,
    restricciones_no_activas,
)
from core.models import PasoSimplex, Problema, ResultadoSimplex
from core.numeros import NumM

MAX_ITER = 100


class ErrorInterno(Exception):
    """Error controlado del solver, que la interfaz puede presentar sin traceback."""


def _aumentar(
    p: Problema,
) -> tuple[list[str], list[list[Fraction]], list[str], dict[str, NumM]]:
    filas = []
    grupos: dict[str, list[str]] = {"s": [], "e": [], "a": []}
    base = []
    extras = []
    for r in p.restricciones:
        signo = -1 if r.rhs < 0 else 1
        tipo = {"<=": ">=", ">=": "<=", "=": "="}[r.tipo] if signo < 0 else r.tipo
        filas.append([a * signo for a in r.coefs] + [r.rhs * signo])
        extra = {}
        for prefijo, coef in (
            [("s", 1)]
            if tipo == "<="
            else [("e", -1), ("a", 1)] if tipo == ">=" else [("a", 1)]
        ):
            nombre = f"{prefijo}{len(grupos[prefijo]) + 1}"
            if nombre in p.nombres:
                raise ValueError(
                    "Un nombre original coincide con una variable auxiliar: " + nombre
                )
            grupos[prefijo].append(nombre)
            extra[nombre] = Fraction(coef)
        base.append(next(n for n, c in extra.items() if c == 1))
        extras.append(extra)
    nombres = list(p.nombres) + sum(grupos.values(), [])
    tabla = [
        fila[:-1]
        + [extra.get(n, Fraction()) for n in nombres[len(p.nombres) :]]
        + fila[-1:]
        for fila, extra in zip(filas, extras)
    ]
    costos = {n: NumM(c=c) for n, c in zip(p.nombres, p.coef_obj)}
    for n in nombres[len(p.nombres) :]:
        costos[n] = NumM((-1 if p.sentido == "max" else 1) if n in grupos["a"] else 0)
    return nombres, tabla, base, costos


def resolver_simplex(problema: Problema) -> ResultadoSimplex:
    """Resuelve una PL exacta y conserva cada tabla anterior al pivote.

    Raises:
        ValueError: Si los datos del problema son inválidos.
        ErrorInterno: Si se alcanza la cota de seguridad contra ciclado.
    """
    nombres, tabla, base, costos = _aumentar(problema)
    pasos: list[PasoSimplex] = []
    avisos: list[str] = []
    degenerado = False
    for numero in range(MAX_ITER + 1):
        cb = [costos[n] for n in base]
        cj = [costos[n] for n in nombres]
        fila_z = [
            sum((cb[i] * tabla[i][j] for i in range(len(tabla))), NumM())
            - (cj[j] if j < len(nombres) else NumM())
            for j in range(len(nombres) + 1)
        ]
        candidatos = [
            j
            for j, z in enumerate(fila_z[:-1])
            if (z < 0 if problema.sentido == "max" else z > 0)
        ]
        col = (
            (
                min(candidatos, key=lambda j: fila_z[j])
                if problema.sentido == "max"
                else max(candidatos, key=lambda j: fila_z[j])
            )
            if candidatos
            else None
        )
        razones = [
            fila[-1] / fila[col] if col is not None and fila[col] > 0 else None
            for fila in tabla
        ]
        fila = None
        operaciones = []
        advertencias = []
        mensaje = "Óptimo alcanzado."
        # Si ya se optimizó el coeficiente de M y sigue habiendo artificiales
        # positivas, la región original es vacía aunque Z pudiera mejorar en c.
        m_optima = all(
            z.m >= 0 if problema.sentido == "max" else z.m <= 0 for z in fila_z[:-1]
        )
        imposible = m_optima and detectar_no_factible(base, [r[-1] for r in tabla])
        estado = "no_factible" if imposible else "optimo"
        if imposible:
            col = None
            mensaje = (
                "Problema no factible: una artificial permanece positiva en la base."
            )
        elif col is not None:
            if detectar_no_acotado([r[col] for r in tabla]):
                estado = "no_acotado"
                mensaje = "Problema no acotado: no existe razón admisible en la columna pivote."
            else:
                menor = min(r for r in razones if r is not None)
                empatadas = [i for i, r in enumerate(razones) if r == menor]
                fila = aplicar_bland(
                    empatadas, base, {n: j for j, n in enumerate(nombres)}
                )
                if detectar_empate_razon(razones):
                    degenerado = True
                    advertencias.append(
                        "Empate en la razón mínima: la siguiente solución será degenerada"
                    )
                pivote = tabla[fila][col]
                operaciones.append(f"F{fila+1} ← F{fila+1} / ({pivote})")
                for i, r in enumerate(tabla):
                    if i != fila and r[col]:
                        operaciones.append(f"F{i+1} ← F{i+1} − ({r[col]})·F{fila+1}")
                if not fila_z[col].es_cero():
                    operaciones.append(f"FZ ← FZ − ({fila_z[col]})·F{fila+1}")
                criterio = (
                    "más negativo" if problema.sentido == "max" else "más positivo"
                )
                mensaje = (
                    f"Paso {numero}: Entra {nombres[col]} (Zj − Cj = {fila_z[col]}, el {criterio}). "
                    f"Sale {base[fila]} (menor razón: {tabla[fila][-1]}/{pivote} = {menor}). "
                    f"Elemento pivote: {pivote}."
                )
                if base[fila].startswith("a"):
                    mensaje += (
                        f" {base[fila]} salió de la base; su columna ya no se necesita."
                    )
        pasos.append(
            PasoSimplex(
                numero,
                nombres[:] + ["b"],
                base[:],
                cb,
                cj,
                [r[:] for r in tabla],
                fila_z,
                col,
                fila,
                tabla[fila][col] if fila is not None else None,
                nombres[col] if col is not None else None,
                base[fila] if fila is not None else None,
                razones,
                operaciones,
                mensaje,
                fila_z[-1],
                advertencias,
            )
        )
        avisos.extend(advertencias)
        if estado in ("no_factible", "no_acotado"):
            return ResultadoSimplex(pasos, estado, degenerado, None, None, avisos)
        if col is None:
            solucion = {n: Fraction() for n in nombres}
            solucion.update({n: r[-1] for n, r in zip(base, tabla)})
            if any(r[-1] == 0 for r in tabla):
                degenerado = True
                avisos.append("Solución degenerada: una variable básica vale 0.")
            if any(n.startswith("a") for n in base):
                avisos.append("Artificial en la base con valor 0 (solución degenerada)")
                degenerado = True
            if fila_z[-1].m:
                raise ErrorInterno("El valor factible de Z conserva una componente M.")
            if detectar_multiple(fila_z, nombres + ["b"], base):
                estado = "multiple"
                avisos.append("Existen infinitas soluciones óptimas")
            for i, holgura in restricciones_no_activas(problema, solucion):
                tipo = (
                    "holgura"
                    if problema.restricciones[i - 1].tipo == "<="
                    else "exceso"
                )
                avisos.append(
                    f"La restricción R{i} no está activa ({tipo} = {holgura})."
                )
            solucion = {n: v for n, v in solucion.items() if not n.startswith("a")}
            return ResultadoSimplex(
                pasos, estado, degenerado, fila_z[-1].c, solucion, avisos
            )
        if numero == MAX_ITER:
            raise ErrorInterno(
                f"Se alcanzó el límite de {MAX_ITER} iteraciones. Revise el problema; posible ciclado."
            )
        saliente = base[fila]
        pivote = tabla[fila][col]
        tabla[fila] = [v / pivote for v in tabla[fila]]
        for i in range(len(tabla)):
            if i != fila:
                factor = tabla[i][col]
                tabla[i] = [a - factor * b for a, b in zip(tabla[i], tabla[fila])]
        base[fila] = nombres[col]
        if saliente.startswith("a"):
            j = nombres.index(saliente)
            nombres.pop(j)
            for r in tabla:
                r.pop(j)
    raise ErrorInterno("No se pudo completar la resolución.")
