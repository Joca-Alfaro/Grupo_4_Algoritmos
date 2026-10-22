# -*- coding: utf-8 -*-
"""
interfaz/presentacion.py
========================
Funciones pequeñas para dar formato a lo que se muestra en pantalla.
Las usan todos los módulos de opciones del menú.
"""

from typing import Optional

from servicios.sistema_gestion import SistemaGestion


def encabezado(titulo: str, con_cancelar: bool = True) -> None:
    """Imprime el título de una operación y, si aplica, el aviso de cancelación.

    Parámetros:
        titulo       : nombre de la operación (se muestra en mayúsculas).
        con_cancelar : si la operación hace preguntas, recuerda que se puede
                       escribir 'cancelar' para volver al menú principal.
    """
    print(f"\n--- {titulo.upper()} ---")
    if con_cancelar:
        print("  (Escriba 'cancelar' en cualquier momento para volver al menú principal)")


def formato_nota(valor: Optional[float]) -> str:
    """Devuelve la nota con 2 decimales, o un guion si todavía no existe."""
    return f"{valor:.2f}" if valor is not None else "  -  "


def imprimir_resumen_datos(sistema: SistemaGestion) -> None:
    """Muestra cuántos registros de cada tipo hay actualmente en el sistema."""
    resumen = sistema.resumen()
    print("  Datos actuales en el sistema:")
    print(f"     - Estudiantes  : {resumen['estudiantes']}")
    print(f"     - Profesores   : {resumen['profesores']}")
    print(f"     - Cursos       : {resumen['cursos']}")
    print(f"     - Inscripciones: {resumen['inscripciones']}")
