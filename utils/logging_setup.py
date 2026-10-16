"""Configuración local de registros sin datos de problemas ni credenciales."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configurar_logging(ruta: Path | None = None) -> None:
    """Configura un archivo local acotado para eventos de la aplicación."""
    ruta = ruta or Path.home() / ".simplexlab" / "logs" / "app.log"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        ruta, maxBytes=100000, backupCount=2, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger = logging.getLogger("simplexlab")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
