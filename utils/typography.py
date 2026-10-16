"""Tipografía portátil para Qt, también en plataformas sin fuentes de sistema."""

from pathlib import Path

from matplotlib import get_data_path
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


def configurar_tipografia() -> None:
    """Carga DejaVu Sans de Matplotlib para conservar texto y símbolos legibles."""
    app = QApplication.instance()
    if app is None or app.property("tipografia_configurada"):
        return
    fuente = Path(get_data_path()) / "fonts" / "ttf" / "DejaVuSans.ttf"
    identificador = QFontDatabase.addApplicationFont(str(fuente))
    familias = QFontDatabase.applicationFontFamilies(identificador)
    if familias:
        app.setFont(QFont(familias[0], 10))
        app.setProperty("tipografia_configurada", True)
