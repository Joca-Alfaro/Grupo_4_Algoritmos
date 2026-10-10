# -*- coding: utf-8 -*-
"""
servicios/datos_prueba.py
=========================
Datos de ejemplo para probar el sistema de inmediato, sin escribir nada a mano.

Incluye casos pensados para demostrar cada regla del sistema:
  - Ana aprueba MAT101 y PRG101, por lo que PUEDE cursar MAT201 y PRG201.
  - Luis reprueba MAT101, por lo que NO puede cursar MAT201 (prerrequisito).
  - María tiene un curso aprobado por muy poco margen y otro aún en curso.
  - José está inscrito pero todavía no tiene notas.
"""

from excepciones import ErrorGestion
from servicios.sistema_gestion import SistemaGestion


def cargar_datos_prueba(sistema: SistemaGestion) -> int:
    """Precarga datos de ejemplo en el sistema.

    Si algún dato ya existe (por ejemplo, si se ejecuta dos veces), se omite
    sin interrumpir la carga, de modo que nunca se duplica nada.

    Retorna:
        La cantidad de registros nuevos que se crearon.
    """
    creados = 0

    def intentar(funcion, *argumentos) -> None:
        """Ejecuta un registro y cuenta si se creó; ignora si ya existía."""
        nonlocal creados
        try:
            funcion(*argumentos)
            creados += 1
        except ErrorGestion:
            pass  # el dato ya existía: se omite

    def inscribir_con_notas(carne: str, codigo: str, notas: dict) -> None:
        """Inscribe a un estudiante y registra las notas indicadas."""
        nonlocal creados
        try:
            sistema.inscribir(carne, codigo)
        except ErrorGestion:
            return  # ya estaba inscrito o no cumple el prerrequisito
        creados += 1
        for evaluacion, nota in notas.items():
            sistema.registrar_calificacion(carne, codigo, evaluacion, nota)

    # --- Profesores ---
    intentar(sistema.registrar_profesor, "P001", "Dr. Carlos Méndez", "Ingeniería de Software")
    intentar(sistema.registrar_profesor, "P002", "Dra. Lucía Ramírez", "Matemática Aplicada")
    intentar(sistema.registrar_profesor, "P003", "Ing. Roberto Castillo", "Bases de Datos")

    # --- Estudiantes ---
    intentar(sistema.registrar_estudiante, "2024001", "Ana García", "ana.garcia@correo.com")
    intentar(sistema.registrar_estudiante, "2024002", "Luis Pérez", "luis.perez@correo.com")
    intentar(sistema.registrar_estudiante, "2024003", "María López", "maria.lopez@correo.com")
    intentar(sistema.registrar_estudiante, "2024004", "José Hernández", "jose.hernandez@correo.com")

    # --- Cursos (con prerrequisitos: MAT101 -> MAT201 y PRG101 -> PRG201) ---
    intentar(sistema.registrar_curso, "MAT101", "Matemática I", 5, None)
    intentar(sistema.registrar_curso, "PRG101", "Programación I", 6, None)
    intentar(sistema.registrar_curso, "MAT201", "Matemática II", 5, "MAT101")
    intentar(sistema.registrar_curso, "PRG201", "Programación II", 6, "PRG101")
    intentar(sistema.registrar_curso, "BDD201", "Bases de Datos", 5, None)

    # --- Asignación de profesores a los cursos ---
    for codigo, id_profesor in [
        ("MAT101", "P002"), ("MAT201", "P002"),
        ("PRG101", "P001"), ("PRG201", "P001"),
        ("BDD201", "P003"),
    ]:
        try:
            sistema.asignar_profesor(codigo, id_profesor)
        except ErrorGestion:
            pass

    # --- Inscripciones con notas de ejemplo ---
    # Ana: aprueba MAT101 y PRG101 (podrá cursar MAT201 y PRG201)
    inscribir_con_notas("2024001", "MAT101",
                        {"Parcial 1": 85, "Parcial 2": 90, "Proyecto": 88, "Examen Final": 92})
    inscribir_con_notas("2024001", "PRG101",
                        {"Parcial 1": 95, "Parcial 2": 90, "Proyecto": 100, "Examen Final": 94})
    # Luis: reprueba MAT101 (no podrá cursar MAT201)
    inscribir_con_notas("2024002", "MAT101",
                        {"Parcial 1": 40, "Parcial 2": 55, "Proyecto": 60, "Examen Final": 45})
    # María: aprueba MAT101 por poco margen; PRG101 aún en curso
    inscribir_con_notas("2024003", "MAT101",
                        {"Parcial 1": 65, "Parcial 2": 62, "Proyecto": 70, "Examen Final": 61})
    inscribir_con_notas("2024003", "PRG101", {"Parcial 1": 78, "Parcial 2": 82})
    # Ana cursa Matemática II (en curso, con una sola nota)
    inscribir_con_notas("2024001", "MAT201", {"Parcial 1": 90})
    # José: solo inscrito, sin notas
    inscribir_con_notas("2024004", "BDD201", {})

    return creados
