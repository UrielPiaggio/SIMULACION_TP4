class Paciente:

    def __init__(self, id_paciente, hora_llegada):

        # =========================
        # IDENTIFICACIÓN
        # =========================

        self.id = id_paciente

        # =========================
        # ESTADO DEL PACIENTE
        # =========================

        # Estados posibles:
        # - Esperando
        # - Vacunandose
        # - Observacion
        # - Finalizado

        self.estado = "Esperando"

        # =========================
        # TIEMPOS IMPORTANTES
        # =========================

        self.hora_llegada = round(hora_llegada, 3)

        self.hora_inicio_vacunacion = None

        self.hora_fin_vacunacion = None

        self.hora_fin_observacion = None

    def __str__(self):

        return (
            f"Paciente {self.id} | "
            f"Estado: {self.estado}"
        )