# -*- coding: utf-8 -*-
"""
interfaz/opciones_datos.py
==========================
Opciones del menú para guardar y cargar los datos en archivos JSON, y para
precargar los datos de prueba.
"""

import os

from config import RUTA_DATOS_POR_DEFECTO
from interfaz.presentacion import encabezado, imprimir_resumen_datos
from servicios.datos_prueba import cargar_datos_prueba
from servicios.persistencia import cargar_desde_json, guardar_en_json, resolver_ruta
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import confirmar, input_validado


def opcion_guardar_datos(sistema: SistemaGestion) -> None:
    """Guarda todos los datos del sistema en un archivo JSON."""
    encabezado("Guardar datos en JSON")
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
    encabezado("Cargar datos desde JSON")
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
    print("    - Estudiantes: Ana García, Luis Pérez, María López, José Hernández")
    print("    - Cursos: MAT101, PRG101, MAT201, PRG201, BDD201")
    print("    - Inscribir a Luis en Matemática II: debe fallar (reprobó Matemática I).")
    print("    - Inscribir a Ana en Programación II: debe funcionar.")
    print("    - Inscribir otra vez a Ana en Matemática I: debe fallar (duplicado).")
