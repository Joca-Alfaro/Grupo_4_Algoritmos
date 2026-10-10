# -*- coding: utf-8 -*-
"""
servicios/persistencia.py
=========================
Guardado y carga de los datos del sistema en archivos JSON.

Características:
  - Formato legible (indentado y con tildes), editable con cualquier editor.
  - Escritura "atómica": primero se escribe un archivo temporal y luego se
    reemplaza al definitivo. Si el programa se interrumpe a mitad de camino,
    el archivo anterior no se corrompe.
  - Carga segura: el archivo se valida por completo antes de reemplazar los
    datos actuales; un archivo dañado nunca deja el sistema a medio cargar.
"""

import json
import os
from datetime import datetime
from typing import Optional

from config import DIRECTORIO_DATOS, RUTA_DATOS_POR_DEFECTO, VERSION_FORMATO_JSON
from excepciones import ErrorPersistencia
from servicios.sistema_gestion import SistemaGestion


def resolver_ruta(entrada: Optional[str]) -> str:
    """Convierte lo que escribió el usuario en una ruta de archivo completa.

    Reglas:
      - Entrada vacía        -> archivo por defecto (datos/academico.json).
      - Se quitan comillas (útil al arrastrar un archivo a la terminal).
      - Si no termina en .json, se agrega la extensión.
      - Si solo se escribió un nombre (sin carpeta), se usa la carpeta datos/.
      - Si se escribió una ruta, se respeta tal cual (relativa o absoluta).
    """
    if not entrada:
        return RUTA_DATOS_POR_DEFECTO

    ruta = os.path.expanduser(entrada.strip().strip('"').strip("'"))
    if not ruta.lower().endswith(".json"):
        ruta += ".json"
    if os.path.basename(ruta) == ruta:  # solo nombre de archivo, sin carpeta
        ruta = os.path.join(DIRECTORIO_DATOS, ruta)
    return os.path.abspath(ruta)


def guardar_en_json(sistema: SistemaGestion, ruta: str = RUTA_DATOS_POR_DEFECTO) -> str:
    """Guarda todos los datos del sistema en un archivo JSON.

    Parámetros:
        sistema : sistema cuyos datos se van a guardar.
        ruta    : ruta completa del archivo de destino.

    Retorna:
        La ruta del archivo guardado.

    Lanza:
        ErrorPersistencia si no se puede escribir el archivo.
    """
    # Estructura final del archivo: metadatos + datos del sistema
    contenido = {
        "version_formato": VERSION_FORMATO_JSON,
        "fecha_guardado": datetime.now().isoformat(timespec="seconds"),
    }
    contenido.update(sistema.a_diccionario())

    carpeta = os.path.dirname(ruta) or "."
    temporal = ruta + ".tmp"
    try:
        os.makedirs(carpeta, exist_ok=True)  # crea la carpeta si no existe
        # 1) Se escribe primero en un archivo temporal...
        with open(temporal, "w", encoding="utf-8") as archivo:
            json.dump(contenido, archivo, ensure_ascii=False, indent=4)
        # 2) ...y solo si salió bien, reemplaza al archivo definitivo
        os.replace(temporal, ruta)
    except (OSError, TypeError, ValueError) as error:
        # Limpieza del temporal si quedó a medias
        try:
            if os.path.exists(temporal):
                os.remove(temporal)
        except OSError:
            pass
        raise ErrorPersistencia(f"No se pudo guardar el archivo '{ruta}': {error}") from error

    sistema.cambios_sin_guardar = False
    return ruta


def cargar_desde_json(sistema: SistemaGestion, ruta: str = RUTA_DATOS_POR_DEFECTO) -> None:
    """Carga los datos de un archivo JSON, reemplazando los datos actuales.

    El archivo se lee y se valida completamente ANTES de modificar el sistema.
    Si hay cualquier problema, se lanza ErrorPersistencia y los datos actuales
    permanecen intactos.

    Lanza:
        ErrorPersistencia si el archivo no existe, no es JSON válido, tiene una
        estructura incorrecta, datos inválidos o referencias inconsistentes.
    """
    if not os.path.isfile(ruta):
        raise ErrorPersistencia(f"No se encontró el archivo '{ruta}'.")

    # --- Lectura y conversión del texto JSON ---
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except json.JSONDecodeError as error:
        raise ErrorPersistencia(
            f"El archivo no es un JSON válido (línea {error.lineno}, columna {error.colno}): "
            f"{error.msg}."
        ) from error
    except (OSError, UnicodeDecodeError) as error:
        raise ErrorPersistencia(f"No se pudo leer el archivo '{ruta}': {error}") from error

    # --- Verificación de la versión del formato ---
    if not isinstance(datos, dict):
        raise ErrorPersistencia("El archivo no tiene la estructura esperada.")
    version = datos.get("version_formato", VERSION_FORMATO_JSON)
    if not isinstance(version, int) or isinstance(version, bool) or version > VERSION_FORMATO_JSON:
        raise ErrorPersistencia(
            f"Versión de formato no soportada: {version!r} "
            f"(este programa soporta hasta la versión {VERSION_FORMATO_JSON})."
        )

    # --- Construcción y validación completa de un sistema nuevo ---
    nuevo_sistema = SistemaGestion.desde_diccionario(datos)

    # --- Solo si todo fue válido se reemplazan los datos actuales ---
    sistema.reemplazar_datos(nuevo_sistema)
