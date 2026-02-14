#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para generar informe de gestión
Procesa actividades realizadas y las asocia con actividades específicas
"""

import csv
import os
from datetime import datetime
from collections import defaultdict

# Rutas de archivos
BASE_DIR = '/home/ndsabogalv/Documents/udistrital-cps1899/informe-gestion'
ACTIVIDADES_ESPECIFICAS = f'{BASE_DIR}/data/actividades_especificas.tsv'
ACTIVIDADES_PERIODO = f'{BASE_DIR}/output/helper/actividades_realizadas_2026-02-01_2026-02-14.tsv'
OUTPUT_FILE = f'{BASE_DIR}/output/informe_202602.tsv'

# Cargar catálogo de actividades específicas
def cargar_actividades_especificas():
    """Lee el catálogo de actividades y sus productos asociados"""
    catalogo = {}
    with open(ACTIVIDADES_ESPECIFICAS, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # La primera columna contiene "número. descripción"
            actividad_col = row['ACTIVIDADES']
            producto_col = row['PRODUCTO ASOCIADO']
            
            # Extraer el número y la descripción
            partes = actividad_col.split('.', 1)
            if len(partes) == 2:
                num = partes[0].strip()
                desc = partes[1].strip()
                catalogo[num] = {
                    'descripcion': desc,
                    'producto': producto_col
                }
    return catalogo

# Cargar actividades realizadas
def cargar_actividades_realizadas():
    """Lee las actividades del periodo filtrado"""
    actividades = []
    with open(ACTIVIDADES_PERIODO, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            actividades.append(row)
    return actividades

# Función para buscar la actividad específica correspondiente
def buscar_actividad_especifica(descripcion, catalogo):
    """
    Busca a qué actividad específica corresponde una actividad realizada
    Retorna el número de actividad específica
    """
    desc_lower = descripcion.lower()
    
    # Mapeo basado en palabras clave
    if 'bugs' in desc_lower or 'corrección' in desc_lower:
        return '10'  # Pruebas de integración
    elif 'demostración' in desc_lower or 'feedback' in desc_lower:
        return '11'  # Acta de validación
    elif 'usabilidad' in desc_lower:
        return '8'  # Auditoría de accesibilidad
    elif 'documentación' in desc_lower and 'api' in desc_lower:
        return '7'  # Manual de usuario
    elif 'ci' in desc_lower or 'despliegue continuo' in desc_lower:
        return '6'  # Scripts de despliegue
    elif 'optimización' in desc_lower or 'rendimiento' in desc_lower:
        return '10'  # Pruebas de integración
    elif 'seguimiento' in desc_lower or 'cierre' in desc_lower:
        return '9'  # Consolidar evidencias
    
    return '9'  # Por defecto, actividades de gestión/seguimiento

# Función para generar producto entregable específico
def generar_producto_especifico(actividad_desc, producto_base, evidencia):
    """
    Genera un nombre de producto más específico basado en la actividad realizada
    """
    desc_lower = actividad_desc.lower()
    
    # Personalizar según el tipo de actividad
    if 'acta' in evidencia.lower() or 'cierre' in desc_lower:
        return 'Acta de cierre de tareas'
    elif 'ci_pipeline' in evidencia or 'yml' in evidencia:
        return 'Pipeline de integración continua'
    elif 'perf_report' in evidencia or 'rendimiento' in desc_lower:
        return 'Reporte de optimización de rendimiento'
    elif 'api_docs' in evidencia:
        return 'Documentación de API REST'
    elif 'usabilidad' in evidencia.lower():
        return 'Reporte de pruebas de usabilidad'
    elif 'commit:' in evidencia:
        return 'Correcciones en código fuente'
    elif 'demo' in evidencia.lower():
        return 'Acta de demostración funcional'
    
    # Si no hay caso específico, usar el producto base sin punto final
    return producto_base.rstrip('.')

# Generar el informe
def generar_informe():
    """Procesa los datos y genera el archivo de informe"""
    catalogo = cargar_actividades_especificas()
    actividades = cargar_actividades_realizadas()
    
    # Agrupar por actividad específica
    agrupadas = defaultdict(list)
    for actividad in actividades:
        num_act_esp = buscar_actividad_especifica(actividad['Actividad'], catalogo)
        agrupadas[num_act_esp].append(actividad)
    
    # Construir el informe
    informe = []
    for num_act_esp in sorted(agrupadas.keys(), key=lambda x: int(x)):
        acts = agrupadas[num_act_esp]
        
        # Si hay más de 5 actividades, agrupar
        if len(acts) > 5:
            # Crear un registro consolidado
            fecha_inicio = acts[0]['Fecha'].split()[0]
            fecha_fin = acts[-1]['Fecha'].split()[0]
            
            producto = catalogo[num_act_esp]['producto']
            evidencias = [a['Evidencia'] for a in acts if a['Evidencia'].strip()]
            evidencia_principal = evidencias[0] if evidencias else ''
            
            registro = {
                'Actividad_Especifica': num_act_esp,
                'Fecha': fecha_inicio,
                'Descripcion': f"Actividades consolidadas de {catalogo[num_act_esp]['descripcion'].lower()}",
                'Producto_Entregable': producto,
                'Evidencia': evidencia_principal
            }
            informe.append(registro)
        else:
            # Registrar cada actividad individualmente
            for act in acts:
                fecha = act['Fecha'].split()[0]
                producto_base = catalogo[num_act_esp]['producto']
                producto = generar_producto_especifico(act['Actividad'], producto_base, act['Evidencia'])
                
                registro = {
                    'Actividad_Especifica': num_act_esp,
                    'Fecha': fecha,
                    'Descripcion': act['Actividad'],
                    'Producto_Entregable': producto,
                    'Evidencia': act['Evidencia']
                }
                informe.append(registro)
    
    # Verificar si el archivo ya existe
    output_path = OUTPUT_FILE
    version = 1
    while os.path.exists(output_path):
        output_path = OUTPUT_FILE.replace('.tsv', f'_v{version}.tsv')
        version += 1
    
    # Escribir el archivo
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['Actividad_Especifica', 'Fecha', 'Descripcion', 'Producto_Entregable', 'Evidencia']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(informe)
    
    print(f"✓ Informe generado exitosamente: {output_path}")
    print(f"  Total de registros: {len(informe)}")
    print(f"  Actividades específicas: {len(set(r['Actividad_Especifica'] for r in informe))}")

if __name__ == '__main__':
    generar_informe()
