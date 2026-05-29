# Clase que modela el paciente de la vacunacion, que en este caso seria el cliente del sistema

class Paciente:

    # Metodo de creacion del paciente recibe como parametro el id del paciente y la hora en la que llega
    def __init__(self, id_paciente, hora_llegada):

        # Con esto podemos identificar a cada paciente en la simulacion
        self.id = id_paciente

        # Estados posibles:
        # - Esperando
        # - Vacunandose
        # - Observacion
        # - Finalizado
        # El estado que tiene por defecto o inicial es Esperando
        self.estado = "Esperando"

        # =========================
        # TIEMPOS IMPORTANTES
        # =========================

        # Me guarda el valor de cuando llega el paciente, redondeado a tres decimales
        self.hora_llegada = round(hora_llegada, 3)

        # Iniciamos estos en None pero despues en la simulacion les ponemos un valor
        self.hora_inicio_vacunacion = None
        self.hora_fin_vacunacion = None
        self.hora_fin_observacion = None

    # Metodo chiquito que devuelve un paciente con su id y estado
    def __str__(self):

        return (
            f"Paciente {self.id} | "
            f"Estado: {self.estado}"
        )