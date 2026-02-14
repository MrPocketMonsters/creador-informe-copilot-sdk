# Generador de Informes de Gestión con IA

Este repositorio es una prueba de concepto para poner en práctica un sistema de generación automática de informes de gestión utilizando un agente de inteligencia artificial (IA) a través de CopilotCLI, y su [SDK en Python](https://github.com/github/copilot-sdk). El objetivo es transformar un registro crudo de actividades diarias en un informe estructurado y formateado, siguiendo las reglas y el estilo de informes previamente aprobados.

## 📋 Tabla de Contenido

- [Propósito](#-propósito)
- [Preparación y Ejecución](#️-preparación-y-ejecución)
  - [Prerrequisitos](#prerrequisitos)
  - [Instalación](#instalación)
  - [Uso](#uso)
- [Archivos Importantes](#️-archivos-importantes)
- [Archivos Inyectables](#-archivos-inyectables)
- [Licencia](#licencia)

## 🎯 Propósito

El objetivo principal es reducir la carga operativa en la elaboración de informes de gestión mensuales. A partir de un registro crudo de actividades (`data/actividades_realizadas.tsv`), el sistema:

1. Filtra las actividades por rango de fechas.
2. Agrupa y sintetiza la información relevante.
3. Asocia cada actividad realizada con su **Actividad Específica** y **Entregable** contractual correspondiente.
4. Genera un archivo de salida que respeta estrictamente el formato de los informes previamente aprobados.

El trabajador puede centrarse en registrar sus actividades diarias en un formato sencillo (Excel), sin preocuparse por el dominio de las actividades realizadas o los productos asociados. El agente de IA se encarga de interpretar, cruzar datos y formatear el informe final, siguiendo las reglas de negocio definidas en `src/task.md`.

## ⚙️ Preparación y Ejecución

### Prerrequisitos

- **[Python 3.13](https://www.python.org/downloads/release/python-31312/)+**: El proyecto está desarrollado y probado con Python 3.13, aunque versiones posteriores también deberían funcionar.
- **[CopilotCLI](https://github.com/github/copilot-cli)**: El agente de IA se ejecuta a través de CopilotCLI, por lo que es necesario tenerlo instalado y configurado correctamente.

### Instalación

1. Clona este repositorio.
2. Crea y activa un entorno virtual (recomendado):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

### Uso

La forma principal de ejecutar el generador es a través del script `run.sh`, que envuelve la lógica principal y facilita el paso de parámetros.

**Sintaxis básica:**

```bash
./run.sh -i YYYY-MM-DD [opciones]
```

**Opciones disponibles:**

| Opción | Descripción | Valor por defecto |
| - | - | - |
| `-i` | **Fecha de inicio** (Requerido) en formato YYYY-MM-DD. | N/A |
| `-f` | Fecha de fin (YYYY-MM-DD). | Fecha actual |
| `-p` | Periodo del informe (YYYYMM). | Mes actual (ej. 202602) |
| `-m` | Modelo de IA a utilizar. | `gpt-5-mini-high` |
| `-d` | Modo detallado (logs en consola). Pasa `-d` al script Python. | Desactivado |
| `-h` | Muestra la ayuda del comando. | N/A |

**Ejemplos:**

Generar informe desde el 1 de febrero de 2026 hasta hoy:

```bash
./run.sh -i 2026-02-01
```

Generar informe para un rango específico y un modelo diferente con logs detallados:

```bash
./run.sh -i 2026-01-01 -f 2026-01-31 -p 202601 -m "gpt-4" -d
```

## 🏗️ Archivos Importantes

Esta sección describe los componentes clave del código fuente (`src/`) que orquestan la generación del informe.

### `src/main.py`

El punto de entrada principal. Su función es:

1. Recibir los argumentos de línea de comandos (`-fi`, `-ff`, etc.).
2. Ejecutar la conversión de datos (llama a `src.actividades_realizadas_to_tsv`).
3. Leer la plantilla de instrucciones (`src/task.md`) e inyectar las variables dinámicas (fechas de inicio/fin).
4. Iniciar la sesión con el agente de IA (`src/agente.py`) para ejecutar la tarea.

### `src/actividades_realizadas_to_tsv.py`

Script auxiliar de preprocesamiento de datos.

- **Entrada**: Busca un archivo Excel en `data/actividades_realizadas.xlsx`.
- **Proceso**: Convierte el libro de Excel a formato TSV (Tab-Separated Values). Limpia los saltos de línea dentro de las celdas para evitar romper el formato del archivo de texto.
- **Salida**: Genera `data/actividades_realizadas.tsv`, que es el archivo que el agente leerá.

### `src/task.md`

El "prompt" o instrucciones maestras del sistema. Define paso a paso la lógica que debe seguir el agente (filtrar, leer, cruzar datos, formatear). Se encuentra en la carpeta `src/` para mantener la lógica cerca del código.

### `src/agente.py`

El cliente que interactúa con el modelo de IA (Copilot).

- Maneja la conexión y la sesión de chat.
- Gestiona los eventos del ciclo de vida (inicio de herramientas, mensajes del asistente, errores).
- Ejecuta las instrucciones recibidas en lenguaje natural (todo en español).

## 📂 Archivos Inyectables

El funcionamiento del agente depende de varios archivos de contexto ubicados principalmente en las carpetas `data/` y `approved/`. Estos archivos guían al modelo sobre *qué* hacer y *cómo* debe verse el resultado.

### En `data/`

- **`actividades_especificas.tsv`**: Catálogo maestro. Relaciona los IDs de actividades contractuales con sus descripciones y los entregables esperados.
- **`actividades_realizadas.tsv`**: (Generado) Log crudo de actividades diarias en formato TSV, listo para ser procesado por el agente.
- **`actividades_realizadas.xlsx`**: (Entrada Manual) El archivo Excel original donde registras tus actividades. **Debe estar en `data/`**.

**Formato Requerido para `actividades_realizadas.xlsx`**:

Esta es la fuente de verdad. Para que el sistema funcione correctamente, la hoja activa o primera hoja del libro debe cumplir lo siguiente:

1. **Primera Columna: FECHA**
   - El sistema filtra por fechas. La columna **A** (o la primera columna leída) debe contener la fecha de la actividad.
   - Formato recomendado: `YYYY-MM-DD` (Texto o fecha Excel estándar).

2. **Columnas de Datos**
   - El resto de columnas (ej. B, C, D...) contendrán la descripción, actividad, observaciones, etc.
   - El agente leerá todas las columnas presentes.

3. **Limpieza de Datos**
   - El script preprocesador (`src/actividades_realizadas_to_tsv.py`) eliminará saltos de línea (`\n`, `\r`) dentro de las celdas para asegurar un formato TSV válido.
   - Encabezados: La primera fila se considera la cabecera.

### En `approved/`

- **`informe_YYYYMM.tsv`**: Ejemplos de informes anteriores exitosos/aprobados. El agente lee estos archivos ("few-shot learning") para entender el estilo de redacción, el formato exacto de las columnas y cómo agrupar la información para mantener la consistencia histórica.

### Salida

Los reportes generados se guardan automáticamente en la carpeta:

- **`output/`**: Aquí encontrarás los archivos `informe_YYYYMM.tsv` generados.
- **`output/helper/`**: Carpeta para archivos temporales o scripts auxiliares. El agente puede crear archivos aquí sin riesgo de sobrescribir documentos importantes.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
