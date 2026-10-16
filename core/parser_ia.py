"""Traducción opcional de enunciados: modo manual y REST de Gemini."""

import json
import re
import socket
import urllib.error
import urllib.request

from core.models import Problema
from core.parser import ParseError, extraer_leyenda, parsear_problema

PROMPT_EXTRACCION = (
    "Eres un asistente que convierte enunciados de Programación Lineal a "
    "un formato fijo.\nLee el enunciado y responde ÚNICAMENTE con un "
    "bloque de texto, sin explicaciones,\nsin markdown y sin comillas, "
    "con exactamente este formato:\n\n# x1 = <qué representa x1>\n# x2 = "
    "<qué representa x2>\nmax <función objetivo>        (o: min <función "
    "objetivo>)\ns.a.\n<restricción 1>\n<restricción 2>\n\nReglas:\n1. "
    "Variables llamadas x1, x2, x3... en el orden en que se definen en "
    "el enunciado.\n2. Operadores permitidos: <=, >=, =.\n3. Coeficientes "
    "numéricos (enteros, decimales o fracciones a/b), sin unidades ni "
    "texto.\n4. No incluyas restricciones de no negatividad (x1, x2 >= "
    "0).\n5. Si hay unidades distintas (horas y minutos, kg y g), "
    "conviértelo todo a una misma unidad.\n6. Si el enunciado no es un "
    "problema de programación lineal o es ambiguo, responde\n   "
    "exactamente: NO_ES_PL\n\nEnunciado:\n{enunciado}"
)
MODELO_PREDETERMINADO = "gemini-flash-lite-latest"
AVISO_REVISION = (
    "Revisa los datos antes de resolver: la IA puede equivocarse al "
    "interpretar el enunciado."
)
ERROR_NO_PL = (
    "La IA no reconoció un problema de programación lineal en el texto. "
    "Revisa el enunciado."
)
ERROR_RED = (
    "No se pudo conectar con Gemini. Revisa tu internet o usa el modo manual (A)."
)
ERROR_RESPUESTA = (
    "La respuesta de Gemini no contiene un problema válido. Revisa el "
    "enunciado o usa el modo manual (A)."
)


class ErrorIA(Exception):
    """Error amigable sin datos de la petición ni credenciales."""


def construir_prompt(enunciado: str) -> str:
    """Inserta el enunciado como texto en la plantilla de extracción."""
    return PROMPT_EXTRACCION.replace("{enunciado}", enunciado)


def limpiar_respuesta(texto: str) -> str:
    """Elimina cercas markdown y texto previo al modelo reconocido."""
    if re.search(r"(?m)^\s*NO_ES_PL\s*$", texto):
        raise ErrorIA(ERROR_NO_PL)
    lineas = [
        s.strip() for s in texto.strip().splitlines() if not s.strip().startswith("```")
    ]
    for i, linea in enumerate(lineas):
        if re.match(r"^(#|max\b|min\b|maximizar\b|minimizar\b)", linea, re.I):
            return "\n".join(lineas[i:]).strip()
    raise ErrorIA(ERROR_RESPUESTA)


def problema_desde_respuesta(texto: str) -> tuple[Problema, list[str]]:
    """Aplica limpieza, parser exacto y extracción de leyenda sin resolver."""
    limpio = limpiar_respuesta(texto)
    return parsear_problema(limpio), extraer_leyenda(limpio)


class ClienteGemini:
    """Cliente sin estado global: red solo al invocar sus métodos explícitamente."""

    def __init__(
        self, api_key: str, modelo: str = MODELO_PREDETERMINADO, timeout: float = 30.0
    ) -> None:
        self._api_key = api_key.strip()
        if not self._api_key:
            raise ErrorIA(
                "Configura una clave en Configuración de IA o usa el modo manual (A)."
            )
        if not re.fullmatch(r"[a-zA-Z0-9_.-]+", modelo):
            raise ErrorIA(
                "El nombre de modelo no es válido. Revísalo en Configuración de IA."
            )
        self.modelo = modelo
        self.timeout = timeout

    def _peticion(self, recurso: str, datos: dict | None = None) -> dict:
        request = urllib.request.Request(
            "https://generativelanguage.googleapis.com/v1beta/" + recurso,
            data=json.dumps(datos).encode("utf-8") if datos is not None else None,
            headers={
                "x-goog-api-key": self._api_key,
                "Content-Type": "application/json",
            },
            method="POST" if datos is not None else "GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as respuesta:
                contenido = json.loads(respuesta.read().decode("utf-8"))
            if not isinstance(contenido, dict):
                raise ErrorIA(ERROR_RESPUESTA)
            return contenido
        except urllib.error.HTTPError as error:
            mensajes = {
                400: "La clave de API no es válida o no tiene permiso. "
                "Revísala en Configuración de IA.",
                403: "La clave de API no es válida o no tiene permiso. "
                "Revísala en Configuración de IA.",
                404: "El modelo configurado no existe o fue retirado. Usa "
                "«Probar conexión» y elige otro en Configuración de "
                "IA.",
                429: "Se agotó la cuota gratuita (por minuto o por día). "
                "Espera un momento o usa el modo manual (A).",
            }
            raise ErrorIA(
                mensajes.get(
                    error.code,
                    "Gemini no está disponible ahora mismo. Intenta "
                    "más tarde o usa el modo manual (A).",
                )
            ) from None
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            raise ErrorIA(ERROR_RED) from None
        except (ValueError, TypeError, KeyError):
            raise ErrorIA(ERROR_RESPUESTA) from None

    def probar_conexion(self) -> list[str]:
        """Consulta los modelos disponibles sin enviar ningún enunciado."""
        datos = self._peticion("models")
        modelos = datos.get("models", [])
        if not isinstance(modelos, list):
            raise ErrorIA(ERROR_RESPUESTA)
        return [
            m["name"].removeprefix("models/")
            for m in modelos
            if isinstance(m, dict) and isinstance(m.get("name"), str)
        ]

    def consultar(self, enunciado: str) -> str:
        """Envía un prompt de extracción y concatena todas las partes textuales."""
        datos = self._peticion(
            f"models/{self.modelo}:generateContent",
            {
                "contents": [{"parts": [{"text": construir_prompt(enunciado)}]}],
                "generationConfig": {"temperature": 0},
            },
        )
        try:
            partes = datos["candidates"][0]["content"]["parts"]
            texto = "".join(p["text"] for p in partes if isinstance(p.get("text"), str))
        except (KeyError, IndexError, TypeError, AttributeError):
            raise ErrorIA(ERROR_RESPUESTA) from None
        if not texto.strip():
            raise ErrorIA(ERROR_RESPUESTA)
        return texto


def analizar_enunciado(
    enunciado: str, cliente: ClienteGemini
) -> tuple[Problema, list[str]]:
    """Consulta y parsea; reintenta una vez únicamente tras un error de sintaxis."""
    respuesta = cliente.consultar(enunciado)
    try:
        return problema_desde_respuesta(respuesta)
    except ParseError as error:
        correccion = (
            enunciado
            + "\nCorrige la respuesta anterior según este error del parser: "
            + str(error)
            + "\nRespuesta anterior:\n"
            + respuesta
        )
    respuesta = cliente.consultar(correccion)
    try:
        return problema_desde_respuesta(respuesta)
    except ParseError:
        raise ErrorIA(ERROR_RESPUESTA) from None
