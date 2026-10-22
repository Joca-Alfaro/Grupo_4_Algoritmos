# -*- coding: utf-8 -*-
"""
utilidades/consola.py
=====================
Funciones auxiliares para interactuar con la consola.

Incluye la función `input_validado`, que es la única puerta de entrada de
datos del usuario en todo el sistema: reintenta hasta recibir un valor
correcto, de modo que el programa nunca se cae por una entrada inválida.
"""

import math
import os
import sys
from typing import Callable, Container, Optional

from excepciones import OperacionCancelada

# Palabra que el usuario escribe en cualquier pregunta para abandonar la operación
PALABRA_CANCELAR = "cancelar"


def limpiar_pantalla() -> None:
    """Limpia la consola según el sistema operativo (Windows o Unix)."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar() -> None:
    """Detiene la ejecución hasta que el usuario presione ENTER."""
    try:
        input("\nPresione ENTER para continuar...")
    except EOFError:
        # Si no hay entrada disponible (stdin cerrado) simplemente se continúa
        pass


def input_validado(
    mensaje: str,
    tipo: type = str,
    minimo: Optional[float] = None,
    maximo: Optional[float] = None,
    permitir_vacio: bool = False,
    validador: Optional[Callable[[str], bool]] = None,
    mensaje_validador: str = "El valor ingresado no es válido.",
    permitir_cancelar: bool = True,
):
    """Captura una entrada del usuario a prueba de fallos.

    Reintenta en un bucle hasta que el dato sea correcto.

    Parámetros:
        mensaje          : texto que se muestra al pedir el dato.
        tipo             : str, int o float (tipo esperado).
        minimo / maximo  : rango permitido (solo para int y float).
        permitir_vacio   : si es True, ENTER vacío devuelve None.
        validador        : función opcional que recibe el texto y devuelve
                           True si es válido (por ejemplo, formato de correo).
        mensaje_validador: mensaje de error cuando el validador falla.
        permitir_cancelar: si es True, escribir 'cancelar' (en mayúsculas o
                           minúsculas) lanza OperacionCancelada para abandonar
                           la operación. El menú principal lo desactiva.

    Retorna:
        El valor convertido al tipo pedido, o None si se permitió vacío.

    Lanza:
        OperacionCancelada si el usuario escribió 'cancelar'.
    """
    while True:
        # --- Lectura de la entrada ---
        try:
            texto = input(mensaje).strip()
        except EOFError:
            # Sin entrada disponible no se puede reintentar: se sale limpiamente
            print("\nEntrada finalizada. Cerrando el programa.")
            sys.exit(0)

        # --- Cancelación: se revisa antes que cualquier otra validación ---
        if permitir_cancelar and texto.lower() == PALABRA_CANCELAR:
            raise OperacionCancelada()

        # --- Manejo de entradas vacías ---
        if texto == "":
            if permitir_vacio:
                return None
            print("  [!] Error: el campo no puede estar vacío.")
            continue

        # --- Texto: solo se aplica el validador adicional (si existe) ---
        if tipo is str:
            if validador is not None and not validador(texto):
                print(f"  [!] Error: {mensaje_validador}")
                continue
            return texto

        # --- Decimales: se acepta la coma como separador (ej. 85,5) ---
        if tipo is float:
            texto = texto.replace(",", ".")

        # --- Números: se intenta la conversión (captura letras y símbolos) ---
        try:
            valor = tipo(texto)
        except ValueError:
            nombre_tipo = "entero" if tipo is int else "decimal"
            print(f"  [!] Error: debe ingresar un número {nombre_tipo} válido.")
            continue

        # --- float("nan") e "inf" son convertibles pero no son notas válidas ---
        if tipo is float and not math.isfinite(valor):
            print("  [!] Error: debe ingresar un número decimal válido.")
            continue

        # --- Validación de rango ---
        if minimo is not None and valor < minimo:
            print(f"  [!] Error: el valor no puede ser menor que {minimo:g}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"  [!] Error: el valor no puede ser mayor que {maximo:g}.")
            continue
        return valor


def pedir_id(mensaje: str) -> str:
    """Pide un identificador (carné, código, ID): no vacío y sin espacios."""
    return input_validado(
        mensaje,
        str,
        validador=lambda t: " " not in t,
        mensaje_validador="el identificador no debe contener espacios.",
    )


def pedir_id_nuevo(mensaje: str, existentes: Container[str], entidad: str) -> str:
    """Pide un identificador NUEVO: si ya existe, avisa y vuelve a preguntar.

    Así, si el usuario se equivoca y escribe un carné repetido, no pierde la
    operación: puede escribir otro o escribir 'cancelar'.

    Parámetros:
        mensaje    : texto de la pregunta.
        existentes : colección con los identificadores ya registrados.
        entidad    : cómo nombrar lo que ya existe en el aviso
                     (por ejemplo, "un estudiante").
    """
    while True:
        valor = pedir_id(mensaje)
        if valor not in existentes:
            return valor
        print(f"  [!] Error: ya existe {entidad} con el identificador '{valor}'. "
              "Escriba otro o 'cancelar'.")


def confirmar(mensaje: str) -> bool:
    """Hace una pregunta de sí/no y devuelve True si la respuesta es afirmativa.

    Acepta: s, si, sí (afirmativo) y n, no (negativo), sin distinguir
    mayúsculas de minúsculas.
    """
    respuesta = input_validado(
        mensaje,
        str,
        validador=lambda t: t.lower() in ("s", "si", "sí", "n", "no"),
        mensaje_validador="responda 's' para sí o 'n' para no.",
    )
    return respuesta.lower() in ("s", "si", "sí")
