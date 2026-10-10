# -*- coding: utf-8 -*-
"""
interfaz/caratula.py
====================
Carátula (encabezado) que se muestra al iniciar el programa.

Los datos se toman de config.py: para completar los marcadores [MOLDE] solo
hay que editar ese archivo; este módulo no necesita modificarse.
"""

from config import (
    FECHA_PRESENTACION,
    INTEGRANTES,
    NOMBRE_CATEDRATICO,
    NOMBRE_CURSO,
    NOMBRE_UNIVERSIDAD,
)

ANCHO = 74  # ancho total de la caja, incluyendo los bordes


def mostrar_caratula() -> None:
    """Imprime el encabezado con los datos de la universidad y del equipo."""

    def centrado(texto: str) -> str:
        """Línea con el texto centrado dentro de los bordes."""
        return "║" + texto[: ANCHO - 2].center(ANCHO - 2) + "║"

    def izquierda(texto: str) -> str:
        """Línea con el texto alineado a la izquierda dentro de los bordes."""
        return "║ " + texto[: ANCHO - 3].ljust(ANCHO - 3) + "║"

    def separador() -> str:
        """Línea divisoria horizontal."""
        return "╠" + "═" * (ANCHO - 2) + "╣"

    print("╔" + "═" * (ANCHO - 2) + "╗")
    print(centrado(""))
    print(centrado(NOMBRE_UNIVERSIDAD.upper()))
    print(centrado(""))
    print(separador())
    print(centrado("SISTEMA DE GESTIÓN ACADÉMICA UNIVERSITARIA"))
    print(separador())
    print(izquierda(f"Curso       : {NOMBRE_CURSO}"))
    print(izquierda(f"Catedrático : {NOMBRE_CATEDRATICO}"))
    print(izquierda(f"Fecha       : {FECHA_PRESENTACION}"))
    print(separador())
    print(izquierda("Integrantes del equipo (Nombre y Carné):"))
    for numero, (nombre, carne) in enumerate(INTEGRANTES, start=1):
        print(izquierda(f"   {numero}. {nombre}  -  Carné: {carne}"))
    print("╚" + "═" * (ANCHO - 2) + "╝")
    print()
