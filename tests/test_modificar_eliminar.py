# -*- coding: utf-8 -*-
"""
tests/test_modificar_eliminar.py
================================
Pruebas de las funciones de modificar, eliminar, elegir de listas y cancelar.

Tres niveles:
  1. Reglas del sistema (SistemaGestion): modificar y eliminar con sus validaciones.
  2. Entrada de consola: la palabra 'cancelar' y los selectores numerados.
  3. Flujos completos de las opciones del menú, simulando lo que escribe el usuario.

Ejecución:  python -m unittest discover -v
"""

import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

from excepciones import ErrorGestion, OperacionCancelada
from interfaz import menu
from interfaz.opciones_cursos import (
    opcion_asignar_profesor,
    opcion_eliminar_curso,
    opcion_modificar_curso,
    opcion_registrar_curso,
)
from interfaz.opciones_estudiantes import (
    opcion_eliminar_estudiante,
    opcion_modificar_estudiante,
    opcion_registrar_estudiante,
)
from interfaz.opciones_inscripciones import (
    opcion_eliminar_calificacion,
    opcion_inscribir,
    opcion_registrar_calificacion,
    opcion_retirar_estudiante,
)
from interfaz.opciones_profesores import opcion_eliminar_profesor, opcion_modificar_profesor
from interfaz.opciones_reportes import opcion_historial
from interfaz.selectores import elegir_de_lista, elegir_estudiante
from servicios.datos_prueba import cargar_datos_prueba
from servicios.persistencia import cargar_desde_json, guardar_en_json
from servicios.sistema_gestion import SIN_CAMBIO, SistemaGestion
from utilidades.consola import confirmar, input_validado, pedir_id_nuevo


def sistema_prueba() -> SistemaGestion:
    """Sistema con los datos de prueba.

    Orden de las listas (el que ve el usuario al elegir por número):
      Estudiantes: 1 Ana(2024001) 2 Luis(2024002) 3 María(2024003) 4 José(2024004)
      Profesores : 1 P001 2 P002 3 P003
      Cursos     : 1 MAT101 2 PRG101 3 MAT201 4 PRG201 5 BDD201
    """
    sistema = SistemaGestion()
    cargar_datos_prueba(sistema)
    sistema.cambios_sin_guardar = False
    return sistema


def cadena_de_cursos() -> SistemaGestion:
    """Sistema con tres cursos encadenados: C1 <- C2 <- C3 (C3 requiere C2, C2 requiere C1)."""
    sistema = SistemaGestion()
    sistema.registrar_curso("C1", "Uno", 3)
    sistema.registrar_curso("C2", "Dos", 3, "C1")
    sistema.registrar_curso("C3", "Tres", 3, "C2")
    return sistema


