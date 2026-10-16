"""Comprueba la preparación del repositorio antes de implementar el núcleo."""

import sys
from pathlib import Path


def test_preparacion() -> None:
    """Exige Python compatible y los directorios de la arquitectura."""
    raiz = Path(__file__).resolve().parents[1]
    assert sys.version_info >= (3, 11)
    for nombre in (
        "core",
        "gui",
        "utils",
        "tests",
        "gui/help",
        "resources/icons",
        "resources/styles",
        "docs",
    ):
        assert (raiz / nombre).is_dir()
