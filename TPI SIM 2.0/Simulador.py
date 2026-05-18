from Servidor import ServidorVacunacion
from distribuciones import (distribucion_exponencial, distribucion_uniforme)
from Paciente import Paciente



class Simulador:

    def __init__(self, config):

        # Configuración
        self.config = config

        # Reloj
        self.reloj = 0

        # Control simulación
        self.iteracion = 0

        # Colas
        self.cola_espera = []

        # Zona observación
        self.zona_observacion = []

        # Servidores
        self.servidores = [
            ServidorVacunacion(1),
            ServidorVacunacion(2)
        ]

        # Próximos eventos

        #LLEGADA
        self.proxima_llegada = None
        self.rnd_llegada = None
        self.tiempo_entre_llegas = None

        # IDs pacientes (contador)
        self.id_paciente = 0

        # =========================
        # ESTADÍSTICAS
        # =========================
        #Paciente que no ingresan
        self.cantidad_no_ingresan = 0
        #tiempo acumulado de bloqueo    
        self.ac_tiempo_bloqueo = 0
        #cantidad bloqueos
        self.cantidad_bloqueos = 0
        #Acumulador de permanencia en el sistema de pacientes
        self.ac_permanencia_total = 0
        #Pacientes finalizados
        self.cantidad_pacientes_finalizados = 0

        # =========================
        # VECTOR ESTADO
        # =========================

        self.tabla_estado = []

    def inicializar_simulacion(self):

        rnd, tiempo = distribucion_exponencial(
            self.config.media_llegadas
            )

        self.rnd_llegada = rnd

        self.tiempo_entre_llegadas = tiempo

        self.proxima_llegada = self.reloj + tiempo

        
    #Buscar proximo evento
    # =====================================
