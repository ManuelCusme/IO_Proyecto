"""Carga HTML de ayuda y verifica vocabulario y acceso F1."""

from PySide6.QtWidgets import QApplication, QTextBrowser

from gui.main_window import MainWindow


def test_ayuda(qapp: QApplication) -> None:
    """Los tres documentos se abren dentro de un QTextBrowser."""
    w = MainWindow()
    for nombre in ("tutorial", "glosario", "sobre"):
        dialogo = w.mostrar_ayuda(nombre)
        browser = dialogo.findChild(QTextBrowser)
        assert browser.toPlainText().strip()
        if nombre == "glosario":
            texto = browser.toPlainText().lower()
            for termino in (
                "variable básica",
                "variable no básica",
                "holgura",
                "exceso",
                "artificial",
                "pivote",
                "fila pivote",
                "columna pivote",
                "zj",
                "cj",
                "zj−cj",
                "región factible",
                "vértice",
                "óptimo múltiple",
                "no factible",
                "no acotado",
                "degeneración",
                "restricción no activa",
                "bland",
                "big-m",
                "razón mínima",
                "asistente ia",
            ):
                assert termino in texto
        dialogo.close()
    assert any(a.shortcut().toString() == "F1" for a in w.menu_ayuda.actions())
    w._oscuro(True)
    assert "#303030" in w.styleSheet()
    w._oscuro(False)
    assert "#FAFAFA" in w.styleSheet()
    w.close()
