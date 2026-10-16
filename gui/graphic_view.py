"""Canvas cartesiano con geometría calculada por el solver exacto."""

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.models import ResultadoGrafico


class GraphicView(QWidget):
    """Dibuja únicamente el resultado final, sin líneas de nivel ni animaciones."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.figura = Figure(figsize=(7, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figura)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.ax = self.figura.add_subplot(111)
        self.avisos = QLabel()
        self.avisos.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.avisos)
        self.resultado: ResultadoGrafico | None = None
        self.puntos_vertices = None
        self.puntos_optimos = None
        self.canvas.mpl_connect("motion_notify_event", self._hover)

    def dibujar(self, resultado: ResultadoGrafico) -> None:
        """Dibuja rectas, región, vértices anotados y óptimos en el primer cuadrante."""
        self.resultado = resultado
        self.ax.clear()
        self.puntos_vertices = self.puntos_optimos = None
        limite = max([10.0] + [max(p) for p in resultado.region])
        for i, r in enumerate(resultado.rectas):
            a, b = (float(c) for c in r["coefs"])
            rhs = float(r["rhs"])
            color = f"C{i % 10}"
            if b:
                self.ax.plot(
                    [0, limite],
                    [rhs / b, (rhs - a * limite) / b],
                    label=r["nombre"],
                    color=color,
                )
            elif a:
                self.ax.axvline(rhs / a, label=r["nombre"], color=color)
        if len(resultado.region) >= 3:
            self.ax.fill(
                *zip(*resultado.region),
                color="gray",
                alpha=0.3,
                label="Región factible",
            )
        elif resultado.region:
            self.ax.plot(
                *zip(*resultado.region),
                color="gray",
                linewidth=5,
                alpha=0.3,
                label="Región factible",
            )
        if resultado.vertices:
            xs, ys = zip(*[(float(x), float(y)) for x, y in resultado.vertices])
            self.puntos_vertices = self.ax.scatter(
                xs, ys, color="#1976D2", s=35, label="Vértices", zorder=4
            )
            for (x, y), z in zip(resultado.vertices, resultado.valores_z):
                self.ax.annotate(
                    f"({x}, {y})\nZ = {z}",
                    (float(x), float(y)),
                    xytext=(7, 7),
                    textcoords="offset points",
                    fontsize=9,
                )
        if resultado.optimos:
            xs, ys = zip(*[(float(x), float(y)) for x, y in resultado.optimos])
            self.puntos_optimos = self.ax.scatter(
                xs, ys, color="#D32F2F", s=95, label="Óptimo", zorder=5
            )
            if len(resultado.optimos) > 1:
                self.ax.plot(xs, ys, color="#D32F2F", linewidth=3)
            coords = ", ".join(f"({x}, {y})" for x, y in resultado.optimos)
            titulo = f"Z* = {resultado.z_optimo} en (x1, x2) = {coords}"
        else:
            titulo = (
                "Problema no factible"
                if resultado.estado == "no_factible"
                else "Problema no acotado"
            )
        self.ax.set(
            title=titulo, xlabel="x1", ylabel="x2", xlim=(0, limite), ylim=(0, limite)
        )
        self.ax.grid(True, alpha=0.2)
        if self.ax.get_legend_handles_labels()[0]:
            self.ax.legend(loc="upper right")
        self.avisos.setText("\n".join(resultado.advertencias))
        self.canvas.draw()

    def _hover(self, event: object) -> None:
        if self.puntos_vertices is None or event.inaxes is not self.ax:
            self.canvas.setToolTip("")
            return
        contiene, datos = self.puntos_vertices.contains(event)
        if contiene:
            i = datos["ind"][0]
            x, y = self.resultado.vertices[i]
            self.canvas.setToolTip(f"({x}, {y})\nZ = {self.resultado.valores_z[i]}")
        else:
            self.canvas.setToolTip("")
