"""Humo de Matplotlib embebido y exclusión de problemas de más dimensiones."""

from PySide6.QtWidgets import QApplication

from core.graphic_solver import resolver_grafico
from core.models import Problema, Restriccion
from gui.graphic_view import GraphicView
from gui.main_window import MainWindow
from tests.casos_taha import CASOS


def test_dibujo_wyndor(qapp: QApplication) -> None:
    """El canvas contiene todos los puntos y el óptimo rojo independiente."""
    vista = GraphicView()
    r = resolver_grafico(CASOS[0][0])
    vista.dibujar(r)
    assert len(vista.puntos_vertices.get_offsets()) == len(r.vertices)
    assert len(vista.puntos_optimos.get_offsets()) == 1
    assert "36" in vista.ax.get_title()
    assert vista.ax.get_xlim()[0] == 0
    assert len(vista.ax.patches) == 1
    vista.close()


def test_tres_variables(qapp: QApplication) -> None:
    """Con tres variables queda deshabilitada la vista con el mensaje especificado."""
    w = MainWindow()
    w.panel.cargar_problema(
        Problema("max", [1, 1, 1], [Restriccion([1, 1, 1], "<=", 5)])
    )
    w.panel.resolver_boton.click()
    assert not w.boton_grafico.isEnabled()
    assert not w.graphic_view.isEnabled()
    assert (
        w.mensaje_grafico.text()
        == "El método gráfico solo aplica a problemas de 2 variables."
    )
    w.panel.cargar_problema(CASOS[0][0])
    w.panel.resolver_boton.click()
    assert w.boton_grafico.isEnabled()
    assert w.graphic_view.resultado.z_optimo == 36
    w._metodo("Solo Simplex")
    assert not w.boton_grafico.isEnabled()
    w._metodo("Solo gráfico")
    assert not w.boton_simplex.isEnabled()
    w.close()
