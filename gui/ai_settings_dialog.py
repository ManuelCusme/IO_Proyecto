"""Configuración local y prueba explícita de modelos disponibles en Gemini."""

import os
import re

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.parser_ia import MODELO_PREDETERMINADO, ClienteGemini, ErrorIA
from gui.ai_worker import DialogoConTrabajo


def configuracion_ia() -> tuple[str, str]:
    """Lee ajustes locales con prioridad sobre GEMINI_API_KEY."""
    ajustes = QSettings("SimplexLab", "SimplexLab")
    clave = (
        str(ajustes.value("ia/clave", "")).strip()
        or os.environ.get("GEMINI_API_KEY", "").strip()
    )
    modelo = (
        str(ajustes.value("ia/modelo", MODELO_PREDETERMINADO)).strip()
        or MODELO_PREDETERMINADO
    )
    return clave, modelo


class AISettingsDialog(DialogoConTrabajo):
    """Edita clave enmascarada y modelo sin registrar información privada."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configuración de IA")
        self.resize(560, 440)
        layout = QVBoxLayout(self)
        clave, modelo = configuracion_ia()
        self.clave = QLineEdit(clave)
        self.clave.setEchoMode(QLineEdit.EchoMode.Password)
        self.clave.setToolTip(
            "Clave gratuita de Gemini; se guarda solo en este equipo."
        )
        self.modelo = QComboBox()
        self.modelo.setEditable(True)
        self.modelo.addItem(modelo)
        self.modelo.setToolTip(
            "Modelo configurable. Probar conexión muestra los disponibles."
        )
        layout.addWidget(QLabel("Clave de API"))
        layout.addWidget(self.clave)
        layout.addWidget(QLabel("Modelo"))
        layout.addWidget(self.modelo)
        aviso = QLabel(
            "La clave se guarda sin cifrar en este equipo mediante QSettings. También puedes usar GEMINI_API_KEY."
        )
        aviso.setWordWrap(True)
        layout.addWidget(aviso)
        enlace = QLabel(
            '<a href="https://aistudio.google.com/apikey">Obtener una clave gratuita en Google AI Studio</a>'
        )
        enlace.setOpenExternalLinks(True)
        layout.addWidget(enlace)
        self.probar = QPushButton("Probar conexión")
        self.probar.setToolTip(
            "Consulta a Google los modelos disponibles usando los datos actuales."
        )
        self.probar.clicked.connect(self.probar_conexion)
        layout.addWidget(self.probar)
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 0)
        self.progreso.hide()
        layout.addWidget(self.progreso)
        self.modelos_disponibles = QListWidget()
        self.modelos_disponibles.itemDoubleClicked.connect(
            lambda item: self.modelo.setCurrentText(item.text())
        )
        layout.addWidget(self.modelos_disponibles)
        self.mensaje = QLabel()
        self.mensaje.setWordWrap(True)
        layout.addWidget(self.mensaje)
        self.botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.botones.accepted.connect(self.guardar)
        self.botones.rejected.connect(self.reject)
        layout.addWidget(self.botones)
        self.ocupado_cambiado.connect(self._ocupado)

    def _ocupado(self, ocupado: bool) -> None:
        self.progreso.setVisible(ocupado)
        self.probar.setEnabled(not ocupado)
        self.botones.button(QDialogButtonBox.StandardButton.Save).setEnabled(
            not ocupado
        )

    def probar_conexion(self) -> None:
        """Consulta modelos en QThread sin persistir los campos del diálogo."""
        try:
            cliente = ClienteGemini(self.clave.text(), self.modelo.currentText())
            self.mensaje.setText("Consultando modelos…")
            self.iniciar(cliente.probar_conexion, self._modelos, self.mensaje.setText)
        except ErrorIA as error:
            self.mensaje.setText(str(error))

    def _modelos(self, modelos: list[str]) -> None:
        self.modelos_disponibles.clear()
        self.modelos_disponibles.addItems(modelos)
        self.mensaje.setText(
            "Conexión correcta. Haz doble clic en un modelo para seleccionarlo."
        )

    def guardar(self) -> None:
        """Guarda solo cuando el usuario pulsa Guardar; no registra la clave."""
        modelo = self.modelo.currentText().strip()
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", modelo):
            self.mensaje.setText("Introduce un nombre de modelo válido.")
            return
        ajustes = QSettings("SimplexLab", "SimplexLab")
        ajustes.setValue("ia/clave", self.clave.text().strip())
        ajustes.setValue("ia/modelo", modelo)
        ajustes.sync()
        if ajustes.status() != QSettings.Status.NoError:
            self.mensaje.setText("No se pudo guardar la configuración local.")
            return
        self.accept()
