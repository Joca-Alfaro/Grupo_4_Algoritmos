# -*- coding: utf-8 -*-
"""
modelos/profesor.py
===================
Clase `Profesor`: representa a un catedrático de la universidad.
"""

from dataclasses import dataclass
from typing import Any, Dict

from utilidades.validadores import extraer_campo


@dataclass
class Profesor:
    """Representa a un profesor o catedrático.

    Atributos:
        id_profesor  : identificador único del profesor (clave en el sistema).
        nombre       : nombre completo.
        especialidad : área de especialización.
    """

    id_profesor: str
    nombre: str
    especialidad: str

    def __str__(self) -> str:
        """Texto legible para mostrar al profesor en la consola."""
        return f"[{self.id_profesor}] {self.nombre} - Especialidad: {self.especialidad}"

    # ------------------------------------------------------------------
    # Serialización a JSON
    # ------------------------------------------------------------------
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte el profesor en un diccionario listo para guardar en JSON."""
        return {
            "id_profesor": self.id_profesor,
            "nombre": self.nombre,
            "especialidad": self.especialidad,
        }

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "Profesor":
        """Reconstruye un profesor a partir de un diccionario leído de JSON."""
        contexto = "Profesor"
        return cls(
            id_profesor=extraer_campo(datos, "id_profesor", str, contexto),
            nombre=extraer_campo(datos, "nombre", str, contexto),
            especialidad=extraer_campo(datos, "especialidad", str, contexto),
        )