# ==============================================================================
# 1. REGLAS DEL SISTEMA: MODIFICAR
# ==============================================================================
class PruebasModificar(unittest.TestCase):
    """Modificar estudiantes, profesores y cursos."""

    def test_corregir_nombre_de_estudiante(self):
        """El caso real: 'Maiquel' registrado por error debe poder pasar a 'Maikol'."""
        sistema = SistemaGestion()
        sistema.registrar_estudiante("E1", "Maiquel", "m@correo.com")
        sistema.modificar_estudiante("E1", nombre="Maikol")
        self.assertEqual(sistema.estudiantes["E1"].nombre, "Maikol")
        self.assertEqual(sistema.estudiantes["E1"].correo, "m@correo.com")  # no se tocó
        self.assertTrue(sistema.cambios_sin_guardar)

    def test_modificar_conserva_inscripciones_y_notas(self):
        sistema = sistema_prueba()
        antes = sistema.obtener_inscripcion("2024001", "MAT101").notas.copy()
        sistema.modificar_estudiante("2024001", nombre="Ana María García")
        self.assertEqual(sistema.obtener_inscripcion("2024001", "MAT101").notas, antes)

    def test_modificar_sin_cambios_no_marca_pendiente(self):
        sistema = SistemaGestion()
        sistema.registrar_estudiante("E1", "Ana", "ana@correo.com")
        sistema.cambios_sin_guardar = False
        sistema.modificar_estudiante("E1")
        sistema.modificar_estudiante("E1", nombre="Ana", correo="ana@correo.com")
        self.assertFalse(sistema.cambios_sin_guardar)

    def test_modificar_es_atomico(self):
        """Si un dato es inválido, NO se aplica ni siquiera el dato válido."""
        sistema = SistemaGestion()
        sistema.registrar_estudiante("E1", "Ana", "ana@correo.com")
        with self.assertRaises(ErrorGestion):
            sistema.modificar_estudiante("E1", nombre="Nuevo", correo="correo-malo")
        self.assertEqual(sistema.estudiantes["E1"].nombre, "Ana")

    def test_modificar_rechaza_vacios_e_inexistentes(self):
        sistema = SistemaGestion()
        sistema.registrar_estudiante("E1", "Ana", "ana@correo.com")
        for nombre in ("", "   ", None, 5):
            with self.assertRaises(ErrorGestion, msg=repr(nombre)):
                sistema.modificar_estudiante("E1", nombre=nombre)
        with self.assertRaises(ErrorGestion):
            sistema.modificar_estudiante("NOEXISTE", nombre="X")

    def test_registrar_estudiante_valida_correo(self):
        with self.assertRaises(ErrorGestion):
            SistemaGestion().registrar_estudiante("E1", "Ana", "sin-arroba")

    def test_modificar_profesor(self):
        sistema = sistema_prueba()
        sistema.modificar_profesor("P001", especialidad="Inteligencia Artificial")
        self.assertEqual(sistema.profesores["P001"].especialidad, "Inteligencia Artificial")
        self.assertEqual(sistema.profesores["P001"].nombre, "Dr. Carlos Méndez")
        with self.assertRaises(ErrorGestion):
            sistema.modificar_profesor("P001", nombre=" ")

    def test_modificar_curso_nombre_y_creditos(self):
        sistema = sistema_prueba()
        sistema.modificar_curso("MAT101", nombre="Cálculo I", creditos=6)
        self.assertEqual(sistema.cursos["MAT101"].nombre, "Cálculo I")
        self.assertEqual(sistema.cursos["MAT101"].creditos, 6)

    def test_modificar_curso_es_atomico(self):
        sistema = sistema_prueba()
        for creditos in (0, -1, "5", True, 2.5):
            with self.assertRaises(ErrorGestion, msg=repr(creditos)):
                sistema.modificar_curso("MAT101", nombre="NO DEBE APLICARSE", creditos=creditos)
        self.assertEqual(sistema.cursos["MAT101"].nombre, "Matemática I")

    def test_prerrequisito_no_puede_formar_ciclos(self):
        sistema = cadena_de_cursos()
        with self.assertRaises(ErrorGestion):
            sistema.modificar_curso("C1", prerrequisito="C2")   # ciclo directo
        with self.assertRaises(ErrorGestion):
            sistema.modificar_curso("C1", prerrequisito="C3")   # ciclo indirecto
        with self.assertRaises(ErrorGestion):
            sistema.modificar_curso("C2", prerrequisito="C2")   # de sí mismo
        with self.assertRaises(ErrorGestion):
            sistema.modificar_curso("C2", prerrequisito="NOEXISTE")
        self.assertIsNone(sistema.cursos["C1"].prerrequisito)

    def test_cambiar_y_quitar_prerrequisito(self):
        sistema = cadena_de_cursos()
        sistema.modificar_curso("C3", prerrequisito="C1")
        self.assertEqual(sistema.cursos["C3"].prerrequisito, "C1")
        sistema.modificar_curso("C3", prerrequisito=None)
        self.assertIsNone(sistema.cursos["C3"].prerrequisito)
        # SIN_CAMBIO conserva el valor
        sistema.modificar_curso("C2", nombre="Dos bis", prerrequisito=SIN_CAMBIO)
        self.assertEqual(sistema.cursos["C2"].prerrequisito, "C1")

    def test_cambiar_y_quitar_profesor_de_curso(self):
        sistema = sistema_prueba()
        sistema.modificar_curso("MAT101", id_profesor="P003")
        self.assertEqual(sistema.cursos["MAT101"].id_profesor, "P003")
        sistema.modificar_curso("MAT101", id_profesor=None)
        self.assertEqual(sistema.nombre_profesor_de_curso(sistema.cursos["MAT101"]), "Sin asignar")
        with self.assertRaises(ErrorGestion):
            sistema.modificar_curso("MAT101", id_profesor="NOEXISTE")

    def test_cursos_posibles_prerrequisito_excluye_ciclos(self):
        sistema = cadena_de_cursos()
        codigos = lambda curso: [c.codigo for c in sistema.cursos_posibles_prerrequisito(curso)]
        self.assertEqual(codigos("C1"), [])              # C2 y C3 dependen de C1
        self.assertEqual(codigos("C2"), ["C1"])          # C3 depende de C2
        self.assertEqual(codigos("C3"), ["C1", "C2"])


