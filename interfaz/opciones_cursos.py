# -*- coding: utf-8 -*-
"""
interfaz/opciones_cursos.py
===========================
Opciones del menú relacionadas con cursos:
registrar, consultar, modificar, eliminar y asignar profesor.
"""

from interfaz.presentacion import encabezado
from interfaz.selectores import elegir_curso, elegir_de_lista, elegir_profesor
from modelos import Curso
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import confirmar, input_validado, pedir_id_nuevo


def opcion_registrar_curso(sistema: SistemaGestion) -> None:
    """Pide los datos y registra un curso (con prerrequisito opcional)."""
    encabezado("Registrar curso")
    codigo = pedir_id_nuevo(
        "Código del curso (único, sin espacios): ", sistema.cursos, "un curso"
    )
    nombre = input_validado("Nombre del curso: ")
    creditos = input_validado("Créditos (1 a 20): ", int, minimo=1, maximo=20)

    # El prerrequisito se ELIGE de la lista de cursos ya registrados
    prerrequisito = None
    if sistema.cursos:
        elegido = elegir_de_lista(
            "Seleccione el prerrequisito (curso que debe estar aprobado)",
            list(sistema.cursos.values()),
            str,
            texto_ninguno="Sin prerrequisito",
        )
        prerrequisito = elegido.codigo if elegido else None

    curso = sistema.registrar_curso(codigo, nombre, creditos, prerrequisito)
    print(f"\n  [OK] Curso registrado: {curso}")
    if prerrequisito:
        print(f"       Prerrequisito: {prerrequisito}")


def opcion_listar_cursos(sistema: SistemaGestion) -> None:
    """Muestra todos los cursos con su profesor y prerrequisito."""
    print("\n--- LISTA DE CURSOS ---")
    if not sistema.cursos:
        print("  (No hay cursos registrados)")
        return
    for curso in sistema.cursos.values():
        profesor = sistema.nombre_profesor_de_curso(curso)
        prerrequisito = curso.prerrequisito if curso.prerrequisito else "Ninguno"
        print(f"  {curso}")
        print(f"      Profesor: {profesor} | Prerrequisito: {prerrequisito}")
    print(f"\n  Total: {len(sistema.cursos)}")


def opcion_modificar_curso(sistema: SistemaGestion) -> None:
    """Modifica nombre, créditos, prerrequisito y/o profesor de un curso."""
    encabezado("Modificar curso")
    curso = elegir_curso(sistema, "Seleccione el curso a modificar")

    prerrequisito_actual = curso.prerrequisito if curso.prerrequisito else "Ninguno"
    print(f"\n  Código       : {curso.codigo}  (no se puede modificar)")
    print(f"  Nombre       : {curso.nombre}")
    print(f"  Créditos     : {curso.creditos}")
    print(f"  Prerrequisito: {prerrequisito_actual}")
    print(f"  Profesor     : {sistema.nombre_profesor_de_curso(curso)}")
    print("\n  Presione ENTER para conservar el valor actual.")

    # Los cambios se acumulan en un diccionario y se aplican todos al final
    cambios = {}

    nombre = input_validado(f"Nuevo nombre [{curso.nombre}]: ", permitir_vacio=True)
    if nombre is not None and nombre != curso.nombre:
        cambios["nombre"] = nombre

    creditos = input_validado(
        f"Nuevos créditos (1 a 20) [{curso.creditos}]: ",
        int, minimo=1, maximo=20, permitir_vacio=True,
    )
    if creditos is not None and creditos != curso.creditos:
        cambios["creditos"] = creditos

    # --- Prerrequisito: solo se ofrecen cursos que no formen un ciclo ---
    if confirmar(f"\n  Prerrequisito actual: {prerrequisito_actual}. ¿Desea cambiarlo? (s/n): "):
        elegido = elegir_de_lista(
            "Seleccione el nuevo prerrequisito",
            sistema.cursos_posibles_prerrequisito(curso.codigo),
            str,
            texto_ninguno="Sin prerrequisito",
        )
        nuevo = elegido.codigo if elegido else None
        if nuevo != curso.prerrequisito:
            cambios["prerrequisito"] = nuevo

    # --- Profesor: se elige de la lista de profesores ---
    if sistema.profesores and confirmar(
        f"\n  Profesor actual: {sistema.nombre_profesor_de_curso(curso)}. "
        "¿Desea cambiarlo? (s/n): "
    ):
        profesor = elegir_profesor(sistema, "Seleccione el nuevo profesor")
        if profesor.id_profesor != curso.id_profesor:
            cambios["id_profesor"] = profesor.id_profesor

    if not cambios:
        print("\n  No se realizaron cambios.")
        return

    sistema.modificar_curso(curso.codigo, **cambios)
    print(f"\n  [OK] Curso modificado: {curso}")
    print(f"       Prerrequisito: {curso.prerrequisito if curso.prerrequisito else 'Ninguno'}"
          f" | Profesor: {sistema.nombre_profesor_de_curso(curso)}")


def opcion_eliminar_curso(sistema: SistemaGestion) -> None:
    """Elimina un curso (y sus inscripciones) previa confirmación."""
    encabezado("Eliminar curso")
    curso = elegir_curso(sistema, "Seleccione el curso a eliminar")

    # Si otros cursos lo exigen como prerrequisito, no se puede eliminar
    dependientes = sistema.cursos_que_dependen_de(curso.codigo)
    if dependientes:
        print("\n  No se puede eliminar este curso: es prerrequisito de:")
        for dependiente in dependientes:
            print(f"     - {dependiente}")
        print("  Modifique primero esos cursos (opción 'Modificar curso').")
        return

    inscripciones = sistema.estudiantes_de_curso(curso.codigo)
    total_notas = sum(len(i.notas) for i in inscripciones)
    print(f"\n  Se eliminará: {curso}")
    if inscripciones:
        print(f"  ATENCIÓN: también se borrarán {len(inscripciones)} inscripción(es) "
              f"y {total_notas} nota(s) registrada(s).")

    if not confirmar("\n  ¿Eliminar definitivamente? (s/n): "):
        print("\n  Eliminación cancelada. No se borró nada.")
        return
    sistema.eliminar_curso(curso.codigo)
    print(f"\n  [OK] Curso eliminado: {curso.nombre}")


def opcion_asignar_profesor(sistema: SistemaGestion) -> None:
    """Asigna un profesor responsable a un curso (ambos se eligen de listas)."""
    encabezado("Asignar profesor a un curso")

    def formato(curso: Curso) -> str:
        """Muestra el profesor actual de cada curso para ubicarse mejor."""
        return f"{curso}  -> Profesor: {sistema.nombre_profesor_de_curso(curso)}"

    curso = elegir_curso(sistema, "Seleccione el curso", formato=formato)
    profesor = elegir_profesor(sistema, "Seleccione el profesor responsable")
    sistema.asignar_profesor(curso.codigo, profesor.id_profesor)
    print(f"\n  [OK] Profesor '{profesor.nombre}' asignado al curso '{curso.nombre}'.")
