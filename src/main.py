"""
Este es el punto de entrada principal del proyecto. Se encarga de:
1. Procesar argumentos de línea de comandos (fecha inicio, fecha fin, periodo, modelo, modo detallado).
2. Ejecutar el script para convertir actividades de Excel a TSV.
3. Leer la plantilla de tarea (task.md) y formatearla con las fechas y periodo.
4. Llamar al agente (src/agente.py) pasando la tarea formateda y el modelo seleccionado.
"""


import asyncio
import argparse
import time
import subprocess

async def main():
    parser = argparse.ArgumentParser(description="Automatizar la generación de informes")
    parser.add_argument(
        '-fi', '--fecha_inicio',
        type=str,
        help='La fecha de inicio para el informe (YYYY-MM-DD). Requerida.',
    )
    parser.add_argument(
        '-ff', '--fecha_fin',
        type=str,
        default=time.strftime('%Y-%m-%d'),
        help='La fecha final para el informe (YYYY-MM-DD) [default: hoy]',
    )
    parser.add_argument(
        '-p', '--periodo',
        type=str,
        default=time.strftime('%Y%m'),
        help='El año y mes del informe (ej. 202601 para Enero 2026)',
    )
    parser.add_argument(
        '-m', '--modelo',
        type=str,
        default='gpt-5-mini-high',
        help='El modelo de lenguaje a usar para el agente (default: gpt-5-mini-high)',
    )
    parser.add_argument(
        '-d', '--detallado',
        action='store_true',
        help='Habilitar salida detallada (logs)',
    )
    
    args = parser.parse_args()

    if not args.fecha_inicio:
        parser.error("Se requiere la fecha de inicio (use el argumento posicional o -fi)")



    # Llamamos al script traducido
    print("Ejecutando el script para convertir actividades a TSV...")
    subprocess.run(['python', '-m', 'src.actividades_realizadas_to_tsv'])


    # Preparar la tarea para el agente
    tarea_path = 'src/task.md'
    try:
        with open(tarea_path, 'r', encoding='utf-8') as f:
            plantilla_tarea = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró la plantilla de tarea en {tarea_path}")
        return

    descripcion_tarea = plantilla_tarea.format(
        FECHA_INICIO=args.fecha_inicio,
        FECHA_FIN=args.fecha_fin,
        PERIODO=args.periodo
    )


    # Construir el comando para ejecutar el agente
    comando_agente = [
        'python', '-m', 'src.agente',
        descripcion_tarea,
        '-m', args.modelo
    ]
    if args.detallado:
        comando_agente.append('--detallado')

    # Llamar al agente
    print("Ejecutando el agente para generar el informe...")
    subprocess.run(comando_agente)


if __name__ == '__main__':
    asyncio.run(main())
