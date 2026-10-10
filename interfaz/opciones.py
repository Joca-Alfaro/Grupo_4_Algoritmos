# -*- coding: utf-8 -*-
"""
interfaz/opciones.py
====================
Una función por cada opción del menú.

Cada función recibe el `SistemaGestion`, pide los datos al usuario con
`input_validado`, llama a la lógica del sistema y muestra el resultado.
Los ErrorGestion que lancen los servicios NO se capturan aquí: suben hasta el
bucle principal (main.py), que los muestra como mensajes amigables.
"""

import os
from typing import Optional

from config import (
    EVALUACIONES,
    NOTA_MAXIMA,
    NOTA_MINIMA,
    RUTA_DATOS_POR_DEFECTO,
)
from excepciones import ErrorGestion
from servicios.datos_prueba import cargar_datos_prueba
from servicios.persistencia import cargar_desde_json, guardar_en_json, resolver_ruta
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import confirmar, input_validado, pedir_id
from utilidades.validadores import es_correo_valido


# ==============================================================================
# FUNCIONES DE APOYO PARA MOSTRAR INFORMACIÓN
# ==============================================================================
def formato_nota(valor: Optional[float]) -> str:
    """Devuelve la nota con 2 decimales, o un guion si todavía no existe."""
    return f"{valor:.2f}" if valor is not None else "  -  "


def imprimir_resumen_datos(sistema: SistemaGestion) -> None:
    """Muestra cuántos registros de cada tipo hay actualmente en el sistema."""
    resumen = sistema.resumen()
    print("  Datos actuales en el sistema:")
    print(f"     - Estudiantes  : {resumen['estudiantes']}")
    print(f"     - Profesores   : {resumen['profesores']}")
    print(f"     - Cursos       : {resumen['cursos']}")
    print(f"     - Inscripciones: {resumen['inscripciones']}")


# ==============================================================================
# ESTUDIANTES
# ==============================================================================
def opcion_registrar_estudiante(sistema: SistemaGestion) -> None:
    """Pide los datos y registra un estudiante nuevo."""
    print("\n--- REGISTRAR ESTUDIANTE ---")
    carne = pedir_id("Carné (único, sin espacios): ")
    # Se verifica antes de pedir el resto de datos para no hacer perder tiempo
    if carne in sistema.estudiantes:
        raise ErrorGestion(f"Ya existe un estudiante con el carné '{carne}'.")
    nombre = input_validado("Nombre completo: ")
    correo = input_validado(
        "Correo electrónico: ",
        validador=es_correo_valido,
        mensaje_validador="formato de correo inválido (ejemplo: nombre@dominio.com).",
    )
    estudiante = sistema.registrar_estudiante(carne, nombre, correo)
    print(f"\n  [OK] Estudiante registrado: {estudiante}")


def opcion_listar_estudiantes(sistema: SistemaGestion) -> None:
    """Muestra todos los estudiantes registrados."""
    print("\n--- LISTA DE ESTUDIANTES ---")
    if not sistema.estudiantes:
        print("  (No hay estudiantes registrados)")
        return
    for estudiante in sistema.estudiantes.values():
        print("  " + str(estudiante))
    print(f"\n  Total: {len(sistema.estudiantes)}")


# ==============================================================================
# PROFESORES
# ==============================================================================
def opcion_registrar_profesor(sistema: SistemaGestion) -> None:
    """Pide los datos y registra un profesor nuevo."""
    print("\n--- REGISTRAR PROFESOR ---")
    id_profesor = pedir_id("ID del profesor (único, sin espacios): ")
    if id_profesor in sistema.profesores:
        raise ErrorGestion(f"Ya existe un profesor con el ID '{id_profesor}'.")
    nombre = input_validado("Nombre completo: ")
    especialidad = input_validado("Especialidad: ")
    profesor = sistema.registrar_profesor(id_profesor, nombre, especialidad)
    print(f"\n  [OK] Profesor registrado: {profesor}")


def opcion_listar_profesores(sistema: SistemaGestion) -> None:
    """Muestra todos los profesores registrados."""
    print("\n--- LISTA DE PROFESORES ---")
    if not sistema.profesores:
        print("  (No hay profesores registrados)")
        return
    for profesor in sistema.profesores.values():
        print("  " + str(profesor))
    print(f"\n  Total: {len(sistema.profesores)}")


