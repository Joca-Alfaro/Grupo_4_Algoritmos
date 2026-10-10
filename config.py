# -*- coding: utf-8 -*-
"""
config.py
=========
Configuración central del Sistema de Gestión Académica Universitaria.

Todas las constantes y reglas académicas viven en este único archivo, de modo
que cambiar una regla (por ejemplo, la nota de aprobación o la ponderación de
una evaluación) no obligue a tocar el resto del código.

Este módulo NO importa ningún otro módulo del proyecto, por lo que puede ser
importado desde cualquier parte sin riesgo de importaciones circulares.
"""

import os
import sys
from typing import Dict, List, Tuple

# ==============================================================================
# RUTAS DE ARCHIVOS
# ==============================================================================

# Carpeta raíz del programa. Se calcula de forma distinta según cómo se ejecute:
#   - Como ejecutable (.exe creado con PyInstaller): `__file__` apunta a una
#     carpeta temporal que se borra al cerrar el programa, así que se usa la
#     carpeta donde está el propio ejecutable. De lo contrario los datos
#     guardados se perderían.
#   - Como script (`python main.py`): la carpeta donde está este archivo, sin
#     importar desde qué carpeta se lance el comando.
if getattr(sys, "frozen", False):
    DIRECTORIO_BASE: str = os.path.dirname(os.path.abspath(sys.executable))
else:
    DIRECTORIO_BASE: str = os.path.dirname(os.path.abspath(__file__))

# Carpeta donde se guardan los archivos JSON con los datos del sistema.
DIRECTORIO_DATOS: str = os.path.join(DIRECTORIO_BASE, "datos")

# Nombre y ruta completa del archivo JSON que se usa por defecto.
NOMBRE_ARCHIVO_POR_DEFECTO: str = "academico.json"
RUTA_DATOS_POR_DEFECTO: str = os.path.join(DIRECTORIO_DATOS, NOMBRE_ARCHIVO_POR_DEFECTO)

# Versión del formato del archivo JSON. Si en el futuro cambia la estructura
# de los datos, se incrementa este número para detectar archivos incompatibles.
VERSION_FORMATO_JSON: int = 1

# ==============================================================================
# REGLAS ACADÉMICAS
# ==============================================================================

NOTA_MINIMA: float = 0.0        # Nota mínima permitida en una evaluación
NOTA_MAXIMA: float = 100.0      # Nota máxima permitida en una evaluación
NOTA_APROBACION: float = 61.0   # Nota mínima (promedio final) para aprobar un curso

# Evaluaciones de cada curso y su ponderación en porcentaje.
# Importante: la suma de los porcentajes debe ser exactamente 100.
EVALUACIONES: Dict[str, float] = {
    "Parcial 1": 20.0,
    "Parcial 2": 20.0,
    "Proyecto": 20.0,
    "Examen Final": 40.0,
}

# Verificación de seguridad: si alguien modifica las ponderaciones y la suma
# deja de ser 100, el programa avisa de inmediato en lugar de calcular mal.
if abs(sum(EVALUACIONES.values()) - 100.0) > 1e-9:
    raise ValueError("La suma de las ponderaciones de EVALUACIONES debe ser 100.")

# ==============================================================================
# DATOS DE LA CARÁTULA
# ==============================================================================
# Reemplace cada marcador [MOLDE] con la información real del equipo.
# Solo es necesario editar este bloque; la carátula se arma sola a partir de él.

NOMBRE_UNIVERSIDAD: str = "UNIVERSIDAD MARIANO GALVEZ DE GUATEMALA"
NOMBRE_CURSO: str = "ALGORITOMOS"
NOMBRE_CATEDRATICO: str = "ING. DEMSHILL COUTIÑO"
FECHA_PRESENTACION: str = "30 DE OCTUBRE DE 2026"

# Lista de integrantes: cada elemento es una tupla (nombre, carné).
INTEGRANTES: List[Tuple[str, str]] = [
    ("JOSE CARLOS ALFARO GARCIA", "0906-26-9140"),
    ("MARVIN MAIKEL GONZALEZ", "0906-26-1010"),
    ("THELMA", "0906-26-2020"),
    ("SEPA COMO SE LLAM LA OTRA", "0906-26-3030"),
]
