"""Asistente opcional para traducir un párrafo al formulario revisable."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.models import Problema
from core.parser import ParseError
from core.parser_ia import (
    AVISO_REVISION,
    ClienteGemini,
    ErrorIA,
    analizar_enunciado,
    construir_prompt,
    problema_desde_respuesta,
)
from gui.ai_settings_dialog import configuracion_ia
from gui.ai_worker import DialogoConTrabajo


class AIPanel(DialogoConTrabajo):
    """Ofrece modos manual y automático que solo cargan datos para revisar."""

    problema_cargado = Signal(object, object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Asistente IA")
        self.resize(700, 760)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enunciado del problema"))
        self.enunciado = QTextEdit()
        self.enunciado.setToolTip(
            "Pega el enunciado; omite datos personales si usarás Gemini."
        )
        layout.addWidget(self.enunciado)
        self.tabs = QTabWidget()
        manual, automatico = QWidget(), QWidget()
        lm, la = QVBoxLayout(manual), QVBoxLayout(automatico)
        self.copiar = QPushButton("Copiar prompt")
        self.copiar.setToolTip(
            "Copia el prompt para usarlo en el chat de IA de tu elección."
        )
        self.copiar.clicked.connect(self.copiar_prompt)
        lm.addWidget(self.copiar)
        lm.addWidget(QLabel("Pega aquí la respuesta de la IA"))
        self.respuesta = QTextEdit()
        self.respuesta.setToolTip("Respuesta en formato max/min, s.a. y restricciones.")
        lm.addWidget(self.respuesta)
        self.cargar = QPushButton("Cargar en el formulario")
        self.cargar.setToolTip(
            "Valida y carga los datos; deberás revisarlos y pulsar Resolver."
        )
        self.cargar.clicked.connect(self.cargar_respuesta)
        lm.addWidget(self.cargar)
        privacidad = QLabel(
            "El enunciado se envía a Google. No incluyas datos personales. En la capa gratuita, Google puede usar los datos enviados para mejorar sus productos."
        )
        privacidad.setWordWrap(True)
        la.addWidget(privacidad)
        self.analizar = QPushButton("Analizar con Gemini")
        self.analizar.clicked.connect(self.analizar_gemini)
        la.addWidget(self.analizar)
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 0)
        self.progreso.hide()
        la.addWidget(self.progreso)
        self.cancelar_boton = QPushButton("Cancelar")
        self.cancelar_boton.setToolTip(
            "Descarta la respuesta; la conexión en curso termina con su timeout."
        )
        self.cancelar_boton.setEnabled(False)
        self.cancelar_boton.clicked.connect(self._cancelar)
        la.addWidget(self.cancelar_boton)
        la.addStretch()
        self.tabs.addTab(manual, "Modo A: manual (sin clave)")
        self.tabs.addTab(automatico, "Modo B: automático (Gemini)")
        layout.addWidget(self.tabs)
        self.mensaje = QLabel(AVISO_REVISION)
        self.mensaje.setWordWrap(True)
        layout.addWidget(self.mensaje)
        self.ocupado_cambiado.connect(self._ocupado)
        self.actualizar_configuracion()

    def actualizar_configuracion(self) -> None:
        """Habilita modo B únicamente si existe una clave local o de entorno."""
        clave, _ = configuracion_ia()
        self.analizar.setEnabled(bool(clave) and self.trabajo is None)
        self.analizar.setToolTip(
            "Analiza el enunciado sin resolverlo."
            if clave
            else "No hay clave configurada. Usa el modo A o Herramientas → Configuración de IA."
        )

    def copiar_prompt(self) -> None:
        """Copia el prompt al portapapeles sin acceder a la red."""
        QApplication.clipboard().setText(construir_prompt(self.enunciado.toPlainText()))
        self.mensaje.setText(
            "Prompt copiado. Pégalo en tu chat de IA y devuelve aquí su respuesta."
        )

    def cargar_respuesta(self) -> None:
        """Valida la respuesta manual y carga únicamente el formulario."""
        try:
            self._cargar(problema_desde_respuesta(self.respuesta.toPlainText()))
        except (ErrorIA, ParseError) as error:
            self.mensaje.setText(str(error))

    def _cargar(self, resultado: tuple[Problema, list[str]]) -> None:
        problema, leyenda = resultado
        if len(problema.nombres) > 10:
            self.mensaje.setText(
                "El formulario admite hasta 10 variables. Revisa el enunciado."
            )
            return
        self.problema_cargado.emit(problema, leyenda)
        self.mensaje.setText("\n".join(leyenda + [AVISO_REVISION]))

    def analizar_gemini(self) -> None:
        """Inicia una consulta solo tras pulsar el botón explícito del modo B."""
        if not self.enunciado.toPlainText().strip():
            self.mensaje.setText("Introduce el enunciado antes de analizar.")
            return
        try:
            clave, modelo = configuracion_ia()
            cliente = ClienteGemini(clave, modelo)
            enunciado = self.enunciado.toPlainText()
            self.mensaje.setText("Analizando con Gemini…")
            self.iniciar(
                lambda: analizar_enunciado(enunciado, cliente),
                self._cargar,
                self.mensaje.setText,
            )
        except ErrorIA as error:
            self.mensaje.setText(str(error))

    def _ocupado(self, ocupado: bool) -> None:
        self.progreso.setVisible(ocupado)
        self.cancelar_boton.setEnabled(ocupado)
        self.actualizar_configuracion()

    def _cancelar(self) -> None:
        self.cancelar()
        self.cancelar_boton.setEnabled(False)
        self.mensaje.setText(
            "Consulta cancelada. Se descartará la respuesta; el modo manual sigue disponible."
        )
