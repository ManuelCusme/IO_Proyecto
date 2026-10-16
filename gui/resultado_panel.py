"""Presentación de resultados y advertencias académicas."""

from html import escape

from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QWidget

from core.models import Problema, ResultadoGrafico, ResultadoSimplex
from core.resultados import resumir_resultado


class ResultadoPanel(QWidget):
    """Muestra Z, todas las variables y los casos especiales del resultado."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.texto = QTextBrowser()
        layout.addWidget(self.texto)
        self.texto.setPlainText("Introduce o carga un problema y pulsa Resolver.")

    def mostrar(
        self, resultado: ResultadoSimplex | ResultadoGrafico, problema: Problema
    ) -> None:
        """Representa fracciones sin conversiones decimales."""
        resultado = resumir_resultado(problema, resultado)
        estados = {
            "optimo": "Óptimo único",
            "multiple": "Óptimo múltiple",
            "no_factible": "Problema no factible",
            "no_acotado": "Problema no acotado",
        }
        lineas = [
            estados[resultado.estado].upper(),
            f"Estado: {estados[resultado.estado]}",
        ]
        if resultado.z is not None:
            lineas.append(f"Z* = {resultado.z}")
            lineas.extend(f"{n} = {v}" for n, v in resultado.solucion.items())
        lineas.append(
            f"Iteraciones: {resultado.iteraciones}"
            if resultado.iteraciones is not None
            else "Método gráfico: resultado final sin iteraciones."
        )
        if resultado.degenerado:
            lineas.append("⚠ Solución degenerada")
        lineas.extend("⚠ " + aviso for aviso in resultado.advertencias)
        color = "#2E7D32" if resultado.estado in ("optimo", "multiple") else "#C62828"
        partes = [f"<h2 style='color: {color}'>{escape(lineas[0])}</h2>"]
        for linea in lineas[1:]:
            color_linea = "#F57C00" if linea.startswith("⚠") else "#212121"
            partes.append(f"<p style='color: {color_linea}'>{escape(linea)}</p>")
        self.texto.setHtml("".join(partes))
