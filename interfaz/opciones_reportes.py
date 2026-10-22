# -*- coding: utf-8 -*-
"""
interfaz/opciones_reportes.py
=============================
Reportes de consulta:
  - cursos inscritos de un estudiante,
  - estudiantes inscritos en un curso,
  - historial académico detallado de un estudiante.

En los tres el estudiante o el curso se elige de una lista numerada.
"""

from config import EVALUACIONES
from interfaz.presentacion import encabezado, formato_nota
from interfaz.selectores import elegir_curso, elegir_estudiante
from servicios.sistema_gestion import SistemaGestion


def opcion_cursos_de_estudiante(sistema: SistemaGestion) -> None:
    """Reporte: cursos en los que está inscrito un estudiante."""
    encabezado("Cursos inscritos de un estudiante")
    estudiante = elegir_estudiante(sistema)
    inscripciones = sistema.cursos_de_estudiante(estudiante.carne)

    print(f"\n  Estudiante: {estudiante}")
    if not inscripciones:
        print("  (No tiene cursos inscritos)")
        return

    print("\n  " + "-" * 66)
    print(f"  {'Código':<10}{'Curso':<26}{'Créd.':<7}{'Profesor':<23}")
    print("  " + "-" * 66)
    for inscripcion in inscripciones:
        curso = sistema.cursos[inscripcion.codigo_curso]
        profesor = sistema.nombre_profesor_de_curso(curso)
        print(f"  {curso.codigo:<10}{curso.nombre[:24]:<26}{curso.creditos:<7}{profesor[:22]:<23}")
    print("  " + "-" * 66)
    print(f"  Total de cursos: {len(inscripciones)}")


def opcion_estudiantes_de_curso(sistema: SistemaGestion) -> None:
    """Reporte: estudiantes inscritos en un curso."""
    encabezado("Estudiantes inscritos en un curso")
    curso = elegir_curso(sistema)
    inscripciones = sistema.estudiantes_de_curso(curso.codigo)

    print(f"\n  Curso: {curso}")
    print(f"  Profesor: {sistema.nombre_profesor_de_curso(curso)}")
    if not inscripciones:
        print("  (No hay estudiantes inscritos)")
        return

    print("\n  " + "-" * 66)
    print(f"  {'Carné':<12}{'Nombre':<28}{'Promedio':<11}{'Estado':<12}")
    print("  " + "-" * 66)
    for inscripcion in inscripciones:
        estudiante = sistema.estudiantes[inscripcion.carne]
        print(
            f"  {estudiante.carne:<12}{estudiante.nombre[:26]:<28}"
            f"{formato_nota(inscripcion.promedio()):<11}{inscripcion.estado():<12}"
        )
    print("  " + "-" * 66)
    print(f"  Total de estudiantes: {len(inscripciones)}")


def opcion_historial(sistema: SistemaGestion) -> None:
    """Reporte: historial académico detallado de un estudiante."""
    encabezado("Historial académico")
    estudiante = elegir_estudiante(sistema)
    inscripciones = sistema.cursos_de_estudiante(estudiante.carne)

    print("\n" + "=" * 70)
    print("                  HISTORIAL ACADÉMICO DETALLADO")
    print("=" * 70)
    print(f"  Carné : {estudiante.carne}")
    print(f"  Nombre: {estudiante.nombre}")
    print(f"  Correo: {estudiante.correo}")
    print("=" * 70)

    if not inscripciones:
        print("  (El estudiante no ha tomado cursos)")
        return

    # Acumuladores para el resumen final
    aprobados = reprobados = en_curso = 0
    creditos_aprobados = 0
    creditos_finalizados = 0
    suma_ponderada = 0.0  # suma de (nota final * créditos) de cursos finalizados

    for inscripcion in inscripciones:
        curso = sistema.cursos[inscripcion.codigo_curso]
        print(f"\n  Curso   : {curso.nombre} ({curso.codigo}) - {curso.creditos} créditos")
        print(f"  Profesor: {sistema.nombre_profesor_de_curso(curso)}")
        print("  Evaluaciones:")
        for evaluacion, peso in EVALUACIONES.items():
            nota = inscripcion.notas.get(evaluacion)
            print(f"     - {evaluacion:<14} ({peso:>4g}%): {formato_nota(nota)}")

        estado = inscripcion.estado()
        etiqueta = "Nota final" if inscripcion.esta_completa() else "Promedio parcial"
        print(f"  {etiqueta}: {formato_nota(inscripcion.promedio())}  =>  ESTADO: {estado}")
        print("  " + "-" * 66)

        # Se acumulan los totales según el estado del curso
        if estado == "APRUEBA":
            aprobados += 1
            creditos_aprobados += curso.creditos
        elif estado == "REPRUEBA":
            reprobados += 1
        else:
            en_curso += 1
        if inscripcion.esta_completa():
            creditos_finalizados += curso.creditos
            suma_ponderada += inscripcion.promedio() * curso.creditos

    print("\n  RESUMEN")
    print(f"     Cursos aprobados  : {aprobados}")
    print(f"     Cursos reprobados : {reprobados}")
    print(f"     Cursos en curso   : {en_curso}")
    print(f"     Créditos aprobados: {creditos_aprobados}")
    if creditos_finalizados > 0:
        promedio_general = suma_ponderada / creditos_finalizados
        print(f"     Promedio general (ponderado por créditos): {promedio_general:.2f}")
    else:
        print("     Promedio general: N/D (aún no hay cursos finalizados)")
    print("=" * 70)
