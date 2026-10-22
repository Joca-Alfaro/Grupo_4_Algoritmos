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

from typing import Any, Dict, List, Optional, Tuple

from excepciones import ErrorGestion, ErrorPersistencia
from modelos import Curso, Estudiante, Inscripcion, Profesor
from utilidades.validadores import es_correo_valido


class _SinCambio:
    """Tipo del valor especial SIN_CAMBIO (solo existe una instancia)."""

    def __repr__(self) -> str:
        return "SIN_CAMBIO"


# Valor especial para los métodos modificar_*: significa "no cambies este dato".
# Se necesita porque None ya tiene significado propio en algunos campos
# (por ejemplo, un curso SIN prerrequisito tiene prerrequisito=None).
SIN_CAMBIO = _SinCambio()


def _texto_modificado(nuevo: Any, actual: str, campo: str) -> str:
    """Devuelve el texto resultante de una modificación (validado).

    Si `nuevo` es SIN_CAMBIO se conserva el valor actual; de lo contrario
    debe ser un texto no vacío (se le quitan los espacios sobrantes).
    """
    if nuevo is SIN_CAMBIO:
        return actual
    if not isinstance(nuevo, str) or not nuevo.strip():
        raise ErrorGestion(f"El {campo} no puede estar vacío.")
    return nuevo.strip()


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
        if not es_correo_valido(correo):
            raise ErrorGestion(f"El correo '{correo}' no tiene un formato válido.")
        estudiante = Estudiante(carne, nombre, correo)
        self.estudiantes[carne] = estudiante
        self.cambios_sin_guardar = True
        return estudiante

    def obtener_estudiante(self, carne: str) -> Estudiante:
        """Devuelve el estudiante, o lanza error si no existe."""
        if carne not in self.estudiantes:
            raise ErrorGestion(f"No existe un estudiante con el carné '{carne}'.")
        return self.estudiantes[carne]

    def modificar_estudiante(
        self, carne: str, nombre: Any = SIN_CAMBIO, correo: Any = SIN_CAMBIO
    ) -> Estudiante:
        """Modifica el nombre y/o el correo de un estudiante.

        El carné NO se puede modificar: es la clave con la que se enlazan sus
        inscripciones y notas. Solo se cambian los datos indicados; los demás
        se conservan. Primero se valida todo y luego se aplica, de modo que si
        un dato es inválido no se aplica ningún cambio.
        """
        estudiante = self.obtener_estudiante(carne)
        nuevo_nombre = _texto_modificado(nombre, estudiante.nombre, "nombre")
        nuevo_correo = _texto_modificado(correo, estudiante.correo, "correo")
        if not es_correo_valido(nuevo_correo):
            raise ErrorGestion(f"El correo '{nuevo_correo}' no tiene un formato válido.")

        if (nuevo_nombre, nuevo_correo) != (estudiante.nombre, estudiante.correo):
            estudiante.nombre = nuevo_nombre
            estudiante.correo = nuevo_correo
            self.cambios_sin_guardar = True
        return estudiante

    def eliminar_estudiante(self, carne: str) -> int:
        """Elimina un estudiante junto con todas sus inscripciones y notas.

        Retorna la cantidad de inscripciones que se eliminaron en cascada.
        """
        self.obtener_estudiante(carne)
        claves = [clave for clave in self.inscripciones if clave[0] == carne]
        for clave in claves:
            del self.inscripciones[clave]
        del self.estudiantes[carne]
        self.cambios_sin_guardar = True
        return len(claves)

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

    def modificar_profesor(
        self, id_profesor: str, nombre: Any = SIN_CAMBIO, especialidad: Any = SIN_CAMBIO
    ) -> Profesor:
        """Modifica el nombre y/o la especialidad de un profesor.

        El ID NO se puede modificar (los cursos lo usan como referencia).
        Se valida todo antes de aplicar cualquier cambio.
        """
        profesor = self.obtener_profesor(id_profesor)
        nuevo_nombre = _texto_modificado(nombre, profesor.nombre, "nombre")
        nueva_especialidad = _texto_modificado(especialidad, profesor.especialidad, "especialidad")

        if (nuevo_nombre, nueva_especialidad) != (profesor.nombre, profesor.especialidad):
            profesor.nombre = nuevo_nombre
            profesor.especialidad = nueva_especialidad
            self.cambios_sin_guardar = True
        return profesor

    def cursos_de_profesor(self, id_profesor: str) -> List[Curso]:
        """Lista los cursos que tiene asignados un profesor."""
        self.obtener_profesor(id_profesor)
        return [c for c in self.cursos.values() if c.id_profesor == id_profesor]

    def eliminar_profesor(self, id_profesor: str) -> List[str]:
        """Elimina un profesor; sus cursos quedan "Sin asignar".

        Retorna los códigos de los cursos que se quedaron sin profesor.
        """
        afectados = self.cursos_de_profesor(id_profesor)
        for curso in afectados:
            curso.id_profesor = None
        del self.profesores[id_profesor]
        self.cambios_sin_guardar = True
        return [curso.codigo for curso in afectados]

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

    def _cadena_incluye(self, inicio: str, buscado: str) -> bool:
        """True si, siguiendo la cadena de prerrequisitos desde `inicio`
        (incluido), se llega al curso `buscado`.

        Sirve para detectar ciclos: si el nuevo prerrequisito de un curso ya
        depende (directa o indirectamente) de ese mismo curso, se formaría un
        ciclo. El conjunto `visitados` evita bucles infinitos.
        """
        actual: Optional[str] = inicio
        visitados = set()
        while actual and actual not in visitados:
            if actual == buscado:
                return True
            visitados.add(actual)
            curso = self.cursos.get(actual)
            actual = curso.prerrequisito if curso else None
        return False

    def cursos_posibles_prerrequisito(self, codigo: str) -> List[Curso]:
        """Cursos que se pueden usar como prerrequisito de `codigo`.

        Se excluyen el propio curso y los que dependen de él, porque
        formarían un ciclo.
        """
        self.obtener_curso(codigo)
        return [
            c for c in self.cursos.values()
            if c.codigo != codigo and not self._cadena_incluye(c.codigo, codigo)
        ]

    def cursos_que_dependen_de(self, codigo: str) -> List[Curso]:
        """Cursos que tienen a `codigo` como prerrequisito directo."""
        self.obtener_curso(codigo)
        return [c for c in self.cursos.values() if c.prerrequisito == codigo]

    def modificar_curso(
        self,
        codigo: str,
        nombre: Any = SIN_CAMBIO,
        creditos: Any = SIN_CAMBIO,
        prerrequisito: Any = SIN_CAMBIO,
        id_profesor: Any = SIN_CAMBIO,
    ) -> Curso:
        """Modifica los datos de un curso.

        El código NO se puede modificar (inscripciones y otros cursos lo usan
        como referencia). Para quitar el prerrequisito o el profesor se pasa
        None; para dejarlos igual, SIN_CAMBIO. Se valida todo antes de aplicar
        cualquier cambio, así que un dato inválido no deja el curso a medias.
        """
        curso = self.obtener_curso(codigo)
        nuevo_nombre = _texto_modificado(nombre, curso.nombre, "nombre")

        nuevos_creditos = curso.creditos
        if creditos is not SIN_CAMBIO:
            if isinstance(creditos, bool) or not isinstance(creditos, int) or creditos <= 0:
                raise ErrorGestion("Los créditos deben ser un número entero mayor que cero.")
            nuevos_creditos = creditos

        nuevo_prerrequisito = curso.prerrequisito
        if prerrequisito is not SIN_CAMBIO:
            if prerrequisito is not None:
                if prerrequisito == codigo:
                    raise ErrorGestion("Un curso no puede ser prerrequisito de sí mismo.")
                if prerrequisito not in self.cursos:
                    raise ErrorGestion(f"El prerrequisito '{prerrequisito}' no existe.")
                if self._cadena_incluye(prerrequisito, codigo):
                    raise ErrorGestion(
                        f"'{prerrequisito}' ya depende de '{codigo}': "
                        "ese prerrequisito formaría un ciclo."
                    )
            nuevo_prerrequisito = prerrequisito

        nuevo_profesor = curso.id_profesor
        if id_profesor is not SIN_CAMBIO:
            if id_profesor is not None:
                self.obtener_profesor(id_profesor)  # valida que exista
            nuevo_profesor = id_profesor

        nuevos = (nuevo_nombre, nuevos_creditos, nuevo_prerrequisito, nuevo_profesor)
        if nuevos != (curso.nombre, curso.creditos, curso.prerrequisito, curso.id_profesor):
            curso.nombre, curso.creditos, curso.prerrequisito, curso.id_profesor = nuevos
            self.cambios_sin_guardar = True
        return curso

    def eliminar_curso(self, codigo: str) -> int:
        """Elimina un curso junto con sus inscripciones y notas.

        No se permite si otros cursos lo tienen como prerrequisito: primero
        hay que modificar esos cursos. Así no se alteran en silencio las
        reglas del pensum.

        Retorna la cantidad de inscripciones que se eliminaron en cascada.
        """
        self.obtener_curso(codigo)
        dependientes = self.cursos_que_dependen_de(codigo)
        if dependientes:
            lista = ", ".join(c.codigo for c in dependientes)
            raise ErrorGestion(
                f"No se puede eliminar '{codigo}': es prerrequisito de {lista}. "
                "Modifique primero esos cursos."
            )
        claves = [clave for clave in self.inscripciones if clave[1] == codigo]
        for clave in claves:
            del self.inscripciones[clave]
        del self.cursos[codigo]
        self.cambios_sin_guardar = True
        return len(claves)

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

    def retirar_estudiante(self, carne: str, codigo_curso: str) -> Inscripcion:
        """Elimina la inscripción de un estudiante en un curso (con sus notas).

        Después podrá volver a inscribirse, porque la pareja deja de existir.
        Retorna la inscripción eliminada (para informar cuántas notas se perdieron).
        """
        inscripcion = self.obtener_inscripcion(carne, codigo_curso)
        del self.inscripciones[(carne, codigo_curso)]
        self.cambios_sin_guardar = True
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

    def eliminar_calificacion(self, carne: str, codigo_curso: str, evaluacion: str) -> None:
        """Elimina la nota de una evaluación; esa evaluación queda sin nota.

        El promedio y el estado del curso se recalculan solos la próxima vez
        que se consulten (nunca se guardan calculados).
        """
        inscripcion = self.obtener_inscripcion(carne, codigo_curso)
        inscripcion.eliminar_nota(evaluacion)
        self.cambios_sin_guardar = True

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
