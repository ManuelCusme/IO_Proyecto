"""Humo de IA sin claves reales ni red, con QSettings aislado."""

import io
import json
from threading import Event
from time import monotonic

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QLineEdit

from core.ejemplos import EJEMPLOS
from core.parser_ia import AVISO_REVISION
from gui.ai_panel import AIPanel
from gui.ai_settings_dialog import AISettingsDialog, configuracion_ia
from gui.main_window import MainWindow


def _esperar(qapp: QApplication, dialogo: AIPanel | AISettingsDialog) -> None:
    limite = monotonic() + 5
    while dialogo.trabajo is not None and monotonic() < limite:
        qapp.processEvents()
    assert dialogo.trabajo is None


def test_modo_manual(qapp: QApplication) -> None:
    """Sin clave B está deshabilitado y A carga sin resolver automáticamente."""
    ajustes = QSettings("SimplexLab", "SimplexLab")
    ajustes.clear()
    w = MainWindow()
    w.abrir_asistente()
    panel = w.ai_panel
    assert not panel.analizar.isEnabled()
    assert "modo A" in panel.analizar.toolTip()
    panel.enunciado.setPlainText("Un enunciado de prueba")
    panel.copiar.click()
    assert "Un enunciado de prueba" in QApplication.clipboard().text()
    panel.respuesta.setPlainText("# x1 = ventanas\n" + next(iter(EJEMPLOS.values())))
    panel.cargar.click()
    assert w.panel.leer_problema().coef_obj == [3, 5]
    assert w.resultado is None
    assert AVISO_REVISION in w.panel.aviso.text()
    panel.reject()
    w.close()


def test_automatico_y_settings(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Prueba conexión y análisis en hilos con respuestas HTTP simuladas."""
    ajustes = QSettings("SimplexLab", "SimplexLab")
    ajustes.clear()
    monkeypatch.setenv("GEMINI_API_KEY", "credencial-ficticia-de-test")

    def urlopen(request: object, **kwargs: object) -> io.BytesIO:
        if request.get_method() == "GET":
            return io.BytesIO(b'{"models":[{"name":"models/modelo-ficticio"}]}')
        return io.BytesIO(
            json.dumps(
                {
                    "candidates": [
                        {
                            "content": {
                                "parts": [{"text": next(iter(EJEMPLOS.values()))}]
                            }
                        }
                    ]
                }
            ).encode()
        )

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    d = AISettingsDialog()
    assert d.clave.echoMode() == QLineEdit.EchoMode.Password
    d.probar.click()
    _esperar(qapp, d)
    assert d.modelos_disponibles.item(0).text() == "modelo-ficticio"
    d.clave.setText("otra-credencial-ficticia")
    d.guardar()
    assert configuracion_ia()[0] == "otra-credencial-ficticia"
    panel = AIPanel()
    cargados = []
    panel.problema_cargado.connect(lambda *datos: cargados.append(datos))
    panel.enunciado.setPlainText("Enunciado simulado")
    panel.analizar.click()
    _esperar(qapp, panel)
    assert len(cargados) == 1
    assert cargados[0][0].coef_obj == [3, 5]
    ajustes.clear()
    panel.close()


def test_cancelacion(qapp: QApplication) -> None:
    """Una respuesta pendiente se descarta al cancelar y el hilo termina estable."""
    panel = AIPanel()
    terminar = Event()
    resultados = []
    panel.iniciar(lambda: terminar.wait(2), resultados.append, resultados.append)
    panel.cancelar()
    terminar.set()
    _esperar(qapp, panel)
    assert not resultados
    panel.close()
