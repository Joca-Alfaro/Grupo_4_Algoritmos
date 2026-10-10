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
from typing import Callable, Optional


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

    Retorna:
        El valor convertido al tipo pedido, o None si se permitió vacío.
    """
    while True:
        # --- Lectura de la entrada ---
        try:
            texto = input(mensaje).strip()
        except EOFError:
            # Sin entrada disponible no se puede reintentar: se sale limpiamente
            print("\nEntrada finalizada. Cerrando el programa.")
            sys.exit(0)

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
