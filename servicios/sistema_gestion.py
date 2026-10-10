# -*- coding: utf-8 -*-
"""
servicios/sistema_gestion.py
============================
Clase `SistemaGestion`: el "cerebro" del programa.

Contiene todos los datos en memoria y aplica las reglas de negocio:
unicidad de identificadores, inscripciones sin duplicados, prerrequisitos,
registro de calificaciones y consultas para los reportes.

Esta clase NO imprime ni lee nada de la consola: solo recibe datos, valida,
y devuelve resultados o lanza ErrorGestion. Así se puede probar de forma
automática y reutilizar con cualquier interfaz.
"""

from typing import Any, Dict, List, Tuple

from excepciones import ErrorGestion, ErrorPersistencia
from modelos import Curso, Estudiante, Inscripcion, Profesor


class SistemaGestion:
    """Administra estudiantes, profesores, cursos e inscripciones.

    Estructuras internas (diccionarios, para buscar rápido por clave única):
        estudiantes   : {carne: Estudiante}
        profesores    : {id_profesor: Profesor}
        cursos        : {codigo: Curso}
        inscripciones : {(carne, codigo_curso): Inscripcion}
                        Usar la tupla como clave GARANTIZA que no pueden
                        existir dos inscripciones de la misma pareja
                        estudiante-curso.

    Atributo adicional:
        cambios_sin_guardar : True si hay modificaciones que todavía no se han
                              guardado en un archivo JSON (se usa para avisar
                              al usuario antes de salir).
    """

    def __init__(self) -> None:
        """Crea un sistema vacío."""
        self.estudiantes: Dict[str, Estudiante] = {}
        self.profesores: Dict[str, Profesor] = {}
        self.cursos: Dict[str, Curso] = {}
        self.inscripciones: Dict[Tuple[str, str], Inscripcion] = {}
        self.cambios_sin_guardar: bool = False

    # ==========================================================================
    # ESTADO GENERAL
    # ==========================================================================
    def esta_vacio(self) -> bool:
        """True si no hay ningún dato registrado en el sistema."""
        return not (self.estudiantes or self.profesores or self.cursos or self.inscripciones)

    def resumen(self) -> Dict[str, int]:
        """Devuelve la cantidad de registros de cada tipo (para mostrar al usuario)."""
        return {
            "estudiantes": len(self.estudiantes),
            "profesores": len(self.profesores),
            "cursos": len(self.cursos),
            "inscripciones": len(self.inscripciones),
        }

    # ==========================================================================
    # ESTUDIANTES
    # ==========================================================================
    def registrar_estudiante(self, carne: str, nombre: str, correo: str) -> Estudiante:
        """Registra un estudiante nuevo; el carné debe ser único."""
        if carne in self.estudiantes:
            raise ErrorGestion(f"Ya existe un estudiante con el carné '{carne}'.")
        estudiante = Estudiante(carne, nombre, correo)
        self.estudiantes[carne] = estudiante
        self.cambios_sin_guardar = True
        return estudiante

    def obtener_estudiante(self, carne: str) -> Estudiante:
        """Devuelve el estudiante, o lanza error si no existe."""
        if carne not in self.estudiantes:
            raise ErrorGestion(f"No existe un estudiante con el carné '{carne}'.")
        return self.estudiantes[carne]

    # ==========================================================================
    # PROFESORES
    # ==========================================================================
    def registrar_profesor(self, id_profesor: str, nombre: str, especialidad: str) -> Profesor:
        """Registra un profesor nuevo; el ID debe ser único."""
        if id_profesor in self.profesores:
            raise ErrorGestion(f"Ya existe un profesor con el ID '{id_profesor}'.")
        profesor = Profesor(id_profesor, nombre, especialidad)
        self.profesores[id_profesor] = profesor
        self.cambios_sin_guardar = True
        return profesor

    def obtener_profesor(self, id_profesor: str) -> Profesor:
        """Devuelve el profesor, o lanza error si no existe."""
        if id_profesor not in self.profesores:
            raise ErrorGestion(f"No existe un profesor con el ID '{id_profesor}'.")
        return self.profesores[id_profesor]

    # ==========================================================================
    # CURSOS
    # ==========================================================================
    def registrar_curso(
        self,
        codigo: str,
        nombre: str,
        creditos: int,
        prerrequisito: str = None,
    ) -> Curso:
        """Registra un curso nuevo; el código debe ser único.

        Si se indica un prerrequisito, ese curso debe existir previamente y
        no puede ser el mismo curso que se está creando.
        """
        if codigo in self.cursos:
            raise ErrorGestion(f"Ya existe un curso con el código '{codigo}'.")
        if creditos <= 0:
            raise ErrorGestion("Los créditos deben ser mayores que cero.")
        if prerrequisito is not None:
            if prerrequisito == codigo:
                raise ErrorGestion("Un curso no puede ser prerrequisito de sí mismo.")
            if prerrequisito not in self.cursos:
                raise ErrorGestion(
                    f"El prerrequisito '{prerrequisito}' no existe. Regístrelo primero."
                )
        curso = Curso(codigo, nombre, creditos, None, prerrequisito)
        self.cursos[codigo] = curso
        self.cambios_sin_guardar = True
        return curso

    def obtener_curso(self, codigo: str) -> Curso:
        """Devuelve el curso, o lanza error si no existe."""
        if codigo not in self.cursos:
            raise ErrorGestion(f"No existe un curso con el código '{codigo}'.")
        return self.cursos[codigo]

    def asignar_profesor(self, codigo_curso: str, id_profesor: str) -> None:
        """Asigna (o reasigna) el profesor responsable de un curso."""
        curso = self.obtener_curso(codigo_curso)
        self.obtener_profesor(id_profesor)  # valida que el profesor exista
        curso.id_profesor = id_profesor
        self.cambios_sin_guardar = True

    def nombre_profesor_de_curso(self, curso: Curso) -> str:
        """Devuelve el nombre del profesor del curso, o 'Sin asignar'."""
        if curso.id_profesor and curso.id_profesor in self.profesores:
            return self.profesores[curso.id_profesor].nombre
        return "Sin asignar"

    # ==========================================================================
    # INSCRIPCIONES
    # ==========================================================================
    def tiene_aprobado(self, carne: str, codigo_curso: str) -> bool:
        """True si el estudiante ya aprobó el curso indicado."""
        inscripcion = self.inscripciones.get((carne, codigo_curso))
        return inscripcion is not None and inscripcion.esta_aprobado()

    def inscribir(self, carne: str, codigo_curso: str) -> Inscripcion:
        """Inscribe a un estudiante en un curso aplicando las validaciones.

        Orden de las validaciones:
          1. El estudiante y el curso deben existir.
          2. NO se permite la inscripción duplicada (validación crítica).
          3. Si el curso tiene prerrequisito, el estudiante debe haberlo
             aprobado (evaluaciones completas y promedio >= nota de aprobación).
        """
        self.obtener_estudiante(carne)
        curso = self.obtener_curso(codigo_curso)

        # 2. Validación crítica: impedir inscribir dos veces al mismo estudiante
        if (carne, codigo_curso) in self.inscripciones:
            raise ErrorGestion(
                f"El estudiante '{carne}' ya está inscrito en el curso '{codigo_curso}'."
            )

        # 3. Validación de prerrequisito
        if curso.prerrequisito and not self.tiene_aprobado(carne, curso.prerrequisito):
            previo = self.cursos[curso.prerrequisito]
            raise ErrorGestion(
                f"No cumple el prerrequisito: debe aprobar primero "
                f"'{previo.nombre}' ({previo.codigo})."
            )

        inscripcion = Inscripcion(carne, codigo_curso)
        self.inscripciones[(carne, codigo_curso)] = inscripcion
        self.cambios_sin_guardar = True
        return inscripcion

    def obtener_inscripcion(self, carne: str, codigo_curso: str) -> Inscripcion:
        """Devuelve la inscripción, o lanza error si el estudiante no está inscrito."""
        inscripcion = self.inscripciones.get((carne, codigo_curso))
        if inscripcion is None:
            raise ErrorGestion(
                f"El estudiante '{carne}' no está inscrito en el curso '{codigo_curso}'."
            )
        return inscripcion

    # ==========================================================================
    # CALIFICACIONES
    # ==========================================================================
    def registrar_calificacion(
        self, carne: str, codigo_curso: str, evaluacion: str, nota: float
    ) -> bool:
        """Registra o modifica una nota.

        Retorna True si la evaluación ya tenía nota (fue una modificación) y
        False si era la primera vez que se registraba.
        """
        inscripcion = self.obtener_inscripcion(carne, codigo_curso)
        era_modificacion = evaluacion in inscripcion.notas
        inscripcion.registrar_nota(evaluacion, nota)  # valida el rango
        self.cambios_sin_guardar = True
        return era_modificacion

    # ==========================================================================
    # CONSULTAS PARA REPORTES
    # ==========================================================================
    def cursos_de_estudiante(self, carne: str) -> List[Inscripcion]:
        """Lista las inscripciones (cursos) de un estudiante."""
        self.obtener_estudiante(carne)
        return [insc for (c, _), insc in self.inscripciones.items() if c == carne]

    def estudiantes_de_curso(self, codigo_curso: str) -> List[Inscripcion]:
        """Lista las inscripciones (estudiantes) de un curso."""
        self.obtener_curso(codigo_curso)
        return [insc for (_, cod), insc in self.inscripciones.items() if cod == codigo_curso]

    # ==========================================================================
    # PERSISTENCIA: CONVERSIÓN A/DESDE DICCIONARIOS
    # ==========================================================================
    def a_diccionario(self) -> Dict[str, Any]:
        """Convierte todo el sistema en un diccionario listo para guardar en JSON."""
        return {
            "estudiantes": [e.a_diccionario() for e in self.estudiantes.values()],
            "profesores": [p.a_diccionario() for p in self.profesores.values()],
            "cursos": [c.a_diccionario() for c in self.cursos.values()],
            "inscripciones": [i.a_diccionario() for i in self.inscripciones.values()],
        }

    @staticmethod
    def _extraer_lista(datos: Dict[str, Any], clave: str) -> List[Any]:
        """Obtiene una sección (lista) del JSON; si no existe, devuelve lista vacía."""
        valor = datos.get(clave, [])
        if not isinstance(valor, list):
            raise ErrorPersistencia(f"La sección '{clave}' del archivo debe ser una lista.")
        return valor

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "SistemaGestion":
        """Construye un sistema nuevo a partir de un diccionario leído de JSON.

        Se arma un sistema NUEVO (sin tocar el actual) y se valida por
        completo: estructura, tipos, identificadores duplicados e integridad
        entre secciones. Solo si todo es correcto se devuelve el resultado.
        Así, un archivo dañado nunca deja el sistema a medio cargar.
        """
        if not isinstance(datos, dict):
            raise ErrorPersistencia("El archivo no tiene la estructura esperada.")

        sistema = cls()

        # --- Estudiantes ---
        for item in cls._extraer_lista(datos, "estudiantes"):
            estudiante = Estudiante.desde_diccionario(item)
            if estudiante.carne in sistema.estudiantes:
                raise ErrorPersistencia(f"Carné duplicado en el archivo: '{estudiante.carne}'.")
            sistema.estudiantes[estudiante.carne] = estudiante

        # --- Profesores ---
        for item in cls._extraer_lista(datos, "profesores"):
            profesor = Profesor.desde_diccionario(item)
            if profesor.id_profesor in sistema.profesores:
                raise ErrorPersistencia(
                    f"ID de profesor duplicado en el archivo: '{profesor.id_profesor}'."
                )
            sistema.profesores[profesor.id_profesor] = profesor

        # --- Cursos ---
        for item in cls._extraer_lista(datos, "cursos"):
            curso = Curso.desde_diccionario(item)
            if curso.codigo in sistema.cursos:
                raise ErrorPersistencia(f"Código de curso duplicado en el archivo: '{curso.codigo}'.")
            sistema.cursos[curso.codigo] = curso

        # --- Inscripciones ---
        for item in cls._extraer_lista(datos, "inscripciones"):
            inscripcion = Inscripcion.desde_diccionario(item)
            clave = (inscripcion.carne, inscripcion.codigo_curso)
            if clave in sistema.inscripciones:
                raise ErrorPersistencia(
                    f"Inscripción duplicada en el archivo: estudiante '{clave[0]}' "
                    f"en el curso '{clave[1]}'."
                )
            sistema.inscripciones[clave] = inscripcion

        # Verifica que las referencias entre secciones sean coherentes
        sistema._validar_integridad()
        sistema.cambios_sin_guardar = False
        return sistema

    def _validar_integridad(self) -> None:
        """Verifica que las referencias entre secciones sean coherentes.

        Comprueba que:
          - el profesor asignado a cada curso exista,
          - el prerrequisito de cada curso exista y no forme un ciclo
            (por ejemplo, A requiere B y B requiere A),
          - cada inscripción apunte a un estudiante y a un curso existentes.
        """
        for curso in self.cursos.values():
            # Profesor asignado
            if curso.id_profesor and curso.id_profesor not in self.profesores:
                raise ErrorPersistencia(
                    f"El curso '{curso.codigo}' tiene un profesor inexistente: "
                    f"'{curso.id_profesor}'."
                )

            # Prerrequisito
            if curso.prerrequisito:
                if curso.prerrequisito not in self.cursos:
                    raise ErrorPersistencia(
                        f"El curso '{curso.codigo}' tiene un prerrequisito inexistente: "
                        f"'{curso.prerrequisito}'."
                    )
                # Detección de ciclos: se sigue la cadena de prerrequisitos y,
                # si se vuelve a pasar por un curso ya visitado, hay un ciclo.
                visitados = set()
                actual = curso.codigo
                while actual:
                    if actual in visitados:
                        raise ErrorPersistencia(
                            f"Los prerrequisitos del curso '{curso.codigo}' forman un ciclo."
                        )
                    visitados.add(actual)
                    actual = self.cursos[actual].prerrequisito

        for (carne, codigo), _ in self.inscripciones.items():
            if carne not in self.estudiantes:
                raise ErrorPersistencia(
                    f"Una inscripción hace referencia a un estudiante inexistente: '{carne}'."
                )
            if codigo not in self.cursos:
                raise ErrorPersistencia(
                    f"Una inscripción hace referencia a un curso inexistente: '{codigo}'."
                )

    def reemplazar_datos(self, otro: "SistemaGestion") -> None:
        """Reemplaza TODOS los datos de este sistema por los de otro sistema.

        Se usa al cargar un archivo: primero se construye y valida un sistema
        nuevo y, solo si es válido, sus datos sustituyen a los actuales.
        """
        self.estudiantes = otro.estudiantes
        self.profesores = otro.profesores
        self.cursos = otro.cursos
        self.inscripciones = otro.inscripciones
        self.cambios_sin_guardar = False
