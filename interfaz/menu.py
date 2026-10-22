# -*- coding: utf-8 -*-
"""
interfaz/menu.py
================
Definición y presentación del menú principal.

El menú se describe UNA sola vez en la lista SECCIONES. Los números de opción
se asignan automáticamente en el orden en que aparecen, y a partir de esa
misma lista se dibuja el menú y se arma la tabla {número: función} que usa
el bucle principal. Para agregar una opción nueva basta añadir una línea.
"""

from typing import Callable, Dict, List, Tuple

from interfaz import opciones_cursos as cursos
from interfaz import opciones_datos as datos
from interfaz import opciones_estudiantes as estudiantes
from interfaz import opciones_inscripciones as inscripciones
from interfaz import opciones_profesores as profesores
from interfaz import opciones_reportes as reportes

# Número de la opción que cierra el programa
OPCION_SALIR = 0

# Cada sección: (título, [(texto, función), ...]). Sin números: se asignan solos.
SECCIONES: List[Tuple[str, List[Tuple[str, Callable]]]] = [
    ("Estudiantes", [
        ("Registrar estudiante", estudiantes.opcion_registrar_estudiante),
        ("Consultar estudiantes", estudiantes.opcion_listar_estudiantes),
        ("Modificar estudiante", estudiantes.opcion_modificar_estudiante),
        ("Eliminar estudiante", estudiantes.opcion_eliminar_estudiante),
    ]),
    ("Profesores", [
        ("Registrar profesor", profesores.opcion_registrar_profesor),
        ("Consultar profesores", profesores.opcion_listar_profesores),
        ("Modificar profesor", profesores.opcion_modificar_profesor),
        ("Eliminar profesor", profesores.opcion_eliminar_profesor),
    ]),
    ("Cursos", [
        ("Registrar curso", cursos.opcion_registrar_curso),
        ("Consultar cursos", cursos.opcion_listar_cursos),
        ("Modificar curso", cursos.opcion_modificar_curso),
        ("Eliminar curso", cursos.opcion_eliminar_curso),
        ("Asignar profesor a un curso", cursos.opcion_asignar_profesor),
    ]),
    ("Inscripciones y calificaciones", [
        ("Inscribir estudiante en un curso", inscripciones.opcion_inscribir),
        ("Retirar estudiante de un curso", inscripciones.opcion_retirar_estudiante),
        ("Registrar / modificar calificación", inscripciones.opcion_registrar_calificacion),
        ("Eliminar calificación", inscripciones.opcion_eliminar_calificacion),
    ]),
    ("Reportes", [
        ("Cursos inscritos de un estudiante", reportes.opcion_cursos_de_estudiante),
        ("Estudiantes inscritos en un curso", reportes.opcion_estudiantes_de_curso),
        ("Historial académico de un estudiante", reportes.opcion_historial),
    ]),
    ("Datos (archivos JSON)", [
        ("Guardar datos en archivo JSON", datos.opcion_guardar_datos),
        ("Cargar datos desde archivo JSON", datos.opcion_cargar_datos),
        ("Cargar datos de prueba", datos.opcion_cargar_datos_prueba),
    ]),
]


def _numerar() -> List[Tuple[str, List[Tuple[int, str, Callable]]]]:
    """Asigna a cada opción su número (1, 2, 3...) siguiendo el orden de SECCIONES."""
    numerado = []
    siguiente = 1
    for titulo, opciones in SECCIONES:
        filas = []
        for texto, funcion in opciones:
            filas.append((siguiente, texto, funcion))
            siguiente += 1
        numerado.append((titulo, filas))
    return numerado


def construir_acciones() -> Dict[int, Callable]:
    """Devuelve el diccionario {número de opción: función a ejecutar}."""
    acciones = {}
    for _, filas in _numerar():
        for numero, _, funcion in filas:
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
    for titulo, filas in _numerar():
        print(f"  --- {titulo} ---")
        for numero, texto, _ in filas:
            print(f"  {numero:>2}. {texto}")
    print(f"  {OPCION_SALIR:>2}. Salir")
    print("=" * 62)
    print("  Consejo: en cualquier operación escriba 'cancelar' para volver aquí.")
