# Imports importantes para manejar APIs y todo el chiste
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Configuracion import ConfiguracionSimulacion
from Simulador import Simulador

# La idea es que en este archivo implementemos una API web asincrona con FastAPI para ejecutar las simulaciones del TP y consultar los resultados. De alguna manera, funciona como el Gestor (que vimos en DSI!), recibiendo parametros, ejecutando la simulacion en segundo plano (asi no explota la PC, gracias Gero por donar la notebook para la causa), guardando los resultados y permitiendo su revision

# Arrancamos creando la instancia de fast api 
app = FastAPI(title="Simulador Salud Vital - Grupo 13")

# Le habilitamos un CORS que sea permisivo para cualquier origen (incluido nuestra propia compu) con cualquier metodo y header. ESTO NO DEBERIA SALIR A PRODUCCION A MENOS QUE QUIERAS QUE TE HACKEEN HASTA EL ALMA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Iniciamos las variables de estado globales que nos van a permitir almacenar el ultimo resultado de la simulacion (asi despues lo mostramos en el frontend) y la simulacion que estamos corriendo actualmente para que si despues queremos cancelarla este proceso se mate, porque sino la PC estaria corriendo tantas simulaciones en paralelo como las que ejecutemos (Gero tiene una anecdota con eso)
resultado_simulacion = None
current_simulation_task = None

# Define el formato y tipos de datos que se tienen q enviar al endpoint /simular. Son casi iguales a los q definimos en Configuracion.py
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
    
    # Crea y ejecuta el simulador
    sim = Simulador(config)
    sim.simular()
    
    # El vector q despues mostramos en el frontend
    vector_filtrado = []
    contador_mostrados = 0
    
    # Filtramos las filas q cumplan lo de la hora a partir de la que queremos mostrar y solamente la cantidad que se pasaron por parametro antes
    for fila in sim.tabla_estado:
        if fila["Reloj"] >= params.mostrar_desde_hora and contador_mostrados < params.cantidad_iteraciones_mostrar:
            vector_filtrado.append(fila)
            contador_mostrados += 1
            
    if sim.tabla_estado:
        ultima_fila = sim.tabla_estado[-1]
        if ultima_fila not in vector_filtrado:
            vector_filtrado.append(ultima_fila)

    # Metricas q devolvemos para despues usar en el grafico  
    return {
        "metricas": {
            "porcentaje_rechazo_fila_externa": sim.porcentaje_rechazo,
            "promedio_minutos_bloqueo": sim.promedio_bloqueo,
            "promedio_permanencia_sistema": sim.promedio_permanencia
        },
        "vector_estado": vector_filtrado
    }

# Este es el endpoint principal q basicamente lanza una simulacion nueva, y cancela la anterior si todavia se esta ejecutando
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
    
    # Este endpoint no devuelve los resultados directamente solo confirma que la simulación se completó o canceló. Los resultados se consultan mediante /mostrar

# O mostramos los resultados o informamos que no hay
@app.get("/mostrar")
async def mostrar():
    if resultado_simulacion is None:
        return {"mensaje": "No hay datos de simulación"}
    return resultado_simulacion

# Cancela cualquier simulación en curso y borra el resultado guardado
@app.post("/limpiar")
async def limpiar():
    global resultado_simulacion, current_simulation_task
    if current_simulation_task:
        current_simulation_task.cancel()
    resultado_simulacion = None
    return {"mensaje": "Datos y tareas limpiados"}