# ==============================================================================
# CURSOS
# ==============================================================================
def opcion_registrar_curso(sistema: SistemaGestion) -> None:
    """Pide los datos y registra un curso (con prerrequisito opcional)."""
    print("\n--- REGISTRAR CURSO ---")
    codigo = pedir_id("Código del curso (único, sin espacios): ")
    if codigo in sistema.cursos:
        raise ErrorGestion(f"Ya existe un curso con el código '{codigo}'.")
    nombre = input_validado("Nombre del curso: ")
    creditos = input_validado("Créditos (1 a 20): ", int, minimo=1, maximo=20)

    # Se muestran los cursos existentes para facilitar elegir el prerrequisito
    if sistema.cursos:
        print("  Cursos disponibles como prerrequisito:", ", ".join(sistema.cursos.keys()))
    prerrequisito = input_validado(
        "Código del prerrequisito (ENTER si no tiene): ", str, permitir_vacio=True
    )

    curso = sistema.registrar_curso(codigo, nombre, creditos, prerrequisito)
    print(f"\n  [OK] Curso registrado: {curso}")
    if prerrequisito:
        print(f"       Prerrequisito: {prerrequisito}")


def opcion_listar_cursos(sistema: SistemaGestion) -> None:
    """Muestra todos los cursos con su profesor y prerrequisito."""
    print("\n--- LISTA DE CURSOS ---")
    if not sistema.cursos:
        print("  (No hay cursos registrados)")
        return
    for curso in sistema.cursos.values():
        profesor = sistema.nombre_profesor_de_curso(curso)
        prerrequisito = curso.prerrequisito if curso.prerrequisito else "Ninguno"
        print(f"  {curso}")
        print(f"      Profesor: {profesor} | Prerrequisito: {prerrequisito}")
    print(f"\n  Total: {len(sistema.cursos)}")


def opcion_asignar_profesor(sistema: SistemaGestion) -> None:
    """Asigna un profesor responsable a un curso."""
    print("\n--- ASIGNAR PROFESOR A CURSO ---")
    if not sistema.cursos or not sistema.profesores:
        raise ErrorGestion("Debe haber al menos un curso y un profesor registrados.")
    codigo = pedir_id("Código del curso: ")
    sistema.obtener_curso(codigo)  # valida antes de pedir el siguiente dato
    id_profesor = pedir_id("ID del profesor: ")
    sistema.asignar_profesor(codigo, id_profesor)
    print(
        f"\n  [OK] Profesor '{sistema.profesores[id_profesor].nombre}' asignado "
        f"al curso '{sistema.cursos[codigo].nombre}'."
    )


# ==============================================================================
# INSCRIPCIONES Y CALIFICACIONES
# ==============================================================================
def opcion_inscribir(sistema: SistemaGestion) -> None:
    """Inscribe un estudiante en un curso."""
    print("\n--- INSCRIBIR ESTUDIANTE EN CURSO ---")
    if not sistema.estudiantes or not sistema.cursos:
        raise ErrorGestion("Debe haber al menos un estudiante y un curso registrados.")
    carne = pedir_id("Carné del estudiante: ")
    estudiante = sistema.obtener_estudiante(carne)
    codigo = pedir_id("Código del curso: ")
    curso = sistema.obtener_curso(codigo)
    sistema.inscribir(carne, codigo)  # aplica duplicados y prerrequisitos
    print(f"\n  [OK] Inscripción registrada: {estudiante.nombre} en {curso.nombre} ({curso.codigo}).")


def opcion_registrar_calificacion(sistema: SistemaGestion) -> None:
    """Registra o modifica la nota de una evaluación."""
    print("\n--- REGISTRAR / MODIFICAR CALIFICACIÓN ---")
    carne = pedir_id("Carné del estudiante: ")
    sistema.obtener_estudiante(carne)
    codigo = pedir_id("Código del curso: ")
    inscripcion = sistema.obtener_inscripcion(carne, codigo)

    # Menú de evaluaciones, mostrando la nota actual si ya existe
    print("\n  Evaluaciones disponibles:")
    nombres = list(EVALUACIONES.keys())
    for numero, evaluacion in enumerate(nombres, start=1):
        actual = inscripcion.notas.get(evaluacion)
        texto_nota = f"nota actual: {actual:.2f}" if actual is not None else "sin nota"
        print(f"    {numero}. {evaluacion} ({EVALUACIONES[evaluacion]:g}%) - {texto_nota}")

    indice = input_validado(
        f"\nSeleccione la evaluación (1-{len(nombres)}): ", int, minimo=1, maximo=len(nombres)
    )
    evaluacion = nombres[indice - 1]
    nota = input_validado(
        f"Nota para '{evaluacion}' ({NOTA_MINIMA:g} a {NOTA_MAXIMA:g}): ",
        float,
        minimo=NOTA_MINIMA,
        maximo=NOTA_MAXIMA,
    )

    fue_modificacion = sistema.registrar_calificacion(carne, codigo, evaluacion, nota)
    accion = "modificada" if fue_modificacion else "registrada"
    print(f"\n  [OK] Nota {accion}: {evaluacion} = {nota:.2f}")
    print(
        f"       Promedio actual: {formato_nota(inscripcion.promedio())} | "
        f"Estado: {inscripcion.estado()}"
    )


