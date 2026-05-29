# Clase que centraliza todos los parametros de la simulacion para que sea facil twekearlos

class ConfiguracionSimulacion:

# Este constructor recibe una banda de parametros pero don't worry son razonables
# media_llegadas es la media de la distribucion exponencial negativa que determina como llegan los pacientes al lugar (los clientes al servidor digamo)
# vacunacion_min y vacunacion_max son los valores A y B que definen mediante una distribucion uniforme los tiempos que se demora en vacunar a un paciente
# tiempo_observacion es el tiempo que tiene que pasar el paciente en una zona de observacion y es un int 
# capacidad_cola_externa es el tamaño de la cola de espera de afuera, seria del servidor de vacunacion
# capacidad_observacion es el tamaño de la zona de observacion
# tiempo_simulacion y max_iteraciones son parametros de corte de la simulacion, al que se llegue primero se termina la simulacion
# mostrar_desde_iteracion y cantidad_iteraciones_mostrar son para ver el vector estado en el resultado de la simulacion

    def __init__(
        self,
        media_llegadas=6,
        vacunacion_min=3,
        vacunacion_max=7,
        tiempo_observacion=1,
        capacidad_cola_externa=10,
        capacidad_observacion=1,
        tiempo_simulacion=30,
        max_iteraciones=100,
        mostrar_desde_iteracion=0,
        cantidad_iteraciones_mostrar=100
    ):

        # =========================
        # DISTRIBUCIONES
        # =========================

        self.media_llegadas = media_llegadas

        self.vacunacion_min = vacunacion_min
        self.vacunacion_max = vacunacion_max

        self.tiempo_observacion = tiempo_observacion

        # =========================
        # CAPACIDADES
        # =========================

        self.capacidad_cola_externa = capacidad_cola_externa
        self.capacidad_observacion = capacidad_observacion


        # =========================
        # CONTROL SIMULACIÓN
        # =========================

        self.tiempo_simulacion = tiempo_simulacion
        self.max_iteraciones = max_iteraciones

        # =========================
        # VISUALIZACIÓN
        # =========================

        self.mostrar_desde_iteracion = mostrar_desde_iteracion
        self.cantidad_iteraciones_mostrar = cantidad_iteraciones_mostrar

# metodo q imprime todos los parametros almacenados de arriba en una forma legible
    def mostrar_configuracion(self):

        print("\n===== CONFIGURACIÓN =====")

        print(f"Media llegadas: {self.media_llegadas}")

        print(
            f"Vacunación uniforme: "
            f"[{self.vacunacion_min}, {self.vacunacion_max}]"
        )

        print(
            f"Tiempo observación: "
            f"{self.tiempo_observacion}"
        )

        print(
            f"Capacidad cola externa: "
            f"{self.capacidad_cola_externa}"
        )

        print(
            f"Capacidad observación: "
            f"{self.capacidad_observacion}"
        )



        print(
            f"Tiempo simulación: "
            f"{self.tiempo_simulacion}"
        )

        print(
            f"Máximo iteraciones: "
            f"{self.max_iteraciones}"
        )

        print(
            f"Mostrar desde iteración: "
            f"{self.mostrar_desde_iteracion}"
        )

        print(
            f"Cantidad iteraciones mostrar: "
            f"{self.cantidad_iteraciones_mostrar}"
        )


# =====================================
# EJEMPLO DE USO
# =====================================

config = ConfiguracionSimulacion(
    media_llegadas=6,
    vacunacion_min=3,
    vacunacion_max=7,
    tiempo_observacion=15,
    capacidad_cola_externa=10,
    capacidad_observacion=20,
    tiempo_simulacion=500,
    max_iteraciones=100000,
    mostrar_desde_iteracion=0,
    cantidad_iteraciones_mostrar=200
)

config.mostrar_configuracion()