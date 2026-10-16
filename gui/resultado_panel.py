"""Presentación de resultados y advertencias académicas."""

from PySide6.QtWidgets import QTextBrowser, QVBoxLayout, QWidget

from core.models import ResultadoSimplex


class ResultadoPanel(QWidget):
    """Muestra Z, todas las variables y los casos especiales del resultado."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.texto = QTextBrowser()
        layout.addWidget(self.texto)
        self.texto.setPlainText("Introduce o carga un problema y pulsa Resolver.")

    def mostrar(self, resultado: ResultadoSimplex) -> None:
        """Representa fracciones sin conversiones decimales."""
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
        lineas.append(f"Iteraciones: {len(resultado.pasos)-1}")
        if resultado.degenerado:
            lineas.append("⚠ Solución degenerada")
        lineas.extend("⚠ " + aviso for aviso in resultado.advertencias)
        self.texto.setPlainText("\n".join(lineas))
