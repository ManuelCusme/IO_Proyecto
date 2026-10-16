"""API simulada con urllib: sin internet y sin credenciales reales."""

import io
import json
import urllib.error
import urllib.request

import pytest

from core.ejemplos import EJEMPLOS
from core.parser_ia import (
    AVISO_REVISION,
    ERROR_NO_PL,
    ERROR_RED,
    ClienteGemini,
    ErrorIA,
    analizar_enunciado,
    construir_prompt,
    limpiar_respuesta,
    problema_desde_respuesta,
)
from core.simplex_solver import resolver_simplex

RESPUESTA = "# x1 = ventanas\n# x2 = puertas\n" + next(iter(EJEMPLOS.values())).strip()
CLAVE_FICTICIA = "valor-ficticio-exclusivo-del-test"


def _respuesta(texto: str) -> io.BytesIO:
    return io.BytesIO(
        json.dumps({"candidates": [{"content": {"parts": [{"text": texto}]}}]}).encode()
    )


def test_manual() -> None:
    """El modo manual carga el problema y la leyenda sin llamar a la red."""
    p, leyenda = problema_desde_respuesta(
        "Claro, aquí está:\n```text\n" + RESPUESTA + "\n```"
    )
    assert resolver_simplex(p).z == 36
    assert leyenda == ["x1 = ventanas", "x2 = puertas"]
    assert "mi enunciado {sin formato}" in construir_prompt(
        "mi enunciado {sin formato}"
    )
    assert "NO_ES_PL" in construir_prompt("enunciado")
    assert "Revisa los datos" in AVISO_REVISION
    with pytest.raises(ErrorIA, match=ERROR_NO_PL):
        limpiar_respuesta("NO_ES_PL")
    with pytest.raises(ErrorIA):
        limpiar_respuesta("Nada reconocible")


def test_cliente_y_modelos(monkeypatch: pytest.MonkeyPatch) -> None:
    """Comprueba cabecera, URL sin clave, temperatura y partes concatenadas."""
    peticiones = []

    def urlopen(request: object, timeout: int) -> io.BytesIO:
        peticiones.append(request)
        assert timeout == 30
        assert CLAVE_FICTICIA not in request.full_url
        assert request.get_header("X-goog-api-key") == CLAVE_FICTICIA
        if request.get_method() == "GET":
            return io.BytesIO(b'{"models":[{"name":"models/prueba-gratis"}]}')
        datos = json.loads(request.data)
        assert datos["generationConfig"] == {"temperature": 0}
        assert "Mi enunciado" in datos["contents"][0]["parts"][0]["text"]
        return _respuesta(RESPUESTA)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    cliente = ClienteGemini(CLAVE_FICTICIA, modelo="prueba-gratis")
    assert cliente.probar_conexion() == ["prueba-gratis"]
    p, _ = analizar_enunciado("Mi enunciado", cliente)
    assert resolver_simplex(p).z == 36
    assert len(peticiones) == 2


@pytest.mark.parametrize("segundo_valido", [True, False])
def test_reintento(monkeypatch: pytest.MonkeyPatch, segundo_valido: bool) -> None:
    """El segundo pedido contiene el error y la respuesta previa, y no hay tercero."""
    pedidos = []
    rota = "max x1 + x2\ns.a.\nx1 + x2 < 4"

    def urlopen(request: object, timeout: int) -> io.BytesIO:
        pedidos.append(json.loads(request.data)["contents"][0]["parts"][0]["text"])
        if len(pedidos) == 2:
            assert "falta el operador" in pedidos[-1]
            assert rota in pedidos[-1]
        return _respuesta(RESPUESTA if len(pedidos) == 2 and segundo_valido else rota)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    cliente = ClienteGemini(CLAVE_FICTICIA)
    if segundo_valido:
        p, _ = analizar_enunciado("Enunciado", cliente)
        assert resolver_simplex(p).z == 36
    else:
        with pytest.raises(ErrorIA):
            analizar_enunciado("Enunciado", cliente)
    assert len(pedidos) == 2


@pytest.mark.parametrize(
    "codigo,fragmento",
    [
        (400, "clave"),
        (403, "clave"),
        (404, "modelo"),
        (429, "cuota"),
        (500, "disponible"),
        (503, "disponible"),
    ],
)
def test_errores_http(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    codigo: int,
    fragmento: str,
) -> None:
    """No filtra la clave aunque el error de urllib la contenga."""

    def urlopen(*args: object, **kwargs: object) -> None:
        raise urllib.error.HTTPError(
            "https://ejemplo.invalid/" + CLAVE_FICTICIA,
            codigo,
            CLAVE_FICTICIA,
            None,
            None,
        )

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    with pytest.raises(ErrorIA) as error:
        ClienteGemini(CLAVE_FICTICIA).consultar("texto")
    assert fragmento in str(error.value)
    assert CLAVE_FICTICIA not in str(error.value) + repr(error.value) + caplog.text


@pytest.mark.parametrize(
    "fallo",
    [
        TimeoutError(CLAVE_FICTICIA),
        urllib.error.URLError(CLAVE_FICTICIA),
        OSError(CLAVE_FICTICIA),
    ],
)
def test_sin_red(monkeypatch: pytest.MonkeyPatch, fallo: Exception) -> None:
    """Timeout y falta de red sugieren siempre el modo manual."""

    def urlopen(*args: object, **kwargs: object) -> None:
        raise fallo

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    with pytest.raises(ErrorIA) as error:
        ClienteGemini(CLAVE_FICTICIA).probar_conexion()
    assert str(error.value) == ERROR_RED
    assert CLAVE_FICTICIA not in repr(error.value)


@pytest.mark.parametrize(
    "datos",
    [
        b"{}",
        b"[]",
        b"no-json",
        b'{"candidates":[]}',
        b'{"candidates":[{"content":{"parts":[]}}]}',
    ],
)
def test_respuesta_vacia(monkeypatch: pytest.MonkeyPatch, datos: bytes) -> None:
    """Respuestas bloqueadas o malformadas son errores amigables."""
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: io.BytesIO(datos))
    with pytest.raises(ErrorIA):
        ClienteGemini(CLAVE_FICTICIA).consultar("enunciado")


def test_configuracion_invalida() -> None:
    """Nunca incorpora clave ni modelo inválido en el mensaje de error."""
    with pytest.raises(ErrorIA):
        ClienteGemini("")
    with pytest.raises(ErrorIA):
        ClienteGemini(CLAVE_FICTICIA, "../" + CLAVE_FICTICIA)
