"""Humo del formulario dinámico sin depender de la ventana principal."""

from PySide6.QtWidgets import QApplication

from gui.problem_panel import ProblemPanel


def test_dimension_y_validacion(qapp: QApplication) -> None:
    """Reconstruye campos y deshabilita Resolver ante entradas inválidas."""
    panel = ProblemPanel()
    panel.numero_variables.setValue(3)
    assert len(panel.coeficientes) == 3
    assert panel.tabla.columnCount() == 6
    panel.coeficientes[1].setText("2/0")
    assert not panel.resolver_boton.isEnabled()
    assert "denominador" in panel.coeficientes[1].toolTip()
    panel.coeficientes[1].setText("3/2")
    assert panel.resolver_boton.isEnabled()
    panel.agregar.click()
    assert panel.tabla.rowCount() == 2
    panel.tabla.cellWidget(0, 5).click()
    assert panel.tabla.rowCount() == 1
