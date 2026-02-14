"""
Este módulo contiene el cliente que interactúa con el modelo de IA (Copilot) para ejecutar la tarea definida en `task.md`. El agente se comunica con Copilot a través de eventos, mostrando mensajes, herramientas ejecutadas, intenciones detectadas y manejando errores. También incluye un mecanismo de monitoreo de inactividad para detener la sesión si no hay actividad por un tiempo definido.
"""


import os
import argparse
import asyncio
import logging

from copilot import CopilotClient, SessionEvent
from math import ceil

def en_evento(evento: SessionEvent, hecho: asyncio.Event, args: argparse.Namespace, callback=None):
    """Manejador de eventos para la sesión del agente. Imprime mensajes relevantes según el tipo de evento y actualiza el estado de inactividad."""

    if callback:
        callback(evento)
    try:
        match evento.type.value:
            case "assistant.message":
                print(f"Copilot: {evento.data.content}")
            case "tool.execution_start":
                print(f"  → Ejecutando: {evento.data.tool_name}")
            case "tool.execution_complete":
                print(f"  ✓ Completado: {evento.data.tool_call_id}")
            case "assistant.intent":
                print(f"  ! Intención detectada: {evento.data.intent_type}")
            case "session.error":
                print(f"[agente][error] Error de sesión: {evento.data.message}")
            case "session.idle":
                hecho.set()
            case _:
                if args.detallado:
                    print(f"[agente][debug] Evento no manejado: {evento.type.value}")
    except Exception as e:
        print(f"[agente][error] Error manejando evento {evento}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Interactuar con el Agente de GitHub Copilot")
    parser.add_argument(
        'tarea',
        type=str,
        help='Descripción de la tarea para Copilot',
    )
    parser.add_argument(
        '-d', '--detallado',
        action='store_true',
        help='Habilitar salida detallada y registros',
    )
    parser.add_argument(
        '-m', '--modelo',
        type=str,
        default='gpt-5-mini-high',
        help='Modelo a usar al ejecutar la tarea'
    )
    parser.add_argument(
        '-c', '--carpeta',
        type=str,
        default='.',
        help='Carpeta donde operará el agente'
    )
    parser.add_argument(
        '-t', '--tiempo_espera',
        type=int,
        default=120,
        help='Tiempo de espera por inactividad en segundos antes de que el agente se detenga'
    )
    args = parser.parse_args()



    # Preparar prompt
    carpeta_objetivo = os.path.realpath(args.carpeta)
    prompt = (
            f"Eres un asistente de trabajo con acceso a un sistema de archivos. Tu tarea es:\n"
            f"{args.tarea}.\n\n"
            f"La carpeta de trabajo es: {carpeta_objetivo}. "
            "Puedes leer y escribir archivos en esta carpeta según sea necesario para completar la tarea. "
            "Asegúrate de explicar lo que estás haciendo a medida que avanzas. "
            "No tienes permitido realizar cambios destructivo en documentos existentes."
        )


    # Configurar logging
    if args.detallado:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.detallado:
        print(f"[agente] Argumentos procesados: tarea={args.tarea!r}, modelo={args.modelo!r}, carpeta={args.carpeta!r}, detallado={args.detallado}")


    # Crear e iniciar agente
    cliente = CopilotClient()
    try:
        if args.detallado:
            print("[agente] Iniciando cliente Copilot...")
        await cliente.start()
        if args.detallado:
            print("[agente] Cliente Copilot iniciado")
    except Exception as e:
        print(f"[agente][error] Falló el inicio del cliente Copilot: {e}")
        return

    # Crear sesión
    sesion = await cliente.create_session({"model": args.modelo})

    # Esperar respuesta
    hecho = asyncio.Event()


    # Monitoreo de inactividad: actualizar timestamp en cada evento
    bucle = asyncio.get_running_loop()
    ultima_actividad = [bucle.time()]
    tiempo_espera_inactividad = args.tiempo_espera
    tarea_monitor = None
    
    async def _monitor_inactividad():
        try:
            while not hecho.is_set():
                await asyncio.sleep(1)
                if args.detallado and ceil(bucle.time() - ultima_actividad[0]) % 30 == 0:
                    print(f"[agente][debug] Chequeo monitor inactividad... {bucle.time() - ultima_actividad[0]:.1f}s transcurridos")
                if bucle.time() - ultima_actividad[0] > tiempo_espera_inactividad:
                    print(f"[agente][advertencia] Sin actividad por {tiempo_espera_inactividad}s. Deteniendo espera.")
                    hecho.set()
                    break
        except asyncio.CancelledError:
            return

    # Manejador de eventos: callback pequeño para actualizar ultima_actividad
    def _tocar(evento): ultima_actividad[0] = bucle.time()
    sesion.on(lambda evento: en_evento(evento, hecho, args, callback=_tocar))


    # Pedir a Copilot completar la tarea
    try:
        if args.detallado:
            print("[agente] Enviando prompt a la sesión...")
        # iniciar monitor
        tarea_monitor = asyncio.create_task(_monitor_inactividad())
        await sesion.send({ "prompt": prompt })
        # esperar hasta que hecho se active por session.idle o monitor
        await hecho.wait()
    except Exception as e:
        print(f"[agente][error] Error enviando prompt o esperando respuesta: {e}")


    # Limpieza
    # cancelar tarea monitor si corre
    try:
        if tarea_monitor:
            tarea_monitor.cancel()
            try:
                await tarea_monitor
            except Exception:
                pass
    except Exception:
        pass

    try:
        await sesion.destroy()
    except Exception:
        pass
    try:
        await cliente.stop()
    except Exception:
        pass


if __name__ == '__main__':
    asyncio.run(main())
