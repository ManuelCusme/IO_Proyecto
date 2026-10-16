"""Humo de navegación y atributos visibles del pivote."""

from PySide6.QtWidgets import QApplication

from core.simplex_solver import resolver_simplex
from gui.simplex_view import SimplexView
from tests.casos_taha import CASOS
from utils.paleta import COLOR_COLUMNA, COLOR_FILA, COLOR_PIVOTE


def test_navegacion_y_color(qapp: QApplication) -> None:
    """Recorre todas las tablas de Wyndor y comprueba resaltado y negrita."""
    vista = SimplexView()
    resultado = resolver_simplex(CASOS[0][0])
    vista.cargar(resultado)
    vista.show()
    for i, paso in enumerate(resultado.pasos):
        vista.barra.ir(i)
        qapp.processEvents()
        assert f"tabla {i}" in vista.encabezado.text()
        if paso.fila_pivote is not None:
            fila, col = paso.fila_pivote + 1, paso.col_pivote + 2
            item = vista.tabla.item(fila, col)
            assert item.background().color().name().upper() == COLOR_PIVOTE
            assert item.font().bold()
            assert (
                vista.tabla.item(fila, 0).background().color().name().upper()
                == COLOR_FILA
            )
            assert (
                vista.tabla.item(0, col).background().color().name().upper()
                == COLOR_COLUMNA
            )
            assert vista.operaciones.count() == len(paso.operaciones)
    assert not vista.barra.siguiente.isEnabled()
    vista.close()
