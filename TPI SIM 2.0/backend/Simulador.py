from Servidor import ServidorVacunacion
from distribuciones import (distribucion_exponencial, distribucion_uniforme)
from Paciente import Paciente



class Simulador:

    def __init__(self, config):

        # Configuración
        self.config = config

        # Reloj
        self.reloj = 0

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

        # VACUNACIÓN

        self.rnd_vacunacion = None
        self.tiempo_vacunacion = None
        self.fin_vacunacion_generado = None

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
        # Control simulacion
        self.iteracion = 0
        self.promedio_permanencia = 0
        self.porcentaje_rechazo = 0
        self.promedio_bloqueo = 0

        self.posiciones_pacientes = {}

    #EVENTO DE INICILIZACION
    def inicializar_simulacion(self):

        rnd, tiempo = distribucion_exponencial(
            self.config.media_llegadas
            )

        self.rnd_llegada = rnd

        self.tiempo_entre_llegadas = tiempo

        self.proxima_llegada = self.reloj + tiempo
    
        self.registrar_vector("Inicializacion")

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
        #FIN SIMULACION
        eventos.append(
            (
                "Fin Simulacion",
                self.config.tiempo_simulacion,
                None
            )   
            )

        # =========================
        # BUSCAR MENOR TIEMPO
        # =========================

        proximo_evento = min(
            eventos,
            key=lambda evento: evento[1]
        )

    

        return proximo_evento


    #Avanzar Reloj
    def avanzar_reloj(self, nuevo_reloj):

        self.reloj = nuevo_reloj

    #EVENTOS 

    #Evento llegada paciente

    def procesar_llegada(self):

        #Crear paciente
        self.id_paciente +=1

        paciente = Paciente(self.id_paciente, self.reloj)
        
        #Proxima llegada

        rnd_llegada, tiempo_llegada = (
        distribucion_exponencial(self.config.media_llegadas))
        self.rnd_llegada = rnd_llegada

        self.tiempo_entre_llegadas = (
            tiempo_llegada
        )

        self.proxima_llegada = (
            self.reloj + tiempo_llegada
        )

        #validar si abandono

        if (len(self.cola_espera) >= self.config.capacidad_cola_externa):
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
            self.rnd_vacunacion = rnd_vac
            self.tiempo_vacunacion = tiempo_vac
            
            hora_fin_vacunacion = round((self.reloj + tiempo_vac),3)
            self.fin_vacunacion_generado = (hora_fin_vacunacion)
            
            paciente.hora_fin_vacunacion = (hora_fin_vacunacion)

            servidor_libre.ocupar(paciente, hora_fin_vacunacion)

        else:

            self.cola_espera.append(paciente)
            self.rnd_vacunacion = None
            self.tiempo_vacunacion = None
            self.fin_vacunacion_generado = None

    #Evento fin vacuancion

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

        paciente.hora_inicio_observacion = (self.reloj)
        paciente.hora_fin_observacion = (self.reloj + self.config.tiempo_observacion)

        self.zona_observacion.append(paciente)

        
    
        
    
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
            self.rnd_vacunacion = rnd_vac
            self.tiempo_vacunacion = tiempo_vac

            hora_fin_vac = (self.reloj + tiempo_vac)
            self.fin_vacunacion_generado = (hora_fin_vac)

            siguiente_paciente.hora_fin_vacunacion = (hora_fin_vac)

            servidor.ocupar(siguiente_paciente, hora_fin_vac)
        else:
            servidor.liberar()

            self.rnd_vacunacion = None
            self.tiempo_vacunacion = None
            self.fin_vacunacion_generado = None

    
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
                

            
            # PASAR A OBSERVACIÓN

                paciente_bloqueado.estado = ("Observacion")
                paciente_bloqueado.hora_inicio_observacion = (self.reloj)
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

                    self.rnd_vacunacion = rnd_vac
                    self.tiempo_vacunacion = tiempo_vac

                    hora_fin_vac = (self.reloj + tiempo_vac)
                    self.fin_vacunacion_generado = (hora_fin_vac)

                    siguiente_paciente.hora_fin_vacunacion = (hora_fin_vac)

                    servidor.inicio_bloqueo = None
                    servidor.paciente_actual = None
                    servidor.ocupar(siguiente_paciente, hora_fin_vac)
                    

            
                    # SI NO HAY COLA
                else:
                    servidor.inicio_bloqueo = None
                    servidor.paciente_actual = None
                    servidor.liberar()
                    self.rnd_vacunacion = None
                    self.tiempo_vacunacion = None
                    self.fin_vacunacion_generado = None
                    
    

    
    # EVENTO FIN SIMULACIÓN


    def procesar_fin_simulacion(self):
    
        # PACIENTES EN OBSERVACIÓN
        for paciente in self.zona_observacion:

            permanencia = (self.reloj - paciente.hora_llegada)
            self.ac_permanencia_total += (permanencia)
            self.cantidad_pacientes_finalizados += 1

    
        # PACIENTES EN VACUNACIÓN
    

        for servidor in self.servidores:

            if servidor.paciente_actual is not None:

                paciente = (servidor.paciente_actual)
                permanencia = (self.reloj - paciente.hora_llegada)
                self.ac_permanencia_total += (permanencia)
                self.cantidad_pacientes_finalizados += 1

        # SERVIDORES BLOQUEADOS
        

            if servidor.estado == "Bloqueado":

                tiempo_bloqueo = (self.reloj - servidor.inicio_bloqueo)
                self.ac_tiempo_bloqueo += (tiempo_bloqueo)

    
        # PACIENTES EN COLA
    

        for paciente in self.cola_espera:

            permanencia = (self.reloj - paciente.hora_llegada)

            self.ac_permanencia_total += (permanencia)

            self.cantidad_pacientes_finalizados += 1

    
        # MÉTRICAS FINALES
    
        #Promedio de permanencia total de las personas en el centro (desde que llegan hasta que 
        #salen de observación).

        if (self.cantidad_pacientes_finalizados > 0):

            self.promedio_permanencia = (self.ac_permanencia_total / self.cantidad_pacientes_finalizados)

        else:

            self.promedio_permanencia = 0

        # =========================
        #Porcentaje de personas que no ingresaron al centro debido a la longitud de la fila externa.

        total_pacientes = (self.id_paciente)

        if total_pacientes > 0:
            self.porcentaje_rechazo = (self.cantidad_no_ingresan / total_pacientes) * 100

        else:

            self.porcentaje_rechazo = 0

        # =========================
        #Tiempo promedio de bloqueo de los puestos de vacunación por falta de espacio en la zona 
        #de observación.

        if self.cantidad_bloqueos > 0:

            self.promedio_bloqueo = (self.ac_tiempo_bloqueo / self.cantidad_bloqueos)

        else:

            self.promedio_bloqueo = 0

        


    
    # =====================================
    # LOOP PRINCIPAL SIMULACIÓN
    # =====================================

    def simular(self):

        self.inicializar_simulacion()
        self.iteracion +=1

        fin_simulacion = False

        while not fin_simulacion:

            evento, hora, objeto = (self.buscar_proximo_evento())

            self.avanzar_reloj(hora)

            if evento == "Llegada Paciente":

                self.procesar_llegada()

            elif evento == "Fin Vacunacion":

                self.procesar_fin_vacunacion(objeto)

            elif evento == "Fin Observacion":

                self.procesar_fin_observacion(objeto)

            elif evento == "Fin Simulacion":

                self.procesar_fin_simulacion()
                fin_simulacion = True
            
            # CORTE POR ITERACIONES
    
            if (self.iteracion >= self.config.max_iteraciones and not fin_simulacion):

                # FORZAR FIN SIMULACIÓN

                self.procesar_fin_simulacion()

                fin_simulacion = True

            #Guardar vector
            self.registrar_vector(evento)
            #Siguiente Iteracion
            self.iteracion += 1
            
          


    

        # =====================================
        # REGISTRAR VECTOR ESTADO
        # =====================================

    def registrar_vector(self, evento):
        fila = {
            # GENERALES
            "Iteracion": self.iteracion,
            "Reloj": round(self.reloj,3),
            "Evento": evento,
        
            # LLEGADAS
    
            "RND Llegada": (
                round(self.rnd_llegada, 4)
                if self.rnd_llegada is not None
                else None
            ),

            "Tiempo Entre Llegadas": (
                round(self.tiempo_entre_llegadas,3)
                if self.tiempo_entre_llegadas
                is not None
                else None
            ),

            "Proxima Llegada": (
                round(self.proxima_llegada, 3)
                if self.proxima_llegada
                is not None
                else None
            ),

            # VACUNACIÓN
        
            "RND Vacunacion": (
                round(self.rnd_vacunacion,3)
                if self.rnd_vacunacion
                is not None
                else None
            ),

            "Tiempo Vacunacion": (
                round(self.tiempo_vacunacion, 3)
                if self.tiempo_vacunacion
                is not None
                else None
            ),

            "Fin Vacunacion Generado": (
                round(self.fin_vacunacion_generado, 3)
                if self.fin_vacunacion_generado
                is not None
                else None
            ),

            # COLAS
            "Cola Espera": len(self.cola_espera),
            "Observacion": len(self.zona_observacion),

            # MÉTRICAS

            "Cantidad No Ingresan": (self.cantidad_no_ingresan),

            "Cantidad Bloqueos": (self.cantidad_bloqueos),

            "Pacientes Finalizados": (self.cantidad_pacientes_finalizados),

            "Ac Tiempo Bloqueo": (round(self.ac_tiempo_bloqueo,3)),

            "Ac Permanencia": (round(self.ac_permanencia_total,3))
        }

        # SERVIDORES
    

        for servidor in self.servidores:

            fila[f"Estado Servidor {servidor.id}"] = servidor.estado

            fila[f"Paciente Servidor {servidor.id}"] = (
                servidor.paciente_actual.id
                if servidor.paciente_actual
                is not None
                else None
            )

            fila[f"Fin Vac Servidor {servidor.id}"] = (
                round(servidor.fin_vacunacion,3)
                if servidor.fin_vacunacion
                is not None
                else None
            )

            fila[f"Inicio Bloqueo Servidor {servidor.id}"] = (
                round(servidor.inicio_bloqueo, 3)
                if servidor.inicio_bloqueo
                is not None
                else None
            )

        # SEGUIMIENTO DE PACIENTES
        pacientes_sistema = []

        for paciente in self.cola_espera:
            pacientes_sistema.append(paciente)

        #Paciente vacunandose
        for servidor in self.servidores:

            if servidor.paciente_actual is not None:

                pacientes_sistema.append(servidor.paciente_actual)
        
        #Paciente observacion
        for paciente in self.zona_observacion:

            pacientes_sistema.append(paciente)

        
        # COLUMNAS PACIENTES


        # --- LÓGICA DE COLUMNAS FIJAS (REUTILIZABLES) ---
        
        # 1. Identificar IDs de pacientes que siguen en el sistema
        ids_actuales = [p.id for p in pacientes_sistema]

        # 2. Limpiar del mapeador a los que ya se fueron (libera la columna)
        ids_a_borrar = [pid for pid in self.posiciones_pacientes if pid not in ids_actuales]
        for pid in ids_a_borrar:
            del self.posiciones_pacientes[pid]

        # 3. Asignar columna a los nuevos que entraron
        for p in pacientes_sistema:
            if p.id not in self.posiciones_pacientes:
                # Busca el primer número de columna (1, 2, 3...) que esté libre
                col_libre = 1
                while any(c == col_libre for c in self.posiciones_pacientes.values()):
                    col_libre += 1
                self.posiciones_pacientes[p.id] = col_libre

        # 4. Llenar la fila con las columnas (ejemplo: capacidad para 10 columnas visibles)
        # Esto asegura que la Columna 1 sea siempre la misma en el Excel/Tabla
        max_columnas_visibles = 15 
        for i in range(1, max_columnas_visibles + 1):
            # Ver si hay algún paciente asignado a esta columna 'i'
            id_en_esta_col = next((pid for pid, c in self.posiciones_pacientes.items() if c == i), None)
            
            p_data = next((p for p in pacientes_sistema if p.id == id_en_esta_col), None)

            if p_data:
                fila[f"P{i}_ID"] = p_data.id
                fila[f"P{i}_Estado"] = p_data.estado
                fila[f"P{i}_Llegada"] = round(p_data.hora_llegada, 2)
                
                if p_data.estado == "Vacunandose":
                    fila[f"P{i}_FinVac"] = round(p_data.hora_fin_vacunacion, 2)
                    fila[f"P{i}_FinObs"] = None
                elif p_data.estado == "Observacion":
                    fila[f"P{i}_FinVac"] = None
                    fila[f"P{i}_FinObs"] = round(p_data.hora_fin_observacion, 2)
                else:
                    fila[f"P{i}_FinVac"] = None
                    fila[f"P{i}_FinObs"] = None
            else:
                # Columna vacía (paciente se fue o nunca hubo)
                fila[f"P{i}_ID"] = None
                fila[f"P{i}_Estado"] = None
                fila[f"P{i}_Llegada"] = None
                fila[f"P{i}_FinVac"] = None
                fila[f"P{i}_FinObs"] = None

        self.tabla_estado.append(fila)
    


