# -*- coding: utf-8 -*-
"""
excepciones.py
==============
Excepciones personalizadas del sistema.

Separar los errores "esperados" (reglas de negocio, archivos dañados, datos
inexistentes) de los errores inesperados del código permite que la interfaz
muestre un mensaje claro al usuario sin mostrar trazas técnicas.
"""


class ErrorGestion(Exception):
    """Error de regla de negocio.

    Se lanza cuando una operación viola una regla del sistema: identificadores
    duplicados, inscripciones repetidas, prerrequisitos sin aprobar, notas
    fuera de rango, datos inexistentes, etc.
    """


class ErrorPersistencia(ErrorGestion):
    """Error al guardar o cargar datos desde un archivo JSON.

    Hereda de ErrorGestion para que cualquier bloque `except ErrorGestion`
    también capture los problemas de lectura/escritura de archivos y los
    muestre al usuario como un mensaje amigable.
    """
