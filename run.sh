#!/bin/bash
set -euo pipefail

uso() {
    cat <<EOF
    Uso: $0 [opciones] [FECHA_INICIO]
    Opciones:
      -i FECHA_INICIO Fecha de inicio (YYYY-MM-DD)
      -f FECHA_FIN    Fecha de fin (YYYY-MM-DD), defecto: hoy
      -p PERIODO      Periodo (YYYYMM), defecto: mes actual
      -m MODELO       Nombre del modelo, defecto: gpt-5-mini-high
      -d              Detallado (pasa -d a python)
      -h              Muestra esta ayuda
    Ejemplo:
      $0 -i 2024-01-01
EOF
}

principal() {
    local FECHA_INICIO=""
    local FECHA_FIN
    FECHA_FIN=$(date +%Y-%m-%d)
    local PERIODO
    PERIODO=$(date +%Y%m)
    local MODELO="gpt-5-mini-high"
    local BANDERA_DETALLADO=""

    while getopts ":i:f:p:m:dh" opcion; do
        case $opcion in
            i) FECHA_INICIO="$OPTARG" ;;
            f) FECHA_FIN="$OPTARG" ;;
            p) PERIODO="$OPTARG" ;;
            m) MODELO="$OPTARG" ;;
            d) BANDERA_DETALLADO="-d" ;;
            h) uso; exit 0 ;;
            \?) echo "Opción inválida: -$OPTARG" >&2; uso; exit 2 ;;
            :) echo "La opción -$OPTARG requiere un argumento." >&2; uso; exit 2 ;;
        esac
    done
    shift $((OPTIND - 1))

    # Si se provee fecha posicional
    if [ -z "$FECHA_INICIO" ] && [ $# -ge 1 ]; then
        FECHA_INICIO="$1"
    fi

    if [ -z "$FECHA_INICIO" ]; then
        echo "Error: Se requiere FECHA_INICIO."
        uso
        exit 1
    fi
     
    python -m src.main -fi "$FECHA_INICIO" -ff "$FECHA_FIN" -p "$PERIODO" -m "$MODELO" $BANDERA_DETALLADO
}

principal "$@"
