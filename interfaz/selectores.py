# -*- coding: utf-8 -*-
"""
interfaz/selectores.py
======================
Listas numeradas para ELEGIR registros en lugar de escribir sus códigos.

El usuario ve las opciones disponibles (estudiantes, profesores, cursos...) y
solo escribe el número de la que quiere. Así no hace falta memorizar carnés,
IDs ni códigos de curso.

Todas las listas aceptan 'cancelar' (lo maneja `input_validado`).
"""

from typing import Callable, List, Optional, Sequence, TypeVar

from excepciones import ErrorGestion
from modelos import Curso, Estudiante, Inscripcion, Profesor
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import input_validado

T = TypeVar("T")


def elegir_de_lista(
    titulo: str,
    elementos: Sequence[T],
    formato: Callable[[T], str],
    texto_ninguno: Optional[str] = None,
) -> Optional[T]:
    """Muestra una lista numerada y devuelve el elemento que elija el usuario.

    Parámetros:
        titulo        : encabezado de la lista (por ejemplo, "Seleccione el curso").
        elementos     : opciones disponibles.
        formato       : función que convierte un elemento en el texto a mostrar.
        texto_ninguno : si se indica, se agrega la opción "0" con ese texto
                        (por ejemplo, "Sin prerrequisito"); al elegirla la
                        función devuelve None.

    Retorna:
        El elemento elegido, o None si se eligió la opción "0".

    Lanza:
        ErrorGestion si no hay elementos y tampoco opción "0".
        OperacionCancelada si el usuario escribe 'cancelar'.
    """
    if not elementos and texto_ninguno is None:
        raise ErrorGestion("No hay opciones disponibles para elegir.")

    print(f"\n  {titulo}:")
    if texto_ninguno is not None:
        print(f"     0. {texto_ninguno}")
    for numero, elemento in enumerate(elementos, start=1):
        print(f"    {numero:>2}. {formato(elemento)}")

    minimo = 0 if texto_ninguno is not None else 1
    maximo = len(elementos)
    rango = f"{minimo}-{maximo}" if minimo != maximo else f"{minimo}"
    indice = input_validado(
        f"\nNúmero ({rango}) o 'cancelar': ", int, minimo=minimo, maximo=maximo
    )
    return None if indice == 0 else elementos[indice - 1]


# ------------------------------------------------------------------------------
# Selectores específicos de cada entidad
# ------------------------------------------------------------------------------
def elegir_estudiante(
    sistema: SistemaGestion, titulo: str = "Seleccione el estudiante"
) -> Estudiante:
    """Lista todos los estudiantes y devuelve el elegido."""
    if not sistema.estudiantes:
        raise ErrorGestion("No hay estudiantes registrados.")
    return elegir_de_lista(titulo, list(sistema.estudiantes.values()), str)


def elegir_profesor(
    sistema: SistemaGestion, titulo: str = "Seleccione el profesor"
) -> Profesor:
    """Lista todos los profesores y devuelve el elegido."""
    if not sistema.profesores:
        raise ErrorGestion("No hay profesores registrados.")
    return elegir_de_lista(titulo, list(sistema.profesores.values()), str)


def elegir_curso(
    sistema: SistemaGestion,
    titulo: str = "Seleccione el curso",
    cursos: Optional[List[Curso]] = None,
    formato: Callable[[Curso], str] = str,
) -> Curso:
    """Lista cursos y devuelve el elegido.

    Por defecto muestra todos los cursos; se puede pasar una lista `cursos`
    para mostrar solo algunos y un `formato` propio para agregar información.
    """
    if cursos is None:
        cursos = list(sistema.cursos.values())
    if not cursos:
        raise ErrorGestion("No hay cursos registrados.")
    return elegir_de_lista(titulo, cursos, formato)


def elegir_inscripcion(
    sistema: SistemaGestion,
    estudiante: Estudiante,
    titulo: str = "Seleccione el curso",
) -> Inscripcion:
    """Lista SOLO los cursos en los que está inscrito el estudiante.

    Cada línea muestra el estado actual del curso para ubicarse rápido.
    """
    inscripciones = sistema.cursos_de_estudiante(estudiante.carne)
    if not inscripciones:
        raise ErrorGestion(f"{estudiante.nombre} no está inscrito en ningún curso.")

    def formato(inscripcion: Inscripcion) -> str:
        curso = sistema.cursos[inscripcion.codigo_curso]
        promedio = inscripcion.promedio()
        detalle = f" - promedio {promedio:.2f}" if promedio is not None else ""
        return f"{curso}  [{inscripcion.estado()}{detalle}]"

    return elegir_de_lista(titulo, inscripciones, formato)
