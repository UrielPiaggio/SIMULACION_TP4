# aca modelamos el servidor de vacunacion 

class ServidorVacunacion:

    def __init__(self, id_servidor):

        # =========================
        # IDENTIFICACIÓN -> identificador único del servidor
        # =========================

        self.id = id_servidor

        # =========================
        # ESTADO DEL SERVIDOR
        # =========================

        # Estados posibles:
        # - Libre
        # - Ocupado
        # - Bloqueado
        # Por defecto el servidor esta inicialmente libre

        self.estado = "Libre"

        # =========================
        # PACIENTE ACTUAL: referencia a la instancia del objeto paciente que está atendiendo en ese momento
        # =========================

        self.paciente_actual = None

        # =========================
        # Fin de vacunacion: referencia al momento en el que se termina de vacunar al paciente, es decir, se libera al servidor de la instancia del objeto que definimos arriba
        # =========================

        self.fin_vacunacion = None

        # =========================
        # BLOQUEO: lo usamos para calcular cuanto tiempo el servidor esta bloqueado cuando no hay espacio en la zona de observacion
        # =========================

        self.inicio_bloqueo = None

    # Le asgina un paciente al servidor y lo pone como Ocupado
    def ocupar(self, paciente, hora_fin_vacunacion):

        self.estado = "Ocupado"
        

        self.paciente_actual = paciente

        self.fin_vacunacion = round(hora_fin_vacunacion, 3)

    # Libera al servidor despues de que el pacien se transfiere a observacion reiniciando todos los atributos a valores por defecto
    def liberar(self):

        self.estado = "Libre"

        self.paciente_actual = None

        self.fin_vacunacion = None

        self.inicio_bloqueo = None

    # Bloquea el servidor porque esta llena la zona de observacion 
    def bloquear(self, reloj_actual):

        self.estado = "Bloqueado"

        self.inicio_bloqueo = reloj_actual

        # La vacunación YA terminó
        self.fin_vacunacion = None

    # Esto es para logging
    def __str__(self):

        return (
            f"Servidor {self.id} | "
            f"Estado: {self.estado}"
        )