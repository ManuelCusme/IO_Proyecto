"""Ventana principal y coordinación de los servicios de SimplexLab."""

import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QActionGroup, QUndoCommand, QUndoStack
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from core.ejemplos import EJEMPLOS
from core.graphic_solver import resolver_grafico
from core.models import Problema, Restriccion, ResultadoSimplex
from core.parser import parsear_problema
from core.simplex_solver import ErrorInterno, resolver_simplex
from gui.graphic_view import GraphicView
from gui.problem_panel import ProblemPanel
from gui.resultado_panel import ResultadoPanel
from gui.simplex_view import SimplexView


class _Edicion(QUndoCommand):
    def __init__(self, ventana: "MainWindow", previo: dict, nuevo: dict) -> None:
        super().__init__("Editar problema")
        self.ventana, self.previo, self.nuevo = ventana, previo, nuevo
        self._primera = True

    def undo(self) -> None:
        """Restaura la edición anterior."""
        self.ventana.restaurar(self.previo)

    def redo(self) -> None:
        """Reaplica la edición sin reconstruir el campo que se está editando."""
        if self._primera:
            self._primera = False
        else:
            self.ventana.restaurar(self.nuevo)


class MainWindow(QMainWindow):
    """Coordina entrada, selección de método y resultados sin lógica matemática."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SimplexLab")
        self.setMinimumSize(1200, 800)
        self._oscuro(False)
        self.dialogos_ayuda: list[QDialog] = []
        self.problema: Problema | None = None
        self.resultado: ResultadoSimplex | None = None
        self.resolver_backend = resolver_simplex
        self.metodo = "Automático"
        self.panel = ProblemPanel()
        self.resultado_panel = ResultadoPanel()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.resultado_panel)
        self.simplex_view = SimplexView()
        self.stack.addWidget(self.simplex_view)
        self.graphic_view = GraphicView()
        self.stack.addWidget(self.graphic_view)
        derecho = QWidget()
        ld = QVBoxLayout(derecho)
        self.selector = QHBoxLayout()
        resultado = QPushButton("Resultado")
        resultado.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.resultado_panel)
        )
        self.selector.addWidget(resultado)
        self.boton_simplex = QPushButton("Simplex")
        self.boton_simplex.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.simplex_view)
        )
        self.selector.addWidget(self.boton_simplex)
        self.boton_grafico = QPushButton("Gráfico")
        self.boton_grafico.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.graphic_view)
        )
        self.selector.addWidget(self.boton_grafico)
        ld.addLayout(self.selector)
        self.mensaje_grafico = QLabel()
        self.mensaje_grafico.setWordWrap(True)
        ld.addWidget(self.mensaje_grafico)
        ld.addWidget(self.stack)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.panel)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(scroll)
        splitter.addWidget(derecho)
        splitter.setSizes([430, 770])
        self.setCentralWidget(splitter)
        self.undo_stack = QUndoStack(self)
        self._restaurando = False
        self._estado = self.panel.snapshot()
        self.panel.estado_cambiado.connect(self._registrar)
        self.panel.resolver.connect(self.on_resolve_clicked)
        self.panel.ejemplos.connect(self.cargar_ejemplo)
        self._menus()
        self.panel.estado_cambiado.connect(self._actualizar_metodos)
        self._actualizar_metodos()
        self.statusBar().showMessage("Listo")

    def _accion(
        self, menu: object, texto: str, callback: object, atajo: str | None = None
    ) -> QAction:
        accion = QAction(texto, self)
        accion.triggered.connect(callback)
        if atajo:
            accion.setShortcut(atajo)
        menu.addAction(accion)
        return accion

    def _menus(self) -> None:
        archivo = self.menuBar().addMenu("Archivo")
        self._accion(archivo, "Nuevo", self.panel.limpiar_formulario, "Ctrl+N")
        self._accion(archivo, "Abrir", self.abrir, "Ctrl+O")
        self._accion(archivo, "Guardar", self.guardar, "Ctrl+S")
        self._accion(archivo, "Salir", self.close, "Ctrl+Q")
        self.menu_archivo = archivo
        editar = self.menuBar().addMenu("Editar")
        deshacer = self.undo_stack.createUndoAction(self, "Deshacer")
        deshacer.setShortcut("Ctrl+Z")
        editar.addAction(deshacer)
        rehacer = self.undo_stack.createRedoAction(self, "Rehacer")
        rehacer.setShortcut("Ctrl+Y")
        editar.addAction(rehacer)
        self._accion(editar, "Limpiar", self.panel.limpiar_formulario)
        self.menu_ver = self.menuBar().addMenu("Ver")
        self._accion(
            self.menu_ver,
            "Resultado",
            lambda: self.stack.setCurrentWidget(self.resultado_panel),
        )
        self.accion_simplex = self._accion(
            self.menu_ver,
            "Vista Simplex",
            lambda: self.stack.setCurrentWidget(self.simplex_view),
        )
        self.accion_grafico = self._accion(
            self.menu_ver,
            "Vista gráfica",
            lambda: self.stack.setCurrentWidget(self.graphic_view),
        )
        self.oscuro = self._accion(self.menu_ver, "Modo oscuro", self._oscuro)
        self.oscuro.setCheckable(True)
        metodo = self.menuBar().addMenu("Método")
        self.grupo_metodo = QActionGroup(self)
        for nombre in ("Automático", "Solo gráfico", "Solo Simplex"):
            a = self._accion(
                metodo, nombre, lambda checked=False, n=nombre: self._metodo(n)
            )
            a.setCheckable(True)
            a.setChecked(nombre == self.metodo)
            self.grupo_metodo.addAction(a)
        self.menu_ayuda = self.menuBar().addMenu("Ayuda")
        self._accion(
            self.menu_ayuda, "Tutorial", lambda: self.mostrar_ayuda("tutorial"), "F1"
        )
        self._accion(
            self.menu_ayuda, "Glosario", lambda: self.mostrar_ayuda("glosario")
        )
        self._accion(self.menu_ayuda, "Acerca de", lambda: self.mostrar_ayuda("sobre"))
        self._accion(self.menu_ayuda, "Cargar ejemplo", self.cargar_ejemplo)

    def _metodo(self, nombre: str) -> None:
        self.metodo = nombre
        self._actualizar_metodos()
        self.statusBar().showMessage(f"Método: {nombre}")

    def _actualizar_metodos(self) -> None:
        aplica = self.panel.numero_variables.value() == 2
        grafico = aplica and self.metodo != "Solo Simplex"
        self.boton_grafico.setEnabled(grafico)
        self.graphic_view.setEnabled(grafico)
        self.accion_grafico.setEnabled(grafico)
        self.boton_simplex.setEnabled(self.metodo != "Solo gráfico")
        self.accion_simplex.setEnabled(self.metodo != "Solo gráfico")
        mensaje = (
            "El método gráfico solo aplica a problemas de 2 variables."
            if not aplica
            else ""
        )
        self.mensaje_grafico.setText(mensaje)
        self.boton_grafico.setToolTip(mensaje or "Resultado final por método gráfico.")

    def _oscuro(self, activo: bool) -> None:
        nombre = "dark.qss" if activo else "light.qss"
        ruta = Path(__file__).resolve().parents[1] / "resources" / "styles" / nombre
        self.setStyleSheet(ruta.read_text(encoding="utf-8"))

    def mostrar_ayuda(self, nombre: str) -> QDialog:
        """Abre un documento HTML local en una ventana de ayuda no modal."""
        if nombre not in ("tutorial", "glosario", "sobre"):
            raise ValueError("Documento de ayuda desconocido.")
        dialogo = QDialog(self)
        dialogo.setWindowTitle(
            {"tutorial": "Tutorial", "glosario": "Glosario", "sobre": "Acerca de"}[
                nombre
            ]
        )
        layout = QVBoxLayout(dialogo)
        browser = QTextBrowser()
        browser.setHtml(
            (Path(__file__).with_name("help") / f"{nombre}.html").read_text(
                encoding="utf-8"
            )
        )
        layout.addWidget(browser)
        dialogo.resize(780, 620)
        self.dialogos_ayuda.append(dialogo)
        dialogo.show()
        return dialogo

    def _registrar(self) -> None:
        if self._restaurando:
            return
        nuevo = self.panel.snapshot()
        if nuevo != self._estado:
            previo = self._estado
            self._estado = nuevo
            self.undo_stack.push(_Edicion(self, previo, nuevo))

    def restaurar(self, estado: dict) -> None:
        """Aplica una edición sin añadirla otra vez al historial."""
        self._restaurando = True
        self.panel.restaurar(estado)
        self._estado = estado
        self._restaurando = False

    def on_resolve_clicked(self) -> None:
        """Invoca el servicio de resolución; el callable permite migrarlo a QThread."""
        try:
            self.statusBar().showMessage("Resolviendo…")
            p = self.panel.leer_problema()
            r = self.resolver_backend(p)
            self.problema, self.resultado = p, r
            self.resultado_panel.mostrar(r)
            self.simplex_view.cargar(r)
            self._actualizar_metodos()
            if len(p.nombres) == 2 and self.metodo != "Solo Simplex":
                self.graphic_view.dibujar(resolver_grafico(p))
            self.stack.setCurrentWidget(
                self.simplex_view
                if self.metodo != "Solo gráfico"
                else (
                    self.graphic_view if len(p.nombres) == 2 else self.resultado_panel
                )
            )
            self.statusBar().showMessage(
                {
                    "optimo": "Óptimo alcanzado",
                    "multiple": "Óptimo múltiple",
                    "no_factible": "Problema no factible",
                    "no_acotado": "Problema no acotado",
                }[r.estado]
            )
        except Exception as error:
            self.statusBar().showMessage("No se pudo resolver el problema.")
            QMessageBox.warning(
                self,
                "Revisa el problema",
                (
                    str(error)
                    if isinstance(error, (ValueError, ErrorInterno))
                    else "No se pudo completar la resolución. Revisa los datos del problema."
                ),
            )

    def cargar_ejemplo(self) -> None:
        """Abre la lista de ejemplos y carga el elegido por doble clic."""
        dialogo = QDialog(self)
        dialogo.setWindowTitle("Cargar ejemplo")
        layout = QVBoxLayout(dialogo)
        lista = QListWidget()
        lista.addItems(list(EJEMPLOS))
        layout.addWidget(lista)

        def elegir(item: object) -> None:
            self.panel.cargar_problema(parsear_problema(EJEMPLOS[item.text()]))
            dialogo.accept()

        lista.itemDoubleClicked.connect(elegir)
        dialogo.resize(400, 300)
        dialogo.exec()

    def guardar_en(self, ruta: Path) -> None:
        """Guarda solo datos del problema, sin configuración ni credenciales."""
        p = self.panel.leer_problema()
        datos = {
            "sentido": p.sentido,
            "coef_obj": [str(c) for c in p.coef_obj],
            "nombres": p.nombres,
            "restricciones": [
                {"coefs": [str(c) for c in r.coefs], "tipo": r.tipo, "rhs": str(r.rhs)}
                for r in p.restricciones
            ],
        }
        ruta.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def abrir_desde(self, ruta: Path) -> None:
        """Lee un archivo local y valida sus dimensiones antes de cargarlo."""
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        p = Problema(
            datos["sentido"],
            datos["coef_obj"],
            [Restriccion(**r) for r in datos["restricciones"]],
            datos["nombres"],
        )
        if len(p.nombres) > 10:
            raise ValueError("El formulario admite hasta 10 variables.")
        self.panel.cargar_problema(p)

    def guardar(self) -> None:
        """Selecciona destino y comunica errores de escritura sin traceback."""
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar problema", "", "SimplexLab (*.json)"
        )
        if ruta:
            try:
                self.guardar_en(Path(ruta))
            except Exception:
                QMessageBox.warning(
                    self,
                    "Guardar",
                    "No se pudo guardar. Revisa los datos y los permisos del archivo.",
                )

    def abrir(self) -> None:
        """Selecciona y valida un archivo local de problema."""
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Abrir problema", "", "SimplexLab (*.json)"
        )
        if ruta:
            try:
                self.abrir_desde(Path(ruta))
            except Exception:
                QMessageBox.warning(
                    self,
                    "Abrir",
                    "El archivo no contiene un problema válido de SimplexLab.",
                )
