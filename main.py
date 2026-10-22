# -*- coding: utf-8 -*-
"""
main.py
=======
Punto de entrada del Sistema de Gestión Académica Universitaria.

Ejecución:
    python main.py

Este archivo solo orquesta el flujo del programa:
  1. Muestra la carátula.
  2. Ofrece cargar el archivo de datos guardado (o los datos de prueba).
  3. Ejecuta el menú principal en un bucle hasta que el usuario sale.
  4. Al salir, avisa si hay cambios sin guardar.

Toda la lógica vive en los paquetes: modelos/, servicios/, interfaz/ y
utilidades/.
"""

import os
import sys

from config import RUTA_DATOS_POR_DEFECTO
from excepciones import ErrorGestion, OperacionCancelada
from interfaz.caratula import mostrar_caratula
from interfaz.menu import (
    OPCION_SALIR,
    construir_acciones,
    mostrar_menu,
    numero_maximo_opcion,
)
from interfaz.opciones_datos import opcion_cargar_datos_prueba
from interfaz.presentacion import imprimir_resumen_datos
from servicios.persistencia import cargar_desde_json, guardar_en_json
from servicios.sistema_gestion import SistemaGestion
from utilidades.consola import confirmar, input_validado, limpiar_pantalla, pausar


def configurar_consola() -> None:
    """Evita que el programa se cierre en consolas que no pueden mostrar
    algún carácter especial (por ejemplo, los bordes de la carátula).

    Si un carácter no se puede mostrar, se reemplaza por '?' en lugar de
    lanzar un error de codificación.
    """
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass  # el flujo no admite reconfigurarse: se deja como está


def inicio_con_datos(sistema: SistemaGestion) -> None:
    """Ofrece al usuario cargar datos al arrancar el programa.

    - Si existe un archivo guardado, ofrece cargarlo.
    - Si no se cargó nada, ofrece cargar los datos de prueba.
    """
    if os.path.isfile(RUTA_DATOS_POR_DEFECTO):
        if confirmar("Se encontró un archivo de datos guardado. ¿Desea cargarlo? (s/n): "):
            cargar_desde_json(sistema, RUTA_DATOS_POR_DEFECTO)
            print(f"\n  [OK] Datos cargados desde: {RUTA_DATOS_POR_DEFECTO}")
            imprimir_resumen_datos(sistema)
            pausar()
            return

    if confirmar("¿Desea cargar datos de prueba para empezar? (s/n): "):
        opcion_cargar_datos_prueba(sistema)
        pausar()


def preparar_salida(sistema: SistemaGestion) -> None:
    """Si hay cambios sin guardar, pregunta si se desean guardar antes de salir.

    Si el guardado falla se lanza ErrorPersistencia: el bucle principal lo
    muestra y el programa NO se cierra, para que el usuario no pierda sus datos.
    """
    if sistema.cambios_sin_guardar:
        if confirmar("Hay cambios sin guardar. ¿Desea guardarlos antes de salir? (s/n): "):
            guardar_en_json(sistema, RUTA_DATOS_POR_DEFECTO)
            print(f"\n  [OK] Datos guardados en: {RUTA_DATOS_POR_DEFECTO}")


def esperar_antes_de_cerrar() -> None:
    """Mantiene abierta la ventana al terminar cuando se ejecuta como .exe.

    Al abrir el .exe con doble clic, Windows cierra la ventana en cuanto el
    programa termina y no daría tiempo de leer el mensaje de despedida.
    Al ejecutarlo como script (`python main.py`) no hace falta esperar.
    """
    if getattr(sys, "frozen", False):
        try:
            input("Presione ENTER para cerrar la ventana...")
        except EOFError:
            pass


def main() -> None:
    """Bucle principal: muestra el menú y ejecuta la opción elegida.

    Cada opción se ejecuta dentro de un try/except:
      - OperacionCancelada -> el usuario escribió 'cancelar': se vuelve al menú
                              sin pausa y sin haber aplicado nada a medias.
      - ErrorGestion       -> error de regla de negocio o de archivos (mensaje amigable).
      - KeyboardInterrupt  -> Ctrl+C: igual que cancelar.
      - Exception          -> cualquier error inesperado, para no tumbar el sistema.
    """
    configurar_consola()
    sistema = SistemaGestion()
    acciones = construir_acciones()
    maximo = numero_maximo_opcion()

    limpiar_pantalla()
    mostrar_caratula()

    # --- Arranque: ofrecer cargar datos guardados o de prueba ---
    try:
        inicio_con_datos(sistema)
    except ErrorGestion as error:
        print(f"\n  [ERROR] {error}")
        pausar()
    except (OperacionCancelada, KeyboardInterrupt):
        print()  # si cancela aquí, simplemente se continúa al menú

    # --- Bucle del menú principal ---
    while True:
        mostrar_menu()
        try:
            opcion = input_validado(
                f"Seleccione una opción ({OPCION_SALIR}-{maximo}): ",
                int,
                minimo=OPCION_SALIR,
                maximo=maximo,
                permitir_cancelar=False,  # en el menú no tiene sentido cancelar
            )

            if opcion == OPCION_SALIR:
                preparar_salida(sistema)
                print("\nGracias por usar el Sistema de Gestión Académica. ¡Hasta pronto!\n")
                esperar_antes_de_cerrar()
                return

            acciones[opcion](sistema)

        except (OperacionCancelada, KeyboardInterrupt):
            # Cancelación voluntaria: se limpia la pantalla, se avisa y se
            # vuelve DIRECTO al menú (sin pedir ENTER).
            limpiar_pantalla()
            print("\n  Operación cancelada. No se realizó ningún cambio.")
            continue
        except ErrorGestion as error:
            print(f"\n  [ERROR] {error}")
        except Exception as error:  # red de seguridad ante errores inesperados
            print(f"\n  [ERROR INESPERADO] {type(error).__name__}: {error}")

        pausar()
        limpiar_pantalla()


if __name__ == "__main__":
    main()
