# -*- coding: utf-8 -*-
"""
interfaz/opciones_estudiantes.py
================================
Opciones del menú relacionadas con estudiantes:
registrar, consultar, modificar y eliminar.

Patrón de todas las operaciones: primero se piden TODOS los datos y solo al
final se aplican. Así, si el usuario escribe 'cancelar' a mitad de camino,
no queda nada registrado ni modificado a medias.
"""

from interfaz.presentacion import encabezado
from interfaz.selectores import elegir_estudiante
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import confirmar, input_validado, pedir_id_nuevo
from utilidades.validadores import es_correo_valido

MENSAJE_CORREO = "formato de correo inválido (ejemplo: nombre@dominio.com)."


def opcion_registrar_estudiante(sistema: SistemaGestion) -> None:
    """Pide los datos y registra un estudiante nuevo."""
    encabezado("Registrar estudiante")
    # Si el carné ya existe, se vuelve a preguntar en lugar de abortar
    carne = pedir_id_nuevo(
        "Carné (único, sin espacios): ", sistema.estudiantes, "un estudiante"
    )
    nombre = input_validado("Nombre completo: ")
    correo = input_validado(
        "Correo electrónico: ", validador=es_correo_valido, mensaje_validador=MENSAJE_CORREO
    )
    estudiante = sistema.registrar_estudiante(carne, nombre, correo)
    print(f"\n  [OK] Estudiante registrado: {estudiante}")


def opcion_listar_estudiantes(sistema: SistemaGestion) -> None:
    """Muestra todos los estudiantes registrados."""
    print("\n--- LISTA DE ESTUDIANTES ---")
    if not sistema.estudiantes:
        print("  (No hay estudiantes registrados)")
        return
    for estudiante in sistema.estudiantes.values():
        print("  " + str(estudiante))
    print(f"\n  Total: {len(sistema.estudiantes)}")


def opcion_modificar_estudiante(sistema: SistemaGestion) -> None:
    """Modifica el nombre y/o el correo de un estudiante elegido de la lista."""
    encabezado("Modificar estudiante")
    estudiante = elegir_estudiante(sistema, "Seleccione el estudiante a modificar")

    print(f"\n  Carné : {estudiante.carne}  (no se puede modificar)")
    print(f"  Nombre: {estudiante.nombre}")
    print(f"  Correo: {estudiante.correo}")
    print("\n  Presione ENTER para conservar el valor actual.")

    # ENTER vacío devuelve None = "no cambiar este dato"
    nombre = input_validado(
        f"Nuevo nombre [{estudiante.nombre}]: ", permitir_vacio=True
    )
    correo = input_validado(
        f"Nuevo correo [{estudiante.correo}]: ",
        validador=es_correo_valido,
        mensaje_validador=MENSAJE_CORREO,
        permitir_vacio=True,
    )

    # Solo se envían al sistema los datos que realmente cambian
    cambios = {}
    if nombre is not None and nombre != estudiante.nombre:
        cambios["nombre"] = nombre
    if correo is not None and correo != estudiante.correo:
        cambios["correo"] = correo
    if not cambios:
        print("\n  No se realizaron cambios.")
        return

    antes = (estudiante.nombre, estudiante.correo)
    sistema.modificar_estudiante(estudiante.carne, **cambios)
    print("\n  [OK] Estudiante modificado:")
    if "nombre" in cambios:
        print(f"       Nombre: {antes[0]}  ->  {estudiante.nombre}")
    if "correo" in cambios:
        print(f"       Correo: {antes[1]}  ->  {estudiante.correo}")


def opcion_eliminar_estudiante(sistema: SistemaGestion) -> None:
    """Elimina un estudiante (y sus inscripciones) previa confirmación."""
    encabezado("Eliminar estudiante")
    estudiante = elegir_estudiante(sistema, "Seleccione el estudiante a eliminar")

    # Se informa qué más se perderá antes de pedir la confirmación
    inscripciones = sistema.cursos_de_estudiante(estudiante.carne)
    total_notas = sum(len(i.notas) for i in inscripciones)
    print(f"\n  Se eliminará: {estudiante}")
    if inscripciones:
        print(f"  ATENCIÓN: también se borrarán sus {len(inscripciones)} inscripción(es) "
              f"y {total_notas} nota(s) registrada(s).")

    if not confirmar("\n  ¿Eliminar definitivamente? (s/n): "):
        print("\n  Eliminación cancelada. No se borró nada.")
        return
    sistema.eliminar_estudiante(estudiante.carne)
    print(f"\n  [OK] Estudiante eliminado: {estudiante.nombre}")
