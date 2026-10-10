# -*- coding: utf-8 -*-
"""
utilidades/validadores.py
=========================
Funciones de validación reutilizables.

Contiene dos grupos de utilidades:
  1. Validación de datos escritos por el usuario (por ejemplo, el correo).
  2. Validación de datos leídos desde un archivo JSON (extraer_campo), que
     garantiza que el archivo tenga la estructura y los tipos esperados antes
     de convertirlo en objetos del sistema.
"""

from typing import Any, Dict, Optional

from excepciones import ErrorPersistencia


def es_correo_valido(texto: str) -> bool:
    """Valida de forma sencilla un correo con el formato usuario@dominio.ext.

    Reglas: sin espacios, exactamente una arroba, usuario no vacío y un
    dominio que contenga un punto que no esté al inicio ni al final.
    """
    if " " in texto or texto.count("@") != 1:
        return False
    usuario, dominio = texto.split("@")
    return (
        bool(usuario)
        and "." in dominio
        and not dominio.startswith(".")
        and not dominio.endswith(".")
    )


def extraer_campo(
    datos: Dict[str, Any],
    clave: str,
    tipo: type,
    contexto: str,
    opcional: bool = False,
) -> Optional[Any]:
    """Obtiene un campo de un diccionario leído de JSON validando su tipo.

    Parámetros:
        datos    : diccionario del que se extrae el valor.
        clave    : nombre del campo a extraer.
        tipo     : tipo esperado (str, int o float).
        contexto : texto que describe qué se está leyendo (se usa en el
                   mensaje de error para que el usuario sepa dónde falló).
        opcional : si es True, un campo ausente o null devuelve None.

    Retorna:
        El valor validado (los float se normalizan con float()).

    Lanza:
        ErrorPersistencia si el campo falta, tiene un tipo incorrecto o es
        un texto vacío.
    """
    # El elemento completo debe ser un objeto JSON (diccionario)
    if not isinstance(datos, dict):
        raise ErrorPersistencia(f"{contexto}: se esperaba un objeto con campos.")

    valor = datos.get(clave)

    # Campo ausente o null
    if valor is None:
        if opcional:
            return None
        raise ErrorPersistencia(f"{contexto}: falta el campo obligatorio '{clave}'.")

    # En Python, bool es subclase de int; se descarta explícitamente
    if isinstance(valor, bool):
        raise ErrorPersistencia(f"{contexto}: el campo '{clave}' tiene un tipo inválido.")

    # Números decimales: se aceptan enteros y decimales
    if tipo is float:
        if not isinstance(valor, (int, float)):
            raise ErrorPersistencia(f"{contexto}: el campo '{clave}' debe ser numérico.")
        return float(valor)

    # Cualquier otro tipo (str, int): comparación estricta
    if not isinstance(valor, tipo):
        raise ErrorPersistencia(
            f"{contexto}: el campo '{clave}' debe ser de tipo {tipo.__name__}."
        )

    # Los textos no pueden estar vacíos
    if tipo is str and not valor.strip():
        raise ErrorPersistencia(f"{contexto}: el campo '{clave}' no puede estar vacío.")

    return valor