# BUSCAR PRÓXIMO EVENTO
# =====================================

    def buscar_proximo_evento(self):

        eventos = []
        # PRÓXIMA LLEGADA
        if self.proxima_llegada is not None:

            eventos.append(
                (
                    "Llegada Paciente",
                    self.proxima_llegada,
                    None
                )
            )

        
        # FINES DE VACUNACIÓN
        
        for servidor in self.servidores:
            if servidor.fin_vacunacion is not None:

                eventos.append(
                    (
                        "Fin Vacunacion",
                        servidor.fin_vacunacion,
                        servidor
                    )
                )
                
        # FINES DE OBSERVACIÓN

        for paciente in self.zona_observacion:
            if (paciente.hora_fin_observacion is not None):
                eventos.append((
                    "Fin Observacion",
                    paciente.hora_fin_observacion,
                    paciente
                    ))

        


        # =========================
        # BUSCAR MENOR TIEMPO
        # =========================

        proximo_evento = min(
            eventos,
            key=lambda evento: evento[1]
        )

        print("\nEVENTOS FUTUROS")

        for e in eventos:
            print(e)

        return proximo_evento

        


    #Avanzar Reloj
    def avanzar_reloj(self, nuevo_reloj):

        self.reloj = nuevo_reloj

        self.iteracion += 1

    
    #EVENTOS 

    #Evento llegada paciente

    def procesar_llegada(self):

        #Crear paciente
        self.id_paciente +=1

        paciente = Paciente(self.id_paciente, self.reloj)
        
        #Proxima llegada

        rnd_llegada, tiempo_llegada = (
        distribucion_exponencial(
            self.config.media_llegadas
            )
        )
        self.rnd_llegada = rnd_llegada

        self.tiempo_entre_llegadas = (
            tiempo_llegada
        )

        self.proxima_llegada = (
            self.reloj + tiempo_llegada
        )

        #validar si abandono

        if (len(self.cola_espera) > self.config.capacidad_cola_externa):
            self.cantidad_no_ingresan += 1

            return
        

        #Buscar servidor libre
        servidor_libre = None

        for servidor in self.servidores:


            if servidor.estado == "Libre":
                servidor_libre = servidor

                break

        #si servidor libre
        if servidor_libre is not None:

            paciente.estado = "Vacunandose"

            paciente.hora_inicio_vacunacion = (self.reloj)

            rnd_vac, tiempo_vac = (distribucion_uniforme(self.config.vacunacion_min, self.config.vacunacion_max))

            hora_fin_vacunacion = round((self.reloj + tiempo_vac),3)

            paciente.hora_fin_vacunacion = (hora_fin_vacunacion)

            servidor_libre.ocupar(paciente, hora_fin_vacunacion)

        else:

            self.cola_espera.append(paciente)

    #Evento fin vacuanciopn
    def procesar_fin_vacunacion(self, servidor):

        # PACIENTE ACTUAL

        paciente = servidor.paciente_actual

    
        # VALIDAR CAPACIDAD
        # OBSERVACIÓN
    

        if (len(self.zona_observacion) >= self.config.capacidad_observacion):

            # BLOQUEAR SERVIDOR

            servidor.bloquear(self.reloj)

            self.cantidad_bloqueos += 1

            return

    
        # PASAR A OBSERVACIÓN

        paciente.estado = "Observacion"

        paciente.hora_fin_observacion = (self.reloj + self.config.tiempo_observacion)

        self.zona_observacion.append(paciente)

     
        # LIBERAR SERVIDOR
    

        servidor.liberar()

    
        # REVISAR COLA
    

        if len(self.cola_espera) > 0:

            siguiente_paciente = (
                self.cola_espera.pop(0)
            )

            siguiente_paciente.estado = ("Vacunandose")

            siguiente_paciente.hora_inicio_vacunacion = (self.reloj)

            rnd_vac, tiempo_vac = (
                distribucion_uniforme(
                    self.config.vacunacion_min,
                    self.config.vacunacion_max
                )
            )

            hora_fin_vac = (self.reloj + tiempo_vac)

            siguiente_paciente.hora_fin_vacunacion = (hora_fin_vac)

            servidor.ocupar(siguiente_paciente, hora_fin_vac)

    
    #Procesar Fines de Observacion

    def procesar_fin_observacion(self, paciente):
        # SACAR DE OBSERVACIÓN

        self.zona_observacion.remove(paciente)

        # FINALIZAR PACIENTE
        
        paciente.estado = "Finalizado"
        paciente.hora_fin_observacion = None

        # CALCULAR PERMANENCIA
    
        permanencia = (self.reloj - paciente.hora_llegada)

        self.ac_permanencia_total += ( permanencia)

        self.cantidad_pacientes_finalizados += 1

    
        # REVISAR SERVIDORES
        # BLOQUEADOS
    

        for servidor in self.servidores:
            
            if servidor.estado == "Bloqueado":

                paciente_bloqueado = (servidor.paciente_actual)
                print("SERVIDOR BLOQUEADO", paciente_bloqueado)

            
            # PASAR A OBSERVACIÓN

                paciente_bloqueado.estado = ("Observacion")
                paciente_bloqueado.hora_fin_observacion = (self.reloj + self.config.tiempo_observacion)
                self.zona_observacion.append(paciente_bloqueado)

                # ACUMULAR BLOQUEO

                tiempo_bloqueo = (self.reloj - servidor.inicio_bloqueo)
                self.ac_tiempo_bloqueo += (tiempo_bloqueo)

            
                # REVISAR COLA
            

                if len(self.cola_espera) > 0:

                    siguiente_paciente = (self.cola_espera.pop(0))

                    siguiente_paciente.estado = ("Vacunandose")

                    siguiente_paciente.hora_inicio_vacunacion = (self.reloj)

                    rnd_vac, tiempo_vac = (distribucion_uniforme(
                        self.config.vacunacion_min,
                        self.config.vacunacion_max
                    ))

                    hora_fin_vac = (self.reloj + tiempo_vac)

                    siguiente_paciente.hora_fin_vacunacion = (hora_fin_vac)

                    servidor.ocupar(siguiente_paciente, hora_fin_vac)

            
                    # SI NO HAY COLA
                else:
                    servidor.liberar()

    


