class ConfiguracionSimulacion:

    def __init__(
        self,

        # Llegadas (Exponencial)
        media_llegadas=6,

        # Vacunación (Uniforme)
        vacunacion_min=3,
        vacunacion_max=7,

        # Observación
        tiempo_observacion=1,

        # Capacidades
        capacidad_cola_externa=10,
        capacidad_observacion=1,
        

        # Simulación
        tiempo_simulacion=30,
        max_iteraciones=100,

        # Visualización del vector
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