class ServidorVacunacion:

    def __init__(self, id_servidor):

        # =========================
        # IDENTIFICACIÓN
        # =========================

        self.id = id_servidor

        # =========================
        # ESTADO DEL SERVIDOR
        # =========================

        # Estados posibles:
        # - Libre
        # - Ocupado
        # - Bloqueado

        self.estado = "Libre"

        # =========================
        # PACIENTE ACTUAL
        # =========================

        self.paciente_actual = None

        # =========================
        # EVENTOS FUTUROS
        # =========================

        self.fin_vacunacion = None

        # =========================
        # BLOQUEO
        # =========================

        self.inicio_bloqueo = None

    def ocupar(self, paciente, hora_fin_vacunacion):

        self.estado = "Ocupado"

        self.paciente_actual = paciente

        self.fin_vacunacion = round(hora_fin_vacunacion, 3)

    def liberar(self):

        self.estado = "Libre"

        self.paciente_actual = None

        self.fin_vacunacion = None

        self.inicio_bloqueo = None

    def bloquear(self, reloj_actual):

        self.estado = "Bloqueado"

        self.inicio_bloqueo = reloj_actual

    def __str__(self):

        return (
            f"Servidor {self.id} | "
            f"Estado: {self.estado}"
        )