# ==============================================================================
# 1. REGLAS DEL SISTEMA: ELIMINAR
# ==============================================================================
class PruebasEliminar(unittest.TestCase):
    """Eliminar con borrado en cascada y protección de prerrequisitos."""

    def test_eliminar_estudiante_borra_sus_inscripciones(self):
        sistema = sistema_prueba()
        self.assertEqual(sistema.eliminar_estudiante("2024001"), 3)  # Ana: 3 cursos
        self.assertNotIn("2024001", sistema.estudiantes)
        self.assertEqual(len(sistema.inscripciones), 4)              # 7 - 3
        self.assertTrue(all(c != "2024001" for c, _ in sistema.inscripciones))
        self.assertTrue(sistema.cambios_sin_guardar)
        with self.assertRaises(ErrorGestion):
            sistema.eliminar_estudiante("2024001")                   # ya no existe

    def test_eliminar_profesor_deja_cursos_sin_asignar(self):
        sistema = sistema_prueba()
        self.assertEqual(sistema.eliminar_profesor("P002"), ["MAT101", "MAT201"])
        self.assertNotIn("P002", sistema.profesores)
        for codigo in ("MAT101", "MAT201"):
            self.assertIsNone(sistema.cursos[codigo].id_profesor)
        self.assertEqual(sistema.cursos["PRG101"].id_profesor, "P001")  # los demás intactos

    def test_curso_prerrequisito_de_otro_no_se_elimina(self):
        sistema = sistema_prueba()
        with self.assertRaises(ErrorGestion):
            sistema.eliminar_curso("MAT101")  # MAT201 lo exige
        self.assertIn("MAT101", sistema.cursos)
        self.assertEqual(len(sistema.inscripciones), 7)

    def test_eliminar_curso_borra_inscripciones_y_libera_su_prerrequisito(self):
        sistema = sistema_prueba()
        self.assertEqual(sistema.eliminar_curso("MAT201"), 1)        # inscripción de Ana
        self.assertNotIn("MAT201", sistema.cursos)
        # Ya nadie depende de MAT101, ahora sí se puede eliminar (Ana, Luis y María)
        self.assertEqual(sistema.eliminar_curso("MAT101"), 3)
        self.assertEqual(len(sistema.inscripciones), 3)

    def test_retirar_estudiante_y_volver_a_inscribirlo(self):
        sistema = sistema_prueba()
        retirada = sistema.retirar_estudiante("2024003", "MAT101")
        self.assertEqual(len(retirada.notas), 4)
        self.assertNotIn(("2024003", "MAT101"), sistema.inscripciones)
        nueva = sistema.inscribir("2024003", "MAT101")               # ya es posible de nuevo
        self.assertEqual(nueva.notas, {})
        with self.assertRaises(ErrorGestion):
            sistema.retirar_estudiante("2024004", "MAT101")          # nunca estuvo inscrito

    def test_eliminar_calificacion_recalcula_estado(self):
        sistema = sistema_prueba()
        inscripcion = sistema.obtener_inscripcion("2024001", "MAT101")
        self.assertEqual(inscripcion.estado(), "APRUEBA")
        sistema.eliminar_calificacion("2024001", "MAT101", "Examen Final")
        self.assertNotIn("Examen Final", inscripcion.notas)
        self.assertEqual(inscripcion.estado(), "EN CURSO")
        with self.assertRaises(ErrorGestion):
            sistema.eliminar_calificacion("2024001", "MAT101", "Examen Final")  # ya no tiene nota
        with self.assertRaises(ErrorGestion):
            sistema.eliminar_calificacion("2024001", "MAT101", "Inventada")

    def test_modificar_y_eliminar_se_guardan_y_cargan_consistentes(self):
        """Tras cascadas y ediciones, el archivo guardado pasa la validación completa de carga."""
        sistema = sistema_prueba()
        sistema.modificar_estudiante("2024002", nombre="Luis Alberto Pérez")
        sistema.eliminar_estudiante("2024001")
        sistema.eliminar_profesor("P003")
        sistema.eliminar_curso("BDD201")
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "datos.json")
            guardar_en_json(sistema, ruta)
            recargado = SistemaGestion()
            cargar_desde_json(recargado, ruta)  # lanza error si quedó algo huérfano
        self.assertEqual(recargado.a_diccionario(), sistema.a_diccionario())
        self.assertEqual(recargado.estudiantes["2024002"].nombre, "Luis Alberto Pérez")


