"""Tablas Simplex exactas con pivote y operaciones elementales visibles."""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.models import ResultadoSimplex
from gui.steps_bar import StepsBar
from utils.paleta import COLOR_COLUMNA, COLOR_FILA, COLOR_PIVOTE, COLOR_Z


class SimplexView(QWidget):
    """Presenta una secuencia automática de tablas sin elección manual de pivote."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.resultado: ResultadoSimplex | None = None
        layout = QVBoxLayout(self)
        self.encabezado = QLabel("Sin tablas")
        self.narrativa = QLabel()
        self.narrativa.setWordWrap(True)
        self.tabla = QTableWidget()
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setToolTip(
            "La columna azul entra; la fila verde sale; amarillo marca el pivote."
        )
        self.operaciones = QListWidget()
        self.operaciones.setMaximumHeight(150)
        self.barra = StepsBar(self)
        self.barra.paso_cambiado.connect(self.mostrar_paso)
        layout.addWidget(self.encabezado)
        layout.addWidget(self.narrativa)
        layout.addWidget(self.tabla)
        layout.addWidget(QLabel("Operaciones entre filas de este paso"))
        layout.addWidget(self.operaciones)
        layout.addWidget(self.barra)

    def cargar(self, resultado: ResultadoSimplex) -> None:
        """Carga todas las instantáneas y se sitúa en la tabla inicial."""
        self.resultado = resultado
        self.barra.configurar(len(resultado.pasos))

    def mostrar_paso(self, indice: int) -> None:
        """Dibuja Cj, base, Cb, restricciones, razones y Zj − Cj."""
        if self.resultado is None or not self.resultado.pasos:
            return
        paso = self.resultado.pasos[indice]
        self.encabezado.setText(
            f"Paso {indice+1} de {len(self.resultado.pasos)} (tabla {paso.numero})"
        )
        self.narrativa.setText(paso.mensaje + "\n" + "\n".join(paso.advertencias))
        encabezados = ["Base", "Cb"] + paso.encabezados + ["Razón"]
        filas = [["Cj", ""] + [str(c) for c in paso.cj] + ["", ""]]
        filas += [
            [n, str(c)]
            + [str(v) for v in f]
            + [str(razon) if razon is not None else "—"]
            for n, c, f, razon in zip(paso.base, paso.cb, paso.tabla, paso.razones)
        ]
        filas += [["Zj − Cj", ""] + [str(z) for z in paso.fila_z] + [""]]
        self.tabla.setRowCount(len(filas))
        self.tabla.setColumnCount(len(encabezados))
        self.tabla.setHorizontalHeaderLabels(encabezados)
        for i, fila in enumerate(filas):
            for j, texto in enumerate(fila):
                item = QTableWidgetItem(texto)
                color = COLOR_Z if i == len(filas) - 1 else "#FFFFFF"
                if paso.col_pivote is not None and j == paso.col_pivote + 2:
                    color = COLOR_COLUMNA
                if paso.fila_pivote is not None and i == paso.fila_pivote + 1:
                    color = COLOR_FILA
                    if j == paso.col_pivote + 2:
                        color = COLOR_PIVOTE
                        fuente = item.font()
                        fuente.setBold(True)
                        item.setFont(fuente)
                        item.setToolTip(f"Elemento pivote: {paso.elemento_pivote}")
                item.setBackground(QColor(color))
                self.tabla.setItem(i, j, item)
        self.tabla.resizeColumnsToContents()
        self.operaciones.clear()
        self.operaciones.addItems(
            paso.operaciones or ["No se requieren más operaciones."]
        )
