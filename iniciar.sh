#!/bin/sh
# ==============================================================
#  Inicia el Sistema de Gestion Academica en Mac o Linux.
#  Uso:  sh iniciar.sh     (o:  ./iniciar.sh)
# ==============================================================
cd "$(dirname "$0")" || exit 1

if command -v python3 >/dev/null 2>&1; then
    python3 main.py
elif command -v python >/dev/null 2>&1; then
    python main.py
else
    echo "No se encontro Python. Instalelo desde https://www.python.org/downloads/"
    exit 1
fi
