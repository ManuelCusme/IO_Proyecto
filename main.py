"""Punto de entrada de la aplicación de escritorio SimplexLab."""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from gui.main_window import MainWindow
from utils.logging_setup import configurar_logging


def main() -> int:
    """Inicia Qt e instala una barrera de errores amigables."""
    app = QApplication(sys.argv)
    app.setApplicationName("SimplexLab")
    app.setOrganizationName("SimplexLab")
    try:
        configurar_logging()
    except OSError:
        app.setProperty("logging_disponible", False)
    sys.excepthook = lambda *_: QMessageBox.warning(
        None,
        "SimplexLab",
        "No se pudo completar la acción. Revisa los datos y vuelve a intentarlo.",
    )
    ventana = MainWindow()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
