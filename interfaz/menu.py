# -*- coding: utf-8 -*-
"""
interfaz/menu.py
================
Definición y presentación del menú principal.

El menú se describe UNA sola vez en la lista SECCIONES. A partir de ella se
dibuja el menú en pantalla y se construye la tabla {número: función} que usa
el bucle principal. Para agregar una opción nueva basta añadir una línea aquí.
"""

from typing import Callable, Dict

from interfaz import opciones as op

# Número de la opción que cierra el programa
OPCION_SALIR = 0

# Cada sección: (título, [(número, texto, función), ...])
SECCIONES = [
    ("Estudiantes", [
        (1, "Registrar estudiante", op.opcion_registrar_estudiante),
        (2, "Consultar estudiantes", op.opcion_listar_estudiantes),
    ]),
    ("Profesores", [
        (3, "Registrar profesor", op.opcion_registrar_profesor),
        (4, "Consultar profesores", op.opcion_listar_profesores),
    ]),
    ("Cursos", [
        (5, "Registrar curso", op.opcion_registrar_curso),
        (6, "Consultar cursos", op.opcion_listar_cursos),
        (7, "Asignar profesor a un curso", op.opcion_asignar_profesor),
    ]),
    ("Inscripciones y calificaciones", [
        (8, "Inscribir estudiante en un curso", op.opcion_inscribir),
        (9, "Registrar / modificar calificación", op.opcion_registrar_calificacion),
    ]),
    ("Reportes", [
        (10, "Cursos inscritos de un estudiante", op.opcion_cursos_de_estudiante),
        (11, "Estudiantes inscritos en un curso", op.opcion_estudiantes_de_curso),
        (12, "Historial académico de un estudiante", op.opcion_historial),
    ]),
    ("Datos (archivos JSON)", [
        (13, "Guardar datos en archivo JSON", op.opcion_guardar_datos),
        (14, "Cargar datos desde archivo JSON", op.opcion_cargar_datos),
        (15, "Cargar datos de prueba", op.opcion_cargar_datos_prueba),
    ]),
]


def construir_acciones() -> Dict[int, Callable]:
    """Devuelve el diccionario {número de opción: función a ejecutar}."""
    acciones = {}
    for _, opciones in SECCIONES:
        for numero, _, funcion in opciones:
            acciones[numero] = funcion
    return acciones


def numero_maximo_opcion() -> int:
    """Devuelve el número de opción más alto del menú."""
    return max(construir_acciones().keys())


def mostrar_menu() -> None:
    """Imprime el menú principal agrupado por secciones."""
    print("\n" + "=" * 62)
    print("                    MENÚ PRINCIPAL")
    print("=" * 62)
    for titulo, opciones in SECCIONES:
        print(f"  --- {titulo} ---")
        for numero, texto, _ in opciones:
            print(f"  {numero:>2}. {texto}")
    print(f"  {OPCION_SALIR:>2}. Salir")
    print("=" * 62)
