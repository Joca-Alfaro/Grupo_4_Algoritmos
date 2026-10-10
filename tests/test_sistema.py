# -*- coding: utf-8 -*-
"""
tests/test_sistema.py
=====================
Pruebas automatizadas del sistema (solo librería estándar: unittest).

Ejecución desde la carpeta raíz del proyecto:
    python -m unittest discover -v

Cubren las reglas críticas: duplicados, prerrequisitos, rango de notas,
cálculo de promedio/estado, entrada validada y guardado/carga en JSON
(incluyendo archivos dañados o inconsistentes).
"""

import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

from excepciones import ErrorGestion, ErrorPersistencia
from servicios.datos_prueba import cargar_datos_prueba
from servicios.persistencia import cargar_desde_json, guardar_en_json, resolver_ruta
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import input_validado


def sistema_base() -> SistemaGestion:
    """Crea un sistema con 1 estudiante, 1 profesor y 2 cursos con prerrequisito."""
    sistema = SistemaGestion()
    sistema.registrar_estudiante("E1", "Ana", "ana@correo.com")
    sistema.registrar_profesor("P1", "Dr. Pérez", "Software")
    sistema.registrar_curso("C1", "Curso Uno", 5)
    sistema.registrar_curso("C2", "Curso Dos", 5, "C1")
    sistema.asignar_profesor("C1", "P1")
    return sistema


def poner_notas(sistema: SistemaGestion, carne: str, curso: str, nota: float) -> None:
    """Registra la misma nota en las 4 evaluaciones de un curso."""
    for evaluacion in ("Parcial 1", "Parcial 2", "Proyecto", "Examen Final"):
        sistema.registrar_calificacion(carne, curso, evaluacion, nota)


# ==============================================================================
class PruebasReglasDeNegocio(unittest.TestCase):
    """Reglas académicas: unicidad, inscripciones, prerrequisitos y notas."""

    def setUp(self):
        self.sistema = sistema_base()

    def test_carne_duplicado(self):
        with self.assertRaises(ErrorGestion):
            self.sistema.registrar_estudiante("E1", "Otro", "otro@correo.com")

    def test_inscripcion_duplicada_es_rechazada(self):
        self.sistema.inscribir("E1", "C1")
        with self.assertRaises(ErrorGestion):
            self.sistema.inscribir("E1", "C1")
        self.assertEqual(len(self.sistema.inscripciones), 1)

    def test_prerrequisito_sin_aprobar_bloquea(self):
        with self.assertRaises(ErrorGestion):
            self.sistema.inscribir("E1", "C2")

    def test_prerrequisito_reprobado_bloquea(self):
        self.sistema.inscribir("E1", "C1")
        poner_notas(self.sistema, "E1", "C1", 50)
        with self.assertRaises(ErrorGestion):
            self.sistema.inscribir("E1", "C2")

    def test_prerrequisito_aprobado_permite(self):
        self.sistema.inscribir("E1", "C1")
        poner_notas(self.sistema, "E1", "C1", 80)
        self.sistema.inscribir("E1", "C2")  # no debe lanzar error

    def test_notas_fuera_de_rango(self):
        self.sistema.inscribir("E1", "C1")
        for invalida in (-1, 100.01, float("nan"), float("inf"), "abc", True):
            with self.assertRaises(ErrorGestion, msg=f"Debió rechazar {invalida!r}"):
                self.sistema.registrar_calificacion("E1", "C1", "Parcial 1", invalida)
        self.assertEqual(self.sistema.obtener_inscripcion("E1", "C1").notas, {})

    def test_notas_limite_son_validas(self):
        self.sistema.inscribir("E1", "C1")
        self.sistema.registrar_calificacion("E1", "C1", "Parcial 1", 0)
        self.sistema.registrar_calificacion("E1", "C1", "Parcial 2", 100)

    def test_evaluacion_inexistente(self):
        self.sistema.inscribir("E1", "C1")
        with self.assertRaises(ErrorGestion):
            self.sistema.registrar_calificacion("E1", "C1", "Tarea Extra", 90)

    def test_modificar_nota_sobrescribe(self):
        self.sistema.inscribir("E1", "C1")
        self.assertFalse(self.sistema.registrar_calificacion("E1", "C1", "Parcial 1", 50))
        self.assertTrue(self.sistema.registrar_calificacion("E1", "C1", "Parcial 1", 90))
        self.assertEqual(self.sistema.obtener_inscripcion("E1", "C1").notas["Parcial 1"], 90.0)

    def test_calificar_sin_inscripcion(self):
        with self.assertRaises(ErrorGestion):
            self.sistema.registrar_calificacion("E1", "C1", "Parcial 1", 90)

    def test_promedio_ponderado(self):
        self.sistema.inscribir("E1", "C1")
        # 100*20% + 100*20% + 100*20% + 0*40% = 60 -> reprueba
        for evaluacion in ("Parcial 1", "Parcial 2", "Proyecto"):
            self.sistema.registrar_calificacion("E1", "C1", evaluacion, 100)
        self.sistema.registrar_calificacion("E1", "C1", "Examen Final", 0)
        insc = self.sistema.obtener_inscripcion("E1", "C1")
        self.assertAlmostEqual(insc.promedio(), 60.0)
        self.assertEqual(insc.estado(), "REPRUEBA")

    def test_estados_academicos(self):
        self.sistema.inscribir("E1", "C1")
        insc = self.sistema.obtener_inscripcion("E1", "C1")
        self.assertEqual(insc.estado(), "SIN NOTAS")
        self.sistema.registrar_calificacion("E1", "C1", "Parcial 1", 100)
        self.assertEqual(insc.estado(), "EN CURSO")
        poner_notas(self.sistema, "E1", "C1", 61)
        self.assertEqual(insc.estado(), "APRUEBA")  # 61 exacto aprueba
        poner_notas(self.sistema, "E1", "C1", 60.99)
        self.assertEqual(insc.estado(), "REPRUEBA")

    def test_prerrequisito_inexistente_o_propio(self):
        with self.assertRaises(ErrorGestion):
            self.sistema.registrar_curso("C3", "Tres", 4, "NOEXISTE")
        with self.assertRaises(ErrorGestion):
            self.sistema.registrar_curso("C4", "Cuatro", 4, "C4")

    def test_datos_de_prueba_no_se_duplican(self):
        sistema = SistemaGestion()
        self.assertGreater(cargar_datos_prueba(sistema), 0)
        self.assertEqual(cargar_datos_prueba(sistema), 0)  # segunda vez: nada nuevo
        # Luis reprobó MAT101 y no puede cursar MAT201
        with self.assertRaises(ErrorGestion):
            sistema.inscribir("2024002", "MAT201")
        # Ana aprobó PRG101 y sí puede cursar PRG201
        sistema.inscribir("2024001", "PRG201")