# ==============================================================================
# 2. ENTRADA DE CONSOLA: CANCELAR Y SELECTORES
# ==============================================================================
class PruebasCancelarYSelectores(unittest.TestCase):
    """La palabra 'cancelar' y las listas numeradas."""

    def pedir(self, respuestas, **kwargs):
        with mock.patch("builtins.input", side_effect=respuestas):
            with contextlib.redirect_stdout(io.StringIO()):
                return input_validado("> ", **kwargs)

    def test_cancelar_funciona_en_cualquier_tipo_de_pregunta(self):
        for variante in ("cancelar", "CANCELAR", "  Cancelar  "):
            for tipo in (str, int, float):
                with self.assertRaises(OperacionCancelada, msg=f"{variante!r} {tipo}"):
                    self.pedir([variante], tipo=tipo)
        with self.assertRaises(OperacionCancelada):
            self.pedir(["cancelar"], permitir_vacio=True)

    def test_cancelar_se_puede_desactivar(self):
        # En el menú principal 'cancelar' es solo una entrada inválida más
        self.assertEqual(self.pedir(["cancelar", "3"], tipo=int, permitir_cancelar=False), 3)

    def test_cancelar_en_confirmaciones(self):
        with mock.patch("builtins.input", side_effect=["cancelar"]):
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(OperacionCancelada):
                    confirmar("¿Seguro? ")

    def test_pedir_id_nuevo_reintenta_si_ya_existe(self):
        with mock.patch("builtins.input", side_effect=["E1", "E1", "E2"]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(pedir_id_nuevo("ID: ", {"E1": 1}, "un estudiante"), "E2")

    def test_selector_devuelve_el_elemento_elegido(self):
        with mock.patch("builtins.input", side_effect=["x", "0", "9", "2"]):  # inválidos y luego 2
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(elegir_de_lista("Elija", ["a", "b", "c"], str), "b")

    def test_selector_con_opcion_ninguno(self):
        with mock.patch("builtins.input", side_effect=["0"]):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertIsNone(elegir_de_lista("Elija", ["a"], str, texto_ninguno="Ninguno"))

    def test_selector_cancelar_y_lista_vacia(self):
        with mock.patch("builtins.input", side_effect=["cancelar"]):
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(OperacionCancelada):
                    elegir_de_lista("Elija", ["a"], str)
        with self.assertRaises(ErrorGestion):
            elegir_de_lista("Elija", [], str)
        with self.assertRaises(ErrorGestion):
            elegir_estudiante(SistemaGestion())  # no hay estudiantes registrados

    def test_menu_numerado_sin_huecos(self):
        acciones = menu.construir_acciones()
        self.assertEqual(sorted(acciones), list(range(1, len(acciones) + 1)))
        self.assertTrue(all(callable(f) for f in acciones.values()))


# ==============================================================================
# 3. FLUJOS COMPLETOS DE LAS OPCIONES DEL MENÚ
# ==============================================================================
class PruebasFlujos(unittest.TestCase):
    """Simulan lo que el usuario escribe en cada opción del menú."""

    def ejecutar(self, opcion, sistema, respuestas, esperar=None):
        """Ejecuta una opción con las respuestas indicadas y devuelve lo que imprimió.

        Verifica además que el flujo consumió EXACTAMENTE esas respuestas (ni
        más ni menos), para detectar preguntas inesperadas.
        Si `esperar` es una excepción, comprueba que se lance.
        """
        salida = io.StringIO()
        with mock.patch("builtins.input", side_effect=list(respuestas)) as entrada:
            with contextlib.redirect_stdout(salida):
                if esperar is None:
                    opcion(sistema)
                else:
                    with self.assertRaises(esperar):
                        opcion(sistema)
        self.assertEqual(entrada.call_count, len(respuestas), "No se usaron todas las respuestas")
        return salida.getvalue()

    # ------------------------------ estudiantes ------------------------------
    def test_registrar_estudiante(self):
        sistema = SistemaGestion()
        self.ejecutar(opcion_registrar_estudiante, sistema, ["E1", "Pedro Ruiz", "pedro@correo.com"])
        self.assertEqual(sistema.estudiantes["E1"].nombre, "Pedro Ruiz")

    def test_cancelar_a_mitad_de_un_registro_no_deja_nada(self):
        sistema = SistemaGestion()
        self.ejecutar(opcion_registrar_estudiante, sistema, ["E1", "Pedro Ruiz", "cancelar"],
                      esperar=OperacionCancelada)
        self.assertEqual(sistema.estudiantes, {})
        self.assertFalse(sistema.cambios_sin_guardar)

    def test_registrar_estudiante_reintenta_carne_repetido_y_correo_malo(self):
        sistema = sistema_prueba()
        salida = self.ejecutar(
            opcion_registrar_estudiante, sistema,
            ["2024001", "2024099", "Pedro", "malo", "pedro@correo.com"],
        )
        self.assertIn("ya existe un estudiante", salida)
        self.assertIn("formato de correo inválido", salida)
        self.assertEqual(sistema.estudiantes["2024099"].correo, "pedro@correo.com")

    def test_modificar_estudiante_maiquel_a_maikol(self):
        sistema = SistemaGestion()
        sistema.registrar_estudiante("E1", "Maiquel", "m@correo.com")
        salida = self.ejecutar(opcion_modificar_estudiante, sistema, ["1", "Maikol", ""])
        self.assertEqual(sistema.estudiantes["E1"].nombre, "Maikol")
        self.assertEqual(sistema.estudiantes["E1"].correo, "m@correo.com")
        self.assertIn("Maiquel  ->  Maikol", salida)

    def test_modificar_estudiante_sin_cambios_y_cancelado(self):
        sistema = SistemaGestion()
        sistema.registrar_estudiante("E1", "Maiquel", "m@correo.com")
        salida = self.ejecutar(opcion_modificar_estudiante, sistema, ["1", "", ""])
        self.assertIn("No se realizaron cambios", salida)
        # Cancelar después de escribir un dato nuevo: no se aplica nada
        self.ejecutar(opcion_modificar_estudiante, sistema, ["1", "Maikol", "cancelar"],
                      esperar=OperacionCancelada)
        self.assertEqual(sistema.estudiantes["E1"].nombre, "Maiquel")

    def test_eliminar_estudiante_con_confirmacion(self):
        sistema = sistema_prueba()
        salida = self.ejecutar(opcion_eliminar_estudiante, sistema, ["1", "n"])  # Ana, dice que no
        self.assertIn("3 inscripción", salida)
        self.assertIn("2024001", sistema.estudiantes)
        self.ejecutar(opcion_eliminar_estudiante, sistema, ["1", "s"])
        self.assertNotIn("2024001", sistema.estudiantes)
        self.ejecutar(opcion_eliminar_estudiante, sistema, ["1", "cancelar"],
                      esperar=OperacionCancelada)
        self.assertEqual(len(sistema.estudiantes), 3)

    def test_listas_sin_registros_avisan(self):
        with self.assertRaises(ErrorGestion):
            self.ejecutar(opcion_modificar_estudiante, SistemaGestion(), [])

    # ------------------------------ profesores ------------------------------
    def test_modificar_y_eliminar_profesor(self):
        sistema = sistema_prueba()
        self.ejecutar(opcion_modificar_profesor, sistema, ["1", "Dr. Carlos A. Méndez", ""])
        self.assertEqual(sistema.profesores["P001"].nombre, "Dr. Carlos A. Méndez")
        salida = self.ejecutar(opcion_eliminar_profesor, sistema, ["2", "s"])  # P002 (2 cursos)
        self.assertIn("Sin asignar", salida)
        self.assertNotIn("P002", sistema.profesores)
        self.assertIsNone(sistema.cursos["MAT101"].id_profesor)

    # -------------------------------- cursos --------------------------------
    def test_registrar_curso_eligiendo_prerrequisito_de_la_lista(self):
        sistema = sistema_prueba()
        self.ejecutar(opcion_registrar_curso, sistema, ["MAT301", "Matemática III", "5", "3"])
        self.assertEqual(sistema.cursos["MAT301"].prerrequisito, "MAT201")  # opción 3 = MAT201
        self.ejecutar(opcion_registrar_curso, sistema, ["EXT100", "Extra", "3", "0"])
        self.assertIsNone(sistema.cursos["EXT100"].prerrequisito)           # opción 0 = ninguno

    def test_registrar_primer_curso_no_pregunta_prerrequisito(self):
        sistema = SistemaGestion()
        self.ejecutar(opcion_registrar_curso, sistema, ["C1", "Uno", "4"])
        self.assertIn("C1", sistema.cursos)

    def test_modificar_curso_quitar_prerrequisito_y_cambiar_creditos(self):
        sistema = sistema_prueba()
        # Curso 3 = MAT201; sin cambiar nombre; créditos 7; cambiar prerrequisito -> 0 (ninguno);
        # no cambiar profesor
        self.ejecutar(opcion_modificar_curso, sistema, ["3", "", "7", "s", "0", "n"])
        self.assertEqual(sistema.cursos["MAT201"].creditos, 7)
        self.assertIsNone(sistema.cursos["MAT201"].prerrequisito)

    def test_modificar_curso_no_ofrece_prerrequisitos_que_formen_ciclo(self):
        sistema = sistema_prueba()
        # Curso 1 = MAT101 (MAT201 depende de él): cancelamos al ver la lista
        salida = self.ejecutar(opcion_modificar_curso, sistema, ["1", "", "", "s", "cancelar"],
                               esperar=OperacionCancelada)
        lista = salida.split("Seleccione el nuevo prerrequisito")[1]
        self.assertNotIn("MAT201", lista)   # formaría un ciclo
        self.assertNotIn("[MAT101]", lista)  # ni él mismo
        self.assertIn("PRG101", lista)

    def test_modificar_curso_cambiando_profesor(self):
        sistema = sistema_prueba()
        # Curso 5 = BDD201 (P003); cambiar profesor -> opción 1 = P001
        self.ejecutar(opcion_modificar_curso, sistema, ["5", "", "", "n", "s", "1"])
        self.assertEqual(sistema.cursos["BDD201"].id_profesor, "P001")

    def test_eliminar_curso_bloqueado_por_prerrequisito(self):
        sistema = sistema_prueba()
        salida = self.ejecutar(opcion_eliminar_curso, sistema, ["1"])  # MAT101
        self.assertIn("No se puede eliminar", salida)
        self.assertIn("MAT201", salida)
        self.assertIn("MAT101", sistema.cursos)

    def test_eliminar_curso_permitido(self):
        sistema = sistema_prueba()
        self.ejecutar(opcion_eliminar_curso, sistema, ["4", "s"])  # PRG201, sin dependientes
        self.assertNotIn("PRG201", sistema.cursos)

    def test_asignar_profesor_eligiendo_de_listas(self):
        sistema = sistema_prueba()
        self.ejecutar(opcion_asignar_profesor, sistema, ["5", "1"])  # BDD201 -> P001
        self.assertEqual(sistema.cursos["BDD201"].id_profesor, "P001")

    # --------------------------- inscripciones y notas ---------------------------
    def test_inscribir_eligiendo_de_listas(self):
        sistema = sistema_prueba()
        self.ejecutar(opcion_inscribir, sistema, ["1", "4"])  # Ana -> PRG201 (aprobó PRG101)
        self.assertIn(("2024001", "PRG201"), sistema.inscripciones)

    def test_inscribir_marca_y_rechaza_duplicado_y_prerrequisito(self):
        sistema = sistema_prueba()
        salida = self.ejecutar(opcion_inscribir, sistema, ["1", "1"], esperar=ErrorGestion)  # duplicado
        self.assertIn("YA INSCRITO", salida)
        salida = self.ejecutar(opcion_inscribir, sistema, ["2", "3"], esperar=ErrorGestion)  # Luis, MAT201
        self.assertIn("requiere aprobar MAT101", salida)
        self.assertEqual(len(sistema.inscripciones), 7)

    def test_retirar_estudiante(self):
        sistema = sistema_prueba()
        # Ana (1) -> su 3.er curso = MAT201 -> confirmar
        self.ejecutar(opcion_retirar_estudiante, sistema, ["1", "3", "s"])
        self.assertNotIn(("2024001", "MAT201"), sistema.inscripciones)
        # Responder 'n' no borra
        self.ejecutar(opcion_retirar_estudiante, sistema, ["1", "1", "n"])
        self.assertIn(("2024001", "MAT101"), sistema.inscripciones)

    def test_registrar_nota_solo_lista_cursos_del_estudiante(self):
        sistema = sistema_prueba()
        # José (4) solo tiene BDD201: curso 1 de SU lista; evaluación 1; nota con coma decimal
        salida = self.ejecutar(opcion_registrar_calificacion, sistema, ["4", "1", "1", "88,5"])
        self.assertEqual(sistema.obtener_inscripcion("2024004", "BDD201").notas["Parcial 1"], 88.5)
        self.assertNotIn("MAT101", salida.split("Evaluaciones de")[0])  # no aparecen cursos ajenos

    def test_registrar_nota_reintenta_valores_invalidos(self):
        sistema = sistema_prueba()
        salida = self.ejecutar(
            opcion_registrar_calificacion, sistema, ["4", "1", "1", "abc", "150", "-3", "70"]
        )
        self.assertEqual(sistema.obtener_inscripcion("2024004", "BDD201").notas["Parcial 1"], 70.0)
        self.assertIn("número decimal válido", salida)
        self.assertIn("mayor que 100", salida)
        self.assertIn("menor que 0", salida)

    def test_estudiante_sin_cursos_no_puede_calificar(self):
        sistema = sistema_prueba()
        sistema.registrar_estudiante("2024005", "Nuevo", "nuevo@correo.com")
        with self.assertRaises(ErrorGestion):
            self.ejecutar(opcion_registrar_calificacion, sistema, ["5"])

    def test_eliminar_calificacion(self):
        sistema = sistema_prueba()
        # Ana (1), MAT101 (1), 4.ª nota = Examen Final, confirmar
        salida = self.ejecutar(opcion_eliminar_calificacion, sistema, ["1", "1", "4", "s"])
        self.assertNotIn("Examen Final", sistema.obtener_inscripcion("2024001", "MAT101").notas)
        self.assertIn("EN CURSO", salida)

    def test_eliminar_calificacion_sin_notas(self):
        sistema = sistema_prueba()
        with self.assertRaises(ErrorGestion):
            self.ejecutar(opcion_eliminar_calificacion, sistema, ["4", "1"])  # José no tiene notas

    # --------------------------------- reportes ---------------------------------
    def test_historial_eligiendo_estudiante(self):
        sistema = sistema_prueba()
        salida = self.ejecutar(opcion_historial, sistema, ["1"])
        self.assertIn("ESTADO: APRUEBA", salida)
        self.assertIn("Ana García", salida)


if __name__ == "__main__":
    unittest.main(verbosity=2)
