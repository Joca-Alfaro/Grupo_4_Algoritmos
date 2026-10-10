# -*- coding: utf-8 -*-
"""
modelos/inscripcion.py
======================
Clase `Inscripcion`: relaciona a un estudiante con un curso y guarda sus
calificaciones. Es también la responsable de calcular el promedio ponderado y
el estado académico (APRUEBA / REPRUEBA / EN CURSO).
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from config import EVALUACIONES, NOTA_APROBACION, NOTA_MAXIMA, NOTA_MINIMA
from excepciones import ErrorGestion, ErrorPersistencia
from utilidades.validadores import extraer_campo


@dataclass
class Inscripcion:
    """Relaciona a un estudiante con un curso y guarda sus calificaciones.

    Atributos:
        carne        : carné del estudiante inscrito.
        codigo_curso : código del curso.
        notas        : diccionario {nombre_de_evaluación: nota}. Solo contiene
                       las evaluaciones que ya fueron registradas.
    """

    carne: str
    codigo_curso: str
    notas: Dict[str, float] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Calificaciones
    # ------------------------------------------------------------------
    def registrar_nota(self, evaluacion: str, nota: float) -> None:
        """Registra o modifica la nota de una evaluación.

        Valida que la evaluación exista y que la nota sea un número finito
        dentro del rango permitido. Si la evaluación ya tenía nota, se
        sobrescribe (así funciona la "modificación" de calificaciones).
        """
        if evaluacion not in EVALUACIONES:
            raise ErrorGestion(f"La evaluación '{evaluacion}' no existe.")

        # Se rechaza todo lo que no sea un número real (texto, bool, nan, inf)
        if isinstance(nota, bool) or not isinstance(nota, (int, float)) or not math.isfinite(nota):
            raise ErrorGestion("La nota debe ser un valor numérico válido.")

        if nota < NOTA_MINIMA or nota > NOTA_MAXIMA:
            raise ErrorGestion(
                f"La nota debe estar entre {NOTA_MINIMA:g} y {NOTA_MAXIMA:g}."
            )
        self.notas[evaluacion] = float(nota)

    def esta_completa(self) -> bool:
        """Indica si ya se registraron TODAS las evaluaciones del curso."""
        return all(evaluacion in self.notas for evaluacion in EVALUACIONES)

    def promedio(self) -> Optional[float]:
        """Calcula el promedio ponderado con las evaluaciones registradas.

        Fórmula: suma(nota * peso) / suma(pesos de las evaluaciones con nota).

        Si todavía faltan evaluaciones, se obtiene un promedio parcial
        proporcional a lo ya evaluado. Cuando todas están registradas, el
        resultado equivale a la nota final del curso.

        Retorna None si aún no hay ninguna nota.
        """
        if not self.notas:
            return None
        suma_ponderada = sum(nota * EVALUACIONES[ev] for ev, nota in self.notas.items())
        suma_pesos = sum(EVALUACIONES[ev] for ev in self.notas)
        return suma_ponderada / suma_pesos

    def estado(self) -> str:
        """Determina el estado académico del curso.

        Posibles valores:
          - "SIN NOTAS" : no se ha registrado ninguna evaluación.
          - "EN CURSO"  : faltan evaluaciones por registrar.
          - "APRUEBA"   : evaluaciones completas y promedio >= NOTA_APROBACION.
          - "REPRUEBA"  : evaluaciones completas y promedio < NOTA_APROBACION.
        """
        if not self.notas:
            return "SIN NOTAS"
        if not self.esta_completa():
            return "EN CURSO"
        return "APRUEBA" if self.promedio() >= NOTA_APROBACION else "REPRUEBA"

    def esta_aprobado(self) -> bool:
        """True únicamente si el curso está finalizado y aprobado."""
        return self.estado() == "APRUEBA"

    # ------------------------------------------------------------------
    # Serialización a JSON
    # ------------------------------------------------------------------
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte la inscripción en un diccionario listo para guardar en JSON."""
        return {
            "carne": self.carne,
            "codigo_curso": self.codigo_curso,
            "notas": dict(self.notas),
        }

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "Inscripcion":
        """Reconstruye una inscripción a partir de un diccionario leído de JSON.

        Las notas se vuelven a registrar con `registrar_nota`, de modo que un
        archivo editado a mano con notas fuera de rango o evaluaciones
        inexistentes sea rechazado igual que si se escribiera en la consola.
        """
        carne = extraer_campo(datos, "carne", str, "Inscripción")
        codigo_curso = extraer_campo(datos, "codigo_curso", str, "Inscripción")
        contexto = f"Inscripción ({carne}, {codigo_curso})"

        notas_crudas = datos.get("notas", {})
        if not isinstance(notas_crudas, dict):
            raise ErrorPersistencia(f"{contexto}: el campo 'notas' debe ser un objeto.")

        inscripcion = cls(carne, codigo_curso)
        for evaluacion, nota in notas_crudas.items():
            try:
                inscripcion.registrar_nota(evaluacion, nota)
            except ErrorGestion as error:
                # Se reenvía como error de persistencia indicando dónde ocurrió
                raise ErrorPersistencia(f"{contexto}: {error}") from error
        return inscripcion
