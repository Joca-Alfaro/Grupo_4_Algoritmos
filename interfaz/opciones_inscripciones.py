# -*- coding: utf-8 -*-
"""
interfaz/opciones_inscripciones.py
==================================
Opciones del menú relacionadas con inscripciones y calificaciones:
inscribir, retirar, registrar/modificar nota y eliminar nota.

En todas se elige primero el estudiante de una lista y después el curso:
al calificar, retirar o eliminar notas solo aparecen los cursos en los que
ese estudiante YA está inscrito.
"""

from config import EVALUACIONES, NOTA_MAXIMA, NOTA_MINIMA
from excepciones import ErrorGestion
from interfaz.presentacion import encabezado, formato_nota
from interfaz.selectores import elegir_curso, elegir_de_lista, elegir_estudiante, elegir_inscripcion
from modelos import Curso
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import confirmar, input_validado


def opcion_inscribir(sistema: SistemaGestion) -> None:
    """Inscribe un estudiante en un curso (ambos se eligen de listas)."""
    encabezado("Inscribir estudiante en un curso")
    estudiante = elegir_estudiante(sistema)

    def formato(curso: Curso) -> str:
        """Marca los cursos donde la inscripción no sería posible, para orientar.

        Solo es una ayuda visual: las validaciones reales (duplicado y
        prerrequisito) las sigue aplicando `sistema.inscribir`.
        """
        if (estudiante.carne, curso.codigo) in sistema.inscripciones:
            return f"{curso}   <- YA INSCRITO"
        if curso.prerrequisito and not sistema.tiene_aprobado(estudiante.carne, curso.prerrequisito):
            return f"{curso}   <- requiere aprobar {curso.prerrequisito}"
        return str(curso)

    curso = elegir_curso(sistema, f"Seleccione el curso para {estudiante.nombre}", formato=formato)
    sistema.inscribir(estudiante.carne, curso.codigo)  # aplica duplicados y prerrequisitos
    print(f"\n  [OK] Inscripción registrada: {estudiante.nombre} en {curso.nombre} ({curso.codigo}).")


def opcion_retirar_estudiante(sistema: SistemaGestion) -> None:
    """Elimina la inscripción de un estudiante en un curso, previa confirmación."""
    encabezado("Retirar estudiante de un curso")
    estudiante = elegir_estudiante(sistema)
    inscripcion = elegir_inscripcion(
        sistema, estudiante, f"Seleccione el curso del que se retirará a {estudiante.nombre}"
    )
    curso = sistema.cursos[inscripcion.codigo_curso]

    print(f"\n  Se retirará a {estudiante.nombre} de {curso}.")
    if inscripcion.notas:
        print(f"  ATENCIÓN: se borrarán sus {len(inscripcion.notas)} nota(s) de este curso.")

    if not confirmar("\n  ¿Desea continuar? (s/n): "):
        print("\n  Operación cancelada. No se borró nada.")
        return
    sistema.retirar_estudiante(estudiante.carne, curso.codigo)
    print(f"\n  [OK] {estudiante.nombre} fue retirado de {curso.nombre}.")


def opcion_registrar_calificacion(sistema: SistemaGestion) -> None:
    """Registra o modifica la nota de una evaluación."""
    encabezado("Registrar / modificar calificación")
    estudiante = elegir_estudiante(sistema)
    inscripcion = elegir_inscripcion(
        sistema, estudiante, f"Seleccione el curso a calificar de {estudiante.nombre}"
    )
    curso = sistema.cursos[inscripcion.codigo_curso]

    # Lista de evaluaciones mostrando la nota actual de cada una
    print(f"\n  Evaluaciones de {curso.nombre}:")
    nombres = list(EVALUACIONES.keys())
    for numero, evaluacion in enumerate(nombres, start=1):
        actual = inscripcion.notas.get(evaluacion)
        texto_nota = f"nota actual: {actual:.2f}" if actual is not None else "sin nota"
        print(f"    {numero}. {evaluacion} ({EVALUACIONES[evaluacion]:g}%) - {texto_nota}")

    indice = input_validado(
        f"\nSeleccione la evaluación (1-{len(nombres)}) o 'cancelar': ",
        int, minimo=1, maximo=len(nombres),
    )
    evaluacion = nombres[indice - 1]
    nota = input_validado(
        f"Nota para '{evaluacion}' ({NOTA_MINIMA:g} a {NOTA_MAXIMA:g}): ",
        float, minimo=NOTA_MINIMA, maximo=NOTA_MAXIMA,
    )

    fue_modificacion = sistema.registrar_calificacion(
        estudiante.carne, curso.codigo, evaluacion, nota
    )
    accion = "modificada" if fue_modificacion else "registrada"
    print(f"\n  [OK] Nota {accion}: {evaluacion} = {nota:.2f}")
    print(f"       Promedio actual: {formato_nota(inscripcion.promedio())} | "
          f"Estado: {inscripcion.estado()}")


def opcion_eliminar_calificacion(sistema: SistemaGestion) -> None:
    """Elimina la nota de una evaluación (queda como 'sin nota')."""
    encabezado("Eliminar calificación")
    estudiante = elegir_estudiante(sistema)
    inscripcion = elegir_inscripcion(
        sistema, estudiante, f"Seleccione el curso de {estudiante.nombre}"
    )
    curso = sistema.cursos[inscripcion.codigo_curso]

    # Solo se ofrecen las evaluaciones que realmente tienen nota
    con_nota = [ev for ev in EVALUACIONES if ev in inscripcion.notas]
    if not con_nota:
        raise ErrorGestion(f"{estudiante.nombre} no tiene notas registradas en {curso.nombre}.")

    evaluacion = elegir_de_lista(
        "Seleccione la nota que desea eliminar",
        con_nota,
        lambda ev: f"{ev} ({EVALUACIONES[ev]:g}%) - nota: {inscripcion.notas[ev]:.2f}",
    )

    if not confirmar(f"\n  ¿Eliminar la nota de '{evaluacion}'? (s/n): "):
        print("\n  Operación cancelada. No se borró nada.")
        return
    sistema.eliminar_calificacion(estudiante.carne, curso.codigo, evaluacion)
    print(f"\n  [OK] Nota eliminada: {evaluacion} (ahora sin nota).")
    print(f"       Promedio actual: {formato_nota(inscripcion.promedio())} | "
          f"Estado: {inscripcion.estado()}")
