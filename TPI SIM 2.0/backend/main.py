import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Configuracion import ConfiguracionSimulacion
from Simulador import Simulador

app = FastAPI(title="Simulador Salud Vital - Grupo 13")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global
resultado_simulacion = None
current_simulation_task = None

class ParametrosSimulacion(BaseModel):
    tiempo_simulacion: float
    max_iteraciones: int
    cantidad_iteraciones_mostrar: int
    mostrar_desde_hora: float
    media_llegadas: float = 6.0
    vacunacion_min: float = 3.0
    vacunacion_max: float = 7.0
    tiempo_observacion: float = 15.0
    capacidad_observacion: int = 20
    capacidad_cola_externa: int = 10

def logica_simulacion(params: ParametrosSimulacion):
    """Función bloqueante que realiza la simulación pesada."""
    config = ConfiguracionSimulacion(
        tiempo_simulacion=params.tiempo_simulacion,
        max_iteraciones=params.max_iteraciones,
        media_llegadas=params.media_llegadas,
        vacunacion_min=params.vacunacion_min,
        vacunacion_max=params.vacunacion_max,
        tiempo_observacion=params.tiempo_observacion,
        capacidad_observacion=params.capacidad_observacion,
        capacidad_cola_externa=params.capacidad_cola_externa
    )
    
    sim = Simulador(config)
    sim.simular()
    
    vector_filtrado = []
    contador_mostrados = 0
    
    for fila in sim.tabla_estado:
        if fila["Reloj"] >= params.mostrar_desde_hora and contador_mostrados < params.cantidad_iteraciones_mostrar:
            vector_filtrado.append(fila)
            contador_mostrados += 1
            
    if sim.tabla_estado:
        ultima_fila = sim.tabla_estado[-1]
        if ultima_fila not in vector_filtrado:
            vector_filtrado.append(ultima_fila)
            
    return {
        "metricas": {
            "porcentaje_rechazo_fila_externa": sim.porcentaje_rechazo,
            "promedio_minutos_bloqueo": sim.promedio_bloqueo,
            "promedio_permanencia_sistema": sim.promedio_permanencia
        },
        "vector_estado": vector_filtrado
    }

@app.post("/simular")
async def simular(params: ParametrosSimulacion):
    global current_simulation_task, resultado_simulacion

    # 1. Cancelar simulación anterior si existe
    if current_simulation_task and not current_simulation_task.done():
        current_simulation_task.cancel()
        try:
            await current_simulation_task
        except asyncio.CancelledError:
            pass

    # 2. Definimos una función asíncrona que ejecute el código bloqueante
    async def ejecutar_en_segundo_plano():
        loop = asyncio.get_event_loop()
        # run_in_executor devuelve un Future, lo esperamos con await
        return await loop.run_in_executor(None, logica_simulacion, params)

    # 3. Creamos la tarea a partir de la corrutina
    current_simulation_task = asyncio.create_task(ejecutar_en_segundo_plano())
    
    # 4. Esperamos a que termine y guardamos
    try:
        resultado_simulacion = await current_simulation_task
        return {"mensaje": "Simulación completada con éxito."}
    except asyncio.CancelledError:
        return {"mensaje": "Simulación cancelada."}
    except Exception as e:
        return {"error": f"Ocurrió un error: {str(e)}"}

@app.get("/mostrar")
async def mostrar():
    if resultado_simulacion is None:
        return {"mensaje": "No hay datos de simulación"}
    return resultado_simulacion

@app.post("/limpiar")
async def limpiar():
    global resultado_simulacion, current_simulation_task
    if current_simulation_task:
        current_simulation_task.cancel()
    resultado_simulacion = None
    return {"mensaje": "Datos y tareas limpiados"}