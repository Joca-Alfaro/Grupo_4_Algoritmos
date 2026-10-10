# -*- coding: utf-8 -*-
"""
Paquete de modelos: clases que representan las entidades del dominio.

Se reexportan aquí para poder escribir simplemente:
    from modelos import Estudiante, Profesor, Curso, Inscripcion
"""

from modelos.curso import Curso
from modelos.estudiante import Estudiante
from modelos.inscripcion import Inscripcion
from modelos.profesor import Profesor

__all__ = ["Curso", "Estudiante", "Inscripcion", "Profesor"]
