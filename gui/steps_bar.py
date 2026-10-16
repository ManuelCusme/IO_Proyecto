"""Navegación manual y reproducción temporizada de tablas."""

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


class StepsBar(QWidget):
    """Controla el índice visible y detiene la reproducción en el último paso."""

    paso_cambiado = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.indice = 0
        self.total = 0
        layout = QHBoxLayout(self)
        self.anterior = QPushButton("◀ Anterior")
        self.etiqueta = QLabel("Paso 0 / 0")
        self.siguiente = QPushButton("Siguiente ▶")
        self.reproducir = QPushButton("▶ Reproducir")
        for w in (self.anterior, self.etiqueta, self.siguiente, self.reproducir):
            layout.addWidget(w)
        self.timer = QTimer(self)
        self.timer.setInterval(1500)
        self.timer.timeout.connect(lambda: self.ir(self.indice + 1))
        self.anterior.clicked.connect(lambda: self.ir(self.indice - 1))
        self.siguiente.clicked.connect(lambda: self.ir(self.indice + 1))
        self.reproducir.clicked.connect(self.alternar)
        self.atajos = []
        for tecla, accion in [
            ("Left", lambda: self.ir(self.indice - 1)),
            ("Right", lambda: self.ir(self.indice + 1)),
            ("Space", self.alternar),
        ]:
            atajo = QShortcut(QKeySequence(tecla), parent or self)
            atajo.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            atajo.activated.connect(accion)
            self.atajos.append(atajo)
        self.ir(0)

    def configurar(self, total: int) -> None:
        """Inicia la navegación de una nueva secuencia."""
        self.timer.stop()
        self.total = total
        self.ir(0)

    def ir(self, indice: int) -> None:
        """Mueve el índice dentro de los límites y actualiza los botones."""
        self.indice = max(0, min(indice, self.total - 1))
        if self.indice >= self.total - 1:
            self.timer.stop()
        self.anterior.setEnabled(self.indice > 0)
        self.siguiente.setEnabled(self.indice < self.total - 1)
        self.reproducir.setEnabled(self.total > 1)
        self.reproducir.setText("⏸ Pausar" if self.timer.isActive() else "▶ Reproducir")
        self.etiqueta.setText(
            f"Paso {self.indice+1 if self.total else 0} / {self.total}"
        )
        self.paso_cambiado.emit(self.indice)

    def alternar(self) -> None:
        """Pausa o reproduce; desde el final vuelve al primer paso."""
        if self.timer.isActive():
            self.timer.stop()
        elif self.total > 1:
            if self.indice == self.total - 1:
                self.ir(0)
            self.timer.start()
        self.reproducir.setText("⏸ Pausar" if self.timer.isActive() else "▶ Reproducir")
