"""Pruebas de humo Qt offscreen para formulario y ventana."""

from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from core.ejemplos import EJEMPLOS
from core.parser import parsear_problema
from gui.main_window import MainWindow
from gui.steps_bar import StepsBar


def test_ventana_ejemplos(qapp: QApplication, monkeypatch) -> None:
    """Abre la ventana, carga cada ejemplo y pulsa Resolver."""
    errores = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *args: errores.append(args))
    w = MainWindow()
    w.show()
    for texto in EJEMPLOS.values():
        p = parsear_problema(texto)
        w.panel.cargar_problema(p)
        assert w.panel.leer_problema() == p
        w.panel.resolver_boton.click()
        qapp.processEvents()
        assert w.resultado is not None
    assert not errores
    w.close()


def test_validacion_historial_y_archivo(qapp: QApplication, tmp_path: Path) -> None:
    """Valida números inválidos, deshacer/rehacer y persistencia de fracciones."""
    w = MainWindow()
    w.panel.cargar_problema(parsear_problema(next(iter(EJEMPLOS.values()))))
    w.panel.coeficientes[0].setText("1/0")
    assert not w.panel.resolver_boton.isEnabled()
    w.undo_stack.undo()
    assert w.panel.coeficientes[0].text() == "3"
    w.undo_stack.redo()
    assert not w.panel.resolver_boton.isEnabled()
    w.undo_stack.undo()
    ruta = tmp_path / "problema.json"
    w.guardar_en(ruta)
    w.panel.limpiar_formulario()
    w.abrir_desde(ruta)
    assert w.panel.leer_problema() == parsear_problema(next(iter(EJEMPLOS.values())))
    w.close()


def test_barra_pasos(qapp: QApplication) -> None:
    """Respeta límites y detiene reproducción al final."""
    barra = StepsBar()
    barra.configurar(3)
    barra.alternar()
    assert barra.timer.isActive()
    barra.ir(2)
    assert not barra.timer.isActive()
    barra.ir(-1)
    assert barra.indice == 0
