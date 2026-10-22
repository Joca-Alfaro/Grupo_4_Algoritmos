# -*- coding: utf-8 -*-
"""
interfaz/opciones_profesores.py
===============================
Opciones del menú relacionadas con profesores:
registrar, consultar, modificar y eliminar.
"""

from interfaz.presentacion import encabezado
from interfaz.selectores import elegir_profesor
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import confirmar, input_validado, pedir_id_nuevo


def opcion_registrar_profesor(sistema: SistemaGestion) -> None:
    """Pide los datos y registra un profesor nuevo."""
    encabezado("Registrar profesor")
    id_profesor = pedir_id_nuevo(
        "ID del profesor (único, sin espacios): ", sistema.profesores, "un profesor"
    )
    nombre = input_validado("Nombre completo: ")
    especialidad = input_validado("Especialidad: ")
    profesor = sistema.registrar_profesor(id_profesor, nombre, especialidad)
    print(f"\n  [OK] Profesor registrado: {profesor}")


def opcion_listar_profesores(sistema: SistemaGestion) -> None:
    """Muestra todos los profesores registrados."""
    print("\n--- LISTA DE PROFESORES ---")
    if not sistema.profesores:
        print("  (No hay profesores registrados)")
        return
    for profesor in sistema.profesores.values():
        print("  " + str(profesor))
    print(f"\n  Total: {len(sistema.profesores)}")


def opcion_modificar_profesor(sistema: SistemaGestion) -> None:
    """Modifica el nombre y/o la especialidad de un profesor elegido de la lista."""
    encabezado("Modificar profesor")
    profesor = elegir_profesor(sistema, "Seleccione el profesor a modificar")

    print(f"\n  ID          : {profesor.id_profesor}  (no se puede modificar)")
    print(f"  Nombre      : {profesor.nombre}")
    print(f"  Especialidad: {profesor.especialidad}")
    print("\n  Presione ENTER para conservar el valor actual.")

    nombre = input_validado(f"Nuevo nombre [{profesor.nombre}]: ", permitir_vacio=True)
    especialidad = input_validado(
        f"Nueva especialidad [{profesor.especialidad}]: ", permitir_vacio=True
    )

    cambios = {}
    if nombre is not None and nombre != profesor.nombre:
        cambios["nombre"] = nombre
    if especialidad is not None and especialidad != profesor.especialidad:
        cambios["especialidad"] = especialidad
    if not cambios:
        print("\n  No se realizaron cambios.")
        return

    antes = (profesor.nombre, profesor.especialidad)
    sistema.modificar_profesor(profesor.id_profesor, **cambios)
    print("\n  [OK] Profesor modificado:")
    if "nombre" in cambios:
        print(f"       Nombre      : {antes[0]}  ->  {profesor.nombre}")
    if "especialidad" in cambios:
        print(f"       Especialidad: {antes[1]}  ->  {profesor.especialidad}")


def opcion_eliminar_profesor(sistema: SistemaGestion) -> None:
    """Elimina un profesor previa confirmación; sus cursos quedan sin asignar."""
    encabezado("Eliminar profesor")
    profesor = elegir_profesor(sistema, "Seleccione el profesor a eliminar")

    cursos = sistema.cursos_de_profesor(profesor.id_profesor)
    print(f"\n  Se eliminará: {profesor}")
    if cursos:
        print("  ATENCIÓN: estos cursos quedarán 'Sin asignar':")
        for curso in cursos:
            print(f"     - {curso}")

    if not confirmar("\n  ¿Eliminar definitivamente? (s/n): "):
        print("\n  Eliminación cancelada. No se borró nada.")
        return
    sistema.eliminar_profesor(profesor.id_profesor)
    print(f"\n  [OK] Profesor eliminado: {profesor.nombre}")
