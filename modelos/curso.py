# -*- coding: utf-8 -*-
"""
modelos/curso.py
================
Clase `Curso`: representa un curso del pensum.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from excepciones import ErrorPersistencia
from utilidades.validadores import extraer_campo


@dataclass
class Curso:
    """Representa un curso del pensum.

    Atributos:
        codigo        : código único del curso (clave en el sistema).
        nombre        : nombre del curso.
        creditos      : cantidad de créditos (entero positivo).
        id_profesor   : ID del profesor responsable (None si aún no tiene).
        prerrequisito : código de un curso que debe estar aprobado para poder
                        inscribirse en este (None si no tiene prerrequisito).
    """

    codigo: str
    nombre: str
    creditos: int
    id_profesor: Optional[str] = None
    prerrequisito: Optional[str] = None

    def __str__(self) -> str:
        """Texto legible para mostrar el curso en la consola."""
        return f"[{self.codigo}] {self.nombre} ({self.creditos} créditos)"

    # ------------------------------------------------------------------
    # Serialización a JSON
    # ------------------------------------------------------------------
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte el curso en un diccionario listo para guardar en JSON."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "creditos": self.creditos,
            "id_profesor": self.id_profesor,
            "prerrequisito": self.prerrequisito,
        }

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "Curso":
        """Reconstruye un curso a partir de un diccionario leído de JSON.

        El profesor y el prerrequisito son opcionales; la existencia real de
        esos códigos se verifica después, a nivel de todo el sistema.
        """
        contexto = "Curso"
        creditos = extraer_campo(datos, "creditos", int, contexto)
        if creditos <= 0:
            raise ErrorPersistencia(f"{contexto}: los créditos deben ser mayores que cero.")
        return cls(
            codigo=extraer_campo(datos, "codigo", str, contexto),
            nombre=extraer_campo(datos, "nombre", str, contexto),
            creditos=creditos,
            id_profesor=extraer_campo(datos, "id_profesor", str, contexto, opcional=True),
            prerrequisito=extraer_campo(datos, "prerrequisito", str, contexto, opcional=True),
        )
