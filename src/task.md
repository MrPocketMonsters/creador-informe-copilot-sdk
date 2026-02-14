# Generación de Informe de Gestión

Genera un informe con las actividades registradas entre `{FECHA_INICIO}` y `{FECHA_FIN}`.

## Pasos de Ejecución

1. **Leer Insumos**:
   - Carga `./data/actividades_especificas.tsv` para obtener el catálogo de actividades y entregables.
   - Analiza la estructura de los informes previos en `./approved/*`.

2. **Obtener Actividades del Periodo**:
   - Ejecuta este comando para filtrar los registros por fecha y generar un archivo temporal:

     ```bash
     awk -F $'\t' 'NR==1{{print; next}} $1 >= "{FECHA_INICIO}" && $1 <= "{FECHA_FIN}"' data/actividades_realizadas.tsv > ./output/helper/actividades_realizadas_{FECHA_INICIO}_{FECHA_FIN}.tsv
     ```

   - Lee el archivo generado para procesar los datos.

3. **Generar Reporte**:
   - Crea el archivo `./output/informe_{PERIODO}.tsv`.
   - **Importante**: Si el archivo ya existe, **NO** lo sobrescribas. Añade un sufijo de versión (ej: `_v1.tsv`).

4. **Procesamiento de Datos**:
   - Cruza las actividades realizadas con las 'actividades específicas' y asigna el 'entregable' correspondiente.
   - Agrupa actividades de planeación o diarias en un único registro consolidado.

## Reglas de Negocio

- **Estructura y Formato**: El resultado debe ser estrictamente consistente con los archivos en `approved/`.
- **Orden**: Ordena el campo 'Actividad Específica' de menor a mayor.
- **Límite de Registros**: Máximo **5 registros** por cada 'Actividad Específica'.
  - Si hay más, agrúpalos en un registro general que resuma la labor.
  - Si no es posible agrupar, descarta las actividades menos relevantes para mantener la concisión.
- **Entregables**: Deben ser **concisos y nominativos** (un solo producto), alineados con `./data/actividades_especificas.tsv` y las actividades realizadas. Evita términos genéricos.
- **Seguridad**: Nunca borres archivos existentes. Usa `./output/helper/` para cualquier archivo temporal o script auxiliar.
- **Ejecución**: Realiza el proceso en su totalidad sin solicitar confirmaciones intermedias de nintún tipo.