# ==============================================================================
class PruebasEntradaValidada(unittest.TestCase):
    """La función input_validado debe reintentar hasta recibir un dato válido."""

    def ejecutar(self, respuestas, **kwargs):
        """Simula las respuestas del usuario y descarta lo impreso."""
        with mock.patch("builtins.input", side_effect=respuestas):
            with contextlib.redirect_stdout(io.StringIO()):
                return input_validado("> ", **kwargs)

    def test_reintenta_hasta_valor_valido(self):
        # letras, vacío, nan, fuera de rango y finalmente un valor correcto
        valor = self.ejecutar(["abc", "", "nan", "150", "-5", "85,5"],
                              tipo=float, minimo=0, maximo=100)
        self.assertEqual(valor, 85.5)

    def test_entero(self):
        self.assertEqual(self.ejecutar(["x", "3.5", "7"], tipo=int, minimo=1, maximo=10), 7)

    def test_texto_vacio_y_opcional(self):
        self.assertEqual(self.ejecutar(["", "hola"]), "hola")
        self.assertIsNone(self.ejecutar([""], permitir_vacio=True))


# ==============================================================================
class PruebasPersistenciaJSON(unittest.TestCase):
    """Guardado y carga en JSON, incluyendo archivos dañados."""

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)
        self.ruta = os.path.join(self.carpeta.name, "datos.json")

    def escribir(self, contenido: str) -> None:
        """Escribe texto crudo en el archivo de prueba."""
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)

    def test_guardar_y_cargar_conserva_todo(self):
        origen = SistemaGestion()
        cargar_datos_prueba(origen)
        guardar_en_json(origen, self.ruta)
        self.assertFalse(origen.cambios_sin_guardar)

        destino = SistemaGestion()
        cargar_desde_json(destino, self.ruta)
        self.assertEqual(destino.a_diccionario(), origen.a_diccionario())
        self.assertEqual(destino.resumen(), origen.resumen())
        # Las reglas siguen funcionando con los datos cargados
        with self.assertRaises(ErrorGestion):
            destino.inscribir("2024001", "MAT101")  # duplicado
        with self.assertRaises(ErrorGestion):
            destino.inscribir("2024002", "MAT201")  # prerrequisito reprobado

    def test_archivo_json_es_legible_y_con_tildes(self):
        sistema = SistemaGestion()
        sistema.registrar_estudiante("E1", "José Ñandú", "jose@correo.com")
        guardar_en_json(sistema, self.ruta)
        with open(self.ruta, encoding="utf-8") as archivo:
            texto = archivo.read()
        self.assertIn("José Ñandú", texto)  # no se escapa como é
        datos = json.loads(texto)
        self.assertEqual(datos["version_formato"], 1)
        self.assertIn("fecha_guardado", datos)

    def test_guardado_no_deja_temporales(self):
        guardar_en_json(SistemaGestion(), self.ruta)
        self.assertEqual(os.listdir(self.carpeta.name), ["datos.json"])

    def test_guardar_crea_carpeta_inexistente(self):
        ruta = os.path.join(self.carpeta.name, "nueva", "sub", "datos.json")
        guardar_en_json(SistemaGestion(), ruta)
        self.assertTrue(os.path.isfile(ruta))

    def test_archivo_inexistente(self):
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), os.path.join(self.carpeta.name, "no_existe.json"))

    def test_json_malformado_no_altera_datos_actuales(self):
        sistema = sistema_base()
        antes = sistema.a_diccionario()
        self.escribir('{"estudiantes": [ {"carne": ')  # JSON truncado
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(sistema, self.ruta)
        self.assertEqual(sistema.a_diccionario(), antes)

    def test_estructura_invalida(self):
        for contenido in ('[]', '"texto"', '{"estudiantes": "no es lista"}',
                          '{"estudiantes": [{"carne": "E1"}]}',            # faltan campos
                          '{"estudiantes": [{"carne": 5, "nombre": "A", "correo": "a@b.c"}]}'):
            self.escribir(contenido)
            with self.assertRaises(ErrorPersistencia, msg=contenido):
                cargar_desde_json(SistemaGestion(), self.ruta)

    def test_version_futura_no_soportada(self):
        self.escribir('{"version_formato": 99}')
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), self.ruta)

    def test_ids_duplicados_en_archivo(self):
        est = {"carne": "E1", "nombre": "A", "correo": "a@b.co"}
        self.escribir(json.dumps({"estudiantes": [est, est]}))
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), self.ruta)

    def test_inscripcion_a_estudiante_inexistente(self):
        self.escribir(json.dumps({
            "cursos": [{"codigo": "C1", "nombre": "Uno", "creditos": 3}],
            "inscripciones": [{"carne": "FANTASMA", "codigo_curso": "C1", "notas": {}}],
        }))
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), self.ruta)

    def test_nota_fuera_de_rango_en_archivo(self):
        self.escribir(json.dumps({
            "estudiantes": [{"carne": "E1", "nombre": "A", "correo": "a@b.co"}],
            "cursos": [{"codigo": "C1", "nombre": "Uno", "creditos": 3}],
            "inscripciones": [{"carne": "E1", "codigo_curso": "C1", "notas": {"Parcial 1": 500}}],
        }))
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), self.ruta)

    def test_ciclo_de_prerrequisitos(self):
        self.escribir(json.dumps({"cursos": [
            {"codigo": "A", "nombre": "A", "creditos": 3, "prerrequisito": "B"},
            {"codigo": "B", "nombre": "B", "creditos": 3, "prerrequisito": "A"},
        ]}))
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), self.ruta)

    def test_profesor_y_prerrequisito_inexistentes(self):
        self.escribir(json.dumps({"cursos": [
            {"codigo": "A", "nombre": "A", "creditos": 3, "id_profesor": "NADIE"}]}))
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), self.ruta)
        self.escribir(json.dumps({"cursos": [
            {"codigo": "A", "nombre": "A", "creditos": 3, "prerrequisito": "NADA"}]}))
        with self.assertRaises(ErrorPersistencia):
            cargar_desde_json(SistemaGestion(), self.ruta)

    def test_cargar_reemplaza_datos_actuales(self):
        guardar_en_json(sistema_base(), self.ruta)
        otro = SistemaGestion()
        otro.registrar_estudiante("X9", "Temporal", "t@correo.com")
        cargar_desde_json(otro, self.ruta)
        self.assertNotIn("X9", otro.estudiantes)
        self.assertIn("E1", otro.estudiantes)
        self.assertFalse(otro.cambios_sin_guardar)

    def test_bandera_cambios_sin_guardar(self):
        sistema = SistemaGestion()
        self.assertFalse(sistema.cambios_sin_guardar)
        sistema.registrar_estudiante("E1", "Ana", "ana@correo.com")
        self.assertTrue(sistema.cambios_sin_guardar)
        guardar_en_json(sistema, self.ruta)
        self.assertFalse(sistema.cambios_sin_guardar)

    def test_resolver_ruta(self):
        self.assertTrue(resolver_ruta("").endswith(os.path.join("datos", "academico.json")))
        self.assertTrue(resolver_ruta("semestre1").endswith(os.path.join("datos", "semestre1.json")))
        self.assertTrue(resolver_ruta('"semestre1.JSON"').endswith("semestre1.JSON"))
        absoluta = os.path.join(self.carpeta.name, "otro")
        self.assertEqual(resolver_ruta(absoluta), absoluta + ".json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
