"""
Este script se encarga de convertir el libro de Excel `data/actividades_realizadas.xlsx` a un archivo TSV (`data/actividades_realizadas.tsv`) que el agente leerá para procesar las actividades realizadas. El script también limpia los saltos de línea dentro de las celdas para evitar romper el formato del archivo de texto.
"""


import pandas as pd
import os

def main():
    # Definir rutas de archivo
    archivo_entrada = "data/actividades_realizadas.xlsx"
    archivo_salida = "data/actividades_realizadas.tsv"

    if not os.path.exists(archivo_entrada):
         print(f"Advertencia: No se encontró {archivo_entrada}. Asegúrese de que el archivo exista en la raíz.")
         return

    df = pd.read_excel(archivo_entrada)

    # Asegurarse de que el directorio de salida exista
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)

    with open(archivo_salida, 'w', encoding='utf-8') as f:
        # Escribir la cabecera del archivo TSV
        # Unir nombres de columnas con tabulador
        f.write('\t'.join([str(c) for c in df.columns]) + '\n')

        # Iterar sobre cada fila del DataFrame y escribirla en el archivo TSV
        for indice, fila in df.iterrows():

            # Preparar los valores de la fila
            valores_fila = []
            for col in df.columns:
                valor = fila[col]

                # Manejar valores NaN y reemplazar saltos de línea
                if pd.isna(valor):
                    valor = ''
                else:
                    # Reemplazar saltos de línea para mantener formato TSV válido
                    valor = str(valor).replace('\n', '\n ').replace('\r', '\r ')

                valores_fila.append(valor)

            # Escribir la fila en el archivo TSV
            f.write('\t'.join(valores_fila) + '\n')

if __name__ == '__main__':
    main()
