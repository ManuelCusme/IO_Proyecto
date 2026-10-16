"""Entorno Qt sin pantalla y sin configuración privada del usuario."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp(tmp_path_factory: pytest.TempPathFactory) -> QApplication:
    """Proporciona una aplicación con QSettings aislado de la cuenta real."""
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        str(tmp_path_factory.mktemp("settings")),
    )
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def sin_clave_real(monkeypatch: pytest.MonkeyPatch) -> None:
    """Impide que tests hereden una credencial real del entorno."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


@pytest.fixture(autouse=True)
def sin_red_real(monkeypatch: pytest.MonkeyPatch) -> None:
    """Toda prueba de Gemini debe sustituir explícitamente urlopen con un mock."""

    def bloquear(*args: object, **kwargs: object) -> None:
        raise AssertionError("Los tests no pueden acceder a internet.")

    monkeypatch.setattr("urllib.request.urlopen", bloquear)