# ==============================================================================
# REPORTES
# ==============================================================================
def opcion_cursos_de_estudiante(sistema: SistemaGestion) -> None:
    """Reporte: cursos en los que está inscrito un estudiante."""
    print("\n--- CURSOS INSCRITOS DE UN ESTUDIANTE ---")
    carne = pedir_id("Carné del estudiante: ")
    estudiante = sistema.obtener_estudiante(carne)
    inscripciones = sistema.cursos_de_estudiante(carne)

    print(f"\n  Estudiante: {estudiante}")
    if not inscripciones:
        print("  (No tiene cursos inscritos)")
        return

    print("\n  " + "-" * 66)
    print(f"  {'Código':<10}{'Curso':<26}{'Créd.':<7}{'Profesor':<23}")
    print("  " + "-" * 66)
    for inscripcion in inscripciones:
        curso = sistema.cursos[inscripcion.codigo_curso]
        profesor = sistema.nombre_profesor_de_curso(curso)
        print(f"  {curso.codigo:<10}{curso.nombre[:24]:<26}{curso.creditos:<7}{profesor[:22]:<23}")
    print("  " + "-" * 66)
    print(f"  Total de cursos: {len(inscripciones)}")


def opcion_estudiantes_de_curso(sistema: SistemaGestion) -> None:
    """Reporte: estudiantes inscritos en un curso."""
    print("\n--- ESTUDIANTES INSCRITOS EN UN CURSO ---")
    codigo = pedir_id("Código del curso: ")
    curso = sistema.obtener_curso(codigo)
    inscripciones = sistema.estudiantes_de_curso(codigo)

    print(f"\n  Curso: {curso}")
    print(f"  Profesor: {sistema.nombre_profesor_de_curso(curso)}")
    if not inscripciones:
        print("  (No hay estudiantes inscritos)")
        return

    print("\n  " + "-" * 66)
    print(f"  {'Carné':<12}{'Nombre':<28}{'Promedio':<11}{'Estado':<12}")
    print("  " + "-" * 66)
    for inscripcion in inscripciones:
        estudiante = sistema.estudiantes[inscripcion.carne]
        print(
            f"  {estudiante.carne:<12}{estudiante.nombre[:26]:<28}"
            f"{formato_nota(inscripcion.promedio()):<11}{inscripcion.estado():<12}"
        )
    print("  " + "-" * 66)
    print(f"  Total de estudiantes: {len(inscripciones)}")


def opcion_historial(sistema: SistemaGestion) -> None:
    """Reporte: historial académico detallado de un estudiante."""
    print("\n--- HISTORIAL ACADÉMICO ---")
    carne = pedir_id("Carné del estudiante: ")
    estudiante = sistema.obtener_estudiante(carne)
    inscripciones = sistema.cursos_de_estudiante(carne)

    print("\n" + "=" * 70)
    print("                  HISTORIAL ACADÉMICO DETALLADO")
    print("=" * 70)
    print(f"  Carné : {estudiante.carne}")
    print(f"  Nombre: {estudiante.nombre}")
    print(f"  Correo: {estudiante.correo}")
    print("=" * 70)

    if not inscripciones:
        print("  (El estudiante no ha tomado cursos)")
        return

    # Acumuladores para el resumen final
    aprobados = reprobados = en_curso = 0
    creditos_aprobados = 0
    creditos_finalizados = 0
    suma_ponderada = 0.0  # suma de (nota final * créditos) de cursos finalizados

    for inscripcion in inscripciones:
        curso = sistema.cursos[inscripcion.codigo_curso]
        print(f"\n  Curso   : {curso.nombre} ({curso.codigo}) - {curso.creditos} créditos")
        print(f"  Profesor: {sistema.nombre_profesor_de_curso(curso)}")
        print("  Evaluaciones:")
        for evaluacion, peso in EVALUACIONES.items():
            nota = inscripcion.notas.get(evaluacion)
            print(f"     - {evaluacion:<14} ({peso:>4g}%): {formato_nota(nota)}")

        estado = inscripcion.estado()
        etiqueta = "Nota final" if inscripcion.esta_completa() else "Promedio parcial"
        print(f"  {etiqueta}: {formato_nota(inscripcion.promedio())}  =>  ESTADO: {estado}")
        print("  " + "-" * 66)

        # Se acumulan los totales según el estado del curso
        if estado == "APRUEBA":
            aprobados += 1
            creditos_aprobados += curso.creditos
        elif estado == "REPRUEBA":
            reprobados += 1
        else:
            en_curso += 1
        if inscripcion.esta_completa():
            creditos_finalizados += curso.creditos
            suma_ponderada += inscripcion.promedio() * curso.creditos

    print("\n  RESUMEN")
    print(f"     Cursos aprobados  : {aprobados}")
    print(f"     Cursos reprobados : {reprobados}")
    print(f"     Cursos en curso   : {en_curso}")
    print(f"     Créditos aprobados: {creditos_aprobados}")
    if creditos_finalizados > 0:
        promedio_general = suma_ponderada / creditos_finalizados
        print(f"     Promedio general (ponderado por créditos): {promedio_general:.2f}")
    else:
        print("     Promedio general: N/D (aún no hay cursos finalizados)")
    print("=" * 70)


