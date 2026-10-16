"""Trabajo IA asíncrono con cancelación cooperativa y cierre seguro."""

from collections.abc import Callable

from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QWidget

from core.parser_ia import ErrorIA


class TrabajoIA(QThread):
    """Ejecuta red fuera del hilo gráfico y descarta respuestas canceladas."""

    exito = Signal(object)
    error = Signal(str)

    def __init__(self, tarea: Callable[[], object], parent: QWidget) -> None:
        super().__init__(parent)
        self._tarea = tarea

    def run(self) -> None:
        """Entrega únicamente errores sanitizados y resultados no cancelados."""
        try:
            resultado = self._tarea()
            if not self.isInterruptionRequested():
                self.exito.emit(resultado)
        except Exception as error:
            if not self.isInterruptionRequested():
                self.error.emit(
                    str(error)
                    if isinstance(error, ErrorIA)
                    else "No se pudo interpretar la respuesta. Revisa el enunciado o usa el modo manual (A)."
                )


class DialogoConTrabajo(QDialog):
    """Mantiene vivo el hilo hasta finalizar la llamada con timeout."""

    ocupado_cambiado = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.trabajo: TrabajoIA | None = None
        self._cerrar = False
        self._cancelado = False

    def iniciar(
        self, tarea: Callable[[], object], exito: Callable, error: Callable
    ) -> None:
        """Inicia un único trabajo y conecta resultados a slots del hilo gráfico."""
        if self.trabajo is not None:
            return
        self._cerrar = False
        self._cancelado = False
        self.trabajo = TrabajoIA(tarea, self)
        self._exito_callback = exito
        self._error_callback = error
        self.trabajo.exito.connect(self._exito, Qt.ConnectionType.QueuedConnection)
        self.trabajo.error.connect(self._error, Qt.ConnectionType.QueuedConnection)
        self.trabajo.finished.connect(
            self._terminar, Qt.ConnectionType.QueuedConnection
        )
        self.ocupado_cambiado.emit(True)
        self.trabajo.start()

    @Slot(object)
    def _exito(self, resultado: object) -> None:
        if not self._cancelado:
            self._exito_callback(resultado)

    @Slot(str)
    def _error(self, mensaje: str) -> None:
        if not self._cancelado:
            self._error_callback(mensaje)

    @Slot()
    def _terminar(self) -> None:
        trabajo = self.trabajo
        # finished precede la limpieza nativa del hilo; esperar aquí garantiza
        # que su padre puede cerrarse sin destruir un QThread todavía activo.
        trabajo.wait()
        self.trabajo = None
        self.ocupado_cambiado.emit(False)
        trabajo.deleteLater()
        if self._cerrar:
            super().reject()

    def cancelar(self) -> None:
        """Solicita cancelación; la conexión en curso termina por su timeout."""
        self._cancelado = True
        if self.trabajo is not None:
            self.trabajo.requestInterruption()

    def reject(self) -> None:
        """Difiere el cierre para no destruir un QThread en ejecución."""
        if self.trabajo is not None:
            self._cerrar = True
            self.cancelar()
        else:
            super().reject()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Cierra cuando termina la conexión cancelada, manteniendo Qt estable."""
        if self.trabajo is not None:
            self._cerrar = True
            self.cancelar()
            event.ignore()
        else:
            super().closeEvent(event)
