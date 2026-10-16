"""Formulario dinámico de coeficientes con validación inmediata."""

from fractions import Fraction

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.models import Problema, Restriccion


class ProblemPanel(QWidget):
    """Editor exacto del problema; nunca inicia cálculos al cargar datos."""

    resolver = Signal()
    ejemplos = Signal()
    asistente = Signal()
    estado_cambiado = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cargando = True
        self.nombres = ["x1", "x2"]
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Problema de programación lineal"))
        sentidos = QHBoxLayout()
        self.maximizar = QRadioButton("Maximizar")
        self.minimizar = QRadioButton("Minimizar")
        self.maximizar.setChecked(True)
        self.maximizar.setToolTip("Busca el mayor valor de Z.")
        self.minimizar.setToolTip("Busca el menor valor de Z, sin cambiar su signo.")
        sentidos.addWidget(self.maximizar)
        sentidos.addWidget(self.minimizar)
        layout.addLayout(sentidos)
        self.numero_variables = QSpinBox()
        self.numero_variables.setRange(1, 10)
        self.numero_variables.setValue(2)
        self.numero_variables.setToolTip("Número de variables no negativas (1 a 10).")
        layout.addWidget(QLabel("Número de variables"))
        layout.addWidget(self.numero_variables)
        self.objetivo_layout = QHBoxLayout()
        layout.addLayout(self.objetivo_layout)
        self.coeficientes: list[QLineEdit] = []
        self.tabla = QTableWidget()
        self.tabla.setToolTip(
            "Coeficientes, operador y término independiente de cada restricción."
        )
        layout.addWidget(self.tabla)
        self.agregar = QPushButton("+ Añadir restricción")
        self.agregar.setToolTip("Agrega una fila al sistema de restricciones.")
        self.agregar.clicked.connect(lambda: self.agregar_restriccion())
        layout.addWidget(self.agregar)
        layout.addWidget(QLabel("Todas las variables son ≥ 0."))
        self.error = QLabel()
        self.error.setWordWrap(True)
        self.error.setStyleSheet("color: #C62828")
        layout.addWidget(self.error)
        self.aviso = QLabel()
        self.aviso.setWordWrap(True)
        layout.addWidget(self.aviso)
        botones = QHBoxLayout()
        self.cargar_ejemplo = QPushButton("Cargar ejemplo")
        self.limpiar = QPushButton("Limpiar")
        self.resolver_boton = QPushButton("Resolver")
        self.resolver_boton.setStyleSheet(
            "background: #1976D2; color: white; padding: 8px"
        )
        for boton, ayuda in [
            (self.cargar_ejemplo, "Carga un problema académico para explorar."),
            (self.limpiar, "Vacía el formulario."),
            (
                self.resolver_boton,
                "Resuelve los datos revisados con aritmética exacta.",
            ),
        ]:
            boton.setToolTip(ayuda)
            botones.addWidget(boton)
        layout.addLayout(botones)
        self.ai_boton = QPushButton("Asistente IA")
        self.ai_boton.setToolTip(
            "Convierte un enunciado en datos para revisar antes de resolver."
        )
        self.ai_boton.hide()
        layout.addWidget(self.ai_boton)
        self.ai_boton.clicked.connect(self.asistente.emit)
        self.cargar_ejemplo.clicked.connect(self.ejemplos.emit)
        self.limpiar.clicked.connect(self.limpiar_formulario)
        self.resolver_boton.clicked.connect(self.resolver.emit)
        self.numero_variables.valueChanged.connect(self._cambiar_dimension)
        self.maximizar.toggled.connect(self._cambio)
        self.tabla.itemChanged.connect(self._cambio)
        self._construir(2)
        self._cargando = False
        self._cambio()

    def _construir(self, n: int) -> None:
        while self.objetivo_layout.count():
            item = self.objetivo_layout.takeAt(0)
            item.widget().deleteLater()
        self.objetivo_layout.addWidget(QLabel("Z ="))
        self.coeficientes = []
        for i in range(n):
            campo = QLineEdit("0")
            campo.setMaximumWidth(75)
            campo.setToolTip(
                "Coeficiente exacto: entero, decimal o fracción, por ejemplo 3/2."
            )
            campo.textChanged.connect(self._cambio)
            self.coeficientes.append(campo)
            self.objetivo_layout.addWidget(campo)
            self.objetivo_layout.addWidget(QLabel(self.nombres[i]))
        self.tabla.setRowCount(0)
        self.tabla.setColumnCount(n + 3)
        self.tabla.setHorizontalHeaderLabels(self.nombres + ["≤ / ≥ / =", "RHS", "−"])
        self.agregar_restriccion()

    def _cambiar_dimension(self, n: int) -> None:
        if self._cargando:
            return
        self._cargando = True
        self.nombres = [f"x{i+1}" for i in range(n)]
        self._construir(n)
        self._cargando = False
        self._cambio()

    def agregar_restriccion(self) -> None:
        """Añade una restricción inicialmente nula."""
        previo = self._cargando
        self._cargando = True
        n = self.numero_variables.value()
        i = self.tabla.rowCount()
        self.tabla.insertRow(i)
        for j in list(range(n)) + [n + 1]:
            item = QTableWidgetItem("0")
            item.setToolTip("Admite enteros, decimales y fracciones a/b.")
            self.tabla.setItem(i, j, item)
        operador = QComboBox()
        operador.addItems(["<=", ">=", "="])
        operador.setToolTip("Sentido de la restricción.")
        operador.currentTextChanged.connect(self._cambio)
        self.tabla.setCellWidget(i, n, operador)
        eliminar = QPushButton("−")
        eliminar.setToolTip("Elimina esta restricción.")
        eliminar.clicked.connect(lambda: self._eliminar(eliminar))
        self.tabla.setCellWidget(i, n + 2, eliminar)
        self._cargando = previo
        self._cambio()

    def _eliminar(self, boton: QPushButton) -> None:
        n = self.numero_variables.value()
        for i in range(self.tabla.rowCount()):
            if self.tabla.cellWidget(i, n + 2) is boton:
                self.tabla.removeRow(i)
                break
        self._cambio()

    def leer_problema(self) -> Problema:
        """Valida y devuelve una copia independiente de los datos del formulario."""
        n = self.numero_variables.value()
        coefs = [Fraction(c.text().strip()) for c in self.coeficientes]
        rs = [
            Restriccion(
                [Fraction(self.tabla.item(i, j).text().strip()) for j in range(n)],
                self.tabla.cellWidget(i, n).currentText(),
                Fraction(self.tabla.item(i, n + 1).text().strip()),
            )
            for i in range(self.tabla.rowCount())
        ]
        return Problema(
            "max" if self.maximizar.isChecked() else "min", coefs, rs, self.nombres
        )

    def _cambio(self, *_args: object) -> None:
        if self._cargando:
            return
        n = self.numero_variables.value()
        self.tabla.blockSignals(True)
        valido = True
        for campo in self.coeficientes:
            try:
                Fraction(campo.text().strip())
                campo.setStyleSheet("")
                campo.setToolTip("Coeficiente exacto: entero, decimal o fracción.")
            except (ValueError, ZeroDivisionError):
                campo.setStyleSheet("background: #FFCDD2")
                campo.setToolTip(
                    "Introduce un entero, decimal o fracción con denominador distinto de cero."
                )
                valido = False

        for i in range(self.tabla.rowCount()):
            for j in list(range(n)) + [n + 1]:
                item = self.tabla.item(i, j)
                try:
                    Fraction(item.text().strip())
                    item.setBackground(QColor("#FFFFFF"))
                    item.setToolTip("Número exacto válido.")
                except (ValueError, ZeroDivisionError, AttributeError):
                    valido = False
                    if item:
                        item.setBackground(QColor("#FFCDD2"))
                        item.setToolTip(
                            "Introduce un entero, decimal o fracción con denominador distinto de cero."
                        )
        valido = valido and self.tabla.rowCount() > 0
        self.resolver_boton.setEnabled(valido)
        self.error.setText(
            "" if valido else "Revisa los números e incluye al menos una restricción."
        )
        self.tabla.blockSignals(False)
        self.estado_cambiado.emit()

    def snapshot(self) -> dict:
        """Captura incluso entradas incompletas para deshacer y rehacer."""
        n = self.numero_variables.value()
        return {
            "n": n,
            "nombres": self.nombres[:],
            "sentido": "max" if self.maximizar.isChecked() else "min",
            "coefs": [c.text() for c in self.coeficientes],
            "rs": [
                [self.tabla.item(i, j).text() for j in range(n)]
                + [
                    self.tabla.cellWidget(i, n).currentText(),
                    self.tabla.item(i, n + 1).text(),
                ]
                for i in range(self.tabla.rowCount())
            ],
        }

    def restaurar(self, estado: dict) -> None:
        """Restaura una instantánea sin resolver el problema."""
        self._cargando = True
        self.numero_variables.setValue(estado["n"])
        self.nombres = estado["nombres"][:]
        self.maximizar.setChecked(estado["sentido"] == "max")
        self.minimizar.setChecked(estado["sentido"] == "min")
        self._construir(estado["n"])
        for campo, texto in zip(self.coeficientes, estado["coefs"]):
            campo.setText(texto)
        self.tabla.setRowCount(0)
        n = estado["n"]
        for i, fila in enumerate(estado["rs"]):
            self.agregar_restriccion()
            for j in range(n):
                self.tabla.item(i, j).setText(fila[j])
            self.tabla.cellWidget(i, n).setCurrentText(fila[n])
            self.tabla.item(i, n + 1).setText(fila[n + 1])
        self._cargando = False
        self._cambio()

    def cargar_problema(self, problema: Problema) -> None:
        """Carga los datos exactos manteniendo los nombres originales."""
        p = problema
        self.aviso.clear()
        self.restaurar(
            {
                "n": len(p.nombres),
                "nombres": p.nombres,
                "sentido": p.sentido,
                "coefs": [str(c) for c in p.coef_obj],
                "rs": [
                    [str(c) for c in r.coefs] + [r.tipo, str(r.rhs)]
                    for r in p.restricciones
                ],
            }
        )

    def limpiar_formulario(self) -> None:
        """Restaura el formulario de dos variables sin resultados previos."""
        self.cargar_problema(Problema("max", [0, 0], [Restriccion([0, 0], "<=", 0)]))