# ==============================================================================
# DATOS: GUARDAR, CARGAR Y DATOS DE PRUEBA
# ==============================================================================
def opcion_guardar_datos(sistema: SistemaGestion) -> None:
    """Guarda todos los datos del sistema en un archivo JSON."""
    print("\n--- GUARDAR DATOS EN JSON ---")
    print(f"  Archivo por defecto: {RUTA_DATOS_POR_DEFECTO}")
    print("  (Puede escribir solo un nombre, ej. 'semestre1', y se guardará en la carpeta datos/)")
    entrada = input_validado(
        "Nombre o ruta del archivo (ENTER = por defecto): ", str, permitir_vacio=True
    )
    ruta = resolver_ruta(entrada)

    # Si el usuario eligió un archivo distinto al de por defecto y ya existe,
    # se pide confirmación para no sobrescribirlo por accidente.
    if ruta != RUTA_DATOS_POR_DEFECTO and os.path.exists(ruta):
        if not confirmar(f"  El archivo '{ruta}' ya existe. ¿Desea sobrescribirlo? (s/n): "):
            print("\n  Guardado cancelado.")
            return

    guardar_en_json(sistema, ruta)
    print(f"\n  [OK] Datos guardados en: {ruta}")
    imprimir_resumen_datos(sistema)


def opcion_cargar_datos(sistema: SistemaGestion) -> None:
    """Carga los datos desde un archivo JSON, reemplazando los actuales."""
    print("\n--- CARGAR DATOS DESDE JSON ---")
    print(f"  Archivo por defecto: {RUTA_DATOS_POR_DEFECTO}")
    entrada = input_validado(
        "Nombre o ruta del archivo (ENTER = por defecto): ", str, permitir_vacio=True
    )
    ruta = resolver_ruta(entrada)

    # Cargar reemplaza todo: si hay datos en memoria se pide confirmación
    if not sistema.esta_vacio():
        aviso = "con cambios sin guardar " if sistema.cambios_sin_guardar else ""
        if not confirmar(
            f"  Los datos actuales {aviso}serán reemplazados. ¿Desea continuar? (s/n): "
        ):
            print("\n  Carga cancelada.")
            return

    cargar_desde_json(sistema, ruta)
    print(f"\n  [OK] Datos cargados desde: {ruta}")
    imprimir_resumen_datos(sistema)


def opcion_cargar_datos_prueba(sistema: SistemaGestion) -> None:
    """Agrega los datos de prueba predefinidos (sin duplicar los existentes)."""
    print("\n--- CARGAR DATOS DE PRUEBA ---")
    creados = cargar_datos_prueba(sistema)
    if creados == 0:
        print("  Los datos de prueba ya estaban cargados (no se duplicó nada).")
    else:
        print(f"  [OK] Datos de prueba cargados ({creados} registros nuevos).")
    print("\n  Sugerencias para probar:")
    print("    - Carnés: 2024001 (Ana), 2024002 (Luis), 2024003 (María), 2024004 (José)")
    print("    - Cursos: MAT101, PRG101, MAT201, PRG201, BDD201")
    print("    - Inscribir a Luis (2024002) en MAT201: debe fallar (reprobó MAT101).")
    print("    - Inscribir a Ana (2024001) en PRG201: debe funcionar.")
    print("    - Inscribir otra vez a Ana en MAT101: debe fallar (duplicado).")
