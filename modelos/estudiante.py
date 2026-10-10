# -*- coding: utf-8 -*-
"""
modelos/estudiante.py
=====================
Clase `Estudiante`: representa a un alumno de la universidad.
"""

from dataclasses import dataclass
from typing import Any, Dict

from utilidades.validadores import extraer_campo


@dataclass
class Estudiante:
    """Representa a un estudiante de la universidad.

    Atributos:
        carne  : identificador único del estudiante (clave en el sistema).
        nombre : nombre completo.
        correo : correo electrónico.
    """

    carne: str
    nombre: str
    correo: str

    def __str__(self) -> str:
        """Texto legible para mostrar al estudiante en la consola."""
        return f"[{self.carne}] {self.nombre} - {self.correo}"

    # ------------------------------------------------------------------
    # Serialización a JSON
    # ------------------------------------------------------------------
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte el estudiante en un diccionario listo para guardar en JSON."""
        return {"carne": self.carne, "nombre": self.nombre, "correo": self.correo}

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "Estudiante":
        """Reconstruye un estudiante a partir de un diccionario leído de JSON.

        Valida que existan los campos obligatorios y que tengan el tipo
        correcto; de lo contrario lanza ErrorPersistencia.
        """
        contexto = "Estudiante"
        return cls(
            carne=extraer_campo(datos, "carne", str, contexto),
            nombre=extraer_campo(datos, "nombre", str, contexto),
            correo=extraer_campo(datos, "correo", str, contexto),
        )
